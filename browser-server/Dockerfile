FROM python:3.12-slim

WORKDIR /app

# Install system dependencies for Chromium
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
    && rm -rf /var/lib/apt/lists/*

# Set Chromium environment
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-browser
ENV DISPLAY=:99

# Copy requirements
COPY pyproject.toml .
COPY src/ src/

# Install Python dependencies
RUN pip install --no-cache-dir playwright browser-use openai 2>/dev/null || true

# Install Playwright browsers
RUN playwright install chromium 2>/dev/null || true

# Create profile directories
RUN mkdir -p /app/browser-profiles /app/browser-sessions

# Expose port
EXPOSE 50052

# Default command
CMD ["python", "-m", "aegis_browser.main"]
