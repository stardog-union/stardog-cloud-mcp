import os
import subprocess
import sys
from unittest.mock import patch, AsyncMock

import pytest
from fastmcp import Client

from stardog_cloud_mcp.constants import Headers
from stardog_cloud_mcp.server import initialize_server, resolve_params


@pytest.fixture
def mcp_server():
    with patch('stardog_cloud_mcp.server.StardogAsyncClient') as mock_stardog_client, \
         patch('stardog_cloud_mcp.server.ToolHandler') as mock_tool_handler, \
         patch('fastmcp.FastMCP.run') as mock_run:
        mock_run.return_value = None  # Prevent running the server loop
        # Setup mocks for ToolHandler methods
        mock_handler_instance = mock_tool_handler.return_value
        mock_handler_instance.handle_voicebox_settings = AsyncMock(return_value="Voicebox App Settings: test-vbx-app-1")
        mock_handler_instance.handle_voicebox_ask = AsyncMock(return_value="Answer: Test answer for flight plan")
        mock_handler_instance.handle_voicebox_generate_query = AsyncMock(return_value="SPARQL: SELECT * WHERE { ?flight ?hasPlan ?plan } | Show me all flights")
        # Initialize the real server (this registers the real tools)
        server = initialize_server(
            endpoint="dummy-endpoint",
            api_token="dummy-token",
            client_id="test-client",
            auth_token_override=None,
            port=7000,
            deployment_mode="development"
        )
        # Return the server instance for FastMCP Client
        return server

@pytest.mark.asyncio
async def test_voicebox_settings(mcp_server):
    async with Client(mcp_server) as client:
        result = await client.call_tool("voicebox_settings", {})
        print("Settings result:", result.data)
        assert "Voicebox App Settings" in result.data
        assert "test-vbx-app-1" in result.data

@pytest.mark.asyncio
async def test_voicebox_ask(mcp_server):
    async with Client(mcp_server) as client:
        result = await client.call_tool("voicebox_ask", {"question": "What is the flight plan?"})
        print("Ask result:", result.data)
        assert "Answer" in result.data
        assert "flight plan" in result.data

@pytest.mark.asyncio
async def test_voicebox_generate_query(mcp_server):
    async with Client(mcp_server) as client:
        result = await client.call_tool("voicebox_generate_query", {"question": "Show me all flights"})
        print("Generate query result:", result.data)
        assert "SPARQL" in result.data or "SELECT" in result.data
        assert "Show me all flights" in result.data

@patch('fastmcp.FastMCP.run')
@pytest.mark.asyncio
async def test_voicebox_settings_missing_token(mock_run, monkeypatch):
    async def raise_value_error(*args, **kwargs):
        raise ValueError("API token is required")
    monkeypatch.setattr("stardog_cloud_mcp.server.resolve_params", raise_value_error)
    mock_run.return_value = None
    server_instance = initialize_server(
        endpoint="dummy-endpoint",
        api_token="",
        client_id="test-client",
        auth_token_override=None,
        port=7000,
        deployment_mode="development"
    )
    async with Client(server_instance) as client:
        with pytest.raises(Exception):
            await client.call_tool("voicebox_settings", {})

@patch('fastmcp.FastMCP.run')
@patch('stardog_cloud_mcp.server.ToolHandler')
@pytest.mark.asyncio
async def test_voicebox_settings_with_header(mock_tool_handler, mock_run, monkeypatch):
    monkeypatch.setattr("stardog_cloud_mcp.server.get_http_headers", lambda: {Headers.STARDOG_CLOUD_API_KEY: "header-token"})
    mock_run.return_value = None
    mock_handler_instance = mock_tool_handler.return_value
    mock_handler_instance.handle_voicebox_settings = AsyncMock(return_value="Voicebox App Settings: test-vbx-app-1")
    server_instance = initialize_server(
        endpoint="dummy-endpoint",
        api_token="arg-token",
        client_id="test-client",
        auth_token_override=None,
        port=7000,
        deployment_mode="development"
    )
    async with Client(server_instance) as client:
        result = await client.call_tool("voicebox_settings", {})
        assert "Voicebox App Settings" in result.data

