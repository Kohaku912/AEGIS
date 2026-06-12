FROM python:3.12-slim

WORKDIR /app

# Install system dependencies for Chromium and browser-use
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    gnupg \
    chromium \
    chromium-driver \
    fonts-ipafont-gothic \
    fonts-wqy-zenhei \
    fonts-thai-tlwg \
    fonts-kacst \
    fonts-freefont-ttf \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set Chromium environment
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-browser
ENV DISPLAY=:99
ENV CHROMIUM_PATH=/usr/bin/chromium

# Copy requirements
COPY pyproject.toml .
COPY src/ src/

# Install Python dependencies
RUN pip install --no-cache-dir \
    playwright \
    browser-use \
    openai \
    langchain-openai \
    grpcio \
    protobuf \
    pydantic \
    2>/dev/null || true

# Install Playwright browsers
RUN playwright install chromium 2>/dev/null || true

# Create directories
RUN mkdir -p /app/browser-profiles /app/browser-sessions /app/traces

# Expose port
EXPOSE 50053

# Default command
CMD ["python", "-m", "aegis_browser.main"]
