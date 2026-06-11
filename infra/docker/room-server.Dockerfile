# Room Server — IoT / Room control (placeholder)
# Phase 1.2: Minimal Python server

FROM python:3.12-slim

LABEL org.aegis.service="room-server"
LABEL org.aegis.version="0.1.0"

WORKDIR /app

RUN echo 'import http.server' > /app/placeholder.py && \
    echo 'import socketserver' >> /app/placeholder.py && \
    echo 'PORT = 50054' >> /app/placeholder.py && \
    echo 'Handler = http.server.SimpleHTTPRequestHandler' >> /app/placeholder.py && \
    echo 'with socketserver.TCPServer(("", PORT), Handler) as httpd:' >> /app/placeholder.py && \
    echo '    print(f"AEGIS Room Server — placeholder on :{PORT}")' >> /app/placeholder.py && \
    echo '    httpd.serve_forever()' >> /app/placeholder.py

EXPOSE 50054

HEALTHCHECK --interval=30s --timeout=5s --retries=3 --start-period=10s \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:50054')" || exit 1

CMD ["python", "/app/placeholder.py"]
