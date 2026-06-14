"""Search integration bridge — wires DuckDuckGo search into ToolRegistry."""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger("aegis_ai.integrations.search.bridge")


def register_search_capabilities(registry: Any) -> list[str]:
    from aegis_schema.models import Capability, RiskLevel, ServerType

    caps = [
        Capability(
            id="ai.search.web", name="Web Search",
            description="Search the web using DuckDuckGo",
            server_type=ServerType.AI, risk_level=RiskLevel.READ_ONLY,
            tags=["search", "web", "read"],
        ),
        Capability(
            id="ai.search.news", name="News Search",
            description="Search news using DuckDuckGo",
            server_type=ServerType.AI, risk_level=RiskLevel.READ_ONLY,
            tags=["search", "news", "read"],
        ),
    ]
    registered = []
    for cap in caps:
        registry.register_capability(cap)
        registered.append(cap.id)
    return registered
