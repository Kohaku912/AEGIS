"""Resolve TCP endpoints for LAN servers whose DHCP IPs may change.

Candidate order:
1. In-memory last-known-good host for the server
2. Persisted cache (`data/endpoint_cache.json` by default)
3. `*_SERVER_HOST` primary env value
4. `*_SERVER_HOSTS` comma-separated candidates
5. IPs resolved from configured MAC addresses (`*_SERVER_MAC` / `*_SERVER_MACS`)
6. Optional LAN /24 scan for the target port (pc-server / room-server only)

Successful probes update memory + disk cache so subsequent calls stay fast.
"""

from __future__ import annotations

import json
import logging
import os
import re
import socket
import subprocess
import threading
import time
from pathlib import Path
from typing import Any

logger = logging.getLogger("aegis_ai.net.endpoint_resolver")

_LOCK = threading.RLock()
_MEMORY: dict[str, dict[str, Any]] = {}
_DEFAULT_CACHE = Path("data/endpoint_cache.json")
_DEFAULT_NEIGHBORS = Path("data/neighbors.json")
_SCAN_SERVERS = frozenset({"pc-server", "room-server"})
_LAST_SCAN_MS: dict[str, int] = {}
_SCAN_COOLDOWN_MS = int(os.getenv("AEGIS_LAN_SCAN_COOLDOWN_MS", "300000"))  # 5 minutes
_MAC_RE = re.compile(r"[^0-9a-fA-F]")


def _cache_path() -> Path:
    raw = os.getenv("AEGIS_ENDPOINT_CACHE_PATH", "").strip()
    return Path(raw) if raw else _DEFAULT_CACHE


def _neighbors_path() -> Path:
    raw = os.getenv("AEGIS_NEIGHBOR_TABLE_PATH", "").strip()
    return Path(raw) if raw else _DEFAULT_NEIGHBORS


def _env_csv(name: str) -> list[str]:
    raw = os.getenv(name, "")
    return [part.strip() for part in raw.split(",") if part.strip()]


