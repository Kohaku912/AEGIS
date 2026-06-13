"""Tests for Dev Server — gRPC service implementation."""

from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path

import pytest

from dev_server import DevServerService


@pytest.fixture()
def tmpdir():
    d = tempfile.mkdtemp()
    yield d
    shutil.rmtree(d, ignore_errors=True)


@pytest.fixture()
def repo(tmpdir):
    subprocess.run(["git", "init"], cwd=tmpdir, capture_output=True)
    subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=tmpdir, capture_output=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=tmpdir, capture_output=True)
    (Path(tmpdir) / "test.py").write_text("print('hello')\n")
    subprocess.run(["git", "add", "-A"], cwd=tmpdir, capture_output=True)
    subprocess.run(["git", "commit", "-m", "init"], cwd=tmpdir, capture_output=True)
    return tmpdir


@pytest.fixture()
def service(repo):
    return DevServerService(repo_path=repo)


class TestHealthCheck:
    def test_health(self, service):
        result = service.HealthCheck(None, None)
        assert result["status"] == "ok"


class TestGetRepoStatus:
    def test_repo_status(self, service):
        result = service.GetRepoStatus(None, None)
        assert result["status"] == "ok"
        assert result["branch"]
        assert result["commit_hash"]
        assert result["is_clean"] is True


class TestGetDiff:
    def test_diff_clean(self, service):
        result = service.GetDiff(type("Req", (), {"from_branch": "main", "to_branch": "HEAD"})(), None)
        assert result["status"] == "ok"

    def test_diff_with_changes(self, service, repo):
        (Path(repo) / "new.py").write_text("x = 1\n")
        result = service.GetDiff(type("Req", (), {"from_branch": "main", "to_branch": "HEAD"})(), None)
        assert result["status"] == "ok"


class TestRunTests:
    def test_run_tests(self, service):
        req = type("Req", (), {"target": "", "extra_args": "echo ok", "timeout_seconds": 10})()
        result = service.RunTests(req, None)
        assert result["status"] == "ok"


class TestRunLint:
    def test_run_lint(self, service):
        req = type("Req", (), {"target": "", "linter": "ruff"})()
        result = service.RunLint(req, None)
        assert result["status"] == "ok"


class TestCreateBranch:
    def test_create_branch(self, service):
        req = type("Req", (), {"branch_name": "test-branch", "base_branch": "main"})()
        result = service.CreateBranch(req, None)
        assert result["status"] == "ok"
        assert result["branch_name"] == "test-branch"

    def test_create_branch_no_name(self, service):
        req = type("Req", (), {"branch_name": "", "base_branch": "main"})()
        result = service.CreateBranch(req, None)
        assert result["status"] == "error"


class TestApplyPatch:
    def test_apply_patch(self, service):
        req = type("Req", (), {"file_path": "patch.py", "patch_content": "x = 42\n"})()
        result = service.ApplyPatch(req, None)
        assert result["applied"] is True

    def test_apply_patch_denied_path(self, service):
        req = type("Req", (), {"file_path": ".env", "patch_content": "SECRET=1"})()
        result = service.ApplyPatch(req, None)
        assert result["applied"] is False


class TestRevertChanges:
    def test_revert_all(self, service, repo):
        (Path(repo) / "new.py").write_text("x = 1\n")
        req = type("Req", (), {"target": "all", "commit_hash": ""})()
        result = service.RevertChanges(req, None)
        assert result["status"] == "ok"

    def test_revert_specific_file(self, service, repo):
        (Path(repo) / "test.py").write_text("modified\n")
        req = type("Req", (), {"target": "test.py", "commit_hash": ""})()
        result = service.RevertChanges(req, None)
        assert result["status"] == "ok"


class TestSafety:
    def test_denied_command(self, service):
        from dev_server import _is_command_safe
        assert _is_command_safe("rm -rf /") is False
        assert _is_command_safe("sudo rm -rf /tmp") is False
        assert _is_command_safe("git push --force") is False
        assert _is_command_safe("| sh") is False
        assert _is_command_safe("echo hello") is True

    def test_denied_path(self, service):
        from dev_server import _is_path_safe
        assert _is_path_safe(".env") is False
        assert _is_path_safe(".ssh/id_rsa") is False
        assert _is_path_safe("../../etc/passwd") is False
        assert _is_path_safe("src/main.py") is True
