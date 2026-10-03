"""The burden check is actually *asked* — the loop, the cadence, and the transport, pinned.

``tests/test_burden_metric_is_judged.py`` pins the **definition** (§4 item 8: judged by the
judgment LLM, checked by the user periodically) and the shape of the question. This file
pins the half that makes the definition *do* something: something has to raise the ask, on
a cadence, through a transport that accepts it.

Each of those is a place the feature can look wired and be inert, which is why each is
measured rather than asserted structurally:

* **A first cycle must not ask.** The question is about a *period*, so there has to be one
  behind it. The loop starts the clock instead, and the clock survives a restart — a loop
  that re-starts every boot would re-ask every boot.
* **An untrustworthy judgement must not be asked about.** A profile the egress gate denies
  degrades to Mock, and asking the user to confirm a Mock's number is asking them to check
  something no model produced.
* **The ask must go through the capability**, not through the confirmation store the loop
  holds read-only (``tests/test_forced_gate_stays_retired.py`` pins that boundary; a loop
  that asks its own question is the forced gate retired on 2026-09-27).
* **The transport must accept it.** ``side_effects`` was a list where the capability's own
  ``input_schema`` declares a string, so the broker denied the ask at validation and the
  question never reached the user. The end-to-end test below therefore drives the **real**
  broker — real catalog, real policy engine, real capability client, real store — because a
  fake broker would have accepted the list and hidden exactly that defect.
"""

from __future__ import annotations

import ast
import json
from functools import lru_cache
from pathlib import Path
from typing import Any

import pytest

_REPO = Path(__file__).resolve().parents[2]
_SRC = _REPO / "ai-server" / "src"
_LOOP_MODULE = _SRC / "aegis_ai" / "autonomous" / "autonomous_loop.py"
_RUNTIME_MODULE = _SRC / "aegis_ai" / "runtime.py"
_CAPABILITIES_DIR = _REPO / "ai-server" / "capabilities"
_APPS_DIR = _REPO / "ai-server" / "apps"

#: The capability the ask must travel through. Named once so a rename is a deliberate edit
#: in one place rather than a silent no-op at the ask site.
_ASK_CAPABILITY = "ai-server.confirmation.request"

#: Methods on the confirmation store the loop may never call. Mirrors the boundary pinned
#: in ``test_forced_gate_stays_retired.py``; asserted again here *for this call site*,
#: because "the module as a whole is clean" does not mean "this new code path is".
_FORBIDDEN_STORE_CALLS = frozenset({"request", "approve", "reject", "resolve", "cancel"})


@lru_cache(maxsize=None)
def _tree(path: Path) -> ast.Module:
    return ast.parse(path.read_text(encoding="utf-8"))


def _function_source(tree: ast.Module, name: str) -> ast.AST:
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == name:
            return node
    raise AssertionError(f"`{name}` is gone from the module under test")


def _calls_on(node: ast.AST, attribute: str) -> list[ast.Call]:
    """Every ``x.<attribute>(...)`` call inside ``node``, whatever ``x`` is."""
    return [
        call
        for call in ast.walk(node)
        if isinstance(call, ast.Call)
        and isinstance(call.func, ast.Attribute)
        and call.func.attr == attribute
    ]


def _kwarg(call: ast.Call, name: str) -> ast.AST | None:
    for keyword in call.keywords:
        if keyword.arg == name:
            return keyword.value
    return None


# ── the real transport, so a fake cannot hide a schema or policy rejection ─────


class _Response:
    def __init__(
        self,
        content: str,
        *,
        provider: str = "typesafe",
        model: str = "jev-latest",
        success: bool = True,
        error: str = "",
    ) -> None:
        self.content = content
        self.provider_used = provider
        self.model_used = model
        self.success = success
        self.error = error


class _FakeLLM:
    """The judgment LLM, stubbed at the provider boundary — not at the metric."""

    def __init__(self, response: _Response) -> None:
        self._response = response
        self.calls: list[dict[str, Any]] = []

    def generate(self, **kwargs: Any) -> _Response:
        self.calls.append(kwargs)
        return self._response


_TRUSTWORTHY = '{"score": 0.7, "summary": "Saved you an errand.", "evidence": ["booked a table"]}'
_MOCK = '{"score": 0.9, "summary": "Looks good!", "evidence": []}'


