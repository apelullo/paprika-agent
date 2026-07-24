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

**What's been built:** A fully tested, CI-gated, and publicly released MCP
server with four working tools (`list_recipes`, `get_recipe`,
`search_recipes`, `sync_recipes`), a demo video, conventional commit
history, and a production-grade project skeleton. Tagged and released
as v0.1.0.

**Key strengths demonstrated so far:** Algorithmic thinking (inverted index
proposal), DRY instincts, test-first debugging, documentation discipline,
and fast conceptual transfer from data science to software engineering.

**Active growth areas:** Software architecture intuition, scope discipline,
implementation velocity, commit message *why* (not just *what*).

---

## Chronological Log

### 2026-05-15 — Project Initialization & MCP Foundations

**Commits:** `7626b3a` → `f75e887`

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

### 2026-05-15 — Planning Docs & Hook Fix

**Commits:** `20c5c56` → `22b1657`

#### What was built
- `docs/` folder created with three human-facing planning documents
- `CLAUDE.md` Planning section updated with ownership boundary
- PostToolUse hook bug identified and fixed

#### Concepts learned
- **Shell glob matching in hook `if` conditions** — `*` matches any sequence;
  leading `*` required to match a non-prefix substring
- **Hook silent failure mode** — mismatched `if` condition produces no error;
  invisible until noticed by absence of expected output

#### Design decisions made
- `docs/` is human-facing and write-protected from Claude Code unless
  explicitly asked

### 2026-05-16 — README, License, AI Workflow, Tool Design Philosophy & Roadmap Restructure

**Commits:** `8b58109` → `8c6c390`

#### What was built
- MIT license added (`LICENSE`)
- README: Features, Quick Start, Architecture sections added/updated
- CI gap closed: ruff lint + format checks added to `ci.yml`
- README staleness check: pre-commit hook (`scripts/check_readme_staleness.sh`)
  warns when `server.py` is modified without `README.md`; non-blocking (exit 0)
- `docs/DEV_PLAN.md` restructured: stage order revised to prioritize ML
  before infrastructure (Stage 2.5 added, Stage 4 = semantic search,
  Stage 5 = recommender, Stage 6 = cloud/app/MLOps)
- `~/.claude/memory/user_background.md` updated: career context, target
  roles, growth areas, building-in-the-open intent
- `~/.claude/CLAUDE.md` updated: added instruction to not re-show diff
  after user confirms — prevents hesitation loop in Claude Code
- Doc update process formalized in `SUMMARY.md`
- Six-file documentation system fully synchronized

#### Concepts learned
- **MIT license** — most permissive open source license; absence signals
  inexperience; required before public promotion
- **Quick Start design** — prerequisites → install → configure → run →
  connect; zero to working in under 5 minutes with no guessing
- **Architecture vs. systems thinking** — "did you think about tomorrow
  while building today?"; intentionality about change, not just efficiency;
  architectural restraint (what you leave out) is as important as decisions made
- **Division of labor between AI tools** — project chat holds learning arc
  and continuity; Claude Code holds execution context; execute where the
  context lives; copy-paste handoffs introduce errors
- **Tool design philosophy for LLMs** — four reasons tools beat LLM
  reasoning for retrieval: context scarcity, determinism, composability,
  latency/cost at scale
- **The shifting tool/LLM boundary** — not fixed; reassess periodically;
  current rule: tools for deterministic lookup, external state, computation,
  or data too large for context
- **Relevance density** — context quality = signal-to-token ratio, not raw
  size; optimizing for relevance density is a recurring design concern
- **Context sizing intuition** — not a fixed threshold; calibrate iteratively
- **Edge cases: reasoning as a tool** — chain-of-thought as structured
  scratchpad; reasoning/synthesis not categorically exempt from tools
- **ML before infrastructure** — for DS/AI engineer portfolio, ML is the
  differentiator; infrastructure wraps it, not the reverse
- **`/context` vs `/clear` in Claude Code** — `/context` shows token usage
  breakdown by category (useful diagnostic); `/clear` resets conversation
  context; restarting Claude Code alone does not clear context fully
- **Pre-commit hook design** — `exit 0` makes a hook advisory (warns but
  never blocks); `--cached` checks staged files only, not working tree;
  `always_run: true` fires regardless of which files changed
- **Claude Code hesitation loop** — re-showing diffs after confirmation is
  a context/instruction conflict; solved by explicit global `CLAUDE.md` rule

#### Design decisions made
- Roadmap reordered: Stage 2 compressed, Stage 2.5 (local DB) added,
  Stage 4 = semantic search, Stage 5 = recommender, Stage 6 = cloud/ops
- Portfolio narrative rewritten to target DS, AI engineer, analytics
  engineer roles explicitly
- Doc update process formalized as a named, repeatable workflow
- README staleness check implemented as advisory pre-commit (Option A)
  rather than blocking CI (Option B) — solo project, discipline sufficient

### 2026-05-21 — Input Validation, Test Philosophy & Doc Update Process Redesign

**Commits:** `60f4650` → `16267fc`

#### What was built
- `MAX_QUERY_LENGTH = 200` module-level constant added after `PAPRIKA_API`
- `_validate_input_string(value, param, tool) -> None` helper added after
  `_normalize()` — raises `ValueError` with `[tool] 'param' must be a
  non-empty string.` or `[tool] 'param' exceeds 200 characters.`
- Called in `get_recipe` (param="name") and `search_recipes` (param="query")
  as first line after `_populate_cache()`
- Redundant `if not tokens: return "Please provide a search query."`
  guard removed from `search_recipes` — now covered by validation
- Function renamed during session: `_validate_query_string` →
  `_validate_input_string` ("query" implied search-specific; function is
  general-purpose)
- Unicode curly apostrophe characters in `_normalize` were accidentally
  corrupted during editing — caught via git diff, diagnosed by comparing
  hex code points, restored from HEAD
