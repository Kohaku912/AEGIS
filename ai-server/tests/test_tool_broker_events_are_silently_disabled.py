"""``ToolBroker``'s event publication is silently disabled by the composition root.

Measured 2026-10-06 (cycle 71). ``ToolBroker.__init__`` accepts ``event_manager`` and stores
``self._event_manager``, and two methods branch on it:

* ``_publish_tool_event`` returns early when it is ``None`` — so ``tool.executed`` is **never
  published**, and ``personal_data`` (which lists ``tool.executed`` among the events that record a
  fact) never records a tool-execution fact;
* ``_observe_recent_event`` returns ``False`` when it is ``None`` — so a capability whose manifest
  asks for a ``check_type: "event"`` verification always fails, and the failure text
  (``event observed=False``) reads as "the event did not happen" rather than "the checker was never
  armed".

**The guards are deliberate.** This pin does not claim a crash: the code explicitly handles a
missing manager, so an unarmed broker is a supported configuration. What is *not* deliberate is the
**silence** — the family the register already tracks (``DELEGATION.md`` §4 items 37/38: an
unreadable source looking like an empty one).

**The reason is ordering, not intent.** ``_build_runtime`` constructs the broker at
``runtime.py::_build_runtime@1111`` and creates the ``EventManager`` at ``runtime.py::_build_runtime@1222``, so there is nothing to pass yet.
Wiring it is a behaviour change — events would start flowing and ``personal_data`` would start
recording facts — so it is **recorded, not executed**.

**It is one of four omitted parameters, and the only one with no path.** Measured 2026-10-06 (cycle
72): ``__init__`` takes 11 parameters, the root supplies 7, and the 4 omitted are
``delegation_policy``, ``repair_manager``, ``event_manager`` and ``capability_health``. Three of the
four *are* wired — after construction, precisely because of the ordering above:
``tool_broker.set_delegation_policy(delegation_policy)`` (``runtime.py::_build_runtime@1284``) writes
``self._delegation_policy``; ``tool_broker.set_repair_manager(repair_manager)`` (``runtime.py::_build_runtime@1530``) writes
``self._repair_manager``; ``tool_broker._capability_health = capability_health`` (``runtime.py::_build_runtime@1230``) sets
the health view. ``event_manager`` alone has **no assignment and no setter** anywhere — ``runtime.py::_build_runtime@1228``'s
``journal_projector._event_manager = event_manager`` sets the *journal projector's* attribute, a
different class. So the defect is not "the ordering leaves four hooks dangling"; it is that this one
hook was never given the post-hoc path its three siblings got. Item 74 first read as if the root
left the broker with 7 of 11; it leaves 4 out, and the specificity is the finding.

Both consequences are **latent**: no shipped manifest currently uses ``check_type: "event"``.
"""

from __future__ import annotations

import ast
from pathlib import Path

_SERVER = Path(__file__).resolve().parents[1]
_SRC = _SERVER / "src"

#: The composition root's ``ToolBroker(...)`` kwargs, measured — **7 of the 11 parameters**. An
#: **equality**, so wiring ``event_manager=`` fails this pin and forces the record to move. The
#: other 4 omitted parameters, and which of them are wired later, are pinned by
#: ``test_the_other_three_omitted_parameters_are_wired_post_hoc``.
_TOOL_BROKER_KWARGS = frozenset(
    {
        "audit_log",
        "catalog",
        "folder_registry",
        "policy_engine",
        "registry",
        "server_executor",
        "verification_service",
    }
)

#: The two methods whose ``None`` branch is a silent ``return``. Named, so deleting one of them is
#: a failure rather than a quiet narrowing of the claim.
_UNARMED_BRANCHES = ("_publish_tool_event", "_observe_recent_event")

#: The three omitted parameters the root *does* wire after construction — ``param -> the name that
#: receives it`` (a setter method, or a direct attribute for ``capability_health``). The fourth
#: omitted parameter, ``event_manager``, is absent from this map on purpose: that absence is the
#: defect, and it is asserted as an absence below.
_POST_HOC_WIRING = {
    "delegation_policy": "set_delegation_policy",
    "repair_manager": "set_repair_manager",
    "capability_health": "_capability_health",
}


def _parsed(path: Path) -> ast.Module:
    return ast.parse(path.read_text(encoding="utf-8", errors="replace"), filename=str(path))


