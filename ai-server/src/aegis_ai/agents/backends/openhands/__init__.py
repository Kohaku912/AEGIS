"""OpenHands backend package — Phase 2 + Phase 8.

このパッケージは `AgentBackend` Protocol を満たす OpenHands 実装を供給する。
直接 register するには:

    from aegis_ai.agents.backends import register_backend
    from aegis_ai.agents.backends.openhands import OpenHandsBackend
    register_backend(OpenHandsBackend())

Phase 8 で `RemoteOpenHandsBackend` を追加。`AGENT_SERVER_URL` を設定するか
`AGENT_BACKEND=remote` にすると remote mode で動作し、AEGIS 本体プロセスに
`openhands-sdk` をインストールしなくてよい。

import 境界ルール (instruction.md §6 / §35.4):
- `from openhands.*` は `adapter.py` 内だけ
- `backend.py` / `config.py` / `remote_backend.py` / `workspace.py` /
  `__init__.py` には OpenHands 依存を書かない
- Phase 2 の DoD: SDK バージョンアップ時に触るのは `adapter.py` だけ
"""

from __future__ import annotations

from aegis_ai.agents.backends.openhands.backend import OpenHandsBackend
from aegis_ai.agents.backends.openhands.config import WorkspaceSpec
from aegis_ai.agents.backends.openhands.remote_backend import RemoteOpenHandsBackend
from aegis_ai.agents.backends.openhands.workspace import (
    LocalWorkspace,
    RemoteAPIError,
    RemoteAPIWorkspace,
    Workspace,
    build_workspace_from_spec,
)

__all__ = [
    "OpenHandsBackend",
    "RemoteOpenHandsBackend",
    "WorkspaceSpec",
    "Workspace",
    "LocalWorkspace",
    "RemoteAPIWorkspace",
    "RemoteAPIError",
    "build_workspace_from_spec",
]
