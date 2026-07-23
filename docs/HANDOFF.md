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

## Current state — Stage 1 complete; Stage 2 Pieces 0–2 complete; Piece 3 next

**Stack:** Python 3.13 · FastMCP 3.2.4 via `uv.lock` (pyproject floor `>=3.2.4`) ·
httpx · uv · pytest · ruff · pre-commit · GitHub Actions CI · git-cliff

**Architecture — three modules:**

| File | Responsibility |
|---|---|
| `server.py` | MCP only. Imports `os`, `typing`, `dotenv`, `fastmcp`, `config`, `paprika_client` (no `httpx`/`asyncio`). `load_dotenv()`, 4 `@mcp.tool()` defs, `_run_kwargs(config)` adapter, `__main__` resolves `ServerConfig.from_env(os.environ)` and calls `mcp.run(**_run_kwargs(config))`. |
| `config.py` | Env-driven config. Frozen `ServerConfig` + `from_env(env)`. Value-authoritative transport (unset→stdio; set→validated; unknown→`ValueError`). Host/port scoped to the `http` branch; fail-closed `127.0.0.1`. Reads only the injected mapping. |
| `paprika_client.py` | Paprika API + cache. Auth, fetch, validation, `sync()`→`SyncResult`. **Sole mutator of `_cache_populated`.** |

**Shipped tools:** `list_recipes`, `get_recipe`, `search_recipes`, `sync_recipes`.
**Tests:** 51. CI green `b41eea2`.

## Stage 2 — Local Network Deployment (pieces)

- **Piece 0 — Refactor** ✅ (`24c9d45`, `090c099`)
- **Piece 1 — Config** ✅ (`35517e5`) — value-authoritative `ServerConfig`; branch-scoped port; fail-closed host.
- **Piece 2 — Transport** ✅ (`3e21a04`, `bd5462e`) — `_run_kwargs` feeds
  `mcp.run()`; host/port omitted in stdio; contract value renamed to `http`.
- **Piece 3 — Auth (NEXT):** bearer token, per-device keys, `hmac.compare_digest`,
  401 on miss. Carries `MCP_HOST` validation + scoped security hardening, first
  `tests/integration/` suite; hands-on piece.
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
| 2 | v0.2.0 | Local Network Deployment (Pieces 0–2 done; Piece 3 next) |
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

**Planned (not yet implemented):** extract the process into `docs/DOC_PROCESS.md`
(SUMMARY is a chronological log, not a process home); split the scratchpad into
author-scoped `docs/session/{code,chat}_session_update.md` (one writer per file);
add `docs/spec/` for transient delete-on-consume specs (empty folder = boundary
processed); `docs/stages/STAGE_0N.md` for living stage plans. Memory-file
ownership moving to sole-author Claude Code (both chats propose via scratchpads),
superseding the 2026-07-17 joint-ownership decision.

## Concepts learned (see LEARNING_PLAN.md for full list)

Stage 1: module state, N+1, inverted index, lazy init, DRY, MCP tool anatomy,
conventional commits, pytest patterns, CI, tool design philosophy, relevance
density, README/license, git-cliff. Refactor: structural vs logical, illegal
states unrepresentable, typed return contracts, import/monkeypatch discipline.
Piece 1: value-authoritative config, pure injectable resolver, config vs domain
constants, functions-vs-classes ladder, fail-closed defaults, invest-at-boundaries,
worktrees vs. git stash.
Piece 2: kwargs passthrough vs. filtering, untestable-by-construction `__main__`,
signature-guard tests, framework config shadowing project config, translator
placement at module boundaries, unit vs. integration (I/O-boundary criterion),
compatibility aliases need existing consumers, append-only history vs. regenerated
views, authn/authz/tenancy as three layers.

## Recurring check-ins (every 2-3 sessions)

- Tool/LLM boundary — has it shifted? Any tools that should become LLM
  reasoning, or reasoning steps that should become tools?
- Context sizing calibration — is relevance density intuition improving?
- Architecture check-in — is "extend naturally, not replace" holding?
- Progress recalibration — honest assessment vs typical developer output
  (correct for underestimation bias).
- Scope discipline — are future-stage ideas staying flagged? Is scope widened
  deliberately + documented rather than drifting?
- **Boundary integrity** — are defined boundaries still clean, or has knowledge
  leaked across them? Audit: `config.py` framework-free? `paprika_client` still
  sole mutator of `_cache_populated`? `SyncResult` still separating what-happened
  from how-it's-phrased? Doc ownership matrix honored (no unique facts authored
  into regenerated views)? A leak is often invisible until named — the itch that
  something is "off" is the signal to look.

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
- **Multi-account access (Art + wife)** — Stage 2.5, before schema lock;
  requirement undefined, do not design ahead. Only pre-commitment: an owner key
  in the 2.5 schema/cache so single-tenant is the one-key case.
- `MCP_HOST` format validation (`ipaddress`) + first `tests/integration/` suite —
  Piece 3
- fastmcp 3.4.4 available (running 3.2.4 via `uv.lock`); signature guards fail
  loudly on upgrade. `/mcp` default endpoint — needed for Piece 7.

## Other projects (context only)
Job Search (separate project). Yelp/SAMHSA causal-inference pipeline (planned;
builds toward the memory-MCP project).
