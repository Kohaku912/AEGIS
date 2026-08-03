"""First-class Operation records for the observation dashboard."""

from __future__ import annotations

import json
import threading
import time
import uuid
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


def _now_ms() -> int:
    return int(time.time() * 1000)


def _new_id() -> str:
    return f"op_{uuid.uuid4().hex[:16]}"


@dataclass
class OperationStep:
    action: str = ""
    target: str = ""
    capability_id: str = ""
    input_summary: str = ""
    output_summary: str = ""
    changed_state: str = ""
    status: str = "ok"
    timestamp_ms: int = 0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class OperationRecord:
    """Canonical user-facing unit of AEGIS work."""

    operation_id: str = ""
    kind: str = "task"  # chat | autonomous | task | approval | event | schedule
    source: str = ""  # user | autonomous | event | schedule
    started_at: int = 0
    updated_at: int = 0
    duration_ms: int = 0
    action_summary: str = ""
    target_summary: str = ""
    purpose: str = ""
    decision_reason: str = ""
    result_summary: str = ""
    changed_state: str = ""
    verification_status: str = "unknown"  # passed | failed | unmet | skipped | unknown
    goal_status: str = "unknown"  # achieved | unmet | in_progress | not_applicable | unknown
    result_status: str = "unknown"  # success | partial | failed | awaiting_approval | non_action
    next_action: str = ""
    wait_reason: str = ""
    evidence_refs: list[str] = field(default_factory=list)
    linked_entity_ids: dict[str, list[str]] = field(default_factory=dict)
    trigger: dict[str, Any] = field(default_factory=dict)
    perceived: list[str] = field(default_factory=list)
    candidates: list[str] = field(default_factory=list)
    goal: str = ""
    steps: list[dict[str, Any]] = field(default_factory=list)
    verification: dict[str, Any] = field(default_factory=dict)
    presentation: dict[str, Any] = field(default_factory=dict)
    follow_up: dict[str, Any] = field(default_factory=dict)
    learning: dict[str, Any] = field(default_factory=dict)
    causal_chain: list[dict[str, Any]] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.operation_id:
            self.operation_id = _new_id()
        if not self.started_at:
            self.started_at = _now_ms()
        if not self.updated_at:
            self.updated_at = self.started_at

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        # Compatibility fields for existing Operations UI.
        data["title"] = self.action_summary or self.purpose or self.goal or self.operation_id
        data["summary"] = self.result_summary or self.action_summary
        data["what_happened"] = self.result_summary or self.action_summary
        data["narrative"] = self.result_summary or self.action_summary
        data["kind_label"] = _kind_label(self.kind, self.source)
        data["status"] = self.result_status
        data["target"] = self.target_summary
        data["skip_reason"] = self.wait_reason if self.result_status == "non_action" else ""
        data["decision"] = self.decision_reason
        return data

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> OperationRecord:
        known = {f.name for f in cls.__dataclass_fields__.values()}  # type: ignore[attr-defined]
        payload = {k: v for k, v in raw.items() if k in known}
        if isinstance(payload.get("learning"), list):
            payload["learning"] = {"items": payload["learning"]}
        return cls(**payload)


def _kind_label(kind: str, source: str) -> str:
    labels = {
        "chat": "ユーザー指示",
        "autonomous": "自律判断",
        "task": "タスク",
        "approval": "承認",
        "event": "イベント",
        "schedule": "Schedule",
    }
    if source == "user":
        return "ユーザー指示"
    if source == "schedule":
        return "Schedule"
    if source == "event":
        return "イベント"
    return labels.get(kind, kind or "操作")


