# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running the server

```bash
uv run python server.py
```

Dependencies are managed with `uv`. To install them:

```bash
uv sync
```

## Running tests

```bash
uv run pytest tests/ -v
```

Tests live in `tests/test_server.py`. Unit tests cover pure functions and
require no credentials or network access.

## Architecture

All MCP tools live in `server.py`. The server authenticates with the Paprika API using email/password credentials from `.env` (`PAPRIKA_EMAIL`, `PAPRIKA_PASSWORD`), exchanging them for a bearer token on each cold start.

### Caching strategy

All recipes are fetched eagerly on first tool call via `_populate_cache()`, which is a no-op if the cache is already warm. Two module-level dicts are maintained:

- `_recipe_cache` — uid → full recipe dict
- `_name_index` — lowercase name → uid (for O(1) name lookups)

New tools that read recipe data should call `await _populate_cache()` first and read from these dicts rather than making their own API calls.

### Adding a new tool

Decorate an `async def` with `@mcp.tool()`. Tools that need recipe data should call `await _populate_cache()` and read from `_recipe_cache` / `_name_index`.

## Commit workflow

Before committing: show the git diff and proposed commit message for review.
Once confirmed, run `git add`, `git commit`, and `git push` together without
asking again.

## Environment

Requires a `.env` file with:

```
PAPRIKA_EMAIL=...
PAPRIKA_PASSWORD=...
```
