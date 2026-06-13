"""Dev Server — sandboxed self-development environment for AEGIS.

Features:
- Git worktree sandbox isolation
- Test execution (auto-detect Python/Rust/TypeScript)
- Lint / typecheck
- Diff review
- Existing code search
- Change impact analysis
- Rollback
- PR creation
- Cannot directly break production code
"""

from __future__ import annotations

import json
import logging
import os
import shutil
import subprocess
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

logger = logging.getLogger("aegis_ai.dev_server")

# Commands that are NEVER allowed in sandbox
DENIED_COMMANDS = frozenset({
    "rm -rf /", "rm -rf /*", "rm -rf ~",
    "sudo rm", "sudo chmod", "sudo chown",
    "git push --force", "git push -f",
    "git reset --hard",
    "curl | sh", "curl | bash", "wget | sh",
    "| sh", "| bash",
    "chmod 777", "chmod -R 777",
    "mkfs", "dd if=", "format",
})

# File paths that are NEVER accessible
DENIED_PATHS = frozenset({
    ".env", ".env.local", ".env.production",
    ".git/config", ".ssh", ".aws", ".gcloud",
    "credentials.json", "secrets.json",
    "id_rsa", "id_ed25519",
})


class SandboxStatus(Enum):
    CREATING = "creating"
    READY = "ready"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    DESTROYED = "destroyed"


@dataclass
class SandboxInfo:
    sandbox_id: str = ""
    repo_path: str = ""
    worktree_path: str = ""
    branch: str = ""
    status: SandboxStatus = SandboxStatus.CREATING
    created_at: int = 0
    destroyed_at: int = 0


@dataclass
class CommandResult:
    command: str = ""
    returncode: int = -1
    stdout: str = ""
    stderr: str = ""
    duration_ms: float = 0.0
    denied: bool = False
    deny_reason: str = ""


@dataclass
class DiffResult:
    files_changed: list[str] = field(default_factory=list)
    insertions: int = 0
    deletions: int = 0
    diff_text: str = ""
    summary: str = ""


@dataclass
class SearchResult:
    query: str = ""
    matches: list[dict[str, Any]] = field(default_factory=list)
    total: int = 0


class SandboxManager:
    """Manages git worktree sandboxes for isolated development."""

    def __init__(self, base_dir: str = "data/sandboxes", repo_path: str = ".") -> None:
        self._base_dir = Path(base_dir)
        self._base_dir.mkdir(parents=True, exist_ok=True)
        self._repo_path = Path(repo_path).resolve()
        self._sandboxes: dict[str, SandboxInfo] = {}
        self._load()

    def create_sandbox(self, branch_name: str = "") -> SandboxInfo:
        sandbox_id = f"sandbox_{uuid.uuid4().hex[:8]}"
        if not branch_name:
            branch_name = f"aegis/dev/{sandbox_id}"

        worktree_path = self._base_dir / sandbox_id
        info = SandboxInfo(
            sandbox_id=sandbox_id,
            repo_path=str(self._repo_path),
            worktree_path=str(worktree_path),
            branch=branch_name,
            created_at=int(time.time() * 1000),
        )

        try:
            result = subprocess.run(
                ["git", "worktree", "add", "-b", branch_name, str(worktree_path)],
                cwd=str(self._repo_path),
                capture_output=True, text=True, encoding="utf-8", errors="replace",
                timeout=30,
            )
            if result.returncode != 0:
                info.status = SandboxStatus.FAILED
                logger.error("Failed to create worktree: %s", result.stderr)
                return info

            info.status = SandboxStatus.READY
            self._sandboxes[sandbox_id] = info
            self._save()
            logger.info("Sandbox created: %s at %s", sandbox_id, worktree_path)
        except Exception as e:
            info.status = SandboxStatus.FAILED
            logger.error("Sandbox creation failed: %s", e)

        return info

    def destroy_sandbox(self, sandbox_id: str) -> bool:
        info = self._sandboxes.get(sandbox_id)
        if info is None:
            return False

        try:
            subprocess.run(
                ["git", "worktree", "remove", "--force", info.worktree_path],
                cwd=info.repo_path,
                capture_output=True, text=True, encoding="utf-8", errors="replace",
                timeout=30,
            )
            info.status = SandboxStatus.DESTROYED
            info.destroyed_at = int(time.time() * 1000)
            self._save()
            return True
        except Exception as e:
            logger.error("Failed to destroy sandbox %s: %s", sandbox_id, e)
            return False

    def get_sandbox(self, sandbox_id: str) -> SandboxInfo | None:
        return self._sandboxes.get(sandbox_id)

    def list_sandboxes(self) -> list[SandboxInfo]:
        return list(self._sandboxes.values())

    def _load(self) -> None:
        path = self._base_dir / "sandboxes.json"
        if not path.exists():
            return
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            for d in data:
                info = SandboxInfo(**d)
                info.status = SandboxStatus(info.get("status", "ready")) if isinstance(info.status, str) else info.status
                self._sandboxes[info.sandbox_id] = info
        except Exception:
            pass

    def _save(self) -> None:
        path = self._base_dir / "sandboxes.json"
        data = []
        for info in self._sandboxes.values():
            d = {
                "sandbox_id": info.sandbox_id,
                "repo_path": info.repo_path,
                "worktree_path": info.worktree_path,
                "branch": info.branch,
                "status": info.status.value,
                "created_at": info.created_at,
                "destroyed_at": info.destroyed_at,
            }
            data.append(d)
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")


