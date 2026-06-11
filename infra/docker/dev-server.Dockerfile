# Dev Server — Sandboxed self-development (placeholder)
# Phase 1.2: Minimal Python server with read-only repo mount
# SECURITY: No Docker socket, no host FS write, no secrets access.

FROM python:3.12-slim

LABEL org.aegis.service="dev-server"
LABEL org.aegis.version="0.1.0"

WORKDIR /app

RUN echo 'import http.server' > /app/placeholder.py && \
    echo 'import socketserver' >> /app/placeholder.py && \
    echo 'PORT = 50055' >> /app/placeholder.py && \
    echo 'Handler = http.server.SimpleHTTPRequestHandler' >> /app/placeholder.py && \
    echo 'with socketserver.TCPServer(("", PORT), Handler) as httpd:' >> /app/placeholder.py && \
    echo '    print(f"AEGIS Dev Server — placeholder on :{PORT}")' >> /app/placeholder.py && \
    echo '    httpd.serve_forever()' >> /app/placeholder.py

EXPOSE 50055

HEALTHCHECK --interval=30s --timeout=5s --retries=3 --start-period=10s \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:50055')" || exit 1

# Security: no Docker socket mount, no privileged mode
# Repository mounted as read-only by docker-compose.yml
CMD ["python", "/app/placeholder.py"]
