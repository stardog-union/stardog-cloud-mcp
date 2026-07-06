ARG BASE_IMAGE=python:3.12-slim-trixie

#############################
# Builder stage: install dependencies into a virtualenv
#############################
FROM ${BASE_IMAGE} AS builder

WORKDIR /app

# Install uv for package management
RUN pip install --no-cache-dir uv

# Copy project files needed for installation
COPY pyproject.toml ./
COPY README.md ./
COPY stardog_cloud_mcp/ ./stardog_cloud_mcp/

# Install the package and its dependencies into an isolated venv that the
# runtime stage copies wholesale (build tooling like uv/pip stays behind).
RUN uv venv /opt/venv && uv pip install --python /opt/venv/bin/python .

#############################
# Runtime stage: minimal image, non-root user
#############################
FROM ${BASE_IMAGE} AS runtime

# Unprivileged runtime user (CIS: containers must not run as root). The server
# only binds port 7000 (>1024) and writes nothing to disk, so no extra
# permissions are needed.
RUN groupadd --gid 1001 nonroot && \
    useradd --uid 1001 --gid nonroot --create-home nonroot

WORKDIR /app

# PYTHONPATH=/app keeps the docker-compose dev workflow working: mounting the
# repo over /app lets local source take import precedence over the venv copy.
ENV PYTHONPATH=/app \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH" \
    SDC_ENDPOINT=https://cloud.stardog.com/api

COPY --from=builder /opt/venv /opt/venv

USER nonroot

# Expose HTTP port
EXPOSE 7000

# Run the FastMCP server using the console script in HTTP mode
ENTRYPOINT ["stardog-cloud-mcp", "--mode", "http"]
