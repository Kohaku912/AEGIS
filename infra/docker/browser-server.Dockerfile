# Browser Server — Node.js + Playwright (placeholder)
# Phase 1.2: Minimal Node.js server with health endpoint

FROM node:22-slim

LABEL org.aegis.service="browser-server"
LABEL org.aegis.version="0.1.0"

WORKDIR /app

# Install Chromium dependencies for Playwright
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    libnss3 libnspr4 libatk-bridge2.0-0 libdrm2 libxkbcommon0 \
    libxcomposite1 libxdamage1 libxfixes3 libxrandr2 libgbm1 \
    libpango-1.0-0 libcairo2 libasound2t64 \
    && rm -rf /var/lib/apt/lists/*

# Copy package.json (placeholder until real implementation)
COPY browser-server/package.json* ./

# Install Node.js dependencies (if package.json exists)
RUN if [ -f package.json ]; then npm install; fi

# Copy source code
COPY browser-server/src/ ./src/

# Placeholder: create minimal HTTP server for health check
RUN echo 'const http = require("http");' > /app/placeholder.js && \
    echo 'const server = http.createServer((req, res) => {' >> /app/placeholder.js && \
    echo '  if (req.url === "/health") { res.writeHead(200); res.end("OK"); }' >> /app/placeholder.js && \
    echo '  else { res.writeHead(200); res.end("AEGIS Browser Server — placeholder"); }' >> /app/placeholder.js && \
    echo '});' >> /app/placeholder.js && \
    echo 'server.listen(50052, () => console.log("Browser Server listening on :50052"));' >> /app/placeholder.js

EXPOSE 50052

HEALTHCHECK --interval=30s --timeout=5s --retries=3 --start-period=10s \
    CMD curl -f http://localhost:50052/health || exit 1

CMD ["node", "/app/placeholder.js"]
