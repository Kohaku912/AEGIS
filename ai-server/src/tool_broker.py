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

import logging
import re
import threading
import time
import uuid
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

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
    risk_map = {
        "low": RiskLevel.READ_ONLY,
        "safe": RiskLevel.SAFE_ACTION,
        "medium": RiskLevel.APPROVAL_REQUIRED,
        "high": RiskLevel.HIGH_RISK,
        "critical": RiskLevel.FORBIDDEN,
    }
    risk = risk_map.get(getattr(manifest, "risk_level", "low"), RiskLevel.READ_ONLY)

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
        description=manifest.description,
        server_type=server_type,
        risk_level=risk,
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


def verify_tool_result(request: ToolExecutionRequest, result: ToolExecutionResult) -> VerificationResult:
    """Basic post-execution verification.

    Checks:
    - File operations: output contains path/status
    - HTTP operations: status code in 2xx-3xx
    - Other: structural presence of output
    """
    vr = VerificationResult(request_id=request.request_id)
    cap_id = request.capability_id

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

    if "file" in cap_id.lower() or "write" in cap_id.lower():
        if "path" in result.output or "file_path" in result.output:
            vr.checks_passed += 1
            vr.details.append("File path in output")
        else:
            vr.checks_failed += 1
            vr.details.append("Missing file path in output")

    if "http" in cap_id.lower() or "request" in cap_id.lower():
        code = result.output.get("status_code", result.output.get("code", 0))
        if 200 <= code < 400:
            vr.checks_passed += 1
            vr.details.append(f"HTTP status {code} OK")
        elif code > 0:
            vr.checks_failed += 1
            vr.details.append(f"HTTP status {code} not OK")

    vr.status = "passed" if vr.checks_failed == 0 else "failed"
    return vr


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


# ═══════════════════════════════════════════════════════════════
# Retry classification
# ═══════════════════════════════════════════════════════════════

_NO_RETRY_CAPS = {
    "send_sns", "post_sns", "send_dm", "send_message", "send_email",
    "delete_file", "delete_all", "rm_", "wipe_", "purchase",
    "upload_", "transmit_", "deploy", "push_main", "merge_to_main",
}


