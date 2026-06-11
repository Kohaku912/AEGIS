"""Dev Server Client — Python adapter for Dev Server integration with AEGIS Core.

This module provides sandboxed self-development capabilities:
- Repository observation (status, diff, file read, code search)
- Branch creation and patch application
- Test and lint execution (auto-detect language)
- Commit and PR creation (with approval)
- Revert/rollback

Safety constraints (per architecture §8.3):
- No direct push/merge to main
- No access to secrets
- No production deploy
- No system package install
- No Docker socket access
- All operations audited
- User is the only merge authority

Sandbox: Workspace directory isolation (OpenHands/SWE-agent inspired).
Language detection: auto-detect Python, Kotlin, TypeScript, etc.

Architecture reference: docs/architecture.md §3.6, §8
"""

from __future__ import annotations

import json
import logging
import time
import uuid
from dataclasses import dataclass
from enum import Enum, auto
from pathlib import Path
from typing import Any, Protocol

from aegis_schema.models import (
    Capability,
    Event,
    EventPriority,
    RiskLevel,
    ServerInfo,
    ServerStatus,
    ServerType,
)

logger = logging.getLogger("aegis.dev_server_client")


# ═══════════════════════════════════════════════════════════════
# Language Detection — auto-detect project type for test/lint
# ═══════════════════════════════════════════════════════════════

LANGUAGE_INDICATORS: dict[str, list[str]] = {
    "python": ["pyproject.toml", "setup.py", "setup.cfg", "requirements.txt", "Pipfile"],
    "kotlin": ["build.gradle.kts", "build.gradle", "settings.gradle.kts"],
    "typescript": ["tsconfig.json", "package.json"],
    "javascript": ["package.json"],
    "rust": ["Cargo.toml"],
}

TEST_COMMANDS: dict[str, list[str]] = {
    "python": ["python", "-m", "pytest", "--tb=short", "-q"],
    "kotlin": ["./gradlew", "test"],
    "typescript": ["npm", "test"],
    "javascript": ["npm", "test"],
    "rust": ["cargo", "test"],
}

LINT_COMMANDS: dict[str, list[str]] = {
    "python": ["python", "-m", "ruff", "check", "."],
    "kotlin": ["./gradlew", "ktlintCheck"],
    "typescript": ["npx", "eslint", "."],
    "javascript": ["npx", "eslint", "."],
    "rust": ["cargo", "clippy", "--", "-D", "warnings"],
}


def detect_language(workspace: str) -> str:
    """Detect the primary language of a project by indicator files."""
    ws = Path(workspace)
    for lang, indicators in LANGUAGE_INDICATORS.items():
        for indicator in indicators:
            if (ws / indicator).exists():
                return lang
    return "unknown"


# ═══════════════════════════════════════════════════════════════
# Safety — path denylist for file operations
# ═══════════════════════════════════════════════════════════════

DENYLIST_FILE_PATTERNS: set[str] = {
    ".env",
    ".env.local",
    ".env.production",
    "credentials.json",
    "credentials.xml",
    ".pem",
    ".key",
    ".crt",
    ".p12",
    "id_rsa",
    "id_ed25519",
    "id_ecdsa",
    "token",
    "secret",
    "password",
}


def is_path_denied(path: str) -> bool:
    """Check if a file path is denied by safety rules."""
    name_lower = Path(path).name.lower()
    for pattern in DENYLIST_FILE_PATTERNS:
        if pattern in name_lower:
            return True
    return False


# ═══════════════════════════════════════════════════════════════
# Provider Protocol — abstracts sandbox operations
# ═══════════════════════════════════════════════════════════════


class DevProvider(Protocol):
    """Protocol for dev server providers."""

    def get_repo_status(self) -> dict[str, Any]:
        """Get git repository status. Returns {branch, commit_hash, is_clean, ...}."""
        ...

    def get_diff(self, from_branch: str = "", to_branch: str = "") -> dict[str, Any]:
        """Get diff between branches. Returns {files: [...]}."""
        ...

    def read_file(self, path: str) -> dict[str, Any]:
        """Read a file from the workspace. Returns {content, size_bytes, path}."""
        ...

    def search_code(self, query: str, include_pattern: str = "") -> dict[str, Any]:
        """Search code in the workspace. Returns {matches: [...]}."""
        ...

    def create_branch(self, branch_name: str, base_branch: str = "main") -> dict[str, Any]:
        """Create a new branch. Returns {success, branch_name}."""
        ...

    def apply_patch(self, file_path: str, patch_content: str) -> dict[str, Any]:
        """Apply a unified diff patch. Returns {success, applied, error_detail}."""
        ...

    def run_tests(self, target: str = "", extra_args: str = "") -> dict[str, Any]:
        """Run tests. Returns {success, total, passed, failed, output}."""
        ...

    def run_lint(self, target: str = "", linter: str = "") -> dict[str, Any]:
        """Run linter. Returns {success, passed, error_count, output}."""
        ...

    def create_commit(self, message: str, files: list[str] | None = None) -> dict[str, Any]:
        """Create a git commit. Returns {success, commit_hash}."""
        ...

    def create_pull_request(
        self,
        title: str,
        description: str,
        head_branch: str,
        base_branch: str = "main",
    ) -> dict[str, Any]:
        """Create a pull request. Returns {success, pr_url, pr_number}."""
        ...

    def revert_changes(self, target: str = "all", commit_hash: str = "") -> dict[str, Any]:
        """Revert changes. Returns {success, reverted_files}."""
        ...

    def is_available(self) -> bool:
        """Check if the dev server / workspace is reachable."""
        ...


