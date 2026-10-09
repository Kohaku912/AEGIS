"""The trigger engine's default rules name events that nothing in the repo produces.

The event-driven core was constructed, subscribed and consumed by branch ① of
``DELEGATION.md`` section 4 item 24 (see ``test_event_driven_core_is_constructed.py``). This pin
measures the *other* half of "event-driven": whether the rules that decide when to wake can ever
fire. They largely cannot.

**Measured 2026-10-09 (cycle 133).** ``create_default_rules()`` returns **12** rules. Scanning the
live producers -- ``ai-server/src`` (``publish_event`` / ``_emit_event`` / ``build_event`` /
``event_type=``), ``pc-server/src`` (``event_type:`` / ``pending.push((``), the Android client
(``eventType =``), and the room/browser servers -- yields **58** distinct event types. Of the
**11** rules that name a specific type, **exactly one** has a producer:

=========================  ============================  ==============================
rule                       pattern                       produced?
=========================  ============================  ==============================
``pc-screen-change``       ``pc.screen_changed``         **yes** (``ai-server`` client)
``user-request``           ``user.request``              no
``dev-test-failure``       ``dev.test_failed``           no
``dev-ci-error``           ``dev.ci_error``              no
``android-notification``   ``android.notification_received``  no -- see below
``android-call``           ``android.incoming_call``     no
``web-rss-updated``        ``web.rss_updated``           no
``web-github-issue``       ``web.github_new_issue``      no
``room-temperature-change````room.temperature_changed``   no
``room-motion-detected``   ``room.motion_detected``      no -- see below
``security-alert``         ``*.security_*``              no
=========================  ============================  ==============================

The near-misses are the evidence that this is naming drift, not a missing feature:

* the rule expects ``android.notification_received``; the Android client emits
  ``android.notification.posted`` (``AegisGrpcClient.kt``);
* the rule expects ``room.motion_detected`` / ``room.temperature_changed``; the room ingest emits
  ``room.motion`` / ``room.still`` / ``room.audio.segment``;
* ``pc-screen-change`` *does* match -- but only because **ai-server's own** ``pc_server_client.py``
  publishes ``pc.screen_changed``. The server that actually observes the PC emits
  ``pc.window.opened`` / ``pc.window.closed`` / ``pc.ui.focus_changed`` instead.

**The 12th rule cannot rescue them.** ``high-severity-catchall`` (``*``) needs ``severity >= 9``.
Measured: ``build_event`` defaults ``severity=0`` and the SDK's ``make_event`` defaults ``3``, and
no producer passes a higher value -- so the catch-all is unreachable from the servers too.

**Consequence.** ``TriggerEngine.on_event`` is subscribed with no filter, so events *arrive*; but
``stats.tasks_generated`` stays at 0 for every real event, and ``AutonomousLoop._drain_trigger_tasks``
returns ``[]`` forever. The loop's L2 bridge is still reached by the *direct* L1 path -- this is not
a break in the L1 -> L2 hand-off -- but the trigger engine itself is starved rather than idle.

**What this pin does not do.** Aligning the rules to the real event names (or emitting the events
the rules expect) is a **behaviour change** and an owner decision -- recorded as ``DELEGATION.md``
section 4 item 93. This pin only makes the gap *stable and measurable*, so a future fix or a new
rule is a visible event rather than a silent one.

The scan is a claim too, so its predicate is recorded: a producer is a string literal in a
**documented emission context** (not a bare literal grep), the roots and the excluded directories
are enumerated below, and the census is asserted non-vacuous and multi-source.
"""

from __future__ import annotations

import re
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]

#: Emission contexts, per language. A bare dotted literal is *not* enough: capability ids
#: (``pc.get_screenshot``) share the shape of event types.
_PY = (
    re.compile(r'publish_event\(\s*"([^"]+)"'),
    re.compile(r'_emit_event\(\s*[A-Za-z_][A-Za-z0-9_.]*\s*,\s*"([^"]+)"'),
    re.compile(r'build_event\(\s*"([^"]+)"'),
    re.compile(r'event_type\s*=\s*"([^"]+)"'),
    re.compile(r'make_event\(\s*event_type\s*=\s*"([^"]+)"'),
)
_RS = (
    re.compile(r'event_type:\s*"([^"]+)"'),
    re.compile(r'pending\.push\(\(\s*"([^"]+)"'),
)
_KT = (
    re.compile(r'eventType\s*=\s*"([^"]+)"'),
    re.compile(r'->\s*"((?:android|pc|web|room|user|dev)\.[a-z0-9_.]+)"'),
)