- Test suite grew from 15 → 20 tests:
  - `test_search_recipes_empty_query` updated to expect `ValueError`
    instead of string return (contract change)
  - `test_get_recipe_empty_name` — empty string raises `ValueError`
  - `test_get_recipe_name_too_long` — name > 200 chars raises `ValueError`
  - `test_search_recipes_query_too_long` — query > 200 chars raises `ValueError`
  - `test_populate_cache_already_warm` — verifies no HTTP calls on warm cache
  - `test_validate_input_string_whitespace_only` — unit test for helper
    directly; `_validate_input_string` imported explicitly
- Doc update process redesigned: Step 0 added (`session_update.md` handoff
  from Claude Code to this chat); `HANDOFF.md` ownership moved to this
  chat and integrated into Step 1; Step 3 revised to close feedback loop

#### Concepts learned
- **FastMCP/Pydantic input validation** — FastMCP uses Pydantic v2 to
  validate tool inputs from type annotations before the function body runs;
  type coercion handles wrong types (e.g. `123` → `"123"`); semantic
  errors (empty string, oversized input) require manual guards
- **Unit vs. integration tests** — unit tests verify logic of a single
  function; integration tests verify wiring (that the function is called
  from the right place); distinct concerns, not redundant coverage
- **DRY in tests** — test the helper's logic once directly; test each
  caller once for wiring; avoid re-testing logic through every caller
- **Constants vs. config files** — module-level constant is correct when
  the value is environment-invariant; promote to config/env var only when
  it needs to differ across environments or be user-configurable
- **`ValueError` in FastMCP** — caught by FastMCP and surfaced as a
  structured error message to the LLM, not a raw traceback; LLM sees
  something actionable and can self-correct
- **Validation order tradeoff** — validation after `_populate_cache()`
  means a cold cache is warmed before bad input is rejected; functionally
  fine (cache is warm for all subsequent calls); could be before for
  maximum efficiency, but not worth changing at this scale

#### Design decisions made
- `_validate_input_string` chosen over `_validate_query_string` — more
  honest about scope; function validates any string param, not just queries
- `MAX_QUERY_LENGTH = 200` as module-level constant — fixed ceiling for
  abuse protection, not a semantic boundary; dynamic calculation
  (e.g. `longest_name * 2`) rejected: creates moving validation boundary,
  surprising behavior if recipes are deleted
- `sync_recipes` scoped to single-account — incremental ID set diff +
  full refresh as escape hatch; named distinctly from future `merge_recipes`
- `merge_recipes` placed in Stage 2.5 — two-account merge requires
  persistent DB to make conflict resolution tractable; conflict strategies:
  keep both, last-write-wins via timestamp, manual override
- Account similarity metric flagged as future idea (no stage assigned) —
  aggregate distance across two recipe collections; natural Stage 5 input
- Doc update process redesigned: Step 0 (`session_update.md`) is the
  key — enables full context cascade from Claude Code → this chat → Claude
  Code; `HANDOFF.md` owned by this chat, not Claude Code

### 2026-06-02 — search_recipes Scope Decision, Demo, v0.1.0 Release

**Commits:** `fa6f327` → `3906d63`

#### What was built
- `search_recipes` empty-results message updated: now returns
  `f"No recipes found matching '{query}' in recipe titles. Ingredient,
  source, and natural language search are coming in a future update.
  Try a different title keyword or a more specific term."` — honest
  about current limitations, sets user expectations without clutter
- `assets/` directory structure created:
  - `assets/demos/stage_01/` — stage-specific demo material
  - `assets/images/` — project-wide images
  - `assets/archive/` — gitignored; for working files and drafts
  - `.gitignore` updated: `assets/archive/`, `assets/**/*.mov`
- Demo files added:
  - `assets/demos/stage_01/paprika_demo_stage01_15fps.mp4` — compressed
    from 11MB to 3MB via `ffmpeg -vcodec libx264 -crf 28 -preset slow`
  - `assets/demos/stage_01/paprika_demo_stage01_script.docx`
- README Demo section added: `<video>` tag with GitHub user-attachments
  CDN URL (the only src format GitHub's README sanitizer allows for
  inline video playback)
- v0.1.0 tagged and released:
  - `gh release create v0.1.0` created the tag prematurely at `09faa48`
  - Tag moved to final HEAD after demo commits: remote tag deleted,
    CHANGELOG regenerated and committed (`3906d63`), retagged at HEAD,
    GitHub release republished from Draft state
  - Final release: https://github.com/apelullo/paprika-agent/releases/tag/v0.1.0

#### Design decisions made
- **`search_recipes` expansion deferred to Stage 4** — without semantic
  understanding, multi-field search adds noise not signal; the LLM cannot
  reliably distinguish title match from ingredient match from source match;
  source search is not deterministic either ("cookie and kate" vs
  "cookieandkate.com" vs "Garlic & Zest"); tool selection ambiguity
  between `search_recipes` and a hypothetical `find_recipes_by_source`
  is worse than the search problem itself; Stage 4 semantic search solves
  all of this correctly and without clutter
- **Empty-results message is a bridge, not a fix** — honest signal to
  the user that the limitation is known and being addressed; does not
  fire on every search, only on zero results
- **Test for empty-results message** — `test_search_recipes_no_match`
  asserts `"No recipes found"` only, not the specific hint text;
  deliberate: the hint copy will change in Stage 4 and a test that
  asserts specific message wording would produce false negatives on
  improvement; test behavior contracts, not message copy
- **Asset directory structure:** zero-padded stage folders
  (`stage_01`, `stage_02`) for correct alphabetical sort at 10+ stages;
  `assets/archive/` gitignored for working files; `*.mov` globally
  ignored under `assets/`
- **ffmpeg installed** (`brew install ffmpeg`) — available for future
  video/audio processing; compression target was crf 28, no explicit
  size target set
- **GitHub video embedding constraint documented** — three approaches
  tried before one worked: relative path (stripped), release download
  URL (stripped), drag-drop via GitHub issue editor to get
  `user-attachments/assets/UUID` URL (works); 10MB issue attachment
  limit required compression first; this is a one-time GUI step per demo

