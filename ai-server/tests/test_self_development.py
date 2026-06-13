"""Tests for Self-Development Sandbox module."""

from __future__ import annotations

import shutil
import tempfile

import pytest

from aegis_ai.self_development.sandbox_manager import SandboxManager
from aegis_ai.self_development.self_development_controller import SelfDevelopmentController
from aegis_ai.self_development.self_development_types import (
    CommandPolicy,
    SelfDevelopmentResult,
    SelfDevelopmentTask,
    SelfDevStatus,
    _mask_secrets,
    classify_command,
    is_secret_path,
)


@pytest.fixture()
def tmpdir():
    d = tempfile.mkdtemp()
    yield d
    shutil.rmtree(d, ignore_errors=True)


@pytest.fixture()
def repo_dir(tmpdir):
    """Create a fake git repo for testing."""
    import pathlib
    import subprocess
    repo = pathlib.Path(tmpdir) / "repo"
    repo.mkdir()
    subprocess.run(["git", "init", str(repo)], capture_output=True, timeout=10)
    subprocess.run(["git", "-C", str(repo), "config", "user.email", "test@test"], capture_output=True, timeout=5)
    subprocess.run(["git", "-C", str(repo), "config", "user.name", "test"], capture_output=True, timeout=5)
    subprocess.run(["git", "-C", str(repo), "checkout", "-b", "main"], capture_output=True, timeout=5)
    (repo / "README.md").write_text("# test\n")
    subprocess.run(["git", "-C", str(repo), "add", "."], capture_output=True, timeout=5)
    subprocess.run(["git", "-C", str(repo), "commit", "-m", "init"], capture_output=True, timeout=5)
    return str(repo)


class TestSelfDevTypes:
    def test_classify_command_allowed(self):
        assert classify_command("pytest") == CommandPolicy.ALLOW
        assert classify_command("ruff check .") == CommandPolicy.ALLOW
        assert classify_command("git status") == CommandPolicy.ALLOW

    def test_classify_command_denied(self):
        assert classify_command("rm -rf /") == CommandPolicy.DENY
        assert classify_command("sudo apt install") == CommandPolicy.DENY
        assert classify_command("git push origin main") == CommandPolicy.DENY
        assert classify_command("git reset --hard") == CommandPolicy.DENY
        assert classify_command("pip install requests") == CommandPolicy.DENY

    def test_classify_command_approval(self):
        assert classify_command("git checkout feature") == CommandPolicy.ASK_APPROVAL
        assert classify_command("npm run build") == CommandPolicy.ASK_APPROVAL

    def test_is_secret_path(self):
        assert is_secret_path(".env") is True
        assert is_secret_path(".env.local") is True
        assert is_secret_path(".ssh/id_rsa") is True
        assert is_secret_path(".git/config") is True
        assert is_secret_path("src/main.py") is False
        assert is_secret_path("tests/test.py") is False

    def test_mask_secrets(self):
        text = "api_key=sk-abcdef1234567890abcdef1234567890 password=hunter2"
        masked = _mask_secrets(text)
        assert "sk-abcdef" not in masked
        assert "hunter2" not in masked

    def test_self_dev_task_to_dict(self):
        task = SelfDevelopmentTask(
            self_dev_task_id="sdt1", title="Fix bug",
            source="desire_driven", source_desire="reliability",
        )
        d = task.to_dict()
        assert d["self_dev_task_id"] == "sdt1"
        assert d["source"] == "desire_driven"

    def test_self_dev_result_to_dict(self):
        result = SelfDevelopmentResult(
            self_dev_task_id="sdt1",
            diff_summary="api_key=secret123 changed a function",
            changed_files=["src/main.py"],
        )
        d = result.to_dict()
        assert "secret123" not in d["diff_summary"]


