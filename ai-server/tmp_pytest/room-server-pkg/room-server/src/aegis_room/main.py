"""Room Server entry point."""

from __future__ import annotations

import os

from aegis_room.server import serve


def main() -> None:
    host = os.environ.get("AEGIS_ROOM_HOST", "0.0.0.0")
    port = int(os.environ.get("AEGIS_ROOM_PORT", "50055"))
    serve(host=host, port=port)


if __name__ == "__main__":
    main()

