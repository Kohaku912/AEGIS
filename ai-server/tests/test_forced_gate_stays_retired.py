"""The forced approval gate stays retired, and the confirmation store cannot revive it.

Phase 5a put the approval **UI** back into service — not the approval **gate**. The
distinction is the whole point, and it is easy to lose:

* retired: a capability is *blocked* because a manifest, a risk level or a rule says it
  must be approved first;
* kept: AEGIS decides, on its own judgement, to ask the user, and the answer informs
  what it does next.

``tests/test_goal_change_guard.py`` pins that the deleted approval *subsystem* stays
deleted. This module pins the harder, newer claim: that the replacement store is not a
gate wearing a different name. The failure mode it exists to prevent is a future change
that makes the tool broker or the policy engine read ``runtime.confirmation_store``
"just to be safe" — which would restore the bottleneck while every existing test kept
passing.

The same failure mode exists for a **third** surface, ``aegis_ai.permissions`` (4
modules): a complete service-permission gate that returns
``{"decision": "ask_approval", "requires_approval": True}``, persists
``requires_approval=True`` for purchase/payment default scopes, and is reachable from
**nothing** outside its own package. It is more dangerous than prose claiming a gate,
precisely because it *works* and its own tests assert the gate semantics — wiring it
would look **better** supported than leaving it alone. So it is pinned here too: no
execution-path module may import it.

So the assertions are structural: **nothing in the execution path may even import the
confirmation package.** An unenforced invariant is not an invariant.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

_SRC = Path(__file__).resolve().parents[1] / "src"
_CONFIRMATION_PACKAGE = "aegis_ai.confirmation"

#: Modules that decide or perform work. If any of them can reach the confirmation
#: store, a confirmation can hold up a capability again.
_EXECUTION_PATH: tuple[str, ...] = (
    "tool_broker.py",
    "policy_engine.py",
    "task/execution_engine.py",
    "task/task_manager.py",
    "task_plan.py",
    "personal_ai/delegation.py",
    # The ai-server capability executor. It is the one execution-path module that
    # legitimately holds the store (so AEGIS can raise a question itself), which is
    # exactly why it is listed here: it must still not *import* the package, and
    # test_aegis_may_never_answer_its_own_question below constrains what it may call.
    "core_capabilities.py",
)

#: Store methods that decide a confirmation. Only the user may call these. AEGIS may
#: ask (``request``) and read (``list``) — an agent that can answer its own question has
#: simply rebuilt the gate with itself as the approver.
#:
#: ``ConfirmationStore`` also declares ``mark_executed`` / ``mark_failed``, and an earlier
#: revision of this comment listed them as AEGIS-reachable. They are not: nothing calls
#: them, and ``core_capabilities._confirmation`` dispatches only the two suffixes above.
#: They are therefore deliberately **not** in this tuple — listing them would assert a
#: contract the code does not have. Add them here if that capability is ever wired up.
_USER_ONLY_STORE_METHODS: tuple[str, ...] = (
    "approve",
    "reject",
    "cancel",
    "resolve",
    "modify_and_approve",
)

#: The only modules allowed to import ``aegis_ai.confirmation``. Kept as an explicit
#: list on purpose: adding a reader is a decision that should require editing this
#: test, because "who can see the questions" is exactly the question that matters.
#: (Phase 5a's LLM-callable capability will be added here when it lands.)
#:
#: ``autonomous_loop.py`` joined on 2026-10-01 (B-5 ①). It imports only
#: ``ConfirmationStatus`` — an enum — and reads the store through ``all()``, so it cannot
#: block on an answer; ``test_the_loop_reads_the_confirmation_store_without_answering``
#: pins exactly which methods it may call.
_ALLOWED_IMPORTERS: frozenset[str] = frozenset(
    {
        "aegis_ai/confirmation/__init__.py",
        "aegis_ai/confirmation/store.py",
        "aegis_ai/runtime.py",
        "aegis_ai/web/routes/approval.py",
        "aegis_ai/autonomous/autonomous_loop.py",
    }
)

#: The third approval surface. ``aegis_ai.permissions`` decides ``ask_approval`` from
#: service scopes — the retired gate's shape, complete with a store, a policy and a
#: scope model. It is reachable from nothing outside its own package, and *that* is the
#: property pinned here. It looks supported because ``tests/test_goal_alignment.py`` and
#: ``tests/test_mission_contract_acceptance.py`` exercise it.
_PERMISSIONS_PACKAGE = "aegis_ai.permissions"

#: Modules under ``src/`` allowed to import the permissions gate: only the package's own
#: modules (observed, not assumed — ``service_scope_types.py`` imports nothing from it).
_PERMISSIONS_ALLOWED_IMPORTERS: frozenset[str] = frozenset(
    {
        "aegis_ai/permissions/__init__.py",
        "aegis_ai/permissions/service_permission_policy.py",
        "aegis_ai/permissions/service_permission_store.py",
    }
)


def _imported_modules(path: Path) -> set[str]:
    """Top-level module names a file imports.

    AST rather than a substring scan, so a docstring that *documents* the retirement
    (legitimate, and this very package does it) is not mistaken for a use.
    """
    tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            names.add(node.module)
    return names


def _imports_package(path: Path, package: str) -> bool:
    """True if the file imports the package or any submodule of it.

    Prefix matching matters: ``from aegis_ai.confirmation.store import ...`` imports
    ``aegis_ai.confirmation.store``, which is not equal to the package name but is
    unmistakably a reach into it.
    """
    return any(
        name == package or name.startswith(package + ".") for name in _imported_modules(path)
    )


def _imports_confirmation(path: Path) -> bool:
    """True if the file reaches into the confirmation package."""
    return _imports_package(path, _CONFIRMATION_PACKAGE)


def _src_files() -> list[Path]:
    return [
        path
        for path in _SRC.rglob("*.py")
        if "__pycache__" not in path.parts and "pb2" not in path.parts
    ]


def _importers_of(package: str) -> set[str]:
    """Every ``src/`` module that reaches into ``package``, as repo-relative paths."""
    return {
        str(path.relative_to(_SRC)).replace("\\", "/")
        for path in _src_files()
        if _imports_package(path, package)
    }


def _confirmation_importers() -> set[str]:
    return _importers_of(_CONFIRMATION_PACKAGE)


def _permissions_importers() -> set[str]:
    return _importers_of(_PERMISSIONS_PACKAGE)


# ── nothing in the execution path can reach the store ─────────────────────────


@pytest.mark.parametrize("relative", _EXECUTION_PATH)
def test_execution_path_does_not_import_the_confirmation_package(relative: str) -> None:
    """The load-bearing assertion of Phase 5a.

    A module that cannot import the store cannot wait on a confirmation. This is a
    stronger statement than "it currently does not wait", because it cannot regress
    without an explicit edit here.
    """
    path = _SRC / "aegis_ai" / relative
    assert path.is_file(), f"{relative} moved; update this guard"
    assert not _imports_confirmation(path), (
        f"{relative} imports {_CONFIRMATION_PACKAGE}; the execution path must never be "
        "able to wait on a confirmation"
    )


def test_only_the_allowed_modules_import_the_confirmation_package() -> None:
    """Pin the reader list, so widening it is a deliberate act rather than a drift."""
    unexpected = _confirmation_importers() - _ALLOWED_IMPORTERS

    assert unexpected == set(), (
        "these modules newly import the confirmation package: "
        f"{sorted(unexpected)}. If a new reader is intended, add it to "
        "_ALLOWED_IMPORTERS in this file and confirm it cannot block on an answer."
    )


def test_the_scan_actually_finds_importers() -> None:
    """Guard the guard: a broken scan would make the assertion above pass vacuously."""
    importers = _confirmation_importers()

    assert "aegis_ai/runtime.py" in importers, "the scan missed a known importer"
    assert "aegis_ai/confirmation/store.py" in importers, (
        "the scan missed a submodule import; the prefix match is broken"
    )
    assert len(_src_files()) > 300


@pytest.mark.parametrize(
    "source",
    [
        "import aegis_ai.confirmation",
        "from aegis_ai.confirmation import ConfirmationStore",
        "from aegis_ai.confirmation.store import ConfirmationStore",
    ],
)
def test_the_detector_recognises_every_import_form(tmp_path, source: str) -> None:
    """Prove the detector can fail, so the assertions above are not vacuous.

    Phase 4's lesson: a check that has never been observed failing is an assumption.
    All three import spellings reach the package, and a substring scan for the bare
    package name would miss the third.
    """
    probe = tmp_path / "probe.py"
    probe.write_text(f"{source}\n", encoding="utf-8")

    assert _imports_confirmation(probe)


def test_the_detector_ignores_a_mention_in_a_docstring(tmp_path) -> None:
    """Documenting the retirement is legitimate; using it is not."""
    probe = tmp_path / "probe.py"
    probe.write_text(
        '"""This module explains why aegis_ai.confirmation is not a gate."""\n\nVALUE = 1\n',
        encoding="utf-8",
    )

    assert not _imports_confirmation(probe)


# ── the store offers no way to block ──────────────────────────────────────────


@pytest.mark.parametrize("name", ["wait", "block", "acquire", "join", "await_decision", "poll"])
def test_the_store_has_no_blocking_api(name: str) -> None:
    """A confirmation is a question, so there is nothing to wait for.

    ``request()`` is deliberately fire-and-forget; a ``wait()`` would be the whole
    retired gate rebuilt in one method.
    """
    from aegis_ai.confirmation import ConfirmationStore

    assert not hasattr(ConfirmationStore, name), f"ConfirmationStore.{name}() came back"


def test_the_store_does_not_import_policy_or_manifests() -> None:
    """No risk inference, no manifest lookup — the decision belongs to the LLM."""
    imports = _imported_modules(_SRC / "aegis_ai" / "confirmation" / "store.py")

    forbidden = {name for name in imports if "policy" in name or "manifest" in name}
    assert forbidden == set(), f"the confirmation store reached into {sorted(forbidden)}"


def test_the_confirmation_package_makes_no_decisions() -> None:
    """It records a question and an answer. It must not classify anything itself.

    ``risk`` / ``side_effects`` are *descriptions AEGIS supplies about its own intended
    action*; the store must never read them to decide whether to ask, which is exactly
    what the retired gate did.
    """
    for name in ("store.py", "models.py"):
        source = (_SRC / "aegis_ai" / "confirmation" / name).read_text(encoding="utf-8")
        accessed = {
            node.attr for node in ast.walk(ast.parse(source)) if isinstance(node, ast.Attribute)
        }
        for suspicious in ("requires_approval", "risk_level", "manifest"):
            assert suspicious not in accessed, (
                f"{name} reads '{suspicious}'; the confirmation store must not infer "
                "whether a question is needed"
            )


# ── a confirmation does not appear in the execution contract ──────────────────


def test_the_tool_contract_carries_no_confirmation_field() -> None:
    """Nothing can be "held awaiting a confirmation" if no such field exists."""
    from tool_broker import ToolExecutionRequest, ToolExecutionResult

    for field in ("confirmation_id", "approval_id", "confirmation_store"):
        assert not hasattr(ToolExecutionRequest, field)
        assert not hasattr(ToolExecutionResult, field)


def test_policy_engine_has_no_confirmation_awareness() -> None:
    """The policy engine decides ALLOW / ALLOW_WITH_AUDIT / DENY / UNAVAILABLE.

    There is no outcome meaning "ask the user first", so no policy decision can be
    parked on a confirmation.
    """
    from policy_engine import PolicyDecision

    assert {member.name for member in PolicyDecision} == {
        "ALLOW",
        "ALLOW_WITH_AUDIT",
        "DENY",
        "UNAVAILABLE",
    }
    source = (_SRC / "aegis_ai" / "policy_engine.py").read_text(encoding="utf-8")
    assert "confirmation" not in source.lower(), (
        "policy_engine.py mentions confirmations; policy must not be aware of them"
    )


# ── AEGIS may ask, but never answer ───────────────────────────────────────────


@pytest.mark.parametrize("method", _USER_ONLY_STORE_METHODS)
def test_aegis_may_never_answer_its_own_question(method: str) -> None:
    """The capability executor may ask and read, never decide.

    This is the failure mode that would matter most: if AEGIS could approve its own
    confirmation, the question would become a formality and the user's judgement would
    be decorative. The executor is checked by call site rather than by capability, so
    adding a new capability cannot quietly add a decision path.
    """
    source = (_SRC / "aegis_ai" / "core_capabilities.py").read_text(encoding="utf-8")

    assert f"self._confirmations.{method}(" not in source, (
        f"core_capabilities.py calls ConfirmationStore.{method}(); only the user may "
        "answer a confirmation"
    )


def test_the_executor_really_does_reach_the_store() -> None:
    """Guard the guard: the check above is vacuous if nothing touches the store."""
    source = (_SRC / "aegis_ai" / "core_capabilities.py").read_text(encoding="utf-8")

    assert "self._confirmations.request(" in source, "AEGIS can no longer raise a question"
    assert "self._confirmations" in source
    # The scan must be looking at a call-through form, not an alias that would hide one.
    assert "self._confirmations = self._personal.get(" in source


# ── the third surface: a working gate that nothing may reach ──────────────────


@pytest.mark.parametrize("relative", _EXECUTION_PATH)
def test_execution_path_does_not_import_the_permissions_gate(relative: str) -> None:
    """A module that cannot import the gate cannot park a capability on it.

    ``aegis_ai.permissions`` returns ``ask_approval`` from a service scope — the retired
    gate's decision, with a store behind it. Wiring it back would restore the bottleneck
    while its own tests kept passing, which is the failure mode this module exists for.
    """
    path = _SRC / "aegis_ai" / relative
    assert path.is_file(), f"{relative} moved; update this guard"
    assert not _imports_package(path, _PERMISSIONS_PACKAGE), (
        f"{relative} imports {_PERMISSIONS_PACKAGE}; the execution path must never be "
        "able to park a capability on an approval decision"
    )


def test_only_the_permissions_package_imports_itself() -> None:
    """Pin the reader list, so wiring the gate becomes a deliberate act.

    If this fails, something outside the package reached into the gate. If that reach is
    intended, it must be added to ``_PERMISSIONS_ALLOWED_IMPORTERS`` here — and the
    reviewer then has to answer whether the caller can block on ``ask_approval``.
    """
    importers = _permissions_importers()

    assert importers, "the scan found no importers at all; the prefix match is broken"

    unexpected = importers - _PERMISSIONS_ALLOWED_IMPORTERS
    assert unexpected == set(), (
        "these modules newly import the permissions gate: "
        f"{sorted(unexpected)}. If a new reader is intended, add it to "
        "_PERMISSIONS_ALLOWED_IMPORTERS and confirm it cannot block on an answer."
    )


def test_the_permissions_gate_still_says_ask_approval(tmp_path) -> None:
    """Record *why* this surface must stay unwired: it decides ``ask_approval``.

    If this ever changes — the gate deleted, or reframed as a voluntary question — then
    the pin above is describing a different thing and must be revisited. The expectation
    mirrors ``tests/test_goal_alignment.py::test_unknown_browser_operation_requires_approval``,
    which is the test that makes the gate look supported.
    """
    from aegis_ai.permissions.service_permission_policy import ServicePermissionPolicy
    from aegis_ai.permissions.service_permission_store import ServicePermissionStore

    policy = ServicePermissionPolicy(store=ServicePermissionStore(path=str(tmp_path / "sp.json")))
    decision = policy.evaluate_browser_action("https://mail.google.com/mail/u/0/#inbox", "")

    assert decision["decision"] == "ask_approval"
    assert decision["requires_approval"] is True


# ── the fourth surface: the approval-era argument, now supplied by one caller ──
#
# ``ReflectionEngine.reflect`` still takes ``approval_decisions``. Until 2026-10-01 **no
# caller anywhere passed it**, so every branch that reads it was unreachable — including
# the only producer of ``approval_lesson`` memories.
#
# A-11 decided ③: keep the argument, but **pin and record** it. This is that record.
# The point is that the surface must not change silently in *either* direction —
# wiring it revives approval-decision recording (a product call: does that fit D4=(b),
# the boundary where the forced gate stays deleted but the voluntary ask stays?), and
# deleting it is a separate decision. Both must trip this file.
#
# **2026-09-30 — the record shape was repaired; the wiring deliberately was not.** The
# producer used to write neither of the two keys its consumers query, so supplying the
# argument alone would not have closed the growth loop. That half is fixed (register §3.1
# item 4, holes ② and ③). The loop was left cut at exactly one place — the caller — which
# was the deliberate A-11 ③ state.
#
# **2026-10-01 — the caller was wired (B-5 ①, owner decision).** The blocker was that a
# resolved confirmation could not be attributed to a desire, so feeding rejections through
# would have punished an *unrelated* desire. Measuring it narrowed the link to two options
# and killed neither; the owner chose to record the desire on the confirmation. So
# ``AutonomousLoop`` now reads the store (read-only) and supplies the argument, grouped per
# desire, dropping every confirmation whose ``desire`` is empty or absent from the live
# desire set. The tests below therefore pin **three** things: that exactly one caller
# supplies it, that the caller fails closed, and that the lesson it produces reaches both
# readers.

_REFLECTION_ENGINE = _SRC / "aegis_ai" / "reflection" / "reflection_engine.py"
_TESTS = Path(__file__).resolve().parent

#: Functions whose signature takes ``approval_decisions``. **Discovered by AST, never
#: hand-listed for matching** — the map only supplies the *reason* each one is expected,
#: and an equality is asserted against the discovered set so a new reader is a deliberate
#: edit. The four are the whole surface: the entry point plus the three classifiers it
#: delegates to.
_RECORDED_APPROVAL_DECISION_CONSUMERS: dict[str, str] = {
    "reflect": "entry point, and the only *producer* of approval_lesson memories",
    "_classify_outcome": "reads it for _OUTCOME_REJECTED",
    "_identify_root_cause": "reads it for the 'Approval rejected' root cause",
    "_classify_failure": "reads it for APPROVAL_REJECTED / APPROVAL_EXPIRED",
}


def _parsed(path: Path) -> ast.Module:
    """Parse a file. AST, so a docstring naming the parameter is not mistaken for a use."""
    return ast.parse(path.read_text(encoding="utf-8", errors="replace"))


def _test_files() -> list[Path]:
    return [
        path
        for path in _TESTS.rglob("*.py")
        if "__pycache__" not in path.parts and "pb2" not in path.parts
    ]


def _functions_declaring(tree: ast.Module, parameter: str) -> set[str]:
    """Names of every function that declares ``parameter``."""
    found: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            args = node.args
            declared = {a.arg for a in (*args.posonlyargs, *args.args, *args.kwonlyargs)}
            if parameter in declared:
                found.add(node.name)
    return found


def _calls_supplying(parameter: str) -> list[str]:
    """Every ``src/`` or ``tests/`` call site that passes ``parameter=``, as ``where:line``."""
    self_path = Path(__file__).resolve()
    offenders: list[str] = []
    for label, files in (("src", _src_files()), ("tests", _test_files())):
        for path in files:
            if path.resolve() == self_path:
                continue
            for node in ast.walk(_parsed(path)):
                if isinstance(node, ast.Call) and any(kw.arg == parameter for kw in node.keywords):
                    offenders.append(f"{label}/{path.name}:{node.lineno}")
    return offenders


def _modules_filtering_on_structured_data_key(key: str) -> set[str]:
    """Modules calling ``<something>.structured_data.get("<key>")``.

    AST rather than a substring scan: a comment or docstring quoting the filter must not
    count as the filter.
    """
    found: set[str] = set()
    for path in _src_files():
        for node in ast.walk(_parsed(path)):
            if not isinstance(node, ast.Call):
                continue
            func = node.func
            if not (isinstance(func, ast.Attribute) and func.attr == "get"):
                continue
            if not (
                isinstance(func.value, ast.Attribute) and func.value.attr == "structured_data"
            ):
                continue
            if node.args and isinstance(node.args[0], ast.Constant) and node.args[0].value == key:
                found.add(path.stem)
    return found


def _enum_member_name(node: ast.expr) -> str | None:
    """The member name in ``MemoryType.MEMORY_TYPE.value``, and in the bare ``MemoryType.X``.

    The extra ``.value`` layer is easy to miss and makes a predicate silently match nothing —
    which is exactly how a discovery helper goes blind while every assertion still passes.
    """
    if not isinstance(node, ast.Attribute):
        return None
    if node.attr == "value" and isinstance(node.value, ast.Attribute):
        return node.value.attr
    return node.attr


def _memory_record_calls(tree: ast.Module, member: str) -> list[ast.Call]:
    """Every ``MemoryRecord(...)`` built with ``MemoryType.<member>``."""
    return [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "MemoryRecord"
        and any(
            kw.arg == "memory_type" and _enum_member_name(kw.value) == member
            for kw in node.keywords
        )
    ]


def _function_named(tree: ast.Module, name: str) -> ast.FunctionDef | ast.AsyncFunctionDef | None:
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == name:
            return node
    return None


def _functions_looping_over(parameter: str) -> set[str]:
    """Functions containing a ``for ... in <parameter>`` loop."""
    found: set[str] = set()
    for node in ast.walk(_parsed(_REFLECTION_ENGINE)):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if any(
            isinstance(inner, ast.For)
            and isinstance(inner.iter, ast.Name)
            and inner.iter.id == parameter
            for inner in ast.walk(node)
        ):
            found.add(node.name)
    return found


def _approval_lesson_producer() -> ast.Call:
    """The single ``MemoryRecord(...)`` built with ``MemoryType.APPROVAL_LESSON``."""
    producers = _memory_record_calls(_parsed(_REFLECTION_ENGINE), "APPROVAL_LESSON")
    assert len(producers) == 1, (
        f"expected exactly one approval_lesson producer, found {len(producers)}; "
        "re-measure this pin"
    )
    return producers[0]


def _approval_lesson_readers() -> dict[str, set[str]]:
    """Module stem -> keyword names of its ``search_memories(memory_type="approval_lesson")``."""
    readers: dict[str, set[str]] = {}
    for path in _src_files():
        for node in ast.walk(_parsed(path)):
            if not isinstance(node, ast.Call):
                continue
            if not (isinstance(node.func, ast.Attribute) and node.func.attr == "search_memories"):
                continue
            if any(
                kw.arg == "memory_type"
                and isinstance(kw.value, ast.Constant)
                and kw.value.value == "approval_lesson"
                for kw in node.keywords
            ):
                readers[path.stem] = {kw.arg for kw in node.keywords if kw.arg}
    return readers


def test_the_approval_decision_parameter_is_read_by_exactly_the_recorded_functions() -> None:
    """Pin the reader set, so adding or removing a reader is a deliberate act."""
    declared = _functions_declaring(_parsed(_REFLECTION_ENGINE), "approval_decisions")

    assert declared == set(_RECORDED_APPROVAL_DECISION_CONSUMERS), (
        "the set of functions reading approval_decisions changed: "
        f"discovered {sorted(declared)}, recorded "
        f"{sorted(_RECORDED_APPROVAL_DECISION_CONSUMERS)}. Update both the record and its "
        "reasons, and re-check whether the argument has acquired a caller."
    )


def test_the_engine_scan_is_not_vacuous() -> None:
    """Guard the guard: a parse that returned nothing would satisfy the equality above."""
    functions = {
        node.name
        for node in ast.walk(_parsed(_REFLECTION_ENGINE))
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }

    # 7 is the measured count: __init__, reflect, and five private helpers. A floor equal to
    # the current count fails if the scan loses a function, which is the point — a scan that
    # silently returns nothing would satisfy every equality below.
    assert len(functions) >= 7, f"only {len(functions)} functions parsed; the scan is broken"
    assert "reflect" in functions


#: Call sites that supply ``approval_decisions``. **Discovered by AST, never hand-listed for
#: matching** — this map only supplies the *reason* each entry is expected, and an equality
#: is asserted against the discovered set, so a second supplier is a deliberate edit.
#:
#: Until 2026-10-01 this set was **empty** and the pin asserted exactly that. B-5 ① was then
#: decided (owner) and executed, so the record moves from "nobody supplies it" to "exactly
#: one does, and it validates the desire first". A second entry is not automatically wrong,
#: but it does change where the growth loop is fed, and the reason has to be written here.
_RECORDED_APPROVAL_DECISION_CALLERS: dict[str, str] = {
    "autonomous_loop.py": (
        "the only supplier: _rejected_confirmations_by_desire() groups the user's rejected "
        "confirmations by a desire it has checked against the live desire set"
    ),
}


def test_exactly_the_recorded_callers_supply_approval_decisions() -> None:
    """Exactly one place feeds the growth loop, and the record names it.

    Re-pointed 2026-10-01 (B-5 ①). This test previously asserted ``offenders == []`` —
    "supplied by nobody" — which was the A-11 ③ state. Wiring it was an owner decision,
    taken *after* measuring that the link had to be defined first (register §3.1 item 4).

    ``tests/`` is scanned too, and deliberately: a test that supplied the argument would
    make the branches look live while production never did — and would quietly make this
    pin pass for the wrong reason.
    """
    callers = _calls_supplying("approval_decisions")
    discovered = {entry.split("/")[-1].split(":")[0] for entry in callers}

    assert discovered == set(_RECORDED_APPROVAL_DECISION_CALLERS), (
        f"the set of call sites supplying approval_decisions changed: {sorted(discovered)} "
        f"(expected {sorted(_RECORDED_APPROVAL_DECISION_CALLERS)}). This is the feed into the "
        "growth loop — a second supplier, or the loss of the only one, moves where the loop "
        "closes. Re-measure, then update this record deliberately."
    )
    assert len(callers) == 1, (
        f"expected exactly one supplying call site, found {callers}. Two suppliers means two "
        "paths into approval-lesson recording; decide which is authoritative."
    )


def test_the_caller_scan_sees_real_call_sites() -> None:
    """Guard the guard: an empty result is only meaningful if the scan reads real calls."""
    callers = [
        f"{path.relative_to(_SRC).as_posix()}:{node.lineno}"
        for path in _src_files()
        for node in ast.walk(_parsed(path))
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "reflect"
    ]

    assert callers, "the scan found no .reflect( call sites at all; the scan is broken"


def test_the_detector_recognises_a_supplied_keyword(tmp_path) -> None:
    """Prove the scan can fail, so its empty result above is not vacuous."""
    probe = tmp_path / "probe.py"
    probe.write_text(
        "engine.reflect(task_id='t', approval_decisions=[{'status': 'rejected'}])\n",
        encoding="utf-8",
    )

    supplied = [
        node
        for node in ast.walk(_parsed(probe))
        if isinstance(node, ast.Call) and any(kw.arg == "approval_decisions" for kw in node.keywords)
    ]

    assert len(supplied) == 1, "the detector cannot see a supplied keyword; the scan is blind"


def test_the_only_approval_lesson_producer_is_guarded_by_the_argument() -> None:
    """Why the producer is reachable now, and what still guards it.

    Re-pointed 2026-10-01 (B-5 ①) from "...sits behind the *unsupplied* parameter": the
    argument is supplied now, so "unsupplied" is no longer the reason the producer is dead
    — the reason it is *safe* is that the supplier drops every confirmation it cannot
    attribute. The structural half is unchanged and still load-bearing: two functions
    iterate the argument, and the split matters — ``reflect`` iterates it to *produce*
    memories, ``_identify_root_cause`` to *classify*. Pinning the set keeps the two from
    being confused for one another.
    """
    looping = _functions_looping_over("approval_decisions")
    assert looping == {"reflect", "_identify_root_cause"}, (
        f"the functions iterating approval_decisions changed: {sorted(looping)}. One of them "
        "guards the only approval_lesson producer — re-measure this pin."
    )

    tree = _parsed(_REFLECTION_ENGINE)
    producers = _memory_record_calls(tree, "APPROVAL_LESSON")
    assert len(producers) == 1, f"expected one approval_lesson producer, found {len(producers)}"
    producer = producers[0]

    reflect = _function_named(tree, "reflect")
    assert reflect is not None, "reflect() vanished; re-measure this pin"
    assert any(node is producer for node in ast.walk(reflect)), (
        "the approval_lesson producer has moved out of reflect()"
    )

    guarding = [
        node
        for node in ast.walk(reflect)
        if isinstance(node, ast.For)
        and isinstance(node.iter, ast.Name)
        and node.iter.id == "approval_decisions"
        and any(inner is producer for inner in ast.walk(node))
    ]
    assert len(guarding) == 1, (
        "the approval_lesson producer is no longer the body of a loop over "
        "approval_decisions, so it may have become reachable"
    )


def test_the_producer_writes_the_keys_its_readers_query() -> None:
    """The producer and its consumers must agree about the record shape.

    Two of the three readers search by ``related_desire`` *and* keep only the records whose
    ``structured_data["decision"]`` is "rejected". The producer used to set **neither**, so
    the record was invisible to both of them: wiring ``approval_decisions`` would have looked
    like a failed fix, and only ``context_builder`` — which filters on the memory type alone —
    would have started seeing records.

    Repaired 2026-09-30 (register §3.1 item 4, holes ② and ③). The pin is now written against
    the *agreement*: dropping either key from the producer trips it. The end-to-end test below
    is the stronger one because it runs the readers; this one names the two keys, so a failure
    here says which half broke.
    """
    producer_keywords = {kw.arg for kw in _approval_lesson_producer().keywords}

    readers = _approval_lesson_readers()
    assert len(readers) >= 3, f"only {len(readers)} approval_lesson readers found; scan is broken"

    desire_readers = sorted(name for name, kws in readers.items() if "related_desire" in kws)
    assert desire_readers, (
        "no reader searches approval_lesson by related_desire any more. Either the readers "
        "changed or the scan went blind — re-measure the loop and update this record."
    )

    assert "related_approval_id" in producer_keywords, (
        "the producer no longer records which decision it came from"
    )
    assert "related_desire" in producer_keywords, (
        f"the producer stopped setting related_desire, which {desire_readers} search by — "
        "the record is invisible to them again. See PROJECT_STATUS_REVIEW.md §3.1 item 4."
    )
    assert "structured_data" in producer_keywords, (
        "the producer stopped setting structured_data. Both penalty readers keep only the "
        'records whose structured_data["decision"] is "rejected", so they go blind again. '
        "See PROJECT_STATUS_REVIEW.md §3.1 item 4."
    )


def test_a_rejected_decision_reaches_both_penalty_readers(tmp_path) -> None:
    """End to end: the real producer, the real store, both real readers.

    **This is the pin that can see a value mismatch.** The structural test above only shows
    that the two sides *name* the same keys; they could name the same keys and still disagree
    about what ``decision`` holds. So this one runs ``ReflectionEngine.reflect`` and then the
    two penalty readers themselves, and asserts that each charges something.

    Nothing supplies ``approval_decisions`` in production yet (A-11 ③), so **no other test
    exercises this path at all** — which is precisely why it is pinned here rather than left
    to an integration suite that would report nothing.

    The negative controls carry the weight: the same query under a *different* desire must
    find nothing, and an ``approved`` decision must produce no record. Without them, a reader
    that ignored its arguments entirely would pass.
    """
    from aegis_ai.autonomous.autonomous_loop import AutonomousLoop
    from aegis_ai.autonomous.motivation_arbiter import MotivationArbiter
    from aegis_ai.memory.memory_manager import MemoryManager
    from aegis_ai.memory.memory_store import MemoryStore
    from aegis_ai.reflection.reflection_engine import ReflectionEngine

    store = MemoryStore(data_dir=str(tmp_path / "store"))
    ReflectionEngine(memory_store=store).reflect(
        task_id="t1",
        approval_decisions=[
            {
                "status": "rejected",
                "capability_id": "pc-server.files.delete",
                "reason": "not now",
                "approval_id": "ap1",
            }
        ],
        source_desire="security",
    )

    # The query both readers make, verbatim.
    found = store.search_memories(
        memory_type="approval_lesson",
        related_desire="security",
        min_importance=0.5,
        limit=3,
    )
    assert len(found) == 1, (
        "the producer's approval_lesson is not visible to the query both readers make "
        f"({len(found)} found) — the growth loop would stay open even once a caller supplies "
        "approval_decisions"
    )
    assert found[0].structured_data.get("decision") == "rejected", (
        "the record is found but carries a different decision value than the readers compare "
        f"against: {found[0].structured_data!r}"
    )

    arbiter = MotivationArbiter(memory_store=store)
    penalty, reason = arbiter._check_memory_penalties("t2", "security")
    assert penalty > 0.0, f"the arbiter no longer penalizes a rejected desire: {reason!r}"

    loop = AutonomousLoop(data_dir=str(tmp_path / "autonomous"))
    loop._memory_manager = MemoryManager(memory_store=store)
    penalty, reason = loop._recent_failure_penalty("security")
    assert penalty > 0.0, f"the autonomous loop no longer penalizes a rejected desire: {reason!r}"

    # Negative controls — the readers must be matching on something, not merely returning rows.
    other = store.search_memories(
        memory_type="approval_lesson",
        related_desire="finance",
        min_importance=0.5,
        limit=3,
    )
    assert other == [], "the record is visible under an unrelated desire; related_desire is ignored"
    assert loop._recent_failure_penalty("finance")[0] == 0.0
    assert arbiter._check_memory_penalties("t3", "finance")[0] == 0.0

    empty = MemoryStore(data_dir=str(tmp_path / "store2"))
    ReflectionEngine(memory_store=empty).reflect(
        task_id="t4",
        approval_decisions=[{"status": "approved", "capability_id": "x"}],
        source_desire="security",
    )
    assert empty.search_memories(memory_type="approval_lesson", limit=10) == [], (
        "an approved decision now produces an approval_lesson; the producer's guard moved"
    )


def test_the_penalty_readers_filter_on_a_key_the_producer_writes() -> None:
    """Name the reader half of the contract, so neither side can drift unobserved.

    Kept separate from the producer-side pin on purpose: this one discovers the readers by
    AST, so a new module that starts filtering on ``structured_data["decision"]`` without
    also searching ``approval_lesson`` fails here.
    """
    filtering = _modules_filtering_on_structured_data_key("decision")

    assert filtering, (
        "no module filters approval lessons on structured_data['decision'] any more; "
        "re-measure this pin"
    )
    assert filtering <= set(_approval_lesson_readers()), (
        "these modules filter on 'decision' but were not found as approval_lesson readers: "
        f"{sorted(filtering - set(_approval_lesson_readers()))}"
    )


# ── B-5 ① (2026-10-01): the link that was missing, and its failure mode ────────
#
# The argument is supplied now, so the thing worth pinning changed: not "is it supplied"
# but "can the supplier be wrong". It can — ``ConfirmationRequest.desire`` is LLM-supplied
# — so the supplier drops anything it cannot attribute, and these tests hold that line.


class _FakeDesires:
    """Minimal stand-in for the desire system: the loop only calls get_all_desires()."""

    def __init__(self, names: list[str]) -> None:
        self._names = list(names)

    def get_all_desires(self) -> dict[str, object]:
        return {name: object() for name in self._names}


def _loop_with(tmp_path, names: list[str]):
    """A real loop over a real ConfirmationStore, with a stub desire system."""
    from aegis_ai.autonomous.autonomous_loop import AutonomousLoop
    from aegis_ai.confirmation import ConfirmationStore

    confirmations = ConfirmationStore(str(tmp_path / "confirmations"))
    loop = AutonomousLoop(
        desire_system=_FakeDesires(names),
        confirmation_store=confirmations,
        data_dir=str(tmp_path / "autonomous"),
    )
    return loop, confirmations


def test_a_rejection_is_only_learned_when_its_desire_is_real(tmp_path) -> None:
    """The link fails **closed**: no desire, or an invented one, yields no lesson.

    This is why B-5 ① needed a decision rather than a one-line wiring. Attributing a
    rejection to a desire that did not raise it punishes an unrelated desire, and a wrong
    penalty silently trains AEGIS against the wrong thing — whereas a missing lesson is
    merely a loop that stays open, which is the state it was already in.
    """
    loop, confirmations = _loop_with(tmp_path, ["security"])

    confirmations.request(summary="delete the logs?", desire="")
    confirmations.request(summary="delete the logs?", desire="does-not-exist")
    for item in confirmations.all(limit=10):
        confirmations.reject(item.approval_id, decided_by="user")

    assert loop._rejected_confirmations_by_desire() == {}, (
        "an unattributable rejection became a lesson. The supplier must drop confirmations "
        "whose desire is empty or absent from the live desire set."
    )

    # Positive control — without it, a supplier that always returned {} would pass.
    confirmations.request(summary="delete the logs?", desire="security")
    good = [
        item
        for item in confirmations.all(limit=10)
        if item.desire == "security" and item.status == "pending"
    ]
    assert good, "the positive-control confirmation was not recorded"
    confirmations.reject(good[0].approval_id, decided_by="user")

    grouped = loop._rejected_confirmations_by_desire()
    assert set(grouped) == {"security"}, f"a real desire was not learned: {grouped}"
    assert len(grouped["security"]) == 1


def test_a_rejection_is_reflected_once_not_every_cycle(tmp_path) -> None:
    """A decided confirmation stays in the store forever, so the supplier must not re-emit it.

    Without the record, every cycle would write another ``approval_lesson`` for the same
    rejection. The readers charge ``0.2 * len(rejected)`` against a 0.9 ceiling, so a single
    user decision would ratchet the penalty to the cap.
    """
    loop, confirmations = _loop_with(tmp_path, ["security"])
    confirmations.request(summary="delete the logs?", desire="security")
    item = confirmations.all(limit=10)[0]
    confirmations.reject(item.approval_id, decided_by="user")

    first = loop._rejected_confirmations_by_desire()
    assert set(first) == {"security"}, f"the rejection was not learned at all: {first}"

    loop._reflected_approval_ids.update(
        str(decision.get("approval_id") or "") for decision in first["security"]
    )
    assert loop._rejected_confirmations_by_desire() == {}, (
        "the same rejection would be reflected again on the next cycle"
    )

    # And the record has to survive a restart, or the loop re-learns everything on boot.
    loop._save()
    loop._reflected_approval_ids.clear()
    loop._load()
    assert item.approval_id in loop._reflected_approval_ids, (
        "the already-reflected ids were not persisted, so a restart re-reflects every "
        "rejection still in the store"
    )


def test_the_loop_reads_the_confirmation_store_without_answering() -> None:
    """The loop may see what the user decided; it may never ask or answer.

    Reading is the new half of B-5 ①. The boundary that must not move is the other
    direction: calling ``request`` / ``approve`` / ``reject`` / ``resolve`` from the loop
    would rebuild the forced approval gate retired on 2026-09-27.
    """
    tree = _parsed(_SRC / "aegis_ai" / "autonomous" / "autonomous_loop.py")

    called = {
        node.func.attr
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and isinstance(node.func.value, ast.Attribute)
        and node.func.value.attr == "_confirmations"
    }

    assert called, "the loop no longer reads the confirmation store; re-measure this pin"
    assert called <= {"all", "get", "pending", "pending_count"}, (
        f"the loop calls more of the confirmation store than it may: {sorted(called)}. "
        "request/approve/reject/resolve belong to AEGIS-as-asker and to the user — the loop "
        "answering its own question is the retired gate."
    )


def test_a_rejected_confirmation_reaches_both_readers_through_the_loop(tmp_path) -> None:
    """End to end through the **loop**: rejection -> lesson -> both readers charge.

    The older end-to-end test drives ``reflect()`` directly, so it proves the producer and
    the readers agree about the record — but not that anything supplies the producer. This
    one starts from a rejected confirmation and runs the loop's own supplier, which is the
    link B-5 ① was about, then asks both readers.
    """
    from aegis_ai.autonomous.motivation_arbiter import MotivationArbiter
    from aegis_ai.memory.memory_manager import MemoryManager
    from aegis_ai.memory.memory_store import MemoryStore
    from aegis_ai.reflection.reflection_engine import ReflectionEngine

    memory = MemoryStore(data_dir=str(tmp_path / "store"))
    loop, confirmations = _loop_with(tmp_path, ["security"])
    loop._reflection = ReflectionEngine(memory_store=memory)
    loop._memory_manager = MemoryManager(memory_store=memory)

    confirmations.request(
        summary="Delete the old logs?",
        capability_id="pc-server.files.delete",
        desire="security",
    )
    item = confirmations.all(limit=10)[0]
    confirmations.reject(item.approval_id, decided_by="user")

    decisions = loop._rejected_confirmations_by_desire()["security"]
    loop._reflection.reflect(
        task_id="confirmation_review_security",
        approval_decisions=decisions,
        source_desire="security",
    )

    assert loop._recent_failure_penalty("security")[0] > 0.0, (
        "the loop's own supplier produced a lesson the loop's own reader cannot see"
    )
    arbiter = MotivationArbiter(memory_store=memory)
    assert arbiter._check_memory_penalties("t", "security")[0] > 0.0, (
        "the arbiter cannot see the lesson the loop produced"
    )
    # Negative control: the charge must be scoped to the desire that was rejected.
    assert loop._recent_failure_penalty("finance")[0] == 0.0