class TestSandboxManager:
    def test_create_sandbox(self, repo_dir, tmpdir):
        mgr = SandboxManager(base_dir=f"{tmpdir}/sandboxes")
        info = mgr.create_sandbox(repo_dir)
        assert info.sandbox_id
        assert info.active is True
        assert info.branch_name.startswith("aegis/selfdev/")

    def test_list_sandboxes(self, repo_dir, tmpdir):
        mgr = SandboxManager(base_dir=f"{tmpdir}/sandboxes")
        mgr.create_sandbox(repo_dir)
        mgr.create_sandbox(repo_dir)
        assert len(mgr.list_sandboxes()) == 2

    def test_destroy_sandbox(self, repo_dir, tmpdir):
        mgr = SandboxManager(base_dir=f"{tmpdir}/sandboxes")
        info = mgr.create_sandbox(repo_dir)
        assert mgr.destroy_sandbox(info.sandbox_id) is True
        assert len(mgr.list_sandboxes()) == 0

    def test_validate_file_path_inside_sandbox(self, repo_dir, tmpdir):
        mgr = SandboxManager(base_dir=f"{tmpdir}/sandboxes")
        info = mgr.create_sandbox(repo_dir)
        ok, reason = mgr.validate_file_path(info.sandbox_id, "src/main.py")
        assert ok is True

    def test_validate_file_path_traversal(self, repo_dir, tmpdir):
        mgr = SandboxManager(base_dir=f"{tmpdir}/sandboxes")
        info = mgr.create_sandbox(repo_dir)
        ok, reason = mgr.validate_file_path(info.sandbox_id, "../../etc/passwd")
        assert ok is False
        assert "traversal" in reason.lower() or "path" in reason.lower()

    def test_validate_secret_path(self, repo_dir, tmpdir):
        mgr = SandboxManager(base_dir=f"{tmpdir}/sandboxes")
        info = mgr.create_sandbox(repo_dir)
        ok, reason = mgr.validate_file_path(info.sandbox_id, ".env")
        assert ok is False

    def test_execute_allowed_command(self, repo_dir, tmpdir):
        mgr = SandboxManager(base_dir=f"{tmpdir}/sandboxes")
        info = mgr.create_sandbox(repo_dir)
        result = mgr.execute_command(info.sandbox_id, "git", ["status"])
        assert result.exit_code == 0

    def test_execute_denied_command(self, repo_dir, tmpdir):
        mgr = SandboxManager(base_dir=f"{tmpdir}/sandboxes")
        info = mgr.create_sandbox(repo_dir)
        result = mgr.execute_command(info.sandbox_id, "rm -rf /")
        assert result.policy == CommandPolicy.DENY
        assert result.exit_code == -1

    def test_execute_approval_command(self, repo_dir, tmpdir):
        mgr = SandboxManager(base_dir=f"{tmpdir}/sandboxes")
        info = mgr.create_sandbox(repo_dir)
        result = mgr.execute_command(info.sandbox_id, "git checkout feature")
        assert result.policy == CommandPolicy.ASK_APPROVAL

    def test_dry_run_no_execution(self, repo_dir, tmpdir):
        mgr = SandboxManager(base_dir=f"{tmpdir}/sandboxes")
        info = mgr.create_sandbox(repo_dir)
        result = mgr.execute_command(info.sandbox_id, "echo", ["test"], dry_run=True)
        assert result.exit_code == 0
        assert "dry_run" in result.stdout

    def test_write_and_read_file(self, repo_dir, tmpdir):
        mgr = SandboxManager(base_dir=f"{tmpdir}/sandboxes")
        info = mgr.create_sandbox(repo_dir)
        ok, _ = mgr.write_file(info.sandbox_id, "test.txt", "hello world")
        assert ok is True
        ok, content = mgr.read_file(info.sandbox_id, "test.txt")
        assert ok is True
        assert "hello world" in content

    def test_write_secret_path_blocked(self, repo_dir, tmpdir):
        mgr = SandboxManager(base_dir=f"{tmpdir}/sandboxes")
        info = mgr.create_sandbox(repo_dir)
        ok, reason = mgr.write_file(info.sandbox_id, ".env", "SECRET=abc")
        assert ok is False

    def test_get_diff(self, repo_dir, tmpdir):
        mgr = SandboxManager(base_dir=f"{tmpdir}/sandboxes")
        info = mgr.create_sandbox(repo_dir)
        mgr.write_file(info.sandbox_id, "new.txt", "new content")
        changed = mgr.get_changed_files(info.sandbox_id)
        assert "new.txt" in changed

    def test_discard_changes(self, repo_dir, tmpdir):
        mgr = SandboxManager(base_dir=f"{tmpdir}/sandboxes")
        info = mgr.create_sandbox(repo_dir)
        mgr.write_file(info.sandbox_id, "temp.txt", "temp")
        assert mgr.discard_changes(info.sandbox_id) is True

    def test_persistence(self, repo_dir, tmpdir):
        mgr1 = SandboxManager(base_dir=f"{tmpdir}/sandboxes")
        info = mgr1.create_sandbox(repo_dir)
        mgr2 = SandboxManager(base_dir=f"{tmpdir}/sandboxes")
        assert len(mgr2.list_sandboxes()) == 1
        assert mgr2.get_sandbox(info.sandbox_id) is not None


