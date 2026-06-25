"""Paprika API client — cache management, authentication, and recipe fetching."""

import asyncio
import os
from dataclasses import dataclass

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


@dataclass
class SyncResult:
    """Structured result of a cache sync. `mode` is the OUTCOME mode:
    "initial" (cold cache → full load), "full" (explicit full refresh),
    or "incremental" (hash diff). added/updated/removed are populated
    only for incremental; total is the recipe count after the op."""

    mode: str
    total: int
    added: int = 0
    updated: int = 0
    removed: int = 0


async def sync(mode: str) -> SyncResult:
    """Sync the in-memory cache with the Paprika API; report what changed.

    Precondition: `mode` is "incremental" or "full" (validated by the
    caller). Owns all reads/writes of _recipe_cache, _name_index, and
    _cache_populated.
    """
    global _cache_populated

    if not _cache_populated:
        await _populate_cache()
        return SyncResult(mode="initial", total=len(_recipe_cache))

    if mode == "full":
        _recipe_cache.clear()
        _name_index.clear()
        _cache_populated = False
        await _populate_cache()
        return SyncResult(mode="full", total=len(_recipe_cache))

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

    return SyncResult(
        mode="incremental",
        total=len(_recipe_cache),
        added=added,
        updated=updated,
        removed=removed,
    )