def _is_retryable(capability_id: str) -> bool:
    """Check if a capability's failure is retryable."""
    for pattern in _NO_RETRY_CAPS:
        if pattern in capability_id:
            return False
    return True


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
        server_executor: ServerExecutor | None = None,
        folder_registry: Any = None,
        catalog: Any = None,
    ) -> None:
        self._registry = registry
        self._policy = policy_engine or create_default_policy_engine()
        self._audit = audit_log
        self._verification = verification_service
        self._approval_queue = approval_queue
        self._server_executor = server_executor or ServerExecutor()
        self._folder_registry = folder_registry
        self._catalog = catalog

        if self._catalog is not None:
            self._server_executor.set_catalog(self._catalog)

        self._mock_executors: dict[str, MockExecutorFunc] = {}
        self._default_mock: MockExecutorFunc = self._default_executor

        # Idempotency: key → result
        self._idempotency_cache: dict[str, ToolExecutionResult] = {}

        # Pending approval requests
        self._pending_approvals: dict[str, ToolExecutionRequest] = {}
        self._lock = threading.RLock()

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
            request.capability_id, request.source.value, str(request.arguments)[:200],
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
        cap = self._registry.get_capability(request.capability_id)
        manifest = None
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
            return result

        if policy_result.decision == PolicyDecision.ASK_APPROVAL:
            request.requires_approval = True
            with self._lock:
                self._pending_approvals[request.request_id] = request

            approval_id = ""
            if self._approval_queue is not None:
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
            self._record_audit(request, result)
            return result

        # Execute (only if ALLOW)
        result = self._invoke_internal(cap, request)
        result.policy_result = policy_result

        # Idempotency cache
        if request.idempotency_key and result.success:
            with self._lock:
                self._idempotency_cache[request.idempotency_key] = result

        # Verification
        if self._verification is not None:
            vr = self._verification.build_request(request, result)
            verification = self._verification.verify(vr)
            result.verification_status = verification.status.value
            self._verification.record_verification(vr, verification)
        else:
            verification = verify_tool_result(request, result)
            result.verification_status = verification.status

        self._record_audit(request, result)
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
        )

    def invoke_tool_approved(
        self,
        capability_id: str,
        params: dict[str, Any] | None = None,
        *,
        caller: str = "user-approved",
    ) -> InvokeResult:
        """Invoke AFTER user approval."""
        params = params or {}

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

        Looks up the approval in the queue, re-evaluates policy,
        and executes if ALLOW. One-time execution per approval_id.
        """
        if self._approval_queue is None:
            return ToolExecutionResult(
                status=InvokeStatus.DENIED,
                error="No approval queue configured.",
            )

        if self._approval_queue.is_executed(approval_id):
            return ToolExecutionResult(
                status=InvokeStatus.DENIED,
                error=f"Approval '{approval_id}' already executed.",
            )

        appr = self._approval_queue.get(approval_id)
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

        cap = self._registry.get_capability(appr.capability_id)
        if cap is None:
            return ToolExecutionResult(
                status=InvokeStatus.NOT_FOUND,
                error=f"Capability '{appr.capability_id}' not found.",
            )

        policy_result = self._policy.evaluate(cap, appr.arguments)
        if policy_result.decision == PolicyDecision.DENY:
            self._approval_queue.mark_failed(approval_id, policy_result.reason)
            return ToolExecutionResult(
                status=InvokeStatus.DENIED,
                error=f"Policy denies after approval: {policy_result.reason}",
                policy_decision="DENY",
                policy_result=policy_result,
                approval_id=approval_id,
            )

        if policy_result.decision == PolicyDecision.ASK_APPROVAL:
            return ToolExecutionResult(
                status=InvokeStatus.APPROVAL_NEEDED,
                error="Still requires approval after re-evaluation.",
                policy_decision="ASK_APPROVAL",
                policy_result=policy_result,
                approval_id=approval_id,
            )

        request = ToolExecutionRequest(
            request_id=appr.request_id,
            task_id=appr.task_id,
            capability_id=appr.capability_id,
            tool_name=appr.tool_name,
            arguments=appr.arguments,
            source=self._resolve_source(appr.source),
            reason=f"Approved: {appr.approval_reason}",
            source_desire=appr.source_desire,
            frustration=appr.frustration,
        )

        result = self._invoke_internal(cap, request)
        result.policy_result = policy_result
        result.approval_id = approval_id

        if self._verification is not None:
            vr = self._verification.build_request(request, result)
            verification = self._verification.verify(vr)
            result.verification_status = verification.status.value
            self._verification.record_verification(vr, verification)

        if result.success:
            self._approval_queue.mark_executed(approval_id, result)
        else:
            self._approval_queue.mark_failed(approval_id, result.error)

        self._record_audit(request, result)
        return result

    def find_capability(self, capability_id: str) -> Capability | None:
        return self._registry.get_capability(capability_id)

    def search_capabilities(
        self,
        query: str,
        server_type: Any = None,
        max_risk: RiskLevel | None = None,
    ) -> list[Capability]:
        return self._registry.search(query, server_type=server_type, max_risk_level=max_risk)

    def list_safe_capabilities(self) -> list[Capability]:
        return self._registry.get_safe_capabilities()

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
            output = self._server_executor.execute(cap, request.arguments)
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
            "arguments_summary": str(masked_args),
            "policy_decision": result.policy_decision,
            "execution_status": result.status.value,
            "error": result.error if result.error else "",
            "output": result.output,
            "duration_ms": result.duration_ms,
            "verification_status": result.verification_status,
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
            request.capability_id, result.status.value, request.source.value, result.duration_ms,
        )

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
