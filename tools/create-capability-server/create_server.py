"""Create Capability Server — scaffold generator for new AEGIS capability servers.

Generates:
- Server implementation with capability registration
- Proto file stub
- Test skeleton
- Documentation skeleton

Usage:
    python create_server.py --name weather --type room --port 50060

``--type`` selects which AEGIS server hosts the generated capabilities, so it also decides the
``server_prefix`` they are built with. ``--name`` only names the server and its files. Before
2026-09-29 the generator used the *name* as the capability prefix, so every scaffold it produced
raised at import unless the name happened to be a roster prefix (B-14).
"""

from __future__ import annotations

import argparse
from pathlib import Path


def _host_for_type(server_type: str) -> tuple[str, str]:
    """``(canonical id prefix, ServerType member name)`` for ``--type``, from the roster.

    Accepts any roster spelling (``room``, ``room-server``) and answers with the **canonical**
    long form, which is the first segment of the canonical id ``{server_id}.{app_id}.{action}``.
    The member name is derived rather than upper-cased, so ``--type room-server`` yields
    ``ServerType.ROOM`` and not the non-existent ``ServerType.ROOM-SERVER``.
    """
    try:
        from aegis_schema.roster import PREFIXES_BY_TYPE_WITH_RETIRED
    except ModuleNotFoundError as exc:  # pragma: no cover - environment, not logic
        raise SystemExit(
            "create_server.py needs the shared schema on its path. Run it from the repo with "
            "ai-server/src on PYTHONPATH, or `pip install -e ai-server`."
        ) from exc

    by_spelling = {
        prefix: (prefixes[1], member.name)
        for member, prefixes in PREFIXES_BY_TYPE_WITH_RETIRED.items()
        for prefix in prefixes
    }
    host = by_spelling.get(server_type)
    if host is None:
        raise SystemExit(
            f"unknown --type {server_type!r}. A capability id is namespaced by the AEGIS server "
            f"that hosts it, so --type must name one: {sorted(by_spelling)}."
        )
    return host


def create_server_scaffold(
    name: str,
    server_type: str = "room",
    port: int = 50060,
    output_dir: str = ".",
) -> list[str]:
    """Create a capability server scaffold.

    Args:
        name: Server name (e.g. "weather", "sensor"). Names the server and its files.
        server_type: Which AEGIS server hosts the generated capabilities (room, pc, android,
            browser, ai — short or long spelling).
        port: gRPC port number.
        output_dir: Output directory.

    Returns:
        List of created file paths.
    """
    prefix = name.lower().replace("-", "_").replace(" ", "_")
    cap_prefix, type_name = _host_for_type(server_type)
    class_name = "".join(w.capitalize() for w in prefix.split("_"))
    output = Path(output_dir)
    created: list[str] = []

    # Server implementation
    server_code = f'''"""AEGIS {class_name} Server — auto-generated scaffold.

Replace TODO comments with actual implementation.
"""

from __future__ import annotations

import time
from typing import Any

from aegis_sdk import (
    EventClient,
    RegistrationClient,
    define_capability,
)
from aegis_schema.models import EventPriority, RiskLevel, ServerType


# ── Capabilities ─────────────────────────────────────────────

# TODO: Define your capabilities here.
# ``server_prefix`` is the AEGIS server that hosts this one — the SDK refuses any other, and
# derives server_type from it. The app's own namespace goes in the action.
EXAMPLE_CAP = define_capability(
    server_prefix="{cap_prefix}",
    action="{prefix}.example",
    name="Example Action",
    description="An example capability. Replace with your own.",
    risk_level=RiskLevel.READ_ONLY,
    tags=["{prefix}", "observe", "read_only"],
)

ALL_CAPABILITIES = [EXAMPLE_CAP]


# ── Server Implementation ────────────────────────────────────


class {class_name}Server:
    """AEGIS {class_name} Server."""

    def __init__(self) -> None:
        self._registration = RegistrationClient(
            server_id="{prefix}-server",
            server_type=ServerType.{type_name},
            port={port},
        )
        self._events = EventClient(
            server_type=ServerType.{type_name},
            server_id="{prefix}-server",
        )

    def register(self, registry: Any) -> bool:
        """Register server and capabilities with AEGIS Core."""
        if not self._registration.register_server(registry):
            return False
        return self._registration.register_capabilities(registry, ALL_CAPABILITIES) == len(ALL_CAPABILITIES)

    def example_action(self) -> dict[str, Any]:
        """TODO: Implement your capability here."""
        return {{"result": "success", "timestamp_ms": int(time.time() * 1000)}}
'''
    server_path = output / f"{prefix}_server.py"
    server_path.write_text(server_code, encoding="utf-8")
    created.append(str(server_path))

    # Test skeleton
    test_code = f'''"""Tests for {class_name} Server."""

from __future__ import annotations

from aegis_sdk import MockAEGISCore, define_capability
from aegis_schema.models import RiskLevel, ServerType


def test_server_registration():
    """Server registers successfully."""
    from {prefix}_server import {class_name}Server, ALL_CAPABILITIES

    core = MockAEGISCore()
    server = {class_name}Server()
    assert server.register(core.registry) is True

    registered = core.registry.get_server("{prefix}-server")
    assert registered is not None


def test_capability_registration():
    """All capabilities are registered."""
    from {prefix}_server import {class_name}Server, ALL_CAPABILITIES

    core = MockAEGISCore()
    server = {class_name}Server()
    server.register(core.registry)

    for cap in ALL_CAPABILITIES:
        assert core.registry.get_capability(cap.id) is not None


def test_example_capability():
    """Example capability works."""
    from {prefix}_server import {class_name}Server

    core = MockAEGISCore()
    server = {class_name}Server()
    server.register(core.registry)

    # Register mock executor
    core.broker.register_mock("{cap_prefix}.{prefix}.example", lambda cap, p: {{"result": "success"}})

    result = core.invoke_capability("{cap_prefix}.{prefix}.example")
    assert result["success"] is True
'''
    test_path = output / "tests" / f"test_{prefix}_server.py"
    test_path.parent.mkdir(parents=True, exist_ok=True)
    test_path.write_text(test_code, encoding="utf-8")
    created.append(str(test_path))

    # README
    readme = f'''# {class_name} Server

An AEGIS capability server for {name}.

## Capabilities

| Capability | Safety Level | Description |
|-----------|-------------|-------------|
| `{cap_prefix}.{prefix}.example` | READ_ONLY | Example capability |

## Setup

```bash
pip install -e .
```

## Testing

```bash
pytest tests/ -v
```

## Registration with AEGIS Core

```python
from {prefix}_server import {class_name}Server

server = {class_name}Server()
server.register(registry)
```
'''
    readme_path = output / "README.md"
    readme_path.write_text(readme, encoding="utf-8")
    created.append(str(readme_path))

    return created


def main() -> None:
    parser = argparse.ArgumentParser(description="Create AEGIS capability server scaffold")
    parser.add_argument("--name", required=True, help="Server name (e.g. 'weather')")
    parser.add_argument(
        "--type",
        default="room",
        help="Which AEGIS server hosts the capabilities (room, pc, android, browser, ai)",
    )
    parser.add_argument("--port", type=int, default=50060, help="gRPC port")
    parser.add_argument("--output", default=".", help="Output directory")
    args = parser.parse_args()

    created = create_server_scaffold(args.name, args.type, args.port, args.output)
    print(f"Created {len(created)} files:")
    for f in created:
        print(f"  {f}")


if __name__ == "__main__":
    main()
