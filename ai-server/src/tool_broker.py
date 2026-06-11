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

import json
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Callable

from aegis_schema.models import Capability, RiskLevel

from policy_engine import PolicyDecision, PolicyEngine, PolicyResult, create_default_policy_engine
from tool_registry import ToolRegistry


class InvokeStatus(Enum):
    """Outcome of a tool invocation."""
    SUCCESS = auto()          # Executed successfully
    DENIED = auto()           # PolicyEngine denied the invocation
    APPROVAL_NEEDED = auto()  # PolicyEngine requires user approval
    NOT_FOUND = auto()        # Capability not registered
    EXECUTION_ERROR = auto()  # Mock executor threw an error
    TIMEOUT = auto()          # Execution exceeded timeout (not implemented yet)


@dataclass
class InvokeResult:
    """Result of invoking a capability through the ToolBroker."""
    status: InvokeStatus
    capability_id: str = ""
    output: dict[str, Any] = field(default_factory=dict)
    error: str = ""
    policy_result: PolicyResult | None = None
    invocation_id: str = ""
    duration_ms: float = 0.0

    @property
    def success(self) -> bool:
        return self.status == InvokeStatus.SUCCESS

    @property
    def denied(self) -> bool:
        return self.status in (InvokeStatus.DENIED, InvokeStatus.APPROVAL_NEEDED)


# Type alias for mock executor functions
MockExecutorFunc = Callable[[Capability, dict[str, Any]], dict[str, Any]]


