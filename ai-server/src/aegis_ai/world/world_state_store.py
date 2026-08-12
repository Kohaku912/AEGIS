"""World State Store — persistent store for WorldState."""

from __future__ import annotations

import json
import logging
import time
import uuid
from pathlib import Path
from typing import Any

from aegis_ai.world.world_state_types import (
    TaskPhase,
    WorldState,
    WorldStateDiff,
    _mask_text,
)

logger = logging.getLogger("aegis_ai.world.world_state_store")


class WorldStateStore:
    """Persistent store for WorldState with JSON storage."""

    def __init__(self, data_dir: str = "data/world_state") -> None:
        self._data_dir = Path(data_dir)
        self._data_dir.mkdir(parents=True, exist_ok=True)
        self._state = WorldState(
            world_state_id=f"ws_{uuid.uuid4().hex[:10]}",
            created_at=int(time.time() * 1000),
            updated_at=int(time.time() * 1000),
            version=1,
        )
        self._load()

    @property
    def state(self) -> WorldState:
        return self._state

    def get_current_state(self) -> WorldState:
        return self._state

    def update_from_observation(self, observation: dict[str, Any]) -> None:
        target = observation.get("target", "")
        now = int(time.time() * 1000)

        if target == "browser":
            bs = self._state.browser_state
            bs.current_url = observation.get("current_url", bs.current_url)
            bs.page_title = observation.get("page_title", bs.page_title)
            if bs.current_url:
                from urllib.parse import urlparse
                parsed = urlparse(bs.current_url)
                bs.domain = parsed.netloc
            bs.visible_text_summary = _mask_text(
                observation.get("visible_text_summary", bs.visible_text_summary)[:500]
            )
            bs.dom_summary = _mask_text(observation.get("dom_summary", bs.dom_summary)[:500])
            bs.last_observation_id = observation.get("observation_id", "")
            bs.last_verified_at = now
            bs.confidence = 0.8 if observation.get("status") == "success" else 0.4
            if "login" in bs.visible_text_summary.lower() or "sign in" in bs.visible_text_summary.lower():
                bs.login_required = True
            if "captcha" in bs.visible_text_summary.lower() or "2fa" in bs.visible_text_summary.lower():
                bs.captcha_or_2fa_detected = True

        elif target == "pc":
            ps = self._state.pc_state
            ps.active_window_title = observation.get("active_window", ps.active_window_title)
            ps.active_process = observation.get("active_app", ps.active_process)
            ps.screenshot_summary = observation.get("screenshot_summary", ps.screenshot_summary)[:300]
            ps.visible_text_summary = _mask_text(
                observation.get("visible_text_summary", ps.visible_text_summary)[:500]
            )
            if observation.get("ui_tree"):
                ps.ui_tree_summary = str(observation.get("ui_tree"))[:500]
            ps.last_observation_id = observation.get("observation_id", "")
            ps.last_verified_at = now
            ps.confidence = 0.8 if observation.get("status") == "success" else 0.4

        elif target == "android":
            ans = self._state.android_state
            ans.current_package = observation.get("active_app", ans.current_package)
            ans.visible_text_summary = _mask_text(
                observation.get("visible_text_summary", ans.visible_text_summary)[:500]
            )
            ans.ui_tree_summary = observation.get("ui_tree", ans.ui_tree_summary)[:500]
            ans.last_observation_id = observation.get("observation_id", "")
            ans.last_verified_at = now
            ans.confidence = 0.8 if observation.get("status") == "success" else 0.4

        self._bump_version()
        self._save()

    def update_from_tool_result(self, tool_request: Any, tool_result: Any) -> None:
        cap_id = getattr(tool_request, "capability_id", "")

        if cap_id.startswith("dev."):
            ds = self._state.dev_state
            ds.git_status_summary = str(
                getattr(tool_result, "output", {}).get("git_status", ds.git_status_summary)
            )[:300]
            ds.confidence = 0.7
            self._remove_stale("dev_state")

        self._bump_version()
        self._save()

    def update_from_verification(self, verification_result: Any) -> None:
        status = getattr(verification_result, "status", None)
        if status and hasattr(status, "value"):
            status_val = status.value
        else:
            status_val = str(status)

        if status_val == "verified":
            self._state.task_state.last_verification_result = "verified"
        elif status_val == "failed":
            self._state.task_state.last_verification_result = "failed"
            self._state.known_uncertainties.append(
                f"verification_failed: {getattr(verification_result, 'reason', '')[:100]}"
            )
        else:
            self._state.task_state.last_verification_result = status_val

        self._bump_version()
        self._save()

    def update_from_desire_snapshot(self, snapshot: Any) -> None:
        ds = self._state.desire_state
        ds.top_unsatisfied_desires = list(
            getattr(snapshot, "top_unsatisfied_desires", [])[:5]
        )
        ds.average_frustration = getattr(snapshot, "average_frustration", 0.0)
        ds.max_frustration = getattr(snapshot, "max_frustration", 0.0)
        self._bump_version()
        self._save()

    def update_approval_state(
        self,
        pending_count: int = 0,
        highest_risk: str = "",
        pending_summaries: list[str] | None = None,
        last_decision: str = "",
    ) -> None:
        ap = self._state.approval_state
        ap.pending_count = pending_count
        ap.highest_risk_pending = highest_risk
        ap.pending_summaries = pending_summaries or []
        if last_decision:
            ap.last_decision = last_decision
        self._bump_version()
        self._save()

    def update_task_state(
        self,
        task_id: str = "",
        source: str = "",
        status: str = "idle",
        blocked_reason: str = "",
    ) -> None:
        ts = self._state.task_state
        ts.active_task_id = task_id
        ts.active_task_source = source
        ts.blocked_reason = blocked_reason
        try:
            ts.status = TaskPhase(status)
        except (ValueError, KeyError):
            ts.status = TaskPhase.IDLE
        self._bump_version()
        self._save()

    def mark_stale(self, section: str, reason: str = "") -> None:
        self._state.mark_stale(section, reason)
        self._bump_version()
        self._save()

    def update_from_agora_poll(self, poll_result: Any) -> None:
        agora = self._state.agora_state
        now = int(time.time() * 1000)
        agora.last_observation_at = now
        agora.staleness = "fresh"
        if hasattr(poll_result, "posts"):
            for post in poll_result.posts[:5]:
                if post.id > agora.last_seen_post_id:
                    agora.last_seen_post_id = post.id
            agora.unread_count = getattr(poll_result, "new_posts", 0)
        if hasattr(poll_result, "summary"):
            agora.recent_posts_summary = poll_result.summary[:200]
        if hasattr(poll_result, "mentions"):
            agora.recent_mentions_summary = f"{len(poll_result.mentions)} mention(s)"
        if hasattr(poll_result, "tasks"):
            agora.pending_reply_candidates = [
                t.reply_to for t in poll_result.tasks if t.requires_reply
            ]
        self._bump_version()
        self._save()

    def update_agora_account(self, me_id: int, me_name: str) -> None:
        agora = self._state.agora_state
        agora.me_id = me_id
        agora.me_name = me_name
        agora.last_observation_at = int(time.time() * 1000)
        self._bump_version()
        self._save()

    def update_agora_cursor(self, cursor_id: int) -> None:
        agora = self._state.agora_state
        agora.last_cursor = cursor_id
        agora.last_observation_at = int(time.time() * 1000)
        self._bump_version()
        self._save()

    def expire_old_entries(self, now_ms: int | None = None) -> int:
        now = now_ms if now_ms is not None else int(time.time() * 1000)
        stale_count = 0

        if self._state.pc_state.last_verified_at > 0:
            age = (now - self._state.pc_state.last_verified_at) / 1000
            if age > 120:
                self._state.mark_stale("pc_state", f"last verified {age:.0f}s ago")
                stale_count += 1

        if self._state.browser_state.last_verified_at > 0:
            age = (now - self._state.browser_state.last_verified_at) / 1000
            if age > 180:
                self._state.mark_stale("browser_state", f"last verified {age:.0f}s ago")
                stale_count += 1

        if self._state.android_state.last_verified_at > 0:
            age = (now - self._state.android_state.last_verified_at) / 1000
            if age > 120:
                self._state.mark_stale("android_state", f"last verified {age:.0f}s ago")
                stale_count += 1

        if stale_count > 0:
            self._save()
        return stale_count

    def diff_states(self, before: WorldState, after: WorldState) -> WorldStateDiff:
        diff = WorldStateDiff(
            before_id=before.world_state_id,
            after_id=after.world_state_id,
        )
        if before.browser_state.current_url != after.browser_state.current_url:
            diff.browser_url_changed = True
            diff.changed_sections.append("browser_state")
        if before.pc_state.active_window_title != after.pc_state.active_window_title:
            diff.pc_window_changed = True
            diff.changed_sections.append("pc_state")
        if before.android_state.current_package != after.android_state.current_package:
            diff.android_app_changed = True
            diff.changed_sections.append("android_state")
        if before.dev_state.active_branch != after.dev_state.active_branch:
            diff.dev_branch_changed = True
            diff.changed_sections.append("dev_state")
        if before.task_state.status != after.task_state.status:
            diff.task_status_changed = True
            diff.changed_sections.append("task_state")
        if before.approval_state.pending_count != after.approval_state.pending_count:
            diff.approval_count_changed = True
            diff.changed_sections.append("approval_state")
        diff.changed_sections = list(set(diff.changed_sections))
        diff.changed = bool(diff.changed_sections)
        change_parts = []
        if diff.browser_url_changed:
            old_url = before.browser_state.current_url[:50]
            new_url = after.browser_state.current_url[:50]
            change_parts.append(f"url: {old_url} → {new_url}")
        if diff.pc_window_changed:
            change_parts.append("window changed")
        if diff.task_status_changed:
            change_parts.append(f"task: {before.task_state.status.value} → {after.task_state.status.value}")
        diff.summary = "; ".join(change_parts) if change_parts else "no changes"
        diff.confidence = 0.8 if diff.changed else 0.9
        return diff

    def summarize_for_context(self, max_chars: int = 1500) -> str:
        return self._state.to_context_string(max_chars)

    def _bump_version(self) -> None:
        self._state.version += 1
        self._state.updated_at = int(time.time() * 1000)

    def _remove_stale(self, section: str) -> None:
        if section in self._state.stale_sections:
            self._state.stale_sections.remove(section)

    def _state_path(self) -> Path:
        return self._data_dir / "world_state.json"

    def _save(self) -> None:
        try:
            with open(self._state_path(), "w", encoding="utf-8") as f:
                json.dump(self._state.to_dict(), f, ensure_ascii=False, indent=2)
        except Exception as exc:
            logger.warning("Failed to save world state: %s", exc)

    def _load(self) -> None:
        path = self._state_path()
        if not path.exists():
            return
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
            self._state.world_state_id = data.get("world_state_id", self._state.world_state_id)
            self._state.created_at = data.get("created_at", self._state.created_at)
            self._state.updated_at = data.get("updated_at", self._state.updated_at)
            self._state.version = data.get("version", 0)
            self._state.memory_state_summary = data.get("memory_state_summary", "")
            self._state.stale_sections = data.get("stale_sections", [])
            self._state.sensitivity_flags = data.get("sensitivity_flags", [])
            self._state.active_goals = data.get("active_goals", [])
            self._state.active_constraints = data.get("active_constraints", [])
            self._state.known_uncertainties = data.get("known_uncertainties", [])

            ts = data.get("task_state_raw", {})
            if ts:
                self._state.task_state.active_task_id = ts.get("active_task_id", "")
                self._state.task_state.active_task_source = ts.get("active_task_source", "")
                self._state.task_state.blocked_reason = ts.get("blocked_reason", "")
                try:
                    self._state.task_state.status = TaskPhase(ts.get("status", "idle"))
                except (ValueError, KeyError):
                    self._state.task_state.status = TaskPhase.IDLE

            aps = data.get("approval_state_raw", {})
            if aps:
                self._state.approval_state.pending_count = aps.get("pending_count", 0)
                self._state.approval_state.highest_risk_pending = aps.get("highest_risk_pending", "")
                self._state.approval_state.last_decision = aps.get("last_decision", "")

            ds = data.get("desire_state_raw", {})
            if ds:
                self._state.desire_state.top_unsatisfied_desires = ds.get("top_unsatisfied_desires", [])
                self._state.desire_state.average_frustration = ds.get("average_frustration", 0.0)
                self._state.desire_state.max_frustration = ds.get("max_frustration", 0.0)

            bs = data.get("browser_state_raw", {})
            if bs:
                self._state.browser_state.current_url = bs.get("current_url", "")
                self._state.browser_state.page_title = bs.get("page_title", "")
                self._state.browser_state.domain = bs.get("domain", "")
                self._state.browser_state.login_required = bs.get("login_required", False)
                self._state.browser_state.captcha_or_2fa_detected = bs.get("captcha_or_2fa_detected", False)
                self._state.browser_state.last_verified_at = bs.get("last_verified_at", 0)
                self._state.browser_state.confidence = bs.get("confidence", 0.0)

            ps = data.get("pc_state_raw", {})
            if ps:
                self._state.pc_state.active_window_title = ps.get("active_window_title", "")
                self._state.pc_state.active_process = ps.get("active_process", "")
                self._state.pc_state.last_verified_at = ps.get("last_verified_at", 0)
                self._state.pc_state.confidence = ps.get("confidence", 0.0)

            ans = data.get("android_state_raw", {})
            if ans:
                self._state.android_state.current_package = ans.get("current_package", "")
                self._state.android_state.current_activity = ans.get("current_activity", "")
                self._state.android_state.permission_dialog_detected = ans.get("permission_dialog_detected", False)
                self._state.android_state.last_verified_at = ans.get("last_verified_at", 0)
                self._state.android_state.confidence = ans.get("confidence", 0.0)

            dvs = data.get("dev_state_raw", {})
            if dvs:
                self._state.dev_state.active_repo = dvs.get("active_repo", "")
                self._state.dev_state.active_branch = dvs.get("active_branch", "")
                self._state.dev_state.sandbox_id = dvs.get("sandbox_id", "")
                self._state.dev_state.test_status = dvs.get("test_status", "")
                self._state.dev_state.lint_status = dvs.get("lint_status", "")
                self._state.dev_state.confidence = dvs.get("confidence", 0.0)

            logger.info("Loaded world state v%d", self._state.version)
        except Exception as exc:
            logger.warning("Failed to load world state: %s", exc)
