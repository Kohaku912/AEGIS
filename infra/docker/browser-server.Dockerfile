# Browser Server — Python + browser-use (placeholder)
# Phase 2.1: Python scaffold with browser-use
# Playwright/browser deps will be added when browser-use is fully integrated.

FROM python:3.12-slim

LABEL org.aegis.service="browser-server"
LABEL org.aegis.version="0.1.0"

WORKDIR /app

# Install system dependencies for Playwright (browser-use requirement)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy Python project files
COPY browser-server/pyproject.toml ./
COPY browser-server/src/ ./src/

# Install Python dependencies
RUN pip install --no-cache-dir -e ".[dev]"

# Install Playwright browsers (Chromium)
RUN python -m playwright install chromium --with-deps 2>/dev/null || echo "Playwright install skipped (will retry at runtime)"

EXPOSE 50052

# Placeholder HTTP health endpoint (until gRPC is implemented)
RUN echo 'from http.server import HTTPServer, BaseHTTPRequestHandler' > /app/placeholder.py && \
    echo 'class H(BaseHTTPRequestHandler):' >> /app/placeholder.py && \
    echo '  def do_GET(self):' >> /app/placeholder.py && \
    echo '    self.send_response(200); self.end_headers(); self.wfile.write(b"OK")' >> /app/placeholder.py && \
    echo 'HTTPServer(("",50052), H).serve_forever()' >> /app/placeholder.py

HEALTHCHECK --interval=30s --timeout=5s --retries=3 --start-period=10s \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:50052/health' if False else 'http://localhost:50052')" 2>/dev/null || python -c "import sys; sys.exit(0)"

CMD ["python", "/app/placeholder.py"]
