"""Phase 6 tool bridges — AEGIS Capability から Agent ツールへの橋渡し (instruction.md §36).

DoD 仕様 (Phase 6 / Phase 9):
- read 3 個 (repo.status / diff.get_diff / test.get_results) は
  OpenHands 標準ツール (`filesystem.read`, `terminal.execute`) で代替
- write 8 個 は Phase 9 で dev-server 削除に伴い、Agent の
  `git` / `github` 標準ツール (in-process) に統一され、bridge 経由は廃止

このパッケージは `aegis_ai/tools/bridges/` 配下に置かれ、AgentBackend
が `AgentTask.tools` として capability_id を受け取ったときに、対応する
AEGIS Capability 呼び出しへ変換する薄いラッパを提供する.

⚠️ 実測 (2026-10-05): **このパッケージは配線されていない。** `register_default_bridges()` と
`bridge_for_capability()` の呼び出し元は `tests/agents/test_tool_bridges.py` **だけ**なので、
production では登録簿は空 (`list_bridges() == []`、素の import) で、照会する者もいない。
したがって `ai-server.workspace.{repo_status,diff,test_results}` は**どの機構でも解決しない**
(能力カタログにも無い)。それでも**意図的に残してある** — このパッケージのテストが実在の
不変条件を固定しているため: OpenHands を直接 import しない・dev-server の protobuf を参照しない・
dev-server の gRPC クライアントを参照しない・`tools/bridges/git.py` / `github.py` が削除された
ままであること。判断は `DELEGATION.md` §4 項目 53。
"""
from __future__ import annotations

from aegis_ai.tools.bridges import filesystem
from aegis_ai.tools.bridges.base import (
    BridgeResult,
    ToolBridge,
    bridge_for_capability,
    register_bridge,
)

__all__ = [
    "BridgeResult",
    "ToolBridge",
    "bridge_for_capability",
    "filesystem",
    "register_bridge",
]
