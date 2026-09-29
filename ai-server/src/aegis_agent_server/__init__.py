"""AEGIS Agent Server package — Phase 8.

systemd unit `aegis-openhands-agent.service` から
`python -m aegis_agent_server.main` で起動される。
"""

from __future__ import annotations

from aegis_agent_server.main import main, serve

__all__ = ["main", "serve"]
