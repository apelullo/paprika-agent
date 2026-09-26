"""Environment-driven server configuration.

Transport selection is value-authoritative: unset → stdio (safe local
default), set → validated and used, unknown → ValueError.
"""

from collections.abc import Mapping
from dataclasses import dataclass, field

VALID_TRANSPORTS = frozenset({"stdio", "http"})
DEFAULT_HOST = "127.0.0.1"  # fail-closed; set MCP_HOST to a LAN IP per machine
DEFAULT_PORT = 8000
API_KEY_PREFIX = "MCP_API_KEY_"


@dataclass(frozen=True)
class DeviceKey:
    device: str
    token: str = field(repr=False)  # kept out of reprs, so out of tracebacks


@dataclass(frozen=True)
class ServerConfig:
    transport: str
    host: str | None = None  # set only in HTTP mode
    port: int | None = None  # set only in HTTP mode
    api_keys: tuple[DeviceKey, ...] = ()  # set only in HTTP mode

    @classmethod
    def from_env(cls, env: Mapping[str, str]) -> "ServerConfig":
        """Resolve a ServerConfig from an environment mapping.

        Operates only on the passed mapping — callers inject os.environ
        (or a test dict); this method never reads os.environ itself.
        """
        transport = env.get("MCP_TRANSPORT")
        if transport is None:
            return cls(transport="stdio")
        if transport not in VALID_TRANSPORTS:
            allowed = ", ".join(sorted(VALID_TRANSPORTS))
            raise ValueError(
                f"Invalid MCP_TRANSPORT {transport!r}: must be one of {{{allowed}}}."
            )
        if transport == "stdio":
            # stdio ignores MCP_HOST/MCP_PORT entirely — never inspected.
            return cls(transport="stdio")

        # http: host/port resolution and validation are scoped
        # to this branch only.
        host = env.get("MCP_HOST", DEFAULT_HOST)
        port_raw = env.get("MCP_PORT")
        if port_raw is None:
            port = DEFAULT_PORT
        else:
            try:
                port = int(port_raw)
            except ValueError:
                raise ValueError(
                    f"Invalid MCP_PORT {port_raw!r}: must be an integer."
                ) from None
            if not 1 <= port <= 65535:
                raise ValueError(f"Invalid MCP_PORT {port}: must be in range 1-65535.")
        api_keys = _parse_api_keys(env)
        return cls(transport="http", host=host, port=port, api_keys=api_keys)


def _parse_api_keys(env: Mapping[str, str]) -> tuple[DeviceKey, ...]:
    """Collect every MCP_API_KEY_<DEVICE> into DeviceKeys sorted by device.

    The device name is the suffix after the prefix. Tokens are taken
    verbatim: no stripping, no minimum length, ASCII only. Error messages
    name the variable, never the token.
    """
    keys = []
    for name, token in env.items():
        if not name.startswith(API_KEY_PREFIX):
            continue
        device = name.removeprefix(API_KEY_PREFIX)
        if not device:
            raise ValueError(
                f"Invalid {name}: no device name; use MCP_API_KEY_<DEVICE>."
            )
        if not token:
            raise ValueError(f"Invalid {name}: the token is empty.")
        if not token.isascii():
            # Starlette decodes header values as latin-1, so a non-ASCII
            # token could never match over HTTP: fail loudly at load instead.
            raise ValueError(f"Invalid {name}: the token must be ASCII.")
        keys.append(DeviceKey(device=device, token=token))
    if not keys:
        raise ValueError(
            "MCP_TRANSPORT=http requires at least one MCP_API_KEY_<DEVICE>."
        )
    keys.sort(key=lambda key: key.device)

    # Plain == via dict lookup is fine here: config load is not an
    # authentication path, so no timing concern applies (auth.py compares
    # presented tokens with hmac.compare_digest).
    device_by_token: dict[str, str] = {}
    for key in keys:
        if key.token in device_by_token:
            other = device_by_token[key.token]
            raise ValueError(
                f"Invalid MCP_API_KEY_{key.device}: it shares a token with "
                f"MCP_API_KEY_{other}; each device needs its own token."
            )
        device_by_token[key.token] = key.device
    return tuple(keys)
