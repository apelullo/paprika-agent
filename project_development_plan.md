# Project Development Plan

## Current state (as of 2026-07-22)

**Tooling:** ruff (lint + format, rules E/F/I/B/UP/N) + pre-commit + pytest + GitHub Actions CI (ruff check, ruff format, pytest) + git-cliff
**MCP tools:** `list_recipes`, `get_recipe`, `search_recipes`, `sync_recipes` (thin wrapper → `paprika_client.sync()`)
**Architecture:** three modules — `server.py` (MCP tools + entry point; resolves `ServerConfig.from_env(os.environ)` in `__main__`), `config.py` (frozen `ServerConfig` + value-authoritative `from_env`; transport auto-detection), and `paprika_client.py` (Paprika API + cache + `sync()`/`SyncResult`); eager in-memory cache (`_recipe_cache`, `_name_index`, `_cache_populated`) owned solely by `paprika_client`; bearer token auth from `.env`
**Stage:** 2 — Local Network Deployment (Pieces 0–2 done; Piece 3 next)

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
- `sync_recipes` — incremental (hash diff) + full refresh modes; `_cache_populated` flag fixes zero-recipe account re-fetch bug
- `sync_recipes` test suite — 10 tests covering cold cache, incremental add/edit/unchanged/delete/rename, full refresh, zero-recipe full refresh, flag reset regression, and invalid mode validation
- `search_recipes` empty-results message — scope hint on no match; expansion deferred to Stage 4
- `assets/` directory structure — `demos/stage_01/`, `images/`, `archive/` (gitignored); `*.mov` ignored
- README: Demo section — MP4 via GitHub user-attachments CDN
- v0.1.0 tagged and released — https://github.com/apelullo/paprika-agent/releases/tag/v0.1.0
- `server.py` refactor (Stage 2 Piece 0) — split into `server.py` (MCP) + `paprika_client.py` (API, cache, `sync()`/`SyncResult`); `sync_recipes` now validate→delegate→format; `paprika_client` sole owner of `_cache_populated`; suite 30→33; commits `24c9d45` (structural split), `090c099` (sync extraction)
- Transport wiring (Stage 2 Piece 2) — `_run_kwargs(config)` adapter in `server.py` feeds `mcp.run()`; host/port **omitted** (not `None`) in stdio because `run()` forwards `**kwargs` to `run_stdio_async()`, which has no such params; transport always passed explicitly so a stray `FASTMCP_TRANSPORT` in `.env` cannot redirect (FastMCP reads the same `.env` with prefix `FASTMCP_`). Contract value renamed `streamable-http` → `http` (exact synonyms upstream). Suite 46→51; verified live on stdio, `:8000`, `:9001`
- `config.py` + transport auto-detection (Stage 2 Piece 1) — frozen `ServerConfig` + `ServerConfig.from_env(env)`; value-authoritative `MCP_TRANSPORT` (unset→stdio, set→validated, unknown→`ValueError`); branch-scoped host/port validation; fail-closed `127.0.0.1`; `.env.example` contract; suite 33→46; commit `35517e5`

## Next actions (Stage 2)
- Piece 0 — `server.py`/`paprika_client.py` split ✅ done (`24c9d45`, `090c099`)
- Piece 1 — `config.py` + value-authoritative transport auto-detection ✅ done (`35517e5`)
- Piece 2 — transport wiring ✅ done (`3e21a04` rename + wiring commit)
- Piece 3 (next) — per-device bearer-token auth
- Then: unauthenticated `GET /health`; tests+CI gate; bind to LAN IP; `launchd` always-on service on MacBook Air; Claude Desktop remote config

## Stage roadmap
1. **MCP Tool Suite** ✅ COMPLETE — v0.1.0
2. **Local Network Deployment** — Streamable HTTP transport, per-device bearer-token auth, `GET /health`, LAN IP bind, `launchd` always-on service; `server.py` split done (Piece 0)
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
- Live integration test: hash verification against Test Recipe account; `tests/integration/`, `@pytest.mark.integration`, `-m "not integration"` in CI

## Deferred improvements
- **0-recipe account messaging** — `list_recipes`, `get_recipe`, and `search_recipes` return generic "not found" responses for empty accounts, indistinguishable from a real miss. Low priority; revisit if it causes user confusion.

## Tooling roadmap
- **mypy or Pyright** — trigger met (2026-06-25: `paprika_client.py` added; cross-module calls); revisit adding static type-checking
- **sentence-transformers + FAISS** — trigger: Stage 4 begins
- **SQLAlchemy or raw sqlite3** — trigger: Stage 2.5 begins (discuss ORM vs. raw SQL then)
- **git-cliff CI automation** — trigger: Stage 4-5; add tag-triggered changelog regeneration to `ci.yml`
