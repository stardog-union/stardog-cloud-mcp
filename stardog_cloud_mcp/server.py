import argparse
import logging
import os
import sys
from functools import wraps
from typing import Optional, cast

from fastmcp import FastMCP
from fastmcp.server.dependencies import get_context, get_http_headers
from stardog.cloud.client import AsyncClient as StardogAsyncClient

from stardog_cloud_mcp import __version__
from stardog_cloud_mcp.constants import Headers
from stardog_cloud_mcp.tools import ToolHandler

logger = logging.getLogger("stardog_cloud_mcp")


def tool_logging(tool_name: str):
    def decorator(func):
        @wraps(func)
        async def wrapper(*argts, **kwargs):
            ctx = get_context()
            if ctx is not None:
                await ctx.info(f"Entering tool: {tool_name}")
            result = await func(*argts, **kwargs)
            if ctx is not None:
                await ctx.info(f"Exiting tool: {tool_name}")
            return result

        return wrapper

    return decorator


def get_header_case_insensitive(
    headers: Optional[dict], header_name: str
) -> Optional[str]:
    """
    Get header value regardless of case.
    """
    if not headers:
        return None
    target = header_name.lower()

    # Check all headers with case-insensitive comparison
    for key, value in headers.items():
        if key.lower() == target:
            return value
    return None


