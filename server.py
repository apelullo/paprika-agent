import asyncio

import httpx
from dotenv import load_dotenv
from fastmcp import FastMCP

import paprika_client

load_dotenv()

mcp = FastMCP("Paprika")


@mcp.tool()
async def list_recipes() -> list[str]:
    """Return a list of all recipe titles from Paprika."""
    await paprika_client._populate_cache()
    return [r["name"] for r in paprika_client._recipe_cache.values()]


@mcp.tool()
async def get_recipe(name: str) -> dict | str:
    """Return full details for a recipe by name (case-insensitive, exact match).
    Returns a not-found message if no recipe with that name exists."""
    await paprika_client._populate_cache()
    paprika_client._validate_input_string(name, "name", "get_recipe")
    uid = paprika_client._name_index.get(paprika_client._normalize(name))
    if uid is None:
        return f"No recipe found with name '{name}'."
    return paprika_client._recipe_cache[uid]


@mcp.tool()
async def search_recipes(query: str) -> list[str] | str:
    """Search recipes by keyword. Returns all recipe names where every query
    token appears in the name (case-insensitive, order-independent)."""
    await paprika_client._populate_cache()
    paprika_client._validate_input_string(query, "query", "search_recipes")
    tokens = paprika_client._normalize(query).split()
    matches = [
        r["name"]
        for r in paprika_client._recipe_cache.values()
        if all(token in paprika_client._normalize(r["name"]) for token in tokens)
    ]
    return (
        matches
        if matches
        else (
            f"No recipes found matching '{query}' in recipe titles. "
            f"Ingredient, source, and natural language search are coming "
            f"in a future update. "
            f"Try a different title keyword or a more specific term."
        )
    )


@mcp.tool()
async def sync_recipes(mode: str = "incremental") -> str:
    """Sync the in-memory recipe cache with the Paprika API.

    Use 'incremental' by default — fetches only new, edited, or deleted
    recipes using hash comparison. Suggest 'full' if the user reports a recipe
    is missing or incorrect after an incremental sync, or if the cache may
    be partially populated.

    Returns a summary of what changed.
    """
    paprika_client._validate_input_string(mode, "mode", "sync_recipes")
    if mode not in ("incremental", "full"):
        raise ValueError("[sync_recipes] 'mode' must be 'incremental' or 'full'.")

    if not paprika_client._cache_populated:
        await paprika_client._populate_cache()
        n = len(paprika_client._recipe_cache)
        return f"Cache was empty — performed initial load. {n} recipes loaded."

    if mode == "full":
        paprika_client._recipe_cache.clear()
        paprika_client._name_index.clear()
        paprika_client._cache_populated = False
        await paprika_client._populate_cache()
        n = len(paprika_client._recipe_cache)
        return f"Sync complete (full refresh). Cache contains {n} recipes."

    # Incremental: fetch uid/hash list and diff against cache
    token = await paprika_client.get_token()
    semaphore = asyncio.Semaphore(5)

    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.get(
            f"{paprika_client.PAPRIKA_API}/sync/recipes/",
            headers={"Authorization": f"Bearer {token}"},
        )
        response.raise_for_status()
        api_entries = response.json()["result"]

        api_map = {entry["uid"]: entry["hash"] for entry in api_entries}
        to_fetch = [
            uid
            for uid, api_hash in api_map.items()
            if uid not in paprika_client._recipe_cache
            or paprika_client._recipe_cache[uid].get("hash") != api_hash
        ]
        deleted_uids = [
            uid for uid in list(paprika_client._recipe_cache) if uid not in api_map
        ]

        fetched = await asyncio.gather(
            *[
                paprika_client.fetch_recipe(client, token, uid, semaphore)
                for uid in to_fetch
            ]
        )

    added = updated = removed = 0

    for uid, recipe in zip(to_fetch, fetched, strict=True):
        if recipe is None:
            continue
        old = paprika_client._recipe_cache.get(uid)
        # Recipe may have been renamed — remove the stale name-index entry first
        if old is not None and paprika_client._normalize(
            old["name"]
        ) != paprika_client._normalize(recipe["name"]):
            paprika_client._name_index.pop(paprika_client._normalize(old["name"]), None)
        paprika_client._recipe_cache[recipe["uid"]] = recipe
        paprika_client._name_index[paprika_client._normalize(recipe["name"])] = recipe[
            "uid"
        ]
        if old is None:
            added += 1
        else:
            updated += 1

    for uid in deleted_uids:
        recipe = paprika_client._recipe_cache.pop(uid, None)
        if recipe is not None:
            paprika_client._name_index.pop(
                paprika_client._normalize(recipe["name"]), None
            )
            removed += 1

    return (
        f"Sync complete (incremental): {added} added, {updated} updated,"
        f" {removed} removed. Cache contains "
        f"{len(paprika_client._recipe_cache)} recipes."
    )


if __name__ == "__main__":
    mcp.run()
