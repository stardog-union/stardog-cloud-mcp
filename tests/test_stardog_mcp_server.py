import pytest
from fastmcp import FastMCP, Client, Context
from unittest.mock import MagicMock, AsyncMock

@pytest.fixture
def mcp_server():
    # Setup mock client as in conftest
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
    # Start the server with the mock client
    server = FastMCP("stardog-cloud-mcp-test")
    # Register tools as in server.py
    @server.tool(name="voicebox_settings")
    async def voicebox_settings(ctx: Context) -> str:
        app = mock_client.voicebox_app("dummy-token", "test-client")
        settings = await app.async_settings()
        return f"Voicebox App Settings:\nName: {settings.name}\nDatabase: {settings.database}"
    @server.tool(name="voicebox_ask")
    async def voicebox_ask(ctx: Context, question: str) -> str:
        app = mock_client.voicebox_app("dummy-token", "test-client")
        answer = await app.async_ask(question=question)
        return f"Answer: {answer.content}\nInterpreted: {answer.interpreted_question}"
    @server.tool(name="voicebox_generate_query")
    async def voicebox_generate_query(ctx: Context, question: str) -> str:
        app = mock_client.voicebox_app("dummy-token", "test-client")
        result = await app.async_generate_query(question=question)
        return f"SPARQL: {result.sparql_query}\nInterpreted: {result.interpreted_question}"
    return server

@pytest.mark.asyncio
async def test_in_memory_voicebox_settings(mcp_server):
    async with Client(mcp_server) as client:
        result = await client.call_tool("voicebox_settings", {})
        assert "Voicebox App Settings" in result.data
        assert "test-vbx-app-1" in result.data

@pytest.mark.asyncio
async def test_in_memory_voicebox_ask(mcp_server):
    async with Client(mcp_server) as client:
        result = await client.call_tool("voicebox_ask", {"question": "What is the flight plan?"})
        assert "Answer" in result.data
        assert "flight plan" in result.data

@pytest.mark.asyncio
async def test_in_memory_voicebox_generate_query(mcp_server):
    async with Client(mcp_server) as client:
        result = await client.call_tool("voicebox_generate_query", {"question": "Show me all flights"})
        assert "SPARQL" in result.data or "SELECT" in result.data
        assert "Show me all flights" in result.data
