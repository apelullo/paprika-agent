import asyncio
import os

import httpx
from dotenv import load_dotenv
from fastmcp import FastMCP

load_dotenv()

mcp = FastMCP("Paprika")

PAPRIKA_API = "https://www.paprikaapp.com/api/v2"

MAX_QUERY_LENGTH = 200

_recipe_cache: dict[str, dict] = {}  # uid → full recipe data
_name_index: dict[str, str] = {}  # lowercase name → uid
_cache_populated: bool = False


async def get_token() -> str:
    email = os.getenv("PAPRIKA_EMAIL")
    password = os.getenv("PAPRIKA_PASSWORD")
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{PAPRIKA_API}/account/login/",
            data={"email": email, "password": password},
            headers={"User-Agent": "Paprika/3.0 (iOS)"},
        )
        response.raise_for_status()
        body = response.json()
        if "result" not in body:
            raise ValueError(f"Unexpected login response: {body}")
        return body["result"]["token"]


async def fetch_recipe(
    client: httpx.AsyncClient, token: str, uid: str, semaphore: asyncio.Semaphore
) -> dict | None:
    async with semaphore:
        response = await client.get(
            f"{PAPRIKA_API}/sync/recipe/{uid}/",
            headers={"Authorization": f"Bearer {token}"},
        )
        if response.status_code == 404:
            return None
        response.raise_for_status()
        return response.json()["result"]


def _normalize(name: str) -> str:
    """Lowercase and normalize curly apostrophes to straight for consistent matching."""
    return name.lower().replace("’", "'").replace("‘", "'")


def _validate_input_string(value: str, param: str, tool: str) -> None:
    """Raise ValueError with a helpful message if a string param is unusable."""
    if not value or not value.strip():
        raise ValueError(f"[{tool}] ‘{param}’ must be a non-empty string.")
    if len(value.strip()) > MAX_QUERY_LENGTH:
        raise ValueError(f"[{tool}] ‘{param}’ exceeds {MAX_QUERY_LENGTH} characters.")


async def _populate_cache() -> None:
    """Fetch all recipes from Paprika and store in module-level cache.
    No-op if cache is already warm."""
    global _cache_populated
    if _cache_populated:
        return

    token = await get_token()
    semaphore = asyncio.Semaphore(5)

    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.get(
            f"{PAPRIKA_API}/sync/recipes/",
            headers={"Authorization": f"Bearer {token}"},
        )
        response.raise_for_status()
        index = response.json()["result"]

        recipes = await asyncio.gather(
            *[fetch_recipe(client, token, entry["uid"], semaphore) for entry in index]
        )

    for recipe in recipes:
        if recipe is not None:
            _recipe_cache[recipe["uid"]] = recipe
            _name_index[_normalize(recipe["name"])] = recipe["uid"]

    _cache_populated = True


@mcp.tool()
async def list_recipes() -> list[str]:
    """Return a list of all recipe titles from Paprika."""
    await _populate_cache()
    return [r["name"] for r in _recipe_cache.values()]


@mcp.tool()
async def get_recipe(name: str) -> dict | str:
    """Return full details for a recipe by name (case-insensitive, exact match).
    Returns a not-found message if no recipe with that name exists."""
    await _populate_cache()
    _validate_input_string(name, "name", "get_recipe")
    uid = _name_index.get(_normalize(name))
    if uid is None:
        return f"No recipe found with name '{name}'."
    return _recipe_cache[uid]


@mcp.tool()
async def search_recipes(query: str) -> list[str] | str:
    """Search recipes by keyword. Returns all recipe names where every query
    token appears in the name (case-insensitive, order-independent)."""
    await _populate_cache()
    _validate_input_string(query, "query", "search_recipes")
    tokens = _normalize(query).split()
    matches = [
        r["name"]
        for r in _recipe_cache.values()
        if all(token in _normalize(r["name"]) for token in tokens)
    ]
    return matches if matches else f"No recipes found matching '{query}'."


@mcp.tool()
async def sync_recipes(mode: str = "incremental") -> str:
    """Sync the in-memory recipe cache with the Paprika API.

    Use 'incremental' by default — fetches only new, edited, or deleted
    recipes using hash comparison. Suggest 'full' if the user reports a recipe
    is missing or incorrect after an incremental sync, or if the cache may
    be partially populated.

    Returns a summary of what changed.
    """
    global _cache_populated
    _validate_input_string(mode, "mode", "sync_recipes")
    if mode not in ("incremental", "full"):
        raise ValueError("[sync_recipes] 'mode' must be 'incremental' or 'full'.")

    if not _cache_populated:
        await _populate_cache()
        n = len(_recipe_cache)
        return f"Cache was empty — performed initial load. {n} recipes loaded."

    if mode == "full":
        _recipe_cache.clear()
        _name_index.clear()
        _cache_populated = False
        await _populate_cache()
        n = len(_recipe_cache)
        return f"Sync complete (full refresh). Cache contains {n} recipes."

    # Incremental: fetch uid/hash list and diff against cache
    token = await get_token()
    semaphore = asyncio.Semaphore(5)

    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.get(
            f"{PAPRIKA_API}/sync/recipes/",
            headers={"Authorization": f"Bearer {token}"},
        )
        response.raise_for_status()
        api_entries = response.json()["result"]

        api_map = {entry["uid"]: entry["hash"] for entry in api_entries}
        to_fetch = [
            uid
            for uid, api_hash in api_map.items()
            if uid not in _recipe_cache or _recipe_cache[uid].get("hash") != api_hash
        ]
        deleted_uids = [uid for uid in list(_recipe_cache) if uid not in api_map]

        fetched = await asyncio.gather(
            *[fetch_recipe(client, token, uid, semaphore) for uid in to_fetch]
        )

    added = updated = removed = 0

    for uid, recipe in zip(to_fetch, fetched, strict=True):
        if recipe is None:
            continue
        old = _recipe_cache.get(uid)
        # Recipe may have been renamed — remove the stale name-index entry first
        if old is not None and _normalize(old["name"]) != _normalize(recipe["name"]):
            _name_index.pop(_normalize(old["name"]), None)
        _recipe_cache[recipe["uid"]] = recipe
        _name_index[_normalize(recipe["name"])] = recipe["uid"]
        if old is None:
            added += 1
        else:
            updated += 1

    for uid in deleted_uids:
        recipe = _recipe_cache.pop(uid, None)
        if recipe is not None:
            _name_index.pop(_normalize(recipe["name"]), None)
            removed += 1

    return (
        f"Sync complete (incremental): {added} added, {updated} updated,"
        f" {removed} removed. Cache contains {len(_recipe_cache)} recipes."
    )


if __name__ == "__main__":
    mcp.run()
