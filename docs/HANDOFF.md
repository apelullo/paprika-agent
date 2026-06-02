# Paprika Agent — New Chat Handoff

> Paste this at the start of the first message in the next project chat.
> Provides full context so the conversation picks up exactly where it left off.

---

## Project identity

**Paprika Agent** — an MCP server connecting Claude Desktop to the Paprika
recipe manager app via its unofficial API. Public repo: github.com/apelullo/paprika-agent

**Developer:** Art Pelullo — Data Science Lead, 7 years Penn Medicine.
Strong Python fundamentals and data science background transferring into
production software engineering. Learns fast conceptually; building
implementation velocity. Tends to underestimate his own output — give
frequent honest calibrated assessments. Building in the open (LinkedIn
posts and blog planned).

**Working style:** Teach the why before the how. Succinct and scannable;
bold key info; clear next step at end of each response. Code-review mode
— explain as you go. Never ghostwrite; always teach.

**Technical conventions:**
- `uv` for all package management (never pip or venv)
- Credentials in `.env`; always verify `.gitignore` excludes it
- One milestone at a time — don't expand scope without being asked
- All tools in `server.py` call `await _populate_cache()` first (except
  `sync_recipes`, which manages the cache directly)

---

## Current state — Stage 1 complete, beginning Stage 2

**Stack:** Python 3.13 · FastMCP · httpx · uv · pytest · ruff ·
pre-commit · GitHub Actions CI · Claude Desktop (MCP client)

**Shipped tools:**
- `list_recipes` — eager cache population on first call; returns all names
- `get_recipe` — O(1) name lookup via `_name_index`; case-insensitive;
  curly apostrophe normalization via `_normalize()`
- `search_recipes` — substring + token-order-independent title search;
  empty-results message signals Stage 4 expansion coming
- `sync_recipes` — incremental (hash diff) + full refresh modes;
  cold cache guard delegates to `_populate_cache()`

**Validation:** `_validate_input_string(value, param, tool)` called in
all tools; raises `ValueError` for empty/whitespace-only or oversized
inputs; `MAX_QUERY_LENGTH = 200` module-level constant.

**Architecture:** Single `server.py`. Three module-level structures:
`_recipe_cache` (uid → full recipe data), `_name_index` (normalized name
→ uid), `_cache_populated` (bool flag — separates "never populated" from
"populated but empty"). Semaphore(5) throttles concurrent API calls.
Timeout=30 for slow API.

**Test suite:** 30 tests — unit, mocked integration, and regression tests.
Live integration tests deferred to `tests/integration/` with
`@pytest.mark.integration`; excluded from CI with `-m "not integration"`.

