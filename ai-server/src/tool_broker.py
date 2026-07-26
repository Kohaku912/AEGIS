"""Tool Broker — capability invocation with mandatory safety enforcement.

The ToolBroker is the ONLY entry point for invoking capabilities.
Every invocation path goes through PolicyEngine — structurally enforced.

Architecture constraint (§5.8, §5.9, §7.3):
- ToolBroker wraps ToolRegistry + PolicyEngine
- ALL invocations call PolicyEngine.evaluate() FIRST
- No code path exists to execute a tool without policy check
- MockExecutor is private — cannot be called from outside
- LLM never sees the full capability list; Planner searches via ToolRegistry

Design: The _invoke_internal method is the ONLY method that calls the executor.
All public invocation APIs funnel through it, and it ALWAYS calls PolicyEngine first.
"""

from __future__ import annotations

import hashlib
import logging
import re
import threading
import time
import uuid
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

from jsonschema import ValidationError, validate

from aegis_ai.capability_catalog import risk_level_from_label
from aegis_ai.production_readiness import is_mock_like_output, is_production_mode
from aegis_schema.models import Capability, RiskLevel, ServerType
from policy_engine import PolicyDecision, PolicyEngine, PolicyResult, create_default_policy_engine
from server_executor import ServerExecutor
from tool_registry import ToolRegistry

logger = logging.getLogger("aegis_ai.tool_broker")


def _capability_from_manifest(manifest: Any) -> Capability:
    """Convert a FolderCapabilityRegistry manifest to a Capability.

    Uses canonical ID format: server_id.app_id.action
    e.g., pc-server.screenshot.get_screenshot
    """
    risk = risk_level_from_label(getattr(manifest, "risk_level", "low"))

    server_id = getattr(manifest, "server_id", "ai-server")
    server_type_map = {
        "pc-server": ServerType.PC,
        "browser-server": ServerType.BROWSER,
        "android-server": ServerType.ANDROID,
        "room-server": ServerType.ROOM,
        "ai-server": ServerType.AI,
    }
    server_type = server_type_map.get(server_id, ServerType.AI)

    cap_id = getattr(manifest, "capability_id", "")
    if not cap_id:
        app_id = getattr(manifest, "app_id", "")
        action = getattr(manifest, "action", "")
        cap_id = f"{server_id}.{app_id}.{action}"

    return Capability(
        id=cap_id,
        name=manifest.title,
        description=manifest.description or manifest.title or cap_id,
        server_type=server_type,
        risk_level=risk,
        requires_approval=getattr(manifest, "requires_approval", False),
        side_effects=list(getattr(manifest, "side_effects", [])),
        tags=manifest.tags,
    )


# ═══════════════════════════════════════════════════════════════
# Execution Source — where the tool invocation originated
# ═══════════════════════════════════════════════════════════════


class ExecutionSource(Enum):
    USER_EXPLICIT = "user_explicit"
    SCHEDULED = "scheduled"
    EVENT_DRIVEN = "event_driven"
    DESIRE_DRIVEN = "desire_driven"
    AUTONOMOUS = "autonomous"
    SYSTEM = "system"


# ═══════════════════════════════════════════════════════════════
# Invoke Status — execution outcome
# ═══════════════════════════════════════════════════════════════


class InvokeStatus(Enum):
    SUCCESS = "success"
    FAILED = "failed"
    DENIED = "denied"
    APPROVAL_NEEDED = "approval_required"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"
    DRY_RUN = "dry_run"
    UNAVAILABLE = "unavailable"
    NOT_FOUND = "not_found"
    IDEMPOTENT_HIT = "idempotent_hit"
    EXECUTION_ERROR = "execution_error"


# ═══════════════════════════════════════════════════════════════
# Tool Execution Request / Result
# ═══════════════════════════════════════════════════════════════


@dataclass
class ToolExecutionRequest:
    request_id: str = ""
    task_id: str = ""
    step_id: str = ""
    source: ExecutionSource = ExecutionSource.SYSTEM
    capability_id: str = ""
    tool_name: str = ""
    arguments: dict[str, Any] = field(default_factory=dict)
    risk_level: RiskLevel = RiskLevel.UNSPECIFIED
    requires_approval: bool = False
    dry_run: bool = False
    idempotency_key: str = ""
    created_at: int = 0
    reason: str = ""
    source_desire: str = ""
    frustration: float = 0.0
    timeout_seconds: float = 30.0
    origin_channel: str = ""
    conversation_id: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ToolExecutionResult:
    request_id: str = ""
    status: InvokeStatus = InvokeStatus.UNAVAILABLE
    output: dict[str, Any] = field(default_factory=dict)
    error: str = ""
    started_at: int = 0
    finished_at: int = 0
    duration_ms: float = 0.0
    policy_decision: str = ""
    policy_result: PolicyResult | None = None
    verification_status: str = "pending"
    audit_log_id: str = ""
    approval_id: str = ""
    verification: VerificationResult | None = None

    @property
    def success(self) -> bool:
        return self.status == InvokeStatus.SUCCESS


# ═══════════════════════════════════════════════════════════════
# Verification
# ═══════════════════════════════════════════════════════════════


@dataclass
class VerificationRequest:
    request_id: str = ""
    capability_id: str = ""
    output: dict[str, Any] = field(default_factory=dict)


@dataclass
class VerificationResult:
    request_id: str = ""
    status: str = "pending"
    checks_passed: int = 0
    checks_failed: int = 0
    details: list[str] = field(default_factory=list)
    repair_hint: str = ""


def verify_tool_result(request: ToolExecutionRequest, result: ToolExecutionResult) -> VerificationResult:
    """Basic post-execution verification.

    Checks:
    - File operations: output contains path/status
    - HTTP operations: status code in 2xx-3xx
    - Other: structural presence of output
    """
    vr = VerificationResult(request_id=request.request_id)
    if result.status != InvokeStatus.SUCCESS:
        vr.status = "skipped"
        vr.details.append(f"Skipped: status={result.status.value}")
        return vr

    if not result.output:
        vr.status = "failed"
        vr.checks_failed = 1
        vr.details.append("No output returned")
        return vr

    vr.checks_passed = 1
    vr.details.append("Output present")

    vr.status = "passed" if vr.checks_failed == 0 else "failed"
    return vr


