"""Hook engine for scheduled, interval, and event-based self calls."""

from __future__ import annotations

import threading
import time
import uuid
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from aegis_schema.models import Event, EventPriority, ServerType

from tool_broker import ExecutionSource, ToolExecutionRequest

from aegis_ai.personal_ai.storage import JsonStateFile, append_jsonl, now_ms


@dataclass
class Hook:
    hook_id: str
    name: str
    kind: str = "interval"  # interval | schedule | event
    capability_id: str = ""
    arguments: dict[str, Any] = field(default_factory=dict)
    condition: dict[str, Any] = field(default_factory=dict)
    interval_seconds: int = 60
    schedule_at_ms: int = 0
    event_type: str = ""
    cooldown_seconds: int = 300
    max_runs_per_hour: int = 12
    dedupe_key: str = ""
    backoff_seconds: int = 0
    max_backoff_seconds: int = 3600
    current_backoff_seconds: int = 0
    consecutive_failures: int = 0
    timeout_seconds: float = 30.0
    enabled: bool = True
    stopped_reason: str = ""
    last_dedupe_value: str = ""
    last_run_ms: int = 0
    last_match_ms: int = 0
    next_run_ms: int = 0
    run_timestamps: list[int] = field(default_factory=list)
    last_result: dict[str, Any] = field(default_factory=dict)
    last_error: str = ""
    created_at: int = 0
    updated_at: int = 0

    def to_dict(self) -> dict[str, Any]:
        return self.__dict__.copy()

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Hook":
        return cls(
            hook_id=str(data.get("hook_id") or f"hook_{uuid.uuid4().hex[:10]}"),
            name=str(data.get("name") or "Hook"),
            kind=str(data.get("kind") or "interval"),
            capability_id=str(data.get("capability_id") or ""),
            arguments=dict(data.get("arguments") or {}),
            condition=dict(data.get("condition") or {}),
            interval_seconds=int(data.get("interval_seconds") or 60),
            schedule_at_ms=int(data.get("schedule_at_ms") or 0),
            event_type=str(data.get("event_type") or ""),
            cooldown_seconds=int(data.get("cooldown_seconds") or 300),
            max_runs_per_hour=int(data.get("max_runs_per_hour") or 12),
            dedupe_key=str(data.get("dedupe_key") or ""),
            backoff_seconds=int(data.get("backoff_seconds") or 0),
            max_backoff_seconds=int(data.get("max_backoff_seconds") or 3600),
            current_backoff_seconds=int(data.get("current_backoff_seconds") or 0),
            consecutive_failures=int(data.get("consecutive_failures") or 0),
            timeout_seconds=float(data.get("timeout_seconds") or 30.0),
            enabled=bool(data.get("enabled", True)),
            stopped_reason=str(data.get("stopped_reason") or ""),
            last_dedupe_value=str(data.get("last_dedupe_value") or ""),
            last_run_ms=int(data.get("last_run_ms") or 0),
            last_match_ms=int(data.get("last_match_ms") or 0),
            next_run_ms=int(data.get("next_run_ms") or 0),
            run_timestamps=list(data.get("run_timestamps") or []),
            last_result=dict(data.get("last_result") or {}),
            last_error=str(data.get("last_error") or ""),
            created_at=int(data.get("created_at") or 0),
            updated_at=int(data.get("updated_at") or 0),
        )


