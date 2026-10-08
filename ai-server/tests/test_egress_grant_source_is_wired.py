"""The gate's second permission path is attached at the composition root.

``aegis_ai/egress/permissions.py`` supplies the permission path the 2026-09-30 re-scope
requires: a permission the user gave about a **specific** destination, recorded as an
ordinary confirmation whose ``capability_id`` is ``egress.external_permission``.

It was implemented on 2026-10-03 and **left unwired** — deliberately, because wiring it
*widens* what may leave the local environment, which is a decision about the constraint
rather than a cleanup. That decision lived in ``DELEGATION.md`` §4 item 22, and the owner
took it on 2026-10-08: **wire it**. This file is what the old
``test_egress_grant_source_is_unwired.py`` became.

Measured 2026-10-08, before the change, by driving the gate the composition root actually
builds: with the shipped ``settings.json``, ``gate._permission_source`` was ``None``, and a
request to a host that is neither allowlisted nor local was **denied identically** whether
or not the user had approved a grant for it. The mechanism was reading the grant correctly
— ``ConfirmationGrantSource(store).grants()`` returned it — and nothing consulted it. So a
recorded permission changed nothing. After the change the same request is **allowed**, and
only for that exact ``(host, purpose)``.

What is pinned is the **property**, not the mechanism: the process-wide gate answers from
the runtime's *own* confirmation store. Wiring it the other way — moving the store's
construction above the gate and passing ``permission_source=`` into
``configure_egress_gate`` — would satisfy this pin too. That is correct; the pin is about
the composed behaviour, so it does not freeze the one-line shape.

Two failure modes, and what each looks like here:

* **The wiring is removed.** ``test_the_composition_root_attaches_the_grant_source...``
  reddens on the ``None`` source, and the end-to-end test reddens on ``deny``.
* **The mechanism is deleted.** The module-level import below fails at *collection*, with
  an ``ImportError`` naming the class — not an ``AttributeError`` from inside a test.

The direction the old pin guarded is gone on purpose: it used to fail if the source was
attached *at all*. Wiring it is now the intended state, so that assertion has no
counterpart. What still keeps the change honest is elsewhere — ``test_egress_permission.py``
pins ``ConfirmationGrantSource``'s public surface to exactly ``{grants, grant_for}`` (so it
cannot grow a way to *ask*), and ``test_forced_gate_stays_retired.py`` pins that the gate
never requests. Read-only by construction: attaching this source cannot re-introduce the
retired forced gate.

Why this file stubs ``_persist`` and uses a per-run host
--------------------------------------------------------
**`AEGIS_DATA_DIR` is not honoured by the composition root.** Measured 2026-10-08:
``runtime._build_runtime`` computes ``base_dir = Path(__file__).resolve().parents[2]`` and
``data_dir = str(base_dir / "data")``; nothing under ``src/`` reads ``AEGIS_DATA_DIR``.
⚠️ **That scope is narrower than it reads** (added 2026-10-09): the three shipped capability
executors under ``apps/builtin/ai-server/memory/{save,search,sleep}/executor.py`` **do** read it,
so "ignored by the composition root" is not "inert". Setting the variable relocates what those
capabilities read and write and nothing else — a split brain, pinned in
``tests/test_data_dir_is_honoured_by_the_leaf_not_the_root.py``.
Four test modules set it (``test_composition_root_resolves_llm_layers.py``,
``test_runtime_singleton.py``, ``agents/test_openhands_backend.py`` and this one) believing
it isolates them — it does not. So a test that boots the runtime and **writes** writes into
the repository's real, gitignored ``ai-server/data/``.

The first draft of this pin did exactly that and was caught by its own control: the second
run found the grant the first run had persisted, and the "denied before anything was
recorded" assertion went red. Two consequences, both applied here:

* ``ConfirmationStore._persist`` is replaced with a no-op, so the confirmations live only in
  memory. The store's read surface (``all``) is what the gate consumes, and it reads
  ``_items``, so the pin still exercises the real composed wiring with no disk writes.
* The hosts carry a per-run token, so a record left behind by an earlier run can never
  satisfy the assertions in this one.

The underlying defect — a suite-wide isolation convention that is a no-op — is recorded as
open work rather than fixed here; fixing it means deciding whether the composition root
should honour the variable at all.
"""

