"""Tests for Dev Server — gRPC service implementation."""

from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path
from types import SimpleNamespace

import pytest

from generated.aegis import common_pb2, dev_server_pb2
from dev_server import DevServerGrpcServicer, DevServerService, _is_command_safe, _is_path_safe


def _git(repo: str, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=repo,
        capture_output=True,
        text=True,
        check=True,
    )


def _req(**kwargs: object) -> SimpleNamespace:
    return SimpleNamespace(**kwargs)


@pytest.fixture()
def tmpdir():
    d = tempfile.mkdtemp()
    yield d
    shutil.rmtree(d, ignore_errors=True)


@pytest.fixture()
def repo(tmpdir):
    _git(tmpdir, "init", "-b", "main")
    _git(tmpdir, "config", "user.email", "test@test.com")
    _git(tmpdir, "config", "user.name", "Test")
    (Path(tmpdir) / "test.py").write_text("print('hello')\n", encoding="utf-8")
    (Path(tmpdir) / "pyproject.toml").write_text("[project]\nname='tmp'\nversion='0'\n", encoding="utf-8")
    (Path(tmpdir) / "tests").mkdir()
    (Path(tmpdir) / "tests" / "test_smoke.py").write_text(
        "def test_ok():\n    assert True\n",
        encoding="utf-8",
    )
    _git(tmpdir, "add", "-A")
    _git(tmpdir, "commit", "-m", "init")
    return tmpdir


@pytest.fixture()
def service(repo):
    return DevServerService(repo_path=repo)


class TestHealthCheck:
    def test_health(self, service):
        result = service.HealthCheck(None, None)
        assert result["status"] == "ok"
        assert result["uptime_ms"] >= 0

    def test_grpc_health(self, service):
        grpc_service = DevServerGrpcServicer(service)
        result = grpc_service.HealthCheck(common_pb2.HealthCheckRequest(server_id="dev-server"), None)
        assert result.status.code == 0
        assert result.server_status == common_pb2.SERVER_STATUS_ONLINE


class TestGetRepoStatus:
    def test_repo_status(self, service):
        result = service.GetRepoStatus(None, None)
        assert result["status"] == "ok"
        assert result["branch"] == "main"
        assert result["commit_hash"]
        assert result["is_clean"] is True


class TestGetDiff:
    def test_diff_clean(self, service):
        result = service.GetDiff(_req(from_branch="main", to_branch="HEAD"), None)
        assert result["status"] == "ok"
        assert result["files"] == []

    def test_diff_with_committed_change(self, service, repo):
        _git(repo, "switch", "-c", "feature")
        path = Path(repo) / "test.py"
        path.write_text("print('hello')\nprint('world')\n", encoding="utf-8")
        _git(repo, "add", "test.py")
        _git(repo, "commit", "-m", "change")
        result = service.GetDiff(_req(from_branch="main", to_branch="HEAD"), None)
        assert result["status"] == "ok"
        assert any(item["path"] == "test.py" and item["diff"] for item in result["files"])


class TestRunTests:
    def test_run_tests(self, service):
        result = service.RunTests(_req(target="all", extra_args="", timeout_seconds=30), None)
        assert result["status"] == "ok"
        assert result["result"]["passed"] >= 1

    def test_get_test_results_remembers_last_run(self, service):
        assert service.GetTestResults(_req(target="", extra_args=""), None)["results"] == []
        service.RunTests(_req(target="all", extra_args="", timeout_seconds=30), None)
        cached = service.GetTestResults(_req(target="", extra_args=""), None)
        assert cached["results"]
        assert cached["results"][0]["passed"] >= 1

    def test_extra_args_shell_meta_rejected(self, service):
        result = service.RunTests(
            _req(target="all", extra_args="foo; rm -rf /", timeout_seconds=10),
            None,
        )
        assert result["status"] == "error"

    def test_grpc_run_tests_response(self, service):
        grpc_service = DevServerGrpcServicer(service)
        result = grpc_service.RunTests(
            dev_server_pb2.RunTestsRequest(target="all", extra_args="", timeout_seconds=30),
            None,
        )
        assert result.status.code == 0
        assert result.result.passed >= 1


class TestRunLint:
    def test_run_lint(self, service):
        result = service.RunLint(_req(target="all", linter="ruff"), None)
        assert result["status"] == "ok"


