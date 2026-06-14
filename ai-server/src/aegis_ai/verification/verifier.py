"""Verification Service — post-execution outcome verification.

Verifies that tool executions actually achieved their intended outcomes
by checking real-world state after execution.
"""

from __future__ import annotations

import logging
import time
import uuid
from pathlib import Path
from typing import Any

from aegis_ai.verification.verification_types import (
    VerificationRequest,
    VerificationResult,
    VerificationStatus,
    VerificationStrategy,
)

logger = logging.getLogger("aegis_ai.verification.verifier")


# Strategy selection patterns
_FILE_WRITE_PATTERNS = [
    "write_file", "create_file", "save_file", "create_directory",
    "mkdir", "write_", "save_", "create_",
]

_FILE_DELETE_PATTERNS = [
    "delete_file", "remove_file", "rm_", "unlink", "rmdir",
]

_HTTP_PATTERNS = [
    "http_request", "fetch", "api_call", "web_request", "get_url",
    "post_url", "put_url", "delete_url",
]

_BROWSER_PATTERNS = [
    "browser.navigate", "browser.click", "browser.type", "browser.fill",
    "browser.submit", "browser.goto", "browser.open",
]

_PC_PATTERNS = [
    "pc-server.screenshot", "pc-server.click", "pc-server.type", "pc-server.key", "pc-server.mouse",
    "pc-server.keyboard", "pc-server.screen",
]

_ANDROID_PATTERNS = [
    "android.tap", "android.swipe", "android.type", "android.screenshot",
    "android.screen", "android.ui",
]

_COMMAND_PATTERNS = [
    "run_command", "execute_command", "shell", "exec", "system_command",
    "git.", "npm.", "pip.", "cargo.", "python.",
]


