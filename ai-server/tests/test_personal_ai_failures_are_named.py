"""The personal_ai/ package names its failures.

Measured 2026-10-06
-------------------
Six modules of ``personal_ai/`` had **no logger at all** and **fourteen** handlers whose
whole body was ``pass`` -- every one on a live path (the composition root constructs
``DelegationPolicyStore`` at ``runtime.py:1110``, ``HookEngine`` at ``:1116``,
``InterruptionController`` at ``:1126``, ``SocialProxy`` at ``:1134``,
``RepairManager`` at ``:1299`` and ``SituationModel`` at ``:1109``).

Two of the fourteen were a *duplicated* defect: five modules each carried an identical
``_audit`` method -- ``except Exception: pass`` wrapped around
``audit_manager.log_decision(...)``, differing only in the actor string. **An audit trail
that can fail silently is not an audit trail.**

The rest: ``__init__`` subscribe failures (``hooks``, ``situation``) that leave the object
constructed and looking healthy but deaf; ``HookEngine._emit_self_call``;
``SituationModel.get_state``; ``InterruptionController.decide`` (the quiet-hours check
silently did not run); ``RepairManager.list_history`` / ``_record_lesson`` /
``_present_unrepairable``; ``SocialProxy.receive_event``.

All fourteen now log at DEBUG (behaviour-preserving: a record only), and the package
gained six loggers. One file, ``interruption.py``, was CRLF in the working tree while its
blob is LF (``attr/text eol=lf``); it was normalised here -- git never saw the difference,
so no line-ending churn is committed.

Scope
-----
The unit is cycle 16's: **no handler in ``personal_ai/`` is a bare ``pass``**. Handlers
that produce a value the caller receives stay out -- that is a different, milder class.
"""

from __future__ import annotations

import ast
import logging
from pathlib import Path

import pytest

from aegis_ai.personal_ai.delegation import DelegationPolicyStore
from aegis_ai.personal_ai.hooks import HookEngine
from aegis_ai.personal_ai.interruption import InterruptionController
from aegis_ai.personal_ai.repair import RepairManager
from aegis_ai.personal_ai.situation import SituationModel
from aegis_ai.personal_ai.social_proxy import SocialProxy

_PKG = Path(__file__).resolve().parents[1] / "src" / "aegis_ai" / "personal_ai"

# module stem -> logger name (the six that gained one this cycle).
_LOGGERS = {
    "delegation": "aegis_ai.personal_ai.delegation",
    "hooks": "aegis_ai.personal_ai.hooks",
    "interruption": "aegis_ai.personal_ai.interruption",
    "repair": "aegis_ai.personal_ai.repair",
    "situation": "aegis_ai.personal_ai.situation",
    "social_proxy": "aegis_ai.personal_ai.social_proxy",
}

# (class, logger name) -- the five members of the duplicated `_audit` family.
_AUDIT_FAMILY = [
    (DelegationPolicyStore, "aegis_ai.personal_ai.delegation"),
    (HookEngine, "aegis_ai.personal_ai.hooks"),
    (InterruptionController, "aegis_ai.personal_ai.interruption"),
    (RepairManager, "aegis_ai.personal_ai.repair"),
    (SocialProxy, "aegis_ai.personal_ai.social_proxy"),
]


# ── structural: no bare `pass` survives in the package ─────────────────────


def _all_pass_handlers() -> list[str]:
    found: list[str] = []
    for module in sorted(_PKG.glob("*.py")):
        tree = ast.parse(module.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.ExceptHandler) and node.body and all(
                isinstance(stmt, ast.Pass) for stmt in node.body
            ):
                found.append(f"{module.name}:{node.lineno}")
    return found


def test_no_handler_in_personal_ai_swallows_without_a_record() -> None:
    silent = _all_pass_handlers()
    assert silent == [], f"handler(s) still swallow with a bare `pass`: {silent}"


def test_the_package_scan_is_not_vacuous() -> None:
    """Control: the walk must see the package's handlers, not a slice."""
    handlers = 0
    for module in sorted(_PKG.glob("*.py")):
        tree = ast.parse(module.read_text(encoding="utf-8"))
        handlers += sum(1 for n in ast.walk(tree) if isinstance(n, ast.ExceptHandler))
    assert handlers >= 20, f"only {handlers} handlers found -- the walk is broken"


@pytest.mark.parametrize("stem,logger_name", sorted(_LOGGERS.items()), ids=sorted(_LOGGERS))
def test_every_module_has_its_logger(stem: str, logger_name: str) -> None:
    source = (_PKG / f"{stem}.py").read_text(encoding="utf-8")
    assert f'logger = logging.getLogger("{logger_name}")' in source, (
        f"{stem}.py lost its logger"
    )


