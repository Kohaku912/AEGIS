"""Agent backends — pluggable Agent execution backends.

`registry.py` で backend を name ベースで登録・解決する.
AEGIS 本体は `runtime.agent_backend` に登録された 1 個だけを持つ.
Phase 1 では LocalBackend のみ, Phase 2 で OpenHandsBackend を追加する.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from aegis_ai.agents.runtime.interface import AgentBackend

_backends: dict[str, AgentBackend] = {}


def register_backend(backend: AgentBackend) -> None:
    """Register a backend by its `name` attribute. Overwrites existing."""
    _backends[backend.name] = backend


def get_backend(name: str) -> AgentBackend | None:
    return _backends.get(name)


def list_backends() -> list[str]:
    return list(_backends.keys())


def clear_backends() -> None:
    """Clear registry. For tests only."""
    _backends.clear()
