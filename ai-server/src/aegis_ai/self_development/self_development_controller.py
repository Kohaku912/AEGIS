"""Self-Development Controller — orchestrates sandbox-based self-improvement."""

from __future__ import annotations

import json
import logging
import time
import uuid
from pathlib import Path
from typing import Any

from aegis_ai.self_development.sandbox_manager import SandboxManager
from aegis_ai.self_development.self_development_types import (
    CommandPolicy,
    SandboxInfo,
    SelfDevelopmentResult,
    SelfDevelopmentTask,
    SelfDevStatus,
)

logger = logging.getLogger("aegis_ai.self_development.controller")


class SelfDevelopmentController:
    """Orchestrates the full self-development workflow.

    Flow: plan → edit → test → verify → review → (approval) → merge

    Parameters
    ----------
    sandbox_manager:
        Manages sandbox creation and file operations.
    memory_store:
        Optional memory store for recording lessons.
    audit_log:
        Optional audit log.
    """

    def __init__(
        self,
        sandbox_manager: SandboxManager | None = None,
        memory_store: Any = None,
        audit_log: Any = None,
        data_dir: str = "data/self_development",
    ) -> None:
        self._sandbox = sandbox_manager or SandboxManager()
        self._memory = memory_store
        self._audit = audit_log
        self._data_dir = Path(data_dir)
        self._data_dir.mkdir(parents=True, exist_ok=True)
        self._tasks: dict[str, SelfDevelopmentTask] = {}
        self._results: dict[str, SelfDevelopmentResult] = {}
        self._load()

    # ── Task lifecycle ────────────────────────────────────────

    def create_task(
        self,
        title: str,
        description: str,
        target_repo: str,
        target_branch: str = "main",
        source: str = "user_explicit",
        source_desire: str = "",
        frustration: float = 0.0,
        motivation: str = "",
    ) -> SelfDevelopmentTask:
        task = SelfDevelopmentTask(
            self_dev_task_id=f"sdt_{uuid.uuid4().hex[:10]}",
            source=source,
            title=title,
            description=description,
            target_repo=target_repo,
            target_branch=target_branch,
            source_desire=source_desire,
            frustration=frustration,
            motivation=motivation,
            created_at=int(time.time() * 1000),
            status=SelfDevStatus.PLANNED.value,
        )
        self._tasks[task.self_dev_task_id] = task
        self._save()
        self._record_audit("task_created", task)
        return task

    def get_task(self, task_id: str) -> SelfDevelopmentTask | None:
        return self._tasks.get(task_id)

    def list_tasks(self, status: str | None = None) -> list[SelfDevelopmentTask]:
        tasks = list(self._tasks.values())
        if status:
            tasks = [t for t in tasks if t.status == status]
        return tasks

    # ── Workflow: plan → sandbox → edit → test → verify ───────

    def start_sandbox(self, task_id: str) -> SandboxInfo | None:
        """Create sandbox for a task."""
        task = self._tasks.get(task_id)
        if task is None:
            return None

        task.status = SelfDevStatus.SANDBOX_PREPARING.value
        self._save()

        sandbox = self._sandbox.create_sandbox(task.target_repo, task.target_branch)
        task.sandbox_id = sandbox.sandbox_id
        task.worktree_path = sandbox.worktree_path
        self._save()
        self._record_audit("sandbox_created", task)
        return sandbox

    def apply_changes(
        self,
        task_id: str,
        file_path: str,
        content: str,
    ) -> bool:
        """Apply a file change within the sandbox."""
        task = self._tasks.get(task_id)
        if task is None or not task.sandbox_id:
            return False

        ok, reason = self._sandbox.validate_file_path(task.sandbox_id, file_path)
        if not ok:
            logger.warning("File validation failed: %s — %s", file_path, reason)
            self._record_audit("edit_blocked", task, reason=f"{file_path}: {reason}")
            return False

        task.status = SelfDevStatus.EDITING.value
        self._save()

        success, msg = self._sandbox.write_file(task.sandbox_id, file_path, content)
        if success:
            self._record_audit("file_edited", task, reason=file_path)
        return success

    def run_tests(self, task_id: str, test_command: str = "pytest") -> dict[str, Any]:
        """Run tests in the sandbox."""
        task = self._tasks.get(task_id)
        if task is None or not task.sandbox_id:
            return {"success": False, "error": "No sandbox"}

        task.status = SelfDevStatus.TESTING.value
        self._save()

        parts = test_command.split()
        result = self._sandbox.execute_command(
            task.sandbox_id, parts[0], parts[1:] if len(parts) > 1 else [],
        )
        test_result = {
            "success": result.exit_code == 0 and result.policy == CommandPolicy.ALLOW,
            "exit_code": result.exit_code,
            "stdout": result.stdout[:1000],
            "stderr": result.stderr[:500],
            "command": test_command,
        }
        self._record_audit("tests_run", task, reason=f"exit={result.exit_code}")
        return test_result

    def run_lint(self, task_id: str, lint_command: str = "ruff check .") -> dict[str, Any]:
        """Run lint in the sandbox."""
        task = self._tasks.get(task_id)
        if task is None or not task.sandbox_id:
            return {"passed": False, "error": "No sandbox"}

        parts = lint_command.split()
        result = self._sandbox.execute_command(
            task.sandbox_id, parts[0], parts[1:] if len(parts) > 1 else [],
        )
        lint_result = {
            "passed": result.exit_code == 0 and result.policy == CommandPolicy.ALLOW,
            "exit_code": result.exit_code,
            "output": result.stdout[:1000],
            "errors": result.stderr[:500],
        }
        self._record_audit("lint_run", task, reason=f"passed={lint_result['passed']}")
        return lint_result

    def verify(self, task_id: str) -> str:
        """Run verification checks on sandbox changes."""
        task = self._tasks.get(task_id)
        if task is None or not task.sandbox_id:
            return "failed"

        issues: list[str] = []

        changed = self._sandbox.get_changed_files(task.sandbox_id)
        for f in changed:
            ok, reason = self._sandbox.validate_file_path(task.sandbox_id, f)
            if not ok:
                issues.append(f"Invalid file: {f} — {reason}")

        diff = self._sandbox.get_diff(task.sandbox_id)
        secret_markers = ["api_key=", "password=", "token=", "secret="]
        for marker in secret_markers:
            if marker in diff.lower():
                issues.append(f"Secret detected in diff: {marker}")
                break

        if issues:
            task.status = SelfDevStatus.VERIFICATION_FAILED.value
            self._save()
            self._record_audit("verification_failed", task, reason="; ".join(issues))
            return "failed"

        task.status = SelfDevStatus.READY_FOR_REVIEW.value
        self._save()
        self._record_audit("verification_passed", task)
        return "verified"

    def build_result(self, task_id: str) -> SelfDevelopmentResult:
        """Build a SelfDevelopmentResult from the current sandbox state."""
        task = self._tasks.get(task_id)
        result = SelfDevelopmentResult(
            self_dev_task_id=task_id,
            created_at=int(time.time() * 1000),
        )
        if task is None or not task.sandbox_id:
            return result

        result.changed_files = self._sandbox.get_changed_files(task.sandbox_id)
        result.diff_summary = self._sandbox.get_diff(task.sandbox_id)[:500]
        return result

    def discard(self, task_id: str) -> bool:
        """Discard sandbox changes and destroy sandbox."""
        task = self._tasks.get(task_id)
        if task is None:
            return False

        if task.sandbox_id:
            self._sandbox.destroy_sandbox(task.sandbox_id)

        task.status = SelfDevStatus.CANCELLED.value
        self._save()
        self._record_audit("task_discarded", task)
        return True

    def mark_approved(self, task_id: str) -> bool:
        task = self._tasks.get(task_id)
        if task is None:
            return False
        task.status = SelfDevStatus.APPROVED_FOR_MERGE.value
        task.requires_approval = False
        self._save()
        self._record_audit("task_approved", task)
        return True

    def mark_rejected(self, task_id: str, reason: str = "") -> bool:
        task = self._tasks.get(task_id)
        if task is None:
            return False
        task.status = SelfDevStatus.REJECTED.value
        self._save()
        self._record_audit("task_rejected", task, reason=reason)
        self._record_memory_lesson(task, "rejected", reason)
        return True

    def mark_failed(self, task_id: str, reason: str = "") -> bool:
        task = self._tasks.get(task_id)
        if task is None:
            return False
        task.status = SelfDevStatus.FAILED.value
        self._save()
        self._record_audit("task_failed", task, reason=reason)
        self._record_memory_lesson(task, "failed", reason)
        return True

    # ── Internal ──────────────────────────────────────────────

    def _record_audit(self, action: str, task: SelfDevelopmentTask, reason: str = "") -> None:
        if self._audit is None:
            return
        try:
            from aegis_ai.audit import AuditEntry
            entry = AuditEntry(
                action=f"selfdev_{action}",
                actor=task.source,
                capability_id="self_development",
                decision=task.status,
                reason=reason or task.title[:200],
                detail={
                    "task_id": task.self_dev_task_id,
                    "source": task.source,
                    "source_desire": task.source_desire,
                    "frustration": task.frustration,
                    "sandbox_id": task.sandbox_id,
                    "status": task.status,
                },
            )
            self._audit.append(entry)
        except Exception as exc:
            logger.warning("Failed to record audit: %s", exc)

    def _record_memory_lesson(
        self,
        task: SelfDevelopmentTask,
        outcome: str,
        reason: str = "",
    ) -> None:
        if self._memory is None:
            return
        try:
            from aegis_ai.memory.memory_types import (
                MemoryRecord,
                MemorySource,
                MemoryType,
                Sensitivity,
                Visibility,
            )
            mem_type = MemoryType.FAILURE_LESSON if outcome == "failed" else MemoryType.APPROVAL_LESSON
            self._memory.add_memory(MemoryRecord(
                memory_type=mem_type.value,
                title=f"Self-dev {outcome}: {task.title}",
                content=(
                    f"Task: {task.title}\nOutcome: {outcome}\n"
                    f"Reason: {reason}\nSource: {task.source}"
                    + (f"\nDesire: {task.source_desire} (frust={task.frustration:.1f})" if task.source_desire else "")
                ),
                source=MemorySource.REFLECTION.value,
                related_task_id=task.self_dev_task_id,
                related_desire=task.source_desire,
                structured_data={"outcome": outcome, "source": task.source},
                confidence=0.8,
                importance=0.7 if outcome == "failed" else 0.5,
                visibility=Visibility.LLM_VISIBLE.value,
                sensitivity=Sensitivity.NORMAL.value,
            ))
        except Exception as exc:
            logger.warning("Failed to record memory lesson: %s", exc)

    def _state_path(self) -> Path:
        return self._data_dir / "self_dev_tasks.json"

    def _save(self) -> None:
        data = {
            "tasks": {tid: t.to_dict() for tid, t in self._tasks.items()},
            "saved_at": int(time.time() * 1000),
        }
        try:
            with open(self._state_path(), "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as exc:
            logger.warning("Failed to save self-dev tasks: %s", exc)

    def _load(self) -> None:
        path = self._state_path()
        if not path.exists():
            return
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
            for tid, d in data.get("tasks", {}).items():
                self._tasks[tid] = SelfDevelopmentTask(**d)
            logger.info("Loaded %d self-dev tasks", len(self._tasks))
        except Exception as exc:
            logger.warning("Failed to load self-dev tasks: %s", exc)
