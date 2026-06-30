"""Unified social communication proxy."""

from __future__ import annotations

import os
import smtplib
import json
import uuid
from email.message import EmailMessage
from pathlib import Path
from typing import Any

from aegis_schema.models import Event, ServerType

from aegis_ai.integrations.webhook_sender import WebhookRequest, WebhookSender
from aegis_ai.personal_ai.storage import JsonStateFile, append_jsonl, now_ms


class SocialProxy:
    """Draft-first social proxy for webhook/email v1."""

    def __init__(self, data_dir: str = "data/personal_ai", event_manager: Any = None, audit_manager: Any = None) -> None:
        self._state = JsonStateFile(Path(data_dir) / "social_proxy.json", {"drafts": []})
        self._history = Path(data_dir) / "social_history.jsonl"
        self._event_manager = event_manager
        self._audit_manager = audit_manager
        self._webhook_sender = WebhookSender(audit_log=audit_manager)
        self._drafts: dict[str, dict[str, Any]] = {}
        self._load()

    def receive_event(self, channel: str, payload: dict[str, Any]) -> dict[str, Any]:
        event_payload = {"channel": channel, "payload": payload, "received_at": now_ms()}
        if self._event_manager is not None:
            try:
                self._event_manager.publish(Event(
                    event_id=f"evt_{uuid.uuid4().hex[:12]}",
                    event_type=f"social.{channel}.received",
                    source_server_type=ServerType.AI,
                    source_server_id="social_proxy",
                    timestamp_ms=now_ms(),
                    payload_json=json.dumps(event_payload, ensure_ascii=False),
                ))
            except Exception:
                pass
        return {"ok": True, **event_payload}

    def create_draft(self, channel: str, to: str = "", subject: str = "", body: str = "", payload: dict[str, Any] | None = None) -> dict[str, Any]:
        draft = {
            "draft_id": f"draft_{uuid.uuid4().hex[:10]}",
            "channel": channel,
            "to": to,
            "subject": subject,
            "body": body,
            "payload": payload or {},
            "status": "draft",
            "created_at": now_ms(),
            "updated_at": now_ms(),
        }
        self._drafts[draft["draft_id"]] = draft
        self._save()
        self._audit("social_draft_created", draft)
        return draft

    def list_drafts(self) -> list[dict[str, Any]]:
        return sorted(self._drafts.values(), key=lambda d: d.get("created_at", 0), reverse=True)

    def send_approved(self, draft_id: str) -> dict[str, Any]:
        draft = self._drafts.get(draft_id)
        if draft is None:
            return {"ok": False, "error": "Draft not found.", "code": "NOT_FOUND"}
        channel = draft.get("channel")
        if channel == "webhook":
            result = self._send_webhook(draft)
        elif channel == "email":
            result = self._send_email(draft)
        else:
            result = {"ok": False, "error": f"{channel} sending is not implemented in SocialProxy v1.", "code": "UNSUPPORTED_CHANNEL"}
        draft["status"] = "sent" if result.get("ok") else "failed"
        draft["updated_at"] = now_ms()
        draft["last_result"] = result
        self._save()
        append_jsonl(self._history, {"draft": draft, "result": result, "timestamp": now_ms()})
        self._audit("social_send_approved", {"draft_id": draft_id, "channel": channel, "result": result})
        return result

    def _send_webhook(self, draft: dict[str, Any]) -> dict[str, Any]:
        payload = dict(draft.get("payload") or {})
        if draft.get("body"):
            payload.setdefault("body", draft["body"])
        response = self._webhook_sender.send(WebhookRequest(url=str(draft.get("to") or ""), payload=payload))
        return {"ok": response.success, "status_code": response.status_code, "error": response.error, "attempts": response.attempts}

    def _send_email(self, draft: dict[str, Any]) -> dict[str, Any]:
        host = os.getenv("AEGIS_SMTP_HOST", "")
        port = int(os.getenv("AEGIS_SMTP_PORT", "587"))
        username = os.getenv("AEGIS_SMTP_USERNAME", "")
        password = os.getenv("AEGIS_SMTP_PASSWORD", "")
        sender = os.getenv("AEGIS_SMTP_FROM", username)
        if not host or not sender:
            return {"ok": False, "error": "SMTP is not configured.", "code": "SMTP_NOT_CONFIGURED"}
        msg = EmailMessage()
        msg["From"] = sender
        msg["To"] = str(draft.get("to") or "")
        msg["Subject"] = str(draft.get("subject") or "AEGIS")
        msg.set_content(str(draft.get("body") or ""))
        try:
            with smtplib.SMTP(host, port, timeout=20) as smtp:
                smtp.starttls()
                if username:
                    smtp.login(username, password)
                smtp.send_message(msg)
            return {"ok": True}
        except Exception as exc:
            return {"ok": False, "error": str(exc), "code": "SMTP_SEND_FAILED"}

    def _load(self) -> None:
        data = self._state.load()
        self._drafts = {str(d["draft_id"]): d for d in data.get("drafts", []) if isinstance(d, dict) and d.get("draft_id")}

    def _save(self) -> None:
        self._state.save({"drafts": list(self._drafts.values()), "updated_at": now_ms()})

    def _audit(self, action: str, detail: dict[str, Any]) -> None:
        if self._audit_manager is None:
            return
        try:
            self._audit_manager.log_decision(action=action, actor="social_proxy", decision="success", reason=action, detail=detail)
        except Exception:
            pass
