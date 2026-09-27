"""Guard for the /health auth bypass (B7).

FastMCP wraps only the MCP route in RequireAuthMiddleware; custom routes
sit outside it. One app instance pins both sides of that boundary, so a
framework change that moves either side fails here.
"""

import pytest
from starlette.testclient import TestClient

from config import ServerConfig
from server import create_server

pytestmark = pytest.mark.integration


def test_health_bypasses_auth_while_mcp_requires_it():
    config = ServerConfig.from_env(
        {"MCP_TRANSPORT": "http", "MCP_API_KEY_LAPTOP": "test-token-laptop"}
    )
    app = create_server(config).http_app(json_response=True)
    with TestClient(app) as client:
        assert client.post("/mcp", json={}).status_code == 401
        response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
