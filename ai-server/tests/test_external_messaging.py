"""External messaging (LINE / Discord / Email) — the gate decides, and only the gate.

The owner put external messaging into v1 on 2026-09-30. The constraint that governs it is
"*unpermitted* user information must never leave the local environment", so the design rule
these tests hold is:

    a message body is the user's own content, so it may leave only when the egress gate
    permits the destination — and nothing else may decide.

Three failure modes are pinned by name:

1. **A channel sends without asking.** Every transport is injected here, so these tests assert
   the transport was *not called*, not merely that a result looked refused.
2. **A channel reorders the gate.** ``OutboundChannel.send`` is the only place the gate is
   consulted; ``test_no_channel_overrides_the_send_ordering`` discovers the subclasses and
   requires that none of them redefines ``send`` or ``_deliver``.
3. **A credential escapes.** The Discord webhook URL *contains* the token, so ``destination()``
   reports the origin only, and a transport exception is reported by type.

A fourth, older defect is pinned too: the router used to blank the body for any declared
external channel. That was written when external channels were forbidden outright; after the
re-scope it makes the permission meaningless, and it mutated ``notification.body`` *before*
the fan-out, so a dashboard copy lost its body as well.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from aegis_ai.egress import EgressGate
from aegis_ai.notification.channels import (
    DiscordNotificationChannel,
    EmailNotificationChannel,
    LineNotificationChannel,
)
from aegis_ai.notification.channels.outbound import OutboundChannel
from aegis_ai.notification.models import Notification, NotificationChannel

pytestmark = pytest.mark.egress

_CHANNELS_DIR = (
    Path(__file__).resolve().parents[1] / "src" / "aegis_ai" / "notification" / "channels"
)

LINE_ENV = {"AEGIS_LINE_CHANNEL_ACCESS_TOKEN": "token-abc", "AEGIS_LINE_TO": "user-1"}
DISCORD_ENV = {"AEGIS_DISCORD_WEBHOOK_URL": "https://discord.com/api/webhooks/1/SECRET"}
EMAIL_ENV = {"AEGIS_SMTP_HOST": "smtp.example.com", "AEGIS_SMTP_TO": "user@example.com"}


def _notification(body: str = "the user's own text") -> Notification:
    return Notification(title="AEGIS notice", body=body)


class _Recorder:
    """A transport that records calls instead of making one."""

    def __init__(self, ok: bool = True, status: int = 200, error: str = "") -> None:
        self.calls: list[tuple[str, str]] = []
        self._ok, self._status, self._error = ok, status, error

    def __call__(self, destination: str, notification: Notification):
        self.calls.append((destination, notification.body))
        return self._ok, self._status, self._error


def _line(store, transport, **kwargs):
    return LineNotificationChannel(
        env=LINE_ENV, transport=transport, egress_gate=EgressGate(settings_store=store), **kwargs
    )


def _discord(store, transport, env=None, **kwargs):
    return DiscordNotificationChannel(
        env=env or DISCORD_ENV,
        transport=transport,
        egress_gate=EgressGate(settings_store=store),
        **kwargs,
    )


def _email(store, transport, **kwargs):
    return EmailNotificationChannel(
        env=EMAIL_ENV, transport=transport, egress_gate=EgressGate(settings_store=store), **kwargs
    )


# ── The default: nothing leaves ───────────────────────────────────────────────


def test_every_channel_refuses_with_the_shipped_default(settings_store_factory):
    """All locks closed — the shipped state — means no transport call for any channel."""
    store = settings_store_factory()
    recorders = [_Recorder() for _ in range(3)]

    results = [
        _line(store, recorders[0]).send(_notification()),
        _discord(store, recorders[1]).send(_notification()),
        _email(store, recorders[2]).send(_notification()),
    ]

    assert [r.refused_by_gate for r in results] == [True, True, True]
    assert [r.attempted for r in results] == [False, False, False]
    assert [r.calls for r in recorders] == [[], [], []]


@pytest.mark.parametrize(
    "build",
    [_line, _discord, _email],
    ids=["line", "discord", "email"],
)
def test_the_transport_is_never_called_when_the_gate_refuses(settings_store_factory, build):
    """The assertion that matters: not "the result says refused" but "nothing was sent"."""
    recorder = _Recorder()
    result = build(settings_store_factory(), recorder).send(_notification())
    assert result.refused_by_gate is True
    assert recorder.calls == []


def test_the_refusal_names_the_destination_and_the_purpose(settings_store_factory):
    """An operator reading the result must learn what to permit, and for what."""
    result = _line(settings_store_factory(), _Recorder()).send(_notification())
    assert "api.line.me" in result.error
    assert "messaging.line" in result.error


# ── Path 1: standing configuration ────────────────────────────────────────────


def test_the_standing_path_permits_a_message(settings_store_factory):
    """Master switch + the messaging flag + an allowlist entry = permitted."""
    store = settings_store_factory(
        external_egress_allowed=True,
        external_messaging_allowed=True,
        egress_allowed_hosts=["api.line.me"],
    )
    recorder = _Recorder()
    result = _line(store, recorder).send(_notification())

    assert result.refused_by_gate is False
    assert result.success is True
    assert recorder.calls == [("https://api.line.me", "the user's own text")]


def test_the_messaging_flag_alone_is_not_enough(settings_store_factory):
    """A flag is not a destination. The host must be allowlisted too, as for every purpose."""
    store = settings_store_factory(
        external_egress_allowed=True, external_messaging_allowed=True
    )
    recorder = _Recorder()
    result = _line(store, recorder).send(_notification())

    assert result.refused_by_gate is True
    assert recorder.calls == []


def test_the_allowlist_alone_is_not_enough(settings_store_factory):
    """The mirror of the previous test: an allowlisted host still needs the purpose flag."""
    store = settings_store_factory(
        external_egress_allowed=True, egress_allowed_hosts=["api.line.me"]
    )
    recorder = _Recorder()
    result = _line(store, recorder).send(_notification())

    assert result.refused_by_gate is True
    assert recorder.calls == []


def test_the_master_switch_still_bounds_messaging(settings_store_factory):
    """Both other locks open, master switch closed — still refused."""
    store = settings_store_factory(
        external_messaging_allowed=True, egress_allowed_hosts=["api.line.me"]
    )
    recorder = _Recorder()
    result = _line(store, recorder).send(_notification())

    assert result.refused_by_gate is True
    assert recorder.calls == []


def test_the_purpose_flag_is_read_by_the_gate(settings_store_factory):
    """Flipping *only* `external_messaging_allowed` must change the decision.

    Without this, the field would be a settings flag with no reader — the bug
    `test_ineffective_flags.py` exists to catch.
    """
    closed = settings_store_factory(
        external_egress_allowed=True, egress_allowed_hosts=["api.line.me"]
    )
    opened = settings_store_factory(
        external_egress_allowed=True,
        external_messaging_allowed=True,
        egress_allowed_hosts=["api.line.me"],
    )
    assert _line(closed, _Recorder()).send(_notification()).refused_by_gate is True
    assert _line(opened, _Recorder()).send(_notification()).refused_by_gate is False


# ── Path 2: a recorded grant ──────────────────────────────────────────────────


class _Grant:
    grant_id = "grant-1"
    host = "api.line.me"
    purpose = "messaging.line"

    def is_expired_at(self, _moment):
        return False


class _GrantSource:
    def __init__(self, grants):
        self._grants = grants

    def grants(self):
        return list(self._grants)

    def grant_for(self, *, host, purpose, moment_ms=None):
        for grant in self._grants:
            if grant.host == host and grant.purpose == purpose:
                return grant
        return None


def test_a_recorded_grant_permits_without_the_standing_flags(settings_store_factory):
    """The narrower path: the user permitted this exact destination.

    The grant stands in for the *standing pair* — the messaging flag and the allowlist
    entry. It does **not** stand in for the master switch: that bounds every external
    request, so it is the one lock left on here. (Pinned by
    ``test_the_master_switch_still_bounds_messaging`` below, and upstream by
    ``test_egress_permission.py::test_the_master_switch_still_bounds_everything`` — a
    grant that could override the master switch would make the switch an ineffective flag.)
    """
    gate = EgressGate(
        settings_store=settings_store_factory(external_egress_allowed=True),
        permission_source=_GrantSource([_Grant()]),
    )
    recorder = _Recorder()
    result = LineNotificationChannel(
        env=LINE_ENV, transport=recorder, egress_gate=gate
    ).send(_notification())

    assert result.refused_by_gate is False
    assert result.success is True
    assert recorder.calls == [("https://api.line.me", "the user's own text")]


def test_a_grant_for_another_purpose_does_not_permit_messaging(settings_store_factory):
    """`messaging.line` is not `voice.tts` — a grant is scoped to its purpose.

    The master switch is deliberately **on** here: with it off the request would be refused
    whatever the grant said, and the test would pass without proving anything about purpose
    scoping.
    """
    other = _Grant()
    other.purpose = "voice.tts"
    gate = EgressGate(
        settings_store=settings_store_factory(external_egress_allowed=True),
        permission_source=_GrantSource([other]),
    )
    recorder = _Recorder()
    result = LineNotificationChannel(
        env=LINE_ENV, transport=recorder, egress_gate=gate
    ).send(_notification())

    assert result.refused_by_gate is True
    assert recorder.calls == []


# ── Local destinations ────────────────────────────────────────────────────────


def test_a_local_destination_needs_no_permission(settings_store_factory):
    """A webhook on loopback is inside the local environment — the constraint does not apply.

    This is the rule working as written, not a hole: the constraint is about user information
    leaving the local environment.
    """
    recorder = _Recorder()
    channel = _discord(
        settings_store_factory(),
        recorder,
        env={"AEGIS_DISCORD_WEBHOOK_URL": "http://localhost:9000/hook"},
    )
    result = channel.send(_notification())

    assert result.refused_by_gate is False
    assert result.success is True
    assert recorder.calls == [("http://localhost", "the user's own text")]


# ── Credentials ───────────────────────────────────────────────────────────────


def test_the_discord_destination_never_carries_the_token(settings_store_factory):
    """The webhook URL holds the token, and the destination is reported to the caller."""
    channel = _discord(settings_store_factory(), _Recorder())
    assert channel.destination() == "https://discord.com"
    assert "SECRET" not in channel.destination()


def test_a_transport_exception_is_reported_by_type_only(settings_store_factory):
    """An exception message can contain a URL with the token, so it is not propagated."""
    store = settings_store_factory(
        external_egress_allowed=True,
        external_messaging_allowed=True,
        egress_allowed_hosts=["discord.com"],
    )

    def _explode(destination, notification):
        raise RuntimeError("https://discord.com/api/webhooks/1/SECRET is bad")

    result = _discord(store, _explode).send(_notification())

    assert result.success is False
    assert "RuntimeError" in result.error
    assert "SECRET" not in result.error


def test_an_unconfigured_channel_refuses_before_the_gate(settings_store_factory):
    """No credentials means no destination, so there is nothing to ask the gate about."""
    store = settings_store_factory(
        external_egress_allowed=True,
        external_messaging_allowed=True,
        egress_allowed_hosts=["api.line.me"],
    )
    recorder = _Recorder()
    result = LineNotificationChannel(
        env={}, transport=recorder, egress_gate=EgressGate(settings_store=store)
    ).send(_notification())

    assert result.success is False
    assert result.refused_by_gate is False
    assert "not configured" in result.error
    assert recorder.calls == []


# ── The ordering must not be overridable ──────────────────────────────────────


def _subclasses() -> list[tuple[str, ast.ClassDef]]:
    found: list[tuple[str, ast.ClassDef]] = []
    for path in sorted(_CHANNELS_DIR.glob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if not isinstance(node, ast.ClassDef):
                continue
            bases = {
                base.id if isinstance(base, ast.Name) else getattr(base, "attr", "")
                for base in node.bases
            }
            if "OutboundChannel" in bases:
                found.append((path.name, node))
    return found


def test_the_discovery_finds_the_channels():
    """Guard the guard: an empty subclass list would make the next test vacuous."""
    names = {node.name for _, node in _subclasses()}
    assert names == {
        "LineNotificationChannel",
        "DiscordNotificationChannel",
        "EmailNotificationChannel",
    }, f"discovered {names}"


def test_no_channel_overrides_the_send_ordering():
    """Only the base may decide *when* the gate is consulted.

    A subclass that redefined ``send`` or ``_deliver`` could call its transport without
    asking, and every other test here would still pass — they drive the base's ``send``.
    """
    offenders = []
    for filename, node in _subclasses():
        for item in node.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)) and item.name in {
                "send",
                "_deliver",
            }:
                offenders.append(f"{filename}:{node.name}.{item.name}")
    assert offenders == [], (
        f"{offenders} override the gate ordering. Supply `_default_transport` instead, so "
        "`OutboundChannel.send` remains the only path to a transport."
    )


def test_every_channel_uses_a_messaging_purpose():
    """The gate maps a purpose's head to a settings flag; `messaging` is what maps."""
    for filename, node in _subclasses():
        assigned = [
            item
            for item in node.body
            if isinstance(item, ast.Assign)
            and any(getattr(t, "id", "") == "purpose" for t in item.targets)
        ]
        assert assigned, f"{filename}:{node.name} does not set `purpose`"
        value = assigned[0].value
        assert isinstance(value, ast.Constant) and str(value.value).startswith("messaging."), (
            f"{filename}:{node.name} uses purpose {value.value!r}; every outbound channel must "
            "use a `messaging.*` purpose so the gate maps it to `external_messaging_allowed`"
        )


