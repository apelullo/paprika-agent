"""Paprika API client — cache management, authentication, and recipe fetching."""

import asyncio
import os

import httpx

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