async def resolve_params(
    header_name: str,
    arg_value: Optional[str],
    required: bool = False,
    error_message: str = "Parameter is required",
) -> Optional[str]:
    """
    Generic resolver for parameters that can come from headers or arguments.
    Headers take precedence over arguments when both are present.

    For API tokens, also checks Authorization header for Bearer tokens.

    Args:
        header_name: Name of the header to look for
        arg_value: Value provided via command-line argument
        required: Whether the parameter is required
        error_message: Error message to raise if required and not found

    Returns:
        Resolved parameter value

    Raises:
        ValueError: If parameter is required but not found
    """
    headers = get_http_headers()
    header_value = get_header_case_insensitive(headers, header_name)

    # Special handling for API token - also check Authorization header
    if header_name == Headers.STARDOG_CLOUD_API_KEY and not header_value:
        auth_header = get_header_case_insensitive(headers, "Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            header_value = auth_header[7:]  # Remove "Bearer " prefix

    if header_value and arg_value:
        return header_value

    resolved_value = header_value or arg_value

    if required and not resolved_value:
        raise ValueError(error_message)

    return resolved_value


def initialize_server(
    endpoint: str,
    api_token: str,
    client_id: str,
    auth_token_override: str,
    mode: str,
    port: int,
    timeout: Optional[float] = None,
):
    """
    Start the Stardog Cloud MCP server using FastMCP.
    """
    logger.info("Starting Stardog Cloud MCP server ⭐🐕☁️")
    server = FastMCP("stardog-cloud-mcp")
    if timeout is not None:
        cloud_client = StardogAsyncClient(base_url=endpoint, timeout=timeout)
    else:
        cloud_client = StardogAsyncClient(base_url=endpoint)
    tool_handler = ToolHandler(cloud_client)

    @server.tool(
        name="voicebox_settings",
        annotations={"title": "Voicebox: Settings", "readOnlyHint": True},
    )
    @tool_logging("voicebox_settings")
    async def voicebox_settings() -> str:
        """
        Get the settings for a Voicebox application in Stardog Cloud
        """
        resolved_token = cast(
            str,
            await resolve_params(
                Headers.STARDOG_CLOUD_API_KEY,
                api_token,
                required=True,
                error_message="API token is required",
            ),
        )
        resolved_client_id = await resolve_params(
            Headers.STARDOG_CLOUD_CLIENT_ID, client_id
        )
        return await tool_handler.handle_voicebox_settings(
            resolved_token, resolved_client_id
        )

    @server.tool(
        name="voicebox_ask",
        annotations={"title": "Voicebox: Ask Questions", "readOnlyHint": True},
    )
    @tool_logging("voicebox_ask")
    async def voicebox_ask(
        question: str,
        conversation_id: Optional[str] = None,
    ) -> str:
        """
        Ask a question to Voicebox and get a natural language response
        """
        resolved_token = cast(
            str,
            await resolve_params(
                Headers.STARDOG_CLOUD_API_KEY,
                api_token,
                required=True,
                error_message="API token is required",
            ),
        )
        resolved_client_id = await resolve_params(
            Headers.STARDOG_CLOUD_CLIENT_ID, client_id
        )
        resolved_auth_token_override = await resolve_params(
            Headers.STARDOG_AUTH_TOKEN_OVERRIDE, auth_token_override
        )
        return await tool_handler.handle_voicebox_ask(
            api_token=resolved_token,
            client_id=resolved_client_id,
            question=question,
            conversation_id=conversation_id,
            stardog_auth_token_override=resolved_auth_token_override,
        )

    @server.tool(
        name="voicebox_generate_query",
        annotations={"title": "Voicebox: Generate SPARQL", "readOnlyHint": True},
    )
    @tool_logging("voicebox_generate_query")
    async def voicebox_generate_query(
        question: str,
        conversation_id: Optional[str] = None,
    ) -> str:
        """
        Generate a SPARQL query from a natural language question using Voicebox
        """
        resolved_token = cast(
            str,
            await resolve_params(
                Headers.STARDOG_CLOUD_API_KEY,
                api_token,
                required=True,
                error_message="API token is required",
            ),
        )
        resolved_client_id = await resolve_params(
            Headers.STARDOG_CLOUD_CLIENT_ID, client_id
        )
        resolved_auth_token_override = await resolve_params(
            Headers.STARDOG_AUTH_TOKEN_OVERRIDE, auth_token_override
        )
        return await tool_handler.handle_voicebox_generate_query(
            api_token=resolved_token,
            client_id=resolved_client_id,
            question=question,
            conversation_id=conversation_id,
            stardog_auth_token_override=resolved_auth_token_override,
        )

    if mode == "http":
        logger.info(
            f"\U0001f310 Starting MCP server in HTTP mode at http://localhost:{port}"
        )
        server.run(transport="streamable-http", host="0.0.0.0", port=port)
    else:
        logger.info("\U0001f9ea Starting MCP server in STDIO (local) mode")
        server.run(transport="stdio")
    return server


def main():
    """Main entry point for the Stardog Cloud MCP Server."""
    parser = argparse.ArgumentParser(
        description="Stardog Cloud MCP Server - Model Context Protocol server for Stardog Voicebox",
        epilog="Environment variables: SDC_ENDPOINT, SDC_API_TOKEN, SDC_TIMEOUT, SDC_MCP_SERVER_MODE, SD_AUTH_TOKEN_OVERRIDE",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {__version__}"
    )

    parser.add_argument(
        "--endpoint",
        type=str,
        default=os.getenv("SDC_ENDPOINT", "https://cloud.stardog.com/api"),
        help="Stardog Cloud API endpoint (default: %(default)s)",
    )

    parser.add_argument(
        "--token",
        type=str,
        help="Stardog Cloud API token (required, can also use SDC_API_TOKEN env var)",
        default=os.getenv("SDC_API_TOKEN"),
    )

    parser.add_argument(
        "--mode",
        choices=["stdio", "http"],
        default=os.getenv("SDC_MCP_SERVER_MODE", "stdio"),
        help="Server mode: stdio for local Claude Desktop, http for remote clients (default: %(default)s)",
    )

    parser.add_argument(
        "--port",
        type=int,
        default=7000,
        help="Port for HTTP server mode (default: %(default)s)",
    )

    parser.add_argument(
        "--client_id",
        type=str,
        default="VBX-APP",
        help="Voicebox application client ID (default: %(default)s)",
    )

    parser.add_argument(
        "--auth_token_override",
        type=str,
        help="Override Stardog auth token for specific user context (optional)",
        default=os.getenv("SD_AUTH_TOKEN_OVERRIDE"),
    )

    parser.add_argument(
        "--timeout",
        type=float,
        default=float(os.getenv("SDC_TIMEOUT")) if os.getenv("SDC_TIMEOUT") else None,
        help="Request timeout in seconds for Stardog Cloud API calls",
    )

    args = parser.parse_args()

    try:
        initialize_server(
            args.endpoint,
            args.token,
            args.client_id,
            args.auth_token_override,
            args.mode,
            args.port,
            args.timeout,
        )
    except KeyboardInterrupt:  # pragma: no cover
        logger.info("Caught manual interrupt, server shutting down...")
    except Exception as e:  # pragma: no cover
        logger.error(f"Error running server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