#### Concepts learned
- **Search system design — field ambiguity** — without semantic
  understanding, you can't distinguish what kind of thing the user is
  searching for; "garlic" could be a title word, an ingredient, or a
  source name; naive multi-field search returns all three and is
  unpredictable; the right solution is semantic search, not more fields
- **Tool selection ambiguity as a design cost** — if the LLM has to
  guess between two tools based on fuzzy signals, the complexity moves
  from the implementation into the tool boundary, which is worse because
  it's invisible and harder to debug
- **Test behavior contracts, not message copy** — assert the invariant
  ("no match returns a non-empty string indicating nothing was found"),
  not the specific wording; wording that's designed to change produces
  false negatives if tested literally
- **GitHub README video embedding** — `<video>` tags only render with
  `user-attachments/assets/` URLs; relative paths and release download
  URLs are stripped by GitHub's sanitizer; the only reliable method is
  drag-drop upload via the GitHub issue editor
- **`brew install --cask` vs `brew install`** — `--cask` is for GUI
  Mac applications; `brew install` is for CLI tools
- **Git tag management** — `git push origin --delete v0.1.0` deletes a
  remote tag; `gh release edit v0.1.0 --draft=false` publishes a Draft
  release; `gh release list` shows release state
- **ffmpeg compression** — `libx264 -crf 28 -preset slow`; CRF
  (Constant Rate Factor) controls quality/size tradeoff; lower = better
  quality, larger file; 28 is a reasonable default for screen recordings

### 2026-05-22 — sync_recipes, Cache Flag, Bug Fixes & Test Suite

**Commits:** `9db09f5` → `7e9e0af`

#### What was built
- `sync_recipes` tool — two modes:
  - `incremental` (default): fetches uid/hash pairs from API, diffs against
    `_recipe_cache` by hash, fetches only new/changed recipes, removes
    deleted ones from both `_recipe_cache` and `_name_index`; handles
    name changes by removing stale `_name_index` entry before updating
  - `full`: resets `_cache_populated`, clears cache and index, calls
    `_populate_cache()`
  - Cold cache guard: delegates to `_populate_cache()` if not yet populated
  - `global _cache_populated` hoisted to top of function (Python requires
    `global` before any reference, not just before assignment)
  - `strict=True` on `zip(to_fetch, fetched)` — surfaces length mismatch
    loudly if `asyncio.gather` assumption ever breaks
- `_cache_populated: bool = False` module-level flag — replaces
  `if _recipe_cache:` guard in `_populate_cache()`; correctly handles
  zero-recipe accounts where the old guard caused a re-fetch on every call
- README updated: `sync_recipes` bullet in Features; `_cache_populated`
  sentence in Architecture
- Test suite grew from 20 → 30 tests; 10 new `sync_recipes` tests:
  cold cache, incremental add/edit/unchanged/delete/rename, full refresh,
  full refresh zero-recipe, flag reset regression, invalid mode
- `test_populate_cache` apostrophe regression fixed: assertion now uses
  `{_normalize("Mom's Soup"): "uid-1"}` so expected key goes through same
  transform as actual — encoding of source literal becomes irrelevant
- `test_sync_recipes_invalid_mode` match pattern fixed: uses
  `match=r"\[sync_recipes\].*must be"` to avoid apostrophe encoding issues
  entirely

#### Bugs caught and fixed
- **Full refresh no-op bug** — after adding `_cache_populated`, full
  refresh cleared `_recipe_cache`/`_name_index` but didn't reset the flag,
  so `_populate_cache()` was a no-op and cache was left permanently empty;
  fix: reset `_cache_populated = False` before calling `_populate_cache()`
- **Zero-recipe account re-fetch bug** — `if _recipe_cache:` guard in
  `_populate_cache()` treated empty cache as cold, causing re-fetch on
  every tool call for accounts with no recipes; fix: `_cache_populated`
  flag tracks population state independent of cache contents
- **Curly apostrophe regression in tests** — Edit call introduced U+2019
  into test assertion; invisible to human eye, caught by comparing hex
  bytes; fix: use `_normalize()` in assertions so encoding of source
  literal is irrelevant

#### Concepts learned
- **Hash-based sync** — content fingerprint (`hash`) detects edits without
  timestamp; more reliable than timestamps for "did this change" questions;
  a hash change means content changed, regardless of when
- **Boolean sentinel flag** — `_cache_populated` separates "never populated"
  from "populated but empty"; the old `if _recipe_cache:` guard conflated
  two distinct states; sentinel is the clean fix
- **`asyncio.gather` behavior** — all results arrive together when the last
  coroutine finishes; use `asyncio.as_completed()` if per-result processing
  is needed before all are done
- **`strict=True` on `zip()`** — raises `ValueError` if iterables have
  different lengths; surfaces logic errors loudly rather than silently
  truncating
