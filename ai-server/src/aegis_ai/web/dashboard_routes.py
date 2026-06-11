"""Dashboard Routes — Flask routes for AEGIS operations dashboard.

Provides:
- GET /                    → Home overview
- GET /dashboard/servers   → Server health
- GET /dashboard/capabilities → Capability list with health
- GET /dashboard/events    → Recent events
- GET /dashboard/tasks     → Active/scheduled/completed tasks
- GET /dashboard/support   → Support suggestions
- GET /dashboard/memory    → Memory overview
- GET /dashboard/audit     → Audit log
- GET /dashboard/errors    → Error list

Security:
- localhost only (no external exposure)
- Sensitive payload redaction
- Dashboard cannot bypass approval
- All actions still go through PolicyEngine
"""

from __future__ import annotations

import logging
from typing import Any

from flask import Flask, jsonify, render_template

from aegis_ai.observability.audit_view import AuditView
from aegis_ai.observability.capability_health import CapabilityHealthView
from aegis_ai.observability.event_view import EventView
from aegis_ai.observability.memory_view import MemoryView
from aegis_ai.observability.server_health import ServerHealthView
from aegis_ai.settings.store import SettingsStore
from approval import ApprovalStore

logger = logging.getLogger("aegis_ai.web.dashboard")


class DashboardApp:
    """Flask-based operations dashboard for AEGIS.

    Provides read-only views of AEGIS internal state.
    All sensitive data is redacted before display.
    """

    def __init__(
        self,
        server_health: ServerHealthView | None = None,
        capability_health: CapabilityHealthView | None = None,
        event_view: EventView | None = None,
        audit_view: AuditView | None = None,
        memory_view: MemoryView | None = None,
        approval_store: ApprovalStore | None = None,
        settings_store: SettingsStore | None = None,
    ) -> None:
        self._server_health = server_health or ServerHealthView()
        self._capability_health = capability_health or CapabilityHealthView()
        self._event_view = event_view or EventView()
        self._audit_view = audit_view or AuditView()
        self._memory_view = memory_view or MemoryView()
        self._approval_store = approval_store
        self._settings_store = settings_store

        self._app = Flask(__name__, template_folder="templates")
        self._setup_routes()

    @property
    def app(self) -> Flask:
        return self._app

    def run(self, host: str = "127.0.0.1", port: int = 8090, debug: bool = False) -> None:
        """Run the dashboard server (localhost only)."""
        self._app.run(host=host, port=port, debug=debug)

    def _setup_routes(self) -> None:
        app = self._app

        # ── Home ──────────────────────────────────────────────

        @app.route("/")
        @app.route("/dashboard")
        def home():
            servers = self._server_health.get_all_servers()
            server_summary = self._server_health.get_summary()
            event_stats = self._event_view.get_stats()
            trigger_stats = self._event_view.get_trigger_stats()
            pending_approvals = self._get_pending_approvals()
            memory_summary = self._memory_view.get_summary()
            settings = self._get_settings_summary()

            return render_template("dashboard/home.html",
                servers=servers,
                server_summary=server_summary,
                event_stats=event_stats,
                trigger_stats=trigger_stats,
                pending_approvals=pending_approvals,
                memory_summary=memory_summary,
                settings=settings,
            )

        # ── Servers ───────────────────────────────────────────

        @app.route("/dashboard/servers")
        def servers():
            servers = self._server_health.get_all_servers()
            summary = self._server_health.get_summary()
            return render_template("dashboard/servers.html",
                servers=servers, summary=summary,
            )

        # ── Capabilities ──────────────────────────────────────

        @app.route("/dashboard/capabilities")
        def capabilities():
            caps = self._capability_health.get_all_capabilities()
            return render_template("dashboard/capabilities.html", capabilities=caps)

        # ── Events ────────────────────────────────────────────

        @app.route("/dashboard/events")
        def events():
            recent = self._event_view.get_recent_events(50)
            stats = self._event_view.get_stats()
            return render_template("dashboard/events.html",
                events=recent, stats=stats,
            )

        # ── Tasks ─────────────────────────────────────────────

        @app.route("/dashboard/tasks")
        def tasks():
            pending = self._event_view.get_pending_tasks()
            trigger_stats = self._event_view.get_trigger_stats()
            scheduled = self._get_scheduled_tasks()
            return render_template("dashboard/tasks.html",
                pending_tasks=pending,
                trigger_stats=trigger_stats,
                scheduled_tasks=scheduled,
            )

        # ── Support Suggestions ───────────────────────────────

        @app.route("/dashboard/support")
        def support():
            suggestions = self._get_support_suggestions()
            return render_template("dashboard/support.html", suggestions=suggestions)

        # ── Memory ────────────────────────────────────────────

        @app.route("/dashboard/memory")
        def memory():
            summary = self._memory_view.get_summary()
            episodic = self._memory_view.get_episodic_recent(20)
            semantic = self._memory_view.get_semantic_facts(20)
            procedural = self._memory_view.get_procedural_memories(20)
            reflections = self._memory_view.get_reflections(20)
            return render_template("dashboard/memory.html",
                summary=summary,
                episodic=episodic,
                semantic=semantic,
                procedural=procedural,
                reflections=reflections,
            )

        # ── Audit ─────────────────────────────────────────────

        @app.route("/dashboard/audit")
        def audit():
            entries = self._audit_view.get_recent_entries(50)
            stats = self._audit_view.get_stats()
            return render_template("dashboard/audit.html",
                entries=entries, stats=stats,
            )

        # ── Errors ────────────────────────────────────────────

        @app.route("/dashboard/errors")
        def errors():
            error_entries = self._get_recent_errors()
            return render_template("dashboard/errors.html", errors=error_entries)

        # ── API endpoints (JSON) ──────────────────────────────

        @app.route("/api/dashboard/overview")
        def api_overview():
            return jsonify({
                "servers": self._server_health.get_summary(),
                "events": self._event_view.get_stats(),
                "triggers": self._event_view.get_trigger_stats(),
                "memory": self._memory_view.get_summary(),
                "pending_approvals": len(self._get_pending_approvals()),
            })

        @app.route("/api/dashboard/events")
        def api_events():
            return jsonify(self._event_view.get_recent_events(50))

        @app.route("/api/dashboard/capabilities")
        def api_capabilities():
            return jsonify(self._capability_health.get_all_capabilities())

        # ── Health ────────────────────────────────────────────

        @app.route("/health")
        def health():
            return jsonify({"status": "ok", "component": "dashboard"})

    # ── Internal helpers ─────────────────────────────────────

    def _get_pending_approvals(self) -> list[dict[str, Any]]:
        """Get pending approvals from ApprovalStore."""
        if not self._approval_store:
            return []
        pending = self._approval_store.get_pending()
        return [
            {
                "approval_id": r.approval_id,
                "capability_id": r.capability_id,
                "tool_name": r.tool_name,
                "risk_level": r.risk_level,
                "status": r.status.name,
            }
            for r in pending
        ]

    def _get_settings_summary(self) -> dict[str, Any]:
        """Get settings summary."""
        if not self._settings_store:
            return {}
        s = self._settings_store.get()
        return {
            "autonomous_enabled": s.autonomous.autonomous_loop_enabled,
            "support_agent_enabled": s.autonomous.support_agent_enabled,
            "self_dev_enabled": s.autonomous.self_dev_proposal_enabled,
            "privacy_camera_enabled": s.privacy.camera_snapshot_enabled,
            "privacy_clipboard_enabled": s.privacy.clipboard_capture_enabled,
        }

    def _get_scheduled_tasks(self) -> list[dict[str, Any]]:
        """Get scheduled tasks from Scheduler."""
        # Placeholder — will integrate with Scheduler
        return []

    def _get_support_suggestions(self) -> list[dict[str, Any]]:
        """Get recent support suggestions."""
        # Placeholder — will integrate with SupportAgent
        return []

    def _get_recent_errors(self) -> list[dict[str, Any]]:
        """Get recent error entries from audit log."""
        entries = self._audit_view.get_recent_entries(100)
        return [e for e in entries if e.get("decision") in ("DENY", "FAILED", "ERROR")]
