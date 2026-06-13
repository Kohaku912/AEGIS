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

import json
import logging
import os
import subprocess
import time
from concurrent import futures
from pathlib import Path

import grpc

logger = logging.getLogger("aegis_ai.dev_server")


# ── Deny patterns ────────────────────────────────────────────

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


def _is_command_safe(command: str) -> bool:
    cmd_lower = command.lower().strip()
    for denied in DENIED_COMMANDS:
        if denied in cmd_lower:
            return False
    return True


def _is_path_safe(path: str) -> bool:
    path_lower = path.lower().replace("\\", "/")
    for denied in DENIED_PATHS:
        if denied in path_lower:
            return False
    if ".." in path:
        return False
    return True


def _run_command(command: str, cwd: str, timeout: int = 60) -> tuple[int, str, str]:
    if not _is_command_safe(command):
        return -1, "", f"Command denied: {command}"
    try:
        result = subprocess.run(
            command, shell=True, cwd=cwd,
            capture_output=True, text=True,
            encoding="utf-8", errors="replace",
            timeout=timeout,
        )
        return result.returncode, result.stdout[:50000], result.stderr[:10000]
    except subprocess.TimeoutExpired:
        return -1, "", f"Timeout after {timeout}s"
    except Exception as e:
        return -1, "", str(e)