@pytest.fixture
def real_broker(tmp_path: Path):
    """A real ToolBroker → real catalog → real capability client → real store chain.

    Deliberately not a fake. The defect this file exists to catch — an ask whose
    ``side_effects`` type the capability's own ``input_schema`` rejects — is invisible to a
    fake broker, because a fake broker does not run ``jsonschema`` and does not consult the
    policy engine. Everything here is the shipped object graph, minus the managers the ask
    path never touches.
    """
    from aegis_ai.audit import AuditLog
    from aegis_ai.capability_catalog import CapabilityCatalog
    from aegis_ai.confirmation import ConfirmationStore
    from aegis_ai.core_capabilities import AegisCoreCapabilityClient
    from policy_engine import create_default_policy_engine
    from server_executor import ServerExecutor
    from tool_broker import ToolBroker
    from tool_registry import ToolRegistry

    catalog = CapabilityCatalog(
        capabilities_dir=str(_CAPABILITIES_DIR),
        apps_dir=str(_APPS_DIR),
        data_dir=str(tmp_path),
    )
    registry = ToolRegistry()
    for capability in catalog.to_tool_registry_capabilities():
        try:
            registry.register_capability(capability)
        except ValueError:
            pass

    store = ConfirmationStore(str(tmp_path / "confirmations"))
    executor = ServerExecutor()
    executor.set_catalog(catalog)
    executor.register_client(
        "ai-server",
        AegisCoreCapabilityClient(
            data_dir=str(tmp_path / "core"),
            server_executor=executor,
            personal_managers={"confirmation_store": store},
        ),
    )
    broker = ToolBroker(
        registry=registry,
        policy_engine=create_default_policy_engine(),
        audit_log=AuditLog(path=str(tmp_path / "audit.jsonl")),
        server_executor=executor,
        folder_registry=catalog.get_folder_registry(),
        catalog=catalog,
        verification_service=None,
    )
    return broker, store


def _loop(tmp_path: Path, *, broker: Any = None, metric: Any = None):
    from aegis_ai.autonomous.autonomous_loop import AutonomousLoop

    loop = AutonomousLoop(
        llm_provider=None,
        tool_broker=broker,
        data_dir=str(tmp_path / "autonomous"),
    )
    if metric is not None:
        loop.set_burden_metric(metric)
    return loop


def _metric(*, response: _Response | None = None, interval_ms: int = 1_000):
    from aegis_ai.burden import BurdenMetric

    llm = _FakeLLM(response or _Response(_TRUSTWORTHY))
    return BurdenMetric(llm, ask_interval_ms=interval_ms), llm


# ── the ask reaches the user, through the real transport ──────────────────────


def test_the_loop_asks_the_user_through_the_capability(tmp_path: Path, real_broker) -> None:
    """End to end: due window → judgement → ask → the question is in the store.

    The store is the real one the capability client writes to, so this fails if the ask is
    denied by the policy engine, rejected by the manifest's ``input_schema``, or never
    raised at all. The judgement is stubbed only at the provider boundary, so the metric's
    own parsing and trustworthiness logic is exercised rather than mocked out.
    """
    broker, store = real_broker
    metric, _ = _metric()
    loop = _loop(tmp_path, broker=broker, metric=metric)

    now = 1_700_000_000_000
    loop._last_burden_ask_ms = now - metric.ask_interval_ms - 1

    assert store.all(limit=5) == [], "the store was not empty before the ask"

    loop._maybe_ask_burden_check(now)

    recorded = store.all(limit=5)
    assert len(recorded) == 1, (
        f"the burden check was not recorded (store has {len(recorded)} items). A denial "
        "here means the ask never reached the user: check the capability's input_schema "
        "against the fields `BurdenMetric.build_user_question` returns."
    )
    assert recorded[0].summary == "Did AEGIS make this period lighter for you?"
    assert recorded[0].status == "pending"
    assert recorded[0].capability_id == "burden_check"


def test_the_ask_carries_the_judgement_so_the_user_can_answer_it(tmp_path: Path, real_broker) -> None:
    """The question the user sees must contain the number they are checking.

    A check on a judgement the user cannot see is not a check — it is a yes/no button. The
    ``preview`` carries the assessment (score, summary, evidence) as JSON, so this asserts
    the preview is present and parses back to the assessment's own fields.
    """
    broker, store = real_broker
    metric, _ = _metric()
    loop = _loop(tmp_path, broker=broker, metric=metric)

    now = 1_700_000_000_000
    loop._last_burden_ask_ms = now - metric.ask_interval_ms - 1
    loop._maybe_ask_burden_check(now)

    recorded = store.all(limit=5)[0]
    preview = json.loads(recorded.preview)
    assert preview["score"] == pytest.approx(0.7), (
        "the preview does not carry the judged score, so the user cannot check it"
    )
    assert preview["evidence"] == ["booked a table"]
    assert preview["judged_by_provider"] == "typesafe", (
        "the preview hides which provider judged — the field that makes a degraded "
        "judgement visible"
    )
    assert recorded.reason == "Saved you an errand.", (
        "the reason shown to the user is not the judgement's own summary"
    )


