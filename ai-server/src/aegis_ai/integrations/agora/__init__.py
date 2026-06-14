"""AGORA integration — safe AGORA chat client for AEGIS."""

from aegis_ai.integrations.agora.agora_bridge import (
    create_agora_post_approval,
    evaluate_agora_notification,
    record_agora_event,
    register_agora_capabilities,
    verify_agora_cursor,
    verify_agora_post,
)
from aegis_ai.integrations.agora.agora_client import AgoraClient
from aegis_ai.integrations.agora.agora_service import AgoraService, check_cooldown
from aegis_ai.integrations.agora.agora_types import (
    AgoraAccount,
    AgoraAuthor,
    AgoraCursor,
    AgoraFetchResult,
    AgoraPost,
    AgoraPostCreate,
    AgoraReplyDraft,
    AgoraTaskDetection,
)

__all__ = [
    "AgoraAccount",
    "AgoraAuthor",
    "AgoraClient",
    "AgoraCursor",
    "AgoraFetchResult",
    "AgoraPost",
    "AgoraPostCreate",
    "AgoraReplyDraft",
    "AgoraService",
    "AgoraTaskDetection",
    "check_cooldown",
    "create_agora_post_approval",
    "evaluate_agora_notification",
    "record_agora_event",
    "register_agora_capabilities",
    "verify_agora_cursor",
    "verify_agora_post",
]