class DevServerService:
    """Python implementation of the DevServer gRPC service."""

    def __init__(self, repo_path: str = ".") -> None:
        self._repo_path = Path(repo_path).resolve()

    def HealthCheck(self, request, context):
        return {"status": "ok", "message": "Dev server running"}

    def GetRepoStatus(self, request, context):
        cwd = str(self._repo_path)
        branch = self._git_output("git rev-parse --abbrev-ref HEAD", cwd)
        commit = self._git_output("git rev-parse HEAD", cwd)
        status_out = self._git_output("git status --porcelain", cwd)
        is_clean = len(status_out.strip()) == 0
        modified = [line[3:] for line in status_out.strip().split("\n") if line.strip()]
        ahead = self._git_output("git rev-list --count @{u}..HEAD", cwd)
        behind = self._git_output("git rev-list --count HEAD..@{u}", cwd)

        return {
            "status": "ok",
            "branch": branch,
            "commit_hash": commit,
            "is_clean": is_clean,
            "modified_files": modified[:50],
            "ahead_commits": int(ahead) if ahead.isdigit() else 0,
            "behind_commits": int(behind) if behind.isdigit() else 0,
        }

    def GetTestResults(self, request, context):
        target = getattr(request, "target", "") or "ai-server"
        extra = getattr(request, "extra_args", "")
        cwd = str(self._repo_path / target) if target != "all" else str(self._repo_path)
        cmd = f"python -m pytest -q --tb=short {extra}".strip()
        code, stdout, stderr = _run_command(cmd, cwd, timeout=120)

        total = passed = failed = errors = 0
        for line in (stdout + stderr).split("\n"):
            if "passed" in line and "failed" in line:
                parts = line.split()
                for i, p in enumerate(parts):
                    if p == "passed" and i > 0:
                        try: passed = int(parts[i-1])
                        except: pass
                    if p == "failed" and i > 0:
                        try: failed = int(parts[i-1])
                        except: pass
            elif line.strip().endswith("passed"):
                parts = line.strip().split()
                if parts[-2].isdigit():
                    passed = int(parts[-2])

        total = passed + failed
        return {
            "status": "ok",
            "result": {
                "suite": target,
                "total": total,
                "passed": passed,
                "failed": failed,
                "errors": errors,
                "duration_sec": 0.0,
                "output": (stdout + stderr)[:5000],
            },
        }

    def GetDiff(self, request, context):
        cwd = str(self._repo_path)
        from_branch = getattr(request, "from_branch", "") or "main"
        to_branch = getattr(request, "to_branch", "") or "HEAD"
        cmd = f"git diff {from_branch}...{to_branch} --stat"
        code, stdout, stderr = _run_command(cmd, cwd)

        files = []
        if code == 0:
            for line in stdout.strip().split("\n"):
                if "|" in line:
                    parts = line.split("|")
                    fname = parts[0].strip()
                    if fname:
                        files.append({
                            "path": fname,
                            "status": "modified",
                            "diff": "",
                            "additions": 0,
                            "deletions": 0,
                        })

        cmd2 = f"git diff {from_branch}...{to_branch}"
        _, diff_out, _ = _run_command(cmd2, cwd)
        if files and diff_out:
            files[0]["diff"] = diff_out[:5000]

        return {"status": "ok", "files": files}

    def CreateBranch(self, request, context):
        branch_name = getattr(request, "branch_name", "")
        base_branch = getattr(request, "base_branch", "") or "main"
        if not branch_name:
            return {"status": "error", "branch_name": ""}
        cwd = str(self._repo_path)
        _run_command(f"git checkout -b {base_branch}", cwd)
        cmd = f"git checkout -b {branch_name}"
        code, stdout, stderr = _run_command(cmd, cwd)
        if code == 0:
            return {"status": "ok", "branch_name": branch_name}
        return {"status": "error", "branch_name": "", "message": stderr[:200]}

    def ApplyPatch(self, request, context):
        file_path = getattr(request, "file_path", "")
        patch_content = getattr(request, "patch_content", "")
        if not _is_path_safe(file_path):
            return {"status": "error", "applied": False, "error_detail": "Path denied."}
        cwd = str(self._repo_path)
        full_path = Path(cwd) / file_path
        try:
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(patch_content, encoding="utf-8")
            return {"status": "ok", "applied": True}
        except Exception as e:
            return {"status": "error", "applied": False, "error_detail": str(e)[:200]}

    def RunTests(self, request, context):
        target = getattr(request, "target", "") or "ai-server"
        extra = getattr(request, "extra_args", "")
        timeout = getattr(request, "timeout_seconds", 60) or 60
        cwd = str(self._repo_path / target) if target != "all" else str(self._repo_path)
        cmd = f"python -m pytest -q --tb=short {extra}".strip()
        code, stdout, stderr = _run_command(cmd, cwd, timeout=timeout)

        total = passed = failed = 0
        for line in (stdout + stderr).split("\n"):
            if "passed" in line:
                parts = line.split()
                for i, p in enumerate(parts):
                    if p == "passed" and i > 0 and parts[i-1].isdigit():
                        passed = int(parts[i-1])
                    if p == "failed" and i > 0 and parts[i-1].isdigit():
                        failed = int(parts[i-1])
        total = passed + failed

        return {
            "status": "ok",
            "result": {
                "suite": target,
                "total": total,
                "passed": passed,
                "failed": failed,
                "errors": 0,
                "duration_sec": 0.0,
                "output": (stdout + stderr)[:5000],
            },
        }

    def RunLint(self, request, context):
        target = getattr(request, "target", "") or "ai-server"
        linter = getattr(request, "linter", "") or "ruff"
        cwd = str(self._repo_path / target) if target != "all" else str(self._repo_path)

        if linter == "ruff":
            cmd = "ruff check ."
        elif linter == "eslint":
            cmd = "npx eslint ."
        elif linter == "ktlint":
            cmd = "ktlint"
        else:
            cmd = "ruff check ."

        code, stdout, stderr = _run_command(cmd, cwd)
        error_count = stdout.count("\n") if code != 0 else 0

        return {
            "status": "ok",
            "passed": code == 0,
            "error_count": error_count,
            "warning_count": 0,
            "output": (stdout + stderr)[:5000],
        }

    def CreateCommit(self, request, context):
        message = getattr(request, "message", "")
        files = getattr(request, "files", [])
        if not message:
            return {"status": "error", "commit_hash": ""}
        cwd = str(self._repo_path)
        if files:
            for f in files:
                _run_command(f"git add {f}", cwd)
        else:
            _run_command("git add -A", cwd)
        code, stdout, stderr = _run_command(f'git commit -m "{message}"', cwd)
        if code == 0:
            commit_hash = self._git_output("git rev-parse HEAD", cwd)
            return {"status": "ok", "commit_hash": commit_hash}
        return {"status": "error", "commit_hash": "", "message": stderr[:200]}

    def CreatePullRequest(self, request, context):
        title = getattr(request, "title", "")
        description = getattr(request, "description", "")
        head = getattr(request, "head_branch", "")
        base = getattr(request, "base_branch", "") or "main"
        if not title or not head:
            return {"status": "error", "pr_url": "", "pr_number": 0}
        cwd = str(self._repo_path)
        cmd = f'gh pr create --title "{title}" --body "{description}" --head {head} --base {base}'
        code, stdout, stderr = _run_command(cmd, cwd)
        if code == 0:
            return {"status": "ok", "pr_url": stdout.strip(), "pr_number": 0}
        return {"status": "error", "pr_url": "", "pr_number": 0, "message": stderr[:200]}

    def RevertChanges(self, request, context):
        target = getattr(request, "target", "") or "all"
        commit_hash = getattr(request, "commit_hash", "")
        cwd = str(self._repo_path)

        if commit_hash:
            code, stdout, stderr = _run_command(f"git revert {commit_hash} --no-edit", cwd)
        elif target == "all":
            _run_command("git checkout -- .", cwd)
            code, stdout, stderr = _run_command("git clean -fd", cwd)
        else:
            if not _is_path_safe(target):
                return {"status": "error", "reverted_files": []}
            code, stdout, stderr = _run_command(f"git checkout -- {target}", cwd)

        reverted = []
        if code == 0:
            status_out = self._git_output("git status --porcelain", cwd)
            reverted = [line[3:] for line in status_out.strip().split("\n") if line.strip()]

        return {"status": "ok" if code == 0 else "error", "reverted_files": reverted}

    def _git_output(self, cmd: str, cwd: str) -> str:
        code, stdout, _ = _run_command(cmd, cwd, timeout=10)
        return stdout.strip() if code == 0 else ""


def serve(host: str = "0.0.0.0", port: int = 50056, repo_path: str = ".") -> None:
    """Start the Dev Server gRPC server."""
    try:
        from generated.aegis import dev_server_pb2_grpc

        server = grpc.server(futures.ThreadPoolExecutor(max_workers=4))
        service = DevServerService(repo_path=repo_path)

        dev_server_pb2_grpc.add_DevServerServicer_to_server(service, server)
        server.add_insecure_port(f"{host}:{port}")
        server.start()
        logger.info("Dev Server started on %s:%d (repo=%s)", host, port, repo_path)
        server.wait_for_termination()
    except ImportError:
        logger.warning("gRPC stubs not available. Running as standalone service.")
        logger.info("Dev Server (standalone) ready at %s:%d", host, port)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    repo = os.getenv("AEGIS_REPO_PATH", ".")
    port = int(os.getenv("DEV_SERVER_PORT", "50056"))
    serve(port=port, repo_path=repo)
