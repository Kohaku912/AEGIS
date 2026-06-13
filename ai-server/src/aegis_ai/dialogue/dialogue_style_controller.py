"""Dialogue Style Controller — controls how AEGIS communicates with the user."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from aegis_ai.user_model.user_model_types import DetailLevel, UserModel

_SENSITIVE_PATTERNS = [
    (re.compile(r"(api[_-]?key|token|password|secret|cookie|auth)[=:]\s*\S+", re.IGNORECASE), r"\1=***"),
    (re.compile(r"Bearer\s+\S+", re.IGNORECASE), "Bearer ***"),
    (re.compile(r"sk-[a-zA-Z0-9]{20,}"), "sk-***"),
]


def _mask_text(text: str) -> str:
    for pat, repl in _SENSITIVE_PATTERNS:
        text = pat.sub(repl, text)
    return text


@dataclass
class SummaryDigest:
    digest_id: str = ""
    period: str = ""
    completed_tasks: int = 0
    failed_tasks: int = 0
    pending_approvals: int = 0
    important_warnings: list[str] = field(default_factory=list)
    self_development_results: list[str] = field(default_factory=list)
    desire_updates_summary: str = ""
    recommendations: list[str] = field(default_factory=list)
    created_at: int = 0

    def to_text(self) -> str:
        parts = [
            f"サマリー ({self.period}):",
            f"  完了: {self.completed_tasks}, 失敗: {self.failed_tasks}, 承認待ち: {self.pending_approvals}",
        ]
        if self.important_warnings:
            parts.append("  警告:")
            for w in self.important_warnings[:3]:
                parts.append(f"    - {w[:100]}")
        if self.recommendations:
            parts.append("  推奨:")
            for r in self.recommendations[:3]:
                parts.append(f"    - {r[:100]}")
        return "\n".join(parts)

    def to_dict(self) -> dict[str, Any]:
        return {
            "digest_id": self.digest_id,
            "period": self.period,
            "completed_tasks": self.completed_tasks,
            "failed_tasks": self.failed_tasks,
            "pending_approvals": self.pending_approvals,
            "important_warnings": self.important_warnings[:5],
            "recommendations": self.recommendations[:5],
            "created_at": self.created_at,
        }


class DialogueStyleController:
    """Controls how AEGIS communicates with the user."""

    def __init__(self, user_model: UserModel | None = None) -> None:
        self._user = user_model

    def set_user_model(self, model: UserModel) -> None:
        self._user = model

    def format_approval_request(
        self,
        what: str,
        why: str,
        impact: str,
        verification_method: str = "",
        cancel_consequence: str = "",
        ai_reason: str = "",
    ) -> str:
        parts = [
            f"承認が必要です: {what}",
            f"理由: {why}",
            f"影響: {impact}",
        ]
        if verification_method:
            parts.append(f"実行後の確認: {verification_method}")
        if cancel_consequence:
            parts.append(f"キャンセルした場合: {cancel_consequence}")
        if ai_reason:
            parts.append(f"AIの判断: {ai_reason}")
        return "\n".join(parts)

    def format_success(self, action: str, result_summary: str) -> str:
        detail = self._get_detail_level()
        if detail == DetailLevel.BRIEF:
            return f"完了: {action}"
        return f"完了: {action}\n結果: {_mask_text(result_summary[:200])}"

    def format_error(self, action: str, error: str, recovery: str = "") -> str:
        parts = [f"失敗: {action}", f"エラー: {_mask_text(error[:200])}"]
        if recovery:
            parts.append(f"復旧案: {recovery}")
        return "\n".join(parts)

    def format_safety_warning(self, warning: str) -> str:
        return f"⚠️ 安全警告: {warning}"

    def format_daily_summary(
        self,
        completed: int,
        failed: int,
        pending: int,
        highlights: list[str] | None = None,
    ) -> str:
        parts = [
            "日次サマリー:",
            f"  完了: {completed}, 失敗: {failed}, 承認待ち: {pending}",
        ]
        if highlights:
            for h in highlights[:3]:
                parts.append(f"  - {h[:100]}")
        return "\n".join(parts)

    def should_be_detailed(self) -> bool:
        return self._get_detail_level() == DetailLevel.DETAILED

    def should_be_brief(self) -> bool:
        return self._get_detail_level() == DetailLevel.BRIEF

    def _get_detail_level(self) -> DetailLevel:
        if self._user:
            return self._user.detail_level
        return DetailLevel.NORMAL
