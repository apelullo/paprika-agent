# Paprika Agent — New Chat Handoff

> Paste this at the start of the first message in the next project chat.
> Provides full context so the conversation picks up exactly where it left off.

---

## Project identity

**Paprika Agent** — an MCP server connecting Claude Desktop to the Paprika
recipe manager app via its unofficial API. Public repo: github.com/apelullo/paprika-agent

**Developer:** Art Pelullo — Senior Data Scientist, 7 years Penn Medicine.
Strong Python fundamentals, data science, and (ex-physics-teacher) math/geometry
intuition transferring into production software engineering. Learns fast
conceptually; building implementation velocity. Architecture intuition and scope
discipline are increasingly demonstrated strengths. Tends to underestimate his
own output — give frequent, honest, calibrated assessments. Building in the open
(LinkedIn posts and blog planned).

**Working style:** Teach the why before the how. Succinct and scannable; bold
key info; clear next step at end of each response. Code-review mode — explain as
you go. Never ghostwrite; always teach. His exact words are ground truth.

**Technical conventions:**
- `uv` for all package management (never pip or venv)
- Credentials in `.env`; always verify `.gitignore` excludes it
- One milestone at a time — don't expand scope without being asked
- Tools that read recipe data call `await paprika_client._populate_cache()` first
  and read from `paprika_client`'s cache; `sync_recipes` manages the cache via
  `paprika_client.sync()` instead

---

## Current state — Stage 1 complete; Stage 2 Piece 0 (refactor) complete; Piece 1 next

**Stack:** Python 3.13 · FastMCP · httpx · uv · pytest · ruff · pre-commit ·
GitHub Actions CI · git-cliff · Claude Desktop (MCP client)

**Architecture (post-refactor, 2026-06-25):** Two modules with an enforced boundary.

| File | Responsibility |
|---|---|
| `server.py` (84 lines) | MCP only. Imports `dotenv`, `fastmcp`, `paprika_client` (no `asyncio`/`httpx`/`os`). `load_dotenv()`, `mcp = FastMCP("Paprika")`, the 4 `@mcp.tool()` defs, `__main__`. |
| `paprika_client.py` (177 lines) | Paprika API + cache. `get_token`, `fetch_recipe`, `_normalize`, `_validate_input_string`, `_populate_cache`; `SyncResult` dataclass; `async def sync(mode)`. **Sole mutator of `_cache_populated`.** Holds `_recipe_cache`, `_name_index`, `PAPRIKA_API`, `MAX_QUERY_LENGTH`, semaphore, timeout. |

**Shipped tools:** `list_recipes`, `get_recipe` (O(1) name lookup; curly-apostrophe
normalization), `search_recipes` (substring + token-order-independent title search;
empty-results message signals Stage 4 expansion), `sync_recipes` (now a thin wrapper:
validate → `paprika_client.sync(mode)` → format; incremental hash-diff + full refresh +
cold-cache modes return a structured `SyncResult`).

**Cache invariant is now structural:** `paprika_client` exclusively owns
`_cache_populated`; `server.py` cannot touch it, so "clearing the cache must reset
the flag" is enforced by architecture, not convention.

**Test suite:** 33 tests (was 30). Sync orchestration tested on `paprika_client.sync()`
asserting `SyncResult` fields; validation tested on the `sync_recipes` wrapper; 3
formatting tests isolate the prose layer. Live integration tests deferred to
`tests/integration/` with `@pytest.mark.integration`, excluded from CI.

**Infrastructure:** ruff lint+format+pre-commit · GitHub Actions CI (ruff + pytest) ·
README staleness check (advisory) · git-cliff + CHANGELOG.md · MIT license · README
with Demo video · `assets/demos/stage_01/` · v0.1.0 released.