class TestCreateBranch:
    def test_create_branch(self, service):
        result = service.CreateBranch(_req(branch_name="test-branch", base_branch="main"), None)
        assert result["status"] == "ok"
        assert result["branch_name"] == "test-branch"
        status = service.GetRepoStatus(None, None)
        assert status["branch"] == "test-branch"

    def test_create_branch_no_name(self, service):
        result = service.CreateBranch(_req(branch_name="", base_branch="main"), None)
        assert result["status"] == "error"

    def test_switch_existing_branch(self, service):
        first = service.CreateBranch(_req(branch_name="feature-a", base_branch="main"), None)
        assert first["status"] == "ok"
        service.CreateBranch(_req(branch_name="main", base_branch=""), None)
        again = service.CreateBranch(_req(branch_name="feature-a", base_branch="main"), None)
        assert again["status"] == "ok"
        assert service.GetRepoStatus(None, None)["branch"] == "feature-a"


class TestApplyPatch:
    def test_apply_file_content(self, service, repo):
        result = service.ApplyPatch(_req(file_path="patch.py", patch_content="x = 42\n"), None)
        assert result["applied"] is True
        assert (Path(repo) / "patch.py").read_text(encoding="utf-8") == "x = 42\n"

    def test_apply_unified_diff(self, service, repo):
        original = (Path(repo) / "test.py").read_text(encoding="utf-8")
        (Path(repo) / "test.py").write_text(original + "print('patched')\n", encoding="utf-8")
        diff = subprocess.check_output(["git", "diff", "--", "test.py"], cwd=repo, text=True)
        (Path(repo) / "test.py").write_text(original, encoding="utf-8")
        result = service.ApplyPatch(_req(file_path="test.py", patch_content=diff), None)
        assert result["applied"] is True
        assert "patched" in (Path(repo) / "test.py").read_text(encoding="utf-8")

    def test_apply_patch_denied_path(self, service):
        result = service.ApplyPatch(_req(file_path=".env", patch_content="SECRET=1"), None)
        assert result["applied"] is False

    def test_apply_patch_parent_escape(self, service):
        result = service.ApplyPatch(_req(file_path="../outside.py", patch_content="x=1\n"), None)
        assert result["applied"] is False


class TestCreateCommit:
    def test_commit_on_main_denied(self, service, repo):
        (Path(repo) / "n.py").write_text("1\n", encoding="utf-8")
        result = service.CreateCommit(_req(message="nope", files=["n.py"]), None)
        assert result["status"] == "error"
        assert "forbidden" in result["message"].lower()

    def test_commit_on_branch(self, service, repo):
        service.CreateBranch(_req(branch_name="work", base_branch="main"), None)
        (Path(repo) / "n.py").write_text("1\n", encoding="utf-8")
        result = service.CreateCommit(_req(message="add n", files=["n.py"]), None)
        assert result["status"] == "ok"
        assert result["commit_hash"]


class TestCreatePullRequest:
    def test_manual_instructions_without_token(self, service, monkeypatch):
        monkeypatch.delenv("GITHUB_TOKEN", raising=False)
        result = service.CreatePullRequest(
            _req(title="Improve tests", description="body", head_branch="work", base_branch="main"),
            None,
        )
        assert result["status"] == "ok"
        assert result["pr_url"] == ""
        assert "gh pr create" in result["message"]


class TestRevertChanges:
    def test_revert_all(self, service, repo):
        (Path(repo) / "new.py").write_text("x = 1\n", encoding="utf-8")
        result = service.RevertChanges(_req(target="all", commit_hash=""), None)
        assert result["status"] == "ok"
        assert not (Path(repo) / "new.py").exists()

    def test_revert_specific_file(self, service, repo):
        (Path(repo) / "test.py").write_text("modified\n", encoding="utf-8")
        result = service.RevertChanges(_req(target="test.py", commit_hash=""), None)
        assert result["status"] == "ok"
        assert (Path(repo) / "test.py").read_text(encoding="utf-8") == "print('hello')\n"


class TestSafety:
    def test_denied_command(self):
        assert _is_command_safe("rm -rf /") is False
        assert _is_command_safe("sudo rm -rf /tmp") is False
        assert _is_command_safe("git push --force") is False
        assert _is_command_safe("| sh") is False
        assert _is_command_safe("echo hello") is True

    def test_denied_path(self):
        assert _is_path_safe(".env") is False
        assert _is_path_safe(".ssh/id_rsa") is False
        assert _is_path_safe("../../etc/passwd") is False
        assert _is_path_safe("src/main.py") is True