def build_causal_chain(record: OperationRecord | dict[str, Any]) -> list[dict[str, Any]]:
    """Build a causal chain from structured operation fields only (no placeholder prose)."""
    data = record.to_dict() if isinstance(record, OperationRecord) else dict(record)
    steps = list(data.get("steps") or [])
    failed = [s for s in steps if str(s.get("status") or "").lower() in {"failed", "error"}]
    ok = [s for s in steps if str(s.get("status") or "").lower() not in {"failed", "error"}]
    non_action = str(data.get("result_status") or "") == "non_action" or bool(data.get("skip_reason") or data.get("wait_reason"))

    def stage(name: str, label: str, summary: str, status: str = "present", detail: str = "") -> dict[str, Any]:
        text = (summary or "").strip()
        return {
            "stage": name,
            "label": label,
            "summary": text[:280] if text else "",
            "status": status if text else "missing",
            "detail": (detail or "")[:280],
        }

    trigger = data.get("trigger") if isinstance(data.get("trigger"), dict) else {}
    trigger_summary = str(
        trigger.get("summary")
        or data.get("kind_label")
        or data.get("source")
        or data.get("kind")
        or ""
    )
    perceived = data.get("perceived") if isinstance(data.get("perceived"), list) else []
    perceived_text = " / ".join(str(item) for item in perceived[:4] if item)
    candidates = data.get("candidates") if isinstance(data.get("candidates"), list) else []
    candidates_text = " / ".join(str(item) for item in candidates[:5] if item)
    decision = str(data.get("decision_reason") or data.get("decision") or "")
    wait = str(data.get("wait_reason") or data.get("skip_reason") or "")
    goal = str(data.get("goal") or data.get("purpose") or "")
    result = str(data.get("result_summary") or data.get("what_happened") or data.get("narrative") or "")
    verification = data.get("verification") if isinstance(data.get("verification"), dict) else {}
    verification_summary = str(
        verification.get("summary")
        or data.get("verification_status")
        or ""
    )
    if not verification_summary and failed:
        verification_summary = f"失敗ステップ {len(failed)} 件"
    elif not verification_summary and ok and not non_action:
        verification_summary = str(data.get("goal_status") or "")
        if verification_summary in {"achieved", "unmet"}:
            verification_summary = "Goal達成" if verification_summary == "achieved" else "Goal未達"
        elif ok:
            verification_summary = ""

    presentation = data.get("presentation") if isinstance(data.get("presentation"), dict) else {}
    presentation_summary = str(presentation.get("summary") or presentation.get("surface") or "")
    follow_up = data.get("follow_up") if isinstance(data.get("follow_up"), dict) else {}
    follow_summary = str(
        follow_up.get("summary")
        or data.get("next_action")
        or wait
        or ""
    )
    learning = data.get("learning") if isinstance(data.get("learning"), dict) else {}
    learning_items = learning.get("items") if isinstance(learning.get("items"), list) else []
    learning_summary = str(learning.get("summary") or " / ".join(str(item) for item in learning_items[:3] if item))

    step_lines = []
    for step in steps[:6]:
        line = str(
            step.get("output_summary")
            or step.get("narrative")
            or step.get("summary")
            or step.get("action")
            or step.get("capability_id")
            or ""
        ).strip()
        if line:
            step_lines.append(line)

    chain = [
        stage("trigger", "Trigger", trigger_summary, detail=str(trigger.get("detail") or "")),
        stage("perceived", "認識した情報", perceived_text),
        stage("decision", "判断", decision or wait),
        stage(
            "candidates",
            "検討した候補",
            candidates_text or ("非行動" if non_action else ""),
            "present" if (candidates_text or non_action) else "missing",
        ),
        stage("goal", "Goal", goal),
        stage(
            "execution",
            "実行Step",
            " → ".join(step_lines) if step_lines else ("行動なし" if non_action else ""),
            "skipped" if non_action and not step_lines else ("present" if step_lines else "missing"),
            f"{len(ok)} 成功 / {len(failed)} 失敗" if steps else "",
        ),
        stage("result", "結果", result),
        stage("verification", "Verification", verification_summary),
        stage("presentation", "Presentation", presentation_summary),
        stage("follow_up", "Follow-up", follow_summary),
        stage("learning", "Learning", learning_summary),
    ]
    return chain


