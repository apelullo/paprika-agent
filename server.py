import asyncio
import os

import httpx
from dotenv import load_dotenv
from fastmcp import FastMCP

load_dotenv()

mcp = FastMCP("Paprika")

PAPRIKA_API = "https://www.paprikaapp.com/api/v2"

_recipe_cache: dict[str, dict] = {}  # uid → full recipe data


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


async def _populate_cache() -> None:
    """Fetch all recipes from Paprika and store in module-level cache.
    No-op if cache is already warm."""
    if _recipe_cache:
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


@mcp.tool()
async def list_recipes() -> list[str]:
    """Return a list of all recipe titles from Paprika."""
    await _populate_cache()
    return [r["name"] for r in _recipe_cache.values()]


if __name__ == "__main__":
    mcp.run()
