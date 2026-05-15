# Project Development Plan

## Current state (as of 2026-05-15)

**Tooling:** ruff (lint + format, rules E/F/I/B/UP/N) + pre-commit + pytest + GitHub Actions CI (ruff check, ruff format, pytest)
**MCP tools:** `list_recipes`, `get_recipe`, `search_recipes`
**Architecture:** single file (`server.py`), eager in-memory cache (`_recipe_cache`, `_name_index`), bearer token auth from `.env`

## Completed milestones
- `list_recipes` — fetch and cache all recipes from Paprika account
- `get_recipe` — retrieve full recipe details by name (case-insensitive, curly apostrophe normalization)
- `search_recipes` — keyword search across titles (substring + token order independence)
- ruff lint rule expansion (B, UP, N) + pre-commit integration
- CI pipeline with ruff check, ruff format, and pytest gates
- PostToolUse hook: poll loop CI status reporter after git push (fixed glob pattern to match chained commands)

## Planned features (near → long term)
1. **Local SQLite DB** — persist recipe cache across server restarts; eliminates cold-start API calls. Needs cache invalidation/refresh strategy. Likely requires a `cache.py` or `db.py` (also the mypy trigger).
2. **2-way account sync** — write back to Paprika (create/edit/delete recipes) via POST/PUT/PATCH/DELETE; requires conflict handling and local DB for state tracking.
3. **Local network deployment** — move MCP server to another machine on the local network; first step toward custom client and cloud hosting.
4. **Custom client** — beyond Claude Desktop.
5. **Cloud deployment**
6. **Semantic search with embeddings** — vague/natural language queries (e.g. "something spicy"); longer-term, part of the recipe recommender vision.
7. **Recipe recommender system**

## Tooling roadmap
1. **mypy or Pyright** — trigger: second source file added, or functions start calling each other.
2. **Semantic search deps** (e.g. sentence-transformers) — trigger: when embedding-based search is prioritized.

## Planned documentation
- **Learning/development summary doc** — will document recaps, learning milestones, and design decisions for long-term reference. `.gitignore` status TBD.
