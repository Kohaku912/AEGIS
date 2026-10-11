"""The audit sink is wired into three services and never written to -- the gate, which shares the
same ``self._audit`` attribute, does write (item 113).

The composition root (``runtime.py::_build_runtime``) hands an ``AuditManager`` to three live
services.  Each stores it on ``self`` and **no method ever reads it**:

* ``social/manager.py::SocialManager`` -- ``audit_manager`` -> ``self._audit``
* ``task/execution_engine.py::TaskExecutionEngine`` -- ``audit_manager`` -> ``self._audit_manager``
* ``backup/retention.py::RetentionManager`` -- ``audit_log`` -> ``self._audit``

All three are wired (``_build_runtime`` passes ``audit_manager=`` / ``audit_log=``), so this is the
*wired-but-ignored* shape of item 112, not the *unsuppliable* shape of item 111.

**The control is the gate.**  ``egress/gate.py::EgressGate`` takes a parameter with the **same name**
(``audit``) and stores it on the **same attribute** (``self._audit``) -- and *does* use it:
``EgressGate._record`` loads ``self._audit`` and calls ``append(...)`` on it.  So the same attribute
name is dead in two of these classes and live in the gate: the verdict is per-class, and the sink is
demonstrably usable.  A name-keyed census cannot produce two answers for one name.

**Why the census must be class-scoped.**  ``self._audit`` is Loaded 91 times elsewhere in ``src/``
and ``self._audit_manager`` 19 times -- every one of those is *outside* the owning module, so a
global scan calls all three read and reports zero dead sinks here.

**One member is already documented.**  ``backup/retention.py``'s module docstring states outright
that ``self._audit`` "is stored in ``__init__`` and never read by any method" (measured 2026-09-29,
B-20).  That instance is *known*; the census's new members are ``SocialManager`` and
``TaskExecutionEngine``.  The record includes all three, and one test pins the documented one so the
distinction cannot rot.

**Excluded on purpose.**  ``observation/observation_service.py::MultimodalObservationService`` also
stores an ``audit_log`` it never reads, but it is **never constructed anywhere** (not in ``src/``,
not in ``tests/``) -- that is a dead-*class* question, not a wired-but-silent sink, and it is left
for its own record.  ``evaluation/runner.py::EvaluationRunner`` is inside the already-pinned dead
evaluation pack (``tests/test_evaluation_pack_is_dead.py``).

Nothing here is fixed.  Making the services write to their audit sink is a **behaviour change** (new
audit entries appear), so it is an owner decision, recorded in ``DELEGATION.md`` §4 item 113.
"""

from __future__ import annotations

import ast
from pathlib import Path

from test_ineffective_flags import _SRC

_RUNTIME = _SRC / "aegis_ai" / "runtime.py"

#: ``(relative module, class, param, attr)`` for the three wired-but-silent audit sinks.
#: Measured 2026-10-12 (item 113).
_SITES: tuple[tuple[str, str, str, str], ...] = (
    ("social/manager.py", "SocialManager", "audit_manager", "_audit"),
    ("task/execution_engine.py", "TaskExecutionEngine", "audit_manager", "_audit_manager"),
    ("backup/retention.py", "RetentionManager", "audit_log", "_audit"),
)

#: The control: the gate takes ``audit`` into ``self._audit`` and *does* use it.
_CONTROL = ("egress/gate.py", "EgressGate", "audit", "_audit")

#: The member whose own module docstring already admits the dead sink.
_DOCUMENTED_MEMBER = "backup/retention.py"
_DOCUMENTED_PHRASE = "never read by any method"

#: One stored parameter per site that *is* read, proving the class is otherwise alive.
_LIVE_CONTROL: tuple[tuple[str, str, str], ...] = (
    ("social/manager.py", "SocialManager", "_events"),
    ("task/execution_engine.py", "TaskExecutionEngine", "_event_manager"),
    ("backup/retention.py", "RetentionManager", "_episodic"),
)


def _parse(path: Path) -> ast.AST:
    return ast.parse(path.read_text(encoding="utf-8"), filename=str(path))


def _class(path: Path, name: str) -> ast.ClassDef:
    return next(
        n for n in ast.walk(_parse(path)) if isinstance(n, ast.ClassDef) and n.name == name
    )


