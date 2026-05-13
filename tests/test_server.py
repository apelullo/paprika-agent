import asyncio

import pytest

import server
from server import PAPRIKA_API, _normalize, _populate_cache, get_recipe, list_recipes


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