# ═══════════════════════════════════════════════════════════════
# Mock Dev Provider — for CI testing (no real git/test/lint)
# ═══════════════════════════════════════════════════════════════


class MockDevProvider:
    """Mock dev provider for CI testing. Returns deterministic fake data."""

    def __init__(self, available: bool = True) -> None:
        self._available = available
        self.call_log: list[tuple[str, dict[str, Any]]] = []
        self._branch = "main"
        self._commit_hash = "abc1234"
        self._is_clean = True
        self._modified_files: list[str] = []
        self._files: dict[str, str] = {}
        self._test_pass = True

    def set_mock_state(
        self,
        branch: str | None = None,
        is_clean: bool | None = None,
        modified_files: list[str] | None = None,
        test_pass: bool | None = None,
    ) -> None:
        if branch is not None:
            self._branch = branch
        if is_clean is not None:
            self._is_clean = is_clean
        if modified_files is not None:
            self._modified_files = modified_files
        if test_pass is not None:
            self._test_pass = test_pass

    def get_repo_status(self) -> dict[str, Any]:
        self.call_log.append(("get_repo_status", {}))
        return {
            "branch": self._branch,
            "commit_hash": self._commit_hash,
            "is_clean": self._is_clean,
            "modified_files": list(self._modified_files),
            "ahead_commits": 0,
            "behind_commits": 0,
        }

    def get_diff(self, from_branch: str = "", to_branch: str = "") -> dict[str, Any]:
        self.call_log.append(("get_diff", {"from_branch": from_branch, "to_branch": to_branch}))
        return {
            "files": [
                {
                    "path": f,
                    "status": "modified",
                    "diff": f"--- a/{f}\n+++ b/{f}\n@@ -1 +1 @@\n-old\n+new",
                    "additions": 1,
                    "deletions": 1,
                }
                for f in self._modified_files
            ]
        }

    def read_file(self, path: str) -> dict[str, Any]:
        self.call_log.append(("read_file", {"path": path}))
        if is_path_denied(path):
            return {"error": f"Path '{path}' is denied by safety rules", "path": path}
        content = self._files.get(path, f"[MOCK_FILE_CONTENT:{path}]")
        return {"success": True, "content": content, "size_bytes": len(content), "path": path}

    def search_code(self, query: str, include_pattern: str = "") -> dict[str, Any]:
        self.call_log.append(("search_code", {"query": query, "include_pattern": include_pattern}))
        return {
            "matches": [
                {"file": "src/example.py", "line": 10, "text": f"# {query} found here"},
            ]
        }

    def create_branch(self, branch_name: str, base_branch: str = "main") -> dict[str, Any]:
        self.call_log.append(("create_branch", {"branch_name": branch_name, "base_branch": base_branch}))
        self._branch = branch_name
        return {"success": True, "branch_name": branch_name}

    def apply_patch(self, file_path: str, patch_content: str) -> dict[str, Any]:
        self.call_log.append(("apply_patch", {"file_path": file_path, "patch_len": len(patch_content)}))
        return {"success": True, "applied": True, "error_detail": ""}

    def run_tests(self, target: str = "", extra_args: str = "") -> dict[str, Any]:
        self.call_log.append(("run_tests", {"target": target, "extra_args": extra_args}))
        if self._test_pass:
            return {
                "success": True,
                "total": 100,
                "passed": 100,
                "failed": 0,
                "errors": 0,
                "duration_sec": 1.5,
                "output": "100 passed",
            }
        return {
            "success": False,
            "total": 100,
            "passed": 98,
            "failed": 2,
            "errors": 0,
            "duration_sec": 1.5,
            "output": "FAILED tests/test_example.py::test_foo",
        }

    def run_lint(self, target: str = "", linter: str = "") -> dict[str, Any]:
        self.call_log.append(("run_lint", {"target": target, "linter": linter}))
        return {"success": True, "passed": True, "error_count": 0, "warning_count": 0, "output": "All checks passed!"}

    def create_commit(self, message: str, files: list[str] | None = None) -> dict[str, Any]:
        self.call_log.append(("create_commit", {"message": message, "files": files}))
        self._commit_hash = f"commit_{uuid.uuid4().hex[:7]}"
        self._is_clean = True
        return {"success": True, "commit_hash": self._commit_hash}

    def create_pull_request(
        self,
        title: str,
        description: str,
        head_branch: str,
        base_branch: str = "main",
    ) -> dict[str, Any]:
        self.call_log.append(
            (
                "create_pull_request",
                {
                    "title": title,
                    "description": description,
                    "head_branch": head_branch,
                    "base_branch": base_branch,
                },
            )
        )
        pr_number = 42
        return {
            "success": True,
            "pr_url": f"https://github.com/Kohaku912/AEGIS/pull/{pr_number}",
            "pr_number": pr_number,
        }

    def revert_changes(self, target: str = "all", commit_hash: str = "") -> dict[str, Any]:
        self.call_log.append(("revert_changes", {"target": target, "commit_hash": commit_hash}))
        self._is_clean = True
        return {"success": True, "reverted_files": list(self._modified_files)}

    def is_available(self) -> bool:
        return self._available