def _function(tree: ast.Module, name: str) -> ast.FunctionDef:
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return node
    raise AssertionError(f"{name} is not defined in this module any more")


def _call(tree: ast.Module, name: str) -> ast.Call:
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func = node.func
            called = func.id if isinstance(func, ast.Name) else getattr(func, "attr", None)
            if called == name:
                return node
    raise AssertionError(f"no `{name}(...)` call in this module")


def _tool_broker_kwargs() -> set[str]:
    return {k.arg for k in _call(_parsed(_SRC / "aegis_ai" / "runtime.py"), "ToolBroker").keywords}


def _assignment_line(tree: ast.Module, target_name: str, called_name: str) -> int:
    """The line of ``<target_name> = <called_name>(...)`` — used to pin the *ordering*."""
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign) or len(node.targets) != 1:
            continue
        t = node.targets[0]
        if not (isinstance(t, ast.Name) and t.id == target_name):
            continue
        v = node.value
        if isinstance(v, ast.Call):
            func = v.func
            called = func.id if isinstance(func, ast.Name) else getattr(func, "attr", None)
            if called == called_name:
                return node.lineno
    raise AssertionError(f"no `{target_name} = {called_name}(...)` assignment found")


def _broker_attribute_writes(tree: ast.Module) -> set[str]:
    """Every ``tool_broker.<attr> = ...`` in the module — the direct-wiring channel."""
    out: set[str] = set()
    for n in ast.walk(tree):
        if isinstance(n, ast.Assign) and len(n.targets) == 1 and isinstance(n.targets[0], ast.Attribute):
            target = n.targets[0]
            if isinstance(target.value, ast.Name) and target.value.id == "tool_broker":
                out.add(target.attr)
    return out


def _broker_method_calls(tree: ast.Module) -> set[str]:
    """Every ``tool_broker.<method>(...)`` in the module — the setter channel."""
    out: set[str] = set()
    for n in ast.walk(tree):
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute):
            func = n.func
            if isinstance(func.value, ast.Name) and func.value.id == "tool_broker":
                out.add(func.attr)
    return out


def _setter_writes(tree: ast.Module, method: str) -> set[str]:
    """The ``self.<attr>`` attributes ``ToolBroker.<method>`` assigns.

    An *equality* on this set is what makes "wired" a claim about the effect rather than about a
    call site: a setter that stopped writing its attribute would be an inert call, and the param it
    is supposed to arm would be starved again.
    """
    cls = next(n for n in ast.walk(tree) if isinstance(n, ast.ClassDef) and n.name == "ToolBroker")
    func = next(f for f in cls.body if isinstance(f, ast.FunctionDef) and f.name == method)
    out: set[str] = set()
    for n in ast.walk(func):
        if isinstance(n, ast.Assign) and len(n.targets) == 1 and isinstance(n.targets[0], ast.Attribute):
            target = n.targets[0]
            if isinstance(target.value, ast.Name) and target.value.id == "self":
                out.add(target.attr)
    return out


def test_the_broker_accepts_an_event_manager_it_is_never_given() -> None:
    """The wiring point exists; the composition root does not use it.

    Both directions are load-bearing: wiring ``event_manager=`` must fail this pin (so the register
    moves), and removing the parameter must fail it too (so the record cannot pass by describing a
    hook that no longer exists).
    """
    init = _function(_parsed(_SRC / "tool_broker.py"), "__init__")
    params = {a.arg for a in (*init.args.args, *init.args.kwonlyargs)}
    assert "event_manager" in params, (
        "ToolBroker no longer accepts an `event_manager` — the starved wiring this pin records is gone"
    )
    stored = {
        n.targets[0].attr
        for n in ast.walk(init)
        if isinstance(n, ast.Assign)
        and len(n.targets) == 1
        and isinstance(n.targets[0], ast.Attribute)
        and isinstance(n.targets[0].value, ast.Name)
        and n.targets[0].value.id == "self"
        and isinstance(n.value, ast.Name)
        and n.value.id == "event_manager"
    }
    assert stored == {"_event_manager"}, (
        f"ToolBroker no longer stores `self._event_manager` (found {sorted(stored)}) — the two "
        "silent branches below would then be reading a different attribute"
    )
    measured = _tool_broker_kwargs()
    assert measured == _TOOL_BROKER_KWARGS, (
        f"the composition root's ToolBroker kwargs moved: {sorted(measured)} != "
        f"{sorted(_TOOL_BROKER_KWARGS)} — if `event_manager` is now among them, the broker is armed "
        "and DELEGATION.md §4 item 74's record has to move"
    )


