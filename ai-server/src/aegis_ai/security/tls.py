"""TLS — optional TLS configuration for local network security.

Provides helpers for generating self-signed certificates and
configuring TLS for gRPC and Flask servers.

Note: For MVP, TLS is optional. Local network trust is the default.
"""

from __future__ import annotations

import logging
import shutil
import subprocess
from pathlib import Path
from typing import Any

logger = logging.getLogger("aegis_ai.security.tls")


class TLSConfig:
    """TLS configuration for AEGIS servers.

    Usage:
        config = TLSConfig(
            enabled=True,
            cert_file="certs/server.crt",
            key_file="certs/server.key",
        )
    """

    def __init__(
        self,
        enabled: bool = False,
        cert_file: str = "",
        key_file: str = "",
        ca_file: str = "",
    ) -> None:
        self.enabled = enabled
        self.cert_file = cert_file
        self.key_file = key_file
        self.ca_file = ca_file

    def is_valid(self) -> bool:
        """Check if TLS configuration is valid."""
        if not self.enabled:
            return True

        if not self.cert_file or not Path(self.cert_file).exists():
            return False
        if not self.key_file or not Path(self.key_file).exists():
            return False

        return True

    def get_grpc_credentials(self) -> Any | None:
        """Get gRPC TLS credentials (if enabled)."""
        if not self.enabled or not self.is_valid():
            return None

        try:
            import grpc
            with open(self.cert_file, "rb") as f:
                cert = f.read()
            with open(self.key_file, "rb") as f:
                key = f.read()
            return grpc.ssl_server_credentials([(key, cert)])
        except Exception as e:
            logger.error("Failed to load TLS credentials: %s", e)
            return None


def generate_self_signed_cert(
    output_dir: str = "certs",
    common_name: str = "localhost",
) -> tuple[str, str]:
    """Generate a self-signed certificate for development.

    Returns (cert_path, key_path).
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    cert_path = str(output_path / "server.crt")
    key_path = str(output_path / "server.key")

    # Locate openssl in a cross-platform way. The previous implementation
    # shelled out with POSIX-only redirections (``> /dev/null``), which made
    # the check always fail on Windows even when openssl was installed.
    openssl = shutil.which("openssl")
    if openssl is None:
        logger.warning("OpenSSL not found — cannot generate self-signed cert")
        return cert_path, key_path

    try:
        # Argument-list execution (no shell) avoids command injection through
        # ``common_name`` and behaves identically on every platform.
        subprocess.run(
            [
                openssl,
                "req",
                "-x509",
                "-newkey",
                "rsa:2048",
                "-keyout",
                key_path,
                "-out",
                cert_path,
                "-days",
                "365",
                "-nodes",
                "-subj",
                f"/CN={common_name}",
            ],
            check=True,
            capture_output=True,
            timeout=60,
        )
    except (subprocess.SubprocessError, OSError) as exc:
        logger.warning("Failed to generate self-signed cert: %s", exc)

    return cert_path, key_path
