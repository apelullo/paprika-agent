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

    result = await paprika_client.sync(mode)

    if result.mode == "initial":
        return (
            f"Cache was empty — performed initial load. {result.total} recipes loaded."
        )
    if result.mode == "full":
        return f"Sync complete (full refresh). Cache contains {result.total} recipes."
    return (
        f"Sync complete (incremental): {result.added} added, {result.updated} updated,"
        f" {result.removed} removed. Cache contains {result.total} recipes."
    )


if __name__ == "__main__":
    mcp.run()