def test_the_unarmed_branches_are_silent_returns() -> None:
    """Non-vacuity for the claim above: the two branches really are silent, not loud.

    ``_publish_tool_event`` returns with no log and ``_observe_recent_event`` returns ``False`` with
    no log. "Silent" is asserted structurally: the guard's body is **only** a ``return``, so there
    is no log statement in it. If either branch started *reporting* the missing manager, the record
    ("silent") would be wrong even though the wiring is still missing.

    Note the two guards do not look alike — one tests ``self._event_manager is None`` directly, the
    other tests a local bound by ``getattr(self, "_event_manager", None)`` — so the assertion is on
    the *function*, not on the guard's test expression.
    """
    tree = _parsed(_SRC / "tool_broker.py")
    for name in _UNARMED_BRANCHES:
        body = _function(tree, name)
        assert "_event_manager" in ast.dump(body), (
            f"{name} no longer consults `_event_manager` — the starvation this pin records is gone"
        )
        silent = [
            n
            for n in ast.walk(body)
            if isinstance(n, ast.If) and len(n.body) == 1 and isinstance(n.body[0], ast.Return)
        ]
        assert silent, (
            f"{name} has no `if <unarmed>: return` branch any more — it either logs before returning "
            "or proceeds anyway, so the record ('silent') has to move"
        )


def test_the_event_manager_is_created_after_the_broker() -> None:
    """The *reason* it is unarmed: ordering inside the composition root.

    ``_build_runtime`` builds the broker before it creates the ``EventManager``, so there is nothing
    to pass at the construction site. This is the same shape as the ``ContextBuilder`` /
    ``Scheduler`` ordering (§4 item 24) — the pin records the cause, not just the symptom.
    """
    tree = _parsed(_SRC / "aegis_ai" / "runtime.py")
    broker_line = _assignment_line(tree, "tool_broker", "ToolBroker")
    em_line = _assignment_line(tree, "event_manager", "EventManager")
    assert broker_line < em_line, (
        f"the broker is now built at :{broker_line} and the EventManager at :{em_line} — the "
        "ordering that made the broker unarmable has changed, so the record has to move"
    )


def test_the_other_three_omitted_parameters_are_wired_post_hoc() -> None:
    """The omitted population is four, and ``event_manager`` is the only one left dangling.

    Cycle 71 recorded "the root passes 7 kwargs and not ``event_manager``", which reads as if the
    broker were left with 7 of 11 parameters. It is left with **7 of 11 supplied at construction and
    3 more supplied afterwards** — so the *defect* is not the ordering, it is that one of the four
    was never given the post-hoc path its siblings got. This test keeps that specificity honest in
    both directions: if a sibling stops being wired the record must widen to "two starved", and if
    ``event_manager`` acquires a path the record must move at all.
    """
    root = _parsed(_SRC / "aegis_ai" / "runtime.py")
    calls = _broker_method_calls(root)
    writes = _broker_attribute_writes(root)

    for param, receiver in _POST_HOC_WIRING.items():
        if receiver.startswith("_"):
            assert receiver in writes, (
                f"`tool_broker.{receiver} = ...` is gone from the composition root — "
                f"`{param}` is now starved too, so item 74's population is out of date"
            )
        else:
            assert receiver in calls, (
                f"`tool_broker.{receiver}(...)` is gone from the composition root — `{param}` is "
                "now starved too, so item 74's population is out of date"
            )
            assert _setter_writes(_parsed(_SRC / "tool_broker.py"), receiver) == {f"_{param}"}, (
                f"`{receiver}` no longer writes `self._{param}` — the call is now inert and the "
                "parameter is starved again, whatever the composition root looks like"
            )

    # The absence *is* the finding. Both channels are checked, so wiring it by either route fails.
    assert "_event_manager" not in writes, (
        "the composition root now assigns `tool_broker._event_manager` — the broker is armed and "
        "DELEGATION.md §4 item 74's record has to move"
    )
    assert not any(m.startswith("set_event") for m in calls), (
        "a `tool_broker.set_event*` call appeared — the broker is armable now and item 74's record "
        "has to move"
    )