- **Regression tests** — written specifically to verify a bug that was
  found and fixed doesn't return; `test_sync_recipes_full_refresh_repopulates
  _after_flag_reset` is a regression test for the full refresh no-op bug
- **`pytest.mark`** — pytest's tagging system; `@pytest.mark.anyio` changes
  *how* a test runs (async event loop); `@pytest.mark.integration` is a
  custom mark that changes *when/where* it runs (excluded from CI); marks
  can be stacked
- **Mocked vs. live integration tests** — mocked tests intercept all HTTP
  calls and run safely in CI; live tests call real external systems, require
  credentials, and run manually or in a separate pipeline; `tests/integration/`
  directory convention with `-m "not integration"` in CI to exclude them
- **Call counter pattern in tests** — monkeypatching with a list that
  appends on each call; `assert fetch_calls == []` is more explicit and
  debuggable than relying on `httpx_mock` to error on unexpected requests
- **Plan mode vs. direct execution in Claude Code** — use plan mode when
  the prompt leaves meaningful decisions to Claude Code, touches 3+ files,
  or introduces a new pattern; skip it when the prompt fully specifies
  behavior and follows existing patterns
- **Architectural seam awareness** — `server.py` currently does two things:
  MCP server + Paprika API client; the seam is visible but not yet painful;
  Stage 2.5 will force the split into `server.py`, `paprika_client.py`,
  `db.py`
- **Reading code you didn't write** — parallel review of `server.py` and
  `test_server.py` during implementation builds code-reading intuition;
  transfers directly to code review, debugging, and onboarding
- **Engineering intuition** — sensing a seam or design tension before being
  able to articulate it formally is a sign of developing architectural taste;
  the feeling surfaces before the vocabulary does

#### Design decisions made
- `_cache_populated` contract: any future code path that clears
  `_recipe_cache`/`_name_index` must also reset `_cache_populated = False`;
  currently only `sync_recipes` full refresh does this; Stage 2.5 will
  replace the caching mechanism with persistent storage
- Zero-recipe account messaging deferred — `list_recipes`, `get_recipe`,
  `search_recipes` return generic "not found" for empty accounts,
  indistinguishable from a real miss; accepted as low-priority edge case
- Hash assumption: Paprika hash field covers all recipe content; to be
  verified by live integration test against Test Recipe account; not
  blocking Stage 1 completion
- Live integration tests: will live in `tests/integration/`, use
  `@pytest.mark.integration`, be excluded from CI with
  `-m "not integration"`; written when hash verification test is built
- `sync_recipes` race conditions noted but not fixed: recipe created between
  list fetch and detail fetch is missed until next sync (unavoidable);
  concurrent `sync_recipes` calls are safe (mutation phase has no await
  points); deleted recipe between list and detail fetch handled by
  `if recipe is None: continue`

### 2026-05-19 — git-cliff, Version Tags & Changelog Workflow

**Commits:** `53d8755` → current

#### What was built
- `git-cliff` added as dev dependency (`git-cliff==2.13.1`)
- `cliff.toml` configured: groups commits by type, body/footer included,
  conventional commit format, sorts oldest-first
- `CHANGELOG.md` generated from full commit history — all commits land in
  `[Unreleased]` until version tags are introduced
- `docs/DEV_PLAN.md` updated: Version Tag Map added (v0.1.0 → v1.0.0),
  target tag added to each stage header, CI automation trigger documented
  for Stage 4-5, Stage 1 status bumped to ~95%
- `docs/SUMMARY.md` + `docs/LEARNING_PLAN.md` synced to reflect all
  completed Stage 1 items

#### Concepts learned
- **git-cliff** — generates `CHANGELOG.md` from conventional commit history;
  config-driven (cliff.toml); output quality directly reflects commit
  message discipline
- **Version tags vs. CI wiring** — two separate concerns; tagging is manual
  and immediate (one command per stage completion); CI automation of
  changelog regeneration is deferred to Stage 4-5 when release cadence
  warrants the overhead
- **Version tag workflow (manual, until Stage 4-5):**
  ```bash
  git tag v0.1.0
  git push origin v0.1.0
  uv run git-cliff --output CHANGELOG.md
  git add CHANGELOG.md && git commit -m "chore: update changelog for v0.1.0"
  git push
  ```
- **`[Unreleased]` vs versioned sections** — without tags, all commits land
  in one bucket; tags create named release sections grouping commits between
  them; the changelog becomes a versioned history, not a running log
- **CI tag trigger** — `on: push: tags: ['v[0-9]*']` fires only on tag
  pushes, not every commit; avoids changelog noise on small changes
- **Config file formats recap** — `.toml` (declarative, Python-friendly,
  used for pyproject.toml + cliff.toml), `.yaml` (declarative, DevOps-
  friendly, used for GitHub Actions), `.json` (strict, used for Claude
  Desktop config), `.env` (simple KEY=VALUE, used for secrets)
- **DevOps = CI/CD configured in YAML** — the GitHub Actions workflow
  is a DevOps task; declarative description of what runs, when, and where

#### Design decisions made
- `CHANGELOG.md` committed and tracked (not gitignored) — it's a portfolio
  artifact and living document
- git-cliff run manually between tags until Stage 4-5 CI automation
- Version tag map established: v0.1.0 (Stage 1) → v1.0.0 (Stage 6)
- Stages 2 + 2.5 share a tag (`v0.2.0`) — logical unit of work

---

### 2026-06-25 — server.py Refactor: Structural Split (A) + Logical Extraction (B)

**Commits:** `24c9d45` → `090c099`

> The seam flagged on 2026-05-22 ("server.py does two things... visible but not
> yet painful") became an enforced architectural boundary. Two pieces:
> **A built the boundary (structural); B sealed it (logical).**

#### Piece 0 (A) — Structural refactor

**What was built**
- Split `server.py` → `server.py` + `paprika_client.py`. Constants, the three cache
  globals, and five helpers (`get_token`, `fetch_recipe`, `_normalize`,
  `_validate_input_string`, `_populate_cache`) moved **verbatim**; zero logic change.
  `server.py` references everything via the `paprika_client.` prefix.
- Test rewrite: blanket `server.` → `paprika_client.` (86 sites) + 3 bare call sites
  re-qualified. New import block: from-import only never-patched names (`PAPRIKA_API`,
  `_normalize`, `_validate_input_string`); `_populate_cache` and `fetch_recipe` left
  module-referenced because they are monkeypatched.
- `global _cache_populated` removed from `sync_recipes`; the full-refresh flag write
  became `paprika_client._cache_populated = False`.
- Gate: **30 passed**, ruff clean. CI `28186455401` → success.

**Contribution to separation of concerns / state ownership**
- *SoC:* established the **file boundary** — MCP-protocol concerns (`server.py`) vs
  Paprika-API/cache concerns (`paprika_client.py`). Built the two rooms.
- *State ownership:* relocated cache state into `paprika_client`, but ownership was
  **not yet exclusive** — `sync_recipes` still reached across to write the flag.
  Moved the state; did not yet seal it.

**Risk noted:** no test exercises the relocated flag write (every full-refresh test
mocks `_populate_cache`), so a bug — bare `_cache_populated = False` silently becoming
a dead function-local — would pass green. Verified correct **by eye**, not by tests.

#### Option B — Logical refactor

**What was built**
- Extracted sync orchestration into `paprika_client.sync(mode) -> SyncResult`
  (cold/full/incremental logic moved out of `sync_recipes`, un-prefixed, with
  `global _cache_populated` restored and structured returns).
- `SyncResult` dataclass: `mode` / `total` / `added` / `updated` / `removed`.
- `sync_recipes` reduced to **validate → delegate → format**: validates the mode
  (validation stays in the wrapper), calls `sync()`, branches on `result.mode` to
  build the same prose. Output **byte-identical** (runtime-verified, em-dash included).
  Removed `import asyncio` and `import httpx` from `server.py`.
- Tests: 9 orchestration tests retargeted onto `paprika_client.sync()` asserting
  `SyncResult` fields (renamed `test_sync_recipes_*` → `test_sync_*`); 1 validation
  test kept on the wrapper; 3 new formatting tests mock `sync` to isolate the prose
  layer. **30 → 33 tests.**
- Gate: **33 passed**, ruff clean. CI `28201385695` → success.

**Contribution to separation of concerns / state ownership**
- *SoC:* **completed** the boundary. `server.py` owns only MCP concerns (tools +
  presentation); `paprika_client` owns all API orchestration. Proof: `server.py` no
  longer imports `asyncio`/`httpx` — the MCP layer does not know HTTP exists. Also
  split *what happened* (`SyncResult`) from *how it is phrased* (formatting).
- *State ownership:* `paprika_client` is now the **sole mutator** of `_cache_populated`
  — ownership is exclusive and **structural**. `server.py` cannot touch the flag, so
  the cache invariant is enforced by architecture, not convention. The missing-`global`
  failure mode flipped from **silent (A)** to **loud `UnboundLocalError` (B)**, caught
  by all 9 orchestration tests.

**One-line synthesis:** A built the boundary; B sealed it. Structural separation
created the rooms; logical extraction made state ownership exclusive and enforced.

#### Concepts learned
- **Import/monkeypatch discipline (precise rule)** — from-import only names never
  monkeypatched (constants, pure helpers); reference via the module anything that is
  patched, so the lookup resolves on the module dict at call time and the patch shows
  through. The same principle the production code follows.
- **Same error, opposite detectability** — a missing `global` is *silent* when the
  function only writes the flag (dead function-local; A) but *loud* when it also reads
  it (`UnboundLocalError`; B). Read+write makes the invariant self-checking.
- **Make illegal states unrepresentable** — moving sole ownership of `_cache_populated`
  into one module converts a remembered rule ("clearing the cache must reset the flag")
  into a boundary the code enforces. Correctness as architecture, not discipline.
- **Typed return contracts** — a dataclass (`SyncResult`) separates *what happened*
  (structured data, client concern) from *how it is phrased* (presentation). Tests
  assert `result.added == 1`, not `"1 added" in result` — decoupled from copy, and the
  on-ramp to typed models (Pydantic / SQLite rows) at Stage 2.5+.
- **Structural vs logical refactor** — A moved files (boundary); B moved logic across
  the boundary (sealing). Distinct operations, distinct risk profiles.

#### Design decisions made
- **Option A then B, B immediately after** — A is the minimal safe move (pure file
  split, clean git checkpoint); B completes separation. Doing B now rather than at
  Stage 2.5 because it is the natural completion of the same refactor and yields the
  clean MCP-only surface that Pieces 1–3 bolt onto.
- **`SyncResult` as a dataclass, not a dict** — typed/documented contract, fail-fast
  on field errors, on-ramp to schema modeling at 2.5. Small practical gain today; the
  point is establishing the pattern while it is cheap.
- **Validation stays in `sync_recipes`, not duplicated into `sync()`** — `sync()`
  trusts a valid mode per its documented precondition; the wrapper guards the boundary.
- **Stage 2 scope deliberately widened** — launchd + per-device auth pulled forward
  from Stage 6, and the `server.py` split pulled forward from Stage 2.5 into Piece 0.
  Documented as a deliberate decision (see DEV_PLAN), not scope creep.

#### Process / tooling
- **Doc-update timing** — run **one** doc pass after B, not between A and B: A is a
  deliberately transitional state that B is about to undo; documenting it then redoing
  it is waste. The git commit (not the doc update) is the rollback checkpoint. Capture
  A and B as labeled sub-entries in one session block.
- **effort vs thinking are separate settings** — effort = thoroughness budget; thinking
  = visible reasoning trace. Use both for architecture/design and debugging; neither for
  mechanical work. `/effort high` at the start of complex Claude Code sessions. Plan
  mode = Shift+Tab ×2 (or `/plan`); read-only enforced at the tool level; approve the
  plan to execute; resets to off on restart.

### 2026-07-16 — Stage 2 Piece 1: Config + Transport Auto-Detection · Doc-Process v2

**Commits:** `35517e5` (Piece 1) · `83e009b` (doc-process v2 install)

#### What was built
- `config.py` — new third module. Frozen `ServerConfig` dataclass +
  `ServerConfig.from_env(env: Mapping)`. Value-authoritative transport
  selection: `MCP_TRANSPORT` unset → stdio; set → validated against
  `{stdio, streamable-http}`; unknown/empty → `ValueError`. Host/port
  resolution + validation scoped to the streamable-http branch only;
  stdio never inspects `MCP_HOST`/`MCP_PORT`. Fail-closed default host
  `127.0.0.1`. `from_env` reads only the injected mapping, never `os.environ`.
- `server.py` — reintroduced `import os`; `__main__` resolves
  `ServerConfig.from_env(os.environ)` (unused until Piece 2 wires transport).
- `.env.example` — full env-var contract (creds + MCP_* + reserved MCP_API_KEY_*).
- `.gitignore` — `.env*` + `!.env.example` (fail-safe).
- `tests/test_config.py` — 12 tests (13 cases; port parametrized x2). Suite 33 → 46.
- CLAUDE.md — Architecture updated to three modules; ownership matrix added.
- Doc Update Process v2 installed (SUMMARY + CLAUDE.md ownership section).

#### Concepts learned
- **Value-authoritative config** — unset→default, set→validate, unknown→raise;
  beats presence-only, which lets `MCP_TRANSPORT=stdio` silently run HTTP.
- **Pure injectable resolver** — `from_env(env)` on an injected mapping is
  unit-testable with plain dicts, no `os.environ` monkeypatching. Extends the
  refactor's import/monkeypatch discipline.
- **Alternative-constructor idiom** — `ServerConfig.from_env` classmethod
  (the `datetime.fromisoformat` family); vs a free function is stylistic only.
- **Config record vs data record** — `ServerConfig` (validated + factory) and
  `SyncResult` (pure data) are the same typed-contract-at-a-boundary family,
  different jobs.
- **Fail-closed defaults** — `127.0.0.1` over `0.0.0.0`; a misconfigured `.env`
  fails unreachable, not wide-open.
- **Configuration vs domain constants** — `config.py` owns what "varies by
  environment"; domain constants (`PAPRIKA_API`, `MAX_QUERY_LENGTH`) stay by
  use. Split on cohesion / rule-of-three / import-graph, not line count.
- **Functions vs classes (the ladder)** — pure fn → typed record at a boundary
  (NOT a state question) → stateful class owning invariants → hierarchy/Protocol
  (rarest). Inheritance is the tail, not the dog.
- **Invest at boundaries, defer internals** — the disciplined-investment tell:
  hardening a seam others depend on (contract, interface, test seam) vs buffing
  a cheap-to-change internal.
- **Worktrees vs. `git stash`** (via dialogue) — a worktree is a second working
  directory (isolated checkout over a shared object DB) for concurrent work;
  stash parks uncommitted changes and re-applies through three-way merge (clobber
  risk if the base moved). Isomorphic to parallel processes with independent
  working memory over a shared append-only log — the substrate under Claude Code
  subagent / parallel-session isolation.

#### Design decisions made
- Transport string `streamable-http` (explicit) over `http` alias.
- Value-authoritative over presence-only (reversed a locked decision — see Decision Log).
- Port validation branch-scoped, not global (symmetry with unvalidated host).
- Resolver in new `config.py`, not `server.py` (reversed locked plan).
- Doc-process v2: two-tier (continuous typed scratchpad + piece-boundary batch pass).
- Ownership matrix canonicalized in CLAUDE.md.

#### Process / tooling
- **"Locked rules" → implementation guidelines** — revisit only on new info or
  principle conflict; record the reversal + reason (Decision Log is the ledger).
- **HANDOFF is a derived VIEW** — always regenerated, never authored into directly.
- **Doc-pass apply mechanic** — splits on the git boundary: the project chat
  authors; Claude Code applies, apostrophe-greps, and commits in-repo files
  (apply/verify/commit stay atomic in the repo); either chat writes out-of-repo
  global memory directly (read-before-write); auto-memory is the memory system's.
  Canonical in CLAUDE.md `## Document ownership`.

