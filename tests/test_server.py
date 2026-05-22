import asyncio

import httpx
import pytest

import server
from server import (
    PAPRIKA_API,
    _normalize,
    _populate_cache,
    _validate_input_string,
    fetch_recipe,
    get_recipe,
    list_recipes,
    search_recipes,
    sync_recipes,
)


async def _noop():
    pass


def test_normalize_curly_apostrophes():
    assert _normalize("Mom’s Soup") == _normalize("Mom's Soup")
    assert _normalize("‘quoted’") == _normalize("'quoted'")


def test_normalize_lowercases():
    assert _normalize("Chicken Soup") == "chicken soup"


def test_list_recipes(monkeypatch):
    monkeypatch.setattr(
        "server._recipe_cache",
        {"uid-1": {"name": "Mom's Soup"}, "uid-2": {"name": "Garlic Bread"}},
    )
    monkeypatch.setattr("server._populate_cache", _noop)
    result = asyncio.run(list_recipes())
    assert set(result) == {"Mom's Soup", "Garlic Bread"}


def test_get_recipe_found(monkeypatch):
    monkeypatch.setattr(
        "server._recipe_cache", {"uid-1": {"uid": "uid-1", "name": "Mom's Soup"}}
    )
    monkeypatch.setattr("server._name_index", {"mom's soup": "uid-1"})
    monkeypatch.setattr("server._populate_cache", _noop)
    result = asyncio.run(get_recipe("Mom's Soup"))
    assert result == {"uid": "uid-1", "name": "Mom's Soup"}


def test_get_recipe_not_found(monkeypatch):
    monkeypatch.setattr("server._recipe_cache", {})
    monkeypatch.setattr("server._name_index", {})
    monkeypatch.setattr("server._populate_cache", _noop)
    result = asyncio.run(get_recipe("Nonexistent"))
    assert "No recipe found" in result


def test_get_recipe_curly_apostrophe(monkeypatch):
    # Paprika stores curly apostrophes; user types straight — both should match
    monkeypatch.setattr(
        "server._recipe_cache",
        {"uid-1": {"uid": "uid-1", "name": "Mom’s Soup"}},
    )
    monkeypatch.setattr("server._name_index", {"mom's soup": "uid-1"})
    monkeypatch.setattr("server._populate_cache", _noop)
    result = asyncio.run(get_recipe("Mom's Soup"))
    assert result == {"uid": "uid-1", "name": "Mom’s Soup"}


def test_normalize_empty_string():
    assert _normalize("") == ""


def test_normalize_mixed_apostrophes():
    assert _normalize("it’s a ‘test’") == "it's a 'test'"


def test_search_recipes_single_token(monkeypatch):
    monkeypatch.setattr(
        "server._recipe_cache",
        {"uid-1": {"name": "Chicken Soup"}, "uid-2": {"name": "Garlic Bread"}},
    )
    monkeypatch.setattr("server._populate_cache", _noop)
    result = asyncio.run(search_recipes("chicken"))
    assert result == ["Chicken Soup"]


def test_search_recipes_token_order_independence(monkeypatch):
    monkeypatch.setattr(
        "server._recipe_cache",
        {"uid-1": {"name": "Chicken Tikka Masala"}, "uid-2": {"name": "Garlic Bread"}},
    )
    monkeypatch.setattr("server._populate_cache", _noop)
    result = asyncio.run(search_recipes("masala chicken"))
    assert result == ["Chicken Tikka Masala"]


def test_search_recipes_multiple_matches(monkeypatch):
    monkeypatch.setattr(
        "server._recipe_cache",
        {
            "uid-1": {"name": "Chicken Soup"},
            "uid-2": {"name": "Chicken Tikka Masala"},
            "uid-3": {"name": "Garlic Bread"},
        },
    )
    monkeypatch.setattr("server._populate_cache", _noop)
    result = asyncio.run(search_recipes("chicken"))
    assert set(result) == {"Chicken Soup", "Chicken Tikka Masala"}


def test_search_recipes_no_match(monkeypatch):
    monkeypatch.setattr("server._recipe_cache", {"uid-1": {"name": "Chicken Soup"}})
    monkeypatch.setattr("server._populate_cache", _noop)
    result = asyncio.run(search_recipes("pasta"))
    assert "No recipes found" in result