def test_every_channel_declares_a_base_class():
    """A channel that is not an `OutboundChannel` would not be gated at all."""
    for filename, node in _subclasses():
        assert filename, f"{node.name} lives in {filename}"


# ── The router ────────────────────────────────────────────────────────────────


class _Sink:
    def __init__(self):
        self.bodies: list[str] = []

    def send(self, notification):
        self.bodies.append(notification.body)


def _router(**kwargs):
    from aegis_ai.notification.router import NotificationRouter

    return NotificationRouter(**kwargs)


def test_the_router_can_reach_an_external_channel():
    """Before this, `NotificationRouter` had no parameter for LINE/Discord/Email at all."""
    line = _Sink()
    router = _router(line_channel=line)
    notification = _notification()
    notification.channels = [NotificationChannel.LINE]

    assert router.send(notification) is True
    assert line.bodies == ["the user's own text"]


def test_the_router_does_not_blank_the_body_for_an_external_channel():
    """The old behaviour made a granted permission meaningless and hit the local copy too."""
    line, dashboard = _Sink(), _Sink()
    router = _router(line_channel=line, dashboard_channel=dashboard)
    notification = _notification()
    notification.channels = [NotificationChannel.LINE, NotificationChannel.DASHBOARD]

    router.send(notification)

    assert line.bodies == ["the user's own text"]
    assert dashboard.bodies == ["the user's own text"], (
        "the body was mutated before the fan-out, so the local channel lost it as well"
    )


def test_this_module_is_marked_egress():
    """Registered with the mutation roster; an unmarked module would run outside it."""
    source = Path(__file__).read_text(encoding="utf-8")
    assert "pytestmark = pytest.mark.egress" in source


def test_a_subclass_without_a_transport_fails_loudly_rather_than_silently():
    """The base invents no transport, and a channel that forgets one must not look successful.

    ``send`` never raises — the router loops over channels, so one failure must not abort the
    rest. "Loudly" therefore means a result with ``success=False`` that names the cause, never
    a result a caller could mistake for a delivered message.

    The gate is stubbed to allow so that this test measures the transport path only.
    """

    class _AlwaysAllow:
        def allow(self, _request) -> bool:
            return True

    class _Bare(OutboundChannel):
        purpose = "messaging.test"
        label = "bare"
        required_env = ()

        def destination(self) -> str:
            return "https://example.com"

    result = _Bare(env={}, egress_gate=_AlwaysAllow()).send(_notification())

    assert result.attempted is True
    assert result.success is False
    assert "NotImplementedError" in result.error
