# AI Server — Python gRPC server (AEGIS Core)
# Phase 1.2: Placeholder with gRPC HealthCheck

FROM python:3.12-slim

LABEL org.aegis.service="ai-server"
LABEL org.aegis.version="0.1.0"

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy Python project files
COPY ai-server/pyproject.toml ai-server/README.md* ./
COPY ai-server/src/ ./src/

# Install Python dependencies
RUN pip install --no-cache-dir -e ".[dev]"

# Copy proto stubs (generated code)
COPY protos/ /protos/

# Expose gRPC port
EXPOSE 50051

# Health check uses gRPC
HEALTHCHECK --interval=15s --timeout=5s --retries=3 --start-period=10s \
    CMD python -c "from generated.aegis import ai_server_pb2_grpc, common_pb2; import grpc; ch=grpc.insecure_channel('localhost:50051'); stub=ai_server_pb2_grpc.AIServerStub(ch); r=stub.HealthCheck(common_pb2.HealthCheckRequest(server_id='docker-hc')); assert r.status.code==0" || exit 1

# Start the gRPC server
CMD ["python", "-m", "aegis_ai.main"]
