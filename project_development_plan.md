# Project Development Plan

## Current state (as of 2026-05-20)

**Tooling:** ruff (lint + format, rules E/F/I/B/UP/N) + pre-commit + pytest + GitHub Actions CI (ruff check, ruff format, pytest) + git-cliff
**MCP tools:** `list_recipes`, `get_recipe`, `search_recipes`
**Architecture:** single file (`server.py`), eager in-memory cache (`_recipe_cache`, `_name_index`), bearer token auth from `.env`
**Stage:** 1 — MCP Tool Suite (~97% complete) — target tag: `v0.1.0`

## Completed milestones
- README: Architecture section
- README staleness pre-commit hook (warns, never blocks)
- `list_recipes` — fetch and cache all recipes from Paprika account
- `get_recipe` — retrieve full recipe details by name (case-insensitive, curly apostrophe normalization)
- `search_recipes` — keyword search across titles (substring + token order independence)
- ruff lint rule expansion (B, UP, N) + pre-commit integration
- CI pipeline with ruff check, ruff format, and pytest gates
- PostToolUse hook: poll loop CI status reporter after git push
- MIT license
- `git-cliff` / CHANGELOG — automated changelog from conventional commits
- Version tag map established: v0.1.0 (Stage 1) → v1.0.0 (Stage 6)
- README: Features, Quick Start, Architecture, Tech Stack, Roadmap sections
- Tool input validation — `_validate_input_string` helper + `MAX_QUERY_LENGTH` constant; raises `ValueError` with tool/param context for empty or oversized inputs

## Next actions (Stage 1 remaining — before `v0.1.0`)
- `sync_recipes` tool — single-account; incremental (ID set diff) + full refresh fallback
- `search_recipes` expansion — ingredients, source, prep instructions (discuss scope first)
- README: Demo section — defer until above tools complete, one recording captures everything
- Tag `v0.1.0` and run release workflow when above are done

## Stage roadmap
1. **MCP Tool Suite** — current; see next actions above
2. **Local Network Deployment** (compressed) — bind to LAN IP, connect Claude Desktop remotely; minimal ops
2.5. **Local Database & Schema** — SQLite persistent cache, dinner history table, dbt basics, incremental sync, deletion protection flag; `merge_recipes` tool — two-account merge (e.g. personal + spouse's account) with conflict resolution strategies: keep both, last-write-wins via timestamp, or manual override
3. **Custom Client** (compressed) — minimal Python script connecting to Stage 2 server; understand protocol from both sides
4. **Semantic Search & Embeddings** — sentence-transformers, FAISS, hybrid search, embedding storage in Stage 2.5 DB
5. **Recipe Recommender** — Bayesian preference model on 365+ day dinner history, temporal modeling, `recommend_recipes` tool, analytics dashboard
6. **Cloud, App & MLOps** — AWS/EC2, Docker, CD pipeline, Postgres migration, pgvector, full frontend, full CLI, observability

## Future ideas (no stage assigned)
- **Account similarity metric** — aggregate a distance/similarity score across two Paprika accounts (ingredient overlap, cuisine distribution, semantic similarity of recipe content); natural input to Stage 5 recommender for cross-account suggestions (e.g. "recipes your wife has that you'd probably enjoy")

## Deferred tests
- `get_token` bad response format — test the `raise ValueError(f"Unexpected login response: {body}")` branch
- `fetch_recipe` non-404 HTTP error — test that `response.raise_for_status()` propagates on e.g. 500

## Tooling roadmap
- **mypy or Pyright** — trigger: second source file added, or functions start calling each other
- **sentence-transformers + FAISS** — trigger: Stage 4 begins
- **SQLAlchemy or raw sqlite3** — trigger: Stage 2.5 begins (discuss ORM vs. raw SQL then)
- **git-cliff CI automation** — trigger: Stage 4-5; add tag-triggered changelog regeneration to `ci.yml`
