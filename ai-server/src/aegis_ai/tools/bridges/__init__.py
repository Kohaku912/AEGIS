"""Phase 6 tool bridges — AEGIS Capability から Agent ツールへの橋渡し (instruction.md §36).

DoD 仕様 (Phase 6 / Phase 9):
- read 3 個 (repo.status / diff.get_diff / test.get_results) は
  OpenHands 標準ツール (`filesystem.read`, `terminal.execute`) で代替
- write 8 個 は Phase 9 で dev-server 削除に伴い、Agent の
  `git` / `github` 標準ツール (in-process) に統一され、bridge 経由は廃止

このパッケージは `aegis_ai/tools/bridges/` 配下に置かれ、AgentBackend
が `AgentTask.tools` として capability_id を受け取ったときに、対応する
AEGIS Capability 呼び出しへ変換する薄いラッパを提供する.
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