def test_validate_input_string_whitespace_only():
    with pytest.raises(ValueError, match="must be a non-empty string"):
        _validate_input_string("   ", "name", "test_tool")


def test_get_recipe_empty_name(monkeypatch):
    monkeypatch.setattr("server._recipe_cache", {})
    monkeypatch.setattr("server._populate_cache", _noop)
    with pytest.raises(ValueError, match="must be a non-empty string"):
        asyncio.run(get_recipe(""))


def test_get_recipe_name_too_long(monkeypatch):
    monkeypatch.setattr("server._recipe_cache", {})
    monkeypatch.setattr("server._populate_cache", _noop)
    with pytest.raises(ValueError, match="exceeds"):
        asyncio.run(get_recipe("a" * 201))


def test_search_recipes_query_too_long(monkeypatch):
    monkeypatch.setattr("server._recipe_cache", {})
    monkeypatch.setattr("server._populate_cache", _noop)
    with pytest.raises(ValueError, match="exceeds"):
        asyncio.run(search_recipes("a" * 201))


def test_search_recipes_empty_query(monkeypatch):
    monkeypatch.setattr("server._recipe_cache", {})
    monkeypatch.setattr("server._populate_cache", _noop)
    with pytest.raises(ValueError, match="must be a non-empty string"):
        asyncio.run(search_recipes(""))


@pytest.mark.anyio
async def test_fetch_recipe_404(httpx_mock):
    httpx_mock.add_response(
        method="GET",
        url=f"{PAPRIKA_API}/sync/recipe/missing-uid/",
        status_code=404,
    )
    async with httpx.AsyncClient() as client:
        result = await fetch_recipe(
            client, "fake-token", "missing-uid", asyncio.Semaphore(1)
        )
    assert result is None


@pytest.mark.anyio
async def test_populate_cache_already_warm(httpx_mock, monkeypatch):
    existing = {"uid-1": {"uid": "uid-1", "name": "Mom's Soup"}}
    monkeypatch.setattr("server._recipe_cache", existing.copy())
    monkeypatch.setattr("server._cache_populated", True)
    await _populate_cache()
    assert server._recipe_cache == existing


@pytest.mark.anyio
async def test_populate_cache(httpx_mock, monkeypatch):
    monkeypatch.setattr("server._recipe_cache", {})
    monkeypatch.setattr("server._name_index", {})
    monkeypatch.setattr("server._cache_populated", False)

    httpx_mock.add_response(
        method="POST",
        url=f"{PAPRIKA_API}/account/login/",
        json={"result": {"token": "fake-token"}},
    )
    httpx_mock.add_response(
        method="GET",
        url=f"{PAPRIKA_API}/sync/recipes/",
        json={"result": [{"uid": "uid-1", "name": "Mom’s Soup"}]},
    )
    httpx_mock.add_response(
        method="GET",
        url=f"{PAPRIKA_API}/sync/recipe/uid-1/",
        json={"result": {"uid": "uid-1", "name": "Mom’s Soup"}},
    )

    await _populate_cache()

    assert server._recipe_cache == {"uid-1": {"uid": "uid-1", "name": "Mom’s Soup"}}
    assert server._name_index == {_normalize("Mom’s Soup"): "uid-1"}


@pytest.mark.anyio
async def test_sync_recipes_cold_cache(monkeypatch):
    monkeypatch.setattr("server._cache_populated", False)
    monkeypatch.setattr("server._recipe_cache", {})
    monkeypatch.setattr("server._name_index", {})

    async def mock_populate():
        server._recipe_cache["uid-1"] = {
            "uid": "uid-1",
            "name": "Chicken Soup",
            "hash": "abc",
        }
        server._cache_populated = True

    monkeypatch.setattr("server._populate_cache", mock_populate)
    result = await sync_recipes()
    assert "initial load" in result
    assert "1 recipes loaded" in result


