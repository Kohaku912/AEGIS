"""AGORA integration bridge — wires AGORA into ToolRegistry, ApprovalQueue, Verification, Memory, InteractionPolicy."""

from __future__ import annotations

import logging
from typing import Any

from aegis_ai.integrations.agora.agora_poller import AgoraPoller
from aegis_ai.integrations.agora.agora_service import AgoraService
from aegis_ai.integrations.agora.agora_types import AgoraPost

logger = logging.getLogger("aegis_ai.integrations.agora.bridge")


def register_agora_capabilities(registry: Any) -> list[str]:
    from aegis_schema.models import Capability, RiskLevel, ServerType

    caps = [
        Capability(
            id="ai.agora.get_me", name="AGORA Get Me",
            description="Get own AGORA account info",
            server_type=ServerType.AI, risk_level=RiskLevel.READ_ONLY,
            tags=["agora", "read"],
        ),
        Capability(
            id="ai.agora.read_posts", name="AGORA Read Posts",
            description="Read recent AGORA posts",
            server_type=ServerType.AI, risk_level=RiskLevel.READ_ONLY,
            tags=["agora", "read"],
        ),
        Capability(
            id="ai.agora.read_thread_posts", name="AGORA Read Thread Posts",
            description="Read posts in a specific thread",
            server_type=ServerType.AI, risk_level=RiskLevel.READ_ONLY,
            tags=["agora", "read"],
        ),
        Capability(
            id="ai.agora.read_mentions", name="AGORA Read Mentions",
            description="Read mentions of own account",
            server_type=ServerType.AI, risk_level=RiskLevel.READ_ONLY,
            tags=["agora", "read"],
        ),
        Capability(
            id="ai.agora.get_cursor", name="AGORA Get Cursor",
            description="Get last read cursor position",
            server_type=ServerType.AI, risk_level=RiskLevel.READ_ONLY,
            tags=["agora", "read"],
        ),
        Capability(
            id="ai.agora.update_cursor", name="AGORA Update Cursor",
            description="Update last read cursor position",
            server_type=ServerType.AI, risk_level=RiskLevel.SAFE_ACTION,
            tags=["agora", "write"],
        ),
        Capability(
            id="ai.agora.draft_reply", name="AGORA Draft Reply",
            description="Draft a reply to an AGORA post",
            server_type=ServerType.AI, risk_level=RiskLevel.READ_ONLY,
            tags=["agora", "draft"],
        ),
        Capability(
            id="ai.agora.create_post", name="AGORA Create Post",
            description="Create a post in AGORA (external send)",
            server_type=ServerType.AI, risk_level=RiskLevel.APPROVAL_REQUIRED,
            tags=["agora", "send"],
        ),
    ]
    registered = []
    for cap in caps:
        registry.register_capability(cap)
        registered.append(cap.id)
    return registered


def create_agora_post_approval(
    approval_queue: Any,
    thread_id: int,
    body: str,
    reply_to: int | None,
    source: str = "user_explicit",
    source_desire: str = "",
    frustration: float = 0.0,
) -> Any:
    from aegis_ai.approval.approval_types import ApprovalRequest, _mask_value

    body_preview = body[:200] + "..." if len(body) > 200 else body
    body_preview = _mask_value("body", body_preview)
    req = ApprovalRequest(
        capability_id="agora.create_post",
        tool_name="AGORA Create Post",
        arguments={"thread_id": thread_id, "body": body, "reply_to": reply_to},
        arguments_summary=f"thread={thread_id}, reply_to={reply_to}",
        risk_level="high",
        policy_decision="ASK_APPROVAL",
        approval_reason="AGORAへの投稿は外部チャットへの送信です。承認が必要です。",
        user_facing_summary=(
            f"AGORAスレッド{thread_id}に投稿しようとしています。\n"
            f"これは外部チャットへの送信なので承認が必要です。\n"
            f"投稿内容: {body_preview}\n"
            f"承認すると実際に公開されます。"
        ),
        expected_outcome="AGORAに投稿が公開されます。",
        possible_side_effects="投稿は削除APIがないため、消せない可能性があります。",
        source=source,
        source_desire=source_desire,
        frustration=frustration,
    )
    return approval_queue.submit(req)


