"""Start gRPC server standalone."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from aegis_ai.config import get_config
from aegis_ai.grpc_server import serve

config = get_config()
print(f"Starting gRPC on {config.grpc_host}:{config.grpc_port}")
serve(config)
