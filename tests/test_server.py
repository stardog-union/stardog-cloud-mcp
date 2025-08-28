from unittest.mock import patch, AsyncMock

import pytest
from fastmcp import Client

from server import initialize_server


@pytest.fixture
def mcp_server():
    with patch('server.StardogAsyncClient') as mock_stardog_client, \
         patch('server.ToolHandler') as mock_tool_handler, \
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
            mode="stdio",
            port=7000
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
    async def raise_value_error():
        raise ValueError("API token is required")
    monkeypatch.setattr("server.get_api_token", raise_value_error)
    mock_run.return_value = None
    server_instance = initialize_server(
        endpoint="dummy-endpoint",
        api_token="",
        client_id="test-client",
        mode="stdio",
        port=7000
    )
    async with Client(server_instance) as client:
        with pytest.raises(Exception):
            await client.call_tool("voicebox_settings", {})

@patch('fastmcp.FastMCP.run')
@patch('server.ToolHandler')
@pytest.mark.asyncio
async def test_voicebox_settings_with_header(mock_tool_handler, mock_run, monkeypatch):
    monkeypatch.setattr("server.get_http_headers", lambda: {"x-sdc-api-key": "header-token"})
    mock_run.return_value = None
    mock_handler_instance = mock_tool_handler.return_value
    mock_handler_instance.handle_voicebox_settings = AsyncMock(return_value="Voicebox App Settings: test-vbx-app-1")
    server_instance = initialize_server(
        endpoint="dummy-endpoint",
        api_token="arg-token",
        client_id="test-client",
        mode="stdio",
        port=7000
    )
    async with Client(server_instance) as client:
        result = await client.call_tool("voicebox_settings", {})
        assert "Voicebox App Settings" in result.data

@pytest.mark.asyncio
@patch('server.get_context', return_value=None)
async def test_get_client_id_header_only(mock_get_context, monkeypatch):
    from server import get_client_id
    monkeypatch.setattr("server.get_http_headers", lambda: {"x-sdc-client-id": "header-client"})
    result = await get_client_id("arg-client")
    assert result == "header-client"

@pytest.mark.asyncio
@patch('server.get_context', return_value=None)
async def test_get_client_id_arg_only(monkeypatch):
    from server import get_client_id
    monkeypatch.setattr("server.get_http_headers", lambda: None)
    result = await get_client_id("arg-client")
    assert result == "arg-client"

@pytest.mark.asyncio
@patch('server.get_context', return_value=None)
async def test_get_client_id_none(monkeypatch):
    from server import get_client_id
    monkeypatch.setattr("server.get_http_headers", lambda: None)
    result = await get_client_id(None)
    assert result is None

# CLI entrypoint coverage
@patch('server.initialize_server', return_value=None)
def test_main_entrypoint(mock_init):
    import subprocess, sys, os
    script_path = os.path.join(os.path.dirname(__file__), '../src/server.py')
    result = subprocess.run([
        sys.executable, script_path,
        '--endpoint', 'dummy-endpoint',
        '--token', 'dummy-token',
        '--client_id', 'test-client',
        '--mode', 'stdio',
        '--port', '7000'
    ], capture_output=True, text=True)
    # Assert successful exit
    assert result.returncode == 0