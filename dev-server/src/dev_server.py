"""Dev Server — gRPC server for sandboxed self-development.

Implements the DevServer gRPC service defined in protos/aegis/dev_server.proto.

Safety constraints (per architecture §8.3):
- No direct push/merge to main
- No access to secrets
- No production deploy
- No system package install
- No Docker daemon access
- All operations sandboxed
- User is the only merge authority
"""

from __future__ import annotations

import logging
import os
import re
import shlex
import shutil
import subprocess
import time
from concurrent import futures
from pathlib import Path
from typing import Any

import grpc

logger = logging.getLogger("aegis_ai.dev_server")

_PROTECTED_BRANCHES = frozenset({"main", "master"})
_SHELL_META = re.compile(r"[|&;<>`$\\\n()]")
_UNIFIED_HUNK = re.compile(r"(?m)^@@ ")
_DIFF_GIT = re.compile(r"(?m)^diff --git ")
_MAX_OUTPUT = 50_000
_MAX_FILE_DIFF = 8_000
_MAX_FILES = 80

DENIED_COMMANDS = frozenset({
    "rm -rf /", "rm -rf /*", "sudo rm", "sudo chmod",
    "git push --force", "git push -f", "git reset --hard",
    "curl | sh", "wget | sh", "| sh", "| bash",
    "chmod 777", "mkfs", "dd if=",
})

DENIED_PATHS = frozenset({
    ".env", ".env.local", ".env.production",
    ".git/config", ".ssh", ".aws", ".gcloud",
    "credentials.json", "secrets.json",
    "id_rsa", "id_ed25519",
})

LANGUAGE_INDICATORS: dict[str, tuple[str, ...]] = {
    "python": ("pyproject.toml", "setup.py", "setup.cfg", "requirements.txt", "Pipfile"),
    "kotlin": ("build.gradle.kts", "build.gradle", "settings.gradle.kts"),
    "typescript": ("tsconfig.json",),
    "javascript": ("package.json",),
    "rust": ("Cargo.toml",),
}

TEST_COMMANDS: dict[str, list[str]] = {
    "python": ["python", "-m", "pytest", "--tb=short", "-q"],
    "kotlin": ["./gradlew", "test"],
    "typescript": ["npm", "test"],
    "javascript": ["npm", "test"],
    "rust": ["cargo", "test"],
}

LINT_COMMANDS: dict[str, list[str]] = {
    "python": ["ruff", "check", "."],
    "kotlin": ["./gradlew", "ktlintCheck"],
    "typescript": ["npx", "eslint", "."],
    "javascript": ["npx", "eslint", "."],
    "rust": ["cargo", "clippy", "--", "-D", "warnings"],
}

LINTER_COMMANDS: dict[str, list[str]] = {
    "ruff": ["ruff", "check", "."],
    "eslint": ["npx", "eslint", "."],
    "ktlint": ["ktlint"],
    "clippy": ["cargo", "clippy", "--", "-D", "warnings"],
}


def _proto_status(status: str | dict, message: str = ""):
    from generated.aegis import common_pb2

    if isinstance(status, dict):
        message = status.get("message", message)
        status = status.get("status", "ok")
    code = 0 if status == "ok" else 1
    return common_pb2.Status(code=code, message=message or str(status))


def _is_command_safe(command: str) -> bool:
    cmd_lower = command.lower().strip()
    return all(denied not in cmd_lower for denied in DENIED_COMMANDS)


def _is_path_safe(path: str) -> bool:
    path_lower = path.lower().replace("\\", "/")
    if ".." in path_lower.split("/"):
        return False
    if ".." in path:
        return False
    return all(denied not in path_lower for denied in DENIED_PATHS)


def _looks_like_unified_diff(text: str) -> bool:
    stripped = text.lstrip()
    if stripped.startswith("diff --git ") or _DIFF_GIT.search(text):
        return True
    if stripped.startswith("--- ") and "\n+++ " in text:
        return True
    return bool(_UNIFIED_HUNK.search(text))


def _parse_extra_args(raw: str) -> tuple[list[str] | None, str]:
    text = str(raw or "").strip()
    if not text:
        return [], ""
    if _SHELL_META.search(text):
        return None, "extra_args contains shell metacharacters"
    if not _is_command_safe(text):
        return None, "extra_args denied"
    try:
        parts = shlex.split(text, posix=True)
    except ValueError as exc:
        return None, f"invalid extra_args: {exc}"
    for part in parts:
        if ".." in part or not _is_path_safe(part):
            return None, "extra_args contains an unsafe path"
    return parts, ""


