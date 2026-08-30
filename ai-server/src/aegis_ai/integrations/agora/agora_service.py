"""AGORA service — high-level AGORA operations with safety integration."""

from __future__ import annotations

import json
import logging
import re
import time
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any

from aegis_ai.integrations.agora.agora_client import AgoraClient
from aegis_ai.integrations.agora.agora_types import (
    AgoraAccount,
    AgoraCursor,
    AgoraFetchResult,
    AgoraPost,
    AgoraReplyDraft,
    AgoraTaskDetection,
)
from aegis_ai.llm.json_utils import extract_json_object

logger = logging.getLogger("aegis_ai.integrations.agora.service")

_SECRET_PATTERN = re.compile(
    r"(api[_-]?key|token|password|secret|cookie|bearer|sk-[a-zA-Z0-9]{20,})",
    re.IGNORECASE,
)

_COOLDOWN_SECONDS = 60
_MAX_REPLIED_TO = 200
_MAX_RECENT_BODIES = 40
_NEAR_DUPLICATE_RATIO = 0.88
_BODY_SNIPPET_CHARS = 180


def _has_secret(text: str) -> bool:
    return bool(_SECRET_PATTERN.search(text))


def normalize_post_body(text: str) -> str:
    """Collapse whitespace for duplicate comparison (not keyword matching)."""
    return " ".join(str(text or "").split()).casefold()


def bodies_are_near_duplicates(left: str, right: str, *, threshold: float = _NEAR_DUPLICATE_RATIO) -> bool:
    """True when two bodies are exact or near-paraphrase duplicates."""
    a = normalize_post_body(left)
    b = normalize_post_body(right)
    if not a or not b:
        return False
    if a == b:
        return True
    return SequenceMatcher(None, a, b).ratio() >= threshold

