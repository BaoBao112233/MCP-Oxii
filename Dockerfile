# Multi-service Dockerfile for MCP Oxii-server + Temp API
FROM python:3.10-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    supervisor \
    nginx \
    && rm -rf /var/lib/apt/lists/*

# Install poetry for MCP server dependencies
RUN pip install poetry

# === MCP Oxii-Server Setup ===
# Create directory for MCP server
RUN mkdir -p /app/mcp-server

# Copy MCP server files
COPY mcp/oxii-server/pyproject.toml /app/mcp-server/
COPY mcp/oxii-server/main.py /app/mcp-server/
COPY mcp/oxii-server/tools/ /app/mcp-server/tools/

# Install MCP server dependencies
WORKDIR /app/mcp-server
RUN poetry config virtualenvs.create false \
    && poetry install --only main --no-root

# === Temp API Setup ===
# Create directory for temp API
RUN mkdir -p /app/temp-api
WORKDIR /app/temp-api

# Copy temp API requirements and install
COPY temp_api/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy temp API files
COPY temp_api/ .

# === Configuration Files ===
WORKDIR /app

# Create supervisor configuration directory
RUN mkdir -p /var/log/supervisor

# Copy configuration files
COPY docker-configs/ /app/configs/

# Set up configurations
RUN cp /app/configs/supervisord.conf /etc/supervisor/conf.d/ \
    && cp /app/configs/nginx.conf /etc/nginx/ \
    && chmod +x /app/configs/start.sh

# Create non-root user for security (but supervisor needs root)
RUN useradd --create-home --shell /bin/bash appuser

# Expose port 80 for nginx reverse proxy
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost/health || exit 1

# Start the application
CMD ["/app/configs/start.sh"]