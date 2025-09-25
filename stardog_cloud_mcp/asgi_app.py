"""
ASGI application module for cloud deployment of Stardog Cloud MCP server.
"""

import logging
import os

from stardog_cloud_mcp.server import initialize_server

logging.basicConfig(
    level=logging.INFO,  # Change to logging.DEBUG for more verbosity
    format="%(asctime)s %(levelname)s %(name)s [PID %(process)d] %(message)s",
)


def create_asgi_app() -> object:
    """
    Create and configure the ASGI application for cloud deployment.
    """
    # Get configuration from environment variables
    endpoint = os.getenv("SDC_ENDPOINT", "https://cloud.stardog.com/api")
    api_token = os.getenv("SDC_API_TOKEN")
    client_id = os.getenv("SDC_CLIENT_ID", "VBX-APP")
    auth_token_override = os.getenv("SD_AUTH_TOKEN_OVERRIDE")
    port = int(os.getenv("SDC_PORT", "7000"))

    # Initialize server in cloud mode
    server = initialize_server(
        endpoint=endpoint,
        api_token=api_token,
        client_id=client_id,
        auth_token_override=auth_token_override or "",
        port=port,
        deployment_mode="cloud",
    )

    return server.http_app()


# Create the ASGI app instance
app = create_asgi_app()