class HookEngine:
    """Executes read-only observations and wakes AutonomousLoop only on matches."""

    def __init__(
        self,
        *,
        data_dir: str = "data/personal_ai",
        tool_broker: Any = None,
        capability_catalog: Any = None,
        event_manager: Any = None,
        audit_manager: Any = None,
        autonomous_loop_getter: Any = None,
        user_state_manager: Any = None,
        poll_interval_seconds: int = 10,
    ) -> None:
        self._state = JsonStateFile(Path(data_dir) / "hooks.json", {"hooks": []})
        self._history_path = Path(data_dir) / "hook_runs.jsonl"
        self._tool_broker = tool_broker
        self._catalog = capability_catalog
        self._event_manager = event_manager
        self._audit_manager = audit_manager
        self._autonomous_loop_getter = autonomous_loop_getter
        self._user_state_manager = user_state_manager
        self._poll_interval_seconds = max(1, poll_interval_seconds)
        self._hooks: dict[str, Hook] = {}
        self._last_values: dict[str, Any] = {}
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None
        self._load()
        if self._event_manager is not None:
            try:
                self._event_manager.subscribe(self.on_event)
            except Exception:
                pass

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._stop.clear()
        self._thread = threading.Thread(target=self._loop, name="aegis-hook-engine", daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2)

    def list_hooks(self) -> list[dict[str, Any]]:
        return [h.to_dict() for h in self._hooks.values()]

    def get_hook(self, hook_id: str) -> dict[str, Any] | None:
        hook = self._hooks.get(hook_id)
        return hook.to_dict() if hook else None

    def upsert_hook(self, patch: dict[str, Any]) -> dict[str, Any]:
        now = now_ms()
        hook_id = str(patch.get("hook_id") or f"hook_{uuid.uuid4().hex[:10]}")
        hook = self._hooks.get(hook_id)
        if hook is None:
            hook = Hook(hook_id=hook_id, name=str(patch.get("name") or "Hook"), created_at=now, updated_at=now)
            self._hooks[hook_id] = hook
        for key in (
            "name", "kind", "capability_id", "arguments", "condition", "interval_seconds",
            "schedule_at_ms", "event_type", "cooldown_seconds", "max_runs_per_hour",
            "dedupe_key", "backoff_seconds", "max_backoff_seconds", "timeout_seconds", "enabled",
        ):
            if key in patch:
                value = patch[key]
                if key in {"arguments", "condition"}:
                    value = dict(value or {})
                elif key == "enabled":
                    value = bool(value)
                elif key in {"interval_seconds", "schedule_at_ms", "cooldown_seconds", "max_runs_per_hour", "backoff_seconds", "max_backoff_seconds"}:
                    value = int(value or 0)
                elif key == "timeout_seconds":
                    value = float(value or 30.0)
                else:
                    value = str(value)
                setattr(hook, key, value)
        hook.updated_at = now
        if not hook.next_run_ms:
            hook.next_run_ms = now
        self._save()
        self._audit("hook_upserted", hook.to_dict())
        return hook.to_dict()

    def delete_hook(self, hook_id: str) -> bool:
        changed = self._hooks.pop(hook_id, None) is not None
        if changed:
            self._save()
            self._audit("hook_deleted", {"hook_id": hook_id})
        return changed

    def stop_hook(self, hook_id: str, reason: str = "stopped") -> dict[str, Any] | None:
        hook = self._hooks.get(hook_id)
        if hook is None:
            return None
        hook.enabled = False
        hook.stopped_reason = reason
        hook.updated_at = now_ms()
        self._save()
        self._audit("hook_stopped", {"hook_id": hook_id, "reason": reason})
        return hook.to_dict()

    def run_due_once(self) -> list[dict[str, Any]]:
        results = []
        now = now_ms()
        for hook in list(self._hooks.values()):
            if not hook.enabled or hook.kind == "event":
                continue
            if hook.kind == "schedule" and hook.schedule_at_ms and now < hook.schedule_at_ms:
                continue
            if hook.kind == "interval" and hook.next_run_ms and now < hook.next_run_ms:
                continue
            results.append(self._run_hook(hook, trigger_payload={"reason": "scheduled"}))
        return results

    def on_event(self, event: Event) -> None:
        event_type = getattr(event, "event_type", "")
        payload: Any = getattr(event, "payload", {}) or {}
        if not payload and getattr(event, "payload_json", ""):
            try:
                payload = json.loads(event.payload_json)
            except Exception:
                payload = {}
        for hook in list(self._hooks.values()):
            if not hook.enabled or hook.kind != "event":
                continue
            if hook.event_type and hook.event_type != event_type:
                continue
            self._run_hook(hook, trigger_payload={"event_type": event_type, "event": payload})

    def _loop(self) -> None:
        while not self._stop.wait(self._poll_interval_seconds):
            try:
                self.run_due_once()
            except Exception as exc:
                self._audit("hook_tick_failed", {"error": str(exc)})

    def _run_hook(self, hook: Hook, trigger_payload: dict[str, Any] | None = None) -> dict[str, Any]:
        now = now_ms()
        if now - hook.last_match_ms < hook.cooldown_seconds * 1000:
            return {"ok": False, "hook_id": hook.hook_id, "skipped": "cooldown"}
        hook.run_timestamps = [t for t in hook.run_timestamps if now - int(t) < 3_600_000]
        if len(hook.run_timestamps) >= max(1, hook.max_runs_per_hour):
            return {"ok": False, "hook_id": hook.hook_id, "skipped": "max_runs_per_hour"}
        if not self._capability_is_read_only(hook.capability_id):
            hook.last_error = "Hook capability must be read-only."
            self._save()
            return {"ok": False, "hook_id": hook.hook_id, "error": hook.last_error}

        hook.last_run_ms = now
        hook.run_timestamps.append(now)
        result_payload: dict[str, Any] = {}
        error = ""
        if hook.capability_id:
            request = ToolExecutionRequest(
                capability_id=hook.capability_id,
                arguments=hook.arguments,
                source=ExecutionSource.SCHEDULED,
                reason=f"Hook observation: {hook.name}",
                timeout_seconds=hook.timeout_seconds,
                origin_channel="hook_engine",
                metadata={"hook_id": hook.hook_id},
            )
            result = self._tool_broker.execute(request) if self._tool_broker is not None else None
            if result is None:
                error = "ToolBroker unavailable."
            elif result.success:
                result_payload = result.output
            else:
                error = result.error or result.status.value
        matched = False if error else self._condition_matches(hook, result_payload)
        dedupe_skipped = False
        if matched:
            if self._dedupe_allows(hook, result_payload):
                hook.last_match_ms = now
                self._emit_self_call(hook, result_payload, trigger_payload or {})
            else:
                matched = False
                dedupe_skipped = True
        if error:
            hook.consecutive_failures += 1
            base = max(1, hook.backoff_seconds or hook.interval_seconds)
            previous = hook.current_backoff_seconds or base
            hook.current_backoff_seconds = min(max(1, hook.max_backoff_seconds), max(base, previous * 2))
        else:
            hook.consecutive_failures = 0
            hook.current_backoff_seconds = 0
        hook.next_run_ms = now + max(1, hook.interval_seconds + hook.current_backoff_seconds) * 1000
        hook.last_result = result_payload
        hook.last_error = error
        self._save()
        entry = {
            "hook_id": hook.hook_id,
            "matched": matched,
            "dedupe_skipped": dedupe_skipped,
            "error": error,
            "backoff_seconds": hook.current_backoff_seconds,
            "result": result_payload,
            "timestamp": now,
        }
        append_jsonl(self._history_path, entry)
        self._audit("hook_run", entry)
        return {"ok": not bool(error), **entry}

    def _capability_is_read_only(self, capability_id: str) -> bool:
        if not capability_id or self._catalog is None:
            return False
        manifest = self._catalog.resolve(capability_id)
        if manifest is None:
            return False
        level = str(getattr(manifest, "risk_level", "") or "").lower()
        return level in {"low", "read_only", "read-only", "readonly"} and not bool(getattr(manifest, "requires_approval", False))

    def _condition_matches(self, hook: Hook, value: dict[str, Any]) -> bool:
        condition = hook.condition or {}
        if not condition:
            return False
        op = str(condition.get("op") or "exists")
        path = str(condition.get("path") or "")
        value_with_context = dict(value or {})
        if path.startswith("user_state.") and self._user_state_manager is not None:
            try:
                value_with_context["user_state"] = self._user_state_manager.get_current_user_state()
            except Exception:
                value_with_context["user_state"] = {}
        current = self._get_path(value_with_context, path)
        expected = condition.get("value")
        key = hook.dedupe_key or f"{hook.hook_id}:{path}"
        if op == "changed":
            previous = self._last_values.get(key)
            self._last_values[key] = current
            return previous is not None and previous != current
        if op == "exists":
            return current is not None
        if op == "eq":
            return current == expected
        if op == "ne":
            return current != expected
        if op == "contains":
            return str(expected) in str(current)
        try:
            cur = float(current)
            exp = float(expected)
            if op == "gt":
                return cur > exp
            if op == "lt":
                return cur < exp
        except Exception:
            return False
        return False

    def _dedupe_allows(self, hook: Hook, result_payload: dict[str, Any]) -> bool:
        if not hook.dedupe_key:
            return True
        raw_value = self._get_path(result_payload, hook.dedupe_key)
        if raw_value is None:
            raw_value = result_payload
        try:
            value = json.dumps(raw_value, ensure_ascii=False, sort_keys=True)
        except Exception:
            value = str(raw_value)
        if value == hook.last_dedupe_value:
            return False
        hook.last_dedupe_value = value
        return True

    @staticmethod
    def _get_path(value: Any, path: str) -> Any:
        cur = value
        for part in [p for p in path.split(".") if p]:
            if isinstance(cur, dict):
                cur = cur.get(part)
            elif isinstance(cur, list) and part.isdigit():
                cur = cur[int(part)]
            else:
                return None
        return cur

    def _emit_self_call(self, hook: Hook, result_payload: dict[str, Any], trigger_payload: dict[str, Any]) -> None:
        payload = {
            "hook_id": hook.hook_id,
            "hook_name": hook.name,
            "reason": f"Hook matched: {hook.name}",
            "result": result_payload,
            "trigger": trigger_payload,
        }
        if self._event_manager is not None:
            try:
                self._event_manager.publish(Event(
                    event_id=f"evt_{uuid.uuid4().hex[:12]}",
                    event_type="self_call",
                    source_server_type=ServerType.AI,
                    source_server_id="hook_engine",
                    timestamp_ms=now_ms(),
                    payload_json=json.dumps(payload, ensure_ascii=False),
                    priority=EventPriority.NORMAL,
                ))
            except Exception:
                pass
        loop = self._autonomous_loop_getter() if self._autonomous_loop_getter else None
        if loop is not None and hasattr(loop, "trigger"):
            loop.trigger(reason=payload["reason"], context=payload)
        elif loop is not None and hasattr(loop, "trigger_now"):
            loop.trigger_now()

    def _load(self) -> None:
        data = self._state.load()
        self._hooks = {h.hook_id: h for h in [Hook.from_dict(x) for x in data.get("hooks", []) if isinstance(x, dict)]}

    def _save(self) -> None:
        self._state.save({"hooks": [h.to_dict() for h in self._hooks.values()], "updated_at": now_ms()})

    def _audit(self, action: str, detail: dict[str, Any]) -> None:
        if self._audit_manager is None:
            return
        try:
            self._audit_manager.log_decision(action=action, actor="hook_engine", decision="success", reason=action, detail=detail)
        except Exception:
            pass
