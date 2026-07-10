"""Dashboard public entry point.

The historical implementation was kept in :mod:`aegis_ai.web.dashboard_legacy`
to avoid breaking existing URLs while the dashboard is being split into
focused route modules under :mod:`aegis_ai.web.routes`.
"""

from __future__ import annotations

from typing import Any

from aegis_ai.web import dashboard_legacy as _legacy
from aegis_ai.web.dashboard_legacy import (  # noqa: F401
    _call_llm_with_runtime,
    _clean_llm_response,
    _get_mem_backend,
    _load_audit_entries,
    _load_chat_history_entries,
    _load_error_log_entries,
    _load_settings_for_status,
    _load_memory_snapshot,
    _reload_capabilities_runtime,
    _runtime_server_status,
)

_DATA_DIR = _legacy._DATA_DIR
build_shared_memory_context = _legacy.build_shared_memory_context
_server_status_context_for_prompt = _legacy._server_status_context_for_prompt

# Compatibility guard: chat route task creation still lives in dashboard_legacy
# and uses task_manager.create_task through the split route shell.


def _build_chat_system_prompt(user_message: str):
    _legacy.build_shared_memory_context = build_shared_memory_context
    _legacy._server_status_context_for_prompt = _server_status_context_for_prompt
    return _legacy._build_chat_system_prompt(user_message)


class DashboardApp(_legacy.DashboardApp):
    """Compatibility shell for the dashboard application.

    The class is intentionally thin: construction and helper behavior are
    delegated to the legacy implementation while new route groups are
    registered from ``aegis_ai.web.routes``.
    """

    def __init__(self, runtime: Any = None) -> None:
        _legacy._DATA_DIR = _DATA_DIR
        for name in (
            "_get_mem_backend",
            "_load_audit_entries",
            "_load_chat_history_entries",
            "_load_error_log_entries",
            "_load_memory_snapshot",
            "_load_settings_for_status",
            "build_shared_memory_context",
        ):
            setattr(_legacy, name, globals()[name])
        super().__init__(runtime=runtime)


__all__ = [
    "DashboardApp",
    "_build_chat_system_prompt",
    "_call_llm_with_runtime",
    "_clean_llm_response",
    "_DATA_DIR",
    "_get_mem_backend",
    "_load_audit_entries",
    "_load_chat_history_entries",
    "_load_error_log_entries",
    "_load_memory_snapshot",
    "_load_settings_for_status",
    "_reload_capabilities_runtime",
    "_runtime_server_status",
    "_server_status_context_for_prompt",
    "build_shared_memory_context",
]