---

### 2026-07-22 — Stage 2 Piece 2: Transport Wiring

**Commits:** `3e21a04` (rename) · `bd5462e` (wiring) · `b988025` (CLAUDE.md arch) ·
`3c31c1e` `17e25c3` `b41eea2` (CI-watch hook: never-fired → over-fire → caveat)

#### What was built
- **Piece 2 — transport wiring.** `_run_kwargs(config)` feeds `mcp.run(**kwargs)`;
  host/port **omitted** (not `None`) in stdio because `run()` forwards
  `**transport_kwargs` to `run_stdio_async()`, which has no such params and raises
  `TypeError` on unexpected keywords. Suite 46→51. `3e21a04` (rename) +
  `bd5462e` (wiring); CI green.
- **Transport contract value renamed** `streamable-http` → `http` across
  `config.py`, `test_config.py`, `.env.example`, `README.md`, `CLAUDE.md`.
- **CI-watch hook fixed twice** — never-fired (`3c31c1e`): permission-rule syntax
  sat in `matcher`, which filters tool *name* only; moved to `if`. Over-fire
  (`17e25c3`): an `if` pattern more specific than a bare command name also fires on
  any command containing `$VAR`/`$()`/backticks, so it reported stale CI on
  unrelated commands; added a stdin-payload gate. Caveat documented (`b41eea2`).
