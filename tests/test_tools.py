import pytest
from tools import ToolHandler


@pytest.mark.asyncio
async def test_handle_voicebox_settings(handler):
    result = await handler.handle_voicebox_settings(
        api_token="dummy-token",
        client_id="test-client"
    )
    assert "Voicebox App Settings" in result or "test-vbx-app-1" in result
    mock_voicebox_app = handler.cloud_client.voicebox_app("dummy-token", "test-client")
    mock_voicebox_app.async_settings.assert_awaited()


@pytest.mark.asyncio
async def test_handle_voicebox_settings_missing_token():
    from unittest.mock import MagicMock, AsyncMock
    mock_voicebox_app = MagicMock()
    mock_voicebox_app.async_settings = AsyncMock()
    mock_client = MagicMock()
    mock_client.voicebox_app.return_value = mock_voicebox_app
    handler = ToolHandler(mock_client)
    with pytest.raises(ValueError, match="app_api_token is required"):
        await handler.handle_voicebox_settings(None, "test-client")


@pytest.mark.asyncio
async def test_handle_voicebox_ask(handler):
    result = await handler.handle_voicebox_ask(
        api_token="dummy-token",
        client_id="test-client",
        question="What is the flight plan?",
        conversation_id=None,
        stardog_auth_token_override=None
    )
    assert result is not None
    mock_voicebox_app = handler.cloud_client.voicebox_app("dummy-token", "test-client")
    mock_voicebox_app.async_ask.assert_awaited()


@pytest.mark.asyncio
async def test_handle_voicebox_ask_missing_question(handler):
    with pytest.raises(ValueError, match="question is required"):
        await handler.handle_voicebox_ask("dummy-token", "test-client", None)


@pytest.mark.asyncio
async def test_handle_voicebox_generate_query(handler):
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
async def test_handle_voicebox_generate_query_missing_question(handler):
    with pytest.raises(ValueError, match="question is required"):
        await handler.handle_voicebox_generate_query("dummy-token", "test-client", None)
