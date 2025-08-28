import argparse
import logging
import os
import sys
from functools import wraps
from typing import Optional

from fastmcp import FastMCP
from fastmcp.server.dependencies import get_context, get_http_headers
from stardog.cloud.client import AsyncClient as StardogAsyncClient

from tools import ToolHandler

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


async def get_api_token(arg_api_token: str) -> Optional[str]:
    """
    Retrieve the API token from HTTP headers if available.
    If both HTTP header and argument token are present, prefer HTTP header token.
    """
    headers = get_http_headers()
    print(f"HEADERS: {headers}", file=sys.stderr)
    http_header_token = headers.get("x-sdc-api-key") if headers else None
    ctx = get_context()
    if ctx is not None:
        await ctx.info(
            f"PRINTING TOKEN VALUES: HTTP Header Token: {http_header_token}, Argument Token: {arg_api_token}"
        )
    print(
        f"PRINTING TOKEN VALUES: HTTP Header Token: {http_header_token}, Argument Token: {arg_api_token}",
        file=sys.stderr,
    )
    if http_header_token and arg_api_token:
        return http_header_token
    resolved_token = http_header_token or arg_api_token
    if not resolved_token:
        raise ValueError("API token is required")
    return resolved_token


async def get_client_id(arg_client_id: str) -> Optional[str]:
    """
    Retrieve the client ID from HTTP headers if available.
    If both HTTP header and argument client ID are present, prefer HTTP header client ID.
    """
    headers = get_http_headers()
    print(f"HEADERS: {headers}", file=sys.stderr)
    http_header_client_id = headers.get("x-sdc-client-id") if headers else None
    ctx = get_context()
    if ctx is not None:
        await ctx.info(
            f"PRINTING CLIENT ID VALUES: HTTP Header Client ID: {http_header_client_id}, Argument Client ID: {arg_client_id}"
        )
    print(
        f"PRINTING CLIENT ID VALUES: HTTP Header Client ID: {http_header_client_id}, Argument Client ID: {arg_client_id}",
        file=sys.stderr,
    )
    if http_header_client_id and arg_client_id:
        return http_header_client_id
    return http_header_client_id or arg_client_id


def initialize_server(
    endpoint: str, api_token: str, client_id: str, mode: str, port: int
):
    """
    Start the Stardog Cloud MCP server using FastMCP.
    """
    logger.info("Starting Stardog Cloud MCP server ⭐🐕☁️")
    server = FastMCP("stardog-cloud-mcp")
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
        resolved_token = await get_api_token(api_token)
        resolved_client_id = await get_client_id(client_id)
        print(
            f"VOICEBOX_SETTINGS TOKEN-settings: {resolved_token} & {resolved_client_id}",
            file=sys.stderr,
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
        stardog_auth_token_override: Optional[str] = None,
    ) -> str:
        """
        Ask a question to Voicebox and get a natural language response
        """
        resolved_token = await get_api_token(api_token)
        resolved_client_id = await get_client_id(client_id)
        print(
            f"VOICEBOX_SETTINGS TOKEN-settings: {resolved_token} & {resolved_client_id}",
            file=sys.stderr,
        )
        return await tool_handler.handle_voicebox_ask(
            api_token=resolved_token,
            client_id=resolved_client_id,
            question=question,
            conversation_id=conversation_id,
            stardog_auth_token_override=stardog_auth_token_override,
        )

    @server.tool(
        name="voicebox_generate_query",
        annotations={"title": "Voicebox: Generate SPARQL", "readOnlyHint": True},
    )
    @tool_logging("voicebox_generate_query")
    async def voicebox_generate_query(
        question: str,
        conversation_id: Optional[str] = None,
        stardog_auth_token_override: Optional[str] = None,
    ) -> str:
        """
        Generate a SPARQL query from a natural language question using Voicebox
        """
        resolved_token = await get_api_token(api_token)
        resolved_client_id = await get_client_id(client_id)
        print(
            f"VOICEBOX_SETTINGS TOKEN-settings: {resolved_token} & {resolved_client_id}",
            file=sys.stderr,
        )
        return await tool_handler.handle_voicebox_generate_query(
            api_token=resolved_token,
            client_id=resolved_client_id,
            question=question,
            conversation_id=conversation_id,
            stardog_auth_token_override=stardog_auth_token_override,
        )

    if mode == "http":
        logger.info(
            f"\U0001f310 Starting MCP server in HTTP mode at http://localhost:{port}"
        )
        server.run(transport="streamable-http", host="0.0.0.0", port=port)
    else:
        logger.info("\U0001f9ea Starting MCP server in STDIO (local) mode")
        server.run(transport="stdio")


if __name__ == "__main__":
    # TODO: can remove, following prints are for logging into the MCP logs
    print("Starting Stardog MCP server...", file=sys.stderr)
    parser = argparse.ArgumentParser(description="Stardog Cloud MCP Server")
    parser.add_argument(
        "--endpoint",
        type=str,
        default=os.getenv("SDC_ENDPOINT", "https://cloud.stardog.com/api"),
        help="Stardog Cloud API endpoint (default: https://cloud.stardog.com/api)",
    )
    parser.add_argument(
        "--token",
        type=str,
        help="Stardog Cloud API token",
        default=os.getenv("API_TOKEN"),
    )
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    parser.add_argument(
        "--mode", choices=["stdio", "http"], default=os.getenv("MCP_MODE", "stdio")
    )
    parser.add_argument("--port", type=int, default=7000)
    parser.add_argument("--client_id", type=str, default="VBX-APP")

    args = parser.parse_args()
    print(f"ENDPOINT -> {args.endpoint}", file=sys.stderr)

    try:
        print(
            "Now going to actually start the Stardog Cloud MCP server...",
            file=sys.stderr,
        )
        # if args.mode == "stdio":
        #     asyncio.run(start_server(args.endpoint, args.token, args.mode, args.port))
        # else:
        #     start_server(args.endpoint, args.token, args.mode, args.port)
        initialize_server(
            args.endpoint, args.token, args.client_id, args.mode, args.port
        )
    except KeyboardInterrupt:
        logger.info("Caught manual interrupt, server shutting down...")
    except Exception as e:
        logger.error(f"Error running server: {e}")
        sys.exit(1)