#: (label, root, glob, patterns). Every root must contribute, or the census is blind.
_SOURCES = (
    ("ai-server", _ROOT / "ai-server" / "src", "*.py", _PY),
    ("room-server", _ROOT / "room-server" / "src", "*.py", _PY),
    ("browser-server", _ROOT / "browser-server" / "src", "*.py", _PY),
    ("sdk", _ROOT / "packages" / "aegis-sdk-python" / "aegis_sdk", "*.py", _PY),
    ("pc-server", _ROOT / "pc-server" / "src", "*.rs", _RS),
    ("android-server", _ROOT / "android-server" / "app" / "src" / "main", "*.kt", _KT),
)

#: Directories that hold generated protobuf stubs or build output, not producers.
_EXCLUDE = frozenset({".venv", "node_modules", "build", "target", "generated", "__pycache__", ".test-tmp"})

#: The servers that actually publish to the bus. Measured 2026-10-09: only these three.
_EMITTERS = frozenset({"ai-server", "pc-server", "android-server"})

#: Scanned, but with **no emission API at all** -- recorded so that one starting to publish is a
#: visible change. ``room-server`` and ``browser-server`` serve capabilities and never emit; the
#: SDK is a library, not a server.
_SILENT_ROOTS = frozenset({"room-server", "browser-server", "sdk"})

#: The whole default rule set, by ``rule_id`` -> ``event_type_pattern``. Asserted by **equality**:
#: a new rule, a deleted rule, or a renamed pattern all fail rather than silently re-scoping.
_RULES: dict[str, str] = {
    "user-request": "user.request",
    "dev-test-failure": "dev.test_failed",
    "dev-ci-error": "dev.ci_error",
    "pc-screen-change": "pc.screen_changed",
    "android-notification": "android.notification_received",
    "android-call": "android.incoming_call",
    "web-rss-updated": "web.rss_updated",
    "web-github-issue": "web.github_new_issue",
    "room-temperature-change": "room.temperature_changed",
    "room-motion-detected": "room.motion_detected",
    "security-alert": "*.security_*",
    "high-severity-catchall": "*",
}

#: The catch-all matches every *type*; it is separated out because it is gated on severity.
_CATCH_ALL = "high-severity-catchall"

#: The finding, in one line: which named patterns a producer exists for.
_MATCHED = frozenset({"pc.screen_changed"})

#: And its complement -- the 10 rules that can never fire.
_UNMATCHED = frozenset(
    {
        "user.request",
        "dev.test_failed",
        "dev.ci_error",
        "android.notification_received",
        "android.incoming_call",
        "web.rss_updated",
        "web.github_new_issue",
        "room.temperature_changed",
        "room.motion_detected",
        "*.security_*",
    }
)

#: The diagnosis: rule -> (its pattern, the event the servers emit for the same situation).
#: Recorded so that a future alignment is a visible change to this table, not a silent one.
_NEAR_MISSES: dict[str, tuple[str, tuple[str, ...]]] = {
    "android-notification": ("android.notification_received", ("android.notification.posted",)),
    "room-motion-detected": ("room.motion_detected", ("room.motion", "room.still")),
    "pc-screen-change": (
        "pc.screen_changed",
        ("pc.window.opened", "pc.window.closed", "pc.ui.focus_changed"),
    ),
}

_MIN_PRODUCERS = 40


def _producers() -> dict[str, set[str]]:
    """event_type -> the source labels that emit it, from documented emission contexts."""
    out: dict[str, set[str]] = {}
    for label, root, glob, patterns in _SOURCES:
        assert root.is_dir(), f"the producer scan root is gone: {root}"
        for path in sorted(root.rglob(glob)):
            if _EXCLUDE & set(path.parts):
                continue
            text = path.read_text(encoding="utf-8", errors="replace")
            for pattern in patterns:
                for found in pattern.findall(text):
                    out.setdefault(found, set()).add(label)
    return out


def _rules():
    import sys

    src = str(_ROOT / "ai-server" / "src")
    if src not in sys.path:
        sys.path.insert(0, src)
    from trigger_engine import create_default_rules

    return create_default_rules()


def test_the_default_rule_set_is_exactly_these() -> None:
    """A budget on the rule set: 12 rules, and each ``rule_id`` still names its recorded pattern."""
    rules = _rules()
    observed = {rule.rule_id: rule.event_type_pattern for rule in rules}
    assert observed == _RULES, (
        "the default trigger rule set changed; re-measure the producer census and update "
        f"_RULES/_MATCHED/_UNMATCHED together.\n  expected {_RULES}\n  observed {observed}"
    )


