"""Sandbox Manager — manages isolated git worktrees for self-development."""

from __future__ import annotations

import json
import logging
import subprocess
import time
import uuid
from pathlib import Path

from aegis_ai.self_development.self_development_types import (
    CommandPolicy,
    CommandResult,
    SandboxInfo,
    _mask_secrets,
    classify_command,
    is_secret_path,
)

logger = logging.getLogger("aegis_ai.self_development.sandbox_manager")

_MAX_STDOUT_LEN = 5000
_MAX_STDERR_LEN = 2000


class SandboxManager:
    """Manages isolated git worktrees for safe self-development.

    Parameters
    ----------
    base_dir:
        Root directory for sandbox worktrees.
    """

    def __init__(self, base_dir: str = "data/sandboxes") -> None:
        self._base_dir = Path(base_dir)
        self._base_dir.mkdir(parents=True, exist_ok=True)
        self._sandboxes: dict[str, SandboxInfo] = {}
        self._load()

    # ── Sandbox lifecycle ─────────────────────────────────────

    def create_sandbox(
        self,
        repo_path: str,
        base_branch: str = "main",
        sandbox_id: str = "",
    ) -> SandboxInfo:
        """Create an isolated worktree sandbox."""
        if not sandbox_id:
            sandbox_id = f"sbox_{uuid.uuid4().hex[:8]}"

        worktree_path = str(self._base_dir / sandbox_id)
        branch_name = f"aegis/selfdev/{sandbox_id}"

        info = SandboxInfo(
            sandbox_id=sandbox_id,
            repo_path=repo_path,
            worktree_path=worktree_path,
            branch_name=branch_name,
            base_branch=base_branch,
            created_at=int(time.time() * 1000),
            active=True,
        )

        if not Path(repo_path).exists():
            logger.warning("Repo path does not exist: %s", repo_path)
            info.active = False
            self._sandboxes[sandbox_id] = info
            self._save()
            return info

        wt_result = self._run_command(
            ["git", "worktree", "add", "-b", branch_name, worktree_path, base_branch],
            cwd=repo_path,
        )
        if wt_result.exit_code != 0:
            logger.error("Failed to create worktree: %s", wt_result.stderr)
            info.active = False
        else:
            logger.info("Sandbox created: %s at %s", sandbox_id, worktree_path)

        self._sandboxes[sandbox_id] = info
        self._save()
        return info

    def destroy_sandbox(self, sandbox_id: str) -> bool:
        """Remove a sandbox worktree."""
        info = self._sandboxes.get(sandbox_id)
        if info is None:
            return False

        wt_path = Path(info.worktree_path)
        if wt_path.exists():
            self._run_command(
                ["git", "worktree", "remove", "--force", info.worktree_path],
                cwd=info.repo_path,
            )

        info.active = False
        self._save()
        logger.info("Sandbox destroyed: %s", sandbox_id)
        return True

    def get_sandbox(self, sandbox_id: str) -> SandboxInfo | None:
        return self._sandboxes.get(sandbox_id)

    def list_sandboxes(self, active_only: bool = True) -> list[SandboxInfo]:
        if active_only:
            return [s for s in self._sandboxes.values() if s.active]
        return list(self._sandboxes.values())

    def cleanup_old_sandboxes(self, max_age_hours: float = 24.0) -> int:
        now_ms = int(time.time() * 1000)
        threshold_ms = now_ms - int(max_age_hours * 3_600_000)
        to_destroy = [
            sid for sid, info in self._sandboxes.items()
            if info.active and info.created_at < threshold_ms
        ]
        for sid in to_destroy:
            self.destroy_sandbox(sid)
        return len(to_destroy)

    # ── Command execution (sandbox-scoped) ────────────────────

    def execute_command(
        self,
        sandbox_id: str,
        command: str,
        args: list[str] | None = None,
        timeout_seconds: int = 60,
        dry_run: bool = False,
    ) -> CommandResult:
        """Execute a command within a sandbox."""
        info = self._sandboxes.get(sandbox_id)
        if info is None or not info.active:
            return CommandResult(command=command, exit_code=-1, stderr="Sandbox not found or inactive")

        policy = classify_command(command)
        if policy == CommandPolicy.DENY:
            return CommandResult(
                command=command, exit_code=-1,
                policy=CommandPolicy.DENY, stderr="Command denied by policy",
            )

        if dry_run:
            return CommandResult(
                command=command, exit_code=0,
                policy=policy, stdout="[dry_run] would execute",
            )

        if policy == CommandPolicy.ASK_APPROVAL:
            return CommandResult(
                command=command, exit_code=-1,
                policy=CommandPolicy.ASK_APPROVAL,
                stderr="Command requires approval",
            )

        full_cmd = [command] + (args or [])
        result = self._run_command(full_cmd, cwd=info.worktree_path, timeout=timeout_seconds)
        result.policy = policy
        result.command = command
        result.stdout = _mask_secrets(result.stdout[:_MAX_STDOUT_LEN])
        result.stderr = _mask_secrets(result.stderr[:_MAX_STDERR_LEN])
        return result

    # ── Sandbox file operations ───────────────────────────────

    def validate_file_path(self, sandbox_id: str, file_path: str) -> tuple[bool, str]:
        """Check that a file path is inside the sandbox and not secret."""
        info = self._sandboxes.get(sandbox_id)
        if info is None:
            return False, "Sandbox not found"

        try:
            resolved = Path(info.worktree_path, file_path).resolve()
            sandbox_root = Path(info.worktree_path).resolve()
            if not str(resolved).startswith(str(sandbox_root)):
                return False, "Path traversal detected"
        except (OSError, ValueError):
            return False, "Invalid path"

        if is_secret_path(file_path):
            return False, "Secret file access denied"

        return True, "ok"

    def read_file(self, sandbox_id: str, file_path: str) -> tuple[bool, str]:
        """Read a file from sandbox (with path validation)."""
        ok, reason = self.validate_file_path(sandbox_id, file_path)
        if not ok:
            return False, reason

        info = self._sandboxes[sandbox_id]
        full_path = Path(info.worktree_path) / file_path
        if not full_path.exists():
            return False, "File not found"
        try:
            content = full_path.read_text(encoding="utf-8", errors="replace")
            return True, content
        except Exception as exc:
            return False, str(exc)

    def write_file(self, sandbox_id: str, file_path: str, content: str) -> tuple[bool, str]:
        """Write a file to sandbox (with path validation)."""
        ok, reason = self.validate_file_path(sandbox_id, file_path)
        if not ok:
            return False, reason

        info = self._sandboxes[sandbox_id]
        full_path = Path(info.worktree_path) / file_path
        try:
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(content, encoding="utf-8")
            return True, "ok"
        except Exception as exc:
            return False, str(exc)

    # ── Diff / status ─────────────────────────────────────────

    def get_diff(self, sandbox_id: str) -> str:
        info = self._sandboxes.get(sandbox_id)
        if info is None:
            return ""
        result = self._run_command(["git", "diff"], cwd=info.worktree_path)
        return _mask_secrets(result.stdout[:5000])

    def get_changed_files(self, sandbox_id: str) -> list[str]:
        info = self._sandboxes.get(sandbox_id)
        if info is None:
            return []
        result = self._run_command(["git", "status", "--porcelain"], cwd=info.worktree_path)
        files = []
        for line in result.stdout.strip().split("\n"):
            line = line.strip()
            if line and len(line) > 3:
                files.append(line[3:])
        return files

    def get_status(self, sandbox_id: str) -> str:
        info = self._sandboxes.get(sandbox_id)
        if info is None:
            return ""
        result = self._run_command(["git", "status", "--short"], cwd=info.worktree_path)
        return result.stdout[:2000]

    def discard_changes(self, sandbox_id: str) -> bool:
        info = self._sandboxes.get(sandbox_id)
        if info is None:
            return False
        self._run_command(["git", "checkout", "."], cwd=info.worktree_path)
        self._run_command(["git", "clean", "-fd"], cwd=info.worktree_path)
        return True

    # ── Internal ──────────────────────────────────────────────

    def _run_command(
        self,
        cmd: list[str],
        cwd: str = "",
        timeout: int = 60,
    ) -> CommandResult:
        try:
            proc = subprocess.run(
                cmd,
                cwd=cwd or None,
                capture_output=True,
                timeout=timeout,
                encoding="utf-8",
                errors="replace",
            )
            return CommandResult(
                command=" ".join(cmd),
                exit_code=proc.returncode,
                stdout=proc.stdout or "",
                stderr=proc.stderr or "",
            )
        except subprocess.TimeoutExpired:
            return CommandResult(
                command=" ".join(cmd),
                exit_code=-1,
                timed_out=True,
                stderr=f"Command timed out after {timeout}s",
            )
        except Exception as exc:
            return CommandResult(
                command=" ".join(cmd),
                exit_code=-1,
                stderr=str(exc),
            )

    def _state_path(self) -> Path:
        return self._base_dir / "sandboxes.json"

    def _save(self) -> None:
        data = {sid: {
            "sandbox_id": s.sandbox_id,
            "repo_path": s.repo_path,
            "worktree_path": s.worktree_path,
            "branch_name": s.branch_name,
            "base_branch": s.base_branch,
            "created_at": s.created_at,
            "baseline_tests_passed": s.baseline_tests_passed,
            "baseline_test_summary": s.baseline_test_summary,
            "active": s.active,
        } for sid, s in self._sandboxes.items()}
        try:
            with open(self._state_path(), "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as exc:
            logger.warning("Failed to save sandboxes: %s", exc)

    def _load(self) -> None:
        path = self._state_path()
        if not path.exists():
            return
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
            for sid, d in data.items():
                self._sandboxes[sid] = SandboxInfo(**d)
            logger.info("Loaded %d sandboxes", len(self._sandboxes))
        except Exception as exc:
            logger.warning("Failed to load sandboxes: %s", exc)
