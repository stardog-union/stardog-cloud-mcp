import pytest


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
    with pytest.raises(ValueError, match="A valid question is required to execute the tool"):
        await tool_handler.handle_voicebox_ask("dummy-token", "test-client", None)


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
    with pytest.raises(ValueError, match="A valid question is required to execute the tool"):
        await tool_handler.handle_voicebox_generate_query("dummy-token", "test-client", None)
