class StardogMCPToolException(Exception):
    """
    Exception for tool-related errors.
    """

    def __init__(self, tool_name: str, message: str):
        self.name = tool_name
        error_message = f"Error executing tool: {tool_name} - {message}"
        super().__init__(error_message)
