FROM python:3.12-slim-bookworm

WORKDIR /app

# Install uv runner for FastMCP
RUN pip install --no-cache-dir uv

# Set PYTHONPATH so src is recognized as a package root
ENV PYTHONPATH=/app/src

# Copy project files
COPY pyproject.toml ./
COPY README.md ./
COPY src/ ./src/

# Install project dependencies
RUN pip install --no-cache-dir .

# Expose HTTP port
EXPOSE 7000

# Run the FastMCP server using uv in HTTP mode
ENTRYPOINT ["uv", "run", "src/server.py", "--mode", "http"]