def _ctor(path: Path, name: str) -> tuple[list[str], dict[str, str]]:
    """(params, {attr: param}) for ``name``'s ``__init__``."""
    cls = _class(path, name)
    init = next(
        n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == "__init__"
    )
    a = init.args
    names = [x.arg for x in a.posonlyargs] + [x.arg for x in a.args] + [x.arg for x in a.kwonlyargs]
    params = [n for n in names if n != "self"]
    assigned: dict[str, str] = {}
    for node in ast.walk(init):
        if (
            isinstance(node, ast.Assign)
            and len(node.targets) == 1
            and isinstance(node.value, ast.Name)
            and node.value.id in params
        ):
            target = node.targets[0]
            if (
                isinstance(target, ast.Attribute)
                and isinstance(target.value, ast.Name)
                and target.value.id == "self"
            ):
                assigned[target.attr] = node.value.id
    return params, assigned


def _class_loads(path: Path, name: str) -> dict[str, list[int]]:
    loads: dict[str, list[int]] = {}
    for node in ast.walk(_class(path, name)):
        if (
            isinstance(node, ast.Attribute)
            and isinstance(node.value, ast.Name)
            and node.value.id == "self"
            and isinstance(node.ctx, ast.Load)
        ):
            loads.setdefault(node.attr, []).append(node.lineno)
    return loads


def _global_loads(attr: str) -> list[str]:
    found: list[str] = []
    for path in sorted(_SRC.rglob("*.py")):
        if "__pycache__" in path.parts:
            continue
        for node in ast.walk(_parse(path)):
            if (
                isinstance(node, ast.Attribute)
                and node.attr == attr
                and isinstance(node.ctx, ast.Load)
                and isinstance(node.value, ast.Name)
                and node.value.id == "self"
            ):
                found.append(f"{path.relative_to(_SRC).as_posix()}:{node.lineno}")
    return found


def _call_keywords(path: Path, class_name: str) -> list[tuple[str, set[str]]]:
    tree = _parse(path)
    calls: list[tuple[str, set[str]]] = []
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == class_name
        ):
            scope = next(
                (
                    n.name
                    for n in ast.walk(tree)
                    if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
                    and n.lineno <= node.lineno <= (n.end_lineno or n.lineno)
                ),
                "<module>",
            )
            calls.append((scope, {kw.arg for kw in node.keywords if kw.arg}))
    return calls


def _module_docstring(rel: str) -> str:
    return ast.get_docstring(_parse(_SRC / "aegis_ai" / rel)) or ""


# ── The census ────────────────────────────────────────────────────────────────


def test_each_service_declares_its_audit_parameter():
    for rel, cls, param, _ in _SITES:
        params, _ = _ctor(_SRC / "aegis_ai" / rel, cls)
        assert param in params, (
            f"{cls} no longer declares {param!r} (params: {params}). If the parameter was "
            "removed, clear this record and DELEGATION.md §4 item 113."
        )


def test_every_recorded_audit_sink_is_stored_and_never_read():
    """The property, per site: ``self._X = <param>`` exists and ``self._X`` is never Loaded."""
    assert len(_SITES) == 3
    for rel, cls, param, attr in _SITES:
        path = _SRC / "aegis_ai" / rel
        _, assigned = _ctor(path, cls)
        assert assigned.get(attr) == param, (
            f"{cls}.{attr} is no longer assigned from {param!r} (now {assigned.get(attr)!r})"
        )
        loads = _class_loads(path, cls).get(attr, [])
        assert loads == [], (
            f"{cls}.{attr} is now read at lines {loads} -- a service started writing to its "
            f"audit sink. Clear the record (this file and DELEGATION.md §4 item 113)."
        )


# ── The controls ──────────────────────────────────────────────────────────────


def test_the_census_must_be_class_scoped():
    """Control: every dead sink attribute is read *elsewhere* in the repo.

    A global scan answers "read" for all three. Each must have a ``self.<attr>`` Load
    **outside** its owning module -- which is what makes the class scope load-bearing.
    """
    for rel, cls, _, attr in _SITES:
        global_hits = _global_loads(attr)
        outside = [h for h in global_hits if not h.startswith(rel + ":")]
        assert outside, (
            f"'{attr}' (dead in {cls}) no longer has a global Load outside {rel} -- the "
            f"collision that justified the class-scoped scan is gone; re-derive this pin."
        )


