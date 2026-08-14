FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY pyproject.toml .
COPY src/ src/

# Install Python dependencies
RUN pip install --no-cache-dir -e ".[dev]" 2>/dev/null || \
    pip install --no-cache-dir flask grpcio grpcio-tools pydantic openai requests

# Create data directories
RUN mkdir -p /app/data /app/evaluation/reports

# Expose ports
EXPOSE 50051 8090

# Default command
CMD ["python", "-m", "aegis_ai.main"]
