"""Health Alert Manager — system health monitoring separate from desires.

Monitors disk usage, server reachability, executor availability, LLM provider,
and data directory size. Alerts are persisted to JSONL and displayed on Dashboard.

Health alerts do NOT affect desire pressure. They are a separate concern.

Usage:
    manager = HealthAlertManager(data_dir="data/health", tool_broker=broker, llm_provider=llm)
    new_alerts = manager.check_system_health()
    active = manager.get_active_alerts()
"""

from __future__ import annotations

import json
import logging
import os
import shutil
import socket
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

logger = logging.getLogger("aegis_ai.health.alert_manager")

# Servers to check for reachability
_SERVER_DEFAULTS: list[tuple[str, str, str, int]] = [
    ("pc-server", "PC_SERVER_HOST", "PC_SERVER_PORT", 50052),
    ("browser-server", "BROWSER_SERVER_HOST", "BROWSER_SERVER_PORT", 50053),
    ("android-server", "ANDROID_SERVER_HOST", "ANDROID_SERVER_PORT", 50054),
    ("room-server", "ROOM_SERVER_HOST", "ROOM_SERVER_PORT", 50055),
    ("dev-server", "DEV_SERVER_HOST", "DEV_SERVER_PORT", 50056),
]

# Deduplication window: same type+source within this window is suppressed
_DEDUP_WINDOW_MS: int = 3_600_000  # 1 hour

# Max alerts to keep in memory
_MAX_ALERTS: int = 200


@dataclass
class HealthAlert:
    """A single health alert."""

    alert_id: str = ""
    alert_type: str = ""  # disk_low, server_unreachable, no_executor, llm_unavailable, high_error_rate, data_dir_large
    severity: str = "info"  # info, warning, critical
    message: str = ""
    source: str = ""  # system, capability, llm, executor
    created_at: int = 0  # epoch-ms
    acknowledged: bool = False
    details: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "alert_id": self.alert_id,
            "alert_type": self.alert_type,
            "severity": self.severity,
            "message": self.message,
            "source": self.source,
            "created_at": self.created_at,
            "acknowledged": self.acknowledged,
            "details": self.details,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> HealthAlert:
        return cls(
            alert_id=data.get("alert_id", ""),
            alert_type=data.get("alert_type", ""),
            severity=data.get("severity", "info"),
            message=data.get("message", ""),
            source=data.get("source", ""),
            created_at=int(data.get("created_at", 0)),
            acknowledged=bool(data.get("acknowledged", False)),
            details=data.get("details", {}),
        )