def test_the_ask_advances_the_clock_so_it_is_not_repeated_every_cycle(tmp_path: Path, real_broker) -> None:
    """A cadence, not a one-shot and not a per-cycle nag."""
    broker, store = real_broker
    metric, llm = _metric(interval_ms=1_000)
    loop = _loop(tmp_path, broker=broker, metric=metric)

    now = 1_700_000_000_000
    loop._last_burden_ask_ms = now - 2_000
    loop._maybe_ask_burden_check(now)
    assert len(store.all(limit=5)) == 1
    assert loop._last_burden_ask_ms == now

    # Same clock: nothing more happens, and no second judgement is bought.
    loop._maybe_ask_burden_check(now)
    assert len(store.all(limit=5)) == 1, "the loop asked twice inside one interval"
    assert len(llm.calls) == 1, "the loop judged twice inside one interval"

    # Past the interval: it asks again, about the new period.
    later = now + 1_001
    loop._maybe_ask_burden_check(later)
    assert len(store.all(limit=5)) == 2, "the check never becomes due again"
    assert len(llm.calls) == 2


# ── the two ways it must decline to ask ──────────────────────────────────────


def test_a_first_cycle_starts_the_clock_instead_of_asking(tmp_path: Path, real_broker) -> None:
    """No period has been observed yet, so there is nothing to ask about.

    This is the loop's half of ``due_for_user_check(last_ask_ms=None, ...) == False``. The
    failure it prevents: a fresh install asks the user "did AEGIS make this period lighter
    for you?" before AEGIS has had a period.
    """
    broker, store = real_broker
    metric, llm = _metric()
    loop = _loop(tmp_path, broker=broker, metric=metric)

    assert loop._last_burden_ask_ms is None, "a fresh loop must start with no ask clock"

    now = 1_700_000_000_000
    loop._maybe_ask_burden_check(now)

    assert store.all(limit=5) == [], "the user was asked on a first run, about no period"
    assert llm.calls == [], "a judgement was bought before there was a period to judge"
    assert loop._last_burden_ask_ms == now, (
        "the first cycle did not start the clock, so the check would never become due"
    )


def test_a_mock_judgement_is_never_asked_about(tmp_path: Path, real_broker) -> None:
    """The allowlist trap, from the loop's side: a denied profile degrades to Mock.

    A Mock returns canned text, so its number says nothing about the user's life. Asking
    the user to confirm it would be asking them to check a number no model produced — and
    the clock must *not* advance, or a transient outage would silently skip the period.
    """
    broker, store = real_broker
    metric, _ = _metric(response=_Response(_MOCK, provider="mock", model="mock"))
    loop = _loop(tmp_path, broker=broker, metric=metric)

    now = 1_700_000_000_000
    clock = now - 2_000
    loop._last_burden_ask_ms = clock
    loop._maybe_ask_burden_check(now)

    assert store.all(limit=5) == [], (
        "the user was asked to confirm a Mock judgement — the allowlist trap is back, and "
        "this time it reaches the user's dashboard"
    )
    assert loop._last_burden_ask_ms == clock, (
        "the clock advanced on an untrustworthy judgement, so the period would be skipped"
    )


def test_a_failed_judgement_is_not_asked_about(tmp_path: Path, real_broker) -> None:
    """An errored judgement is recorded as one, and never becomes a question."""
    broker, store = real_broker
    metric, _ = _metric(
        response=_Response("", provider="typesafe", model="jev-latest", success=False, error="401")
    )
    loop = _loop(tmp_path, broker=broker, metric=metric)

    now = 1_700_000_000_000
    loop._last_burden_ask_ms = now - 2_000
    loop._maybe_ask_burden_check(now)

    assert store.all(limit=5) == []


def test_without_a_metric_the_loop_does_nothing(tmp_path: Path, real_broker) -> None:
    """The metric is opt-in by construction, and an unset one is not an error."""
    broker, store = real_broker
    loop = _loop(tmp_path, broker=broker, metric=None)

    now = 1_700_000_000_000
    loop._maybe_ask_burden_check(now)

    assert store.all(limit=5) == []
    assert loop._last_burden_ask_ms is None