def _detect_language(workspace: Path) -> str:
    for lang, indicators in LANGUAGE_INDICATORS.items():
        if any((workspace / name).exists() for name in indicators):
            return lang
    return "unknown"


def _command_available(argv: list[str], cwd: Path | None = None) -> bool:
    if not argv:
        return False
    binary = argv[0]
    if binary.startswith("./"):
        root = cwd or Path.cwd()
        return (root / binary).exists()
    return shutil.which(binary) is not None


def _split_unified_diffs(text: str) -> list[tuple[str, str]]:
    chunks: list[tuple[str, str]] = []
    current_path = ""
    current_lines: list[str] = []
    for line in text.splitlines(keepends=True):
        if line.startswith("diff --git "):
            if current_path:
                chunks.append((current_path, "".join(current_lines)))
            parts = line.strip().split()
            rhs = parts[-1] if parts else ""
            current_path = rhs[2:] if rhs.startswith("b/") else rhs
            current_lines = [line]
        else:
            current_lines.append(line)
    if current_path:
        chunks.append((current_path, "".join(current_lines)))
    return chunks


def _run(
    argv: list[str],
    cwd: Path,
    *,
    timeout: int = 60,
    input_text: str | None = None,
    env: dict[str, str] | None = None,
) -> tuple[int, str, str]:
    if not argv:
        return -1, "", "empty command"
    joined = " ".join(argv)
    if not _is_command_safe(joined):
        return -1, "", f"Command denied: {joined}"
    try:
        result = subprocess.run(
            argv,
            cwd=str(cwd),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
            input=input_text,
            env=env,
            shell=False,
        )
        return result.returncode, result.stdout[:_MAX_OUTPUT], result.stderr[:10_000]
    except FileNotFoundError:
        return -1, "", f"toolchain missing: {argv[0]}"
    except subprocess.TimeoutExpired:
        return -1, "", f"Timeout after {timeout}s"
    except Exception as exc:
        return -1, "", str(exc)


def _git_status_paths(line: str) -> list[str]:
    raw = line[3:] if len(line) >= 3 else line
    if " -> " in raw:
        return [part.strip() for part in raw.split(" -> ", 1)]
    return [raw.strip()]