# ═══════════════════════════════════════════════════════════════
# Connection State & Retry
# ═══════════════════════════════════════════════════════════════


class ConnectionState(Enum):
    DISCONNECTED = auto()
    CONNECTING = auto()
    CONNECTED = auto()
    FAILED = auto()


@dataclass
class RetryConfig:
    max_retries: int = 5
    base_delay_ms: int = 100
    max_delay_ms: int = 30_000
    backoff_factor: float = 2.0


@dataclass
class ConnectionStats:
    state: ConnectionState = ConnectionState.DISCONNECTED
    retry_count: int = 0
    last_error: str = ""
    last_connected_at_ms: int = 0
    last_attempt_at_ms: int = 0
    total_registrations: int = 0
    total_events_pushed: int = 0


# ═══════════════════════════════════════════════════════════════
# Dev Server Capabilities — static definitions
# ═══════════════════════════════════════════════════════════════

DEV_SERVER_ID = "dev-server-main"

DEV_CAPABILITIES: list[Capability] = [
    # ── Observe (Level 0) ──
    Capability(
        id="dev.get_repo_status",
        name="Get Repo Status",
        description="Get current git repository status (branch, commit, modified files).",
        server_type=ServerType.DEV,
        risk_level=RiskLevel.READ_ONLY,
        tags=["git", "observe", "read_only"],
        timeout_ms=3000,
    ),
    Capability(
        id="dev.get_diff",
        name="Get Diff",
        description="Get diff between branches or working tree.",
        server_type=ServerType.DEV,
        risk_level=RiskLevel.READ_ONLY,
        tags=["git", "observe", "read_only"],
        timeout_ms=5000,
    ),
    Capability(
        id="dev.read_file",
        name="Read File",
        description="Read a file from the workspace. Denied for secrets.",
        server_type=ServerType.DEV,
        risk_level=RiskLevel.READ_ONLY,
        tags=["file", "observe", "read_only"],
        timeout_ms=2000,
    ),
    Capability(
        id="dev.search_code",
        name="Search Code",
        description="Search code in the workspace by pattern.",
        server_type=ServerType.DEV,
        risk_level=RiskLevel.READ_ONLY,
        tags=["search", "observe", "read_only"],
        timeout_ms=5000,
    ),
    # ── Action Level 1 ──
    Capability(
        id="dev.create_branch",
        name="Create Branch",
        description="Create a new git branch from base branch.",
        server_type=ServerType.DEV,
        risk_level=RiskLevel.SAFE_ACTION,
        tags=["git", "action"],
        timeout_ms=3000,
    ),
    Capability(
        id="dev.run_tests",
        name="Run Tests",
        description="Run test suite (auto-detect language). Returns pass/fail counts.",
        server_type=ServerType.DEV,
        risk_level=RiskLevel.SAFE_ACTION,
        tags=["test", "action"],
        timeout_ms=300000,
    ),
    Capability(
        id="dev.run_lint",
        name="Run Lint",
        description="Run linter (auto-detect language). Returns error/warning counts.",
        server_type=ServerType.DEV,
        risk_level=RiskLevel.SAFE_ACTION,
        tags=["lint", "action"],
        timeout_ms=60000,
    ),
    # ── Action Level 2 (approval required) ──
    Capability(
        id="dev.apply_patch",
        name="Apply Patch",
        description="Apply a unified diff patch to a file. Requires approval.",
        server_type=ServerType.DEV,
        risk_level=RiskLevel.APPROVAL_REQUIRED,
        requires_approval=True,
        side_effects=["file_modification"],
        tags=["patch", "action", "approval_required"],
        timeout_ms=10000,
    ),
    Capability(
        id="dev.create_commit",
        name="Create Commit",
        description="Create a git commit with message. Requires approval.",
        server_type=ServerType.DEV,
        risk_level=RiskLevel.APPROVAL_REQUIRED,
        requires_approval=True,
        side_effects=["git_commit"],
        tags=["git", "action", "approval_required"],
        timeout_ms=10000,
    ),
    Capability(
        id="dev.create_pull_request",
        name="Create Pull Request",
        description="Create a GitHub pull request. Requires approval and GITHUB_TOKEN.",
        server_type=ServerType.DEV,
        risk_level=RiskLevel.APPROVAL_REQUIRED,
        requires_approval=True,
        side_effects=["github_pr"],
        tags=["github", "action", "approval_required"],
        timeout_ms=30000,
    ),
    Capability(
        id="dev.revert_changes",
        name="Revert Changes",
        description="Revert uncommitted changes or a specific commit. Requires approval.",
        server_type=ServerType.DEV,
        risk_level=RiskLevel.APPROVAL_REQUIRED,
        requires_approval=True,
        side_effects=["git_revert"],
        tags=["git", "action", "approval_required"],
        timeout_ms=10000,
    ),
]


