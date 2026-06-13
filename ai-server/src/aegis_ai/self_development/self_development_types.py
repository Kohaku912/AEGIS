"""Self-Development types — data structures for sandbox-based self-improvement."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

_SENSITIVE_PATTERNS = [
    re.compile(r"(api[_-]?key|token|password|secret|cookie|auth)[=:]\s*\S+", re.IGNORECASE),
    re.compile(r"Bearer\s+\S+", re.IGNORECASE),
    re.compile(r"sk-[a-zA-Z0-9]{20,}"),
]


def _mask_secrets(text: str) -> str:
    for pat in _SENSITIVE_PATTERNS:
        text = pat.sub("***MASKED***", text)
    return text


class SelfDevStatus(Enum):
    PLANNED = "planned"
    SANDBOX_PREPARING = "sandbox_preparing"
    EDITING = "editing"
    TESTING = "testing"
    VERIFICATION_FAILED = "verification_failed"
    READY_FOR_REVIEW = "ready_for_review"
    APPROVED_FOR_MERGE = "approved_for_merge"
    REJECTED = "rejected"
    MERGED = "merged"
    FAILED = "failed"
    CANCELLED = "cancelled"


class SelfDevSource(Enum):
    USER_EXPLICIT = "user_explicit"
    DESIRE_DRIVEN = "desire_driven"
    REFLECTION_DRIVEN = "reflection_driven"
    SCHEDULED = "scheduled"


class CommandPolicy(Enum):
    ALLOW = "allow"
    ASK_APPROVAL = "ask_approval"
    DENY = "deny"


@dataclass
class SandboxInfo:
    sandbox_id: str = ""
    repo_path: str = ""
    worktree_path: str = ""
    branch_name: str = ""
    base_branch: str = "main"
    created_at: int = 0
    baseline_tests_passed: bool = False
    baseline_test_summary: str = ""
    active: bool = True


@dataclass
class CommandRequest:
    command: str = ""
    args: list[str] = field(default_factory=list)
    working_dir: str = ""
    sandbox_id: str = ""
    timeout_seconds: int = 60
    dry_run: bool = False


@dataclass
class CommandResult:
    command: str = ""
    exit_code: int = -1
    stdout: str = ""
    stderr: str = ""
    policy: CommandPolicy = CommandPolicy.ALLOW
    timed_out: bool = False
    duration_ms: float = 0.0
    masked: bool = False


@dataclass
class SelfDevelopmentTask:
    self_dev_task_id: str = ""
    source: str = "user_explicit"
    title: str = ""
    description: str = ""
    target_repo: str = ""
    target_branch: str = ""
    worktree_path: str = ""
    sandbox_id: str = ""
    related_issue: str = ""
    motivation: str = ""
    source_desire: str = ""
    frustration: float = 0.0
    risk_level: str = "low"
    requires_approval: bool = False
    created_at: int = 0
    status: str = "planned"

    def to_dict(self) -> dict[str, Any]:
        return {
            "self_dev_task_id": self.self_dev_task_id,
            "source": self.source,
            "title": self.title,
            "description": self.description,
            "target_repo": self.target_repo,
            "target_branch": self.target_branch,
            "worktree_path": self.worktree_path,
            "sandbox_id": self.sandbox_id,
            "related_issue": self.related_issue,
            "motivation": self.motivation,
            "source_desire": self.source_desire,
            "frustration": self.frustration,
            "risk_level": self.risk_level,
            "requires_approval": self.requires_approval,
            "created_at": self.created_at,
            "status": self.status,
        }


@dataclass
class SelfDevelopmentResult:
    self_dev_task_id: str = ""
    changed_files: list[str] = field(default_factory=list)
    diff_summary: str = ""
    test_commands: list[str] = field(default_factory=list)
    test_results: list[dict[str, Any]] = field(default_factory=list)
    lint_results: dict[str, Any] = field(default_factory=dict)
    typecheck_results: dict[str, Any] = field(default_factory=dict)
    verification_result: str = ""
    risk_assessment: str = ""
    approval_id: str = ""
    memory_records: list[str] = field(default_factory=list)
    created_at: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "self_dev_task_id": self.self_dev_task_id,
            "changed_files": self.changed_files,
            "diff_summary": _mask_secrets(self.diff_summary[:500]),
            "test_results": self.test_results,
            "lint_results": self.lint_results,
            "typecheck_results": self.typecheck_results,
            "verification_result": self.verification_result,
            "risk_assessment": self.risk_assessment,
            "approval_id": self.approval_id,
            "created_at": self.created_at,
        }


# ── Command allowlists ────────────────────────────────────────────

ALLOWED_COMMANDS: set[str] = {
    "python", "python3", "pytest", "ruff", "mypy", "pyright",
    "npm", "node", "cargo", "git", "ls", "cat", "echo",
    "pip", "uv",
}

ALLOWED_SUBCOMMANDS: set[str] = {
    "-m", "test", "check", "format", "clippy", "status", "diff",
    "log", "branch", "worktree", "add", "commit",
}

DENIED_PATTERNS: list[re.Pattern] = [
    re.compile(r"\brm\s+-rf?\b"),
    re.compile(r"\bdel\s+/[sS]\b"),
    re.compile(r"\bformat\b"),
    re.compile(r"\bshutdown\b"),
    re.compile(r"\breboot\b"),
    re.compile(r"\bsudo\b"),
    re.compile(r"\bchmod\s+-R\b"),
    re.compile(r"\bchown\s+-R\b"),
    re.compile(r"\bgit\s+push\b"),
    re.compile(r"\bgit\s+merge\b"),
    re.compile(r"\bgit\s+rebase\b"),
    re.compile(r"\bgit\s+reset\s+--hard\b"),
    re.compile(r"\bgit\s+clean\s+-fd\b"),
    re.compile(r"\bcurl\s*\|"),
    re.compile(r"\bwget\s*\|"),
    re.compile(r"\bpip\s+install\b"),
    re.compile(r"\bnpm\s+install\b"),
    re.compile(r"\bcargo\s+install\b"),
]

APPROVAL_PATTERNS: list[re.Pattern] = [
    re.compile(r"\bgit\s+checkout\b"),
    re.compile(r"\bgit\s+stash\b"),
    re.compile(r"\bgit\s+cherry-pick\b"),
    re.compile(r"\bnpm\s+run\b"),
]

SECRET_PATH_PATTERNS: list[re.Pattern] = [
    re.compile(r"\.env$"),
    re.compile(r"\.env\."),
    re.compile(r"\.git/config$"),
    re.compile(r"\.ssh/"),
    re.compile(r"\.aws/"),
    re.compile(r"\.gnupg/"),
    re.compile(r"id_rsa"),
    re.compile(r"id_ed25519"),
    re.compile(r"\.pem$"),
    re.compile(r"\.key$"),
]


def classify_command(command: str) -> CommandPolicy:
    for pat in DENIED_PATTERNS:
        if pat.search(command):
            return CommandPolicy.DENY
    for pat in APPROVAL_PATTERNS:
        if pat.search(command):
            return CommandPolicy.ASK_APPROVAL
    return CommandPolicy.ALLOW


def is_secret_path(path: str) -> bool:
    for pat in SECRET_PATH_PATTERNS:
        if pat.search(path):
            return True
    return False