**Infrastructure:**
- ruff lint + format + pre-commit hooks
- GitHub Actions CI (ruff check, ruff format, pytest gates)
- PostToolUse CI poll hook (polls every 5s, max 120s after git push)
- NOTE: PostToolUse Bash matcher hooks broken in Claude Code v2.1.123+
  (issue #55889); manually poll CI after push until fixed
- README staleness check (advisory pre-commit hook, non-blocking)
- git-cliff + CHANGELOG.md (conventional commit changelog)
- MIT license, full README with Demo video (Features, Quick Start,
  Architecture, Tech Stack, Demo)
- `assets/demos/stage_01/` — demo MP4 and script; zero-padded stage folders
- Seven-file documentation system (see below)
- v0.1.0 released: https://github.com/apelullo/paprika-agent/releases/tag/v0.1.0

---

## Stage 2 — where to start

**Immediate next:** Local Network Deployment — bind server to LAN IP,
connect Claude Desktop on primary machine to server running on a second
machine. Design discussion first: MCP transport selection (stdio only
works locally; SSE or streamable HTTP for network), config separation
(dev vs. local-network), basic security considerations.

After Stage 2: Stage 2.5 (Local DB & Schema) → Stage 3 (Custom Client)
→ Stage 4 (Semantic Search — the portfolio differentiator).

---

## Full stage roadmap

| Stage | Version | Description |
|---|---|---|
| 1 | v0.1.0 | MCP Tool Suite ✅ COMPLETE |
| 2 | v0.2.0 | Local Network Deployment (compressed) |
| 2.5 | v0.2.0 | Local DB & Schema — SQLite, dinner history, dbt; `merge_recipes` tool |
| 3 | v0.3.0 | Custom Client (compressed) — minimal Python client |
| 4 | v0.4.0 | Semantic Search & Embeddings (pulled forward) |
| 5 | v0.5.0 | Recipe Recommender + Bayesian Inference |
| 6 | v1.0.0 | Cloud, App & MLOps |

**Key principle:** ML before infrastructure. Stages 4-5 are the portfolio
differentiators for DS/AI engineer roles. Cloud deployment wraps a
finished ML system, not the other way around.

---

## Documentation system — seven files

| File | Location | Owner | Purpose |
|---|---|---|---|
| `SUMMARY.md` | `docs/` | Project chat | Chronological log, concepts, decisions, TODOs |
| `LEARNING_PLAN.md` | `docs/` | Project chat | Staged learning goals with check-ins |
| `DEV_PLAN.md` | `docs/` | Project chat | Stage roadmap with version tags |
| `HANDOFF.md` | `docs/` | Project chat | New chat context handoff (this file) |
| `project_development_plan.md` | repo root | Claude Code | Operational memory — lean, current state only |
| `CLAUDE.md` | repo root | Claude Code | Architecture, conventions, workflow |
| `user_background.md` | `~/.claude/memory/` | Project chat | Career context, background, style |

**Doc update process:** Defined in `docs/SUMMARY.md` → "Doc Update Process"
section. Includes Step 0 (`session_update.md` context handoff from Claude
Code to this chat). Run at end of every meaningful session.

---

## Concepts learned (summary — see LEARNING_PLAN.md for full list)

Stage 1 completed concepts include: module-level state, N+1 query problem,
inverted index, lazy initialization, DRY, MCP tool anatomy, conventional
commits, pytest patterns (unit vs. integration, DRY in tests, call counter,
regression tests, mocked vs. live, behavior contracts not message copy),
pre-commit hooks, GitHub Actions CI, race condition awareness, tool design
philosophy for LLMs, the shifting tool/LLM boundary, relevance density,
architecture thinking, README design, MIT license, AI tool division of
labor, git-cliff and version tags, config file formats, DevOps = CI/CD in
YAML, FastMCP/Pydantic input validation, constants vs. config files,
hash-based sync, boolean sentinel flag, pytest.mark, plan mode vs. direct
execution, architectural seam awareness, engineering intuition, search
field ambiguity, tool selection ambiguity as a design cost, GitHub README
video embedding constraints, git tag management, ffmpeg basics.

---

## Recurring check-ins (every 2-3 sessions)

- Tool/LLM boundary — has it shifted? Any tools that should become LLM
  reasoning? Any reasoning steps that should become tools?
- Context sizing calibration — is relevance density intuition improving?
- Architecture check-in — is "extend naturally, not replace" holding?
- Progress recalibration — honest assessment vs. typical developer output
- Scope discipline — Stage 6 ideas staying flagged, not implemented?

---

## Deferred ideas (flagged — do not implement yet)

- `search_recipes` expansion: ingredients, source, natural language — Stage 4
- Live integration test: hash verification against Test Recipe account;
  `tests/integration/`, `@pytest.mark.integration`, `-m "not integration"` in CI
- Local SQLite persistent cache (Stage 2.5)
- `merge_recipes` tool — two-account merge with conflict resolution (Stage 2.5)
- Account similarity metric — natural Stage 5 recommender input (no stage)
- Two-way sync with deletion protection flag (Stage 2.5)
- Semantic search / embeddings / knowledge graphs (Stage 4)
- Vision models for ingredient prediction (Stage 6)
- AWS EC2 manager + Route 53 updater (Stage 6)
- MLOps + observability dashboards (Stage 6)
- Windows desktop + RTX 3090 via WSL 2 — relevant at Stage 4 (local
  embedding inference) and Stage 5 (model training)
- Claude memory MCP server / "persistent identity layer" — tripartite
  knowledge classification, Bayesian trust + decay, graph diffusion;
  deferred until after Paprika + Yelp/SAMHSA

---

## Other active projects (context only — not this chat's scope)

**Job Search project** (separate Claude project)
Resume, LinkedIn, cover letters, portfolio strategy. Career targets: Data
Science Lead, AI Engineer, Analytics Engineer, Data Architect. Portfolio
narrative: "I build data systems that think."

**Yelp/SAMHSA causal inference pipeline** (planned — after paprika Stage 1)
Serious portfolio piece: causal inference at scale, public health impact,
production data engineering. Builds hands-on intuition in entity resolution,
graph similarity, and Bayesian inference — directly relevant to the memory
MCP server project.