def get_dev_server_info() -> ServerInfo:
    """Create ServerInfo for the Dev Server."""
    return ServerInfo(
        server_id=DEV_SERVER_ID,
        server_type=ServerType.DEV,
        version="0.1.0",
        status=ServerStatus.ONLINE,
        capability_ids=[cap.id for cap in DEV_CAPABILITIES],
        host="localhost",
        port=50055,
        started_at_ms=int(time.time() * 1000),
    )


# ═══════════════════════════════════════════════════════════════
# Dev Server Client — main integration point
# ═══════════════════════════════════════════════════════════════


class DevServerClient:
    """Python client that integrates Dev Server with AEGIS Core.

    Responsibilities:
    1. Register Dev capabilities with ToolRegistry
    2. Push Dev events to EventBus
    3. Handle connection state and retry/backoff
    4. Invoke capabilities through ToolBroker (with PolicyEngine enforcement)
    5. Push action result events to EventBus
    6. Language auto-detection for test/lint
    7. File path safety checks
    """

    def __init__(
        self,
        event_bus: Any,
        registry: Any,
        provider: DevProvider | None = None,
        retry_config: RetryConfig | None = None,
        tool_broker: Any = None,
    ) -> None:
        self._event_bus = event_bus
        self._registry = registry
        self._provider = provider or MockDevProvider()
        self._retry = retry_config or RetryConfig()
        self._stats = ConnectionStats()
        self._registered = False
        self._tool_broker = tool_broker

    @property
    def stats(self) -> ConnectionStats:
        return self._stats

    @property
    def is_registered(self) -> bool:
        return self._registered

    @property
    def provider(self) -> Any:
        return self._provider

    # ── Registration ─────────────────────────────────────────

    def register(self) -> bool:
        """Register Dev Server and its capabilities with AEGIS Core."""
        if not self._provider.is_available():
            self._stats.state = ConnectionState.FAILED
            self._stats.last_error = "Dev Server is not available"
            logger.warning("Dev Server not available — skipping registration")
            return False

        try:
            server_info = get_dev_server_info()
            self._registry.register_server(server_info)
            for cap in DEV_CAPABILITIES:
                self._registry.register_capability(cap)

            self._registered = True
            self._stats.state = ConnectionState.CONNECTED
            self._stats.total_registrations = len(DEV_CAPABILITIES)
            self._stats.last_connected_at_ms = int(time.time() * 1000)
            logger.info("Dev Server registered %d capabilities", len(DEV_CAPABILITIES))
            return True

        except Exception as e:
            self._stats.state = ConnectionState.FAILED
            self._stats.last_error = str(e)
            logger.error("Dev Server registration failed: %s", e)
            return False

    def unregister(self) -> None:
        """Unregister Dev Server from AEGIS Core."""
        self._registry.unregister_server(DEV_SERVER_ID)
        for cap in DEV_CAPABILITIES:
            self._registry.unregister_capability(cap.id)
        self._registered = False
        self._stats.state = ConnectionState.DISCONNECTED

    # ── Event Push ───────────────────────────────────────────

    def push_event(self, event: Event) -> bool:
        """Push an event to the EventBus."""
        if not self._registered:
            logger.warning("Cannot push event — Dev Server not registered")
            return False
        try:
            result = self._event_bus.publish(event)
            if result:
                self._stats.total_events_pushed += 1
            return result
        except Exception as e:
            self._stats.last_error = str(e)
            logger.error("Failed to push event: %s", e)
            return False

    def push_action_result_event(
        self,
        capability_id: str,
        success: bool,
        output: dict[str, Any] | None = None,
        error: str = "",
        *,
        severity: int = 2,
        priority: EventPriority = EventPriority.NORMAL,
    ) -> bool:
        """Push a dev.action_completed or dev.action_failed event."""
        event_type = "dev.action_completed" if success else "dev.action_failed"
        payload = json.dumps(
            {
                "capability_id": capability_id,
                "success": success,
                "output": output or {},
                "error": error,
                "timestamp_ms": int(time.time() * 1000),
            }
        )
        event = Event(
            event_id=f"evt_{uuid.uuid4().hex[:8]}",
            event_type=event_type,
            source_server_type=ServerType.DEV,
            source_server_id=DEV_SERVER_ID,
            timestamp_ms=int(time.time() * 1000),
            payload_json=payload,
            severity=severity,
            priority=priority,
            dedupe_key=f"{event_type}:{capability_id}:{success}",
        )
        return self.push_event(event)

    # ── Capability Invocation ────────────────────────────────

    def invoke_capability(self, capability_id: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        """Invoke a Dev capability via the provider (for testing)."""
        if not self._provider.is_available():
            return {"error": "Dev Server is not available", "capability_id": capability_id}

        params = params or {}
        try:
            # ── Observe ──
            if capability_id == "dev.get_repo_status":
                return self._provider.get_repo_status()
            elif capability_id == "dev.get_diff":
                return self._provider.get_diff(params.get("from_branch", ""), params.get("to_branch", ""))
            elif capability_id == "dev.read_file":
                path = params.get("path", "")
                if is_path_denied(path):
                    return {"error": f"Path '{path}' is denied by safety rules", "path": path}
                return self._provider.read_file(path)
            elif capability_id == "dev.search_code":
                return self._provider.search_code(params.get("query", ""), params.get("include_pattern", ""))

            # ── Branch & Patch ──
            elif capability_id == "dev.create_branch":
                return self._provider.create_branch(params["branch_name"], params.get("base_branch", "main"))
            elif capability_id == "dev.apply_patch":
                return self._provider.apply_patch(params["file_path"], params["patch_content"])

            # ── Test & Lint ──
            elif capability_id == "dev.run_tests":
                return self._provider.run_tests(params.get("target", ""), params.get("extra_args", ""))
            elif capability_id == "dev.run_lint":
                return self._provider.run_lint(params.get("target", ""), params.get("linter", ""))

            # ── Commit & PR ──
            elif capability_id == "dev.create_commit":
                return self._provider.create_commit(params["message"], params.get("files"))
            elif capability_id == "dev.create_pull_request":
                return self._provider.create_pull_request(
                    params["title"],
                    params["description"],
                    params["head_branch"],
                    params.get("base_branch", "main"),
                )
            elif capability_id == "dev.revert_changes":
                return self._provider.revert_changes(params.get("target", "all"), params.get("commit_hash", ""))

            else:
                return {"error": f"Unknown capability: {capability_id}"}
        except KeyError as e:
            return {"error": f"Missing required parameter: {e}", "capability_id": capability_id}
        except Exception as e:
            return {"error": str(e), "capability_id": capability_id}

    # ── Retry / Backoff ──────────────────────────────────────

    def connect_with_retry(self) -> bool:
        """Attempt to connect to Dev Server with exponential backoff."""
        delay_ms = self._retry.base_delay_ms
        for attempt in range(self._retry.max_retries):
            self._stats.retry_count = attempt + 1
            self._stats.last_attempt_at_ms = int(time.time() * 1000)
            self._stats.state = ConnectionState.CONNECTING
            if self._provider.is_available():
                if self.register():
                    return True
            time.sleep(delay_ms / 1000.0)
            delay_ms = min(delay_ms * self._retry.backoff_factor, self._retry.max_delay_ms)
        self._stats.state = ConnectionState.FAILED
        self._stats.last_error = f"Failed to connect after {self._retry.max_retries} attempts"
        return False
