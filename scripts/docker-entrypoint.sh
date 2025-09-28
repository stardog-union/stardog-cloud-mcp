#!/bin/bash
set -e

# Default values
SDC_DEPLOYMENT_MODE=${SDC_DEPLOYMENT_MODE:-launchpad}
SDC_PORT=${SDC_PORT:-7000}
SDC_WORKERS=${SDC_WORKERS:-4}

echo "Starting Stardog Cloud MCP server in $SDC_DEPLOYMENT_MODE mode"

case "$SDC_DEPLOYMENT_MODE" in
  "launchpad")
    echo "🚀 Launchpad mode: using HTTP transport on port $SDC_PORT"
    exec uv run stardog-cloud-mcp --deployment launchpad --port "$SDC_PORT" "$@"
    ;;

  "cloud")
    echo "☁️ Cloud mode: using ASGI with $SDC_WORKERS workers on port $SDC_PORT"
    exec uvicorn stardog_cloud_mcp.asgi_app:app \
      --host 0.0.0.0 \
      --port "$SDC_PORT" \
      --workers "$SDC_WORKERS" \
      --log-level debug \
      --access-log \
      "$@"
    ;;

  *)
    echo "Unknown deployment mode: $SDC_DEPLOYMENT_MODE"
    echo "Available modes: launchpad, cloud"
    exit 1
    ;;
esac