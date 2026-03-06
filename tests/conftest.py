import pytest
from contextlib import asynccontextmanager
from unittest.mock import MagicMock, AsyncMock

from stardog_cloud_mcp.tools import ToolHandler


async def _async_iter(items):
    for item in items:
        yield item


@pytest.fixture
def tool_handler():
    mock_voicebox_app = MagicMock()
    mock_voicebox_app.async_settings = AsyncMock(return_value=MagicMock(
        name="test-vbx-app-1",
        database="flight-db-2",
        model="flight_plan",
        named_graphs=["tag:stardog:api:context:local"],
        reasoning=True
    ))
    mock_voicebox_app.async_ask = AsyncMock(return_value=MagicMock(
        content="Test answer",
        interpreted_question="What is the flight plan?",
        sparql_query="SELECT * WHERE { ?s ?p ?o }",
        conversation_id="conv-1",
        message_id="msg-1"
    ))
    mock_voicebox_app.async_generate_query = AsyncMock(return_value=MagicMock(
        interpreted_question="Show me all flights",
        sparql_query="SELECT * WHERE { ?flight ?hasPlan ?plan }",
        conversation_id="conv-2",
        message_id="msg-2"
    ))

    mock_intermediate = MagicMock(
        content="", pending=True, conversation_id="conv-1", message_id="msg-int"
    )
    mock_final = MagicMock(
        content="Final answer", pending=False,
        conversation_id="conv-1", message_id="msg-final",
        interpreted_question="Rewritten question",
        sparql_query="SELECT * WHERE { ?s ?p ?o }",
    )
    mock_final.__str__ = lambda self: "Final answer"

    @asynccontextmanager
    async def mock_async_stream_ask(**kwargs):
        yield _async_iter([mock_intermediate, mock_final])

    mock_voicebox_app.async_stream_ask = mock_async_stream_ask

    mock_client = MagicMock()
    mock_client.voicebox_app.return_value = mock_voicebox_app
    return ToolHandler(mock_client)