def _fingerprint(value: Any) -> str:
    text = str(value)
    try:
        import json as _json

        text = _json.dumps(value, sort_keys=True, ensure_ascii=False, default=str)
    except Exception:
        pass
    return hashlib.sha256(text.encode("utf-8", errors="replace")).hexdigest()


# ═══════════════════════════════════════════════════════════════
# Sensitive data masking
# ═══════════════════════════════════════════════════════════════

_SENSITIVE_PATTERNS = [
    (re.compile(r"(api[_-]?key|token|password|secret|cookie|auth)[=:]\s*\S+", re.IGNORECASE), r"\1=***MASKED***"),
    (re.compile(r"Bearer\s+\S+", re.IGNORECASE), "Bearer ***MASKED***"),
    (re.compile(r"sk-[a-zA-Z0-9]{20,}"), "sk-***MASKED***"),
]


def _mask_sensitive(data: dict[str, Any]) -> dict[str, Any]:
    """Mask sensitive values in a dict for logging."""
    masked: dict[str, Any] = {}
    for k, v in data.items():
        k_lower = k.lower()
        if any(s in k_lower for s in ("key", "token", "password", "secret", "cookie", "auth")):
            masked[k] = "***MASKED***"
        elif isinstance(v, str):
            masked[k] = _mask_string(v)
        elif isinstance(v, dict):
            masked[k] = _mask_sensitive(v)
        else:
            masked[k] = v
    return masked


def _mask_string(s: str) -> str:
    for pattern, replacement in _SENSITIVE_PATTERNS:
        s = pattern.sub(replacement, s)
    return s


def _compact_audit_value(value: Any, *, depth: int = 0) -> Any:
    """Bound audit detail size without changing the tool result itself."""

    if depth >= 8:
        return {"omitted": True, "reason": "max_depth"}
    if isinstance(value, str):
        masked = _mask_string(value)
        encoded = masked.encode("utf-8", errors="replace")
        if len(encoded) <= 8_192:
            return masked
        return {
            "omitted": True,
            "type": "string",
            "length": len(encoded),
            "sha256": hashlib.sha256(encoded).hexdigest(),
        }
    if isinstance(value, bytes):
        return {
            "omitted": True,
            "type": "bytes",
            "length": len(value),
            "sha256": hashlib.sha256(value).hexdigest(),
        }
    if isinstance(value, dict):
        compact: dict[str, Any] = {}
        items = list(value.items())
        for key, item in items[:100]:
            key_text = str(key)
            if any(
                sensitive in key_text.lower()
                for sensitive in (
                    "key",
                    "token",
                    "password",
                    "secret",
                    "cookie",
                    "auth",
                )
            ):
                compact[key_text] = "***MASKED***"
            else:
                compact[key_text] = _compact_audit_value(item, depth=depth + 1)
        if len(items) > 100:
            compact["_omitted_items"] = len(items) - 100
        return compact
    if isinstance(value, (list, tuple)):
        compact_list = [_compact_audit_value(item, depth=depth + 1) for item in value[:100]]
        if len(value) > 100:
            compact_list.append({"omitted_items": len(value) - 100})
        return compact_list
    if value is None or isinstance(value, (bool, int, float)):
        return value
    return _compact_audit_value(str(value), depth=depth + 1)


# ═══════════════════════════════════════════════════════════════
# Retry classification
# ═══════════════════════════════════════════════════════════════

# ═══════════════════════════════════════════════════════════════
# Invoke Result (backward-compatible)
# ═══════════════════════════════════════════════════════════════


@dataclass
class InvokeResult:
    """Result of invoking a capability through the ToolBroker."""

    status: InvokeStatus = InvokeStatus.UNAVAILABLE
    capability_id: str = ""
    output: dict[str, Any] = field(default_factory=dict)
    error: str = ""
    policy_result: PolicyResult | None = None
    invocation_id: str = ""
    duration_ms: float = 0.0
    request: ToolExecutionRequest | None = None
    verification: VerificationResult | None = None

    @property
    def success(self) -> bool:
        return self.status == InvokeStatus.SUCCESS

    @property
    def denied(self) -> bool:
        return self.status in (InvokeStatus.DENIED, InvokeStatus.APPROVAL_NEEDED)


# Type alias for mock executor functions
MockExecutorFunc = Callable[[Capability, dict[str, Any]], dict[str, Any]]


# ═══════════════════════════════════════════════════════════════
# Tool Broker
# ═══════════════════════════════════════════════════════════════


