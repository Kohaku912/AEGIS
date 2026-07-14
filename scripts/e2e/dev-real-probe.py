#!/usr/bin/env python3
"""Read-only gRPC probe for the real Dev Server."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import grpc

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "ai-server" / "src"))

from generated.aegis import common_pb2, dev_server_pb2, dev_server_pb2_grpc  # noqa: E402


def main() -> int:
    host = sys.argv[1] if len(sys.argv) > 1 else "127.0.0.1"
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 50056
    channel = grpc.insecure_channel(f"{host}:{port}")
    stub = dev_server_pb2_grpc.DevServerStub(channel)
    health = stub.HealthCheck(common_pb2.HealthCheckRequest(server_id="readiness-probe"), timeout=10)
    status = stub.GetRepoStatus(dev_server_pb2.GetRepoStatusRequest(), timeout=15)
    diff = stub.GetDiff(dev_server_pb2.GetDiffRequest(), timeout=15)
    payload = {
        "health_code": health.status.code,
        "server_status": health.server_status,
        "repo_status_code": status.status.code,
        "branch": status.branch,
        "commit_hash": status.commit_hash,
        "is_clean": status.is_clean,
        "modified_file_count": len(status.modified_files),
        "diff_status_code": diff.status.code,
        "diff_file_count": len(diff.files),
    }
    print(json.dumps(payload, ensure_ascii=False))
    return 0 if health.status.code == 0 and status.status.code == 0 and diff.status.code == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
