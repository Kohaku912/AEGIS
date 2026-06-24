FROM python:3.12-slim

LABEL org.aegis.service="browser-server"
LABEL org.aegis.version="0.1.0"

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src \
    AEGIS_GRPC_HOST=0.0.0.0 \
    AEGIS_GRPC_PORT=50053 \
    AEGIS_BROWSER_HEADLESS=true \
    PLAYWRIGHT_BROWSERS_PATH=/ms-playwright

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY browser-server/pyproject.toml ./pyproject.toml
COPY browser-server/src ./src
COPY browser-server/config.json* ./

RUN pip install --no-cache-dir -e ".[dev]"
RUN python -m playwright install chromium --with-deps
RUN mkdir -p /app/browser-profiles /app/browser-sessions /app/traces

EXPOSE 50053

HEALTHCHECK --interval=20s --timeout=5s --retries=5 --start-period=20s \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:50053/health', timeout=3)"

CMD ["python", "-m", "aegis_browser.main"]
