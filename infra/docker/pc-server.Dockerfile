# PC Server — PC control (placeholder, NOT used by docker-compose.yml)
# Phase 1.2: Minimal Python server.
#
# The real PC Server is the Rust implementation in pc-server/ and listens on
# port 50052 (see AGENTS.md). This placeholder exists only for early smoke
# tests; docker-compose.yml intentionally does not build it.

FROM python:3.12-slim

LABEL org.aegis.service="pc-server"
LABEL org.aegis.version="0.1.0"

WORKDIR /app

# Placeholder server script
RUN echo 'import http.server' > /app/placeholder.py && \
    echo 'import socketserver' >> /app/placeholder.py && \
    echo 'PORT = 50052' >> /app/placeholder.py && \
    echo 'Handler = http.server.SimpleHTTPRequestHandler' >> /app/placeholder.py && \
    echo 'with socketserver.TCPServer(("", PORT), Handler) as httpd:' >> /app/placeholder.py && \
    echo '    print(f"AEGIS PC Server — placeholder on :{PORT}")' >> /app/placeholder.py && \
    echo '    httpd.serve_forever()' >> /app/placeholder.py

EXPOSE 50052

HEALTHCHECK --interval=30s --timeout=5s --retries=3 --start-period=10s \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:50052')" || exit 1

CMD ["python", "/app/placeholder.py"]