@pytest.mark.anyio
async def test_sync_recipes_incremental_new_recipe(httpx_mock, monkeypatch):
    existing = {"uid-1": {"uid": "uid-1", "name": "Chicken Soup", "hash": "abc"}}
    monkeypatch.setattr("server._recipe_cache", existing.copy())
    monkeypatch.setattr("server._name_index", {"chicken soup": "uid-1"})
    monkeypatch.setattr("server._cache_populated", True)

    httpx_mock.add_response(
        method="POST",
        url=f"{PAPRIKA_API}/account/login/",
        json={"result": {"token": "fake-token"}},
    )
    httpx_mock.add_response(
        method="GET",
        url=f"{PAPRIKA_API}/sync/recipes/",
        json={
            "result": [
                {"uid": "uid-1", "hash": "abc"},
                {"uid": "uid-2", "hash": "def"},
            ]
        },
    )
    httpx_mock.add_response(
        method="GET",
        url=f"{PAPRIKA_API}/sync/recipe/uid-2/",
        json={"result": {"uid": "uid-2", "name": "Garlic Bread", "hash": "def"}},
    )

    result = await sync_recipes()
    assert "1 added" in result
    assert "0 updated" in result
    assert "0 removed" in result
    assert "uid-2" in server._recipe_cache
    assert "garlic bread" in server._name_index


@pytest.mark.anyio
async def test_sync_recipes_incremental_edited_recipe(httpx_mock, monkeypatch):
    existing = {"uid-1": {"uid": "uid-1", "name": "Chicken Soup", "hash": "old-hash"}}
    monkeypatch.setattr("server._recipe_cache", existing.copy())
    monkeypatch.setattr("server._name_index", {"chicken soup": "uid-1"})
    monkeypatch.setattr("server._cache_populated", True)

    httpx_mock.add_response(
        method="POST",
        url=f"{PAPRIKA_API}/account/login/",
        json={"result": {"token": "fake-token"}},
    )
    httpx_mock.add_response(
        method="GET",
        url=f"{PAPRIKA_API}/sync/recipes/",
        json={"result": [{"uid": "uid-1", "hash": "new-hash"}]},
    )
    httpx_mock.add_response(
        method="GET",
        url=f"{PAPRIKA_API}/sync/recipe/uid-1/",
        json={
            "result": {
                "uid": "uid-1",
                "name": "Chicken Soup Updated",
                "hash": "new-hash",
            }
        },
    )

    result = await sync_recipes()
    assert "0 added" in result
    assert "1 updated" in result
    assert "0 removed" in result
    assert server._recipe_cache["uid-1"]["name"] == "Chicken Soup Updated"


@pytest.mark.anyio
async def test_sync_recipes_incremental_unchanged_recipe(httpx_mock, monkeypatch):
    existing = {"uid-1": {"uid": "uid-1", "name": "Chicken Soup", "hash": "abc"}}
    monkeypatch.setattr("server._recipe_cache", existing.copy())
    monkeypatch.setattr("server._name_index", {"chicken soup": "uid-1"})
    monkeypatch.setattr("server._cache_populated", True)

    fetch_called = []

    async def mock_fetch(client, token, uid, semaphore):
        fetch_called.append(uid)
        return None

    monkeypatch.setattr("server.fetch_recipe", mock_fetch)

    httpx_mock.add_response(
        method="POST",
        url=f"{PAPRIKA_API}/account/login/",
        json={"result": {"token": "fake-token"}},
    )
    httpx_mock.add_response(
        method="GET",
        url=f"{PAPRIKA_API}/sync/recipes/",
        json={"result": [{"uid": "uid-1", "hash": "abc"}]},
    )

    result = await sync_recipes()
    assert fetch_called == []
    assert "0 added" in result
    assert "0 updated" in result
    assert "0 removed" in result


@pytest.mark.anyio
async def test_sync_recipes_incremental_deleted_recipe(httpx_mock, monkeypatch):
    existing = {
        "uid-1": {"uid": "uid-1", "name": "Chicken Soup", "hash": "abc"},
        "uid-2": {"uid": "uid-2", "name": "Garlic Bread", "hash": "def"},
    }
    monkeypatch.setattr("server._recipe_cache", existing.copy())
    monkeypatch.setattr(
        "server._name_index",
        {"chicken soup": "uid-1", "garlic bread": "uid-2"},
    )
    monkeypatch.setattr("server._cache_populated", True)

    httpx_mock.add_response(
        method="POST",
        url=f"{PAPRIKA_API}/account/login/",
        json={"result": {"token": "fake-token"}},
    )
    httpx_mock.add_response(
        method="GET",
        url=f"{PAPRIKA_API}/sync/recipes/",
        json={"result": [{"uid": "uid-1", "hash": "abc"}]},
    )

    result = await sync_recipes()
    assert "1 removed" in result
    assert "uid-2" not in server._recipe_cache
    assert "garlic bread" not in server._name_index