**Open repo TODOs (small):** README + CLAUDE.md still describe the single-file
architecture — both need updating to reflect the split (CLAUDE.md is Claude Code's
to own). Note: PostToolUse CI poll hook is broken in Claude Code v2.1.123+
(issue #55889); poll CI manually after push via `gh run list --commit <SHA>`.

---

## Stage 2 — Local Network Deployment (where to start)

**Next action: Piece 1.** Full design is locked (transport, config, security, server
machine). Detailed plan: `~/Desktop/career/claude_pro/paprika_mcp_project/paprika_stage_02_plan_*.md`.

**Architectural decisions (locked):** Streamable HTTP transport (SSE deprecated,
dropped April 2026) · env-var config with auto-detection (presence of `MCP_TRANSPORT`
selects mode; twelve-factor) · static LAN IP via router DHCP reservation (not
`0.0.0.0`, not mDNS for now) · HTTP bearer-token auth, one key per device (OAuth 2.1
deferred to Stage 6) · MacBook Air as always-on server managed by `launchd`.

**The eight pieces:**
- **Piece 0 — Refactor** ✅ DONE (`24c9d45` split, `090c099` Option B)
- **Piece 1 — Config:** `.env` schema + auto-detection logic in `server.py` (NEXT). Adds
  `MCP_TRANSPORT`/`MCP_HOST`/`MCP_PORT`/`MCP_API_KEY_*`; re-introduces `import os`.
- **Piece 2 — Transport:** wire FastMCP to start Streamable HTTP from the config.
- **Piece 3 — Auth middleware:** bearer token, per-device keys, 401 on miss. Use
  `hmac.compare_digest` for constant-time comparison.
- **Piece 4 — Health endpoint:** unauthenticated `GET /health` (bypasses auth by design).
- **Piece 5 — Tests + CI:** auth + health + auto-detection tests; gate before leaving repo.
- **Piece 6 — MacBook Air:** static IP → clone + `uv sync` → `.env` → `launchd` plist →
  firewall. ⚠️ `launchd` doesn't inherit shell env/CWD: set `WorkingDirectory` in the
  plist or pass an explicit path to `load_dotenv()`.
- **Piece 7 — Claude Desktop config:** remote MCP entry per machine; keep stdio entry too.

**Scope note:** `launchd` + per-device auth + health endpoint were deliberately pulled
forward from Stage 6 (an always-on server that survives reboot is the real Stage 2
deliverable). Documented as a deliberate decision, not scope creep. *Full* hardening
(OAuth 2.1, full service config) still deferred to Stage 6.

After Stage 2: Stage 2.5 (Local DB & Schema — SQLite; centralize test fixtures into
`conftest.py` first) → Stage 3 (Custom Client) → Stage 4 (Semantic Search — the
portfolio differentiator).

---

## Full stage roadmap

| Stage | Version | Description |
|---|---|---|
| 1 | v0.1.0 | MCP Tool Suite ✅ COMPLETE |
| 2 | v0.2.0 | Local Network Deployment (Piece 0 done; Piece 1 next) |
| 2.5 | v0.2.0 | Local DB & Schema — SQLite, dinner history, dbt; `merge_recipes` |
| 3 | v0.3.0 | Custom Client — minimal Python client |
| 4 | v0.4.0 | Semantic Search & Embeddings (pulled forward) |
| 5 | v0.5.0 | Recipe Recommender + Bayesian Inference |
| 6 | v1.0.0 | Cloud, App & MLOps |

**Key principle:** ML before infrastructure. Stages 4–5 are the portfolio
differentiators. Cloud deployment wraps a finished ML system, not the reverse.

---

## Documentation system

| File | Location | Owner | Purpose |
|---|---|---|---|
| `SUMMARY.md` | `docs/` | Project chat | Chronological log, concepts, decisions, TODOs |
| `LEARNING_PLAN.md` | `docs/` | Project chat | Staged learning goals with check-ins |
| `DEV_PLAN.md` | `docs/` | Project chat | Stage roadmap with version tags |
| `HANDOFF.md` | `docs/` | Project chat | New chat context handoff (this file) |
| `project_development_plan.md` | repo root | Claude Code | Operational memory — lean, current state |
| `CLAUDE.md` | repo root | Claude Code | Architecture, conventions, workflow |
| `user_background.md` | `~/.claude/memory/` | Project chat | Durable facts: career, background, style |
| `working_principles.md` | `~/.claude/memory/` | Project chat | Cross-project working/learning/dev philosophy |

**Doc update process:** Defined in `docs/SUMMARY.md` → "Doc Update Process". Includes
Step 0 (`session_update.md` handoff from Claude Code to this chat). Run at the end of
every meaningful session.

---

## Concepts learned (summary — see LEARNING_PLAN.md for full list)

Stage 1: module-level state, N+1 query problem, inverted index, lazy init, DRY, MCP
tool anatomy, conventional commits, pytest patterns (unit vs integration, mocked vs
live, regression tests, call-counter, behavior-contracts-not-copy), pre-commit hooks,
GitHub Actions CI, race-condition awareness, tool design philosophy for LLMs, the
shifting tool/LLM boundary, relevance density, architecture thinking, README design,
MIT license, AI tool division of labor, git-cliff + version tags, config formats,
FastMCP/Pydantic validation, constants vs config, hash-based sync, boolean sentinel
flag, architectural seam awareness, search field ambiguity, ffmpeg basics.

Refactor (2026-06-25): **structural vs logical refactor**; **make illegal states
unrepresentable** (single-owner state); **separation of concerns made provable**;
**typed return contracts** (dataclass boundary, what-happened vs how-phrased);
**import/monkeypatch discipline** (from-import only never-patched names; same missing
`global` is silent on write-only, loud on read+write); **effort vs thinking** are
separate settings; Claude Code plan mode mechanics.

---

## Recurring check-ins (every 2-3 sessions)

- Tool/LLM boundary — has it shifted? Any tools that should become LLM reasoning, or
  reasoning steps that should become tools?
- Context sizing calibration — is relevance density intuition improving?
- Architecture check-in — is "extend naturally, not replace" holding?
- Progress recalibration — honest assessment vs typical developer output (correct for
  underestimation bias).
- Scope discipline — are future-stage ideas staying flagged? Is scope being widened
  *deliberately and documented* rather than drifting?

---

## Deferred ideas (flagged — do not implement yet)

- Centralize test fixtures (factory fixture in `tests/conftest.py`) — before Stage 2.5
- Auto-sync on client connect (Stage 3); cache/DB warming on startup (Stage 2.5)
- `search_recipes` expansion: ingredients, source, natural language — Stage 4
- Local SQLite persistent cache; `merge_recipes`; two-way sync with deletion flag — Stage 2.5
- Semantic search / embeddings / knowledge graphs — Stage 4
- `PaprikaClient` class encapsulation — natural at Stage 2.5 (with `db.py`)
- Windows desktop + RTX 3090 as distributed task-queue compute node — Stage 4/5
- AWS EC2 manager + Route 53 updater; MLOps + observability dashboards — Stage 6
- Claude memory MCP server / "persistent identity layer" — after Paprika + Yelp/SAMHSA

---

## Other active projects (context only — not this chat's scope)

**Job Search project** (separate Claude project) — resume, LinkedIn, cover letters,
portfolio strategy. Targets: Senior DS, AI Engineer, Analytics Engineer, Data Architect.
Narrative: "I build data systems that think."

**Yelp/SAMHSA causal inference pipeline** (planned) — causal inference at scale, public
health impact, production data engineering; builds intuition for the memory MCP project.