# ── the clock survives a restart ─────────────────────────────────────────────


def test_the_ask_clock_survives_a_restart(tmp_path: Path, real_broker) -> None:
    """Without persistence the loop re-asks on every boot — a daily nag on a weekly cadence."""
    broker, _ = real_broker
    metric, _ = _metric()
    loop = _loop(tmp_path, broker=broker, metric=metric)

    now = 1_700_000_000_000
    loop._last_burden_ask_ms = now - 2_000
    loop._maybe_ask_burden_check(now)
    asked_at = loop._last_burden_ask_ms
    assert asked_at == now

    restarted = _loop(tmp_path, broker=broker, metric=metric)
    assert restarted._last_burden_ask_ms == asked_at, (
        "the ask clock did not survive a restart, so the loop re-asks on every boot"
    )

    # And the restored clock really suppresses the ask.
    restarted._maybe_ask_burden_check(now + 10)
    assert restarted._last_burden_ask_ms == asked_at


def test_a_stored_zero_is_not_read_as_a_real_clock(tmp_path: Path, real_broker) -> None:
    """``0`` and a missing key both mean "no period observed", not "asked at the epoch".

    The sentinel is ``None``, so a stored ``0`` must not be read as a real timestamp: it
    would make the first cycle report "due" and ask about a period that never happened.
    """
    broker, store = real_broker
    loop = _loop(tmp_path, broker=broker)
    state_path = Path(loop._data_dir) / "loop_state.json"
    state_path.write_text(json.dumps({"last_burden_ask_ms": 0}), encoding="utf-8")

    reloaded = _loop(tmp_path, broker=broker)
    assert reloaded._last_burden_ask_ms is None, (
        "a stored 0 was read as a real ask clock; the first cycle would ask immediately"
    )


# ── the activity handed to the judgement ─────────────────────────────────────


def test_the_activity_is_the_periods_work_not_the_loops_whole_history(tmp_path: Path) -> None:
    """A judgement over a window must see that window, or it reports last month as this one."""
    loop = _loop(tmp_path)
    log_path = Path(loop._data_dir) / "execution_log.jsonl"
    log_path.write_text(
        "\n".join(
            json.dumps(entry)
            for entry in (
                {
                    "timestamp_ms": 100,
                    "tasks": [{"what_was_done": "booked a table (too old)"}],
                },
                {
                    "timestamp_ms": 5_000,
                    "tasks": [{"what_was_done": "paid the rent"}],
                },
                {
                    "timestamp_ms": 6_000,
                    "tasks": [{"action_goal": "renewed the passport"}],
                },
            )
        ),
        encoding="utf-8",
    )

    activity = loop._burden_activity(window_start_ms=1_000)
    assert activity == ["paid the rent", "renewed the passport"], (
        f"the activity is not the window's work: {activity}"
    )


# ── structure: the boundary and the wiring ───────────────────────────────────


def test_the_loop_never_asks_through_the_store_it_holds_read_only() -> None:
    """The ask is a capability call; the store stays read-only in this loop.

    ``tests/test_forced_gate_stays_retired.py`` pins the boundary over the whole module.
    This asserts it for the *new* call site specifically, because a clean module does not
    make a new code path clean.
    """
    body = _function_source(_tree(_LOOP_MODULE), "_maybe_ask_burden_check")

    # The forbidden shape is `self._confirmations.<method>(...)`.
    on_the_store = {
        node.func.attr
        for node in ast.walk(body)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and isinstance(node.func.value, ast.Attribute)
        and node.func.value.attr == "_confirmations"
    }
    assert not (on_the_store & _FORBIDDEN_STORE_CALLS), (
        f"`_maybe_ask_burden_check` calls {sorted(on_the_store & _FORBIDDEN_STORE_CALLS)} "
        "on the confirmation store. The loop may read it and may never ask — the ask is "
        "AEGIS-as-asker's job, raised through the capability."
    )

    requests = [
        node
        for node in ast.walk(body)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "ToolExecutionRequest"
    ]
    assert requests, (
        "`_maybe_ask_burden_check` no longer builds a ToolExecutionRequest, so it is not "
        "raising the ask through the capability"
    )
    executed = {
        value for call in requests for value in _string_constants(_kwarg(call, "capability_id"))
    }
    assert executed == {_ASK_CAPABILITY}, (
        f"the ask no longer executes `{_ASK_CAPABILITY}`; observed {sorted(executed)}"
    )

    executed_via = {
        call.func.attr
        for call in _calls_on(body, "execute")
        if isinstance(call.func, ast.Attribute)
    }
    assert executed_via == {"execute"}, (
        "the request is built but never executed, so the ask is raised nowhere"
    )


