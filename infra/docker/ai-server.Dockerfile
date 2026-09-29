FROM node:22-bookworm-slim AS web-ui-build

WORKDIR /web-ui

COPY web-ui/package*.json ./
RUN if [ -f package-lock.json ]; then npm ci; else npm install; fi
# Phase L6 fix: docker COPY adds files but never removes files that have
# been deleted from the source tree. Stale files in older image layers
# (e.g. HomePage.tsx, GlobalSearch.tsx, PolicySimulationPage.tsx) keep
# tsc -b happy at file-presence level but cause TS2305 "Module has no
# exported member X" because they import symbols that no longer exist in
# the new source. Wipe the previous web-ui tree (except node_modules) before
# re-copying.
RUN find /web-ui -mindepth 1 -maxdepth 1 \
    ! -name 'node_modules' \
    -exec rm -rf {} +
COPY web-ui ./
COPY design-tokens /design-tokens
RUN npm run build

FROM python:3.12-slim

LABEL org.aegis.service="ai-server"
LABEL org.aegis.version="0.1.0"

WORKDIR /app

ARG AEGIS_SOURCE_REVISION=unknown
ENV PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src \
    AEGIS_GRPC_HOST=0.0.0.0 \
    AEGIS_GRPC_PORT=50051 \
    AEGIS_SOURCE_REVISION=$AEGIS_SOURCE_REVISION

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

COPY ai-server/pyproject.toml ./pyproject.toml
# Install runtime dependencies only. The `[dev]` extra (ruff, grpcio-tools,
# mypy) is intentionally NOT installed here: no runtime module imports them
# (proto stubs are committed under src/generated), and shipping build tooling
# in the production image needlessly enlarges the attack surface.
RUN mkdir -p src/aegis_ai \
    && touch src/aegis_ai/__init__.py \
    && pip install --no-cache-dir . flask pyyaml requests

COPY ai-server/src ./src
COPY ai-server/config ./config
COPY ai-server/capabilities ./capabilities
COPY ai-server/apps ./apps
COPY protos /protos
COPY --from=web-ui-build /ai-server/src/aegis_ai/web/static/ui-v2 ./src/aegis_ai/web/static/ui-v2

RUN pip install --no-cache-dir --no-deps -e .
RUN mkdir -p /app/data /app/evaluation/reports

EXPOSE 50051 8090

HEALTHCHECK --interval=15s --timeout=5s --retries=5 --start-period=20s \
    CMD python -c "import grpc; from generated.aegis import ai_server_pb2_grpc, common_pb2; ch=grpc.insecure_channel('localhost:50051'); r=ai_server_pb2_grpc.AIServerStub(ch).HealthCheck(common_pb2.HealthCheckRequest(server_id='docker-health'), timeout=3); raise SystemExit(0 if r.status.code == 0 else 1)"

CMD ["python", "-m", "aegis_ai.docker_entrypoint"]
