FROM python:3.12-slim

LABEL org.aegis.service="dev-server"
LABEL org.aegis.version="0.1.0"

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src \
    DEV_SERVER_PORT=50056 \
    AEGIS_REPO_PATH=/workspace

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

COPY dev-server/pyproject.toml ./pyproject.toml
COPY dev-server/src ./src

RUN pip install --no-cache-dir -e .
RUN mkdir -p /workspace

EXPOSE 50056

HEALTHCHECK --interval=20s --timeout=5s --retries=5 --start-period=10s \
    CMD python -c "import grpc; from generated.aegis import common_pb2, dev_server_pb2_grpc; ch=grpc.insecure_channel('localhost:50056'); r=dev_server_pb2_grpc.DevServerStub(ch).HealthCheck(common_pb2.HealthCheckRequest(server_id='docker-health'), timeout=3); raise SystemExit(0 if r.status.code == 0 else 1)"

CMD ["python", "-m", "dev_server"]
