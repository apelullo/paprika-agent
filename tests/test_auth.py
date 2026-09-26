import pytest

from auth import DeviceTokenVerifier
from config import DeviceKey

KEYS = (
    DeviceKey(device="DESKTOP", token="test-token-desktop"),
    DeviceKey(device="LAPTOP", token="test-token-laptop"),
)


@pytest.fixture
def verifier():
    return DeviceTokenVerifier(KEYS)


@pytest.mark.anyio
@pytest.mark.parametrize("key", KEYS, ids=lambda key: key.device)
async def test_each_token_returns_its_device(verifier, key):
    access = await verifier.verify_token(key.token)
    assert access is not None
    assert access.client_id == key.device
    assert access.token == key.token
    assert access.scopes == []


@pytest.mark.anyio
@pytest.mark.parametrize(
    "token",
    ["test-token-unknown", "", "test-token-lap"],
    ids=["unknown", "empty", "strict-prefix"],
)
async def test_non_matching_token_returns_none(verifier, token):
    assert await verifier.verify_token(token) is None


@pytest.mark.anyio
async def test_non_ascii_token_returns_none_without_raising(verifier):
    # hmac.compare_digest raises TypeError on non-ASCII str; bytes do not.
    assert await verifier.verify_token("test-tökén-🔑") is None