@pytest.mark.anyio
async def test_sync_recipes_incremental_name_change(httpx_mock, monkeypatch):
    existing = {"uid-1": {"uid": "uid-1", "name": "Old Name", "hash": "old-hash"}}
    monkeypatch.setattr("server._recipe_cache", existing.copy())
    monkeypatch.setattr("server._name_index", {"old name": "uid-1"})
    monkeypatch.setattr("server._cache_populated", True)

    httpx_mock.add_response(
        method="POST",
        url=f"{PAPRIKA_API}/account/login/",
        json={"result": {"token": "fake-token"}},
    )
    httpx_mock.add_response(
        method="GET",
        url=f"{PAPRIKA_API}/sync/recipes/",
        json={"result": [{"uid": "uid-1", "hash": "new-hash"}]},
    )
    httpx_mock.add_response(
        method="GET",
        url=f"{PAPRIKA_API}/sync/recipe/uid-1/",
        json={"result": {"uid": "uid-1", "name": "New Name", "hash": "new-hash"}},
    )

    await sync_recipes()
    assert "old name" not in server._name_index
    assert "new name" in server._name_index


@pytest.mark.anyio
async def test_sync_recipes_full_refresh(monkeypatch):
    stale = {"uid-1": {"uid": "uid-1", "name": "Stale Recipe", "hash": "old"}}
    monkeypatch.setattr("server._recipe_cache", stale.copy())
    monkeypatch.setattr("server._name_index", {"stale recipe": "uid-1"})
    monkeypatch.setattr("server._cache_populated", True)

    async def mock_populate():
        server._recipe_cache["uid-2"] = {
            "uid": "uid-2",
            "name": "Fresh Recipe",
            "hash": "new",
        }
        server._cache_populated = True

    monkeypatch.setattr("server._populate_cache", mock_populate)

    result = await sync_recipes(mode="full")
    assert "full refresh" in result
    assert "uid-2" in server._recipe_cache
    assert "uid-1" not in server._recipe_cache


@pytest.mark.anyio
async def test_sync_recipes_full_refresh_repopulates_after_flag_reset(monkeypatch):
    existing = {"uid-1": {"uid": "uid-1", "name": "Chicken Soup", "hash": "abc"}}
    monkeypatch.setattr("server._recipe_cache", existing.copy())
    monkeypatch.setattr("server._name_index", {"chicken soup": "uid-1"})
    monkeypatch.setattr("server._cache_populated", True)

    populate_called = []

    async def mock_populate():
        populate_called.append(True)
        server._recipe_cache["uid-1"] = {
            "uid": "uid-1",
            "name": "Chicken Soup",
            "hash": "abc",
        }
        server._cache_populated = True

    monkeypatch.setattr("server._populate_cache", mock_populate)

    await sync_recipes(mode="full")
    assert populate_called == [True]
    assert server._recipe_cache


@pytest.mark.anyio
async def test_sync_recipes_full_refresh_zero_recipes(monkeypatch):
    monkeypatch.setattr("server._recipe_cache", {})
    monkeypatch.setattr("server._name_index", {})
    monkeypatch.setattr("server._cache_populated", True)

    async def mock_populate():
        server._cache_populated = True

    monkeypatch.setattr("server._populate_cache", mock_populate)

    result = await sync_recipes(mode="full")
    assert "full refresh" in result
    assert server._cache_populated is True


@pytest.mark.anyio
async def test_sync_recipes_invalid_mode(monkeypatch):
    monkeypatch.setattr("server._cache_populated", True)
    with pytest.raises(ValueError, match=r"\[sync_recipes\].*must be"):
        await sync_recipes(mode="invalid")