def test_the_producer_census_is_not_vacuous_and_names_the_emitters() -> None:
    """Control: the scan finds real producers, and the set of emitters is exactly as recorded.

    Also a finding in its own right: two capability servers (``room``, ``browser``) publish
    **nothing at all**, yet the default rules carry ``room.*`` and ``web.*`` entries for them.
    """
    producers = _producers()
    assert len(producers) >= _MIN_PRODUCERS, (
        f"only {len(producers)} producers found (expected >= {_MIN_PRODUCERS}) -- an emission "
        "context regex no longer matches, so 'no producer' below would be a lie"
    )
    labels = {label for files in producers.values() for label in files}
    assert labels == _EMITTERS, (
        "the set of servers that publish events changed -- a dead rule may now be able to fire, "
        f"or an emitter went silent.\n  expected {sorted(_EMITTERS)}\n  observed {sorted(labels)}"
    )
    assert _SILENT_ROOTS.isdisjoint(labels), (
        f"a root with no emission API started producing: {sorted(_SILENT_ROOTS & labels)}"
    )


def test_the_matcher_still_distinguishes_a_near_miss() -> None:
    """Control for the matcher itself: it accepts the exact name and rejects the drift.

    The pattern is read from the rule, not written as a literal -- a control that hard-codes the
    pattern cannot notice the rule being widened to swallow the drift (found by mutation M4, which
    survived the first version of this test).
    """
    rule = next(r for r in _rules() if r.rule_id == "android-notification")
    pattern = rule.event_type_pattern
    assert rule._match_pattern(pattern, pattern), "the matcher rejects its own pattern"
    assert not rule._match_pattern(pattern, "android.notification.posted"), (
        "the matcher now treats the drift as a match, so the finding below is meaningless"
    )


def test_only_pc_screen_changed_has_a_producer() -> None:
    """The finding: exactly one named rule can fire, and exactly ten cannot."""
    producers = _producers()
    matched, unmatched = set(), set()
    for rule in _rules():
        if rule.rule_id == _CATCH_ALL:
            continue
        (matched if any(rule._match_pattern(rule.event_type_pattern, et) for et in producers)
         else unmatched).add(rule.event_type_pattern)
    assert matched == _MATCHED, f"the matched set moved: {sorted(matched)}"
    assert unmatched == _UNMATCHED, f"the unmatched set moved: {sorted(unmatched)}"
    assert matched | unmatched == set(_RULES.values()) - {"*"}, (
        "the two sets no longer partition the named patterns"
    )


def test_the_near_misses_are_still_near_misses() -> None:
    """Pin the diagnosis, not just the count: each drift pair must still hold as recorded.

    A count alone would not tell a reader *why* a rule is dead, and would not notice if the
    server started emitting the expected name (which is the fix).
    """
    rules = {rule.rule_id: rule for rule in _rules()}
    producers = _producers()
    for rule_id, (pattern, alternatives) in _NEAR_MISSES.items():
        assert rules[rule_id].event_type_pattern == pattern, (
            f"{rule_id} no longer names {pattern}"
        )
        for alt in alternatives:
            assert alt in producers, (
                f"{alt} is no longer produced -- if it was renamed to {pattern} the rule now "
                "fires and this record must move"
            )


def test_the_catch_all_needs_a_severity_nothing_sends() -> None:
    """The 12th rule cannot rescue the other 11: its gate is above every producer's default."""
    from inspect import signature

    import sys

    sys.path.insert(0, str(_ROOT / "ai-server" / "src"))
    from aegis_ai.event.helpers import build_event

    catch_all = next(r for r in _rules() if r.rule_id == _CATCH_ALL)
    assert catch_all.event_type_pattern == "*" and catch_all.min_severity == 9, (
        "the catch-all changed shape; re-measure whether it is reachable"
    )

    def _default(fn, name: str) -> int:
        return signature(fn).parameters[name].default

    assert _default(build_event, "severity") == 0, (
        "`build_event` now defaults a non-zero severity -- ai-server's own events could reach "
        "the catch-all, which changes the finding"
    )

    sdk_events = _ROOT / "packages" / "aegis-sdk-python" / "aegis_sdk" / "events.py"
    text = sdk_events.read_text(encoding="utf-8")
    assert "severity: int = 3" in text, (
        "the SDK's `make_event` severity default changed; re-measure the catch-all's reach"
    )