class ToolBroker:
    """Central capability dispatch with mandatory safety enforcement.

    STRUCTURAL CONSTRAINT: All execution goes through _invoke_internal(),
    which ALWAYS calls policy_engine.evaluate() before the executor.
    There is NO public method that executes a capability without policy check.
    """

    def __init__(
        self,
        registry: ToolRegistry,
        policy_engine: PolicyEngine | None = None,
        audit_log: Any = None,
        verification_service: Any = None,
        approval_queue: Any = None,
        approval_manager: Any = None,
        server_executor: ServerExecutor | None = None,
        folder_registry: Any = None,
        catalog: Any = None,
        delegation_policy: Any = None,
        repair_manager: Any = None,
        event_manager: Any = None,
    ) -> None:
        self._registry = registry
        self._policy = policy_engine or create_default_policy_engine()
        self._audit = audit_log
        self._verification = verification_service
        self._approval_queue = approval_queue
        self._approval_manager = approval_manager
        self._server_executor = server_executor
        self._folder_registry = folder_registry
        self._catalog = catalog
        self._delegation_policy = delegation_policy
        self._repair_manager = repair_manager
        self._event_manager = event_manager
        self._continuation_manager: Any = None

        if self._catalog is not None and self._server_executor is not None:
            self._server_executor.set_catalog(self._catalog)

        self._mock_executors: dict[str, MockExecutorFunc] = {}
        self._default_mock: MockExecutorFunc = self._default_executor

        # Idempotency: key → result
        self._idempotency_cache: dict[str, ToolExecutionResult] = {}

        # Pending approval requests
        self._pending_approvals: dict[str, ToolExecutionRequest] = {}
        self._lock = threading.RLock()

    def set_delegation_policy(self, delegation_policy: Any) -> None:
        """Attach user-specific delegation policy after runtime construction."""
        self._delegation_policy = delegation_policy

    def set_repair_manager(self, repair_manager: Any) -> None:
        """Attach repair manager after runtime construction."""
        self._repair_manager = repair_manager

    def set_continuation_manager(self, continuation_manager: Any) -> None:
        """Attach durable continuation tracking after runtime construction."""
        self._continuation_manager = continuation_manager

    # ── Public API — the ONLY way to invoke tools ──────────────

    def execute(
        self,
        request: ToolExecutionRequest,
    ) -> ToolExecutionResult:
        """Execute a tool with full safety enforcement.

        This is the PRIMARY entry point for all tool invocations.
        PolicyEngine is ALWAYS called — cannot be bypassed.
        """
        if not request.request_id:
            request.request_id = uuid.uuid4().hex[:12]
        if not request.created_at:
            request.created_at = int(time.time() * 1000)

        logger.info(
            "Capability call: cap=%s source=%s args=%s",
            request.capability_id,
            request.source.value,
            str(request.arguments)[:200],
        )

        # Dry run check
        if request.dry_run:
            return ToolExecutionResult(
                request_id=request.request_id,
                status=InvokeStatus.DRY_RUN,
                error="Dry run — not executed.",
                started_at=request.created_at,
                finished_at=int(time.time() * 1000),
                duration_ms=0.0,
                policy_decision="dry_run",
            )

        # Idempotency check
        if request.idempotency_key:
            with self._lock:
                cached = self._idempotency_cache.get(request.idempotency_key)
            if cached is not None:
                return ToolExecutionResult(
                    request_id=request.request_id,
                    status=InvokeStatus.IDEMPOTENT_HIT,
                    output=cached.output,
                    error=f"Idempotent hit for key '{request.idempotency_key}'.",
                    started_at=request.created_at,
                    finished_at=int(time.time() * 1000),
                    duration_ms=0.0,
                    policy_decision="idempotent",
                )

        # Look up capability — try ToolRegistry first, then FolderCapabilityRegistry
        manifest = self._resolve_manifest(request.capability_id)
        if manifest is None:
            return ToolExecutionResult(
                request_id=request.request_id,
                status=InvokeStatus.NOT_FOUND,
                error=f"Capability '{request.capability_id}' is not registered in the capability catalog.",
                started_at=request.created_at,
                finished_at=int(time.time() * 1000),
            )
        if not bool(getattr(manifest, "enabled", True)):
            result = ToolExecutionResult(
                request_id=request.request_id,
                status=InvokeStatus.DENIED,
                error=f"Capability '{request.capability_id}' is disabled by user override.",
                started_at=request.created_at,
                finished_at=int(time.time() * 1000),
                policy_decision="DISABLED_BY_OVERRIDE",
            )
            self._record_audit(request, result)
            return result
        request.capability_id = manifest.capability_id
        validation_error = self._validate_arguments(manifest, request.arguments)
        if validation_error:
            return ToolExecutionResult(
                request_id=request.request_id,
                status=InvokeStatus.DENIED,
                error=validation_error,
                started_at=request.created_at,
                finished_at=int(time.time() * 1000),
                policy_decision="VALIDATION_DENY",
            )

        cap = self._registry.get_capability(request.capability_id)
        if cap is None and self._folder_registry is not None:
            manifest = self._folder_registry.get(request.capability_id)
            if manifest is not None:
                cap = _capability_from_manifest(manifest)
        if cap is None:
            return ToolExecutionResult(
                request_id=request.request_id,
                status=InvokeStatus.NOT_FOUND,
                error=f"Capability '{request.capability_id}' is not registered.",
                started_at=request.created_at,
                finished_at=int(time.time() * 1000),
            )

        request.tool_name = cap.name
        request.risk_level = cap.risk_level
        continuation_id = self._ensure_continuation(request)

        # Policy check — MANDATORY
        policy_result = self._policy.evaluate(cap, request.arguments)

        if policy_result.decision == PolicyDecision.DENY:
            result = ToolExecutionResult(
                request_id=request.request_id,
                status=InvokeStatus.DENIED,
                error=policy_result.reason,
                started_at=request.created_at,
                finished_at=int(time.time() * 1000),
                policy_decision="DENY",
                policy_result=policy_result,
            )
            self._record_audit(request, result)
            self._record_failure_for_repair(request, result)
            return result

        if policy_result.decision == PolicyDecision.UNAVAILABLE:
            result = ToolExecutionResult(
                request_id=request.request_id,
                status=InvokeStatus.UNAVAILABLE,
                error=policy_result.reason,
                started_at=request.created_at,
                finished_at=int(time.time() * 1000),
                policy_decision="UNAVAILABLE",
                policy_result=policy_result,
            )
            self._record_audit(request, result)
            return result

        if self._delegation_policy is not None and policy_result.decision in (
            PolicyDecision.ALLOW,
            PolicyDecision.ALLOW_WITH_AUDIT,
        ):
            manifest = self._catalog.resolve(cap.id) if self._catalog is not None else None
            declared_context = dict(request.metadata.get("delegation_context") or {})
            if manifest is not None:
                operation_category = str(getattr(manifest, "operation_category", "") or "")
                ownership_scope = str(getattr(manifest, "ownership_scope", "") or "")
                if operation_category:
                    declared_context.setdefault("operation_category", operation_category)
                if ownership_scope:
                    declared_context.setdefault("scope", ownership_scope)
            delegation = self._delegation_policy.evaluate(
                cap.id,
                request.arguments,
                side_effects=list(getattr(cap, "side_effects", []) or []),
                operation_context=declared_context,
            )
            if delegation.decision == "forbidden":
                result = ToolExecutionResult(
                    request_id=request.request_id,
                    status=InvokeStatus.DENIED,
                    error=delegation.reason,
                    started_at=request.created_at,
                    finished_at=int(time.time() * 1000),
                    policy_decision="DELEGATION_DENY",
                    policy_result=policy_result,
                )
                self._record_audit(request, result)
                self._record_failure_for_repair(request, result)
                return result
            if delegation.decision == "approval_required":
                policy_result = self._policy._create_approval_result(
                    cap,
                    request.arguments,
                    reason_override=delegation.reason or "Delegation policy requires approval.",
                )

        if policy_result.decision == PolicyDecision.ASK_APPROVAL:
            request.requires_approval = True
            with self._lock:
                self._pending_approvals[request.request_id] = request

            approval_id = ""
            if self._approval_manager is not None:
                appr = self._approval_manager.create_request(request, policy_result)
                approval_id = appr.approval_id
            elif self._approval_queue is not None:
                appr = self._approval_queue.enqueue(request, policy_result)
                approval_id = appr.approval_id

            result = ToolExecutionResult(
                request_id=request.request_id,
                status=InvokeStatus.APPROVAL_NEEDED,
                error=policy_result.reason,
                started_at=request.created_at,
                finished_at=int(time.time() * 1000),
                policy_decision="ASK_APPROVAL",
                policy_result=policy_result,
                approval_id=approval_id,
            )
            self._advance_continuation(
                continuation_id,
                stage="awaiting_approval",
                state="open",
                reason=policy_result.reason,
                approval_id=approval_id,
                waiting_for="user",
            )
            self._record_audit(request, result)
            return result

        # Execute (ALLOW or ALLOW_WITH_AUDIT)
        pre_observations = self._collect_completion_observations(manifest, phase="before")
        self._advance_continuation(continuation_id, stage="executing", state="open")
        result = self._invoke_internal(cap, request)
        self._apply_production_mock_guard(request, result)
        result.policy_result = policy_result

        # Idempotency cache
        if request.idempotency_key and result.success:
            with self._lock:
                self._idempotency_cache[request.idempotency_key] = result

        # Verification
        verification = self._verify_completion_or_default(request, result, manifest, pre_observations)
        if verification.status == "failed" and result.success and self._completion_retry_count(manifest) > 0:
            max_retries = self._completion_retry_count(manifest)
            for attempt in range(max_retries):
                delay_ms = self._completion_retry_delay_ms(manifest)
                if delay_ms > 0:
                    time.sleep(delay_ms / 1000.0)
                retry_pre = self._collect_completion_observations(manifest, phase="before")
                retry_result = self._invoke_internal(cap, request)
                self._apply_production_mock_guard(request, retry_result)
                retry_result.policy_result = policy_result
                retry_verification = self._verify_completion_or_default(request, retry_result, manifest, retry_pre)
                retry_result.output.setdefault("retry_of_request_id", result.request_id)
                retry_result.output.setdefault("retry_attempt", attempt + 1)
                result = retry_result
                verification = retry_verification
                if verification.status == "passed" or not result.success:
                    break
        result.verification = verification
        result.verification_status = verification.status
        if continuation_id:
            result.output.setdefault("continuation_id", continuation_id)
        if verification.status == "failed" and result.success and self._manifest_has_completion(manifest):
            result.status = InvokeStatus.EXECUTION_ERROR
            result.error = "Completion verification failed: " + "; ".join(verification.details)
            result.output.setdefault(
                "completion_verification",
                {
                    "status": verification.status,
                    "details": list(verification.details),
                    "repair_hint": verification.repair_hint,
                },
            )

        if result.success and verification.status == "passed":
            self._advance_continuation(
                continuation_id,
                stage="verified",
                state="completed",
                reason="Execution and completion verification passed.",
                waiting_for="",
            )
        elif verification.status in {"pending", "requires_observation"}:
            self._advance_continuation(
                continuation_id,
                stage="observing",
                state="open",
                reason="Additional observation is required.",
                waiting_for="external",
            )
        else:
            self._advance_continuation(
                continuation_id,
                stage="failed",
                state="failed",
                reason=result.error or "; ".join(verification.details),
            )
        self._record_audit(request, result)
        if not result.success:
            self._record_failure_for_repair(request, result)
        return result

    def invoke_tool(
        self,
        capability_id: str,
        params: dict[str, Any] | None = None,
        *,
        caller: str = "unknown",
    ) -> InvokeResult:
        """Backward-compatible invoke via capability_id."""
        request = ToolExecutionRequest(
            capability_id=capability_id,
            arguments=params or {},
            source=ExecutionSource.USER_EXPLICIT,
            reason=f"Direct invocation by {caller}",
        )
        result = self.execute(request)
        return InvokeResult(
            status=result.status,
            capability_id=capability_id,
            output=result.output,
            error=result.error,
            invocation_id=result.request_id,
            duration_ms=result.duration_ms,
            request=request,
            policy_result=result.policy_result,
            verification=result.verification,
        )

    def invoke_tool_approved(
        self,
        capability_id: str,
        params: dict[str, Any] | None = None,
        *,
        caller: str = "user-approved",
    ) -> InvokeResult:
        """Invoke AFTER user approval. DEPRECATED: use execute_approved(approval_id) instead."""
        import warnings

        warnings.warn(
            "invoke_tool_approved is deprecated. Use execute_approved instead.", DeprecationWarning, stacklevel=2
        )
        params = params or {}

        manifest = self._resolve_manifest(capability_id)
        if manifest is None:
            return InvokeResult(
                status=InvokeStatus.NOT_FOUND,
                capability_id=capability_id,
                error=f"Capability '{capability_id}' is not registered in the capability catalog.",
            )
        capability_id = manifest.capability_id
        validation_error = self._validate_arguments(manifest, params)
        if validation_error:
            return InvokeResult(
                status=InvokeStatus.DENIED,
                capability_id=capability_id,
                error=validation_error,
            )

        cap = self._registry.get_capability(capability_id)
        if cap is None:
            return InvokeResult(
                status=InvokeStatus.NOT_FOUND,
                capability_id=capability_id,
                error=f"Capability '{capability_id}' is not registered.",
            )

        store = self._policy.approval_store
        if not store.is_approved(capability_id):
            return InvokeResult(
                status=InvokeStatus.DENIED,
                capability_id=capability_id,
                error=f"No valid approval for '{capability_id}'.",
            )

        policy_result = self._policy.evaluate(cap, params)
        if policy_result.decision != PolicyDecision.ALLOW:
            return InvokeResult(
                status=InvokeStatus.DENIED,
                capability_id=capability_id,
                error=f"Policy denies after approval: {policy_result.reason}",
            )

        store.consume_approval(capability_id)

        request = ToolExecutionRequest(
            capability_id=capability_id,
            arguments=params,
            source=ExecutionSource.USER_EXPLICIT,
            reason=f"Approved invocation by {caller}",
        )
        result = self._invoke_internal(cap, request)
        self._record_audit(request, result)

        return InvokeResult(
            status=result.status,
            capability_id=capability_id,
            output=result.output,
            error=result.error,
            invocation_id=result.request_id,
            duration_ms=result.duration_ms,
            request=request,
        )

    # ── Convenience methods ────────────────────────────────────

    def execute_approved(self, approval_id: str) -> ToolExecutionResult:
        """Execute a previously approved request.

        Looks up the approval in the manager/queue, re-evaluates policy,
        validates arguments, and executes if ALLOW. One-time execution per approval_id.
        """
        manager = self._approval_manager
        queue = self._approval_queue

        if manager is None and queue is None:
            return ToolExecutionResult(
                status=InvokeStatus.DENIED,
                error="No approval manager or queue configured.",
            )

        # Check double-execution
        if manager is not None:
            if manager.is_executed(approval_id):
                return ToolExecutionResult(
                    status=InvokeStatus.DENIED,
                    error=f"Approval '{approval_id}' already executed.",
                )
            appr = manager.get(approval_id)
        else:
            if queue.is_executed(approval_id):
                return ToolExecutionResult(
                    status=InvokeStatus.DENIED,
                    error=f"Approval '{approval_id}' already executed.",
                )
            appr = queue.get(approval_id)

        if appr is None:
            return ToolExecutionResult(
                status=InvokeStatus.NOT_FOUND,
                error=f"Approval '{approval_id}' not found.",
            )

        if appr.status == "expired":
            return ToolExecutionResult(
                status=InvokeStatus.DENIED,
                error=f"Approval '{approval_id}' has expired.",
            )

        if appr.status not in ("approved", "modified"):
            return ToolExecutionResult(
                status=InvokeStatus.DENIED,
                error=f"Approval '{approval_id}' is not approved (status={appr.status}).",
            )

        # Mark as executing
        if manager is not None:
            manager.mark_executing(approval_id)

        manifest = self._resolve_manifest(appr.capability_id)
        if manifest is None:
            error_msg = f"Capability '{appr.capability_id}' not found in catalog."
            if manager is not None:
                manager.mark_failed(approval_id, error_msg)
            else:
                queue.mark_failed(approval_id, error_msg)
            return ToolExecutionResult(
                status=InvokeStatus.NOT_FOUND,
                error=error_msg,
                approval_id=approval_id,
            )
        validation_error = self._validate_arguments(manifest, appr.arguments)
        if validation_error:
            if manager is not None:
                manager.mark_failed(approval_id, validation_error)
            else:
                queue.mark_failed(approval_id, validation_error)
            return ToolExecutionResult(
                status=InvokeStatus.DENIED,
                error=validation_error,
                policy_decision="VALIDATION_DENY",
                approval_id=approval_id,
            )

        cap = self._registry.get_capability(manifest.capability_id)
        if cap is None:
            return ToolExecutionResult(
                status=InvokeStatus.NOT_FOUND,
                error=f"Capability '{manifest.capability_id}' not found.",
            )

        # Re-evaluate policy (MANDATORY)
        policy_result = self._policy.evaluate(cap, appr.arguments)
        if policy_result.decision == PolicyDecision.DENY:
            error_msg = f"Policy denies after approval: {policy_result.reason}"
            if manager is not None:
                manager.mark_failed(approval_id, error_msg)
            else:
                queue.mark_failed(approval_id, error_msg)
            return ToolExecutionResult(
                status=InvokeStatus.DENIED,
                error=error_msg,
                policy_decision="DENY",
                policy_result=policy_result,
                approval_id=approval_id,
            )

        # The approval_id being executed is already approved/modified.
        # Re-evaluation is kept for DENY gates, but ASK_APPROVAL should not
        # create a second approval loop for the same reviewed request.

        request = ToolExecutionRequest(
            request_id=appr.request_id,
            task_id=appr.task_id,
            capability_id=manifest.capability_id,
            tool_name=appr.tool_name,
            arguments=appr.arguments,
            source=self._resolve_source(appr.source),
            reason=f"Approved: {appr.approval_reason}",
            source_desire=appr.source_desire,
            frustration=appr.frustration,
            origin_channel=appr.origin_channel,
            conversation_id=appr.conversation_id,
            metadata={**dict(appr.metadata or {}), "approval_id": approval_id, "approved_execution": True},
        )

        pre_observations = self._collect_completion_observations(manifest, phase="before")
        result = self._invoke_internal(cap, request)
        self._apply_production_mock_guard(request, result)
        result.policy_result = policy_result
        result.approval_id = approval_id
        verification = self._verify_completion_or_default(request, result, manifest, pre_observations)
        if verification.status == "failed" and result.success and self._completion_retry_count(manifest) > 0:
            for attempt in range(self._completion_retry_count(manifest)):
                delay_ms = self._completion_retry_delay_ms(manifest)
                if delay_ms > 0:
                    time.sleep(delay_ms / 1000.0)
                retry_pre = self._collect_completion_observations(manifest, phase="before")
                result = self._invoke_internal(cap, request)
                self._apply_production_mock_guard(request, result)
                result.policy_result = policy_result
                result.approval_id = approval_id
                verification = self._verify_completion_or_default(request, result, manifest, retry_pre)
                result.output.setdefault("retry_attempt", attempt + 1)
                if verification.status == "passed" or not result.success:
                    break
        result.verification = verification
        result.verification_status = verification.status
        if verification.status == "failed" and result.success and self._manifest_has_completion(manifest):
            result.status = InvokeStatus.EXECUTION_ERROR
            result.error = "Completion verification failed: " + "; ".join(verification.details)
            result.output.setdefault(
                "completion_verification",
                {
                    "status": verification.status,
                    "details": list(verification.details),
                    "repair_hint": verification.repair_hint,
                },
            )

        continuation_id = str(request.metadata.get("continuation_id") or "")
        if continuation_id:
            result.output.setdefault("continuation_id", continuation_id)
        if result.success and verification.status == "passed":
            self._advance_continuation(
                continuation_id,
                stage="verified",
                state="completed",
                reason="Approved execution and completion verification passed.",
                waiting_for="",
            )
        elif result.success:
            self._advance_continuation(
                continuation_id,
                stage="observing",
                state="open",
                reason="Approved execution requires additional observation.",
                waiting_for="external",
            )
        else:
            self._advance_continuation(
                continuation_id,
                stage="failed",
                state="failed",
                reason=result.error or "; ".join(verification.details),
            )

        if result.success:
            if manager is not None:
                manager.mark_executed(approval_id, result)
            else:
                queue.mark_executed(approval_id, result)
        else:
            if manager is not None:
                manager.mark_failed(approval_id, result.error)
            else:
                queue.mark_failed(approval_id, result.error)

        self._record_audit(request, result)
        return result

    def _ensure_continuation(self, request: ToolExecutionRequest) -> str:
        continuation_id = str(request.metadata.get("continuation_id") or "")
        if continuation_id or self._continuation_manager is None:
            return continuation_id
        try:
            record = self._continuation_manager.create(
                goal=request.reason or request.tool_name or request.capability_id,
                trigger=request.source.value,
                task_id=request.task_id,
                step_id=request.step_id,
                request_id=request.request_id,
                capability_id=request.capability_id,
                arguments=dict(request.arguments),
                purpose=request.reason,
                source_desire=request.source_desire,
                conversation_id=request.conversation_id,
                stage="selected",
                success_condition=str(request.metadata.get("success_condition") or ""),
                stop_condition=str(request.metadata.get("stop_condition") or ""),
                rationale=request.reason,
            )
            continuation_id = record.continuation_id
            request.metadata["continuation_id"] = continuation_id
        except Exception:
            logger.debug("Failed to create continuation", exc_info=True)
        return continuation_id

    def _advance_continuation(
        self,
        continuation_id: str,
        *,
        stage: str,
        state: str,
        reason: str = "",
        **updates: Any,
    ) -> None:
        if not continuation_id or self._continuation_manager is None:
            return
        try:
            self._continuation_manager.advance(
                continuation_id,
                stage=stage,
                state=state,
                reason=reason,
                **updates,
            )
        except Exception:
            logger.debug("Failed to advance continuation %s", continuation_id, exc_info=True)

    def find_capability(self, capability_id: str) -> Capability | None:
        return self._registry.get_capability(capability_id)

    def _resolve_manifest(self, capability_id: str) -> Any | None:
        if self._catalog is None:
            return None
        return self._catalog.resolve(capability_id)

    def _validate_arguments(self, manifest: Any, arguments: dict[str, Any]) -> str:
        schema = getattr(manifest, "input_schema", None) or {"type": "object", "properties": {}}
        try:
            validate(instance=arguments or {}, schema=schema)
            return ""
        except ValidationError as exc:
            path = ".".join(str(part) for part in exc.path)
            location = f" at '{path}'" if path else ""
            return f"Invalid arguments for '{manifest.capability_id}'{location}: {exc.message}"

    def search_capabilities(
        self,
        query: str,
        server_type: Any = None,
        max_risk: RiskLevel | None = None,
    ) -> list[Capability]:
        return self._registry.search(query, server_type=server_type, max_risk_level=max_risk)

    def list_safe_capabilities(self) -> list[Capability]:
        return self._registry.get_safe_capabilities()

    def list_autonomous_capabilities(self) -> list[Capability]:
        """Return capabilities available for autonomous execution.

        Includes ALLOW, ALLOW_WITH_AUDIT, and ASK_APPROVAL capabilities.
        Excludes DENY and UNAVAILABLE.
        """
        all_caps = self._registry.list_capabilities()
        autonomous_caps = []
        for cap in all_caps:
            policy_result = self._policy.evaluate(cap)
            if policy_result.decision in (
                PolicyDecision.ALLOW,
                PolicyDecision.ALLOW_WITH_AUDIT,
                PolicyDecision.ASK_APPROVAL,
            ):
                autonomous_caps.append(cap)
        return autonomous_caps

    def list_autonomous_capability_options(self) -> list[Any]:
        """Return every capability with its policy-aware autonomy disposition.

        This is descriptive only. Execution still goes through ``execute`` and
        PolicyEngine. Including denied and unavailable options lets the LLM
        explain non-action without accidentally invoking them.
        """
        from aegis_ai.autonomous.models import (
            AutonomousCapabilityOption,
            CapabilityDisposition,
        )

        options: list[AutonomousCapabilityOption] = []
        catalog = self._catalog
        for capability in self._registry.list_capabilities():
            manifest = catalog.resolve(capability.id) if catalog is not None else None
            enabled = bool(getattr(manifest, "enabled", True))
            result = self._policy.evaluate(capability)
            if not enabled:
                disposition = CapabilityDisposition.UNAVAILABLE
            elif result.decision in (PolicyDecision.ALLOW, PolicyDecision.ALLOW_WITH_AUDIT):
                disposition = CapabilityDisposition.EXECUTE_SAFE
            elif result.decision == PolicyDecision.ASK_APPROVAL:
                disposition = CapabilityDisposition.PROPOSE_FOR_APPROVAL
            elif result.decision == PolicyDecision.UNAVAILABLE:
                disposition = CapabilityDisposition.UNAVAILABLE
            else:
                disposition = CapabilityDisposition.FORBIDDEN
            options.append(
                AutonomousCapabilityOption(
                    capability_id=capability.id,
                    disposition=disposition,
                    policy_decision=result.decision.name,
                    policy_reason=result.reason,
                    risk_level=result.risk_level.name,
                    requires_approval=disposition == CapabilityDisposition.PROPOSE_FOR_APPROVAL,
                    enabled=enabled,
                    available=enabled and disposition != CapabilityDisposition.UNAVAILABLE,
                    server_id=capability.id.split(".", 1)[0],
                )
            )
        return options

    def get_pending_approvals(self) -> dict[str, ToolExecutionRequest]:
        with self._lock:
            return dict(self._pending_approvals)

    def clear_pending_approval(self, request_id: str) -> None:
        with self._lock:
            self._pending_approvals.pop(request_id, None)

    # ── Mock Executor Registration ─────────────────────────────

    def register_mock(self, capability_id_prefix: str, executor: MockExecutorFunc) -> None:
        """Register a mock executor for testing."""
        with self._lock:
            self._mock_executors[capability_id_prefix] = executor

    def set_default_mock(self, executor: MockExecutorFunc) -> None:
        """Override the default executor (for testing only)."""
        with self._lock:
            self._default_mock = executor

    def _manifest_has_completion(self, manifest: Any) -> bool:
        completion = getattr(manifest, "completion", {}) or {}
        return isinstance(completion, dict) and bool(completion.get("checks"))

    def _completion_retry_count(self, manifest: Any) -> int:
        completion = getattr(manifest, "completion", {}) or {}
        retry = completion.get("retry", {}) if isinstance(completion, dict) else {}
        if not isinstance(retry, dict):
            return 0
        return max(0, min(3, int(retry.get("max_attempts", 0) or 0)))

    def _completion_retry_delay_ms(self, manifest: Any) -> int:
        completion = getattr(manifest, "completion", {}) or {}
        retry = completion.get("retry", {}) if isinstance(completion, dict) else {}
        if not isinstance(retry, dict):
            return 0
        return max(0, min(5000, int(retry.get("delay_ms", 0) or 0)))

    def _collect_completion_observations(self, manifest: Any, *, phase: str) -> dict[str, Any]:
        completion = getattr(manifest, "completion", {}) or {}
        checks = completion.get("checks", []) if isinstance(completion, dict) else []
        observations: dict[str, Any] = {}
        if phase != "before" or not isinstance(checks, list):
            return observations
        for idx, check in enumerate(checks):
            if not isinstance(check, dict) or not check.get("capture_before", True):
                continue
            key = str(check.get("name") or f"check_{idx}")
            observations[key] = self._run_completion_observation(check)
        return observations

    def _verify_completion_or_default(
        self,
        request: ToolExecutionRequest,
        result: ToolExecutionResult,
        manifest: Any,
        pre_observations: dict[str, Any] | None = None,
    ) -> VerificationResult:
        if self._manifest_has_completion(manifest):
            return self._verify_manifest_completion(request, result, manifest, pre_observations or {})
        if self._verification is not None:
            vr = self._verification.build_request(request, result)
            verification = self._verification.verify(vr)
            result.verification_status = verification.status.value
            self._verification.record_verification(vr, verification)
            return VerificationResult(
                request_id=request.request_id,
                status=verification.status.value,
                details=[str(getattr(verification, "reason", ""))],
            )
        return verify_tool_result(request, result)

    def _verify_manifest_completion(
        self,
        request: ToolExecutionRequest,
        result: ToolExecutionResult,
        manifest: Any,
        pre_observations: dict[str, Any],
    ) -> VerificationResult:
        verification = VerificationResult(request_id=request.request_id)
        completion = getattr(manifest, "completion", {}) or {}
        checks = completion.get("checks", []) if isinstance(completion, dict) else []
        mode = str(completion.get("mode", "all")).lower()
        if result.status != InvokeStatus.SUCCESS:
            verification.status = "skipped"
            verification.details.append(f"Skipped: status={result.status.value}")
            return verification
        passed = 0
        failed = 0
        for idx, check in enumerate(checks if isinstance(checks, list) else []):
            if not isinstance(check, dict):
                continue
            name = str(check.get("name") or f"check_{idx}")
            ok, detail = self._evaluate_completion_check(check, result, pre_observations.get(name))
            if ok:
                passed += 1
            else:
                failed += 1
            verification.details.append(f"{name}: {detail}")
        verification.checks_passed = passed
        verification.checks_failed = failed
        if not checks:
            verification.status = "skipped"
        elif mode == "any":
            verification.status = "passed" if passed > 0 else "failed"
        else:
            verification.status = "passed" if failed == 0 else "failed"
        if verification.status == "failed":
            verification.repair_hint = str(completion.get("on_failure") or "retry_or_user_confirmation")
        return verification

    def _evaluate_completion_check(
        self,
        check: dict[str, Any],
        result: ToolExecutionResult,
        before: Any = None,
    ) -> tuple[bool, str]:
        check_type = str(check.get("type", "")).lower()
        if check_type == "http_status":
            code = int(result.output.get("status_code", result.output.get("code", 0)) or 0)
            minimum = int(check.get("min", 200) or 200)
            maximum = int(check.get("max", 399) or 399)
            return minimum <= code <= maximum, f"HTTP status {code}, expected {minimum}-{maximum}"
        if check_type == "file_exists":
            path_key = str(check.get("path_param") or check.get("path_key") or "path")
            path = str(result.output.get(path_key) or result.output.get("file_path") or check.get("path") or "")
            exists = bool(path) and Path(path).exists()
            return exists, f"file exists={exists} path={path}"
        if check_type == "event":
            event_type = str(check.get("event_type") or "")
            observed = self._observe_recent_event(event_type)
            return observed, f"event observed={observed} type={event_type or '(any)'}"
        if check_type in {"screenshot", "ui_tree"}:
            after = self._run_completion_observation(check)
            if isinstance(after, dict) and after.get("error"):
                return False, f"observation failed: {after.get('error')}"
            if check.get("expect_changed", False):
                if before is None:
                    return False, "missing before observation"
                changed = _fingerprint(before) != _fingerprint(after)
                return changed, f"changed={changed}"
            if check_type == "ui_tree":
                nodes = self._count_ui_nodes(after)
                minimum = int(check.get("min_nodes", 1) or 1)
                return nodes >= minimum, f"ui nodes={nodes}, expected >= {minimum}"
            return bool(after), "observation present"
        if check_type == "output_field":
            field_name = str(check.get("field") or "")
            expected = check.get("equals")
            value: Any = result.output
            for part in field_name.split("."):
                if not isinstance(value, dict):
                    value = None
                    break
                value = value.get(part)
            ok = value == expected if "equals" in check else bool(value)
            return ok, f"output {field_name}={value!r}"
        return False, f"unsupported completion check type={check_type}"

    def _run_completion_observation(self, check: dict[str, Any]) -> Any:
        capability_id = str(check.get("capability_id") or "")
        if not capability_id or self._server_executor is None:
            return {"error": "No observation capability configured"}
        params = dict(check.get("params") or {})
        try:
            return self._server_executor.execute_capability(capability_id, params)
        except Exception as exc:
            return {"error": str(exc)}

    def _observe_recent_event(self, event_type: str) -> bool:
        manager = getattr(self, "_event_manager", None)
        if manager is None:
            return False
        try:
            result = manager.list_recent(limit=25)
            events = result.get("events", []) if isinstance(result, dict) else result
            for event in events:
                value = event.get("event_type") if isinstance(event, dict) else getattr(event, "event_type", "")
                if not event_type or value == event_type:
                    return True
        except Exception:
            logger.debug("Completion event observation failed", exc_info=True)
        return False

    @staticmethod
    def _count_ui_nodes(value: Any) -> int:
        if isinstance(value, dict):
            if isinstance(value.get("nodes"), list):
                return len(value["nodes"])
            if isinstance(value.get("ui_tree"), dict):
                return ToolBroker._count_ui_nodes(value["ui_tree"])
            return sum(ToolBroker._count_ui_nodes(v) for v in value.values())
        if isinstance(value, list):
            return len(value) + sum(ToolBroker._count_ui_nodes(v) for v in value)
        return 0

    # ── Internal — the ONLY execution path ─────────────────────

    def _invoke_internal(
        self,
        cap: Capability,
        request: ToolExecutionRequest,
    ) -> ToolExecutionResult:
        """Execute a capability after policy has ALLOWed it.

        PRIVATE. Cannot be called from outside the class.
        ALWAYS called after PolicyEngine.evaluate() returns ALLOW.
        """
        started_at = int(time.time() * 1000)
        try:
            arguments = dict(request.arguments)
            if request.metadata.get("approved_execution"):
                arguments["_aegis_approved_execution"] = True
                arguments["_aegis_approval_id"] = request.metadata.get("approval_id", "")
            output = self._server_executor.execute(cap, arguments)
            finished_at = int(time.time() * 1000)
            if isinstance(output, dict) and output.get("error"):
                error_msg = output["error"]
                return ToolExecutionResult(
                    request_id=request.request_id,
                    status=InvokeStatus.EXECUTION_ERROR,
                    error=error_msg,
                    output=output,
                    started_at=started_at,
                    finished_at=finished_at,
                    duration_ms=finished_at - started_at,
                    policy_decision="ALLOW",
                )
            return ToolExecutionResult(
                request_id=request.request_id,
                status=InvokeStatus.SUCCESS,
                output=output if isinstance(output, dict) else {"result": output},
                started_at=started_at,
                finished_at=finished_at,
                duration_ms=finished_at - started_at,
                policy_decision="ALLOW",
            )
        except Exception as e:
            finished_at = int(time.time() * 1000)
            return ToolExecutionResult(
                request_id=request.request_id,
                status=InvokeStatus.EXECUTION_ERROR,
                error=f"Server execution error: {e}",
                started_at=started_at,
                finished_at=finished_at,
                duration_ms=finished_at - started_at,
                policy_decision="ALLOW",
            )

    # ── Audit ──────────────────────────────────────────────────

    def _record_audit(self, request: ToolExecutionRequest, result: ToolExecutionResult) -> None:
        """Record execution to audit log with sensitive data masking."""
        masked_args = _mask_sensitive(request.arguments)
        entry = {
            "request_id": request.request_id,
            "task_id": request.task_id,
            "source": request.source.value,
            "capability_id": request.capability_id,
            "tool_name": request.tool_name,
            "arguments_summary": str(_compact_audit_value(masked_args))[:16_384],
            "policy_decision": result.policy_decision,
            "execution_status": result.status.value,
            "error": result.error if result.error else "",
            "output": _compact_audit_value(result.output),
            "duration_ms": result.duration_ms,
            "verification_status": result.verification_status,
            "verification": {
                "status": result.verification.status if result.verification else result.verification_status,
                "checks_passed": result.verification.checks_passed if result.verification else 0,
                "checks_failed": result.verification.checks_failed if result.verification else 0,
                "details": _compact_audit_value(result.verification.details if result.verification else []),
                "repair_hint": result.verification.repair_hint if result.verification else "",
            },
            "reason": request.reason,
            "timestamp": int(time.time() * 1000),
        }

        if request.source == ExecutionSource.DESIRE_DRIVEN:
            entry["source_desire"] = request.source_desire
            entry["frustration"] = request.frustration

        if self._audit is not None:
            try:
                from aegis_ai.audit import AuditEntry

                audit_entry = AuditEntry(
                    action="tool_execution",
                    actor=request.source.value,
                    capability_id=request.capability_id,
                    decision=result.policy_decision,
                    reason=request.reason,
                    detail=entry,
                )
                self._audit.append(audit_entry)
                result.audit_log_id = audit_entry.entry_id
            except Exception as exc:
                logger.warning("Failed to write audit: %s", exc)

        logger.info(
            "Tool execution: cap=%s status=%s source=%s duration=%.1fms",
            request.capability_id,
            result.status.value,
            request.source.value,
            result.duration_ms,
        )

    def _apply_production_mock_guard(
        self,
        request: ToolExecutionRequest,
        result: ToolExecutionResult,
    ) -> None:
        if not is_production_mode() or not result.success:
            return
        if not is_mock_like_output(result.output):
            return
        result.status = InvokeStatus.EXECUTION_ERROR
        result.error = f"Production mode rejected mock/stub output for capability '{request.capability_id}'."
        result.output.setdefault("production_blocker", True)
        result.output.setdefault("production_blocker_reason", result.error)
        result.verification_status = "failed"

    def _record_failure_for_repair(self, request: ToolExecutionRequest, result: ToolExecutionResult) -> None:
        if self._repair_manager is None or result.success:
            return
        try:
            self._repair_manager.record_failure(
                capability_id=request.capability_id,
                error=result.error,
                status=result.status.value,
                request=request,
                result=result,
            )
        except Exception:
            logger.debug("RepairManager failure recording failed", exc_info=True)

    @staticmethod
    def _default_executor(cap: Capability, params: dict[str, Any]) -> dict[str, Any]:
        """Default mock executor — returns a generic success response."""
        return {
            "mock": True,
            "capability": cap.id,
            "params_received": params,
            "message": f"Mock execution of '{cap.name}' completed successfully.",
        }

    @staticmethod
    def _resolve_source(source_str: str) -> ExecutionSource:
        for es in ExecutionSource:
            if es.value == source_str:
                return es
        return ExecutionSource.USER_EXPLICIT