def verify_agora_post(
    service: AgoraService,
    expected_body: str,
    expected_thread_id: int,
    post_id: int,
) -> dict[str, Any]:
    result = service.read_posts(since_id=post_id - 1, limit=5)
    if isinstance(result, dict) and "error" in result:
        return {"verified": False, "error": result.get("message", "Read failed.")}

    for post in result.posts:
        if post.id == post_id:
            body_match = post.body.strip() == expected_body.strip()
            thread_match = post.thread_id == expected_thread_id
            return {
                "verified": body_match and thread_match,
                "post_id": post_id,
                "body_match": body_match,
                "thread_match": thread_match,
                "author": post.author.name,
                "created_at": post.created_at,
            }
    return {"verified": False, "error": f"Post {post_id} not found."}


def verify_agora_cursor(
    service: AgoraService,
    expected_cursor: int,
) -> dict[str, Any]:
    result = service.get_cursor()
    if isinstance(result, dict) and "error" in result:
        return {"verified": False, "error": result.get("message", "Cursor read failed.")}
    match = result.last_read_post_id == expected_cursor
    return {
        "verified": match,
        "expected": expected_cursor,
        "actual": result.last_read_post_id,
    }


def record_agora_event(
    memory_store: Any,
    event_type: str,
    post: AgoraPost | None = None,
    details: dict[str, Any] | None = None,
) -> None:
    if memory_store is None:
        return
    try:
        from aegis_ai.memory.memory_types import MemoryRecord

        content_parts = [f"AGORA event: {event_type}"]
        if post:
            content_parts.append(f"post_id={post.id}, author={post.author.name}")
            content_parts.append(f"body={post.body[:100]}")
        if details:
            for k, v in details.items():
                if k not in ("token", "password", "secret", "api_key"):
                    content_parts.append(f"{k}={v}")

        record = MemoryRecord(
            content=" | ".join(content_parts),
            title=f"AGORA: {event_type}",
            memory_type="observation",
            source="agora_integration",
            importance=0.5,
        )
        memory_store.add(record)
    except Exception as exc:
        logger.warning("Failed to record AGORA event: %s", exc)


def evaluate_agora_notification(
    interaction_policy: Any,
    category: str,
    post: AgoraPost | None = None,
    is_mention: bool = False,
    is_task_request: bool = False,
    user_model: Any = None,
) -> Any:
    from aegis_ai.dialogue.interaction_policy import InteractionContext

    urgency = "normal"
    if is_mention:
        urgency = "high"
    if is_task_request:
        urgency = "high"

    ctx = InteractionContext(
        user_model=user_model,
        category=category,
        urgency=urgency,
        is_approval_required=(category == "approval_required"),
    )
    return interaction_policy.evaluate(ctx)


def agora_poll_and_integrate(
    poller: AgoraPoller,
    world_state_store: Any = None,
    memory_store: Any = None,
    interaction_policy: Any = None,
    user_model: Any = None,
    dry_run: bool = False,
) -> dict[str, Any]:
    result = poller.poll_once(dry_run=dry_run)
    if not result.success:
        return {"success": False, "error": result.error}

    if world_state_store:
        world_state_store.update_from_agora_poll(result)
        world_state_store.update_agora_account(
            poller.state.me.id, poller.state.me.name,
        )

    notifications: list[dict[str, Any]] = []
    if result.mentions and memory_store:
        for post in result.mentions:
            record_agora_event(memory_store, "mention_received", post=post)

    if result.tasks and interaction_policy:
        for task in result.tasks:
            if task.is_task_request:
                decision = evaluate_agora_notification(
                    interaction_policy,
                    category="approval_required",
                    post=None,
                    is_mention=True,
                    is_task_request=True,
                    user_model=user_model,
                )
                dec_val = decision.decision
                dec_str = dec_val.value if hasattr(dec_val, "value") else str(dec_val)
                notifications.append({
                    "task_title": task.task_title,
                    "urgency": task.urgency,
                    "decision": dec_str,
                })

    if memory_store and result.new_posts > 0:
        record_agora_event(
            memory_store, "poll_completed",
            details={"new_posts": result.new_posts, "tasks": result.tasks_detected},
        )

    return {
        "success": True,
        "new_posts": result.new_posts,
        "new_mentions": result.new_mentions,
        "tasks_detected": result.tasks_detected,
        "notifications": notifications,
        "summary": result.summary,
    }