def _env_bool(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def normalize_mac(mac: str) -> str:
    """Normalize MAC to lowercase colon-separated form, or '' if invalid."""
    hex_only = _MAC_RE.sub("", (mac or "").strip()).lower()
    if len(hex_only) != 12:
        return ""
    return ":".join(hex_only[i : i + 2] for i in range(0, 12, 2))


def _probe(host: str, port: int, timeout: float) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def _resolve_hostnames(candidates: list[str]) -> list[str]:
    """Expand hostnames to IPs while keeping original names first."""
    expanded: list[str] = []
    seen: set[str] = set()
    for candidate in candidates:
        if candidate not in seen:
            expanded.append(candidate)
            seen.add(candidate)
        try:
            infos = socket.getaddrinfo(candidate, None, family=socket.AF_INET, type=socket.SOCK_STREAM)
        except OSError:
            continue
        for info in infos:
            ip = info[4][0]
            if ip not in seen:
                expanded.append(ip)
                seen.add(ip)
    return expanded


def _guess_lan_prefix() -> str | None:
    explicit = os.getenv("AEGIS_LAN_SCAN_PREFIX", "").strip()
    if explicit:
        return explicit.rstrip(".")
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.connect(("8.8.8.8", 80))
            local_ip = sock.getsockname()[0]
        parts = local_ip.split(".")
        if len(parts) == 4 and not local_ip.startswith("127."):
            return ".".join(parts[:3])
    except OSError:
        return None
    return None


def _parse_proc_arp(path: Path) -> dict[str, str]:
    """Return mac -> ip mapping from a /proc/net/arp style table."""
    mapping: dict[str, str] = {}
    try:
        lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
    except OSError:
        return mapping
    for line in lines[1:]:
        parts = line.split()
        if len(parts) < 4:
            continue
        ip, _hw_type, flags, mac = parts[0], parts[1], parts[2], parts[3]
        if flags in {"0x0", "0"}:
            continue
        norm = normalize_mac(mac)
        if norm and not ip.startswith("127."):
            mapping[norm] = ip
    return mapping


def _parse_ip_neigh(text: str) -> dict[str, str]:
    mapping: dict[str, str] = {}
    for line in text.splitlines():
        # 192.168.50.120 dev wlp2s0 lladdr 20:86:a0:62:98:e0 REACHABLE
        parts = line.split()
        if len(parts) < 5 or "lladdr" not in parts:
            continue
        ip = parts[0]
        try:
            mac = parts[parts.index("lladdr") + 1]
        except (ValueError, IndexError):
            continue
        state = parts[-1].upper() if parts else ""
        if state in {"FAILED", "INCOMPLETE", "NONE"}:
            continue
        norm = normalize_mac(mac)
        if norm and re.match(r"^\d+\.\d+\.\d+\.\d+$", ip):
            mapping[norm] = ip
    return mapping


def _parse_neighbors_json(path: Path) -> dict[str, str]:
    mapping: dict[str, str] = {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return mapping
    items = data.get("neighbors") if isinstance(data, dict) else data
    if not isinstance(items, list):
        return mapping
    for item in items:
        if not isinstance(item, dict):
            continue
        norm = normalize_mac(str(item.get("mac") or ""))
        ip = str(item.get("ip") or "").strip()
        state = str(item.get("state") or "").upper()
        if state in {"FAILED", "INCOMPLETE", "NONE"}:
            continue
        if norm and re.match(r"^\d+\.\d+\.\d+\.\d+$", ip):
            mapping[norm] = ip
    return mapping


def read_neighbor_table() -> dict[str, str]:
    """Collect mac->ip from host ARP mounts, local ARP, ip neigh, and JSON cache."""
    mapping: dict[str, str] = {}
    for path in (
        Path("/host/proc/net/arp"),
        Path("/proc/net/arp"),
    ):
        mapping.update(_parse_proc_arp(path))
    mapping.update(_parse_neighbors_json(_neighbors_path()))
    try:
        completed = subprocess.run(
            ["ip", "-4", "neigh", "show"],
            check=False,
            capture_output=True,
            text=True,
            timeout=2,
        )
        if completed.returncode == 0 and completed.stdout:
            mapping.update(_parse_ip_neigh(completed.stdout))
    except Exception:
        logger.debug("ip neigh unavailable", exc_info=True)
    return mapping


def _configured_macs(server_id: str) -> list[str]:
    prefix = server_id.upper().replace("-", "_")
    values = _env_csv(f"{prefix}_MACS")
    single = os.getenv(f"{prefix}_MAC", "").strip()
    if single:
        values = [single, *values]
    # Stable built-in fallbacks for known AEGIS devices (overridable via env).
    if server_id == "room-server" and not values:
        values = ["02:00:50:a7:b0:58", "20:86:a0:62:98:e0"]
    if server_id == "pc-server" and not values:
        values = ["44:af:28:14:f2:f8", "d8:5e:d3:5b:d7:fa"]
    unique: list[str] = []
    seen: set[str] = set()
    for raw in values:
        norm = normalize_mac(raw)
        if norm and norm not in seen:
            unique.append(norm)
            seen.add(norm)
    return unique


def _ips_for_macs(macs: list[str], table: dict[str, str] | None = None) -> list[str]:
    table = table if table is not None else read_neighbor_table()
    ips: list[str] = []
    seen: set[str] = set()
    for mac in macs:
        ip = table.get(mac)
        if ip and ip not in seen:
            ips.append(ip)
            seen.add(ip)
    return ips


def _ping_lan_prefix(prefix: str) -> None:
    """Best-effort ARP refresh by probing the /24 (ICMP if available, else UDP)."""
    for last in range(1, 255):
        ip = f"{prefix}.{last}"
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(0.01)
            sock.sendto(b"", (ip, 9))
            sock.close()
        except OSError:
            pass


def _scan_lan(port: int, timeout: float) -> list[str]:
    prefix = _guess_lan_prefix()
    if not prefix:
        return []
    found: list[str] = []
    for last in range(1, 255):
        ip = f"{prefix}.{last}"
        if _probe(ip, port, timeout=min(timeout, 0.08)):
            found.append(ip)
    return found


def _load_disk_cache() -> dict[str, Any]:
    path = _cache_path()
    try:
        if path.is_file():
            return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        logger.debug("Failed reading endpoint cache %s", path, exc_info=True)
    return {}


def _save_disk_cache(server_id: str, host: str, port: int, *, mac: str | None = None) -> None:
    path = _cache_path()
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        data = _load_disk_cache()
        entry: dict[str, Any] = {
            "host": host,
            "port": port,
            "updated_at_ms": int(time.time() * 1000),
        }
        if mac:
            entry["mac"] = normalize_mac(mac)
        data[server_id] = entry
        path.write_text(json.dumps(data, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
    except Exception:
        logger.debug("Failed writing endpoint cache %s", path, exc_info=True)


def _mac_for_ip(ip: str, table: dict[str, str] | None = None) -> str | None:
    table = table if table is not None else read_neighbor_table()
    for mac, mapped_ip in table.items():
        if mapped_ip == ip:
            return mac
    return None


def _candidate_hosts(server_id: str, host_env: str, hosts_env: str | None) -> list[str]:
    prefix = server_id.upper().replace("-", "_")
    hosts_key = hosts_env or f"{prefix}_HOSTS"
    primary_key = host_env or f"{prefix}_HOST"

    ordered: list[str] = []
    with _LOCK:
        mem = _MEMORY.get(server_id)
        if mem and mem.get("host"):
            ordered.append(str(mem["host"]))

    disk = _load_disk_cache().get(server_id) or {}
    if disk.get("host"):
        ordered.append(str(disk["host"]))

    primary = os.getenv(primary_key, "").strip()
    if primary:
        ordered.append(primary)
    ordered.extend(_env_csv(hosts_key))

    # MAC-derived IPs from current neighbor/ARP tables.
    ordered.extend(_ips_for_macs(_configured_macs(server_id)))

    if server_id == "room-server":
        ordered.extend(["orangepi-room", "orangepi-room.local"])

    unique: list[str] = []
    seen: set[str] = set()
    for item in ordered:
        if item and item not in seen:
            unique.append(item)
            seen.add(item)
    return _resolve_hostnames(unique)


def _remember(server_id: str, host: str, port: int) -> tuple[str, int]:
    table = read_neighbor_table()
    mac = _mac_for_ip(host, table)
    with _LOCK:
        _MEMORY[server_id] = {"host": host, "port": port, "mac": mac}
    _save_disk_cache(server_id, host, port, mac=mac)
    return host, port


def resolve_by_mac(
    server_id: str,
    *,
    port: int,
    timeout: float = 0.4,
    refresh_arp: bool = True,
) -> tuple[str, int] | None:
    """Resolve a server by configured MAC address via ARP/neighbor tables."""
    macs = _configured_macs(server_id)
    if not macs:
        return None

    table = read_neighbor_table()
    for ip in _ips_for_macs(macs, table):
        if _probe(ip, port, timeout=timeout):
            logger.info("Resolved %s by MAC to %s:%s", server_id, ip, port)
            return _remember(server_id, ip, port)

    if not refresh_arp:
        return None

    prefix = _guess_lan_prefix()
    if prefix:
        _ping_lan_prefix(prefix)
        # Brief settle for host ARP updates when /host/proc/net/arp is mounted.
        time.sleep(0.2)
        table = read_neighbor_table()
        for ip in _ips_for_macs(macs, table):
            if _probe(ip, port, timeout=timeout):
                logger.info("Resolved %s by MAC (after ARP refresh) to %s:%s", server_id, ip, port)
                return _remember(server_id, ip, port)

    # Last resort: port-scan and accept only IPs whose MAC matches.
    for ip in _scan_lan(port, timeout=timeout):
        table = read_neighbor_table()
        mac = _mac_for_ip(ip, table)
        if mac and mac in macs and _probe(ip, port, timeout=timeout):
            logger.info("Resolved %s by MAC+port-scan to %s:%s (%s)", server_id, ip, port, mac)
            return _remember(server_id, ip, port)
    return None


def resolve_tcp_endpoint(
    server_id: str,
    *,
    port: int,
    host_env: str | None = None,
    hosts_env: str | None = None,
    timeout: float = 0.4,
    allow_lan_scan: bool | None = None,
) -> tuple[str, int] | None:
    """Return a reachable (host, port) or None if all candidates fail."""
    prefix = server_id.upper().replace("-", "_")
    host_env = host_env or f"{prefix}_HOST"
    hosts_env = hosts_env or f"{prefix}_HOSTS"

    candidates = _candidate_hosts(server_id, host_env, hosts_env)
    for host in candidates:
        if _probe(host, port, timeout=timeout):
            if host != os.getenv(host_env, ""):
                logger.info("Resolved %s endpoint to %s:%s", server_id, host, port)
            return _remember(server_id, host, port)

    # Explicit MAC discovery (refresh ARP, then match).
    by_mac = resolve_by_mac(server_id, port=port, timeout=timeout, refresh_arp=True)
    if by_mac:
        return by_mac

    scan_enabled = (
        allow_lan_scan
        if allow_lan_scan is not None
        else _env_bool("AEGIS_LAN_SCAN_ENABLED", server_id in _SCAN_SERVERS)
    )
    now_ms = int(time.time() * 1000)
    last_scan = _LAST_SCAN_MS.get(server_id, 0)
    scan_due = (now_ms - last_scan) >= _SCAN_COOLDOWN_MS
    if scan_enabled and server_id in _SCAN_SERVERS and scan_due:
        _LAST_SCAN_MS[server_id] = now_ms
        logger.warning("Primary %s candidates unreachable; scanning LAN for :%s", server_id, port)
        macs = set(_configured_macs(server_id))
        for host in _scan_lan(port, timeout=timeout):
            if macs:
                mac = _mac_for_ip(host)
                if mac and mac not in macs:
                    continue
            logger.info("LAN scan found %s at %s:%s", server_id, host, port)
            return _remember(server_id, host, port)

    return None


def cached_endpoint(server_id: str) -> tuple[str, int] | None:
    with _LOCK:
        item = _MEMORY.get(server_id)
        if not item:
            return None
        return str(item["host"]), int(item["port"])


def clear_endpoint_cache(server_id: str | None = None) -> None:
    with _LOCK:
        if server_id is None:
            _MEMORY.clear()
        else:
            _MEMORY.pop(server_id, None)