- **CLAUDE.md architecture accuracy** (`b988025`).
- **HANDOFF pace-preference sync** (`69c47bd`) — working-style/pace guidance
  synced from `working_principles` memory into the handoff view.
- **CLAUDE.md CI Notes corrected + upstream comment** (`c9656a9`) — commented on
  anthropics/claude-code#79616 (same symptom, wrong JSON shape); corrected the
  in-repo CI Notes to document `matcher` (tool-name only) vs. `if`
  (permission-rule syntax, evaluated per subcommand).

#### Concepts learned
- **Kwargs passthrough is not kwargs filtering** — a framework accepting `**kwargs`
  at one layer and named params at the next has no "ignored when irrelevant"
  behavior. The caller must branch; omission, not `None`, is the contract.
- **Untestable-by-construction code** — logic inside `if __name__ == "__main__":`
  is never imported, therefore never tested. Extracting the branch to a
  module-level function is what makes it assertable at all.
- **Signature-guard tests** — `inspect.signature(...).bind_partial(...)` pins a
  third-party calling convention so a dependency upgrade fails loudly in CI rather
  than silently at deploy. Justified by the soft floor (`>=3.2.4`), not a hard pin.
- **Framework config can shadow project config** — FastMCP reads the project's own
  `.env` with prefix `FASTMCP_` (settings.py:140-141; ENV_FILE at :20), so
  `FASTMCP_*` keys become live framework config bypassing our resolver. Hence
  passing `transport` explicitly + the `.env.example` warning.
- **Translator placement** — an adapter speaking a framework's calling convention
  belongs on that framework's side of a module boundary, even when it restates an
  invariant the other side encodes. Local visible duplication beats distributed
  hidden coupling.
- **Unit vs. integration** — the line is *crossing a real I/O boundary* (socket,
  disk, subprocess), not how many components are wired. `from_env` → `_run_kwargs`
  is a wide *unit* test.
