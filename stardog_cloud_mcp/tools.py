import logging
from typing import Optional

from stardog.cloud.client import BaseClient
from stardog.cloud.voicebox import ThinkMode, VoiceboxAnswer, VoiceboxAppSettings

from stardog_cloud_mcp.exceptions import StardogMCPToolException

logger = logging.getLogger("stardog_cloud_mcp")


class ToolHandler:
    """
    Handler for MCP tools that interact with Stardog Cloud.
    """

    def __init__(self, cloud_client: BaseClient):
        """
        Initialize the tool handler.

        Args:
            cloud_client: The Stardog Cloud client
        """
        self.cloud_client = cloud_client

    async def handle_voicebox_settings(
        self, api_token: str, client_id: str | None
    ) -> str:
        """
        Handle the voicebox_settings tool.
        Args:
            api_token: The Voicebox app API token
            client_id: The client ID (optional)
        Returns:
            A string representation of the Voicebox settings
        """
        try:
            voicebox_app = self.cloud_client.voicebox_app(
                app_api_token=api_token, client_id=client_id
            )
            voicebox_settings: VoiceboxAppSettings = await voicebox_app.async_settings()
        except Exception as e:
            logger.error(f"Error occurred while fetching Voicebox settings: {e}")
            raise StardogMCPToolException(
                tool_name="voicebox_settings", message=str(e)
            ) from e

        return str(voicebox_settings)

    async def handle_voicebox_ask(
        self,
        api_token: str,
        client_id: Optional[str],
        question: str,
        conversation_id: Optional[str] = None,
        stardog_auth_token_override: Optional[str] = None,
    ) -> str:
        """
        Handle the voicebox_ask tool.

        Args:
            api_token: The Voicebox app API token
            client_id: The client ID (optional)
            question: The question to ask
            conversation_id: The conversation ID (optional)
            stardog_auth_token_override: Token override (optional)
        Returns:
            A string representation of the Voicebox answer
        """
        try:
            if not question:
                raise ValueError("A valid question is required to execute the tool")

            voicebox_app = self.cloud_client.voicebox_app(
                app_api_token=api_token, client_id=client_id
            )

            answer: VoiceboxAnswer = await voicebox_app.async_ask(
                question=question,
                conversation_id=conversation_id,
                client_id=client_id,
                stardog_auth_token_override=stardog_auth_token_override,
            )
        except Exception as e:
            logger.error(f"Error occurred while asking question: {e}")
            raise StardogMCPToolException(
                tool_name="voicebox_ask", message=str(e)
            ) from e

        return str(answer)

    async def handle_voicebox_generate_query(
        self,
        api_token: str,
        client_id: Optional[str],
        question: str,
        conversation_id: Optional[str] = None,
        stardog_auth_token_override: Optional[str] = None,
    ) -> str:
        """
        Handle the voicebox_generate_query tool.

        Args:
            api_token: The Voicebox app API token
            client_id: The client ID (optional)
            question: The question to generate a query for
            conversation_id: The conversation ID (optional)
            stardog_auth_token_override: Token override (optional)
        Returns:
            A string representation of the generated SPARQL query
        """
        try:
            if not question:
                raise ValueError("A valid question is required to execute the tool")

            voicebox_app = self.cloud_client.voicebox_app(
                app_api_token=api_token, client_id=client_id
            )
            response: VoiceboxAnswer = await voicebox_app.async_generate_query(
                question=question,
                conversation_id=conversation_id,
                client_id=client_id,
                stardog_auth_token_override=stardog_auth_token_override,
            )
        except Exception as e:
            logger.error(f"Error occurred while generating SPARQL query: {e}")
            raise StardogMCPToolException(
                tool_name="voicebox_generate_query", message=str(e)
            ) from e
        return str(response)

    async def handle_voicebox_stream_ask(
        self,
        api_token: str,
        client_id: Optional[str],
        question: str,
        conversation_id: Optional[str] = None,
        stardog_auth_token_override: Optional[str] = None,
        think_mode: ThinkMode = "standard",
    ) -> str:
        """
        Handle the voicebox_stream_ask tool using the streaming API.

        Args:
            api_token: The Voicebox app API token
            client_id: The client ID (optional)
            question: The question to ask
            conversation_id: The conversation ID (optional)
            stardog_auth_token_override: Token override (optional)
            think_mode: Think mode - 'standard', 'lite', or 'fast' (default: 'standard')
        Returns:
            A string representation of the final Voicebox answer
        """
        try:
            if not question:
                raise ValueError("A valid question is required to execute the tool")

            voicebox_app = self.cloud_client.voicebox_app(
                app_api_token=api_token, client_id=client_id
            )
            final_answer = None
            async with voicebox_app.async_stream_ask(
                question=question,
                conversation_id=conversation_id,
                client_id=client_id,
                stardog_auth_token_override=stardog_auth_token_override,
                think_mode=think_mode,
            ) as stream:
                async for answer in stream:
                    if not answer.pending:
                        final_answer = answer
            if final_answer is None:
                raise RuntimeError("Stream ended without a final answer")
        except Exception as e:
            logger.error(f"Error during streaming ask: {e}")
            raise StardogMCPToolException(
                tool_name="voicebox_stream_ask", message=str(e)
            ) from e

        return str(final_answer)
