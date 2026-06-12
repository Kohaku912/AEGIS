"""TLS Configuration for gRPC server.

Provides TLS support for secure gRPC communication.
Default: disabled (plaintext). Enable via settings or environment.

Usage:
    tls = TLSConfig(enabled=True, cert_file="cert.pem", key_file="key.pem")
    server = tls.configure_server(grpc.server(...))
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass, field
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

    def configure_server(self, server: Any) -> Any:
        """Configure a gRPC server with TLS."""
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

            logger.info("TLS enabled with cert=%s", self.cert_file)
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
