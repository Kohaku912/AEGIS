"""L2 Autonomous Mind — DASHBOARD_V3_PLAN.md Phase L4.

L2 (自律思考層) は `L2Context` を組み立て、`LLMGateway.request(layer="L2", ...)`
で中期サイズの LLM に判断を仰ぎ、`L2Decision` を返す薄いファサード。

設計原則:
- 既存 `AutonomousLoop` には **触らない**。L2Mind は独立した薄いラッパーとして
  提供し、Phase L5 以降で `AutonomousLoop` を L2 化する選択肢を残す。
- 既存 Manager パターン遵守: state mutation はすべて Manager 経由 (Phase L4 では
  context 構築と decision 生成のみ。Task 登録は L4 後半 / L5 以降で実装)。
- L2 の prompt は `l2_default` profile (Phase L1 で追加済み) を必ず使用。
- L1 escalations は `L2Context.l1_summaries` に dict として注入。
- `L2Decision.escalate_to_l3` が True なら `L2Escalation` を生成し
  EventBus に publish (Phase L5 で L3Reasoner が受信)。

依存最小化:
- `memory_system` / `desire_system` / `task_state_provider` / `l1_summaries_provider`
  は optional。None のときは空 snapshot / 空 summary で代用 (テスト容易性)。
- `llm_gateway` は optional。None のときは `LLMGateway.instance()`。
"""
from __future__ import annotations

import json
import logging
import time
import uuid
from dataclasses import dataclass
from typing import Any

from aegis_ai.autonomous.l2_models import (
    L2Action,
    L2ActionType,
    L2Context,
    L2Decision,
    L2Escalation,
)

logger = logging.getLogger("aegis_ai.autonomous.l2_mind")

_L2_SYSTEM_PROMPT = """You are L2 (Autonomous Mind) of AEGIS. You integrate world state, memory, desires, active tasks, and L1 escalations into a single decision.

Decide ONE of:
- task: produce a concrete task spec {capability_id, args, reason}
- escalate_l3: produce a problem for L3 Deep Reasoner {problem, context_summary}
- observe: just re-evaluate later
- noop: do nothing

Respond with JSON: {"action_type": "task"|"escalate_l3"|"observe"|"noop", "task_spec"|"l3_problem": {...}, "reason": "...", "plan": "...", "confidence": 0.0-1.0, "escalate_to_l3": bool}

Be concise. If `l1_summaries` contains a high-priority observation that requires L3 reasoning, choose escalate_l3. If desires are low and you have a concrete plan, choose task. Otherwise noop or observe."""