class DevServer:
    """Sandboxed development operations for AEGIS self-development."""

    def __init__(self, repo_path: str = ".", sandbox_manager: SandboxManager | None = None) -> None:
        self._repo_path = Path(repo_path).resolve()
        self._sandbox_mgr = sandbox_manager or SandboxManager(repo_path=repo_path)

    @property
    def sandbox_manager(self) -> SandboxManager:
        return self._sandbox_mgr

    def run_command(
        self,
        command: str,
        cwd: str = "",
        timeout: int = 60,
    ) -> CommandResult:
        if not self._is_command_safe(command):
            return CommandResult(
                command=command, denied=True,
                deny_reason=f"Command '{command}' is not allowed.",
            )

        work_dir = cwd or str(self._repo_path)
        start = time.perf_counter()

        try:
            result = subprocess.run(
                command, shell=True, cwd=work_dir,
                capture_output=True, text=True,
                encoding="utf-8", errors="replace",
                timeout=timeout,
            )
            duration = (time.perf_counter() - start) * 1000
            return CommandResult(
                command=command,
                returncode=result.returncode,
                stdout=result.stdout[:50000],
                stderr=result.stderr[:10000],
                duration_ms=duration,
            )
        except subprocess.TimeoutExpired:
            return CommandResult(command=command, returncode=-1, stderr=f"Timeout after {timeout}s")
        except Exception as e:
            return CommandResult(command=command, returncode=-1, stderr=str(e))

    def run_tests(self, sandbox_id: str = "", test_path: str = "") -> CommandResult:
        cwd = self._resolve_cwd(sandbox_id)
        if not test_path:
            test_path = self._detect_test_command(cwd)
        return self.run_command(test_path, cwd=cwd, timeout=120)

    def run_lint(self, sandbox_id: str = "") -> CommandResult:
        cwd = self._resolve_cwd(sandbox_id)
        cmd = self._detect_lint_command(cwd)
        return self.run_command(cmd, cwd=cwd)

    def run_typecheck(self, sandbox_id: str = "") -> CommandResult:
        cwd = self._resolve_cwd(sandbox_id)
        cmd = self._detect_typecheck_command(cwd)
        return self.run_command(cmd, cwd=cwd)

    def get_diff(self, sandbox_id: str = "") -> DiffResult:
        cwd = self._resolve_cwd(sandbox_id)
        result = self.run_command("git diff --stat && git diff --cached --stat && git status --porcelain", cwd=cwd)
        if result.returncode != 0:
            return DiffResult(summary="Failed to get diff.")

        files = []
        insertions = 0
        deletions = 0
        for line in result.stdout.strip().split("\n"):
            line = line.strip()
            if not line:
                continue
            if "|" in line:
                parts = line.split("|")
                fname = parts[0].strip()
                if fname and fname not in files:
                    files.append(fname)
                if "+" in parts[-1]:
                    insertions += parts[-1].count("+")
                if "-" in parts[-1]:
                    deletions += parts[-1].count("-")
            elif line.startswith("??"):
                fname = line[3:].strip()
                if fname and fname not in files:
                    files.append(fname)
            elif len(line) > 3 and line[0] in "AMDRC":
                fname = line[3:].strip()
                if fname and fname not in files:
                    files.append(fname)

        diff_result = self.run_command("git diff", cwd=cwd)
        return DiffResult(
            files_changed=files,
            insertions=insertions,
            deletions=deletions,
            diff_text=diff_result.stdout[:10000],
            summary=f"{len(files)} files changed, {insertions} insertions(+), {deletions} deletions(-)",
        )

    def search_code(self, query: str, sandbox_id: str = "", file_pattern: str = "*.py") -> SearchResult:
        cwd = self._resolve_cwd(sandbox_id)
        cmd = f'findstr /S /N "{query}" {file_pattern}'
        result = self.run_command(cmd, cwd=cwd)

        matches = []
        if result.returncode == 0:
            for line in result.stdout.strip().split("\n")[:50]:
                line = line.strip()
                if ":" in line:
                    parts = line.split(":", 2)
                    if len(parts) >= 3:
                        matches.append({
                            "file": parts[0],
                            "line": int(parts[1]) if parts[1].isdigit() else 0,
                            "content": parts[2][:200],
                        })

        if not matches:
            cmd2 = f'grep -rn "{query}" --include="{file_pattern}" .'
            result2 = self.run_command(cmd2, cwd=cwd)
            if result2.returncode == 0:
                for line in result2.stdout.strip().split("\n")[:50]:
                    if ":" in line:
                        parts = line.split(":", 2)
                        if len(parts) >= 3:
                            matches.append({
                                "file": parts[0],
                                "line": int(parts[1]) if parts[1].isdigit() else 0,
                                "content": parts[2][:200],
                            })

        return SearchResult(query=query, matches=matches, total=len(matches))

    def analyze_impact(self, sandbox_id: str = "") -> dict[str, Any]:
        diff = self.get_diff(sandbox_id)
        impacted_modules = set()
        impacted_tests = set()

        for f in diff.files_changed:
            if "/" in f:
                module = f.split("/")[0]
                impacted_modules.add(module)
            if "test_" in f:
                impacted_tests.add(f)

        return {
            "files_changed": diff.files_changed,
            "impacted_modules": list(impacted_modules),
            "impacted_tests": list(impacted_tests),
            "insertions": diff.insertions,
            "deletions": diff.deletions,
            "summary": diff.summary,
        }

    def rollback(self, sandbox_id: str = "") -> CommandResult:
        cwd = self._resolve_cwd(sandbox_id)
        self.run_command("git checkout -- .", cwd=cwd)
        return self.run_command("git clean -fd", cwd=cwd)

    def create_pr(self, sandbox_id: str, title: str, body: str = "") -> dict[str, Any]:
        info = self._sandbox_mgr.get_sandbox(sandbox_id)
        if info is None:
            return {"error": f"Sandbox '{sandbox_id}' not found."}

        cwd = info.worktree_path
        diff = self.get_diff(sandbox_id)
        if not diff.files_changed:
            return {"error": "No changes to create PR from."}

        commit_result = self.run_command(f'git add -A && git commit -m "{title}"', cwd=cwd)
        if commit_result.returncode != 0:
            return {"error": f"Commit failed: {commit_result.stderr[:200]}"}

        push_result = self.run_command(f"git push -u origin {info.branch}", cwd=cwd)
        if push_result.returncode != 0:
            return {"error": f"Push failed: {push_result.stderr[:200]}"}

        pr_body = body or f"Auto-generated PR from AEGIS sandbox {sandbox_id}\n\n{diff.summary}"
        pr_cmd = f'gh pr create --title "{title}" --body "{pr_body}" --head {info.branch}'
        pr_result = self.run_command(pr_cmd, cwd=cwd)

        if pr_result.returncode != 0:
            return {"error": f"PR creation failed: {pr_result.stderr[:200]}"}

        return {
            "success": True,
            "branch": info.branch,
            "pr_url": pr_result.stdout.strip(),
            "diff_summary": diff.summary,
        }

    def read_file(self, path: str, sandbox_id: str = "") -> dict[str, Any]:
        if not self._is_path_safe(path):
            return {"error": f"Access denied: {path}"}

        full_path = Path(self._resolve_cwd(sandbox_id)) / path
        if not full_path.exists():
            return {"error": f"File not found: {path}"}

        try:
            content = full_path.read_text(encoding="utf-8", errors="replace")
            return {"path": path, "content": content[:100000], "size": len(content)}
        except Exception as e:
            return {"error": f"Read failed: {e}"}

    def write_file(self, path: str, content: str, sandbox_id: str = "") -> dict[str, Any]:
        if not self._is_path_safe(path):
            return {"error": f"Access denied: {path}"}

        full_path = Path(self._resolve_cwd(sandbox_id)) / path
        try:
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(content, encoding="utf-8")
            return {"path": path, "size": len(content), "success": True}
        except Exception as e:
            return {"error": f"Write failed: {e}"}

    def _resolve_cwd(self, sandbox_id: str) -> str:
        if sandbox_id:
            info = self._sandbox_mgr.get_sandbox(sandbox_id)
            if info and info.status == SandboxStatus.READY:
                return info.worktree_path
        return str(self._repo_path)

    def _is_command_safe(self, command: str) -> bool:
        cmd_lower = command.lower().strip()
        for denied in DENIED_COMMANDS:
            if denied in cmd_lower:
                return False
        return True

    def _is_path_safe(self, path: str) -> bool:
        path_lower = path.lower().replace("\\", "/")
        for denied in DENIED_PATHS:
            if denied in path_lower:
                return False
        if ".." in path:
            return False
        return True

    def _detect_test_command(self, cwd: str) -> str:
        if (Path(cwd) / "pyproject.toml").exists():
            return "python -m pytest -q --tb=short"
        if (Path(cwd) / "Cargo.toml").exists():
            return "cargo test"
        if (Path(cwd) / "package.json").exists():
            return "npm test"
        return "python -m pytest -q --tb=short"

    def _detect_lint_command(self, cwd: str) -> str:
        if (Path(cwd) / "pyproject.toml").exists():
            return "ruff check ."
        if (Path(cwd) / "Cargo.toml").exists():
            return "cargo clippy -- -D warnings"
        if (Path(cwd) / "package.json").exists():
            return "npx eslint ."
        return "ruff check ."

    def _detect_typecheck_command(self, cwd: str) -> str:
        if (Path(cwd) / "pyproject.toml").exists():
            return "python -m mypy src --ignore-missing-imports"
        if (Path(cwd) / "tsconfig.json").exists():
            return "npx tsc --noEmit"
        return "echo 'No typecheck configured'"