from __future__ import annotations

import uuid

import pytest

from aegis_ai.egress import get_egress_gate, is_local_destination
from aegis_ai.egress.gate import EgressDecision, EgressRequest
from aegis_ai.egress.permissions import (
    EGRESS_PERMISSION_CAPABILITY,
    ConfirmationGrantSource,
    format_scope,
)

pytestmark = pytest.mark.egress

#: A purpose whose feature flag is **on** in the shipped settings, so the *host* is the
#: only thing standing between the request and an ``ALLOW``. That is what makes the grant
#: visible: with the flag off, a denial could be blamed on the flag instead of the host.
_PURPOSE = "llm.chat"

#: Fresh per run, so no record persisted by an earlier run can answer for this one.
_TOKEN = uuid.uuid4().hex[:8]


def _host(label: str) -> str:
    """A destination name nothing else in the shipped configuration can open."""
    return f"api.{label}-{_TOKEN}.example"


_PERMITTED = _host("grant-pin")
_NEVER_RECORDED = _host("never-recorded")
_REJECTED = _host("rejected")
_UNANSWERED = _host("unanswered")


@pytest.fixture(autouse=True)
def _never_leak_the_runtime_or_the_gate():
    """Boot the real runtime, then leave neither it nor the gate behind.

    Same shape as ``test_composition_root_resolves_llm_layers.py``'s fixture, and for the
    same reason: the runtime's ``status-check`` thread re-resolves the LAN endpoints into a
    process-global cache and would corrupt ``test_endpoint_resolver.py`` roughly ninety
    files away.

    The gate needs its own reset because it is a **separate** process-global singleton:
    ``_build_runtime`` replaces it, and the copy this test leaves behind has a permission
    source pointing at the runtime's confirmation store. A later test that reads
    ``get_egress_gate()`` without configuring it would then be answered from that store.
    """
    yield

    from aegis_ai.egress import configure_egress_gate
    from aegis_ai.runtime import reset_runtime_for_tests

    reset_runtime_for_tests()
    configure_egress_gate()  # every lock closed, no permission source


def _runtime(monkeypatch, tmp_path):
    """The real composition root, with its confirmation writes kept in memory.

    ``AEGIS_DATA_DIR`` is set for consistency with the sibling tests, but it is **not** what
    makes this hermetic — the composition root ignores it (see the module docstring). The
    in-memory store is.
    """
    monkeypatch.setenv("AEGIS_DATA_DIR", str(tmp_path / "data"))
    from aegis_ai.runtime import get_runtime

    runtime = get_runtime()
    # The confirmations this test records must not reach the repository's real data dir.
    monkeypatch.setattr(runtime.confirmation_store, "_persist", lambda item: None)
    return runtime


def _request(host: str) -> EgressRequest:
    """A request that carries user information, so the gate must find a permission.

    ``carries_user_information`` defaults to ``True``; it is passed explicitly so that a
    future change to that default cannot silently turn this file into a no-op — a request
    carrying nothing is allowed without any permission at all.
    """
    return EgressRequest(
        destination=f"https://{host}/v1/chat",
        purpose=_PURPOSE,
        component="test.egress_grant_source_is_wired",
        data_summary="a question about the user's schedule",
        carries_user_information=True,
    )


def _record(store, host: str, *, approve: bool) -> None:
    """Record an egress permission for ``host``, then approve or reject it."""
    rec = store.request(
        capability_id=EGRESS_PERMISSION_CAPABILITY,
        tool_name="egress.external_permission",
        summary=f"Allow sending to {host} for {_PURPOSE}?",
        target=format_scope(host, _PURPOSE),
    )
    if approve:
        store.approve(rec.approval_id, decided_by="owner")
    else:
        store.reject(rec.approval_id, decided_by="owner")