class AgoraService:
    """High-level AGORA operations with safety checks."""

    def __init__(
        self,
        client: AgoraClient | None = None,
        *,
        data_dir: str | Path | None = None,
        llm: Any = None,
    ) -> None:
        self._client = client or AgoraClient()
        self._llm = llm
        base = Path(data_dir) if data_dir else Path("data/social")
        self._guard_path = base / "agora_post_guard.json"
        self._guard_path.parent.mkdir(parents=True, exist_ok=True)
        self._guard = self._load_guard()

    def set_llm(self, llm: Any) -> None:
        self._llm = llm

    def set_data_dir(self, data_dir: str | Path) -> None:
        self._guard_path = Path(data_dir) / "agora_post_guard.json"
        self._guard_path.parent.mkdir(parents=True, exist_ok=True)
        self._guard = self._load_guard()

    @property
    def client(self) -> AgoraClient:
        return self._client

    @property
    def is_configured(self) -> bool:
        return self._client.is_configured

    def get_me(self) -> AgoraAccount | dict[str, Any]:
        return self._client.get_me()

    def read_posts(self, since_id: int = 0, limit: int = 50) -> AgoraFetchResult | dict[str, Any]:
        return self._client.list_posts(since_id=since_id, limit=limit)

    def read_thread_posts(
        self, thread_id: int = 1, since_id: int = 0, limit: int = 50,
    ) -> AgoraFetchResult | dict[str, Any]:
        return self._client.list_thread_posts(thread_id=thread_id, since_id=since_id, limit=limit)

    def read_mentions(self, since_id: int = 0, limit: int = 50) -> AgoraFetchResult | dict[str, Any]:
        return self._client.get_mentions(since_id=since_id, limit=limit)

    def get_cursor(self) -> AgoraCursor | dict[str, Any]:
        return self._client.get_cursor()

    def update_cursor(self, last_read_post_id: int) -> AgoraCursor | dict[str, Any]:
        return self._client.update_cursor(last_read_post_id=last_read_post_id)

    def evaluate_social_suitability(
        self,
        body: str,
        *,
        reply_to: int | None = None,
    ) -> dict[str, Any]:
        """LLM judgment: is this suitable as a public AGORA social post?

        Fail-closed when LLM is unavailable. Does not use keyword denylists.
        """
        if self._llm is None:
            return {
                "suitable": False,
                "reason": "Social suitability gate unavailable (no LLM); posting blocked.",
                "category": "gate_unavailable",
            }

        recent_bodies = list(self._guard.get("recent_bodies") or [])[-5:]
        replied_to = list(self._guard.get("replied_to_ids") or [])[-20:]
        prompt = f"""Judge whether this draft is suitable as a public AGORA social post
between humans (and AEGIS as a social participant).

Return JSON only:
{{"suitable": true, "reason": "...", "category": "social_reply|cold_open|unsuitable_internal|unsuitable_test|unsuitable_duplicate|unsuitable_meta|other"}}

Rules (reason from meaning, not keywords):
- suitable: genuine social reciprocity, helpful reply to someone, or a grounded public update a human would welcome
- unsuitable: internal system/ops status, incident/timeout/permission reports, approval-request meta about AEGIS itself,
  meaningless test/probe content, or near-duplicate of a recent AEGIS post on the same topic/reply_to
- Do not classify by capability id. Judge body + context only.

Draft body:
{body}

reply_to: {reply_to!s}
Recent AEGIS post bodies (for duplicate awareness):
{json.dumps(recent_bodies, ensure_ascii=False)}
Recent reply_to ids already answered by AEGIS:
{json.dumps(replied_to, ensure_ascii=False)}
"""
        try:
            if hasattr(self._llm, "generate"):
                response = self._llm.generate(
                    prompt=prompt,
                    system_prompt=(
                        "You are AEGIS's AGORA social suitability judge. "
                        "Prefer blocking internal/test/meta posts over letting them through. "
                        "Output JSON only."
                    ),
                    max_tokens=400,
                    json_mode=True,
                )
                if not getattr(response, "success", False):
                    return {
                        "suitable": False,
                        "reason": f"Suitability LLM failed: {getattr(response, 'error', 'unknown')}",
                        "category": "gate_unavailable",
                    }
                content = getattr(response, "content", "") or ""
            else:
                return {
                    "suitable": False,
                    "reason": "Social suitability gate unavailable (LLM has no generate).",
                    "category": "gate_unavailable",
                }
            data = extract_json_object(content)
            suitable = bool(data.get("suitable"))
            return {
                "suitable": suitable,
                "reason": str(data.get("reason") or ("suitable" if suitable else "unsuitable"))[:500],
                "category": str(data.get("category") or ("other" if suitable else "unsuitable")),
            }
        except Exception as exc:
            logger.warning("AGORA suitability evaluation failed: %s", exc)
            return {
                "suitable": False,
                "reason": f"Suitability evaluation error: {exc}",
                "category": "gate_unavailable",
            }

    def create_post(
        self,
        thread_id: int = 1,
        body: str = "",
        reply_to: int | None = None,
        *,
        already_approved: bool = False,
        skip_suitability: bool = False,
    ) -> AgoraPost | dict[str, Any]:
        if _has_secret(body):
            return {"error": "blocked", "message": "Post body contains potential secrets. Posting denied."}

        if not body.strip():
            return {"error": "blocked", "message": "Post body is empty."}

        structural = self._structural_block(body=body, reply_to=reply_to)
        if structural is not None:
            return structural

        run_suitability = not already_approved and not skip_suitability
        if run_suitability:
            judgment = self.evaluate_social_suitability(body, reply_to=reply_to)
            if not judgment.get("suitable"):
                return {
                    "error": "blocked",
                    "message": (
                        "Post blocked by social suitability gate: "
                        f"{judgment.get('reason')}"
                    ),
                    "suitability": judgment,
                }

        result = self._client.create_post(thread_id=thread_id, body=body, reply_to=reply_to)
        if isinstance(result, AgoraPost):
            self._record_successful_post(body=body, reply_to=reply_to)
        return result

    def draft_reply(self, target_post: AgoraPost, context: str = "") -> AgoraReplyDraft:
        return AgoraReplyDraft(
            reply_body=f"[Draft reply to #{target_post.id}] {context}",
            reply_to=target_post.id,
            reason=f"Reply to {target_post.author.name}: {target_post.body[:50]}",
            risk_level="low",
            requires_approval=True,
        )

    def detect_task(self, post: AgoraPost, my_account_id: int = 0) -> AgoraTaskDetection:
        """Return transport facts only; SocialManager performs LLM triage."""
        if post.author.id == my_account_id:
            return AgoraTaskDetection(is_task_request=False, reason="Own post.")
        return AgoraTaskDetection(
            is_task_request=False,
            requires_reply=False,
            reply_to=post.id,
            confidence=0.0,
            reason="Pending LLM triage in SocialManager.",
        )

    def has_replied_to(self, reply_to: int | None) -> bool:
        if reply_to is None:
            return False
        replied = {int(x) for x in (self._guard.get("replied_to_ids") or []) if str(x).isdigit() or isinstance(x, int)}
        return int(reply_to) in replied

    def post_avoidance_context(self, *, body_limit: int = 8, reply_limit: int = 40) -> dict[str, Any]:
        """Facts the draft LLM should see before inventing another AGORA message."""
        recent_bodies = [str(b).strip() for b in (self._guard.get("recent_bodies") or []) if str(b).strip()]
        replied = [
            int(x)
            for x in (self._guard.get("replied_to_ids") or [])
            if str(x).lstrip("-").isdigit() or isinstance(x, int)
        ]
        snippets = [body[:_BODY_SNIPPET_CHARS] for body in recent_bodies[-max(1, body_limit):]]
        return {
            "replied_to_ids": replied[-max(1, reply_limit):],
            "recent_bodies": snippets,
            "guidance": (
                "Do not reply_to any id in replied_to_ids. "
                "Do not draft a body that restates or paraphrases recent_bodies; "
                "write a fresh message only when there is new substance, otherwise skip posting."
            ),
        }

    def matches_recent_body(self, body: str) -> bool:
        """True when body is exact or near-duplicate of a recent AEGIS post."""
        candidate = str(body or "").strip()
        if not candidate:
            return False
        recent_bodies = [str(b).strip() for b in (self._guard.get("recent_bodies") or []) if str(b).strip()]
        last_body = str(self._guard.get("last_post_body") or "").strip()
        if last_body:
            recent_bodies = [*recent_bodies, last_body]
        return any(bodies_are_near_duplicates(candidate, prior) for prior in recent_bodies)

    def _structural_block(self, *, body: str, reply_to: int | None) -> dict[str, Any] | None:
        now = time.time()
        last_time = float(self._guard.get("last_post_time") or 0.0)
        if now - last_time < _COOLDOWN_SECONDS:
            remaining = int(_COOLDOWN_SECONDS - (now - last_time))
            return {"error": "cooldown", "message": f"Post cooldown active. Wait {remaining}s."}

        if self.matches_recent_body(body):
            return {
                "error": "duplicate",
                "message": "Near-duplicate of a recent AEGIS post body. Posting denied.",
            }

        if reply_to is not None and self.has_replied_to(int(reply_to)):
            return {
                "error": "duplicate_reply",
                "message": f"AEGIS already replied to post #{int(reply_to)}. Posting denied.",
            }
        return None

    def _record_successful_post(self, *, body: str, reply_to: int | None) -> None:
        now = time.time()
        self._guard["last_post_time"] = now
        self._guard["last_post_body"] = body
        recent = list(self._guard.get("recent_bodies") or [])
        recent.append(body.strip())
        self._guard["recent_bodies"] = recent[-_MAX_RECENT_BODIES:]
        if reply_to is not None:
            replied = [int(x) for x in (self._guard.get("replied_to_ids") or []) if str(x).lstrip("-").isdigit()]
            rid = int(reply_to)
            if rid not in replied:
                replied.append(rid)
            self._guard["replied_to_ids"] = replied[-_MAX_REPLIED_TO:]
        self._save_guard()

    def _load_guard(self) -> dict[str, Any]:
        if not self._guard_path.exists():
            return {
                "last_post_time": 0.0,
                "last_post_body": "",
                "recent_bodies": [],
                "replied_to_ids": [],
            }
        try:
            data = json.loads(self._guard_path.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                return data
        except Exception as exc:
            logger.warning("Failed to load AGORA post guard state: %s", exc)
        return {
            "last_post_time": 0.0,
            "last_post_body": "",
            "recent_bodies": [],
            "replied_to_ids": [],
        }

    def _save_guard(self) -> None:
        try:
            self._guard_path.write_text(
                json.dumps(self._guard, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )
        except Exception as exc:
            logger.warning("Failed to save AGORA post guard state: %s", exc)


def check_cooldown(data_dir: str | Path | None = None) -> dict[str, Any]:
    service = AgoraService(data_dir=data_dir)
    now = time.time()
    last_time = float(service._guard.get("last_post_time") or 0.0)
    remaining = max(0, _COOLDOWN_SECONDS - (now - last_time))
    return {"cooldown_active": remaining > 0, "remaining_seconds": int(remaining)}