def _string_constants(node: ast.AST | None) -> set[str]:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return {node.value}
    return set()


def test_the_run_loop_actually_calls_the_burden_check() -> None:
    """A method nothing calls is not a wiring. The loop body must reach it."""
    body = _function_source(_tree(_LOOP_MODULE), "_run_loop")
    called = {
        call.func.attr
        for call in _calls_on(body, "_maybe_ask_burden_check")
        if isinstance(call.func, ast.Attribute)
    }
    assert called == {"_maybe_ask_burden_check"}, (
        "`_run_loop` no longer calls `_maybe_ask_burden_check`, so the periodic user check "
        "never runs and the metric is judged into the void"
    )


def test_the_composition_root_hands_the_metric_to_the_loop() -> None:
    """The loop only asks if the runtime gave it a metric — pinned where it is given.

    A ``set_burden_metric`` that nobody calls is the "declared but ineffective" shape: the
    metric module, the loop method and the pins would all be present and green, and the
    user would never be asked anything.
    """
    tree = _tree(_RUNTIME_MODULE)
    setters = [
        call
        for call in _calls_on(tree, "set_burden_metric")
        if isinstance(call.func, ast.Attribute)
    ]
    assert setters, (
        "the composition root never calls `set_burden_metric`, so the loop has no metric "
        "and the periodic user check is dead"
    )

    constructed = {
        node.func.id
        for call in setters
        for node in ast.walk(call.args[0])
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
    }
    assert "BurdenMetric" in constructed, (
        "`set_burden_metric` is called with something other than a BurdenMetric; "
        f"observed {sorted(constructed)}"
    )


def test_the_wiring_lines_actually_run(tmp_path: Path) -> None:
    """Execute the composition root's two new lines — the function itself never runs.

    `_create_autonomous_loop` is called **only** by `start_autonomous_if_enabled`, which
    returns early unless `autonomous_loop_enabled` is set, so the suite never executes this
    function's body. The project has been bitten by exactly that: a wiring edit inside it
    left the whole suite green and only ruff's `F821` caught it. The AST test above proves
    the lines are *present*; this proves the three runtime facts about them — the import
    resolves, the constructor accepts one positional argument, and the loop accepts and
    stores the result — by running the same statements.
    """
    from aegis_ai.burden import BurdenMetric
    from aegis_ai.burden.metric import DEFAULT_ASK_INTERVAL_MS

    loop = _loop(tmp_path)
    assert loop._burden_metric is None, "a fresh loop already has a metric"

    # The composition root's exact call shape: one positional argument.
    loop.set_burden_metric(BurdenMetric(object()))

    assert loop._burden_metric is not None, "`set_burden_metric` did not store the metric"
    assert loop._burden_metric.ask_interval_ms == DEFAULT_ASK_INTERVAL_MS, (
        "the stored metric is not the shipped one"
    )


def test_the_composition_root_passes_exactly_one_positional_argument() -> None:
    """An arity mistake here is invisible to the suite and to `F821`.

    `BurdenMetric.__init__(self, llm, *, ask_interval_ms=...)` takes the LLM positionally,
    so `BurdenMetric()` or `BurdenMetric(a, b)` would raise only when the loop is switched
    on. Pinned as a shape, because there is no execution to fall back on.
    """
    from inspect import Parameter, signature

    from aegis_ai.burden import BurdenMetric

    first = [
        parameter
        for name, parameter in signature(BurdenMetric.__init__).parameters.items()
        if name != "self"
    ][0]
    assert first.kind in (Parameter.POSITIONAL_ONLY, Parameter.POSITIONAL_OR_KEYWORD), (
        f"`BurdenMetric.__init__`'s first parameter is {first.kind.name}, so the "
        "composition root's positional call would raise"
    )

    calls = [
        node
        for node in ast.walk(_tree(_RUNTIME_MODULE))
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "BurdenMetric"
    ]
    assert calls, "the composition root no longer constructs a BurdenMetric"
    for call in calls:
        assert len(call.args) == 1 and not call.keywords, (
            "the composition root constructs `BurdenMetric` with "
            f"{len(call.args)} positional args and {len(call.keywords)} keywords; the "
            "constructor takes exactly one positional argument (the LLM)"
        )
