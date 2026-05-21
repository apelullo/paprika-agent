import asyncio

import httpx
import pytest

import server
from server import (
    PAPRIKA_API,
    _normalize,
    _populate_cache,
    fetch_recipe,
    get_recipe,
    list_recipes,
    search_recipes,
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


def test_get_recipe_empty_name(monkeypatch):
    monkeypatch.setattr("server._recipe_cache", {})
    monkeypatch.setattr("server._populate_cache", _noop)
    with pytest.raises(ValueError, match="must be a non-empty string"):
        asyncio.run(get_recipe(""))


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
async def test_populate_cache(httpx_mock, monkeypatch):
    monkeypatch.setattr("server._recipe_cache", {})
    monkeypatch.setattr("server._name_index", {})

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
    assert server._name_index == {"mom's soup": "uid-1"}
