"""Per-device bearer-token verification for the HTTP transport.

FastMCP's RequireAuthMiddleware issues the 401 and calls verify_token;
this module only decides whether a presented token belongs to a
configured device. It is the adapter between config.DeviceKey and the
hmac boundary: tokens are compared as bytes.
"""

import hmac

from fastmcp.server.auth import AccessToken, TokenVerifier

from config import DeviceKey


class DeviceTokenVerifier(TokenVerifier):
    def __init__(self, keys: tuple[DeviceKey, ...]):
        super().__init__()
        # Encoded once. hmac.compare_digest raises TypeError on non-ASCII
        # str; bytes always compare.
        self._keys = tuple((key.device, key.token.encode("utf-8")) for key in keys)

    async def verify_token(self, token: str) -> AccessToken | None:
        presented = token.encode("utf-8")
        # Each compare_digest is constant-time in the token contents, but
        # the loop varies with the number of keys and stops at the first
        # match. Accepted for a handful of LAN devices (STAGE_02 3a
        # security note), not hidden behind an unqualified "constant-time".
        for device, expected in self._keys:
            if hmac.compare_digest(presented, expected):
                return AccessToken(token=token, client_id=device, scopes=[])
        return None
