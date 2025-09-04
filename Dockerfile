FROM python:3.12-slim-bookworm

WORKDIR /app

# Install uv for package management and running
RUN pip install --no-cache-dir uv

# Set environment variables
ENV PYTHONPATH=/app \
    PYTHONUNBUFFERED=1 \
    SDC_ENDPOINT=https://cloud.stardog.com/api

# Copy project files
COPY pyproject.toml ./
COPY README.md ./
COPY stardog_cloud_mcp/ ./stardog_cloud_mcp/

# Install project dependencies using uv
RUN uv pip install --system .

# Expose HTTP port
EXPOSE 7000

# Run the FastMCP server using the console script in HTTP mode
ENTRYPOINT ["uv", "run", "stardog-cloud-mcp", "--mode", "http"]