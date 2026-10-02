"""The agent-step path is entered only from sync contexts — which is what makes its thread hop dead.

`task/execution_engine._execute_agent_step` bridges sync to async. It checks for a running loop and,
**only if one exists**, runs the coroutine on a fresh ``ThreadPoolExecutor(max_workers=1)``; otherwise
it calls ``asyncio.run`` directly. ``docs/improvement-review.md`` §E-3 read the first branch as a
per-step cost ("the pool is built and destroyed once per agent step").

Measured 2026-10-02, and the premise is **refuted**: every path into the engine is sync, so that
branch is never entered.

* the only two real callers of ``execute_task`` are sync — ``autonomous/l2_mind.py``
  (``_create_task_and_execute``) and ``interaction/router.py`` (``_execute_plan``);
* ``interaction/router.py``'s ``InteractionRouter`` is **never constructed** anywhere in
  ``src/aegis_ai``, so that path is unreachable as well;
* the chain's own module, ``runtime.py``, defines **zero** ``async def`` — as do ``l2_mind.py``,
  ``router.py`` and ``execution_engine.py``;
* and no module that *does* define ``async def`` (11 of them) reaches the path — this file pins that.

The second test is the reason the branch must not be deleted as "dead code": it is a **guard** for a
future async caller, and it works. It is dead only because no caller meets its precondition.

A **text** scan for these names reports **2** modules and both are wrong: ``agents/runtime/
executor.py`` and ``agents/backends/openhands/backend.py`` name ``TaskExecutionEngine`` only in
docstrings and a comment. The reference check below is therefore ``ast``-based — a mention is not a
caller. That is also why the positive control is a *sync* module that genuinely calls the path.
"""

from __future__ import annotations

import ast
import asyncio
import concurrent.futures
from pathlib import Path

import aegis_ai
import aegis_ai.runtime as runtime_module
from aegis_ai.agents.runtime import executor as executor_module
from aegis_ai.task import execution_engine as engine_module
from aegis_ai.task_plan import PlanStep, StepStatus

# Names that, if referenced from a coroutine, would make the thread-hop branch live.
_ENTRY_NAMES = frozenset(
    {"execute_task", "_execute_agent_step", "_run_l2_pipeline", "run_once", "TaskExecutionEngine"}
)

#: The sync module that genuinely calls the path — the positive control for the reference check.
_CONTROL_MODULE = "autonomous/l2_mind.py"


def _production_modules() -> list[Path]:
    root = Path(aegis_ai.__file__).resolve().parent
    return sorted(root.rglob("*.py"))


def _defines_async(tree: ast.AST) -> bool:
    return any(isinstance(node, ast.AsyncFunctionDef) for node in ast.walk(tree))


def _references_entry(tree: ast.AST) -> bool:
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and node.id in _ENTRY_NAMES:
            return True
        if isinstance(node, ast.Attribute) and node.attr in _ENTRY_NAMES:
            return True
    return False


def test_no_async_module_reaches_the_agent_step_path() -> None:
    root = Path(aegis_ai.__file__).resolve().parent
    referencing: dict[str, bool] = {}
    scanned = 0
    async_modules = 0

    for path in _production_modules():
        tree = ast.parse(path.read_text(encoding="utf-8"))
        scanned += 1
        is_async = _defines_async(tree)
        async_modules += is_async
        if _references_entry(tree):
            referencing[path.relative_to(root).as_posix()] = is_async

    # Floors strictly weaker than the equality (measurement-hygiene rule 10).
    assert scanned >= 300, f"the scan collapsed: only {scanned} modules read"
    assert async_modules >= 5, f"only {async_modules} async-defining modules found — the filter is blind"

    # Positive control: the reference check must *see* a module that really calls the path. It asserts
    # visibility only — asserting that the control is also *sync* would fire first and mask the
    # equality's accurate message the moment that module becomes async (measurement-hygiene rule 10).
    assert len(referencing) >= 1, (
        "the reference check is blind: it saw no caller of the agent-step path at all, so the "
        "equality below would pass vacuously"
    )
    assert _CONTROL_MODULE in referencing, (
        f"{_CONTROL_MODULE} calls execute_task but the reference check did not see it"
    )

    from_async = {module for module, is_async in referencing.items() if is_async}
    assert from_async == set(), (
        "an async module now reaches the agent-step path, so the thread-hop branch is live: "
        f"{sorted(from_async)} — re-measure docs/improvement-review.md §E-3 and drop this pin"
    )


def _run_one_step(monkeypatch, *, from_async: bool) -> int:
    """Drive one agent step; return how many thread pools were constructed."""

    ran: list[bool] = []

    async def fake_run_agent_step(step: PlanStep, plan: object, *, backend: object) -> str:
        ran.append(True)
        step.status = StepStatus.COMPLETED
        return "ok"

    monkeypatch.setattr(executor_module, "run_agent_step", fake_run_agent_step)
    monkeypatch.setattr(executor_module, "is_agent_capability", lambda capability_id: True)

    class _Runtime:
        def get_agent_backend(self) -> object:
            return object()

    monkeypatch.setattr(runtime_module, "get_runtime", lambda: _Runtime())

    built: list[int] = []
    real_pool = concurrent.futures.ThreadPoolExecutor

    def counting_pool(*args: object, **kwargs: object) -> object:
        built.append(1)
        return real_pool(*args, **kwargs)  # type: ignore[arg-type]

    monkeypatch.setattr(concurrent.futures, "ThreadPoolExecutor", counting_pool)

    step = PlanStep(description="d", action_type="agent_delegate", capability_id="ai-server.agent.x")

    def call() -> str:
        # ``self`` is unused by the function (measured), so a bare object is enough.
        return engine_module.TaskExecutionEngine._execute_agent_step(object(), "t1", step, object())

    if from_async:

        async def in_loop() -> str:
            return call()

        asyncio.run(in_loop())
    else:
        call()

    assert ran, "the fake coroutine never ran — the probe did not exercise the bridge"
    return len(built)


def test_a_sync_caller_never_builds_a_thread_pool(monkeypatch) -> None:
    assert _run_one_step(monkeypatch, from_async=False) == 0


def test_an_async_caller_does_build_one(monkeypatch) -> None:
    """The guard works, so it is a guard — not dead code to delete."""

    assert _run_one_step(monkeypatch, from_async=True) == 1
