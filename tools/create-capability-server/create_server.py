"""Create Capability Server — scaffold generator for new AEGIS capability servers.

Generates:
- Server implementation with capability registration
- Proto file stub
- Test skeleton
- Documentation skeleton

Usage:
    python create_server.py --name weather --type room --port 50060
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path


def create_server_scaffold(
    name: str,
    server_type: str = "dev",
    port: int = 50060,
    output_dir: str = ".",
) -> list[str]:
    """Create a capability server scaffold.

    Args:
        name: Server name (e.g. "weather", "sensor").
        server_type: Server type (dev, room, pc, android, browser).
        port: gRPC port number.
        output_dir: Output directory.

    Returns:
        List of created file paths.
    """
    prefix = name.lower().replace("-", "_").replace(" ", "_")
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

# TODO: Define your capabilities here
EXAMPLE_CAP = define_capability(
    server_prefix="{prefix}",
    action="example",
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
            server_type=ServerType.{server_type.upper()},
            port={port},
        )
        self._events = EventClient(
            server_type=ServerType.{server_type.upper()},
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
    core.broker.register_mock("{prefix}.example", lambda cap, p: {{"result": "success"}})

    result = core.invoke_capability("{prefix}.example")
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
| `{prefix}.example` | READ_ONLY | Example capability |

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
    parser.add_argument("--type", default="dev", help="Server type (dev, room, pc, android, browser)")
    parser.add_argument("--port", type=int, default=50060, help="gRPC port")
    parser.add_argument("--output", default=".", help="Output directory")
    args = parser.parse_args()

    created = create_server_scaffold(args.name, args.type, args.port, args.output)
    print(f"Created {len(created)} files:")
    for f in created:
        print(f"  {f}")


if __name__ == "__main__":
    main()