class HealthAlertManager:
    """System health monitoring — separate from desire system.

    Parameters
    ----------
    data_dir:
        Directory for ``alerts.jsonl``.
    tool_broker:
        Optional ToolBroker for executor availability check.
    llm_provider:
        Optional LLM provider for availability check.
    data_path:
        Path to main data directory for size check. Defaults to ``data``.
    """

    def __init__(
        self,
        data_dir: str = "data/health",
        tool_broker: Any = None,
        llm_provider: Any = None,
        status_manager: Any = None,
        data_path: str = "data",
    ) -> None:
        self._data_dir = Path(data_dir)
        self._data_dir.mkdir(parents=True, exist_ok=True)
        self._broker = tool_broker
        self._llm = llm_provider
        self._status_manager = status_manager
        self._data_path = Path(data_path)
        self._active_alerts: list[HealthAlert] = []
        self._all_alerts: list[HealthAlert] = []
        self._load()

    # ── Public API ───────────────────────────────────────────────────────

    def check_system_health(self) -> list[HealthAlert]:
        """Run ALL health checks, return newly created alerts."""
        new_alerts: list[HealthAlert] = []

        disk = self.check_disk_usage()
        if disk:
            new_alerts.append(disk)

        passed_keys: set[tuple[str, str, str]] = set()
        for server_id, host, port in self._configured_servers():
            srv = self.check_server_reachable(server_id, host, port)
            if srv:
                new_alerts.append(srv)
            else:
                passed_keys.add(("server_unreachable", "capability", server_id))

        executor = self.check_executor_available()
        if executor:
            new_alerts.append(executor)
        else:
            passed_keys.add(("no_executor", "executor", ""))

        llm = self.check_llm_provider()
        if llm:
            new_alerts.append(llm)
        else:
            passed_keys.add(("llm_unavailable", "llm", ""))

        data_size = self.check_data_dir_size()
        if data_size:
            new_alerts.append(data_size)
        else:
            passed_keys.add(("data_dir_large", "system", ""))

        resolved = self._acknowledge_resolved(passed_keys)

        # Deduplicate and persist
        unique: list[HealthAlert] = []
        updated = 0
        for alert in new_alerts:
            if self._deduplicate(alert):
                continue
            if self._update_existing_active(alert):
                updated += 1
                continue
            else:
                self._active_alerts.append(alert)
                self._all_alerts.append(alert)
                unique.append(alert)

        if unique or resolved or updated:
            self._save()
            logger.info(
                "Health check: %d new alerts, %d updated, %d resolved",
                len(unique),
                updated,
                resolved,
            )

        return unique

    def check_disk_usage(self) -> HealthAlert | None:
        """Check disk space. < 10% free = critical, < 20% = warning."""
        try:
            total, used, free = shutil.disk_usage("/")
            free_pct = free / total
            if free_pct < 0.1:
                return self._create_alert(
                    alert_type="disk_low",
                    severity="critical",
                    message=f"Disk space critically low: {free_pct:.0%} free ({free // (1024**3)}GB)",
                    source="system",
                    details={"free_pct": free_pct, "free_gb": free // (1024**3)},
                )
            elif free_pct < 0.2:
                return self._create_alert(
                    alert_type="disk_low",
                    severity="warning",
                    message=f"Disk space low: {free_pct:.0%} free ({free // (1024**3)}GB)",
                    source="system",
                    details={"free_pct": free_pct, "free_gb": free // (1024**3)},
                )
        except Exception:
            pass
        return None

    def check_server_reachable(
        self, server_id: str, host: str, port: int
    ) -> HealthAlert | None:
        """Check if a server is reachable via TCP."""
        if self._status_manager is not None:
            try:
                snapshot = self._status_manager.get_snapshot()
                item = snapshot.get(server_id, {}) if isinstance(snapshot, dict) else {}
                status = str(item.get("status") or "").lower()
                if status in {"online", "degraded"}:
                    return None
                if status in {"offline", "disabled", "unconfigured"}:
                    return self._create_alert(
                        alert_type="server_unreachable",
                        severity="warning",
                        message=f"{server_id} status is {status}",
                        source="capability",
                        details={"server_id": server_id, "host": host, "port": port, "status": status},
                    )
            except Exception:
                logger.debug("StatusManager health lookup failed", exc_info=True)
        if not self._check_port(host, port):
            return self._create_alert(
                alert_type="server_unreachable",
                severity="warning",
                message=f"{server_id} unreachable ({host}:{port})",
                source="capability",
                details={"server_id": server_id, "host": host, "port": port},
            )
        return None

    def _configured_servers(self) -> list[tuple[str, str, int]]:
        servers: list[tuple[str, str, int]] = []
        for server_id, host_env, port_env, default_port in _SERVER_DEFAULTS:
            default_host = "localhost"
            if server_id == "pc-server":
                default_host = "localhost"
            host = os.environ.get(host_env, default_host)
            port = int(os.environ.get(port_env, str(default_port)))
            servers.append((server_id, host, port))
        return servers

    def _acknowledge_resolved(self, passed_keys: set[tuple[str, str, str]]) -> int:
        count = 0
        for alert in self._all_alerts:
            if alert.acknowledged:
                continue
            server_id = str(alert.details.get("server_id") or "")
            key = (alert.alert_type, alert.source, server_id)
            generic_key = (alert.alert_type, alert.source, "")
            if key in passed_keys or generic_key in passed_keys:
                alert.acknowledged = True
                count += 1
        if count:
            self._active_alerts = [a for a in self._all_alerts if not a.acknowledged]
        return count

    def check_executor_available(self) -> HealthAlert | None:
        """Check if tool broker has any valid capabilities."""
        if self._broker is None:
            return self._create_alert(
                alert_type="no_executor",
                severity="warning",
                message="No tool broker configured — cannot execute capabilities",
                source="executor",
            )
        try:
            caps = self._broker.list_safe_capabilities()
            if not caps:
                return self._create_alert(
                    alert_type="no_executor",
                    severity="warning",
                    message="No safe capabilities available in tool broker",
                    source="executor",
                )
        except Exception:
            return self._create_alert(
                alert_type="no_executor",
                severity="warning",
                message="Tool broker check failed — cannot list capabilities",
                source="executor",
            )
        return None

    def check_llm_provider(self) -> HealthAlert | None:
        """Check if LLM provider is available."""
        if self._llm is None:
            return self._create_alert(
                alert_type="llm_unavailable",
                severity="warning",
                message="No LLM provider configured",
                source="llm",
            )
        # Check if provider has a generate method
        if not hasattr(self._llm, "generate"):
            return self._create_alert(
                alert_type="llm_unavailable",
                severity="warning",
                message="LLM provider missing generate() method",
                source="llm",
            )
        return None

    def check_data_dir_size(self) -> HealthAlert | None:
        """Check if data directory is excessively large (> 100MB)."""
        try:
            if not self._data_path.exists():
                return None
            total_size = sum(
                f.stat().st_size for f in self._data_path.rglob("*") if f.is_file()
            )
            if total_size > 100 * 1024 * 1024:
                return self._create_alert(
                    alert_type="data_dir_large",
                    severity="info",
                    message=f"Data directory large: {total_size // (1024*1024)}MB",
                    source="system",
                    details={"size_mb": total_size // (1024 * 1024)},
                )
        except Exception:
            pass
        return None

    def get_active_alerts(self) -> list[HealthAlert]:
        """Return unacknowledged alerts."""
        return [a for a in self._all_alerts if not a.acknowledged]

    def get_all_alerts(self, limit: int = 50) -> list[HealthAlert]:
        """Return all alerts (most recent first)."""
        return list(reversed(self._all_alerts[-limit:]))

    def acknowledge(self, alert_id: str) -> bool:
        """Mark an alert as acknowledged."""
        for alert in self._all_alerts:
            if alert.alert_id == alert_id:
                alert.acknowledged = True
                self._save()
                return True
        return False

    def acknowledge_all(self) -> int:
        """Acknowledge all active alerts. Returns count."""
        count = 0
        for alert in self._all_alerts:
            if not alert.acknowledged:
                alert.acknowledged = True
                count += 1
        if count:
            self._save()
        return count

    def get_alert_stats(self) -> dict[str, Any]:
        """Summary: count by type, severity, total active."""
        by_type: dict[str, int] = {}
        by_severity: dict[str, int] = {}
        active = 0
        for alert in self._all_alerts:
            if not alert.acknowledged:
                active += 1
                by_type[alert.alert_type] = by_type.get(alert.alert_type, 0) + 1
                by_severity[alert.severity] = by_severity.get(alert.severity, 0) + 1
        return {
            "total": len(self._all_alerts),
            "active": active,
            "by_type": by_type,
            "by_severity": by_severity,
        }

    def to_dict(self) -> dict[str, Any]:
        """Serializable state for API."""
        return {
            "active_alerts": [a.to_dict() for a in self.get_active_alerts()],
            "stats": self.get_alert_stats(),
            "recent_alerts": [a.to_dict() for a in self.get_all_alerts(limit=20)],
        }

    # ── Internal ─────────────────────────────────────────────────────────

    def _create_alert(
        self,
        alert_type: str,
        severity: str,
        message: str,
        source: str,
        details: dict[str, Any] | None = None,
    ) -> HealthAlert:
        """Create a new HealthAlert with unique ID."""
        return HealthAlert(
            alert_id=f"ha_{int(time.time() * 1000)}_{os.urandom(2).hex()}",
            alert_type=alert_type,
            severity=severity,
            message=message,
            source=source,
            created_at=int(time.time() * 1000),
            acknowledged=False,
            details=details or {},
        )

    def _deduplicate(self, alert: HealthAlert) -> bool:
        """Check if a similar alert already exists (same type+source in dedup window)."""
        now = int(time.time() * 1000)
        for existing in self._active_alerts:
            if (
                existing.alert_type == alert.alert_type
                and existing.source == alert.source
                and not existing.acknowledged
                and now - existing.created_at < _DEDUP_WINDOW_MS
            ):
                return True
        return False

    def _update_existing_active(self, alert: HealthAlert) -> bool:
        """Refresh an unresolved alert for the same target instead of adding noise."""
        alert_target = str(alert.details.get("server_id") or "")
        for existing in self._active_alerts:
            if existing.acknowledged:
                continue
            existing_target = str(existing.details.get("server_id") or "")
            if (
                existing.alert_type == alert.alert_type
                and existing.source == alert.source
                and existing_target == alert_target
            ):
                existing.message = alert.message
                existing.severity = alert.severity
                existing.details = alert.details
                return True
        return False

    def _check_port(self, host: str, port: int, timeout: float = 1.0) -> bool:
        """TCP port connectivity check."""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(timeout)
            s.connect((host, port))
            s.close()
            return True
        except Exception:
            return False

    # ── Persistence ──────────────────────────────────────────────────────

    def _alert_path(self) -> Path:
        return self._data_dir / "alerts.jsonl"

    def _save(self) -> None:
        """Persist all alerts to JSONL."""
        try:
            with open(self._alert_path(), "w", encoding="utf-8") as f:
                for alert in self._all_alerts[-_MAX_ALERTS:]:
                    f.write(json.dumps(alert.to_dict(), ensure_ascii=False) + "\n")
        except Exception as exc:
            logger.warning("Failed to save health alerts: %s", exc)

    def _load(self) -> None:
        """Load alerts from JSONL."""
        path = self._alert_path()
        if not path.exists():
            return
        try:
            alerts: list[HealthAlert] = []
            with open(path, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        data = json.loads(line)
                        alerts.append(HealthAlert.from_dict(data))
            self._all_alerts = alerts[-_MAX_ALERTS:]
            collapsed = self._collapse_duplicate_active_alerts()
            self._active_alerts = [a for a in self._all_alerts if not a.acknowledged]
            if collapsed:
                self._save()
            logger.info("Loaded %d health alerts from %s", len(alerts), path)
        except Exception as exc:
            logger.warning("Failed to load health alerts: %s", exc)

    def _collapse_duplicate_active_alerts(self) -> int:
        """Keep only the newest unresolved alert for the same type/source/target."""
        seen: set[tuple[str, str, str]] = set()
        collapsed = 0
        for alert in reversed(self._all_alerts):
            if alert.acknowledged:
                continue
            target = str(alert.details.get("server_id") or "")
            key = (alert.alert_type, alert.source, target)
            if key in seen:
                alert.acknowledged = True
                collapsed += 1
            else:
                seen.add(key)
        return collapsed
