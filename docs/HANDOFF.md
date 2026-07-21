# Paprika Agent — New Chat Handoff

> Paste as the first message in the next project chat. This file is a
> regenerated VIEW of the other docs — never author unique facts into it.

## Project identity

**Paprika Agent** — MCP server connecting Claude Desktop to the Paprika recipe
manager via its unofficial API. Repo: github.com/apelullo/paprika-agent

**Developer:** Art Pelullo — Senior Data Scientist, 7 yrs Penn Medicine.
Strong Python/DS fundamentals moving into production software engineering.
Learns fast conceptually; architecture judgment and scope discipline are
demonstrated strengths (principled reversals of locked decisions, fail-safe
defaults reached for unprompted). Underestimates his own output — give
calibrated assessments.
Building in the open.

**Working style:** Why before how. Succinct, scannable, bold key info, clear
next step. Code-review mode; never ghostwrite. His exact words are ground truth.
**Pace:** fundamentals are solidifying — keep wording tight and bolded, move
quickly to decisions, but never drop information that would otherwise have been
shared. Slow down and rebuild foundations at the start of a new **stage** (or a
substantial piece). He asks questions when unclear, so terseness is safe.

**Conventions:** `uv` only · credentials in `.env` (verify `.gitignore`) · one
piece at a time, widen scope only deliberately + documented.

## Current state — Stage 1 complete; Stage 2 Pieces 0–1 complete; Piece 2 next

**Stack:** Python 3.13 · FastMCP (pinned 3.2.4) · httpx · uv · pytest · ruff ·
pre-commit · GitHub Actions CI · git-cliff

**Architecture — three modules:**

| File | Responsibility |
|---|---|
| `server.py` | MCP only. Imports `os`, `dotenv`, `fastmcp`, `config`, `paprika_client` (no `httpx`/`asyncio`). `load_dotenv()`, 4 `@mcp.tool()` defs, `__main__` resolves `ServerConfig.from_env(os.environ)`. |
| `config.py` | Env-driven config. Frozen `ServerConfig` + `from_env(env)`. Value-authoritative transport (unset→stdio; set→validated; unknown→`ValueError`). Host/port scoped to streamable-http branch; fail-closed `127.0.0.1`. Reads only the injected mapping. |
| `paprika_client.py` | Paprika API + cache. Auth, fetch, validation, `sync()`→`SyncResult`. **Sole mutator of `_cache_populated`.** |

**Shipped tools:** `list_recipes`, `get_recipe`, `search_recipes`, `sync_recipes`.
**Tests:** 46 (`test_server.py` 33 + `test_config.py` 13). CI green `35517e5`.

## Stage 2 — Local Network Deployment (pieces)

- **Piece 0 — Refactor** ✅ (`24c9d45`, `090c099`)
- **Piece 1 — Config** ✅ (`35517e5`) — value-authoritative `ServerConfig`; branch-scoped port; fail-closed host.
- **Piece 2 — Transport (NEXT):** wire FastMCP Streamable HTTP from config.
  ⚠️ **Verify against FastMCP 3.2.4 first** (handoff previously said 2.8.1): whether
  `mcp.run(transport=, host=, port=)` accepts host/port kwargs, and the transport
  literal (`streamable-http` vs `http`). Fallback: set host/port via FastMCP settings.
- **Piece 3 — Auth:** bearer token, per-device keys, `hmac.compare_digest`, 401 on miss.
- **Piece 4 — Health:** unauthenticated `GET /health`.
- **Piece 5 — Tests + CI.**
- **Piece 6 — MacBook Air:** static IP → `uv sync` → `.env` → `launchd`. ⚠️ launchd doesn't inherit CWD — explicit `load_dotenv()` path.
- **Piece 7 — Claude Desktop remote config.**

**Scope note:** launchd + per-device auth + health pulled forward from Stage 6
deliberately (documented). Full hardening (OAuth 2.1) still Stage 6.

## Roadmap

| Stage | Ver | Description |
|---|---|---|
| 1 | v0.1.0 | MCP Tool Suite ✅ |
| 2 | v0.2.0 | Local Network Deployment (Pieces 0–1 done; Piece 2 next) |
| 2.5 | v0.2.0 | Local DB & Schema — SQLite, dinner history; `merge_recipes` |
| 3 | v0.3.0 | Custom Client |
| 4 | v0.4.0 | Semantic Search & Embeddings (pulled forward) |
| 5 | v0.5.0 | Recommender + Bayesian Inference |
| 6 | v1.0.0 | Cloud, App & MLOps |

**Principle:** ML before infrastructure; Stages 4–5 are the differentiators.

## Documentation system

Ownership matrix is canonical in **CLAUDE.md** (`## Document ownership`).
Doc Update Process (v2) is in `docs/SUMMARY.md`: **two-tier** — Claude Code
appends typed bullets (`SHIPPED/DECISION/LEARNED/EXTERNAL/FLAG`) to gitignored
`docs/session_update.md` as-they-happen; the project chat runs a full **batch
pass at each piece boundary**, routing bullets + harvesting its own dialogue
learnings, then Claude Code reviews + commits. Decision Log lives in SUMMARY.md.

## Concepts learned (see LEARNING_PLAN.md for full list)

Stage 1: module state, N+1, inverted index, lazy init, DRY, MCP tool anatomy,
conventional commits, pytest patterns, CI, tool design philosophy, relevance
density, README/license, git-cliff. Refactor: structural vs logical, illegal
states unrepresentable, typed return contracts, import/monkeypatch discipline.
Piece 1: value-authoritative config, pure injectable resolver, config vs domain
constants, functions-vs-classes ladder, fail-closed defaults, invest-at-boundaries,
worktrees vs. git stash.

## Recurring check-ins (every 2-3 sessions)

- Tool/LLM boundary — has it shifted? Any tools that should become LLM
  reasoning, or reasoning steps that should become tools?
- Context sizing calibration — is relevance density intuition improving?
- Architecture check-in — is "extend naturally, not replace" holding?
- Progress recalibration — honest assessment vs typical developer output
  (correct for underestimation bias).
- Scope discipline — are future-stage ideas staying flagged? Is scope widened
  deliberately + documented rather than drifting?

## Deferred (flagged — do not implement)
- Centralize test fixtures (`conftest.py`) — before Stage 2.5
- `search_recipes` expansion (ingredients/source/NL) — Stage 4
- SQLite cache; `merge_recipes`; two-way sync — Stage 2.5
- Auto-sync on client connect (Stage 3); cache/DB warming on startup (Stage 2.5)
- Windows desktop + RTX 3090 as distributed task-queue compute node (Stage 4/5)
- `PaprikaClient` class encapsulation — Stage 2.5
- Semantic search / embeddings / KG — Stage 4
- AWS EC2 manager + Route 53; MLOps dashboards — Stage 6
- Claude memory MCP / persistent-identity layer — after Paprika + Yelp/SAMHSA

## Other projects (context only)
Job Search (separate project). Yelp/SAMHSA causal-inference pipeline (planned;
builds toward the memory-MCP project).
