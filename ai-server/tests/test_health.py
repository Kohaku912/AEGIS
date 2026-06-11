"""Test gRPC HealthCheck endpoint."""

from __future__ import annotations

import grpc

from ellie_ai.config import Config
from ellie_ai.grpc_server import EllieAIServicer

# Generated stubs
from generated.ellie.common_pb2 import HealthCheckRequest, ServerStatus


class TestHealthCheck:
    """Verify the HealthCheck gRPC endpoint works."""

    def test_health_check_returns_online(self):
        servicer = EllieAIServicer(Config())
        request = HealthCheckRequest(server_id="test-client")
        # Call directly (no gRPC server needed for unit test)
        response = servicer.HealthCheck(request, context=None)  # type: ignore[arg-type]
        assert response.status.code == 0
        assert response.status.message == "ok"
        assert response.server_status == ServerStatus.SERVER_STATUS_ONLINE
        assert response.version == "0.1.0"

    def test_servicer_instantiation(self):
        servicer = EllieAIServicer(Config())
        assert servicer is not None
        assert servicer._config.grpc_port == 50051


class TestGrpcServerStartup:
    """Integration test: start and stop a real gRPC server."""

    def test_server_starts_and_stops(self):
        """Start a gRPC server, verify HealthCheck, then stop."""

        from concurrent import futures

        config = Config()
        config.grpc_port = 50052

        server = grpc.server(futures.ThreadPoolExecutor(max_workers=2))
        from generated.ellie import ai_server_pb2_grpc
        ai_server_pb2_grpc.add_AIServerServicer_to_server(
            EllieAIServicer(config), server
        )

        port = server.add_insecure_port(f"localhost:{config.grpc_port}")
        assert port > 0

        server.start()

        try:
            channel = grpc.insecure_channel(f"localhost:{port}")
            stub = ai_server_pb2_grpc.AIServerStub(channel)
            response = stub.HealthCheck(HealthCheckRequest(server_id="test"))
            assert response.status.code == 0
            channel.close()
        finally:
            server.stop(grace=1)