def test_the_same_audit_attribute_is_live_in_the_gate():
    """Control: ``self._audit`` is dead in the services and **live in ``EgressGate``**.

    Same parameter name (``audit``), same attribute (``self._audit``), opposite verdict. A
    name-keyed census cannot produce two answers for one name; only a class-scoped one can.
    """
    rel, cls, param, attr = _CONTROL
    loads = _class_loads(_SRC / "aegis_ai" / rel, cls).get(attr, [])
    assert loads, (
        f"control broken: {cls}.{attr} is no longer read -- the live/dead pair cannot be "
        f"demonstrated"
    )
    # And it is not in the dead set.
    _, assigned = _ctor(_SRC / "aegis_ai" / rel, cls)
    assert assigned.get(attr) == param
    assert (rel, cls) not in {(r, c) for r, c, _, _ in _SITES}


def test_the_gate_actually_appends_to_its_sink():
    """Control: the sink is *usable*, not merely read -- ``_record`` calls ``append`` on it."""
    rel, cls, _, attr = _CONTROL
    gate = _class(_SRC / "aegis_ai" / rel, cls)
    record = next(
        (n for n in gate.body if isinstance(n, ast.FunctionDef) and n.name == "_record"), None
    )
    assert record is not None, "EgressGate._record is gone; the control no longer applies"
    reads_audit = any(
        isinstance(n, ast.Attribute)
        and n.attr == attr
        and isinstance(n.ctx, ast.Load)
        and isinstance(n.value, ast.Name)
        and n.value.id == "self"
        for n in ast.walk(record)
    )
    appends = any(
        isinstance(n, ast.Call)
        and isinstance(n.func, ast.Name)
        and n.func.id == "append"
        for n in ast.walk(record)
    )
    assert reads_audit and appends, (
        f"EgressGate._record no longer loads self.{attr} and calls append() on it; the "
        "control that shows the sink is usable is gone"
    )


def test_each_service_is_otherwise_alive():
    """Control: each class reads *other* collaborators, so the finding is specifically audit.

    This rules out "the whole class is inert". ``SocialManager`` reads ``self._events``,
    ``TaskExecutionEngine`` reads ``self._event_manager``, ``RetentionManager`` reads
    ``self._episodic`` -- each records something; it just never records to the audit sink.
    """
    for rel, cls, attr in _LIVE_CONTROL:
        loads = _class_loads(_SRC / "aegis_ai" / rel, cls).get(attr, [])
        assert loads, f"{cls}.{attr} is no longer read -- the per-class live control is broken"


def test_the_composition_root_wires_all_three_sinks():
    """The sinks are supplied, then dropped -- this is the wired-but-ignored shape."""
    wanted = {
        "SocialManager": "audit_manager",
        "TaskExecutionEngine": "audit_manager",
        "RetentionManager": "audit_log",
    }
    for cls, kw in wanted.items():
        calls = _call_keywords(_RUNTIME, cls)
        assert len(calls) == 1, f"expected one {cls} call in runtime.py, got {calls}"
        scope, keywords = calls[0]
        assert scope == "_build_runtime", f"{cls} is now built in {scope!r}"
        assert kw in keywords, (
            f"the composition root no longer passes {kw}= to {cls}; if the sink was "
            f"deliberately unwired, clear this record. keywords: {sorted(keywords)}"
        )


def test_one_member_documents_its_own_dead_sink():
    """``RetentionManager``'s module docstring already admits it; the other two are new.

    Pinned so the distinction between "known, documented debt" and "silent" cannot rot.
    """
    doc = _module_docstring(_DOCUMENTED_MEMBER)
    assert _DOCUMENTED_PHRASE in doc, (
        f"{_DOCUMENTED_MEMBER}'s docstring no longer admits its dead audit sink (phrase "
        f"{_DOCUMENTED_PHRASE!r} not found); if it was removed, the census must say so"
    )
    documented_classes = {cls for rel, cls, _, _ in _SITES if rel == _DOCUMENTED_MEMBER}
    assert documented_classes == {"RetentionManager"}
