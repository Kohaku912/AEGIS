"""Android integration for fixed-capability gRPC devices."""

from aegis_ai.integrations.android.capability_mapper import AndroidCapabilityMapper
from aegis_ai.integrations.android.device_registry import AndroidDeviceRegistry
from aegis_ai.integrations.android.grpc_client import AndroidGrpcClient
from aegis_ai.integrations.android.manager import AndroidServerManager
from aegis_ai.integrations.android.stream_session import AndroidStreamSession

__all__ = [
    "AndroidCapabilityMapper",
    "AndroidDeviceRegistry",
    "AndroidGrpcClient",
    "AndroidServerManager",
    "AndroidStreamSession",
]
