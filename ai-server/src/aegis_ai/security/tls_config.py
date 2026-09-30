"""TLS Configuration for gRPC server.

⚠️ UNWIRED (measured 2026-10-01): this module is imported by **nothing at all**, and its
``configure_server`` is the only code in the repo that calls ``add_secure_port`` — so TLS never
takes effect. It duplicates ``security/tls.py``'s ``TLSConfig`` with a different API. Do not wire
without a decision — ``DELEGATION.md`` §4; ``tests/test_security_package_stays_unwired.py``.

Provides TLS support for secure gRPC communication.
Default: disabled (plaintext). Enable via settings or environment.

Usage:
    tls = TLSConfig(enabled=True, cert_file="cert.pem", key_file="key.pem")
    server = tls.configure_server(grpc.server(...), port=50051)
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger("aegis_ai.security.tls")


@dataclass
class TLSConfig:
    """TLS configuration for gRPC."""
    enabled: bool = False
    cert_file: str = ""
    key_file: str = ""
    ca_file: str = ""
    require_client_cert: bool = False

    @classmethod
    def from_env(cls) -> TLSConfig:
        """Create TLS config from environment variables."""
        return cls(
            enabled=os.getenv("AEGIS_TLS_ENABLED", "false").lower() == "true",
            cert_file=os.getenv("AEGIS_TLS_CERT_FILE", ""),
            key_file=os.getenv("AEGIS_TLS_KEY_FILE", ""),
            ca_file=os.getenv("AEGIS_TLS_CA_FILE", ""),
            require_client_cert=os.getenv("AEGIS_TLS_REQUIRE_CLIENT_CERT", "false").lower() == "true",
        )

    def configure_server(self, server: Any, port: int | None = None) -> Any:
        """Configure a gRPC server with TLS.

        Args:
            server: A ``grpc.Server`` instance.
            port: Port to bind with TLS. Required for TLS to actually take
                effect, because gRPC only exposes ports that are added via
                ``add_secure_port``. When omitted, the credentials are built
                but no port is bound (the caller must bind them explicitly).

        Returns:
            The same ``server`` instance.
        """
        if not self.enabled:
            logger.info("TLS disabled, using plaintext")
            return server

        if not self.cert_file or not self.key_file:
            logger.warning("TLS enabled but cert/key files not specified, falling back to plaintext")
            return server

        try:
            import grpc

            # Read certificate files
            with open(self.cert_file, 'rb') as f:
                cert = f.read()
            with open(self.key_file, 'rb') as f:
                key = f.read()

            # Create server credentials
            if self.require_client_cert and self.ca_file:
                with open(self.ca_file, 'rb') as f:
                    ca = f.read()
                server_credentials = grpc.ssl_server_credentials(
                    [(key, cert)],
                    root_certificates=ca,
                    require_client_auth=True,
                )
            else:
                server_credentials = grpc.ssl_server_credentials([(key, cert)])

            if port is None:
                # Without a port we cannot call add_secure_port, so TLS would
                # silently stay off. Make that explicit instead of logging a
                # misleading "TLS enabled".
                logger.warning(
                    "TLS credentials built for cert=%s but no port was provided; "
                    "pass configure_server(server, port) to actually enable TLS.",
                    self.cert_file,
                )
                return server

            server.add_secure_port(f"[::]:{port}", server_credentials)
            logger.info("TLS enabled on port %s with cert=%s", port, self.cert_file)
            return server

        except Exception as e:
            logger.error("Failed to configure TLS: %s", e)
            return server

    def configure_channel(self, channel_kwargs: dict[str, Any]) -> dict[str, Any]:
        """Configure channel kwargs for TLS."""
        if not self.enabled:
            return channel_kwargs

        try:
            import grpc

            if self.cert_file:
                with open(self.cert_file, 'rb') as f:
                    cert = f.read()
                channel_kwargs["credentials"] = grpc.ssl_channel_credentials(
                    root_certificates=cert,
                )
            else:
                channel_kwargs["credentials"] = grpc.ssl_channel_credentials()

            return channel_kwargs

        except Exception as e:
            logger.error("Failed to configure TLS channel: %s", e)
            return channel_kwargs
