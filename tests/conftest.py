import pytest
from unittest.mock import MagicMock, AsyncMock

from tools import ToolHandler


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
    mock_client = MagicMock()
    mock_client.voicebox_app.return_value = mock_voicebox_app
    return ToolHandler(mock_client)
