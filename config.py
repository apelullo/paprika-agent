"""Environment-driven server configuration.

Transport selection is value-authoritative: unset → stdio (safe local
default), set → validated and used, unknown → ValueError.
"""

from collections.abc import Mapping
from dataclasses import dataclass

VALID_TRANSPORTS = frozenset({"stdio", "streamable-http"})
DEFAULT_HOST = "127.0.0.1"  # fail-closed; set MCP_HOST to a LAN IP per machine
DEFAULT_PORT = 8000


@dataclass(frozen=True)
class ServerConfig:
    transport: str
    host: str | None = None  # set only in HTTP mode
    port: int | None = None  # set only in HTTP mode

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

        # streamable-http: host/port resolution and validation are scoped
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
        return cls(transport="streamable-http", host=host, port=port)
