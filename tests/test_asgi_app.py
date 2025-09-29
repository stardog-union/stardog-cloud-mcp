import os
from unittest.mock import patch, Mock

from stardog_cloud_mcp.asgi_app import create_asgi_app


@patch('stardog_cloud_mcp.asgi_app.initialize_server')
def test_create_asgi_app(mock_initialize_server):
    """Test ASGI app creation with default configuration"""
    mock_server = Mock()
    mock_server.http_app.return_value = "mock_asgi_app"
    mock_initialize_server.return_value = mock_server

    with patch.dict(os.environ, {}, clear=True):
        result = create_asgi_app()

        mock_initialize_server.assert_called_once_with(
            endpoint="https://cloud.stardog.com/api",
            api_token=None,
            client_id="VBX-APP",
            auth_token_override="",
            port=7000,
            deployment_mode="cloud"
        )
        assert result == "mock_asgi_app"


def test_app_instance_creation():
    """Test that the app instance is created when the module is imported"""
    import stardog_cloud_mcp.asgi_app

    # The app should exist as a module-level variable
    assert hasattr(stardog_cloud_mcp.asgi_app, 'app')
    assert stardog_cloud_mcp.asgi_app.app is not None