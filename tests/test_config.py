import dataclasses

import pytest

from config import DeviceKey, ServerConfig

# Every http-mode test carries one valid key, so each negative test is
# otherwise valid and no test encodes the validation order (host, port, keys).
DEVICE = "LAPTOP"
TOKEN = "test-token-laptop"
KEY_ENV = {f"MCP_API_KEY_{DEVICE}": TOKEN}
KEYS = (DeviceKey(device=DEVICE, token=TOKEN),)


def test_empty_env_defaults_to_stdio():
    config = ServerConfig.from_env({})
    assert config == ServerConfig(transport="stdio", host=None, port=None)


def test_http_transport_gets_defaults():
    config = ServerConfig.from_env({"MCP_TRANSPORT": "http", **KEY_ENV})
    assert config == ServerConfig(
        transport="http", host="127.0.0.1", port=8000, api_keys=KEYS
    )


def test_explicit_stdio_stays_stdio():
    config = ServerConfig.from_env({"MCP_TRANSPORT": "stdio"})
    assert config == ServerConfig(transport="stdio", host=None, port=None)


def test_unknown_transport_raises():
    with pytest.raises(ValueError, match="garbage") as excinfo:
        ServerConfig.from_env({"MCP_TRANSPORT": "garbage"})
    assert "stdio" in str(excinfo.value)
    assert "http" in str(excinfo.value)


def test_http_host_and_port_resolve_through():
    config = ServerConfig.from_env(
        {
            "MCP_TRANSPORT": "http",
            "MCP_HOST": "192.168.1.50",
            "MCP_PORT": "9000",
            **KEY_ENV,
        }
    )
    assert config == ServerConfig(
        transport="http", host="192.168.1.50", port=9000, api_keys=KEYS
    )


def test_http_non_integer_port_raises():
    with pytest.raises(ValueError, match="MCP_PORT"):
        ServerConfig.from_env({"MCP_TRANSPORT": "http", "MCP_PORT": "abc", **KEY_ENV})


@pytest.mark.parametrize("port", ["70000", "0"])
def test_http_out_of_range_port_raises(port):
    with pytest.raises(ValueError, match="1-65535"):
        ServerConfig.from_env({"MCP_TRANSPORT": "http", "MCP_PORT": port, **KEY_ENV})


def test_http_default_host_is_fail_closed():
    config = ServerConfig.from_env({"MCP_TRANSPORT": "http", **KEY_ENV})
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
    # Contract lock: port validation is branch-scoped to http.
    # stdio never inspects MCP_PORT, so a malformed value must not raise.
    config = ServerConfig.from_env({"MCP_TRANSPORT": "stdio", "MCP_PORT": "abc"})
    assert config == ServerConfig(transport="stdio", host=None, port=None)


def test_config_is_frozen():
    config = ServerConfig.from_env({})
    with pytest.raises(dataclasses.FrozenInstanceError):
        config.transport = "http"


def test_streamable_http_alias_rejected():
    # Deliberate: FastMCP accepts "streamable-http" as a v2-era synonym for
    # "http", but our env contract has exactly one spelling per meaning.
    with pytest.raises(ValueError, match="streamable-http"):
        ServerConfig.from_env({"MCP_TRANSPORT": "streamable-http"})


# --- Per-device API keys (Piece 3a) ---


def test_stdio_ignores_api_keys():
    # Contract lock: keys are branch-scoped to http. stdio never inspects
    # them, so even a malformed key must not raise.
    config = ServerConfig.from_env(
        {"MCP_TRANSPORT": "stdio", **KEY_ENV, "MCP_API_KEY_": ""}
    )
    assert config == ServerConfig(transport="stdio")


def test_http_parses_api_keys_sorted_by_device():
    config = ServerConfig.from_env(
        {
            "MCP_TRANSPORT": "http",
            **KEY_ENV,
            "MCP_API_KEY_DESKTOP": "test-token-desktop",
        }
    )
    assert config.api_keys == (
        DeviceKey(device="DESKTOP", token="test-token-desktop"),
        DeviceKey(device=DEVICE, token=TOKEN),
    )


def test_http_zero_keys_raises():
    with pytest.raises(ValueError, match="at least one MCP_API_KEY_<DEVICE>"):
        ServerConfig.from_env({"MCP_TRANSPORT": "http"})


def test_http_empty_device_suffix_raises():
    with pytest.raises(ValueError, match="MCP_API_KEY_: no device name"):
        ServerConfig.from_env(
            {"MCP_TRANSPORT": "http", **KEY_ENV, "MCP_API_KEY_": "test-token-x"}
        )


def test_http_empty_token_raises():
    with pytest.raises(ValueError, match="MCP_API_KEY_DESKTOP: the token is empty"):
        ServerConfig.from_env(
            {"MCP_TRANSPORT": "http", **KEY_ENV, "MCP_API_KEY_DESKTOP": ""}
        )


def test_http_non_ascii_token_raises():
    # A non-ASCII token could never authenticate (headers arrive latin-1
    # decoded), so config load rejects it rather than failing silently.
    with pytest.raises(
        ValueError, match="MCP_API_KEY_DESKTOP: the token must be ASCII"
    ) as excinfo:
        ServerConfig.from_env(
            {"MCP_TRANSPORT": "http", **KEY_ENV, "MCP_API_KEY_DESKTOP": "test-tökén"}
        )
    assert "tökén" not in str(excinfo.value)


def test_http_duplicate_token_raises():
    with pytest.raises(
        ValueError,
        match="MCP_API_KEY_LAPTOP: it shares a token with MCP_API_KEY_DESKTOP",
    ) as excinfo:
        ServerConfig.from_env(
            {"MCP_TRANSPORT": "http", **KEY_ENV, "MCP_API_KEY_DESKTOP": TOKEN}
        )
    assert TOKEN not in str(excinfo.value)


def test_repr_hides_tokens():
    config = ServerConfig.from_env({"MCP_TRANSPORT": "http", **KEY_ENV})
    assert DEVICE in repr(config)
    assert TOKEN not in repr(config)
