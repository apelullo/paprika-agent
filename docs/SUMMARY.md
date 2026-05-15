# Learning & Development Summary

> Chronological record of project milestones, design decisions, and concepts
> learned. Updated at the end of each working session or major milestone.
> Primary audience: Art (for reflection and blogging) and recruiters.

---

## Executive Summary

**Project:** Paprika Agent — an MCP server connecting Claude Desktop to the
Paprika recipe manager app via its unofficial API.

**Developer:** Art Pelullo, Senior Data Scientist (7 years, Penn Medicine).
Bringing strong Python fundamentals, algorithmic thinking, and data science
intuition into software engineering and production-grade development for the
first time in a structured, deliberate way.

**Stack:** Python 3.13 · FastMCP · httpx · uv · pytest · ruff · pre-commit ·
GitHub Actions · Claude Desktop (MCP client)

**What's been built:** A fully cached, tested, and CI-gated MCP server with
three working tools (`list_recipes`, `get_recipe`, `search_recipes`),
conventional commit history, and a production-grade project skeleton.

**Key strengths demonstrated so far:** Algorithmic thinking (inverted index
proposal), DRY instincts, test-first debugging, documentation discipline,
and fast conceptual transfer from data science to software engineering.

**Active growth areas:** Software architecture intuition, scope discipline,
implementation velocity, commit message *why* (not just *what*).

---

## Chronological Log

### 2026-05-15 — Project Initialization & MCP Foundations

**Commits:** `7626b3a` → `f75e887` (full history as of this writing)

#### What was built
- Project scaffolded with `uv`, Python 3.13, FastMCP
- `list_recipes` implemented: authenticates with Paprika API, fetches all
  recipe IDs, fetches full data per recipe (N+1 calls), returns name list
- Identified N+1 API call problem; refactored to module-level in-memory cache
  (`_recipe_cache`) populated once on first tool call (`_populate_cache()`)
- Added `_name_index` (lowercase name → uid) for O(1) name lookups —
  **Art's idea**, proposed before Claude Code could suggest the naive loop
- `get_recipe` implemented: case-insensitive exact name match via `_name_index`
- `_normalize()` helper added: lowercases + normalizes curly apostrophes
  (`\u2018`, `\u2019`) to straight quotes for consistent matching
- `search_recipes` implemented: substring + token-order-independent matching
  across recipe titles
- Apostrophe encoding bug caught and fixed via manual testing
- Descriptive error returns added (`dict | str`) instead of silent `None`
- Full pytest suite: unit tests for pure functions, monkeypatched cache/tools,
  async integration tests with `pytest-httpx`
- ruff lint + format + pre-commit hooks configured
- GitHub Actions CI: ruff check, ruff format, pytest gates on push + PR
- PostToolUse hook: polls GitHub Actions every 5s (max 120s) to report CI
  results in terminal after every push — Art's solution to race condition
  between push and CI spin-up
- `CLAUDE.md` written: architecture, caching strategy, commit workflow,
  test/run instructions for Claude Code
- `project_development_plan.md` written: current state, milestones, roadmap
- `docs/` folder created with SUMMARY, LEARNING_PLAN, DEV_PLAN

#### Concepts learned
- **Module-level state** — Python equivalent of file-scoped globals in C;
  variables declared at the top of a `.py` file persist for the server's
  lifetime
- **N+1 query problem** — fetching a collection then looping to fetch each
  item individually; solution is eager population into a cache
- **Inverted index** — secondary dict keyed by a lookup field (name → uid)
  enabling O(1) lookup without scanning the full collection; same concept
  underlying database indexes
- **Lazy initialization** — populate on first use, not at import time;
  `if _recipe_cache: return` guards the expensive operation
- **DRY (Don't Repeat Yourself)** — extracting shared logic into a helper
  (`_populate_cache`) so multiple tools share one implementation
- **Incremental sync pattern** — set difference (`new - cached`) to find
  only what's missing; symmetric difference for two-way sync
- **MCP tool anatomy** — `@mcp.tool()` decorator, async functions, input
  schemas inferred from type annotations, docstrings as LLM-readable contracts
- **Conventional commits** — `feat:`, `fix:`, `docs:`, `ci:`, `test:`,
  `chore:` prefixes; tight scope per commit; *what* + *why* in message body
- **pytest patterns** — `monkeypatch` for module-level state, `pytest-httpx`
  for async HTTP mocking, `@pytest.mark.anyio` for async tests
- **Pre-commit hooks** — client-side lint gates that run before every commit
- **GitHub Actions CI** — push/PR triggered workflows; `uv sync` for
  reproducible installs; ruff + pytest as gates
- **Race condition (CI polling)** — `gh run watch` could miss a run that
  finished before the watch started; solved with a poll loop + timeout
- **README as living document** — public repo README must reflect current
  reality; staleness signals inexperience to senior engineers
- **CLAUDE.md** — project-level instruction file read by Claude Code at
  session start; encodes architecture, conventions, and workflow

#### Design decisions made
- Cache keyed by `uid` (not name) — uid is stable, names can change
- `_name_index` separate from `_recipe_cache` — separation of concerns;
  lookup index vs. data store
- Single `server.py` for now — appropriate for current scale; split into
  modules when second file is warranted (trigger: mypy addition)
- `asyncio.Semaphore(5)` — throttles concurrent Paprika API calls to avoid
  overwhelming a slow third-party server
- `httpx.AsyncClient(timeout=30)` — generous timeout for slow API
- `dict | str` return type on tools — honest about error states; LLM reads
  the string and handles it gracefully

---

## Open Items & Reminders

### TODO (immediate)
- [ ] Add MIT license to repo root
- [ ] Add Demo, Quick Start, Architecture sections to README
- [ ] Add README staleness check to pre-commit or CI
- [ ] Review and tighten commit message *why* on non-obvious changes
- [ ] Add `git-cliff` for automated CHANGELOG generation

### Deferred ideas (flagged, not forgotten)
- Local SQLite persistent cache — eliminates cold-start API calls on restart
- Two-way sync with deletion flag ("safe sync only" mode — wife-approved)
- Incremental sync: set diff on ID list to find new/deleted recipes
- Timestamp-based update detection on set intersection
- `search_recipes` expansion: ingredients, prep instructions, source, nutrition
- Semantic search / embeddings / knowledge graphs (Stage 6)
- Vision models for image-based ingredient prediction (Stage 6)
- AWS EC2 "manager" server with Route 53 A-record updater (Stage 4-5)
- MLOps + observability dashboards (Stage 6)
- Dataset section in README (add back when analytics features exist)

### Resources to pursue
- *Designing Data-Intensive Applications* — Kleppmann (systems design)
- `git-cliff` or `commitizen` — automated changelog from conventional commits
- ADRs (Architecture Decision Records) — when project architecture matures
- TDD formalization — test-first as a discipline, not just a habit
