"""User Model Store — persistent user preferences."""

from __future__ import annotations

import json
import logging
import time
from pathlib import Path
from typing import Any

from aegis_ai.user_model.user_model_types import (
    ApprovalStrictness,
    AutonomyLevel,
    DetailLevel,
    NotificationPreference,
    QuietHours,
    UserModel,
)

logger = logging.getLogger("aegis_ai.user_model.store")


class UserModelStore:
    """Persistent store for UserModel with JSON file storage."""

    def __init__(self, data_dir: str = "data/user_model") -> None:
        self._data_dir = Path(data_dir)
        self._data_dir.mkdir(parents=True, exist_ok=True)
        self._model: UserModel = UserModel()
        self._load()

    @property
    def model(self) -> UserModel:
        return self._model

    def get(self) -> UserModel:
        return self._model

    def update(self, patch: dict[str, Any], reason: str = "") -> None:
        now_ms = int(time.time() * 1000)
        if "detail_level" in patch:
            self._model.detail_level = DetailLevel(patch["detail_level"])
        if "autonomy_level" in patch:
            self._model.autonomy_level = AutonomyLevel(patch["autonomy_level"])
        if "notification_preference" in patch:
            self._model.notification_preference = NotificationPreference(patch["notification_preference"])
        if "approval_strictness" in patch:
            self._model.approval_strictness = ApprovalStrictness(patch["approval_strictness"])
        if "focus_mode" in patch:
            self._model.focus_mode = bool(patch["focus_mode"])
        if "preferred_language" in patch:
            self._model.preferred_language = patch["preferred_language"]
        if "preferred_tone" in patch:
            self._model.preferred_tone = patch["preferred_tone"]
        if "quiet_hours" in patch:
            qh = patch["quiet_hours"]
            if isinstance(qh, dict):
                self._model.quiet_hours = QuietHours(**qh)
        if "allowed_proactive_categories" in patch:
            self._model.allowed_proactive_categories = list(patch["allowed_proactive_categories"])
        if "disallowed_proactive_categories" in patch:
            self._model.disallowed_proactive_categories = list(patch["disallowed_proactive_categories"])
        for key in (
            "preferences",
            "work_patterns",
            "permission_scopes",
            "notification_conditions",
            "writing_style",
        ):
            if key in patch and isinstance(patch[key], dict):
                setattr(self._model, key, dict(patch[key]))
        if "common_apps" in patch:
            self._model.common_apps = list(patch["common_apps"])
        if "long_term_goals" in patch:
            self._model.long_term_goals = list(patch["long_term_goals"])
        if "trust_score" in patch:
            self._model.trust_score = max(0.0, min(1.0, float(patch["trust_score"])))
        if "annoyance_score" in patch:
            self._model.annoyance_score = max(0.0, min(1.0, float(patch["annoyance_score"])))
        self._model.updated_at = now_ms
        if reason:
            self._model.last_user_feedback = reason
        self._save()

    def record_interaction(self, feedback: str = "") -> None:
        self._model.last_interaction_at = int(time.time() * 1000)
        if feedback:
            self._model.last_user_feedback = feedback
        self._save()

    def adjust_trust(self, delta: float, reason: str = "") -> None:
        self._model.trust_score = max(0.0, min(1.0, self._model.trust_score + delta))
        self._model.updated_at = int(time.time() * 1000)
        self._save()

    def adjust_annoyance(self, delta: float, reason: str = "") -> None:
        self._model.annoyance_score = max(0.0, min(1.0, self._model.annoyance_score + delta))
        self._model.updated_at = int(time.time() * 1000)
        self._save()

    def record_user_feedback(self, feedback: str, confidence: float = 1.0) -> None:
        """Learn from user feedback. High confidence for explicit, low for inferred."""
        fb = feedback.lower()
        if "短く" in fb or "brief" in fb or "concise" in fb:
            self.update({"detail_level": "brief"}, reason=feedback)
        elif "詳しく" in fb or "detailed" in fb or "verbose" in fb:
            self.update({"detail_level": "detailed"}, reason=feedback)
        elif "勝手にやらないで" in fb or "stop" in fb or "don't do that" in fb:
            self.update({
                "autonomy_level": "low",
                "approval_strictness": "strict",
            }, reason=feedback)
        elif "もっと自動で" in fb or "automate" in fb or "do more" in fb:
            self.update({"autonomy_level": "high"}, reason=feedback)
        elif "うるさい" in fb or "noisy" in fb or "too many" in fb:
            self.update({"notification_preference": "minimal"}, reason=feedback)
        self._model.last_user_feedback = feedback
        self._model.last_interaction_at = int(time.time() * 1000)
        self._save()

    def to_context_string(self) -> str:
        m = self._model
        lines = [
            f"User preferences: lang={m.preferred_language}, tone={m.preferred_tone}",
            f"Detail: {m.detail_level.value}, Autonomy: {m.autonomy_level.value}",
            f"Notifications: {m.notification_preference.value}",
            f"Focus mode: {'on' if m.focus_mode else 'off'}",
        ]
        if m.common_apps:
            lines.append(f"Common apps: {', '.join(m.common_apps[:5])}")
        if m.long_term_goals:
            goals = [str(g.get("title") or g.get("goal") or g) for g in m.long_term_goals[:3]]
            lines.append(f"Long-term goals: {', '.join(goals)}")
        if m.quiet_hours.enabled:
            lines.append(f"Quiet hours: {m.quiet_hours.start_hour}:00-{m.quiet_hours.end_hour}:00")
        return "\n".join(lines)

    def relevant_context(self, query: str = "", situation: dict[str, Any] | None = None, limit: int = 8) -> list[str]:
        """Return a compact list of relevant user-model facts."""
        q = (query or "").lower()
        situation = situation or {}
        m = self._model
        facts = [
            f"language={m.preferred_language}",
            f"tone={m.preferred_tone}",
            f"detail_level={m.detail_level.value}",
            f"autonomy={m.autonomy_level.value}",
            f"notification_preference={m.notification_preference.value}",
        ]
        if situation.get("state"):
            facts.append(f"situation={situation.get('state')}, interruptibility={situation.get('interruptibility')}")
        for key, value in list(m.preferences.items())[:6]:
            if not q or key.lower() in q or str(value).lower() in q:
                facts.append(f"preference.{key}={value}")
        for app in m.common_apps[:6]:
            if not q or app.lower() in q:
                facts.append(f"common_app={app}")
        for goal in m.long_term_goals[:6]:
            title = str(goal.get("title") or goal.get("goal") or goal)
            if not q or title.lower() in q:
                facts.append(f"long_term_goal={title}")
        return facts[:limit]

    def _state_path(self) -> Path:
        return self._data_dir / "user_model.json"

    def _save(self) -> None:
        data = self._model.to_dict()
        data["last_user_feedback"] = self._model.last_user_feedback
        data["last_interaction_at"] = self._model.last_interaction_at
        data["preferred_report_format"] = self._model.preferred_report_format
        data["created_at"] = self._model.created_at
        data["updated_at"] = self._model.updated_at
        data["allowed_proactive_categories"] = self._model.allowed_proactive_categories
        data["disallowed_proactive_categories"] = self._model.disallowed_proactive_categories
        data["preferences"] = self._model.preferences
        data["work_patterns"] = self._model.work_patterns
        data["permission_scopes"] = self._model.permission_scopes
        data["common_apps"] = self._model.common_apps
        data["notification_conditions"] = self._model.notification_conditions
        data["writing_style"] = self._model.writing_style
        data["long_term_goals"] = self._model.long_term_goals
        try:
            with open(self._state_path(), "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as exc:
            logger.warning("Failed to save user model: %s", exc)

    def _load(self) -> None:
        path = self._state_path()
        if not path.exists():
            return
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
            self._model.user_id = data.get("user_id", "default")
            self._model.preferred_language = data.get("preferred_language", "ja")
            self._model.preferred_tone = data.get("preferred_tone", "polite")
            if "detail_level" in data:
                self._model.detail_level = DetailLevel(data["detail_level"])
            if "autonomy_level" in data:
                self._model.autonomy_level = AutonomyLevel(data["autonomy_level"])
            if "notification_preference" in data:
                self._model.notification_preference = NotificationPreference(data["notification_preference"])
            if "approval_strictness" in data:
                self._model.approval_strictness = ApprovalStrictness(data["approval_strictness"])
            if "quiet_hours" in data:
                self._model.quiet_hours = QuietHours(**data["quiet_hours"])
            self._model.focus_mode = data.get("focus_mode", False)
            self._model.trust_score = data.get("trust_score", 0.5)
            self._model.annoyance_score = data.get("annoyance_score", 0.0)
            self._model.last_interaction_at = data.get("last_interaction_at", 0)
            self._model.last_user_feedback = data.get("last_user_feedback", "")
            self._model.allowed_proactive_categories = data.get(
                "allowed_proactive_categories",
                self._model.allowed_proactive_categories,
            )
            self._model.disallowed_proactive_categories = data.get(
                "disallowed_proactive_categories", [],
            )
            self._model.preferences = data.get("preferences", {})
            self._model.work_patterns = data.get("work_patterns", {})
            self._model.permission_scopes = data.get("permission_scopes", {})
            self._model.common_apps = data.get("common_apps", [])
            self._model.notification_conditions = data.get("notification_conditions", {})
            self._model.writing_style = data.get("writing_style", {})
            self._model.long_term_goals = data.get("long_term_goals", [])
            self._model.created_at = data.get("created_at", 0)
            self._model.updated_at = data.get("updated_at", 0)
            logger.info("Loaded user model")
        except Exception as exc:
            logger.warning("Failed to load user model: %s", exc)
