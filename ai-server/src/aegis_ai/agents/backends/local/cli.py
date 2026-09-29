"""Local CLI entrypoint — Phase 1 dummy agent.

`python -m aegis_ai.agents.backends.local.cli` で起動.
stdin から JSON 1 行の `AgentTask` 風 dict を受け取り、stdout に
`AgentResult` 風 dict を 1 行で書き出す.

Phase 1 の振る舞い: `goal` を echo するだけの 1 action を返す.
外部依存ゼロ. 既存 Capability / ネットワークを一切経由しない (read-only DoD).
"""
from __future__ import annotations

import hashlib
import json
import sys
import time


def _hash_args(args: dict) -> str:
    """ApprovalManager.compute_args_hash() と同じ SHA-256 実装 (instruction.md §5)."""
    serialized = json.dumps(args, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def run(request: dict) -> dict:
    """Build the dummy AgentResult payload."""
    task_id = str(request.get("task_id", ""))
    goal = str(request.get("goal", ""))
    started_ms = int(time.time() * 1000)

    arguments = {"echo": goal}
    arguments_hash = _hash_args(arguments)
    action = {
        "step_id": f"{task_id}-step-1",
        "capability_id": "ai-server.agent.task.echo",
        "arguments": arguments,
        "arguments_hash": arguments_hash,
        "result": {"echoed": goal},
        "error": "",
        "duration_ms": 0,
    }
    return {
        "task_id": task_id,
        "status": "completed",
        "summary": f"local echo: {goal[:80]}",
        "actions": [action],
        "artifacts": [],
        "tool_calls": [action],
        "errors": [],
        "approvals_requested": [],
        "suggested_memory": [],
        "suggested_follow_ups": [],
        "usage": {
            "input_tokens": 0,
            "output_tokens": 0,
            "cache_hit_tokens": 0,
            "cost_usd": 0.0,
            "model": "local-dummy",
            "provider": "local",
            "tool_call_count": 1,
            "duration_ms": int(time.time() * 1000) - started_ms,
        },
    }


def main() -> int:
    raw = sys.stdin.read()
    if not raw.strip():
        sys.stderr.write("local cli: empty stdin\n")
        return 2
    try:
        request = json.loads(raw)
    except json.JSONDecodeError as e:
        sys.stderr.write(f"local cli: invalid json: {e}\n")
        return 2
    if not isinstance(request, dict):
        sys.stderr.write("local cli: request must be a JSON object\n")
        return 2
    payload = run(request)
    sys.stdout.write(json.dumps(payload, ensure_ascii=False))
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