class ToolBroker:
    """Central capability dispatch with mandatory safety enforcement.

    STRUCTURAL CONSTRAINT: All execution goes through _invoke_internal(),
    which ALWAYS calls policy_engine.evaluate() before the executor.
    There is NO public method that executes a capability without policy check.

    Usage:
        registry = ToolRegistry()
        policy = create_default_policy_engine()
        broker = ToolBroker(registry, policy)

        # Register capabilities via registry first
        registry.register_capability(cap)

        # Invoke (policy check is automatic)
        result = broker.invoke_tool("pc.screenshot", {"display_id": 0})
        if result.success:
            print(result.output)
    """

    def __init__(
        self,
        registry: ToolRegistry,
        policy_engine: PolicyEngine | None = None,
    ) -> None:
        """Initialize ToolBroker.

        Args:
            registry: The ToolRegistry holding registered capabilities.
            policy_engine: PolicyEngine instance. If None, creates a default
                          PolicyEngine with sensible safety defaults.
        """
        self._registry = registry
        self._policy = policy_engine or create_default_policy_engine()

        # Mock executors: capability_id_prefix → executor function
        # Private — cannot be accessed from outside
        self._mock_executors: dict[str, MockExecutorFunc] = {}

        # Default mock executor for capabilities without a specific one
        self._default_mock: MockExecutorFunc = self._default_executor

    # ── Public API — the ONLY way to invoke tools ──────────────

    def invoke_tool(
        self,
        capability_id: str,
        params: dict[str, Any] | None = None,
        *,
        caller: str = "unknown",
    ) -> InvokeResult:
        """Invoke a capability with mandatory safety enforcement.

        This is the PRIMARY entry point. All tool invocations MUST use this method.
        PolicyEngine is ALWAYS called — cannot be bypassed.

        Args:
            capability_id: The capability to invoke (e.g. "pc.screenshot").
            params: Input parameters for the capability.
            caller: Identifier for audit log (agent name, user, etc.).

        Returns:
            InvokeResult with status, output, and metadata.
        """
        params = params or {}
        invocation_id = str(uuid.uuid4())[:8]
        start_time = time.perf_counter()

        # Step 1: Look up capability
        cap = self._registry.get_capability(capability_id)
        if cap is None:
            return InvokeResult(
                status=InvokeStatus.NOT_FOUND,
                capability_id=capability_id,
                error=f"Capability '{capability_id}' is not registered.",
                invocation_id=invocation_id,
                duration_ms=(time.perf_counter() - start_time) * 1000,
            )

        # Step 2: Policy check — MANDATORY, cannot be bypassed
        policy_result = self._policy.evaluate(cap, params)

        if policy_result.decision == PolicyDecision.DENY:
            return InvokeResult(
                status=InvokeStatus.DENIED,
                capability_id=capability_id,
                error=policy_result.reason,
                policy_result=policy_result,
                invocation_id=invocation_id,
                duration_ms=(time.perf_counter() - start_time) * 1000,
            )

        if policy_result.decision == PolicyDecision.ASK_APPROVAL:
            return InvokeResult(
                status=InvokeStatus.APPROVAL_NEEDED,
                capability_id=capability_id,
                error=policy_result.reason,
                policy_result=policy_result,
                invocation_id=invocation_id,
                duration_ms=(time.perf_counter() - start_time) * 1000,
            )

        # Step 3: Execute (only if ALLOW)
        return self._invoke_internal(cap, params, invocation_id, start_time)

    def invoke_tool_approved(
        self,
        capability_id: str,
        params: dict[str, Any] | None = None,
        *,
        caller: str = "user-approved",
    ) -> InvokeResult:
        """Invoke a capability AFTER user has approved it via Approval UI.

        Checks the ApprovalStore for a valid approval before executing.
        If a valid approval exists:
        - ONE_TIME approvals are consumed (single use)
        - SESSION approvals allow repeated execution within the session

        After approval check passes, re-evaluates policy (in case rules changed).
        If ALLOWED, executes.
        """
        params = params or {}
        invocation_id = str(uuid.uuid4())[:8]
        start_time = time.perf_counter()

        cap = self._registry.get_capability(capability_id)
        if cap is None:
            return InvokeResult(
                status=InvokeStatus.NOT_FOUND,
                capability_id=capability_id,
                error=f"Capability '{capability_id}' is not registered.",
                invocation_id=invocation_id,
                duration_ms=(time.perf_counter() - start_time) * 1000,
            )

        # Check ApprovalStore for valid approval
        store = self._policy.approval_store
        if not store.is_approved(capability_id):
            return InvokeResult(
                status=InvokeStatus.DENIED,
                capability_id=capability_id,
                error=f"No valid approval found for '{capability_id}'. "
                      "User must approve via Approval UI first.",
                invocation_id=invocation_id,
                duration_ms=(time.perf_counter() - start_time) * 1000,
            )

        # Re-evaluate policy (approval state is now valid)
        policy_result = self._policy.evaluate(cap, params)
        if policy_result.decision != PolicyDecision.ALLOW:
            return InvokeResult(
                status=InvokeStatus.DENIED,
                capability_id=capability_id,
                error=f"Policy still denies after approval: {policy_result.reason}",
                policy_result=policy_result,
                invocation_id=invocation_id,
                duration_ms=(time.perf_counter() - start_time) * 1000,
            )

        # Consume the approval (ONE_TIME approvals are used up)
        store.consume_approval(capability_id)

        return self._invoke_internal(cap, params, invocation_id, start_time)

    # ── Convenience methods for Planner/Agents ───────────────

    def find_capability(self, capability_id: str) -> Capability | None:
        """Look up a capability by ID. Does NOT invoke it."""
        return self._registry.get_capability(capability_id)

    def search_capabilities(
        self,
        query: str,
        server_type: Any = None,
        max_risk: RiskLevel | None = None,
    ) -> list[Capability]:
        """Search for capabilities matching a query.

        The Planner uses this to discover relevant tools without seeing
        the entire registry at once.
        """
        return self._registry.search(query, server_type=server_type, max_risk_level=max_risk)

    def list_safe_capabilities(self) -> list[Capability]:
        """Get capabilities that can execute without approval."""
        return self._registry.get_safe_capabilities()

    # ── Mock Executor Registration ──────────────────────────

    def register_mock(self, capability_id_prefix: str, executor: MockExecutorFunc) -> None:
        """Register a mock executor for capabilities matching a prefix.

        The executor receives (Capability, params) and returns a dict.
        Only usable during development/testing.
        """
        self._mock_executors[capability_id_prefix] = executor

    def set_default_mock(self, executor: MockExecutorFunc) -> None:
        """Override the default mock executor."""
        self._default_mock = executor

    # ── Internal — the ONLY execution path ───────────────────

    def _invoke_internal(
        self,
        cap: Capability,
        params: dict[str, Any],
        invocation_id: str,
        start_time: float,
    ) -> InvokeResult:
        """Execute a capability after policy has ALLOWed it.

        PRIVATE. Cannot be called from outside the class.
        ALWAYS called after PolicyEngine.evaluate() returns ALLOW.

        This is structurally enforced:
        - _invoke_internal is private (leading underscore)
        - Only invoke_tool() and invoke_tool_approved() call it
        - Both methods ALWAYS call policy_engine.evaluate() first
        """
        # Find the right mock executor
        executor: MockExecutorFunc | None = None
        for prefix, func in self._mock_executors.items():
            if cap.id.startswith(prefix):
                executor = func
                break

        if executor is None:
            executor = self._default_mock

        try:
            output = executor(cap, params)
            return InvokeResult(
                status=InvokeStatus.SUCCESS,
                capability_id=cap.id,
                output=output,
                invocation_id=invocation_id,
                duration_ms=(time.perf_counter() - start_time) * 1000,
            )
        except Exception as e:
            return InvokeResult(
                status=InvokeStatus.EXECUTION_ERROR,
                capability_id=cap.id,
                error=f"Execution error: {e}",
                invocation_id=invocation_id,
                duration_ms=(time.perf_counter() - start_time) * 1000,
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
