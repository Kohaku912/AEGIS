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
_ALLOWED_IMPORTERS: frozenset[str] = frozenset(
    {
        "aegis_ai/confirmation/__init__.py",
        "aegis_ai/confirmation/store.py",
        "aegis_ai/runtime.py",
        "aegis_ai/web/routes/approval.py",
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