class OperationStore:
    """Append-only JSONL store for OperationRecord."""

    def __init__(self, data_dir: str | Path = "data") -> None:
        self._path = Path(data_dir) / "operations" / "operations.jsonl"
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.RLock()
        self._cache: dict[str, OperationRecord] = {}
        self._load()

    def _load(self) -> None:
        if not self._path.exists():
            return
        loaded: dict[str, OperationRecord] = {}
        try:
            with self._path.open("r", encoding="utf-8") as handle:
                for line in handle:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        raw = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    if not isinstance(raw, dict):
                        continue
                    record = OperationRecord.from_dict(raw)
                    loaded[record.operation_id] = record
        except OSError:
            return
        self._cache = loaded

    def upsert(self, record: OperationRecord) -> OperationRecord:
        with self._lock:
            record.updated_at = _now_ms()
            if not record.causal_chain:
                record.causal_chain = build_causal_chain(record)
            self._cache[record.operation_id] = record
            with self._path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(record.to_dict(), ensure_ascii=False) + "\n")
            return record

    def get(self, operation_id: str) -> OperationRecord | None:
        with self._lock:
            return self._cache.get(operation_id)

    def list_recent(self, *, limit: int = 50) -> list[OperationRecord]:
        with self._lock:
            values = sorted(self._cache.values(), key=lambda item: item.updated_at, reverse=True)
            return values[: max(1, min(500, limit))]

    def record_autonomous_cycle(
        self,
        *,
        tasks: list[dict[str, Any]],
        results: list[dict[str, Any]],
        decision: str = "",
        skip_reason: str = "",
        no_action_reason: str = "",
        candidates: list[str] | None = None,
        decision_axes: dict[str, Any] | None = None,
        timestamp_ms: int | None = None,
    ) -> OperationRecord:
        ts = int(timestamp_ms or _now_ms())
        steps: list[dict[str, Any]] = []
        targets: list[str] = []
        narratives: list[str] = []
        changed: list[str] = []
        linked_tasks: list[str] = []
        linked_caps: list[str] = []
        any_failed = False
        any_approval = False

        for index, task in enumerate(tasks or []):
            result = results[index] if index < len(results or []) else {}
            cap = str(task.get("capability_id") or "")
            done = str(task.get("what_was_done") or task.get("action") or cap)
            out = str(result.get("result_summary") or result.get("result") or "")
            state = str(task.get("changed_state") or result.get("changed_state") or "")
            success = bool(result.get("success", True)) if result else False
            if not success or str(out).lower().startswith("failed"):
                any_failed = True
            if "awaiting approval" in out.lower() or "approval" in str(result.get("status") or "").lower():
                any_approval = True
            if cap:
                linked_caps.append(cap)
                server = cap.split(".", 1)[0]
                if server and server not in targets:
                    targets.append(server.replace("-server", "").upper() if server.endswith("-server") else server)
            task_id = str(task.get("task_id") or result.get("task_id") or "")
            if task_id:
                linked_tasks.append(task_id)
            line = out or done
            if line:
                narratives.append(line)
            if state:
                changed.append(state)
            steps.append(
                {
                    "action": done,
                    "target": targets[-1] if targets else "",
                    "capability_id": cap,
                    "input_summary": json.dumps(task.get("arguments") or {}, ensure_ascii=False)[:180],
                    "output_summary": out[:280],
                    "changed_state": state[:200],
                    "status": "failed" if not success else ("awaiting_approval" if any_approval else "ok"),
                    "timestamp_ms": ts,
                    "summary": (out or done)[:220],
                    "narrative": (out or done)[:220],
                }
            )

        reason = (no_action_reason or skip_reason or decision or "").strip()
        if not steps and reason:
            action_summary = f"行動しなかった：{reason}"
            result_status = "non_action"
            result_summary = action_summary
            goal_status = "not_applicable"
            verification_status = "skipped"
        elif any_approval:
            action_summary = narratives[0] if narratives else "承認待ちの操作を開始"
            result_status = "awaiting_approval"
            result_summary = " / ".join(narratives[:3]) or action_summary
            goal_status = "in_progress"
            verification_status = "unknown"
        elif any_failed and narratives:
            action_summary = narratives[0]
            result_status = "partial" if any(s.get("status") == "ok" for s in steps) else "failed"
            result_summary = " / ".join(narratives[:3])
            goal_status = "unmet"
            verification_status = "failed"
        elif narratives:
            action_summary = narratives[0]
            result_status = "success"
            result_summary = " / ".join(narratives[:3])
            goal_status = "achieved"
            verification_status = "passed"
        else:
            action_summary = "観測したが具体的な操作記録がありません"
            result_status = "non_action"
            result_summary = action_summary
            goal_status = "not_applicable"
            verification_status = "skipped"

        purpose = str(decision or reason or action_summary)
        record = OperationRecord(
            operation_id=f"autonomous-cycle:{ts}",
            kind="autonomous",
            source="autonomous",
            started_at=ts,
            updated_at=ts,
            action_summary=action_summary[:280],
            target_summary=", ".join(targets[:4]),
            purpose=purpose[:280],
            decision_reason=reason[:280],
            result_summary=result_summary[:400],
            changed_state=" / ".join(changed[:4])[:280],
            verification_status=verification_status,
            goal_status=goal_status,
            result_status=result_status,
            next_action="" if result_status == "success" else (reason if result_status == "non_action" else "結果を確認して必要なら再試行"),
            wait_reason=reason if result_status in {"non_action", "awaiting_approval"} else "",
            linked_entity_ids={
                "task": linked_tasks[:12],
                "capability": linked_caps[:12],
            },
            trigger={"summary": "自律判断", "detail": purpose[:200]},
            perceived=[purpose] if purpose else [],
            candidates=list(candidates or [])[:12],
            goal=purpose[:200],
            steps=steps,
            verification={"summary": verification_status, "status": verification_status},
            follow_up={"summary": reason if result_status == "non_action" else ""},
            learning={"items": []},
        )
        if decision_axes:
            record.trigger["decision_axes"] = decision_axes
        return self.upsert(record)