# ── The wiring: the gate the composition root builds reads the runtime's own store ──


def test_the_composition_root_attaches_the_grant_source_to_the_process_wide_gate(
    monkeypatch, tmp_path
) -> None:
    runtime = _runtime(monkeypatch, tmp_path)
    gate = get_egress_gate()

    source = gate._permission_source
    assert isinstance(source, ConfirmationGrantSource), (
        f"the process-wide gate's permission source is {source!r}, not a "
        f"{ConfirmationGrantSource.__name__}. The recorded-grant path is implemented and the "
        "gate consults it on every check(), but nothing supplies it — so a permission the "
        "user gave about a specific destination changes nothing. See DELEGATION.md §4 item "
        "22 (the owner chose 'wire it' on 2026-10-08) and PROJECT_STATUS_REVIEW.md §3.2."
    )

    # Identity, not just type: a source reading some *other* store would answer from a
    # different set of decisions than the one the dashboard and the loop read.
    assert source._store is runtime.confirmation_store, (
        "the gate's permission source reads a different confirmation store than the "
        "runtime's — the user's answer would be recorded in one place and consulted from "
        "another, so a grant would be invisible exactly where it is needed"
    )


def test_a_recorded_grant_opens_exactly_the_destination_the_user_permitted(
    monkeypatch, tmp_path
) -> None:
    """End to end through the composed gate: record, answer, and watch the verdict move.

    Every step is a control for the next. If the *first* assertion fails the probe is not a
    probe; if the later ones fail while the first passes, the grant is not what moved it.
    """
    runtime = _runtime(monkeypatch, tmp_path)
    gate = get_egress_gate()
    store = runtime.confirmation_store

    allowlist = {
        str(host).strip().lower()
        for host in (runtime.settings_store.get().privacy.egress_allowed_hosts or [])
    }
    assert _PERMITTED not in allowlist, (
        f"{_PERMITTED} is in the shipped egress allowlist, so this pin would pass without "
        "the grant and prove nothing about the second permission path. Pick a host the "
        "standing configuration cannot open."
    )
    assert not is_local_destination(f"https://{_PERMITTED}/v1/chat"), (
        f"{_PERMITTED} resolves to a local destination, which needs no permission at all"
    )

    assert gate.check(_request(_PERMITTED)) is EgressDecision.DENY, (
        "a request to an unpermitted, non-allowlisted host was allowed before the user "
        "recorded anything — something other than the grant is opening it"
    )

    _record(store, _PERMITTED, approve=True)
    assert gate.check(_request(_PERMITTED)) is EgressDecision.ALLOW, (
        "the user approved a grant for exactly this (host, purpose) and the gate still "
        "denied it — the recorded-grant path is not reaching the composed gate"
    )

    assert gate.check(_request(_NEVER_RECORDED)) is EgressDecision.DENY, (
        f"a grant for {_PERMITTED} also opened {_NEVER_RECORDED} — the match must be exact, "
        "with no wildcard"
    )

    _record(store, _REJECTED, approve=False)
    assert gate.check(_request(_REJECTED)) is EgressDecision.DENY, (
        "a *rejected* confirmation permitted the destination — only a status the user "
        "actually gave counts as a permission"
    )

    store.request(
        capability_id=EGRESS_PERMISSION_CAPABILITY,
        tool_name="egress.external_permission",
        summary=f"Allow sending to {_UNANSWERED} for {_PURPOSE}?",
        target=format_scope(_UNANSWERED, _PURPOSE),
    )
    assert gate.check(_request(_UNANSWERED)) is EgressDecision.DENY, (
        "an *unanswered* confirmation permitted the destination — a question AEGIS asked "
        "is not a decision the user made, and treating it as one would be the retired "
        "forced gate's behaviour wearing the new mechanism's name"
    )
