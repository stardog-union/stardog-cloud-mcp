# Deployment configuration for Stardog Cloud MCP server

deployment_configs = {
    "development": {
        "transport": "stdio",
        "auth_enabled": False,
        "log_level": "DEBUG",
        "workers": 1,
    },
    "launchpad": {
        "transport": "streamable-http",
        "auth_enabled": False,
        "log_level": "INFO",
        "workers": 1,
    },
    "cloud": {
        "transport": "asgi",
        "auth_enabled": True,
        "log_level": "INFO",
        "workers": 4,
    },
}