@dataclass
class L2AutonomousMind:
    """L2 Autonomous Mind — context builder + decision generator.

    Attributes:
        llm_gateway: L2 用 LLM gateway (None なら singleton を使う)
        memory_system: 既存 memory (None なら空 summary)
        desire_system: 既存 desire (None なら空 snapshot)
        task_state_provider: active task を提供する callable
        l1_summaries_provider: L1 observation summary を提供する callable
        event_publisher: EventBus publish callable (None なら no-op)
        enabled: master switch
        l3_confidence_threshold: この値未満なら escalate_to_l3 = True を推奨
        cycle_interval_seconds: 定期起動間隔 (DoD: 30 分)
    """

    llm_gateway: Any = None
    memory_system: Any = None
    desire_system: Any = None
    task_state_provider: Any = None  # callable returning list[dict]
    l1_summaries_provider: Any = None  # callable returning list[dict]
    world_state_provider: Any = None  # callable returning dict
    obligations_provider: Any = None  # callable returning list[dict]
    recent_failures_provider: Any = None  # callable returning list[str]
    event_publisher: Any = None  # callable(event_type, payload)
    task_manager: Any = None
    execution_engine: Any = None
    capability_catalog: Any = None
    enabled: bool = True
    l3_confidence_threshold: float = 0.4
    cycle_interval_seconds: int = 1800  # 30 分
    last_cycle_at_ms: int = 0

    # ------------------------------------------------------------------
    # dependency resolution
    # ------------------------------------------------------------------
    def _get_gateway(self) -> Any:
        if self.llm_gateway is not None:
            return self.llm_gateway
        from aegis_ai.llm.gateway import LLMGateway

        gw = LLMGateway.instance()
        if gw is None:
            raise RuntimeError(
                "No LLMGateway registered. Set AegisRuntime first or pass llm_gateway explicitly."
            )
        return gw

    def _publish(self, event_type: str, payload: dict[str, Any]) -> None:
        if self.event_publisher is None:
            logger.debug("L2 publish skipped (no event_publisher): %s", event_type)
            return
        try:
            self.event_publisher(event_type, payload)
        except Exception:  # noqa: BLE001
            logger.exception("L2 event publish failed: %s", event_type)

    # ------------------------------------------------------------------
    # context construction
    # ------------------------------------------------------------------
    def _safe_call(self, fn: Any, default: Any) -> Any:
        if fn is None:
            return default
        try:
            return fn()
        except Exception:  # noqa: BLE001
            logger.exception("L2 provider failed")
            return default

    def build_context(self) -> L2Context:
        """L2Context を組み立てる.

        - memory_system: `summarize_recent(max_entries=5)` のような API を期待
          (なければ `.recent()` / `.summarize()` / 単純 `repr` にフォールバック)
        - desire_system: `get_snapshot()` のような API を期待 (なければ空 dict)
        - task_state_provider: list[dict] を返す callable
        - l1_summaries_provider: list[dict] を返す callable
        """
        memory_summary = ""
        if self.memory_system is not None:
            for method_name in ("summarize_recent", "summarize", "recent"):
                method = getattr(self.memory_system, method_name, None)
                if callable(method):
                    try:
                        memory_summary = str(method(max_entries=5) if "recent" in method_name else method())
                    except Exception:  # noqa: BLE001
                        memory_summary = ""
                    break

        desire_snapshot: dict[str, float] = {}
        if self.desire_system is not None:
            for method_name in ("get_snapshot", "snapshot", "to_dict", "as_dict"):
                method = getattr(self.desire_system, method_name, None)
                if callable(method):
                    try:
                        value = method()
                        if isinstance(value, dict):
                            desire_snapshot = {
                                str(k): float(v) for k, v in value.items() if isinstance(v, (int, float))
                            }
                    except Exception:  # noqa: BLE001
                        desire_snapshot = {}
                    break

        task_state = self._safe_call(self.task_state_provider, [])
        if not isinstance(task_state, list):
            task_state = []
        l1_summaries = self._safe_call(self.l1_summaries_provider, [])
        if not isinstance(l1_summaries, list):
            l1_summaries = []
        world_state = self._safe_call(self.world_state_provider, {})
        if not isinstance(world_state, dict):
            world_state = {}
        world_state = {"now_ms": int(time.time() * 1000), **world_state}
        pending_obligations = self._safe_call(self.obligations_provider, [])
        if not isinstance(pending_obligations, list):
            pending_obligations = []
        recent_failures = self._safe_call(self.recent_failures_provider, [])
        if not isinstance(recent_failures, list):
            recent_failures = []

        return L2Context(
            world_state=world_state,
            memory_summary=memory_summary,
            desire_snapshot=desire_snapshot,
            task_state=[dict(t) for t in task_state],
            l1_summaries=[dict(s) for s in l1_summaries],
            pending_obligations=[dict(item) for item in pending_obligations if isinstance(item, dict)],
            recent_failures=[str(item) for item in recent_failures if item],
            raw={
                "memory_system": repr(self.memory_system)[:200],
                "desire_system": repr(self.desire_system)[:200],
                "world_state_provider": repr(self.world_state_provider)[:200],
            },
        )

    # ------------------------------------------------------------------
    # decision generation
    # ------------------------------------------------------------------
    def decide(self, context: L2Context | None = None) -> L2Decision:
        """L2Context から L2Decision を生成.

        - `enabled=False` のとき NOOP を返す
        - LLM 呼び出しに失敗したら安全側に倒して NOOP を返す (instruction.md §38)
        """
        if not self.enabled:
            return L2Decision(
                action=L2Action(type=L2ActionType.NOOP, reason="L2 mind disabled"),
                context=context,
            )

        ctx = context or self.build_context()
        self._publish("l2.thinking", {"context_size": len(ctx.to_prompt())})

        try:
            gateway = self._get_gateway()
            response = gateway.request(
                layer="L2",
                prompt=ctx.to_prompt(),
                system_prompt=_L2_SYSTEM_PROMPT,
                json_mode=True,
                context_meta={"caller": "l2_mind", "layer": "L2"},
            )
        except Exception as exc:  # noqa: BLE001
            logger.exception("L2 gateway.request failed: %r", exc)
            return L2Decision(
                action=L2Action(type=L2ActionType.NOOP, reason=f"gateway error: {exc!r}"),
                confidence=0.0,
                context=ctx,
            )

        decision = self._parse_decision(response.content if response.success else "", ctx)
        self.last_cycle_at_ms = int(time.time() * 1000)
        self._publish("l2.decision", decision.to_payload())

        if decision.escalate_to_l3:
            self._publish(
                "l2.escalation",
                L2Escalation(
                    problem=decision.action.l3_problem.get("problem", decision.plan) if isinstance(decision.action.l3_problem, dict) else decision.plan,
                    context_summary=ctx.to_prompt(),
                    l1_observations=list(ctx.l1_summaries),
                    reason=decision.action.reason,
                ).to_payload(),
            )
        return decision

    def _parse_decision(self, content: str, ctx: L2Context) -> L2Decision:
        """LLM 出力 (JSON) を L2Decision に parse.

        失敗時は安全側に倒して NOOP を返す (フォールバック禁止方針、instruction.md §38)。
        """
        try:
            data = json.loads(content)
        except (json.JSONDecodeError, TypeError):
            return L2Decision(
                action=L2Action(type=L2ActionType.NOOP, reason="json parse failed"),
                confidence=0.0,
                context=ctx,
            )

        if not isinstance(data, dict):
            return L2Decision(
                action=L2Action(type=L2ActionType.NOOP, reason="non-dict llm output"),
                confidence=0.0,
                context=ctx,
            )

        try:
            action_type = L2ActionType(str(data.get("action_type", "noop")).strip().lower())
        except ValueError:
            action_type = L2ActionType.NOOP

        confidence = float(data.get("confidence", 0.0) or 0.0)
        plan = str(data.get("plan", ""))
        reason = str(data.get("reason", ""))
        escalate = bool(data.get("escalate_to_l3", False))

        # auto-escalate when confidence is low (Phase L4 explicit rule)
        if confidence < self.l3_confidence_threshold and action_type in (L2ActionType.TASK, L2ActionType.OBSERVE):
            escalate = True
            reason = (
                (reason + " ") if reason else ""
            ) + f"[auto] confidence {confidence:.2f} < threshold {self.l3_confidence_threshold:.2f}"

        task_spec = data.get("task_spec") if action_type == L2ActionType.TASK else {}
        l3_problem = data.get("l3_problem") if action_type == L2ActionType.ESCALATE_L3 else {}
        if not isinstance(task_spec, dict):
            task_spec = {}
        if not isinstance(l3_problem, dict):
            l3_problem = {}

        return L2Decision(
            action=L2Action(
                type=action_type,
                task_spec=task_spec,
                l3_problem=l3_problem,
                reason=reason,
            ),
            plan=plan,
            confidence=confidence,
            escalate_to_l3=escalate or action_type == L2ActionType.ESCALATE_L3,
            context=ctx,
        )

    # ------------------------------------------------------------------
    # convenience
    # ------------------------------------------------------------------
    def should_run_cycle(self, now_ms: int | None = None) -> bool:
        """定期 cycle を回すタイミングか."""
        if not self.enabled:
            return False
        now = int(now_ms if now_ms is not None else time.time() * 1000)
        if self.last_cycle_at_ms == 0:
            return True
        return (now - self.last_cycle_at_ms) >= self.cycle_interval_seconds * 1000

    def escalate_to_l3(
        self,
        problem_text: str,
        *,
        context: dict[str, Any] | None = None,
        l1_observations: list[dict[str, Any]] | None = None,
        reason: str = "",
        constraints: dict[str, Any] | None = None,
    ) -> Any | None:
        """L3 Reasoner に escalation する convenience (DASHBOARD_V3_PLAN.md Phase L5).

        Returns:
            `L3Result` (成功時) または None (L3 disabled / 失敗時)。

        Notes:
            - L3 は `aegis_ai.llm.l3_reasoner.L3Reasoner` を singleton 風に解決する。
              runtime 未起動なら None 返却。
            - L3 の結果は L2 が Validation 後に Task 化する責務 (本メソッドは L3 呼び出しのみ)。
        """
        from aegis_ai.llm.l3_models import L3Problem
        from aegis_ai.llm.l3_reasoner import L3Reasoner

        if not self.enabled:
            return None
        # L3Reasoner singleton (なければ生成)
        reasoner = getattr(self, "_l3_reasoner", None)
        if reasoner is None:
            reasoner = L3Reasoner(
                llm_gateway=self.llm_gateway,
                capability_catalog=getattr(self, "capability_catalog", None),
                event_publisher=self.event_publisher,
            )
            self._l3_reasoner = reasoner
        problem = L3Problem(
            problem=problem_text,
            context=dict(context or {}),
            l1_observations=list(l1_observations or []),
            constraints=dict(constraints or {}),
            reason=reason,
        )
        return reasoner.reason(problem)

    def _get_catalog(self) -> Any | None:
        if self.capability_catalog is not None:
            return self.capability_catalog
        try:
            from aegis_ai.capability_catalog import CapabilityCatalog

            return CapabilityCatalog.instance()
        except Exception:  # noqa: BLE001
            return None

    def _resolve_manifest(self, capability_id: str) -> Any | None:
        if not capability_id:
            return None
        catalog = self._get_catalog()
        if catalog is None or not hasattr(catalog, "resolve"):
            return None
        try:
            return catalog.resolve(capability_id)
        except Exception:  # noqa: BLE001
            logger.debug("L2 manifest resolve failed for %s", capability_id, exc_info=True)
            return None

    def _risk_category_for_capability(self, capability_id: str) -> Any:
        """Classify a capability's action kind for the plan step.

        This is an **annotation**. It does not decide whether a step may run:
        the only deny left is a capability the operator switched off
        (``enabled: false`` — see ``LLMTaskInterpreter._validate_safety``).

        ``FORBIDDEN`` is therefore **no longer** mapped to ``BLOCKED``: a risk
        *label* must not create a deny, and a forbidden capability is already
        kept out of the catalog the LLM plans from
        (``capability_catalog._capability_from_manifest`` skips it).

        The fallback is the most consequential category rather than ``READ``,
        because an unrecognised label is *unknown* — and claiming "read-only,
        no side effects" for something we could not classify is the same
        fabrication this codebase treats as a bug everywhere else.
        """
        from aegis_ai.task_plan import RiskCategory

        manifest = self._resolve_manifest(capability_id)
        risk_label = str(
            getattr(manifest, "risk_level", "") or getattr(manifest, "manifest_risk_level", "")
        ).upper()
        if risk_label in {"READ_ONLY", "LOW"}:
            return RiskCategory.READ
        if risk_label in {"SAFE_ACTION", "SAFE"}:
            return RiskCategory.OBSERVE
        if risk_label in {"APPROVAL_REQUIRED", "MEDIUM"}:
            return RiskCategory.EXTERNAL_SEND
        return RiskCategory.DEVICE_ACTION

    def _plan_from_task_spec(self, decision: L2Decision) -> Any | None:
        from aegis_ai.task_plan import PlanStep, TaskPlan

        task_spec = dict(decision.action.task_spec or {})
        capability_id = str(task_spec.get("capability_id") or "").strip()
        if not capability_id:
            return None
        args = dict(task_spec.get("args") or {})
        step_id = f"l2_{uuid.uuid4().hex[:8]}"
        description = str(task_spec.get("description") or decision.plan or decision.action.reason or capability_id)
        expected_result = str(task_spec.get("expected_result") or decision.plan or description)
        plan = TaskPlan(
            plan_id=f"l2plan_{uuid.uuid4().hex[:10]}",
            user_goal=str(task_spec.get("goal") or description),
            interpreted_request=description,
            required_capabilities=[capability_id],
            expected_result=expected_result,
            verification_plan=str(task_spec.get("verification_plan") or expected_result),
            steps=[
                PlanStep(
                    step_id=step_id,
                    description=description,
                    action_type="tool_invoke",
                    capability_id=capability_id,
                    params=args,
                    risk_category=self._risk_category_for_capability(capability_id),
                    expected_result=expected_result,
                )
            ],
        )
        return plan

    def _plan_from_l3_result(self, l3_result: Any, *, fallback_goal: str = "") -> Any | None:
        from aegis_ai.task_plan import PlanStep, TaskPlan

        raw_steps = list(getattr(getattr(l3_result, "plan", None), "steps", []) or [])
        plan_steps: list[Any] = []
        required_capabilities: list[str] = []
        for raw_step in raw_steps:
            capability_id = str(getattr(raw_step, "capability_id", "") or "").strip()
            if not capability_id:
                continue
            required_capabilities.append(capability_id)
            description = str(getattr(raw_step, "reason", "") or capability_id)
            plan_steps.append(
                PlanStep(
                    step_id=f"l3_{uuid.uuid4().hex[:8]}",
                    description=description,
                    action_type="tool_invoke",
                    capability_id=capability_id,
                    params=dict(getattr(raw_step, "args", {}) or {}),
                    risk_category=self._risk_category_for_capability(capability_id),
                    expected_result=description,
                )
            )
        if not plan_steps:
            return None
        reasoning_summary = str(getattr(l3_result, "reasoning_summary", "") or fallback_goal or "L3 recommendation")
        return TaskPlan(
            plan_id=f"l3plan_{uuid.uuid4().hex[:10]}",
            user_goal=fallback_goal or reasoning_summary,
            interpreted_request=reasoning_summary,
            assumptions=[
                str(item)
                for item in list(getattr(getattr(l3_result, "plan", None), "assumptions", []) or [])
                if item
            ],
            risk_notes=[
                str(item)
                for item in list(getattr(getattr(l3_result, "plan", None), "risks", []) or [])
                if item
            ],
            required_capabilities=required_capabilities,
            expected_result=reasoning_summary,
            verification_plan=reasoning_summary,
            steps=plan_steps,
        )

    def _create_task_and_execute(self, plan: Any, *, title: str, goal: str, source: str) -> dict[str, Any]:
        task_manager = self.task_manager
        execution_engine = self.execution_engine
        if task_manager is None or execution_engine is None or plan is None:
            return {"handled": False, "reason": "task bridge is not configured"}
        try:
            task = task_manager.create_task(
                title=title[:120] or "L2 autonomous task",
                goal=goal[:500] or title[:120],
                source=source,
                priority=80,
            )
            task_id = str(task.get("task_id") or "")
            response = execution_engine.execute_task(task_id, plan)
            return {
                "handled": True,
                "task_id": task_id,
                "execution_text": str(getattr(response, "text", "") or ""),
            }
        except Exception as exc:  # noqa: BLE001
            logger.exception("L2 task materialization failed")
            return {"handled": False, "reason": f"task materialization failed: {exc!r}"}

    def run_once(self, context: L2Context | None = None) -> dict[str, Any]:
        """Run one L2 reasoning pass and, when possible, materialize work via Managers."""
        ctx = context or self.build_context()
        decision = self.decide(ctx)
        result: dict[str, Any] = {
            "handled": False,
            "action_type": decision.action.type.value,
            "reason": decision.action.reason,
            "confidence": decision.confidence,
            "plan": decision.plan,
        }
        if decision.action.type == L2ActionType.NOOP:
            result["handled"] = True
            return result
        if decision.action.type == L2ActionType.OBSERVE and not decision.escalate_to_l3:
            result["handled"] = True
            return result

        if decision.escalate_to_l3:
            l3_problem = dict(decision.action.l3_problem or {})
            problem_text = str(l3_problem.get("problem") or decision.plan or decision.action.reason or "Need deeper reasoning")
            l3_result = self.escalate_to_l3(
                problem_text,
                context={
                    "world_state": dict(ctx.world_state),
                    "memory_summary": ctx.memory_summary,
                    "pending_obligations": list(ctx.pending_obligations),
                    "recent_failures": list(ctx.recent_failures),
                },
                l1_observations=list(ctx.l1_summaries),
                reason=decision.action.reason,
                constraints=l3_problem.get("constraints") if isinstance(l3_problem.get("constraints"), dict) else {},
            )
            result["l3_invoked"] = True
            if l3_result is None:
                result["reason"] = f"{result['reason']} | L3 returned no result".strip(" |")
                return result
            recommended = str(getattr(getattr(l3_result, "recommended_action", None), "value", "abort"))
            result["l3_recommended_action"] = recommended
            if recommended == "abort":
                result["handled"] = True
                result["action_type"] = "abort"
                result["reason"] = str(getattr(l3_result, "reasoning_summary", "") or decision.action.reason)
                return result
            if recommended == "observe":
                result["handled"] = True
                result["action_type"] = "observe"
                result["reason"] = str(getattr(l3_result, "reasoning_summary", "") or decision.action.reason)
                return result
            plan = self._plan_from_l3_result(l3_result, fallback_goal=problem_text)
            execution = self._create_task_and_execute(
                plan,
                title=str(getattr(l3_result, "reasoning_summary", "") or problem_text or "L3 recommended task"),
                goal=problem_text,
                source="l2_l3_autonomous",
            )
            result.update(execution)
            return result

        if decision.action.type == L2ActionType.TASK:
            plan = self._plan_from_task_spec(decision)
            task_goal = str(
                dict(decision.action.task_spec or {}).get("goal")
                or decision.plan
                or decision.action.reason
                or "L2 autonomous task"
            )
            execution = self._create_task_and_execute(
                plan,
                title=task_goal,
                goal=task_goal,
                source="l2_autonomous",
            )
            result.update(execution)
            return result
        return result


__all__ = ["L2AutonomousMind"]
