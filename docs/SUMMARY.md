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

## Open Items & Reminders

### TODO (immediate — Stage 1 remaining before `v0.1.0`)
- [ ] Tool input validation — FastMCP/Pydantic behavior
- [ ] `sync_recipes` tool — incremental + full refresh modes
- [ ] `search_recipes` expansion — discuss scope before implementing
- [ ] README: Demo section — defer until remaining tools complete
- [ ] **Tag `v0.1.0` and run release workflow** when above are done

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
- Two-way sync with deletion flag ("safe sync only") — Stage 2.5
- `search_recipes` expansion: ingredients, prep, source, nutrition
- Semantic search / embeddings / knowledge graphs — Stage 4
- Vision models for image-based ingredient prediction — Stage 6
- AWS EC2 manager + Route 53 updater — Stage 6
- MLOps + observability dashboards — Stage 6
- Dataset section in README — add back when analytics features exist
- Claude memory management MCP server — future project after Paprika +
  Yelp/SAMHSA; sits at intersection of everything learned by then

### Resources to pursue
- *Designing Data-Intensive Applications* — Kleppmann (systems design)
- ADRs (Architecture Decision Records) — as project architecture matures
- TDD formalization — test-first as a discipline, not just a habit

---

## Doc Update Process

> Run this at the end of any session where significant progress was made,
> plans changed, or new concepts were learned. Keeps all interconnected
> documents consistent without ad-hoc one-file-at-a-time updates.

### Trigger conditions
- A stage is completed or its scope changes
- The roadmap order changes
- New concepts are learned that belong in the learning plan
- Career goals, target roles, or portfolio strategy shift
- A new tool, pattern, or workflow is adopted
- Any memory file becomes stale relative to current reality

### Document ownership map

| File | Owner | Update when |
|---|---|---|
| `docs/SUMMARY.md` | This project chat | New concepts, design decisions, session ends |
| `docs/LEARNING_PLAN.md` | This project chat | Stage completed, concept added, check-ins evolve |
| `docs/DEV_PLAN.md` | This project chat | Roadmap changes, milestone completed |
| `project_development_plan.md` | Claude Code | Any DEV_PLAN change; lean, current state + next actions |
| `CLAUDE.md` (project) | Claude Code | Architecture changes, new conventions |
| `~/.claude/CLAUDE.md` (global) | Manual | Global preferences change |
| `~/.claude/memory/user_background.md` | This project chat | Career goals, background, style evolves |
| `~/.claude/memory/feedback_recaps.md` | This project chat | Recap preferences change |
| `~/.claude/memory/MEMORY.md` | Claude Code (auto) | Do not edit manually |

### Step-by-step

**Step 1 — This chat updates `docs/` files directly via filesystem connector**
- `SUMMARY.md` — session entry: built, learned, decided; update TODOs
- `LEARNING_PLAN.md` — check off completed; add concepts to right stage
- `DEV_PLAN.md` — mark completed; update order/scope; update narrative

**Step 2 — This chat updates global memory files if needed**
- `user_background.md` — career context, roles, growth areas, style
- `feedback_recaps.md` — recap preferences

**Step 3 — Claude Code prompt (run after Steps 1 and 2)**
```
Three things in sequence — wait for confirmation before each:

1. docs/ files were updated externally. Run git status, show the diff
   across all changed files, propose a commit message. Do not commit yet.

2. After that commit: update project_development_plan.md to reflect any
   stage order, milestone, or next-action changes. Lean — no narrative.
   Show diff before committing.

3. After that commit: check CLAUDE.md (project-level) for needed updates
   based on architecture or workflow changes this session. If none needed,
   say so explicitly. Show diff before committing if changes exist.
```

### What this is NOT
- Not a replacement for real-time notes mid-session — capture decisions
  as they happen, don't reconstruct at the end
- Not needed for trivial changes (typos, one-line fixes)
- Not needed if Claude Code already updated files as part of normal workflow

### Frequency
- **End of every meaningful session** — even if only SUMMARY.md changes
- **Immediately** when roadmap order or career framing changes
- **At every stage completion** — run release workflow first, then doc update