@pytest.mark.asyncio
async def test_resolve_headers_header_only(monkeypatch):
    monkeypatch.setattr("stardog_cloud_mcp.server.get_http_headers", lambda: {Headers.STARDOG_CLOUD_CLIENT_ID: "header-client"})
    result = await resolve_params(Headers.STARDOG_CLOUD_CLIENT_ID, "arg-client")
    assert result == "header-client"


@pytest.mark.asyncio
async def test_resolve_headers_case_insensitive(monkeypatch):
    # Test with different case variations
    monkeypatch.setattr("stardog_cloud_mcp.server.get_http_headers", lambda: {"X-SDC-Client-ID": "header-client"})
    result = await resolve_params(Headers.STARDOG_CLOUD_CLIENT_ID, "arg-client")
    assert result == "header-client"
    
    monkeypatch.setattr("stardog_cloud_mcp.server.get_http_headers", lambda: {"X-Sdc-Client-Id": "header-client2"})
    result = await resolve_params(Headers.STARDOG_CLOUD_CLIENT_ID, "arg-client")
    assert result == "header-client2"

@pytest.mark.asyncio
async def test_resolve_headers_arg_only(monkeypatch):
    monkeypatch.setattr("stardog_cloud_mcp.server.get_http_headers", lambda: None)
    result = await resolve_params(Headers.STARDOG_CLOUD_CLIENT_ID, "arg-client")
    assert result == "arg-client"

@pytest.mark.asyncio
async def test_resolve_headers_none(monkeypatch):
    monkeypatch.setattr("stardog_cloud_mcp.server.get_http_headers", lambda: None)
    result = await resolve_params(Headers.STARDOG_CLOUD_CLIENT_ID, None)
    assert result is None


@pytest.mark.asyncio
async def test_resolve_headers_auth_token_header_only(monkeypatch):
    monkeypatch.setattr("stardog_cloud_mcp.server.get_http_headers", lambda: {Headers.STARDOG_AUTH_TOKEN_OVERRIDE: "header-auth"})
    result = await resolve_params(Headers.STARDOG_AUTH_TOKEN_OVERRIDE, None)
    assert result == "header-auth"


@pytest.mark.asyncio
async def test_resolve_headers_auth_token_arg_only(monkeypatch):
    monkeypatch.setattr("stardog_cloud_mcp.server.get_http_headers", lambda: None)
    result = await resolve_params(Headers.STARDOG_AUTH_TOKEN_OVERRIDE, "arg-auth")
    assert result == "arg-auth"


@pytest.mark.asyncio
async def test_resolve_headers_both_prefer_header(monkeypatch):
    monkeypatch.setattr("stardog_cloud_mcp.server.get_http_headers", lambda: {Headers.STARDOG_AUTH_TOKEN_OVERRIDE: "header-auth"})
    result = await resolve_params(Headers.STARDOG_AUTH_TOKEN_OVERRIDE, "arg-auth")
    assert result == "header-auth"


@pytest.mark.asyncio
async def test_resolve_headers_auth_token_none(monkeypatch):
    monkeypatch.setattr("stardog_cloud_mcp.server.get_http_headers", lambda: None)
    result = await resolve_params(Headers.STARDOG_AUTH_TOKEN_OVERRIDE, None)
    assert result is None

# CLI entrypoint coverage
@patch('stardog_cloud_mcp.server.initialize_server', return_value=None)
def test_main_entrypoint(mock_init):
    script_path = os.path.join(os.path.dirname(__file__), '../stardog_cloud_mcp/server.py')
    result = subprocess.run([
        sys.executable, script_path,
        '--endpoint', 'dummy-endpoint',
        '--token', 'dummy-token',
        '--client_id', 'test-client',
        '--auth_token_override', 'test-auth-override',
        '--deployment', 'development',
        '--port', '7000'
    ], capture_output=True, text=True)
    # Assert successful exit
    assert result.returncode == 0