- **Compatibility aliases need something to be compatible with** — accepting
  `streamable-http` alongside `http` would add a normalization layer for zero
  existing consumers and break the 1:1 env-value ↔ `ServerConfig.transport` map.
- **Append-only ledgers are not stale docs** — a Decision Log entry recording a
  since-reversed decision must not be edited; the superseding entry is appended.
  Distinguish *history* (append-only) from *views* (regenerated).
- **Authentication ≠ authorization ≠ tenancy** — identity, permission, and data
  partitioning live in different layers. Bearer tokens are a perimeter, not a
  partition; tenancy needs the principal to reach the data layer and the schema to
  have somewhere to put it.
- **A stale-closed upstream issue matching your symptom is weak evidence** —
  #55889 was misattributed as the cause of the never-firing hook from 2026-06-01
  to 2026-07-21 (~2 months) purely because the symptom matched. Matching symptoms
  are not matching causes: verify your own config *first*, then look upstream.
  Recurred this session — three wrong theories about the Filesystem connector
  outage, ultimately resolved by direct config inspection (the finding: no
  standalone `mcpServers` entry; provisioned via `coworkUserFilesPath`).

#### Design decisions made
- Transport contract value `http`, reversing 2026-07-16 (see Decision Log).
- `streamable-http` rejected as an alias, not silently accepted.
- `_run_kwargs` in `server.py`, not `config.py` (see Decision Log).
- `MCP_` env prefix retained over `FASTMCP_` — `FASTMCP_*` are live framework
  config in the same `.env`; one owner per variable.
- Two commits split on "what happened": contract rename vs. wiring.
- `MCP_HOST` validation + integration tests deferred to Piece 3.

#### Process / tooling
- **Two-Claude split validated at the plan checkpoint** — plan mode caught a false
  fact in the chat-authored spec (`settings.transport` defaults to `"stdio"`, not
  `"http"`, settings.py:257), closed an open flag by source read (banner uses
  `Console(stderr=True)`, cli.py:246 — cannot corrupt stdio framing), and traced a
  doc blast radius the spec under-scoped.
- **Ownership boundary held** — Claude Code edited the three Claude-Code-owned
  files carrying the old literal, routed the five project-chat-owned occurrences to
  the scratchpad instead of reaching across.
- **Filesystem connector outage (EXTERNAL)** — multi-day; discovery succeeded,
  execution failed with bare `Tool execution failed`, no deny-reason. Servers were
  provably healthy (`tools/list` handshakes, no `tools/call` ever arriving). Fixed
  via process kill + cache clear + connector toggle (off, ≥10s, on) in main
  Settings. **Config finding:** Filesystem has no standalone `mcpServers` entry —
  provisioned via top-level `coworkUserFilesPath`, so its lifecycle is Cowork's.
  Root cause not isolated (several variables changed at once).
- **CHANGELOG.md:67 — leave, do not rewrite.** It asserts the hook fails due to
  #55889; that was accurate-at-the-time history, corrected chronologically by
  `3c31c1e` at the next release. Same append-only principle as the Decision Log,
  recorded here so a future reader doesn't "fix" it.

---

## Decision Log

> Append-only. One line per reversed/notable decision:
> `YYYY-MM-DD — what · reversed-from (if any) · reason/principle`. Grep at piece/stage boundaries.

- 2026-07-16 — `MCP_TRANSPORT` value-authoritative · reversed from locked presence-only · make illegal states unrepresentable
- 2026-07-16 — `MCP_PORT` validation branch-scoped to streamable-http (not global) · symmetry with unvalidated `MCP_HOST`; "stdio ignores host/port" = not inspected
- 2026-07-16 — config resolver in new `config.py` · reversed from locked "logic in `server.py`" · separation of concerns + pure-resolver testability
- 2026-07-16 — transport string `streamable-http` over `http` alias · explicit, consistent naming
- 2026-07-17 — Doc Update Process v2: two-tier scratchpad + batch · Step 0 generate-at-end kept silently failing · honor capture-as-you-happen via append-as-you-go
- 2026-07-17 — ownership matrix canonical in CLAUDE.md · was scattered (SUMMARY/memory/CLAUDE) · single in-repo source of truth
- 2026-07-17 — doc-pass apply mechanics split on the git boundary (three branches) · in-repo → Claude Code applies + apostrophe-greps + commits (atomic where git lives); out-of-repo memory → written directly, no commit; auto-memory → memory system · supersedes the earlier two-branch rule; ownership matrix gains Author/Executor columns
- 2026-07-17 — global curated memory → joint ownership (project chat + Claude Code) · was project-chat-sole (an artifact of the Filesystem-access framing) · both chats generate user-insight; unversioned-clobber risk handled by read-before-write + additive + batch reconciliation · authorized live in the Claude Code session
- 2026-07-22 — transport contract value `streamable-http` → `http` · reversed from 2026-07-16 "transport string `streamable-http` over `http` alias" · `http` is FastMCP 3.x's own default for `run_http_async(transport=)` and the spelling its docstrings/CLI use; both literals route identically (transport.py:337), so this is contract clarity, not behavior
- 2026-07-22 — `_run_kwargs` in `server.py`, not `config.py` nor folded into `from_env` · a translator belongs on the side of the boundary it translates INTO; FastMCP owns `run()`'s signature and `server.py` owns the FastMCP relationship; `config.py` stays framework-free · accepted tradeoff: "host/port only in HTTP mode" now stated twice — local visible duplication over distributed hidden coupling
- 2026-07-23 — `docs/` staging site: lifecycle by location; `docs/spec/` + `docs/session/` transient with delete-on-consume; empty folders = boundary processed · turns a per-piece judgment call into an observable invariant
- 2026-07-23 — two author-scoped scratchpads replace the single shared one · separate-by-file over separate-by-column; one writer per file, both readable
- 2026-07-23 — memory files: Claude Code sole author, both actors propose via own scratchpads · reversed from 2026-07-17 "joint ownership" · joint authorship is a smell; separate proposing from authoring · authorship assigned by principle, not reachability (the connector outage was the test)
- 2026-07-23 — executor rule rewritten in CLAUDE.md *and* working_principles.md: the git boundary is a *proxy* for one-author, not the rule itself
- 2026-07-23 — stage plans migrate in-repo as living `docs/stages/STAGE_0N.md` · dated snapshots hand-roll version control and invite staleness (this one had two stale points); repo authoritative on detail, stage file on sequence + rationale
- 2026-07-23 — scope split: trans-project principles live in memory, project conventions live in-repo · a single repo cannot source a convention that outlives it

