# Browser Server — Node.js + Playwright (placeholder)
# Phase 1.2: Minimal Node.js server with health endpoint
# Playwright dependencies will be added in Phase 2 when Browser Server is implemented.

FROM node:22-slim

LABEL org.aegis.service="browser-server"
LABEL org.aegis.version="0.1.0"

WORKDIR /app

# Placeholder: create minimal HTTP server for health check
RUN echo 'const http = require("http");' > /app/placeholder.js && \
    echo 'const server = http.createServer((req, res) => {' >> /app/placeholder.js && \
    echo '  if (req.url === "/health") { res.writeHead(200); res.end("OK"); }' >> /app/placeholder.js && \
    echo '  else { res.writeHead(200); res.end("AEGIS Browser Server — placeholder"); }' >> /app/placeholder.js && \
    echo '});' >> /app/placeholder.js && \
    echo 'server.listen(50052, () => console.log("Browser Server listening on :50052"));' >> /app/placeholder.js

EXPOSE 50052

HEALTHCHECK --interval=30s --timeout=5s --retries=3 --start-period=10s \
    CMD node -e "require('http').get('http://localhost:50052/health', (r) => { process.exit(r.statusCode === 200 ? 0 : 1) })"

CMD ["node", "/app/placeholder.js"]