@pytest.mark.asyncio
async def test_resolve_headers_required_missing():
    with pytest.raises(ValueError, match="API token is required"):
        await resolve_params(Headers.STARDOG_CLOUD_API_KEY, None, required=True, error_message="API token is required")


@pytest.mark.asyncio
async def test_resolve_headers_required_missing_with_empty_headers(monkeypatch):
    monkeypatch.setattr("stardog_cloud_mcp.server.get_http_headers", lambda: {})
    with pytest.raises(ValueError, match="API token is required"):
        await resolve_params(Headers.STARDOG_CLOUD_API_KEY, None, required=True, error_message="API token is required")


@pytest.mark.asyncio
async def test_resolve_headers_api_token_case_insensitive(monkeypatch):
    # Test with uppercase header
    monkeypatch.setattr("stardog_cloud_mcp.server.get_http_headers", lambda: {"X-SDC-API-KEY": "token-upper"})
    result = await resolve_params(Headers.STARDOG_CLOUD_API_KEY, None)
    assert result == "token-upper"
    
    # Test with mixed case header
    monkeypatch.setattr("stardog_cloud_mcp.server.get_http_headers", lambda: {"X-Sdc-Api-Key": "token-mixed"})
    result = await resolve_params(Headers.STARDOG_CLOUD_API_KEY, None)
    assert result == "token-mixed"


@pytest.mark.asyncio
async def test_resolve_headers_bearer_token(monkeypatch):
    # Test Bearer token extraction
    monkeypatch.setattr("stardog_cloud_mcp.server.get_http_headers", lambda: {"Authorization": "Bearer test-bearer-token"})
    result = await resolve_params(Headers.STARDOG_CLOUD_API_KEY, None)
    assert result == "test-bearer-token"


@pytest.mark.asyncio
async def test_resolve_headers_bearer_token_case_insensitive(monkeypatch):
    # Test Bearer token with different case
    monkeypatch.setattr("stardog_cloud_mcp.server.get_http_headers", lambda: {"authorization": "Bearer test-bearer-lower"})
    result = await resolve_params(Headers.STARDOG_CLOUD_API_KEY, None)
    assert result == "test-bearer-lower"
    
    # Test with AUTHORIZATION header
    monkeypatch.setattr("stardog_cloud_mcp.server.get_http_headers", lambda: {"AUTHORIZATION": "Bearer test-bearer-upper"})
    result = await resolve_params(Headers.STARDOG_CLOUD_API_KEY, None)
    assert result == "test-bearer-upper"


@pytest.mark.asyncio
async def test_resolve_headers_bearer_token_with_arg(monkeypatch):
    # Test Bearer token takes priority over command line argument
    monkeypatch.setattr("stardog_cloud_mcp.server.get_http_headers", lambda: {"Authorization": "Bearer bearer-token"})
    result = await resolve_params(Headers.STARDOG_CLOUD_API_KEY, "arg-token")
    assert result == "bearer-token"


@pytest.mark.asyncio
async def test_resolve_headers_priority_order(monkeypatch):
    # Test full priority order: custom header > bearer token > arg
    
    # All three present: custom header wins
    monkeypatch.setattr("stardog_cloud_mcp.server.get_http_headers", lambda: {
        "x-sdc-api-key": "custom-token",
        "Authorization": "Bearer bearer-token"
    })
    result = await resolve_params(Headers.STARDOG_CLOUD_API_KEY, "arg-token")
    assert result == "custom-token"
    
    # Only bearer and arg: bearer wins
    monkeypatch.setattr("stardog_cloud_mcp.server.get_http_headers", lambda: {
        "Authorization": "Bearer bearer-token"
    })
    result = await resolve_params(Headers.STARDOG_CLOUD_API_KEY, "arg-token")
    assert result == "bearer-token"
    
    # Only arg: arg is used
    monkeypatch.setattr("stardog_cloud_mcp.server.get_http_headers", lambda: {})
    result = await resolve_params(Headers.STARDOG_CLOUD_API_KEY, "arg-token")
    assert result == "arg-token"


