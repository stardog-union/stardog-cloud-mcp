import pytest
from contextlib import asynccontextmanager
from unittest.mock import MagicMock, AsyncMock

from stardog_cloud_mcp.exceptions import StardogMCPToolException
from stardog_cloud_mcp.tools import ToolHandler

from conftest import _async_iter


@pytest.mark.asyncio
async def test_handle_voicebox_settings(tool_handler):
    result = await tool_handler.handle_voicebox_settings(
        api_token="dummy-token",
        client_id="test-client"
    )
    assert "Voicebox App Settings" in result or "test-vbx-app-1" in result
    mock_voicebox_app = tool_handler.cloud_client.voicebox_app("dummy-token", "test-client")
    mock_voicebox_app.async_settings.assert_awaited()


@pytest.mark.asyncio
async def test_handle_voicebox_ask(tool_handler):
    result = await tool_handler.handle_voicebox_ask(
        api_token="dummy-token",
        client_id="test-client",
        question="What is the flight plan?",
        conversation_id=None,
        stardog_auth_token_override=None
    )
    assert result is not None
    mock_voicebox_app = tool_handler.cloud_client.voicebox_app("dummy-token", "test-client")
    mock_voicebox_app.async_ask.assert_awaited()


@pytest.mark.asyncio
async def test_handle_voicebox_ask_missing_question(tool_handler):
    with pytest.raises(StardogMCPToolException, match="A valid question is required to execute the tool") as exc_info:
        await tool_handler.handle_voicebox_ask("dummy-token", "test-client", None)
    assert exc_info.value.name == "voicebox_ask"


@pytest.mark.asyncio
async def test_handle_voicebox_generate_query(tool_handler):
    result = await tool_handler.handle_voicebox_generate_query(
        api_token="dummy-token",
        client_id="test-client",
        question="Show me all flights",
        conversation_id=None,
        stardog_auth_token_override=None
    )
    assert result is not None
    mock_voicebox_app = tool_handler.cloud_client.voicebox_app("dummy-token", "test-client")
    mock_voicebox_app.async_generate_query.assert_awaited()


@pytest.mark.asyncio
async def test_handle_voicebox_generate_query_missing_question(tool_handler):
    with pytest.raises(StardogMCPToolException, match="A valid question is required to execute the tool") as exc_info:
        await tool_handler.handle_voicebox_generate_query("dummy-token", "test-client", None)
    assert exc_info.value.name == "voicebox_generate_query"


@pytest.mark.asyncio
async def test_handle_voicebox_settings_exception():
    mock_client = MagicMock()
    mock_voicebox_app = MagicMock()
    mock_voicebox_app.async_settings = AsyncMock(side_effect=Exception("Connection failed"))
    mock_client.voicebox_app.return_value = mock_voicebox_app
    
    handler = ToolHandler(mock_client)
    
    with pytest.raises(StardogMCPToolException) as exc_info:
        await handler.handle_voicebox_settings("dummy-token", "test-client")
    
    assert exc_info.value.name == "voicebox_settings"
    assert "Connection failed" in str(exc_info.value)


@pytest.mark.asyncio
async def test_handle_voicebox_ask_exception():
    mock_client = MagicMock()
    mock_voicebox_app = MagicMock()
    mock_voicebox_app.async_ask = AsyncMock(side_effect=RuntimeError("API error"))
    mock_client.voicebox_app.return_value = mock_voicebox_app
    
    handler = ToolHandler(mock_client)
    
    with pytest.raises(StardogMCPToolException) as exc_info:
        await handler.handle_voicebox_ask(
            "dummy-token", "test-client", "What is the flight plan?", None, None
        )
    
    assert exc_info.value.name == "voicebox_ask"
    assert "API error" in str(exc_info.value)


@pytest.mark.asyncio
async def test_handle_voicebox_generate_query_exception():
    mock_client = MagicMock()
    mock_voicebox_app = MagicMock()
    mock_voicebox_app.async_generate_query = AsyncMock(
        side_effect=ValueError("Invalid query format")
    )
    mock_client.voicebox_app.return_value = mock_voicebox_app
    
    handler = ToolHandler(mock_client)
    
    with pytest.raises(StardogMCPToolException) as exc_info:
        await handler.handle_voicebox_generate_query(
            "dummy-token", "test-client", "What is the flight plan?", None, None
        )
    
    assert exc_info.value.name == "voicebox_generate_query"
    assert "Invalid query format" in str(exc_info.value)


@pytest.mark.asyncio
async def test_handle_voicebox_stream_ask(tool_handler):
    result = await tool_handler.handle_voicebox_stream_ask(
        api_token="dummy-token",
        client_id="test-client",
        question="What is the flight plan?",
        think_mode="standard",
    )
    assert result is not None
    assert "Final answer" in result


@pytest.mark.asyncio
async def test_handle_voicebox_stream_ask_missing_question(tool_handler):
    with pytest.raises(StardogMCPToolException, match="A valid question is required to execute the tool") as exc_info:
        await tool_handler.handle_voicebox_stream_ask(
            "dummy-token", "test-client", None
        )
    assert exc_info.value.name == "voicebox_stream_ask"


@pytest.mark.asyncio
async def test_handle_voicebox_stream_ask_exception():
    mock_client = MagicMock()
    mock_voicebox_app = MagicMock()

    @asynccontextmanager
    async def failing_stream_ask(**kwargs):
        raise RuntimeError("API error")
        yield  # pragma: no cover

    mock_voicebox_app.async_stream_ask = failing_stream_ask
    mock_client.voicebox_app.return_value = mock_voicebox_app

    handler = ToolHandler(mock_client)

    with pytest.raises(StardogMCPToolException) as exc_info:
        await handler.handle_voicebox_stream_ask(
            "dummy-token", "test-client", "What is the flight plan?", None, None, "standard"
        )

    assert exc_info.value.name == "voicebox_stream_ask"
    assert "API error" in str(exc_info.value)


@pytest.mark.asyncio
async def test_handle_voicebox_stream_ask_no_final_answer():
    mock_client = MagicMock()
    mock_voicebox_app = MagicMock()

    mock_pending_only = MagicMock(
        content="", pending=True, conversation_id="conv-1", message_id="msg-int"
    )

    @asynccontextmanager
    async def pending_only_stream(**kwargs):
        yield _async_iter([mock_pending_only])

    mock_voicebox_app.async_stream_ask = pending_only_stream
    mock_client.voicebox_app.return_value = mock_voicebox_app

    handler = ToolHandler(mock_client)

    with pytest.raises(StardogMCPToolException) as exc_info:
        await handler.handle_voicebox_stream_ask(
            "dummy-token", "test-client", "What is the flight plan?", None, None, "standard"
        )

    assert exc_info.value.name == "voicebox_stream_ask"
    assert "Stream ended without a final answer" in str(exc_info.value)