# ── behavioural: the duplicated `_audit` family ────────────────────────────


class _RaisingAudit:
    def log_decision(self, **kwargs):
        raise RuntimeError("audit manager unavailable")


class _OkAudit:
    def __init__(self) -> None:
        self.calls: list[dict] = []

    def log_decision(self, **kwargs):
        self.calls.append(kwargs)
        return None


def _bare(cls):
    """An instance without running ``__init__`` -- only ``_audit_manager`` is needed."""
    return object.__new__(cls)


@pytest.mark.parametrize("cls,logger_name", _AUDIT_FAMILY, ids=[c.__name__ for c, _ in _AUDIT_FAMILY])
def test_the_audit_family_names_its_failure(cls, logger_name, caplog) -> None:
    instance = _bare(cls)
    instance._audit_manager = _RaisingAudit()

    with caplog.at_level(logging.DEBUG, logger=logger_name):
        instance._audit("probe_action", {"k": "v"})  # must not raise

    messages = [r.getMessage() for r in caplog.records if r.name == logger_name]
    assert any("probe_action" in m for m in messages), (
        f"{cls.__name__}._audit swallowed a failed audit; got {messages}"
    )


@pytest.mark.parametrize("cls,logger_name", _AUDIT_FAMILY, ids=[c.__name__ for c, _ in _AUDIT_FAMILY])
def test_a_successful_audit_stays_silent(cls, logger_name, caplog) -> None:
    """Control: a working audit must not warn."""
    instance = _bare(cls)
    audit = _OkAudit()
    instance._audit_manager = audit

    with caplog.at_level(logging.DEBUG, logger=logger_name):
        instance._audit("probe_action", {})

    assert audit.calls, "the audit was not even attempted -- the double is wrong"
    assert [r for r in caplog.records if r.name == logger_name] == []


@pytest.mark.parametrize("cls,logger_name", _AUDIT_FAMILY, ids=[c.__name__ for c, _ in _AUDIT_FAMILY])
def test_an_absent_audit_manager_stays_silent(cls, logger_name, caplog) -> None:
    """Control: no audit manager at all is a legitimate absence, not a failure."""
    instance = _bare(cls)
    instance._audit_manager = None

    with caplog.at_level(logging.DEBUG, logger=logger_name):
        instance._audit("probe_action", {})

    assert [r for r in caplog.records if r.name == logger_name] == []


# ── behavioural: the subscribe and situation-read paths ────────────────────


class _RaisingSubscriber:
    def subscribe(self, handler):
        raise RuntimeError("event bus unavailable")


class _OkSubscriber:
    def subscribe(self, handler):
        self.handler = handler


def test_a_failed_subscribe_is_named(tmp_path, caplog) -> None:
    with caplog.at_level(logging.DEBUG, logger="aegis_ai.personal_ai.situation"):
        SituationModel(data_dir=str(tmp_path), event_manager=_RaisingSubscriber())

    messages = [r.getMessage() for r in caplog.records if r.name == "aegis_ai.personal_ai.situation"]
    assert any("subscribe" in m for m in messages), f"no record; got {messages}"


def test_a_successful_subscribe_stays_silent(tmp_path, caplog) -> None:
    with caplog.at_level(logging.DEBUG, logger="aegis_ai.personal_ai.situation"):
        SituationModel(data_dir=str(tmp_path), event_manager=_OkSubscriber())

    assert [r for r in caplog.records if r.name == "aegis_ai.personal_ai.situation"] == []


class _RaisingUserState:
    def get_current_user_state(self):
        raise RuntimeError("user state unavailable")


def test_a_failed_situation_read_is_named(tmp_path, caplog) -> None:
    model = SituationModel(data_dir=str(tmp_path))
    model._user_state_manager = _RaisingUserState()

    with caplog.at_level(logging.DEBUG, logger="aegis_ai.personal_ai.situation"):
        state = model.get_state()

    assert state["state"] == "unknown", "the fallback value changed"
    messages = [r.getMessage() for r in caplog.records if r.name == "aegis_ai.personal_ai.situation"]
    assert any("user state" in m for m in messages), f"no record; got {messages}"


def test_an_absent_user_state_manager_stays_silent(tmp_path, caplog) -> None:
    """Control: no user-state manager is a legitimate absence, not a failure."""
    model = SituationModel(data_dir=str(tmp_path))

    with caplog.at_level(logging.DEBUG, logger="aegis_ai.personal_ai.situation"):
        state = model.get_state()

    assert state["state"] == "unknown"
    assert [r for r in caplog.records if r.name == "aegis_ai.personal_ai.situation"] == []