class DevServerService:
    """Sandboxed git / test / lint / PR operations inside a workspace."""

    def __init__(self, repo_path: str = ".") -> None:
        self._repo_path = Path(repo_path).resolve()
        self._started_at = time.monotonic()
        self._last_test_result: dict[str, Any] | None = None

    def uptime_ms(self) -> int:
        return int((time.monotonic() - self._started_at) * 1000)

    def HealthCheck(self, request, context) -> dict[str, Any]:
        return {"status": "ok", "message": "Dev server running", "uptime_ms": self.uptime_ms()}

    def GetRepoStatus(self, request, context) -> dict[str, Any]:
        cwd = self._repo_path
        branch = self._git_output(["rev-parse", "--abbrev-ref", "HEAD"], cwd)
        commit = self._git_output(["rev-parse", "HEAD"], cwd)
        status_out = self._git_output(["status", "--porcelain"], cwd)
        modified = []
        for line in status_out.splitlines():
            if not line.strip():
                continue
            modified.extend(_git_status_paths(line))
        ahead, behind = self._ahead_behind(cwd)
        return {
            "status": "ok",
            "branch": branch,
            "commit_hash": commit,
            "is_clean": not bool(status_out.strip()),
            "modified_files": modified[:50],
            "ahead_commits": ahead,
            "behind_commits": behind,
        }

    def GetTestResults(self, request, context) -> dict[str, Any]:
        if self._last_test_result is None:
            return {"status": "ok", "result": {}, "results": []}
        return {"status": "ok", "result": dict(self._last_test_result), "results": [dict(self._last_test_result)]}

    def GetDiff(self, request, context) -> dict[str, Any]:
        cwd = self._repo_path
        from_branch = str(getattr(request, "from_branch", "") or "").strip()
        to_branch = str(getattr(request, "to_branch", "") or "").strip()
        if not from_branch:
            from_branch = self._default_base(cwd)
        if not to_branch:
            to_branch = "HEAD"
        range_spec = f"{from_branch}...{to_branch}"
        code, numstat, stderr = _run(["git", "diff", "--numstat", range_spec], cwd, timeout=30)
        if code != 0:
            return {"status": "error", "files": [], "message": (stderr or numstat)[:200]}
        stats: dict[str, tuple[int, int]] = {}
        for line in numstat.splitlines():
            parts = line.split("\t")
            if len(parts) < 3:
                continue
            added_raw, deleted_raw, path = parts[0], parts[1], parts[2]
            stats[path] = (
                int(added_raw) if added_raw.isdigit() else 0,
                int(deleted_raw) if deleted_raw.isdigit() else 0,
            )
        code, full_diff, stderr = _run(["git", "diff", range_spec], cwd, timeout=30)
        if code != 0:
            return {"status": "error", "files": [], "message": (stderr or full_diff)[:200]}
        files: list[dict[str, Any]] = []
        for path, chunk in _split_unified_diffs(full_diff):
            if not _is_path_safe(path):
                continue
            added, deleted = stats.get(path, (0, 0))
            files.append({
                "path": path,
                "status": "modified",
                "diff": chunk[:_MAX_FILE_DIFF],
                "additions": added,
                "deletions": deleted,
            })
            if len(files) >= _MAX_FILES:
                break
        if not files:
            for path, (added, deleted) in list(stats.items())[:_MAX_FILES]:
                if not _is_path_safe(path):
                    continue
                files.append({
                    "path": path,
                    "status": "modified",
                    "diff": "",
                    "additions": added,
                    "deletions": deleted,
                })
        return {"status": "ok", "files": files}

    def CreateBranch(self, request, context) -> dict[str, Any]:
        branch_name = str(getattr(request, "branch_name", "") or "").strip()
        base_branch = str(getattr(request, "base_branch", "") or "").strip()
        if not branch_name:
            return {"status": "error", "branch_name": "", "message": "branch_name is required"}
        if not re.fullmatch(r"[A-Za-z0-9._/\-]+", branch_name) or branch_name.startswith("-"):
            return {"status": "error", "branch_name": "", "message": "invalid branch_name"}
        cwd = self._repo_path
        existing = self._git_output(["rev-parse", "--verify", branch_name], cwd)
        if existing:
            code, _, stderr = _run(["git", "switch", branch_name], cwd)
            if code != 0:
                return {"status": "error", "branch_name": "", "message": stderr[:200]}
            return {"status": "ok", "branch_name": branch_name, "message": "switched to existing branch"}
        if base_branch:
            code, _, stderr = _run(["git", "switch", base_branch], cwd)
            if code != 0:
                return {"status": "error", "branch_name": "", "message": stderr[:200]}
        code, _, stderr = _run(["git", "switch", "-c", branch_name], cwd)
        if code != 0:
            return {"status": "error", "branch_name": "", "message": stderr[:200]}
        return {"status": "ok", "branch_name": branch_name}

    def ApplyPatch(self, request, context) -> dict[str, Any]:
        file_path = str(getattr(request, "file_path", "") or "")
        patch_content = str(getattr(request, "patch_content", "") or "")
        if not patch_content.strip():
            return {"status": "error", "applied": False, "error_detail": "patch_content is empty"}
        cwd = self._repo_path
        if _looks_like_unified_diff(patch_content):
            check_code, _, check_err = _run(
                ["git", "apply", "--check", "--whitespace=nowarn"],
                cwd,
                input_text=patch_content,
            )
            if check_code != 0:
                return {"status": "error", "applied": False, "error_detail": check_err[:200] or "git apply --check failed"}
            code, _, stderr = _run(
                ["git", "apply", "--whitespace=nowarn"],
                cwd,
                input_text=patch_content,
            )
            if code != 0:
                return {"status": "error", "applied": False, "error_detail": stderr[:200]}
            return {"status": "ok", "applied": True}
        if not file_path:
            return {"status": "error", "applied": False, "error_detail": "file_path is required for non-diff content"}
        resolved = self._safe_repo_path(file_path)
        if resolved is None:
            return {"status": "error", "applied": False, "error_detail": "Path denied."}
        try:
            resolved.parent.mkdir(parents=True, exist_ok=True)
            resolved.write_text(patch_content, encoding="utf-8")
            return {"status": "ok", "applied": True}
        except Exception as exc:
            return {"status": "error", "applied": False, "error_detail": str(exc)[:200]}

    def RunTests(self, request, context) -> dict[str, Any]:
        target = str(getattr(request, "target", "") or "").strip() or "ai-server"
        extra = str(getattr(request, "extra_args", "") or "")
        timeout = int(getattr(request, "timeout_seconds", 0) or 0) or 60
        extra_parts, extra_error = _parse_extra_args(extra)
        if extra_parts is None:
            return {"status": "error", "result": self._empty_test_result(target), "message": extra_error}
        workdir, workdir_error = self._target_dir(target)
        if workdir is None:
            return {"status": "error", "result": self._empty_test_result(target), "message": workdir_error}
        language = _detect_language(workdir)
        argv = list(TEST_COMMANDS.get(language) or [])
        if not argv:
            message = f"no test command for language '{language}' in {workdir}"
            result = {**self._empty_test_result(target), "output": message}
            return {"status": "error", "result": result, "message": message}
        if language != "python" and not _command_available(argv, workdir):
            message = f"toolchain missing for {language}: {argv[0]}"
            result = {**self._empty_test_result(target), "output": message}
            return {"status": "error", "result": result, "message": message}
        argv = [*argv, *extra_parts]
        started = time.monotonic()
        code, stdout, stderr = _run(argv, workdir, timeout=timeout)
        duration = time.monotonic() - started
        parsed = _parse_pytest_counts(stdout + stderr)
        result = {
            "suite": target,
            "total": parsed["total"],
            "passed": parsed["passed"],
            "failed": parsed["failed"],
            "errors": parsed["errors"],
            "duration_sec": duration,
            "output": (stdout + stderr)[:5000],
        }
        self._last_test_result = result
        return {"status": "ok" if code == 0 else "error", "result": result}

    def RunLint(self, request, context) -> dict[str, Any]:
        target = str(getattr(request, "target", "") or "").strip() or "ai-server"
        linter = str(getattr(request, "linter", "") or "").strip()
        workdir, workdir_error = self._target_dir(target)
        if workdir is None:
            return {
                "status": "error",
                "passed": False,
                "error_count": 0,
                "warning_count": 0,
                "output": workdir_error,
                "message": workdir_error,
            }
        if linter:
            argv = list(LINTER_COMMANDS.get(linter) or [])
            if not argv:
                return {
                    "status": "error",
                    "passed": False,
                    "error_count": 0,
                    "warning_count": 0,
                    "output": f"unknown linter '{linter}'",
                    "message": f"unknown linter '{linter}'",
                }
        else:
            language = _detect_language(workdir)
            argv = list(LINT_COMMANDS.get(language) or [])
            if not argv:
                message = f"no lint command for language '{language}' in {workdir}"
                return {
                    "status": "error",
                    "passed": False,
                    "error_count": 0,
                    "warning_count": 0,
                    "output": message,
                    "message": message,
                }
        if argv[:1] == ["ruff"] and not shutil.which("ruff"):
            argv = ["python", "-m", "ruff", *argv[1:]]
        if not _command_available(argv, workdir):
            message = f"toolchain missing: {argv[0]}"
            return {
                "status": "error",
                "passed": False,
                "error_count": 0,
                "warning_count": 0,
                "output": message,
                "message": message,
            }
        code, stdout, stderr = _run(argv, workdir, timeout=120)
        output = (stdout + stderr)[:5000]
        error_count = 0 if code == 0 else max(output.count("\n"), 1 if output.strip() else 0)
        return {
            "status": "ok",
            "passed": code == 0,
            "error_count": error_count,
            "warning_count": 0,
            "output": output,
        }

    def CreateCommit(self, request, context) -> dict[str, Any]:
        message = str(getattr(request, "message", "") or "").strip()
        files = [str(item) for item in (getattr(request, "files", []) or [])]
        if not message:
            return {"status": "error", "commit_hash": "", "message": "commit message is required"}
        cwd = self._repo_path
        branch = self._git_output(["rev-parse", "--abbrev-ref", "HEAD"], cwd)
        if branch.lower() in _PROTECTED_BRANCHES:
            return {
                "status": "error",
                "commit_hash": "",
                "message": f"Direct commit to '{branch}' is forbidden. Create a branch and open a PR.",
            }
        to_add: list[str]
        if files:
            to_add = []
            for raw in files:
                if self._safe_repo_path(raw) is None:
                    return {"status": "error", "commit_hash": "", "message": f"Path denied: {raw}"}
                to_add.append(raw.replace("\\", "/"))
        else:
            status_out = self._git_output(["status", "--porcelain"], cwd)
            to_add = []
            for line in status_out.splitlines():
                for path in _git_status_paths(line):
                    if _is_path_safe(path):
                        to_add.append(path)
        if not to_add:
            return {"status": "error", "commit_hash": "", "message": "no safe files to commit"}
        for path in to_add:
            code, _, stderr = _run(["git", "add", "--", path], cwd)
            if code != 0:
                return {"status": "error", "commit_hash": "", "message": stderr[:200]}
        code, _, stderr = _run(["git", "commit", "-m", message], cwd)
        if code != 0:
            return {"status": "error", "commit_hash": "", "message": stderr[:200]}
        commit_hash = self._git_output(["rev-parse", "HEAD"], cwd)
        return {"status": "ok", "commit_hash": commit_hash}

    def CreatePullRequest(self, request, context) -> dict[str, Any]:
        title = str(getattr(request, "title", "") or "").strip()
        description = str(getattr(request, "description", "") or "")
        head = str(getattr(request, "head_branch", "") or "").strip()
        base = str(getattr(request, "base_branch", "") or "").strip() or "main"
        if not title or not head:
            return {"status": "error", "pr_url": "", "pr_number": 0, "message": "title and head_branch are required"}
        if head.lower() in _PROTECTED_BRANCHES:
            return {
                "status": "error",
                "pr_url": "",
                "pr_number": 0,
                "message": "PRs from main/master are forbidden.",
            }
        if base.lower() not in _PROTECTED_BRANCHES and base.lower() != "main":
            # still allow custom bases, but never merge locally
            pass
        token = os.getenv("GITHUB_TOKEN", "").strip()
        gh = shutil.which("gh")
        if not token or not gh:
            instructions = (
                f"GITHUB_TOKEN or gh CLI missing. Create the PR manually:\n"
                f"gh pr create --title {shlex.quote(title)} --body {shlex.quote(description)} "
                f"--head {shlex.quote(head)} --base {shlex.quote(base)}"
            )
            return {
                "status": "ok",
                "pr_url": "",
                "pr_number": 0,
                "message": instructions,
            }
        env = os.environ.copy()
        env["GH_TOKEN"] = token
        env["GITHUB_TOKEN"] = token
        argv = [
            "gh", "pr", "create",
            "--title", title,
            "--body", description,
            "--head", head,
            "--base", base,
        ]
        code, stdout, stderr = _run(argv, self._repo_path, env=env, timeout=60)
        if code != 0:
            return {"status": "error", "pr_url": "", "pr_number": 0, "message": (stderr or stdout)[:200]}
        url = stdout.strip().splitlines()[-1] if stdout.strip() else ""
        pr_number = 0
        match = re.search(r"/pull/(\d+)", url)
        if match:
            pr_number = int(match.group(1))
        return {"status": "ok", "pr_url": url, "pr_number": pr_number}

    def RevertChanges(self, request, context) -> dict[str, Any]:
        target = str(getattr(request, "target", "") or "").strip() or "all"
        commit_hash = str(getattr(request, "commit_hash", "") or "").strip()
        cwd = self._repo_path
        reverted: list[str] = []
        if commit_hash:
            if not re.fullmatch(r"[0-9a-fA-F]{7,40}", commit_hash):
                return {"status": "error", "reverted_files": [], "message": "invalid commit_hash"}
            before = self._git_output(["status", "--porcelain"], cwd)
            code, _, stderr = _run(["git", "revert", "--no-edit", commit_hash], cwd)
            if code != 0:
                return {"status": "error", "reverted_files": [], "message": stderr[:200]}
            after = self._git_output(["show", "--name-only", "--pretty=format:", "HEAD"], cwd)
            reverted = [line.strip() for line in after.splitlines() if line.strip()]
            _ = before
            return {"status": "ok", "reverted_files": reverted}
        if target == "all":
            before = [
                path
                for line in self._git_output(["status", "--porcelain"], cwd).splitlines()
                for path in _git_status_paths(line)
            ]
            _run(["git", "restore", "--worktree", "--staged", "."], cwd)
            code, _, stderr = _run(["git", "clean", "-fd"], cwd)
            if code != 0:
                return {"status": "error", "reverted_files": [], "message": stderr[:200]}
            return {"status": "ok", "reverted_files": before}
        if self._safe_repo_path(target) is None:
            return {"status": "error", "reverted_files": [], "message": "Path denied."}
        code, _, stderr = _run(["git", "restore", "--worktree", "--staged", "--", target], cwd)
        if code != 0:
            return {"status": "error", "reverted_files": [], "message": stderr[:200]}
        return {"status": "ok", "reverted_files": [target]}

    def _git_output(self, args: list[str], cwd: Path) -> str:
        code, stdout, _ = _run(["git", *args], cwd, timeout=15)
        return stdout.strip() if code == 0 else ""

    def _ahead_behind(self, cwd: Path) -> tuple[int, int]:
        code, stdout, _ = _run(
            ["git", "rev-list", "--left-right", "--count", "@{upstream}...HEAD"],
            cwd,
            timeout=15,
        )
        if code != 0:
            return 0, 0
        parts = stdout.strip().split()
        if len(parts) != 2:
            return 0, 0
        behind = int(parts[0]) if parts[0].isdigit() else 0
        ahead = int(parts[1]) if parts[1].isdigit() else 0
        return ahead, behind

    def _default_base(self, cwd: Path) -> str:
        for name in ("main", "master"):
            if self._git_output(["rev-parse", "--verify", name], cwd):
                return name
        return "HEAD"

    def _target_dir(self, target: str) -> tuple[Path | None, str]:
        if target in {"", "all"}:
            return self._repo_path, ""
        candidate = (self._repo_path / target).resolve()
        try:
            candidate.relative_to(self._repo_path)
        except ValueError:
            return None, "target escapes workspace"
        if not candidate.exists() or not candidate.is_dir():
            return None, f"target directory not found: {target}"
        return candidate, ""

    def _safe_repo_path(self, raw: str) -> Path | None:
        if not raw or not _is_path_safe(raw):
            return None
        path = Path(raw)
        if path.is_absolute():
            return None
        resolved = (self._repo_path / path).resolve()
        try:
            resolved.relative_to(self._repo_path)
        except ValueError:
            return None
        return resolved

    @staticmethod
    def _empty_test_result(suite: str) -> dict[str, Any]:
        return {
            "suite": suite,
            "total": 0,
            "passed": 0,
            "failed": 0,
            "errors": 0,
            "duration_sec": 0.0,
            "output": "",
        }


