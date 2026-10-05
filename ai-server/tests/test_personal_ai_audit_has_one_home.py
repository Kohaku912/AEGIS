"""The personal_ai audit convention has one home.

Measured 2026-10-06
-------------------
Six classes in six modules each carried an identical ``_audit`` method:

    if self._audit_manager is None:
        return
    try:
        self._audit_manager.log_decision(
            action=action, actor=<actor>, decision="success", reason=action, detail=detail
        )
    except Exception:
        <record the failure>

They differed only in ``actor`` -- and had **already drifted** on the level (five at
DEBUG, one at WARNING), which is what a copy does. Cycle 46 moved the body to
``personal_ai/storage.py::audit_decision`` with ``actor`` and ``level`` as parameters,
and left each ``_audit`` a one-line delegation.

The migration was proved **value-identical**: driving every old and new ``_audit`` with
a spy captured byte-equal kwargs for ``log_decision`` at all six sites.

The pin below fixes the *residue* -- where the fact is still spelled -- by equality, so
it fails both when a seventh copy appears and when one of the six is cleaned up.
"""

from __future__ import annotations

import ast
import logging
from pathlib import Path

import pytest

from aegis_ai.personal_ai.storage import audit_decision

_PKG = Path(__file__).resolve().parents[1] / "src" / "aegis_ai" / "personal_ai"

# The six `_audit` wrappers, by (module stem, class name).
_WRAPPERS = {
    "commitments": "CommitmentManager",
    "delegation": "DelegationPolicyStore",
    "hooks": "HookEngine",
    "interruption": "InterruptionController",
    "repair": "RepairManager",
    "social_proxy": "SocialProxy",
}

# The one site that reports a failed audit at WARNING rather than the DEBUG default.
_RECORDED_NON_DEFAULT_LEVEL = {"commitments.py": "logging.WARNING"}


def _trees() -> dict[str, ast.Module]:
    return {
        p.name: ast.parse(p.read_text(encoding="utf-8")) for p in sorted(_PKG.glob("*.py"))
    }


def _calls(tree: ast.Module, attr: str) -> list[ast.Call]:
    return [
        n
        for n in ast.walk(tree)
        if isinstance(n, ast.Call)
        and isinstance(n.func, ast.Attribute)
        and n.func.attr == attr
    ]


def _func(module: ast.Module, cls_name: str, fn_name: str) -> ast.FunctionDef:
    for cls in ast.walk(module):
        if isinstance(cls, ast.ClassDef) and cls.name == cls_name:
            for node in cls.body:
                if isinstance(node, ast.FunctionDef) and node.name == fn_name:
                    return node
    raise AssertionError(f"{cls_name}.{fn_name} not found")


def test_the_package_has_exactly_one_log_decision_call_site() -> None:
    """Equality, not a floor: a seventh copy fails this, and so does an over-eager cleanup."""
    sites = [
        f"{name}:{call.lineno}"
        for name, tree in _trees().items()
        for call in _calls(tree, "log_decision")
    ]
    assert sites == ["storage.py:108"], (
        f"the `log_decision` call sites moved or multiplied: {sites}. The audit convention "
        "must stay spelled once, in `personal_ai/storage.py::audit_decision`."
    )


def test_the_helper_is_where_log_decision_is_called() -> None:
    """The single call site must be inside `audit_decision`, not merely in storage.py."""
    tree = _trees()["storage.py"]
    helper = next(
        n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == "audit_decision"
    )
    calls = _calls(helper, "log_decision")
    assert len(calls) == 1, f"audit_decision holds {len(calls)} log_decision calls"


@pytest.mark.parametrize("stem,cls_name", sorted(_WRAPPERS.items()), ids=sorted(_WRAPPERS))
def test_each_audit_wrapper_delegates_to_the_helper(stem: str, cls_name: str) -> None:
    wrapper = _func(_trees()[f"{stem}.py"], cls_name, "_audit")
    delegates = [
        n
        for n in ast.walk(wrapper)
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == "audit_decision"
    ]
    assert len(delegates) == 1, f"{stem}.{cls_name}._audit no longer delegates to audit_decision"
    assert not _calls(wrapper, "log_decision"), (
        f"{stem}.{cls_name}._audit calls log_decision directly again"
    )


def _name_calls(tree: ast.Module, name: str) -> list[ast.Call]:
    return [
        n
        for n in ast.walk(tree)
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == name
    ]


def test_exactly_the_recorded_site_passes_a_non_default_level() -> None:
    """The drift that motivated the consolidation, pinned by name rather than smoothed over."""
    observed: dict[str, str] = {}
    for name, tree in _trees().items():
        for call in _name_calls(tree, "audit_decision"):
            for kw in call.keywords:
                if kw.arg == "level":
                    observed[name] = ast.unparse(kw.value)
    assert observed == _RECORDED_NON_DEFAULT_LEVEL, (
        f"the set of audit sites overriding the level changed: {observed}"
    )


# ── behavioural ────────────────────────────────────────────────────────────


class _RaisingAudit:
    def log_decision(self, **kwargs):
        raise RuntimeError("audit manager unavailable")


class _OkAudit:
    def __init__(self) -> None:
        self.calls: list[dict] = []

    def log_decision(self, **kwargs):
        self.calls.append(kwargs)


def test_a_failed_audit_is_named_at_the_default_level(caplog) -> None:
    with caplog.at_level(logging.DEBUG, logger="probe"):
        audit_decision(
            _RaisingAudit(),
            actor="probe_actor",
            action="probe_action",
            detail={},
            logger=logging.getLogger("probe"),
        )
    records = [r for r in caplog.records if r.name == "probe"]
    assert len(records) == 1, f"expected one record, got {records}"
    assert records[0].levelno == logging.DEBUG
    assert "probe_action" in records[0].getMessage()


def test_the_level_parameter_is_honoured(caplog) -> None:
    with caplog.at_level(logging.DEBUG, logger="probe"):
        audit_decision(
            _RaisingAudit(),
            actor="probe_actor",
            action="probe_action",
            detail={},
            logger=logging.getLogger("probe"),
            level=logging.WARNING,
        )
    records = [r for r in caplog.records if r.name == "probe"]
    assert records and records[0].levelno == logging.WARNING


def test_a_successful_audit_stays_silent(caplog) -> None:
    audit = _OkAudit()
    with caplog.at_level(logging.DEBUG, logger="probe"):
        audit_decision(
            audit, actor="probe_actor", action="a", detail={}, logger=logging.getLogger("probe")
        )
    assert audit.calls == [
        {"action": "a", "actor": "probe_actor", "decision": "success", "reason": "a", "detail": {}}
    ]
    assert [r for r in caplog.records if r.name == "probe"] == []


def test_an_absent_audit_manager_stays_silent(caplog) -> None:
    """Control: no audit manager at all is a legitimate absence, not a failure."""
    with caplog.at_level(logging.DEBUG, logger="probe"):
        audit_decision(
            None, actor="probe_actor", action="a", detail={}, logger=logging.getLogger("probe")
        )
    assert [r for r in caplog.records if r.name == "probe"] == []