class VerificationService:
    """Verifies tool execution outcomes against real-world state.

    Parameters
    ----------
    audit_log:
        Optional audit log for recording verification results.
    browser_client:
        Optional browser-server client for browser verification.
    pc_client:
        Optional pc-server client for PC verification.
    android_client:
        Optional android-server client for Android verification.
    """

    def __init__(
        self,
        audit_log: Any = None,
        browser_client: Any = None,
        pc_client: Any = None,
        android_client: Any = None,
    ) -> None:
        self._audit = audit_log
        self._browser = browser_client
        self._pc = pc_client
        self._android = android_client

    def build_request(
        self,
        tool_request: Any,
        tool_result: Any,
        pre_observation: dict[str, Any] | None = None,
        post_observation: dict[str, Any] | None = None,
    ) -> VerificationRequest:
        """Build a VerificationRequest from tool execution data."""
        cap_id = getattr(tool_request, "capability_id", "")
        tool_name = getattr(tool_request, "tool_name", "")
        arguments = getattr(tool_request, "arguments", {})
        output = getattr(tool_result, "output", {})

        strategy = self.select_strategy(cap_id, tool_name, arguments)

        return VerificationRequest(
            verification_id=uuid.uuid4().hex[:12],
            request_id=getattr(tool_request, "request_id", ""),
            task_id=getattr(tool_request, "task_id", ""),
            source=getattr(tool_request, "source", "system"),
            capability_id=cap_id,
            tool_name=tool_name,
            arguments=arguments,
            expected_outcome="",
            execution_output=output,
            pre_observation=pre_observation or {},
            post_observation=post_observation or {},
            verification_strategy=strategy,
            created_at=int(time.time() * 1000),
        )

    def select_strategy(
        self,
        capability_id: str,
        tool_name: str,
        arguments: dict[str, Any],
    ) -> VerificationStrategy:
        """Select verification strategy based on capability."""
        cap_lower = capability_id.lower()
        tool_lower = tool_name.lower()

        # File operations
        for pattern in _FILE_DELETE_PATTERNS:
            if pattern in cap_lower or pattern in tool_lower:
                return VerificationStrategy.FILE_NOT_EXISTS

        for pattern in _FILE_WRITE_PATTERNS:
            if pattern in cap_lower or pattern in tool_lower:
                if "path" in arguments or "file_path" in arguments:
                    return VerificationStrategy.FILE_EXISTS
                return VerificationStrategy.NONE

        # HTTP operations
        for pattern in _HTTP_PATTERNS:
            if pattern in cap_lower or pattern in tool_lower:
                return VerificationStrategy.HTTP_STATUS

        # Browser operations
        for pattern in _BROWSER_PATTERNS:
            if pattern in cap_lower:
                if "url" in arguments:
                    return VerificationStrategy.BROWSER_URL
                return VerificationStrategy.BROWSER_DOM

        # PC operations
        for pattern in _PC_PATTERNS:
            if pattern in cap_lower:
                return VerificationStrategy.PC_SCREEN_OBSERVATION

        # Android operations
        for pattern in _ANDROID_PATTERNS:
            if pattern in cap_lower:
                return VerificationStrategy.ANDROID_SCREEN_OBSERVATION

        # Command operations
        for pattern in _COMMAND_PATTERNS:
            if pattern in cap_lower or pattern in tool_lower:
                return VerificationStrategy.COMMAND_EXIT_CODE

        return VerificationStrategy.NONE

    def verify(self, request: VerificationRequest) -> VerificationResult:
        """Execute verification based on the selected strategy."""
        if not request.verification_id:
            request.verification_id = uuid.uuid4().hex[:12]
        if not request.created_at:
            request.created_at = int(time.time() * 1000)

        strategy = request.verification_strategy

        try:
            if strategy == VerificationStrategy.NONE:
                return self._verify_none(request)
            elif strategy == VerificationStrategy.FILE_EXISTS:
                return self._verify_file_exists(request)
            elif strategy == VerificationStrategy.FILE_NOT_EXISTS:
                return self._verify_file_not_exists(request)
            elif strategy == VerificationStrategy.FILE_CONTENT_CONTAINS:
                return self._verify_file_content(request)
            elif strategy == VerificationStrategy.DIRECTORY_EXISTS:
                return self._verify_directory_exists(request)
            elif strategy == VerificationStrategy.HTTP_STATUS:
                return self._verify_http_status(request)
            elif strategy == VerificationStrategy.API_RESPONSE_SCHEMA:
                return self._verify_api_response_schema(request)
            elif strategy == VerificationStrategy.PROCESS_RUNNING:
                return self._verify_process_running(request)
            elif strategy == VerificationStrategy.STATE_DIFF:
                return self._verify_state_diff(request)
            elif strategy == VerificationStrategy.CUSTOM:
                return self._verify_custom(request)
            elif strategy == VerificationStrategy.COMMAND_EXIT_CODE:
                return self._verify_command_exit_code(request)
            elif strategy in (
                VerificationStrategy.BROWSER_URL,
                VerificationStrategy.BROWSER_DOM,
                VerificationStrategy.BROWSER_SCREENSHOT,
            ):
                return self._verify_browser_operation(request)
            elif strategy in (
                VerificationStrategy.PC_SCREEN_OBSERVATION,
                VerificationStrategy.ANDROID_SCREEN_OBSERVATION,
            ):
                return self._verify_screen_observation(request)
            else:
                return self._verify_unverified(request)
        except Exception as exc:
            logger.error("Verification error: %s", exc)
            return VerificationResult(
                verification_id=request.verification_id,
                request_id=request.request_id,
                status=VerificationStatus.ERROR,
                confidence=0.0,
                reason=f"Verification error: {exc}",
                created_at=int(time.time() * 1000),
            )

    def _verify_none(self, request: VerificationRequest) -> VerificationResult:
        """No verification needed — trust executor output."""
        return VerificationResult(
            verification_id=request.verification_id,
            request_id=request.request_id,
            status=VerificationStatus.SKIPPED,
            confidence=1.0,
            reason="No verification strategy — trusted execution.",
            created_at=int(time.time() * 1000),
        )

    def _verify_file_exists(self, request: VerificationRequest) -> VerificationResult:
        """Verify that a file was created/exists."""
        path = (
            request.arguments.get("path")
            or request.arguments.get("file_path")
            or request.execution_output.get("path")
            or request.execution_output.get("file_path")
        )

        if not path:
            return VerificationResult(
                verification_id=request.verification_id,
                request_id=request.request_id,
                status=VerificationStatus.UNVERIFIED,
                confidence=0.3,
                reason="No file path found in arguments or output.",
                created_at=int(time.time() * 1000),
            )

        try:
            p = Path(path)
            if p.exists():
                size = p.stat().st_size if p.is_file() else 0
                return VerificationResult(
                    verification_id=request.verification_id,
                    request_id=request.request_id,
                    status=VerificationStatus.VERIFIED,
                    confidence=0.9,
                    reason=f"File exists: {path} (size={size})",
                    evidence=[f"exists=True, size={size}"],
                    created_at=int(time.time() * 1000),
                )
            else:
                return VerificationResult(
                    verification_id=request.verification_id,
                    request_id=request.request_id,
                    status=VerificationStatus.FAILED,
                    confidence=0.95,
                    reason=f"File does not exist: {path}",
                    failure_type="file_missing",
                    suggested_recovery="Re-attempt file creation or check path validity.",
                    created_at=int(time.time() * 1000),
                )
        except Exception as exc:
            return VerificationResult(
                verification_id=request.verification_id,
                request_id=request.request_id,
                status=VerificationStatus.ERROR,
                confidence=0.0,
                reason=f"File check error: {exc}",
                created_at=int(time.time() * 1000),
            )

    def _verify_file_not_exists(self, request: VerificationRequest) -> VerificationResult:
        """Verify that a file was deleted."""
        path = (
            request.arguments.get("path")
            or request.arguments.get("file_path")
        )

        if not path:
            return VerificationResult(
                verification_id=request.verification_id,
                request_id=request.request_id,
                status=VerificationStatus.UNVERIFIED,
                confidence=0.3,
                reason="No file path found in arguments.",
                created_at=int(time.time() * 1000),
            )

        try:
            p = Path(path)
            if not p.exists():
                return VerificationResult(
                    verification_id=request.verification_id,
                    request_id=request.request_id,
                    status=VerificationStatus.VERIFIED,
                    confidence=0.9,
                    reason=f"File deleted: {path}",
                    evidence=["exists=False"],
                    created_at=int(time.time() * 1000),
                )
            else:
                return VerificationResult(
                    verification_id=request.verification_id,
                    request_id=request.request_id,
                    status=VerificationStatus.FAILED,
                    confidence=0.95,
                    reason=f"File still exists: {path}",
                    failure_type="file_not_deleted",
                    suggested_recovery="Re-attempt deletion or check permissions.",
                    created_at=int(time.time() * 1000),
                )
        except Exception as exc:
            return VerificationResult(
                verification_id=request.verification_id,
                request_id=request.request_id,
                status=VerificationStatus.ERROR,
                confidence=0.0,
                reason=f"File check error: {exc}",
                created_at=int(time.time() * 1000),
            )

    def _verify_file_content(self, request: VerificationRequest) -> VerificationResult:
        """Verify file contains expected content."""
        path = request.arguments.get("path") or request.arguments.get("file_path")
        expected = request.arguments.get("expected_content") or request.expected_outcome

        if not path or not expected:
            return VerificationResult(
                verification_id=request.verification_id,
                request_id=request.request_id,
                status=VerificationStatus.UNVERIFIED,
                confidence=0.3,
                reason="Missing path or expected content.",
                created_at=int(time.time() * 1000),
            )

        try:
            p = Path(path)
            if not p.exists():
                return VerificationResult(
                    verification_id=request.verification_id,
                    request_id=request.request_id,
                    status=VerificationStatus.FAILED,
                    confidence=0.95,
                    reason=f"File does not exist: {path}",
                    failure_type="file_missing",
                    created_at=int(time.time() * 1000),
                )

            content = p.read_text(encoding="utf-8", errors="replace")
            if expected in content:
                return VerificationResult(
                    verification_id=request.verification_id,
                    request_id=request.request_id,
                    status=VerificationStatus.VERIFIED,
                    confidence=0.85,
                    reason="File contains expected content.",
                    evidence=[f"content_length={len(content)}"],
                    created_at=int(time.time() * 1000),
                )
            else:
                return VerificationResult(
                    verification_id=request.verification_id,
                    request_id=request.request_id,
                    status=VerificationStatus.FAILED,
                    confidence=0.8,
                    reason="File does not contain expected content.",
                    failure_type="content_mismatch",
                    created_at=int(time.time() * 1000),
                )
        except Exception as exc:
            return VerificationResult(
                verification_id=request.verification_id,
                request_id=request.request_id,
                status=VerificationStatus.ERROR,
                confidence=0.0,
                reason=f"Content check error: {exc}",
                created_at=int(time.time() * 1000),
            )

    def _verify_directory_exists(self, request: VerificationRequest) -> VerificationResult:
        """Verify that a directory was created."""
        path = request.arguments.get("path") or request.arguments.get("dir_path")

        if not path:
            return VerificationResult(
                verification_id=request.verification_id,
                request_id=request.request_id,
                status=VerificationStatus.UNVERIFIED,
                confidence=0.3,
                reason="No directory path found.",
                created_at=int(time.time() * 1000),
            )

        try:
            p = Path(path)
            if p.exists() and p.is_dir():
                return VerificationResult(
                    verification_id=request.verification_id,
                    request_id=request.request_id,
                    status=VerificationStatus.VERIFIED,
                    confidence=0.9,
                    reason=f"Directory exists: {path}",
                    evidence=["is_dir=True"],
                    created_at=int(time.time() * 1000),
                )
            else:
                return VerificationResult(
                    verification_id=request.verification_id,
                    request_id=request.request_id,
                    status=VerificationStatus.FAILED,
                    confidence=0.95,
                    reason=f"Directory does not exist: {path}",
                    failure_type="directory_missing",
                    created_at=int(time.time() * 1000),
                )
        except Exception as exc:
            return VerificationResult(
                verification_id=request.verification_id,
                request_id=request.request_id,
                status=VerificationStatus.ERROR,
                confidence=0.0,
                reason=f"Directory check error: {exc}",
                created_at=int(time.time() * 1000),
            )

    def _verify_http_status(self, request: VerificationRequest) -> VerificationResult:
        """Verify HTTP response status."""
        output = request.execution_output
        status_code = output.get("status_code") or output.get("code") or output.get("status")

        if status_code is None:
            return VerificationResult(
                verification_id=request.verification_id,
                request_id=request.request_id,
                status=VerificationStatus.UNVERIFIED,
                confidence=0.3,
                reason="No HTTP status code in output.",
                created_at=int(time.time() * 1000),
            )

        try:
            code = int(status_code)
            if 200 <= code < 400:
                return VerificationResult(
                    verification_id=request.verification_id,
                    request_id=request.request_id,
                    status=VerificationStatus.VERIFIED,
                    confidence=0.85,
                    reason=f"HTTP status {code} (success).",
                    evidence=[f"status_code={code}"],
                    created_at=int(time.time() * 1000),
                )
            elif 400 <= code < 500:
                return VerificationResult(
                    verification_id=request.verification_id,
                    request_id=request.request_id,
                    status=VerificationStatus.FAILED,
                    confidence=0.9,
                    reason=f"HTTP status {code} (client error).",
                    failure_type="client_error",
                    suggested_recovery="Check request parameters.",
                    created_at=int(time.time() * 1000),
                )
            else:
                return VerificationResult(
                    verification_id=request.verification_id,
                    request_id=request.request_id,
                    status=VerificationStatus.FAILED,
                    confidence=0.9,
                    reason=f"HTTP status {code} (server error).",
                    failure_type="server_error",
                    suggested_recovery="Server error — may be retryable.",
                    created_at=int(time.time() * 1000),
                )
        except (ValueError, TypeError):
            return VerificationResult(
                verification_id=request.verification_id,
                request_id=request.request_id,
                status=VerificationStatus.UNVERIFIED,
                confidence=0.2,
                reason=f"Invalid status code: {status_code}",
                created_at=int(time.time() * 1000),
            )

    def _verify_command_exit_code(self, request: VerificationRequest) -> VerificationResult:
        """Verify command execution exit code."""
        output = request.execution_output
        exit_code = output.get("exit_code", output.get("returncode", output.get("return_code")))

        if exit_code is None:
            return VerificationResult(
                verification_id=request.verification_id,
                request_id=request.request_id,
                status=VerificationStatus.UNVERIFIED,
                confidence=0.3,
                reason="No exit code in output.",
                created_at=int(time.time() * 1000),
            )

        try:
            code = int(exit_code)
            if code == 0:
                return VerificationResult(
                    verification_id=request.verification_id,
                    request_id=request.request_id,
                    status=VerificationStatus.VERIFIED,
                    confidence=0.8,
                    reason="Command exited with code 0 (success).",
                    evidence=[f"exit_code={code}"],
                    created_at=int(time.time() * 1000),
                )
            else:
                stderr = output.get("stderr", "")[:200]
                return VerificationResult(
                    verification_id=request.verification_id,
                    request_id=request.request_id,
                    status=VerificationStatus.FAILED,
                    confidence=0.9,
                    reason=f"Command exited with code {code}. stderr={stderr}",
                    failure_type="command_failed",
                    suggested_recovery="Check command output for errors.",
                    created_at=int(time.time() * 1000),
                )
        except (ValueError, TypeError):
            return VerificationResult(
                verification_id=request.verification_id,
                request_id=request.request_id,
                status=VerificationStatus.UNVERIFIED,
                confidence=0.2,
                reason=f"Invalid exit code: {exit_code}",
                created_at=int(time.time() * 1000),
            )

    def _verify_browser_operation(self, request: VerificationRequest) -> VerificationResult:
        """Verify browser operation — requires browser client."""
        if self._browser is None:
            return VerificationResult(
                verification_id=request.verification_id,
                request_id=request.request_id,
                status=VerificationStatus.REQUIRES_OBSERVATION,
                confidence=0.0,
                reason="Browser client not available — requires manual observation.",
                suggested_recovery="Check browser state manually or connect browser-server.",
                created_at=int(time.time() * 1000),
            )

        # If browser client exists, try to get current state
        try:
            if hasattr(self._browser, "get_current_url"):
                current_url = self._browser.get_current_url()
                expected_url = request.arguments.get("url", "")
                if expected_url and expected_url in str(current_url):
                    return VerificationResult(
                        verification_id=request.verification_id,
                        request_id=request.request_id,
                        status=VerificationStatus.VERIFIED,
                        confidence=0.7,
                        reason=f"Browser URL matches: {current_url}",
                        evidence=[f"url={current_url}"],
                        created_at=int(time.time() * 1000),
                    )

            return VerificationResult(
                verification_id=request.verification_id,
                request_id=request.request_id,
                status=VerificationStatus.REQUIRES_OBSERVATION,
                confidence=0.3,
                reason="Browser state unclear — requires observation.",
                created_at=int(time.time() * 1000),
            )
        except Exception as exc:
            return VerificationResult(
                verification_id=request.verification_id,
                request_id=request.request_id,
                status=VerificationStatus.REQUIRES_OBSERVATION,
                confidence=0.0,
                reason=f"Browser check error: {exc}",
                created_at=int(time.time() * 1000),
            )

    def _verify_screen_observation(self, request: VerificationRequest) -> VerificationResult:
        """Verify PC/Android operation — requires screen observation."""
        return VerificationResult(
            verification_id=request.verification_id,
            request_id=request.request_id,
            status=VerificationStatus.REQUIRES_OBSERVATION,
            confidence=0.0,
            reason="Screen observation required — cannot verify automatically.",
            suggested_recovery="Take screenshot and verify visually, or connect pc/android server.",
            created_at=int(time.time() * 1000),
        )

    def _verify_unverified(self, request: VerificationRequest) -> VerificationResult:
        """Unknown strategy — mark as unverified."""
        return VerificationResult(
            verification_id=request.verification_id,
            request_id=request.request_id,
            status=VerificationStatus.UNVERIFIED,
            confidence=0.0,
            reason=f"Unknown verification strategy: {request.verification_strategy.value}",
            created_at=int(time.time() * 1000),
        )

    def _verify_api_response_schema(self, request: VerificationRequest) -> VerificationResult:
        """Verify API response has expected structure."""
        output = request.execution_output
        expected_keys = request.arguments.get("expected_keys", [])
        error_keys = {"error", "errors", "message", "detail"}

        status_code = output.get("status_code", output.get("code", 0))
        if 400 <= status_code < 600:
            return VerificationResult(
                verification_id=request.verification_id,
                request_id=request.request_id,
                status=VerificationStatus.FAILED,
                confidence=0.9,
                reason=f"HTTP {status_code} error response.",
                failure_type="api_error",
                created_at=int(time.time() * 1000),
            )

        has_error = any(k in output for k in error_keys) and output.get("error")
        if has_error:
            return VerificationResult(
                verification_id=request.verification_id,
                request_id=request.request_id,
                status=VerificationStatus.FAILED,
                confidence=0.8,
                reason="Response contains error field.",
                failure_type="api_error_in_body",
                created_at=int(time.time() * 1000),
            )

        if expected_keys and not all(k in output for k in expected_keys):
            missing = [k for k in expected_keys if k not in output]
            return VerificationResult(
                verification_id=request.verification_id,
                request_id=request.request_id,
                status=VerificationStatus.FAILED,
                confidence=0.7,
                reason=f"Missing expected keys: {missing}",
                failure_type="schema_mismatch",
                created_at=int(time.time() * 1000),
            )

        return VerificationResult(
            verification_id=request.verification_id,
            request_id=request.request_id,
            status=VerificationStatus.VERIFIED,
            confidence=0.8,
            reason="API response structure OK.",
            evidence=[f"keys={list(output.keys())[:10]}"],
            created_at=int(time.time() * 1000),
        )

    def _verify_process_running(self, request: VerificationRequest) -> VerificationResult:
        """Verify a process is running — requires observation hook."""
        return VerificationResult(
            verification_id=request.verification_id,
            request_id=request.request_id,
            status=VerificationStatus.REQUIRES_OBSERVATION,
            confidence=0.0,
            reason="Process state requires OS-level observation.",
            suggested_recovery="Check process list via pc-server or shell command.",
            created_at=int(time.time() * 1000),
        )

    def _verify_state_diff(self, request: VerificationRequest) -> VerificationResult:
        """Verify state changed between pre and post observation."""
        pre = request.pre_observation
        post = request.post_observation
        if not pre or not post:
            return VerificationResult(
                verification_id=request.verification_id,
                request_id=request.request_id,
                status=VerificationStatus.REQUIRES_OBSERVATION,
                confidence=0.0,
                reason="Pre/post observation required for state diff.",
                suggested_recovery="Collect pre and post observations around the operation.",
                created_at=int(time.time() * 1000),
            )

        changed_keys = [k for k in post if k in pre and post[k] != pre[k]]
        if changed_keys:
            return VerificationResult(
                verification_id=request.verification_id,
                request_id=request.request_id,
                status=VerificationStatus.VERIFIED,
                confidence=0.7,
                reason=f"State changed in keys: {changed_keys[:5]}",
                evidence=[f"changed={changed_keys[:5]}"],
                created_at=int(time.time() * 1000),
            )

        return VerificationResult(
            verification_id=request.verification_id,
            request_id=request.request_id,
            status=VerificationStatus.FAILED,
            confidence=0.6,
            reason="No state change detected between pre and post observation.",
            failure_type="no_state_change",
            created_at=int(time.time() * 1000),
        )

    def _verify_custom(self, request: VerificationRequest) -> VerificationResult:
        """Custom verification — falls back to unverified."""
        return VerificationResult(
            verification_id=request.verification_id,
            request_id=request.request_id,
            status=VerificationStatus.UNVERIFIED,
            confidence=0.0,
            reason="Custom verification requires a verifier callback.",
            suggested_recovery="Provide a custom verification function.",
            created_at=int(time.time() * 1000),
        )

    def record_verification(
        self,
        request: VerificationRequest,
        result: VerificationResult,
    ) -> None:
        """Record verification result to audit log."""
        if self._audit is None:
            return

        try:
            from audit import AuditEntry

            entry = AuditEntry(
                action="verification",
                actor=request.source or "system",
                capability_id=request.capability_id,
                decision=result.status.value,
                reason=result.reason,
                detail={
                    "verification_id": result.verification_id,
                    "request_id": request.request_id,
                    "task_id": request.task_id,
                    "capability_id": request.capability_id,
                    "strategy": request.verification_strategy.value,
                    "status": result.status.value,
                    "confidence": result.confidence,
                    "failure_type": result.failure_type,
                    "suggested_recovery": result.suggested_recovery,
                    "evidence_count": len(result.evidence),
                },
            )
            self._audit.append(entry)
        except Exception as exc:
            logger.warning("Failed to record verification: %s", exc)