def _parse_pytest_counts(text: str) -> dict[str, int]:
    passed = failed = errors = 0
    for line in text.splitlines():
        lower = line.lower()
        tokens = lower.replace(",", " ").split()
        for index, token in enumerate(tokens):
            if index == 0:
                continue
            prev = tokens[index - 1]
            if not prev.isdigit():
                continue
            value = int(prev)
            if token.startswith("passed"):
                passed = value
            elif token.startswith("failed"):
                failed = value
            elif token.startswith("error"):
                errors = value
    total = passed + failed + errors
    return {"passed": passed, "failed": failed, "errors": errors, "total": total}


class DevServerGrpcServicer:
    """Proto adapter around DevServerService."""

    def __init__(self, service: DevServerService) -> None:
        self._service = service

    def HealthCheck(self, request, context):
        from generated.aegis import common_pb2

        result = self._service.HealthCheck(request, context)
        return common_pb2.HealthCheckResponse(
            status=_proto_status(result),
            server_status=common_pb2.SERVER_STATUS_ONLINE,
            uptime_ms=int(result.get("uptime_ms", 0)),
            version="0.1.0+docker-grpc",
        )

    def GetRepoStatus(self, request, context):
        from generated.aegis import dev_server_pb2

        result = self._service.GetRepoStatus(request, context)
        return dev_server_pb2.GetRepoStatusResponse(
            status=_proto_status(result),
            branch=result.get("branch", ""),
            commit_hash=result.get("commit_hash", ""),
            is_clean=bool(result.get("is_clean", False)),
            modified_files=list(result.get("modified_files", [])),
            ahead_commits=int(result.get("ahead_commits", 0)),
            behind_commits=int(result.get("behind_commits", 0)),
        )

    def GetTestResults(self, request, context):
        from generated.aegis import dev_server_pb2

        result = self._service.GetTestResults(request, context)
        items = result.get("results") or ([result["result"]] if result.get("result") else [])
        return dev_server_pb2.GetTestResultsResponse(
            status=_proto_status(result),
            results=[self._test_result(item) for item in items if item],
        )

    def GetDiff(self, request, context):
        from generated.aegis import dev_server_pb2

        result = self._service.GetDiff(request, context)
        files = [
            dev_server_pb2.FileDiff(
                path=item.get("path", ""),
                status=item.get("status", ""),
                diff=item.get("diff", ""),
                additions=int(item.get("additions", 0)),
                deletions=int(item.get("deletions", 0)),
            )
            for item in result.get("files", [])
        ]
        return dev_server_pb2.GetDiffResponse(status=_proto_status(result), files=files)

    def CreateBranch(self, request, context):
        from generated.aegis import dev_server_pb2

        result = self._service.CreateBranch(request, context)
        return dev_server_pb2.CreateBranchResponse(
            status=_proto_status(result),
            branch_name=result.get("branch_name", ""),
        )

    def ApplyPatch(self, request, context):
        from generated.aegis import dev_server_pb2

        result = self._service.ApplyPatch(request, context)
        return dev_server_pb2.ApplyPatchResponse(
            status=_proto_status(result),
            applied=bool(result.get("applied", False)),
            error_detail=result.get("error_detail", ""),
        )

    def RunTests(self, request, context):
        from generated.aegis import dev_server_pb2

        result = self._service.RunTests(request, context)
        return dev_server_pb2.RunTestsResponse(
            status=_proto_status(result),
            result=self._test_result(result.get("result", {})),
        )

    def RunLint(self, request, context):
        from generated.aegis import dev_server_pb2

        result = self._service.RunLint(request, context)
        return dev_server_pb2.RunLintResponse(
            status=_proto_status(result),
            passed=bool(result.get("passed", False)),
            error_count=int(result.get("error_count", 0)),
            warning_count=int(result.get("warning_count", 0)),
            output=result.get("output", ""),
        )

    def CreateCommit(self, request, context):
        from generated.aegis import dev_server_pb2

        result = self._service.CreateCommit(request, context)
        return dev_server_pb2.CreateCommitResponse(
            status=_proto_status(result),
            commit_hash=result.get("commit_hash", ""),
        )

    def CreatePullRequest(self, request, context):
        from generated.aegis import dev_server_pb2

        result = self._service.CreatePullRequest(request, context)
        return dev_server_pb2.CreatePullRequestResponse(
            status=_proto_status(result),
            pr_url=result.get("pr_url", ""),
            pr_number=int(result.get("pr_number", 0)),
        )

    def RevertChanges(self, request, context):
        from generated.aegis import dev_server_pb2

        result = self._service.RevertChanges(request, context)
        return dev_server_pb2.RevertChangesResponse(
            status=_proto_status(result),
            reverted_files=list(result.get("reverted_files", [])),
        )

    @staticmethod
    def _test_result(item: dict):
        from generated.aegis import dev_server_pb2

        item = item or {}
        return dev_server_pb2.TestResult(
            suite=item.get("suite", ""),
            total=int(item.get("total", 0)),
            passed=int(item.get("passed", 0)),
            failed=int(item.get("failed", 0)),
            errors=int(item.get("errors", 0)),
            duration_sec=float(item.get("duration_sec", 0.0)),
            output=item.get("output", ""),
        )


def serve(host: str = "0.0.0.0", port: int = 50056, repo_path: str = ".") -> None:
    """Start the Dev Server gRPC server."""
    from generated.aegis import dev_server_pb2_grpc

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=4))
    service = DevServerService(repo_path=repo_path)
    dev_server_pb2_grpc.add_DevServerServicer_to_server(DevServerGrpcServicer(service), server)
    server.add_insecure_port(f"{host}:{port}")
    server.start()
    logger.info("Dev Server started on %s:%d (repo=%s)", host, port, repo_path)
    server.wait_for_termination()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    repo = os.getenv("AEGIS_REPO_PATH", ".")
    port = int(os.getenv("DEV_SERVER_PORT", "50056"))
    serve(port=port, repo_path=repo)
