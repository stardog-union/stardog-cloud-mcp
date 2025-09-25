FROM python:3.12-slim-trixie

WORKDIR /app

# Install uv for package management and running
RUN pip install --no-cache-dir uv

# Set environment variables
ENV PYTHONPATH=/app \
    PYTHONUNBUFFERED=1 \
    SDC_ENDPOINT=https://cloud.stardog.com/api \
    SDC_DEPLOYMENT_MODE=launchpad \

# Copy project files
COPY pyproject.toml ./
COPY README.md ./
COPY stardog_cloud_mcp/ ./stardog_cloud_mcp/

# Install project dependencies using uv (including uvicorn for cloud deployment)
RUN uv pip install --system . && \
    uv pip install --system uvicorn[standard]

# Expose HTTP port
EXPOSE 7000 8000

# Create entrypoint script for flexible deployment
COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

# Use flexible entrypoint
ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]