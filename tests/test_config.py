import dataclasses

import pytest

from config import ServerConfig


def test_empty_env_defaults_to_stdio():
    config = ServerConfig.from_env({})
    assert config == ServerConfig(transport="stdio", host=None, port=None)


def test_http_transport_gets_defaults():
    config = ServerConfig.from_env({"MCP_TRANSPORT": "streamable-http"})
    assert config == ServerConfig(
        transport="streamable-http", host="127.0.0.1", port=8000
    )


def test_explicit_stdio_stays_stdio():
    config = ServerConfig.from_env({"MCP_TRANSPORT": "stdio"})
    assert config == ServerConfig(transport="stdio", host=None, port=None)


def test_unknown_transport_raises():
    with pytest.raises(ValueError, match="garbage") as excinfo:
        ServerConfig.from_env({"MCP_TRANSPORT": "garbage"})
    assert "stdio" in str(excinfo.value)
    assert "streamable-http" in str(excinfo.value)


def test_http_host_and_port_resolve_through():
    config = ServerConfig.from_env(
        {
            "MCP_TRANSPORT": "streamable-http",
            "MCP_HOST": "192.168.1.50",
            "MCP_PORT": "9000",
        }
    )
    assert config == ServerConfig(
        transport="streamable-http", host="192.168.1.50", port=9000
    )


def test_http_non_integer_port_raises():
    with pytest.raises(ValueError, match="MCP_PORT"):
        ServerConfig.from_env({"MCP_TRANSPORT": "streamable-http", "MCP_PORT": "abc"})


@pytest.mark.parametrize("port", ["70000", "0"])
def test_http_out_of_range_port_raises(port):
    with pytest.raises(ValueError, match="1-65535"):
        ServerConfig.from_env({"MCP_TRANSPORT": "streamable-http", "MCP_PORT": port})


def test_http_default_host_is_fail_closed():
    config = ServerConfig.from_env({"MCP_TRANSPORT": "streamable-http"})
    assert config.host == "127.0.0.1"
    assert config.host != "0.0.0.0"  # noqa: S104 — asserting the *absence* of bind-all


def test_empty_transport_raises():
    # Present-but-empty is invalid, not "unset" — value-authoritative.
    with pytest.raises(ValueError, match="MCP_TRANSPORT"):
        ServerConfig.from_env({"MCP_TRANSPORT": ""})


def test_stdio_ignores_host_and_port():
    config = ServerConfig.from_env(
        {"MCP_TRANSPORT": "stdio", "MCP_HOST": "10.0.0.5", "MCP_PORT": "9000"}
    )
    assert config == ServerConfig(transport="stdio", host=None, port=None)


def test_stdio_ignores_malformed_port():
    # Contract lock: port validation is branch-scoped to streamable-http.
    # stdio never inspects MCP_PORT, so a malformed value must not raise.
    config = ServerConfig.from_env({"MCP_TRANSPORT": "stdio", "MCP_PORT": "abc"})
    assert config == ServerConfig(transport="stdio", host=None, port=None)


def test_config_is_frozen():
    config = ServerConfig.from_env({})
    with pytest.raises(dataclasses.FrozenInstanceError):
        config.transport = "streamable-http"
