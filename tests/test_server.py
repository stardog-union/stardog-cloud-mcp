import pytest
from unittest.mock import patch, MagicMock
import server


@pytest.mark.asyncio
async def test_voicebox_settings(handler):
    result = await handler.handle_voicebox_settings(
        api_token="dummy-token",
        client_id="test-client"
    )
    assert "test-vbx-app-1" in result
    mock_voicebox_app = handler.cloud_client.voicebox_app("dummy-token", "test-client")
    mock_voicebox_app.async_settings.assert_awaited()


@pytest.mark.asyncio
async def test_voicebox_ask(handler):
    result = await handler.handle_voicebox_ask(
        api_token="dummy-token",
        client_id="test-client",
        question="What is the flight plan?",
        conversation_id=None,
        stardog_auth_token_override=None
    )
    # The mock returns a MagicMock, so check the content attribute
    assert result is not None
    mock_voicebox_app = handler.cloud_client.voicebox_app("dummy-token", "test-client")
    mock_voicebox_app.async_ask.assert_awaited()


@pytest.mark.asyncio
async def test_voicebox_generate_query(handler):
    result = await handler.handle_voicebox_generate_query(
        api_token="dummy-token",
        client_id="test-client",
        question="Show me all flights",
        conversation_id=None,
        stardog_auth_token_override=None
    )
    assert result is not None
    mock_voicebox_app = handler.cloud_client.voicebox_app("dummy-token", "test-client")
    mock_voicebox_app.async_generate_query.assert_awaited()


@pytest.mark.asyncio
@patch('server.get_http_headers')
@patch('server.get_context', return_value=None)
async def test_get_api_token_header_only(mock_get_context, mock_get_headers):
    mock_get_headers.return_value = {'x-sdc-api-key': 'header-token'}
    token = await server.get_api_token(None)
    assert token == 'header-token'


@pytest.mark.asyncio
@patch('server.get_http_headers')
@patch('server.get_context', return_value=None)
async def test_get_api_token_arg_only(mock_get_context, mock_get_headers):
    mock_get_headers.return_value = None
    token = await server.get_api_token('arg-token')
    assert token == 'arg-token'


@pytest.mark.asyncio
@patch('server.get_http_headers')
@patch('server.get_context', return_value=None)
async def test_get_api_token_both(mock_get_context, mock_get_headers):
    mock_get_headers.return_value = {'x-sdc-api-key': 'header-token'}
    token = await server.get_api_token('arg-token')
    assert token == 'header-token'


@pytest.mark.asyncio
@patch('server.get_http_headers')
@patch('server.get_context', return_value=None)
async def test_get_api_token_none(mock_get_context, mock_get_headers):
    mock_get_headers.return_value = None
    with pytest.raises(ValueError):
        await server.get_api_token(None)


@pytest.mark.asyncio
@patch('server.get_http_headers')
@patch('server.get_context', return_value=None)
async def test_get_client_id_header_only(mock_get_context, mock_get_headers):
    mock_get_headers.return_value = {'x-sdc-client-id': 'header-client'}
    client_id = await server.get_client_id(None)
    assert client_id == 'header-client'


@pytest.mark.asyncio
@patch('server.get_http_headers')
@patch('server.get_context', return_value=None)
async def test_get_client_id_arg_only(mock_get_context, mock_get_headers):
    mock_get_headers.return_value = None
    client_id = await server.get_client_id('arg-client')
    assert client_id == 'arg-client'


@pytest.mark.asyncio
@patch('server.get_http_headers')
@patch('server.get_context', return_value=None)
async def test_get_client_id_both(mock_get_context, mock_get_headers):
    mock_get_headers.return_value = {'x-sdc-client-id': 'header-client'}
    client_id = await server.get_client_id('arg-client')
    assert client_id == 'header-client'


@pytest.mark.asyncio
@patch('server.get_http_headers')
@patch('server.get_context', return_value=None)
async def test_get_client_id_none(mock_get_context, mock_get_headers):
    mock_get_headers.return_value = None
    client_id = await server.get_client_id(None)
    assert client_id is None


@patch('server.FastMCP')
@patch('server.StardogAsyncClient')
@patch('server.ToolHandler')
def test_initialize_server(mock_tool_handler, mock_stardog_client, mock_fastmcp):
    mock_server = MagicMock()
    mock_fastmcp.return_value = mock_server
    mock_stardog_client.return_value = MagicMock()
    mock_tool_handler.return_value = MagicMock()
    server.initialize_server('endpoint', 'token', 'client_id', 'stdio', 7000)
    mock_fastmcp.assert_called_once_with('stardog-cloud-mcp')
    mock_stardog_client.assert_called_once_with(base_url='endpoint')
    mock_tool_handler.assert_called_once()