class TestSelfDevelopmentController:
    def test_create_task(self, tmpdir):
        ctrl = SelfDevelopmentController(data_dir=f"{tmpdir}/sdev")
        task = ctrl.create_task(
            title="Fix memory leak",
            description="Fix the leak in memory module",
            target_repo="/tmp/repo",
            source="desire_driven",
            source_desire="reliability",
            frustration=6.0,
        )
        assert task.self_dev_task_id
        assert task.status == SelfDevStatus.PLANNED.value
        assert task.source_desire == "reliability"

    def test_get_task(self, tmpdir):
        ctrl = SelfDevelopmentController(data_dir=f"{tmpdir}/sdev")
        task = ctrl.create_task(title="Test", description="desc", target_repo="/tmp")
        assert ctrl.get_task(task.self_dev_task_id) is not None

    def test_list_tasks(self, tmpdir):
        ctrl = SelfDevelopmentController(data_dir=f"{tmpdir}/sdev")
        ctrl.create_task(title="A", description="", target_repo="/tmp")
        ctrl.create_task(title="B", description="", target_repo="/tmp")
        assert len(ctrl.list_tasks()) == 2
        assert len(ctrl.list_tasks(status="planned")) == 2

    def test_start_sandbox(self, repo_dir, tmpdir):
        ctrl = SelfDevelopmentController(data_dir=f"{tmpdir}/sdev")
        task = ctrl.create_task(title="Test", description="", target_repo=repo_dir)
        sandbox = ctrl.start_sandbox(task.self_dev_task_id)
        assert sandbox is not None
        assert sandbox.active is True
        assert ctrl.get_task(task.self_dev_task_id).sandbox_id

    def test_apply_changes(self, repo_dir, tmpdir):
        ctrl = SelfDevelopmentController(data_dir=f"{tmpdir}/sdev")
        task = ctrl.create_task(title="Test", description="", target_repo=repo_dir)
        ctrl.start_sandbox(task.self_dev_task_id)
        ok = ctrl.apply_changes(task.self_dev_task_id, "src/new.py", "print('hello')")
        assert ok is True
        assert ctrl.get_task(task.self_dev_task_id).status == SelfDevStatus.EDITING.value

    def test_apply_changes_blocked_for_env(self, repo_dir, tmpdir):
        ctrl = SelfDevelopmentController(data_dir=f"{tmpdir}/sdev")
        task = ctrl.create_task(title="Test", description="", target_repo=repo_dir)
        ctrl.start_sandbox(task.self_dev_task_id)
        ok = ctrl.apply_changes(task.self_dev_task_id, ".env", "SECRET=abc")
        assert ok is False

    def test_run_tests(self, repo_dir, tmpdir):
        ctrl = SelfDevelopmentController(data_dir=f"{tmpdir}/sdev")
        task = ctrl.create_task(title="Test", description="", target_repo=repo_dir)
        ctrl.start_sandbox(task.self_dev_task_id)
        result = ctrl.run_tests(task.self_dev_task_id, "git branch")
        assert "success" in result
        assert "exit_code" in result
        assert "command" in result

    def test_verify_passes(self, repo_dir, tmpdir):
        ctrl = SelfDevelopmentController(data_dir=f"{tmpdir}/sdev")
        task = ctrl.create_task(title="Test", description="", target_repo=repo_dir)
        ctrl.start_sandbox(task.self_dev_task_id)
        status = ctrl.verify(task.self_dev_task_id)
        assert status == "verified"

    def test_build_result(self, repo_dir, tmpdir):
        ctrl = SelfDevelopmentController(data_dir=f"{tmpdir}/sdev")
        task = ctrl.create_task(title="Test", description="", target_repo=repo_dir)
        ctrl.start_sandbox(task.self_dev_task_id)
        result = ctrl.build_result(task.self_dev_task_id)
        assert result.self_dev_task_id == task.self_dev_task_id

    def test_discard(self, repo_dir, tmpdir):
        ctrl = SelfDevelopmentController(data_dir=f"{tmpdir}/sdev")
        task = ctrl.create_task(title="Test", description="", target_repo=repo_dir)
        ctrl.start_sandbox(task.self_dev_task_id)
        assert ctrl.discard(task.self_dev_task_id) is True
        assert ctrl.get_task(task.self_dev_task_id).status == SelfDevStatus.CANCELLED.value

    def test_mark_approved(self, tmpdir):
        ctrl = SelfDevelopmentController(data_dir=f"{tmpdir}/sdev")
        task = ctrl.create_task(title="Test", description="", target_repo="/tmp")
        assert ctrl.mark_approved(task.self_dev_task_id) is True
        assert ctrl.get_task(task.self_dev_task_id).status == SelfDevStatus.APPROVED_FOR_MERGE.value

    def test_mark_rejected(self, tmpdir):
        ctrl = SelfDevelopmentController(data_dir=f"{tmpdir}/sdev")
        task = ctrl.create_task(title="Test", description="", target_repo="/tmp")
        assert ctrl.mark_rejected(task.self_dev_task_id, "too risky") is True
        assert ctrl.get_task(task.self_dev_task_id).status == SelfDevStatus.REJECTED.value

    def test_mark_failed(self, tmpdir):
        ctrl = SelfDevelopmentController(data_dir=f"{tmpdir}/sdev")
        task = ctrl.create_task(title="Test", description="", target_repo="/tmp")
        assert ctrl.mark_failed(task.self_dev_task_id, "tests broke") is True
        assert ctrl.get_task(task.self_dev_task_id).status == SelfDevStatus.FAILED.value

    def test_persistence(self, tmpdir):
        ctrl1 = SelfDevelopmentController(data_dir=f"{tmpdir}/sdev")
        task = ctrl1.create_task(title="Persist", description="", target_repo="/tmp")
        ctrl2 = SelfDevelopmentController(data_dir=f"{tmpdir}/sdev")
        assert ctrl2.get_task(task.self_dev_task_id) is not None

    def test_full_workflow(self, repo_dir, tmpdir):
        ctrl = SelfDevelopmentController(data_dir=f"{tmpdir}/sdev")
        task = ctrl.create_task(
            title="Add test file",
            description="Add a test file to the repo",
            target_repo=repo_dir,
            source="desire_driven",
            source_desire="reliability",
        )
        sandbox = ctrl.start_sandbox(task.self_dev_task_id)
        assert sandbox is not None

        ok = ctrl.apply_changes(task.self_dev_task_id, "test_new.py", "def test_ok(): assert True")
        assert ok is True

        result = ctrl.run_tests(task.self_dev_task_id, "git log --oneline -1")
        assert result["success"] is True

        status = ctrl.verify(task.self_dev_task_id)
        assert status == "verified"

        dev_result = ctrl.build_result(task.self_dev_task_id)
        assert dev_result.self_dev_task_id == task.self_dev_task_id

        assert ctrl.mark_approved(task.self_dev_task_id) is True
        assert ctrl.get_task(task.self_dev_task_id).status == SelfDevStatus.APPROVED_FOR_MERGE.value