@pytest.mark.asyncio
async def test_resolve_headers_invalid_bearer_format(monkeypatch):
    # Test that invalid Bearer format is ignored
    monkeypatch.setattr("stardog_cloud_mcp.server.get_http_headers", lambda: {"Authorization": "InvalidBearer token"})
    result = await resolve_params(Headers.STARDOG_CLOUD_API_KEY, None)
    assert result is None
    
    # Test Bearer without space
    monkeypatch.setattr("stardog_cloud_mcp.server.get_http_headers", lambda: {"Authorization": "Bearertoken"})
    result = await resolve_params(Headers.STARDOG_CLOUD_API_KEY, None)
    assert result is None
    
    # Test just "Bearer" without token
    monkeypatch.setattr("stardog_cloud_mcp.server.get_http_headers", lambda: {"Authorization": "Bearer"})
    result = await resolve_params(Headers.STARDOG_CLOUD_API_KEY, None)
    assert result is None


@patch('fastmcp.FastMCP.run')
def test_initialize_server_http_mode(mock_run):
    mock_run.return_value = None

    server = initialize_server(
        endpoint="http://test-endpoint",
        api_token="test-token",
        client_id="test-client",
        auth_token_override=None,
        port=8080,
        deployment_mode="launchpad"
    )

    mock_run.assert_called_once_with(transport="streamable-http", host="0.0.0.0", port=8080)
    assert server is not None


@patch('fastmcp.FastMCP.run')
@patch('fastmcp.settings')
def test_initialize_server_cloud_mode(mock_settings, mock_run):
    mock_run.return_value = None

    server = initialize_server(
        endpoint="http://test-endpoint",
        api_token="test-token",
        client_id="test-client",
        auth_token_override=None,
        port=8080,
        deployment_mode="cloud"
    )

    # Should not call run() in cloud mode, just return server
    mock_run.assert_not_called()
    # Should enable stateless HTTP for cloud mode
    assert mock_settings.stateless_http == True
    assert server is not None


@patch('fastmcp.FastMCP.run')
@patch('stardog_cloud_mcp.server.os.getenv')
def test_initialize_server_with_mcp_logging(mock_getenv, mock_run):
    mock_run.return_value = None
    # Mock environment variable to enable MCP logging
    mock_getenv.side_effect = lambda key, default=None: "true" if key == "SDC_MCP_LOGGING" else default

    with patch('stardog_cloud_mcp.server.LoggingMiddleware') as mock_middleware:
        server = initialize_server(
            endpoint="http://test-endpoint",
            api_token="test-token",
            client_id="test-client",
            auth_token_override=None,
            port=8080,
            deployment_mode="development"
        )

        # Should add logging middleware when SDC_MCP_LOGGING=true
        mock_middleware.assert_called_once()
        assert server is not None


@patch('fastmcp.FastMCP.run')
def test_initialize_server_development_mode(mock_run):
    mock_run.return_value = None

    server = initialize_server(
        endpoint="http://test-endpoint",
        api_token="test-token",
        client_id="test-client",
        auth_token_override=None,
        port=8080,
        deployment_mode="development"
    )

    mock_run.assert_called_once_with(transport="stdio")
    assert server is not None


@patch('fastmcp.FastMCP.run')
@patch('stardog_cloud_mcp.server.time.time', return_value=1234567890)
@pytest.mark.asyncio
async def test_health_check_endpoint(mock_time, mock_run):
    """Test the health check endpoint functionality"""
    from starlette.testclient import TestClient

    mock_run.return_value = None

    server = initialize_server(
        endpoint="http://test-endpoint",
        api_token="test-token",
        client_id="test-client",
        auth_token_override=None,
        port=8080,
        deployment_mode="cloud"
    )

    # Get the HTTP app from the server
    app = server.http_app()
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    json_response = response.json()

    assert json_response["status"] == "healthy"
    assert json_response["service"] == "stardog-cloud-mcp"
    assert json_response["timestamp"] == 1234567890
    assert json_response["deployment_mode"] == "cloud"
    assert json_response["transport"] == "asgi"


