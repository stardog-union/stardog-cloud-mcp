# Deployment configuration for Stardog Cloud MCP server

deployment_configs = {
    "development": {
        "transport": "stdio",
        "log_level": "DEBUG",
        "workers": 1,
    },
    "launchpad": {
        "transport": "streamable-http",
        "log_level": "INFO",
        "workers": 1,
    },
    "cloud": {
        "transport": "asgi",
        "log_level": "INFO",
        "workers": 4,
    },
}
