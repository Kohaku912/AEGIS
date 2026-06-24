FROM python:3.12-slim

LABEL org.aegis.service="room-server"
LABEL org.aegis.version="0.1.0"

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src \
    AEGIS_ROOM_HOST=0.0.0.0 \
    AEGIS_ROOM_PORT=50055 \
    AEGIS_ROOM_LIGHT_PROVIDER=mock

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY room-server/pyproject.toml ./pyproject.toml
COPY room-server/src ./src

RUN pip install --no-cache-dir -e ".[dev]"

EXPOSE 50055

HEALTHCHECK --interval=20s --timeout=5s --retries=5 --start-period=10s \
    CMD python -c "import grpc; from generated.aegis import common_pb2, room_server_pb2_grpc; ch=grpc.insecure_channel('localhost:50055'); r=room_server_pb2_grpc.RoomServerStub(ch).HealthCheck(common_pb2.HealthCheckRequest(server_id='docker-health'), timeout=3); raise SystemExit(0 if r.status.code == 0 else 1)"

CMD ["python", "-m", "aegis_room.main"]