---

## Open Items & Reminders

### TODO (immediate — Stage 2 next)
- [x] Tool input validation — FastMCP/Pydantic behavior
- [x] `sync_recipes` tool — incremental (hash diff) + full refresh; `_cache_populated` flag
- [x] `search_recipes` scope decision — title-only for Stage 1; deferred to Stage 4
- [x] README: Demo section — MP4 via GitHub user-attachments CDN
- [x] **v0.1.0 tagged and released**
- [x] **Stage 2 Piece 0 — refactor complete** (commits `24c9d45` structural split,
  `090c099` Option B); `server.py` = MCP only, `paprika_client` owns sync + cache;
  33 tests, CI green
- [x] **Stage 2 Piece 1 — env-driven `ServerConfig` + value-authoritative transport auto-detection** (`config.py`, `test_config.py`; suite 33→46; CI green `35517e5`)
- [x] **Stage 2 Piece 2 — transport wiring**; `_run_kwargs` adapter; suite 46→51; CI green (`3e21a04`, `bd5462e`)
- [ ] Stage 2 Piece 3 — per-device bearer-token auth; `hmac.compare_digest`; 401 on
  miss. **Carries:** `MCP_HOST` validation + scoped security hardening; first
  `tests/integration/` suite; earmarked as a hands-on piece.

### Stage completion release workflow (manual until Stage 4-5)
Run this at the end of every stage, before moving to the next:
```bash
git tag vX.Y.Z
git push origin vX.Y.Z
uv run git-cliff --output CHANGELOG.md
git add CHANGELOG.md && git commit -m "chore: update changelog for vX.Y.Z"
git push
```

### Recurring check-ins (every 2-3 sessions)
- [ ] Where does the tool/LMM boundary sit today? Has it shifted?
- [ ] Context sizing calibration — is relevance density intuition improving?
- [ ] Edge cases: are any reasoning/synthesis tasks candidates for tools?
- [ ] Progress recalibration — honest assessment vs. typical developer output
- [ ] Scope discipline — are future-stage ideas staying flagged, not built?
- [ ] Architecture check-in — how has overall paprika-agent architecture evolved?

### Deferred ideas (flagged, not forgotten)
- Local SQLite persistent cache — Stage 2.5
- Centralize test fixtures (factory fixture in `tests/conftest.py`) — just before the
  Stage 2.5 schema change; mutation-safe shared recipe data, eliminates inline-dict
  duplication across the suite
- Two-way sync with deletion flag ("safe sync only") — Stage 2.5
- Auto-sync on client connect (Stage 3); cache/DB warming on startup (Stage 2.5)
- Windows desktop + RTX 3090 as distributed task-queue compute node (Stage 4/5)
- `search_recipes` expansion: ingredients, prep, source, nutrition
- Semantic search / embeddings / knowledge graphs — Stage 4
- Vision models for image-based ingredient prediction — Stage 6
- AWS EC2 manager + Route 53 updater — Stage 6
- MLOps + observability dashboards — Stage 6
- Dataset section in README — add back when analytics features exist
- Claude memory management MCP server — future project after Paprika +
  Yelp/SAMHSA; sits at intersection of everything learned by then
- `MCP_HOST` format validation (`ipaddress` stdlib) — Piece 3; currently
  unvalidated and fails late at uvicorn bind rather than early in the resolver
- `tests/integration/` — Piece 3, where auth makes real request/response
  assertions earn their cost; convention `tests/integration/`, marked so
  `pytest -m "not integration"` keeps the inner loop fast
- **Multi-account access (Art + wife)** — Stage 2.5, *before schema lock*. Open:
  separate vs. joint accounts vs. both; credential input mechanism (not `.env`);
  relation to two-way sync / `merge_recipes`. Requirement undefined — do not design
  ahead of it. **Only pre-commitment:** include an owner key in the Stage 2.5 schema
  and cache structure so single-tenant is the one-key case (cheap now, migration later)
- fastmcp 3.4.4 available (running 3.2.4 via `uv.lock`); signature guards will fail
  loudly on upgrade
- `/mcp` default endpoint (settings.py:264) — needed for Piece 7 remote config
- `docs/DOC_PROCESS.md` — extract Doc Update Process out of SUMMARY (chronological
  log is not a process home; ownership table already moved to CLAUDE.md)
- `docs/stages/STAGE_0N.md` — living stage plans, no date suffix; migrate
  sequence+rationale from the desktop file; repo detail wins where they conflict.
  Do NOT migrate `paprika_handoff_*` (superseded by HANDOFF.md)
- `docs/spec/` — transient specs, delete-on-consume; empty folder = boundary
  processed. Gitignore `docs/spec/*` with `!docs/spec/README.md` as tracked keeper
- `docs/session/` — two author-scoped scratchpads (`code_session_update.md`,
  `chat_session_update.md`); one *writer* per file, multiple readers allowed
- Memory-file ownership: sole author = Claude Code; both chats propose via own
  scratchpads; new `MEMORY:` type candidate. **Supersedes 2026-07-17 joint
  ownership** — log at step 2 when implemented, not now
- Claude Skill packaging the doc-update/sync process — ships ahead of and informs
  the memory-MCP project; portfolio artifact in its own right

### Resources to pursue
- *Designing Data-Intensive Applications* — Kleppmann (systems design)
- ADRs (Architecture Decision Records) — as project architecture matures
- TDD formalization — test-first as a discipline, not just a habit

---

## Doc Update Process

Moved to [`docs/DOC_PROCESS.md`](DOC_PROCESS.md) — the single source of truth for the process (this log is a chronological record, not a process home). The Decision Log remains in this file, above.
