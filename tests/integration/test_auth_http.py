"""HTTP auth suite: the real ASGI app from create_server, driven in process.

FastMCP's in-memory Client bypasses HTTP, so it never meets
RequireAuthMiddleware; these tests send real HTTP requests to the
Starlette app through TestClient instead. json_response=True makes
initialize answer with one JSON body instead of an SSE stream: it
changes response framing only, not auth.
"""

import pytest
from mcp.types import LATEST_PROTOCOL_VERSION
from starlette.testclient import TestClient

from config import ServerConfig
from server import create_server

pytestmark = pytest.mark.integration

MCP_PATH = "/mcp"  # FastMCP's default streamable_http_path
TOKENS = {"DESKTOP": "test-token-desktop", "LAPTOP": "test-token-laptop"}
INITIALIZE = {
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
        "protocolVersion": LATEST_PROTOCOL_VERSION,
        "capabilities": {},
        "clientInfo": {"name": "test-auth-http", "version": "0"},
    },
}


def _test_client(tokens: dict[str, str]) -> TestClient:
    env = {"MCP_TRANSPORT": "http"}
    env.update({f"MCP_API_KEY_{device}": token for device, token in tokens.items()})
    app = create_server(ServerConfig.from_env(env)).http_app(json_response=True)
    return TestClient(app)


def _initialize(client: TestClient, token: str | None = None):
    headers = {"Accept": "application/json, text/event-stream"}
    if token is not None:
        headers["Authorization"] = f"Bearer {token}"
    return client.post(MCP_PATH, json=INITIALIZE, headers=headers)


@pytest.fixture
def client():
    # Used as a context manager so the app lifespan runs: it starts the
    # streamable-HTTP session manager that /mcp needs.
    with _test_client(TOKENS) as test_client:
        yield test_client


def test_missing_header_returns_401_with_challenge(client):
    response = _initialize(client)
    assert response.status_code == 401
    assert "WWW-Authenticate" in response.headers


def test_wrong_token_returns_401(client):
    assert _initialize(client, "test-token-wrong").status_code == 401


@pytest.mark.parametrize("device", sorted(TOKENS))
def test_each_device_token_completes_initialize(client, device):
    response = _initialize(client, TOKENS[device])
    assert response.status_code == 200
    assert response.json()["result"]["serverInfo"]["name"] == "Paprika"


def test_revoked_device_token_returns_401():
    # Revocation is config-driven: resolve without LAPTOP's key, rebuild.
    with _test_client({"DESKTOP": TOKENS["DESKTOP"]}) as client:
        assert _initialize(client, TOKENS["LAPTOP"]).status_code == 401
        assert _initialize(client, TOKENS["DESKTOP"]).status_code == 200
