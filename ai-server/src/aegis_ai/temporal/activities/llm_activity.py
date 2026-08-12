"""LLM activity for Temporal workflows."""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger("aegis_ai.temporal.activities.llm")

_ACTIVITY_CONTEXT: dict[str, Any] = {}


def configure_llm_activity_context(**deps: Any) -> None:
    _ACTIVITY_CONTEXT.update(deps)


try:
    from temporalio import activity as _activity
except Exception:  # pragma: no cover
    _activity = None


def _llm_generate(payload: dict[str, Any]) -> dict[str, Any]:
    gateway = _ACTIVITY_CONTEXT.get("llm_gateway")
    if gateway is None:
        return {"success": False, "error": "llm_gateway unavailable"}
    prompt = str(payload.get("prompt") or "")
    system_prompt = str(payload.get("system_prompt") or "")
    profile = str(payload.get("profile") or "chat_balanced")
    try:
        if hasattr(gateway, "generate"):
            response = gateway.generate(prompt, system_prompt=system_prompt, profile=profile)
        else:
            response = gateway.route(prompt, profile=profile)
        return {
            "success": bool(getattr(response, "success", True)),
            "content": getattr(response, "content", str(response)),
            "error": getattr(response, "error", ""),
        }
    except Exception as exc:
        logger.warning("LLM activity failed: %s", exc)
        return {"success": False, "error": str(exc)}


if _activity is not None:

    @_activity.defn(name="llm_generate_activity")
    def llm_generate_activity(payload: dict[str, Any]) -> dict[str, Any]:
        return _llm_generate(payload)

else:

    def llm_generate_activity(payload: dict[str, Any]) -> dict[str, Any]:
        return _llm_generate(payload)
