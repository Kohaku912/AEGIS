"""gRPC client adapter for Dev Server capabilities."""

from __future__ import annotations

import os
from typing import Any

import grpc

from generated.aegis import common_pb2, dev_server_pb2, dev_server_pb2_grpc


class DevServerGrpcClient:
    """Adapter used by ServerExecutor for canonical dev-server capabilities."""

    def __init__(self, host: str | None = None, port: int | None = None, timeout_seconds: float = 30.0) -> None:
        self.host = host or os.getenv("DEV_SERVER_HOST", "localhost")
        self.port = port or int(os.getenv("DEV_SERVER_PORT", "50056"))
        self.timeout_seconds = timeout_seconds

    def invoke_capability(self, capability_id: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        params = params or {}
        try:
            with grpc.insecure_channel(f"{self.host}:{self.port}") as channel:
                stub = dev_server_pb2_grpc.DevServerStub(channel)
                if capability_id == "dev-server.system.health_check":
                    return self._health_check(stub)
                if capability_id == "dev-server.repo.status":
                    return self._get_repo_status(stub)
                if capability_id == "dev-server.test.get_results":
                    return self._get_test_results(stub, params)
                if capability_id == "dev-server.diff.get_diff":
                    return self._get_diff(stub, params)
                if capability_id == "dev-server.branch.create":
                    return self._create_branch(stub, params)
                if capability_id == "dev-server.patch.apply":
                    return self._apply_patch(stub, params)
                if capability_id == "dev-server.test.run_tests":
                    return self._run_tests(stub, params)
                if capability_id == "dev-server.lint.run_lint":
                    return self._run_lint(stub, params)
                if capability_id == "dev-server.git.create_commit":
                    return self._create_commit(stub, params)
                if capability_id == "dev-server.pr.create":
                    return self._create_pull_request(stub, params)
                if capability_id == "dev-server.git.revert_changes":
                    return self._revert_changes(stub, params)
                return {"error": f"Unsupported Dev capability: {capability_id}", "capability_id": capability_id}
        except grpc.RpcError as exc:
            return {
                "error": f"Dev server gRPC error: {exc.code().name}: {exc.details()}",
                "capability_id": capability_id,
            }
        except Exception as exc:
            return {"error": f"Dev server execution error: {exc}", "capability_id": capability_id}

    def _health_check(self, stub: dev_server_pb2_grpc.DevServerStub) -> dict[str, Any]:
        response = stub.HealthCheck(common_pb2.HealthCheckRequest(), timeout=self.timeout_seconds)
        return {
            **self._status_dict(response.status),
            "server_status": int(response.server_status),
            "uptime_ms": int(response.uptime_ms),
            "version": response.version,
        }

    def _get_repo_status(self, stub: dev_server_pb2_grpc.DevServerStub) -> dict[str, Any]:
        response = stub.GetRepoStatus(dev_server_pb2.GetRepoStatusRequest(), timeout=self.timeout_seconds)
        return {
            **self._status_dict(response.status),
            "branch": response.branch,
            "commit_hash": response.commit_hash,
            "is_clean": response.is_clean,
            "modified_files": list(response.modified_files),
            "ahead_commits": int(response.ahead_commits),
            "behind_commits": int(response.behind_commits),
        }

    def _get_test_results(self, stub: dev_server_pb2_grpc.DevServerStub, params: dict[str, Any]) -> dict[str, Any]:
        response = stub.GetTestResults(
            dev_server_pb2.GetTestResultsRequest(
                target=str(params.get("target", "") or ""),
                extra_args=str(params.get("extra_args", "") or ""),
            ),
            timeout=self.timeout_seconds,
        )
        return {**self._status_dict(response.status), "results": [self._test_result_to_dict(item) for item in response.results]}

    def _get_diff(self, stub: dev_server_pb2_grpc.DevServerStub, params: dict[str, Any]) -> dict[str, Any]:
        response = stub.GetDiff(
            dev_server_pb2.GetDiffRequest(
                from_branch=str(params.get("from_branch", "") or ""),
                to_branch=str(params.get("to_branch", "") or ""),
            ),
            timeout=self.timeout_seconds,
        )
        return {**self._status_dict(response.status), "files": [self._file_diff_to_dict(item) for item in response.files]}

    def _create_branch(self, stub: dev_server_pb2_grpc.DevServerStub, params: dict[str, Any]) -> dict[str, Any]:
        response = stub.CreateBranch(
            dev_server_pb2.CreateBranchRequest(
                branch_name=str(params.get("branch_name", "") or ""),
                base_branch=str(params.get("base_branch", "") or ""),
            ),
            timeout=self.timeout_seconds,
        )
        return {**self._status_dict(response.status), "branch_name": response.branch_name}

    def _apply_patch(self, stub: dev_server_pb2_grpc.DevServerStub, params: dict[str, Any]) -> dict[str, Any]:
        response = stub.ApplyPatch(
            dev_server_pb2.ApplyPatchRequest(
                file_path=str(params.get("file_path", "") or ""),
                patch_content=str(params.get("patch_content", "") or ""),
            ),
            timeout=self.timeout_seconds,
        )
        return {
            **self._status_dict(response.status),
            "applied": response.applied,
            "error_detail": response.error_detail,
        }

    def _run_tests(self, stub: dev_server_pb2_grpc.DevServerStub, params: dict[str, Any]) -> dict[str, Any]:
        response = stub.RunTests(
            dev_server_pb2.RunTestsRequest(
                target=str(params.get("target", "") or ""),
                extra_args=str(params.get("extra_args", "") or ""),
                timeout_seconds=int(params.get("timeout_seconds", 0) or 0),
            ),
            timeout=max(self.timeout_seconds, float(params.get("timeout_seconds", 0) or 0) + 5.0),
        )
        return {**self._status_dict(response.status), "result": self._test_result_to_dict(response.result)}

    def _run_lint(self, stub: dev_server_pb2_grpc.DevServerStub, params: dict[str, Any]) -> dict[str, Any]:
        response = stub.RunLint(
            dev_server_pb2.RunLintRequest(
                target=str(params.get("target", "") or ""),
                linter=str(params.get("linter", "") or ""),
            ),
            timeout=self.timeout_seconds,
        )
        return {
            **self._status_dict(response.status),
            "passed": response.passed,
            "error_count": int(response.error_count),
            "warning_count": int(response.warning_count),
            "output": response.output,
        }

    def _create_commit(self, stub: dev_server_pb2_grpc.DevServerStub, params: dict[str, Any]) -> dict[str, Any]:
        response = stub.CreateCommit(
            dev_server_pb2.CreateCommitRequest(
                message=str(params.get("message", "") or ""),
                files=list(params.get("files", []) or []),
            ),
            timeout=self.timeout_seconds,
        )
        return {**self._status_dict(response.status), "commit_hash": response.commit_hash}

    def _create_pull_request(self, stub: dev_server_pb2_grpc.DevServerStub, params: dict[str, Any]) -> dict[str, Any]:
        response = stub.CreatePullRequest(
            dev_server_pb2.CreatePullRequestRequest(
                title=str(params.get("title", "") or ""),
                description=str(params.get("description", "") or ""),
                head_branch=str(params.get("head_branch", "") or ""),
                base_branch=str(params.get("base_branch", "") or ""),
            ),
            timeout=self.timeout_seconds,
        )
        return {**self._status_dict(response.status), "pr_url": response.pr_url, "pr_number": int(response.pr_number)}

    def _revert_changes(self, stub: dev_server_pb2_grpc.DevServerStub, params: dict[str, Any]) -> dict[str, Any]:
        response = stub.RevertChanges(
            dev_server_pb2.RevertChangesRequest(
                target=str(params.get("target", "") or ""),
                commit_hash=str(params.get("commit_hash", "") or ""),
            ),
            timeout=self.timeout_seconds,
        )
        return {**self._status_dict(response.status), "reverted_files": list(response.reverted_files)}

    @staticmethod
    def _status_dict(status: Any) -> dict[str, Any]:
        result: dict[str, Any] = {
            "success": int(status.code) == 0,
            "status_code": int(status.code),
            "message": status.message,
        }
        if status.code:
            result["error"] = status.message
        return result

    @staticmethod
    def _test_result_to_dict(item: Any) -> dict[str, Any]:
        return {
            "suite": item.suite,
            "total": int(item.total),
            "passed": int(item.passed),
            "failed": int(item.failed),
            "errors": int(item.errors),
            "duration_sec": float(item.duration_sec),
            "output": item.output,
        }

    @staticmethod
    def _file_diff_to_dict(item: Any) -> dict[str, Any]:
        return {
            "path": item.path,
            "status": item.status,
            "diff": item.diff,
            "additions": int(item.additions),
            "deletions": int(item.deletions),
        }
