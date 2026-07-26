"""LLM-authored daily planning grounded in commitments and open loops."""

from __future__ import annotations

import datetime as dt
import json
from pathlib import Path
from typing import Any

from aegis_ai.llm.json_utils import extract_json_object
from aegis_ai.personal_ai.storage import JsonStateFile, now_ms


class DailyPlanningManager:
    def __init__(
        self,
        data_dir: str,
        *,
        llm: Any = None,
        commitment_manager: Any = None,
        continuation_manager: Any = None,
    ) -> None:
        self._state_file = JsonStateFile(Path(data_dir) / "daily_plans.json", {"plans": {}})
        self._state = self._state_file.load()
        self._llm = llm
        self._commitments = commitment_manager
        self._continuations = continuation_manager
        self._agent_state: Any = None

    def set_agent_state(self, agent_state: Any) -> None:
        """Use the process-wide state facade for planning context."""
        self._agent_state = agent_state

    def generate(self, date: str | None = None) -> dict[str, Any]:
        day = date or dt.date.today().isoformat()
        commitments = self._commitments.list_commitments(status="open") if self._commitments else []
        open_loops = self._continuations.list_open() if self._continuations else []
        decision_context = (
            self._agent_state.snapshot(f"daily plan for {day}").to_dict()
            if self._agent_state is not None
            else {}
        )
        if self._llm is None:
            plan = {
                "date": day,
                "status": "deferred",
                "reason": "LLM unavailable; priorities were not guessed.",
                "items": [],
                "commitment_ids": [item.get("commitment_id") for item in commitments],
                "continuation_ids": [item.get("continuation_id") for item in open_loops],
                "generated_at": now_ms(),
            }
            self._store(day, plan)
            return plan
        prompt = f"""Create AEGIS's bounded plan for {day} from durable commitments and open loops.
Return JSON only. Do not invent obligations.

Commitments:
{json.dumps(commitments, ensure_ascii=False)}

Open loops:
{json.dumps(open_loops, ensure_ascii=False)}

Shared AgentState:
{json.dumps(decision_context, ensure_ascii=False)}

Return JSON with a summary and an items array. Each item must contain goal,
why_today, source_id, next_action, requires_approval, success_condition, and
stop_condition."""
        result = self._llm.generate(
            prompt=prompt,
            system_prompt="You are AEGIS's daily planner. Ground every item in supplied durable state.",
            max_tokens=900,
            json_mode=True,
        )
        if not getattr(result, "success", False):
            raise RuntimeError(getattr(result, "error", "Daily planning failed"))
        payload = extract_json_object(str(result.content))
        plan = {
            "date": day,
            "status": "planned",
            "summary": str(payload.get("summary") or ""),
            "items": list(payload.get("items") or [])[:20],
            "commitment_ids": [item.get("commitment_id") for item in commitments],
            "continuation_ids": [item.get("continuation_id") for item in open_loops],
            "generated_at": now_ms(),
        }
        self._store(day, plan)
        return plan

    def get(self, date: str | None = None) -> dict[str, Any] | None:
        return self._state.get("plans", {}).get(date or dt.date.today().isoformat())

    def _store(self, date: str, plan: dict[str, Any]) -> None:
        self._state.setdefault("plans", {})[date] = plan
        self._state_file.save(self._state)
