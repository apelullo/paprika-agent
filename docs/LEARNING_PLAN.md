# Learning Plan

> Sequenced learning goals balancing Art's interests, optimal knowledge
> integration, and the natural progression of the project.
> Updated as milestones are hit and new concepts are introduced.

---

## Guiding Principles

1. **Learn by building** — every concept is anchored to a real implementation
   decision in this project, not an abstract exercise
2. **Why before how** — understand the problem a pattern solves before
   implementing it
3. **Spiral learning** — concepts reappear at increasing depth (e.g. caching
   appears as in-memory dict → SQLite → Redis → CDN)
4. **Honest sequencing** — defer concepts that require foundations not yet
   laid; flag them clearly rather than skipping them silently
5. **Relevance density over volume** — in learning as in context windows,
   tightly relevant material at the right moment beats exhaustive coverage
   too early; sequence for maximum integration, not maximum coverage

---

## Recurring Check-ins (Every 2-3 Sessions)

These questions should be revisited periodically — they don't have permanent
answers and must be recalibrated as the project and AI landscape evolve:

- **Tool/LLM boundary** — has it shifted since last check? Are any current
  tools candidates for native LLM reasoning? Are any LLM reasoning steps
  candidates for tools?
- **Context sizing intuition** — are relevance density tradeoffs being made
  deliberately? Is the intuition for "too large for context" improving?
- **Edge cases** — are any reasoning, synthesis, or judgment tasks becoming
  complex enough to warrant tool calls (e.g. structured scratchpad,
  chain-of-thought as an inspectable step)?
- **Scope discipline** — are Stage 6 ideas staying flagged rather than
  implemented? Is the current stage's learning arc being completed first?
- **Progress recalibration** — honest assessment of what's been built vs.
  what a typical developer would have at this point; correct for
  underestimation bias
- **Architecture check-in** — how has the overall paprika-agent architecture
  evolved? Is the "extend naturally, not replace" principle holding?

---

## Stage 1 — MCP Foundations ✅ COMPLETE

**Goal:** Solidify the request/response loop, tool design, and server
lifecycle before adding network complexity.

### Completed
- [x] MCP tool anatomy (`@mcp.tool()`, async, type annotations, docstrings)
- [x] Module-level state and server process lifetime
- [x] N+1 query problem and eager cache population
- [x] Inverted index for O(1) lookup
- [x] Lazy initialization pattern
- [x] Conventional commits and commit hygiene
- [x] pytest: unit tests, monkeypatching, async mocking with pytest-httpx
- [x] Pre-commit hooks (ruff lint + format + advisory staleness check)
- [x] GitHub Actions CI pipeline (ruff + pytest gates)
- [x] Race condition awareness (CI polling solution)
- [x] Tool design philosophy — why tools beat LLM reasoning for retrieval
      (context scarcity, determinism, composability, latency/cost)
- [x] The shifting tool/LLM boundary — current rule of thumb and why it
      must be periodically reassessed
- [x] Relevance density — context quality is signal-to-token ratio, not
      raw size; a foundational concept for all future context design
- [x] Function composition via structured tool output vs. probabilistic
      reasoning output
- [x] Architecture thinking — "did you think about tomorrow while building
      today?"; intentionality about change; restraint is as important as
      decisions made
- [x] README design — Quick Start, Architecture, staleness discipline
- [x] MIT license — open source norms; public repo requirements
- [x] AI tool division of labor — project chat vs. Claude Code; when to
      use `/context` vs. `/clear`; context bloat diagnosis

### Remaining (before Stage 2)
- [x] **Tool input validation** — FastMCP uses Pydantic v2; type coercion
  handles wrong types; semantic errors (empty, oversized) require manual
  guards; `ValueError` surfaces cleanly to the LLM
- [x] **Unit vs. integration tests** — unit tests verify logic; integration
  tests verify wiring; DRY: test the helper once, test each caller once
  for the connection; don't re-test logic through every caller
- [x] **Constants vs. config files** — module-level constant when
  environment-invariant; promote to env var when it needs to differ across
  environments or be user-configurable
- [x] **Hash-based sync and boolean sentinel flag** — content fingerprint
  detects edits without timestamps; `_cache_populated` separates "never
  populated" from "populated but empty"; sentinel is cleaner than
  conflating cache state with population state
- [x] **Regression tests** — written after a bug is found and fixed;
  guard against the same bug returning; `test_sync_recipes_full_refresh
  _repopulates_after_flag_reset` is the first regression test in this project
- [x] **`pytest.mark` and mocked vs. live integration tests** — `@pytest.mark.anyio`
  changes how a test runs; custom marks like `@pytest.mark.integration`
  change when/where it runs; live tests in `tests/integration/`, excluded
  from CI with `-m "not integration"`
- [x] **Call counter pattern in tests** — monkeypatching with a list;
  `assert fetch_calls == []` is more explicit than relying on httpx_mock
  to error on unexpected requests
- [x] **Plan mode vs. direct execution** — plan mode when prompt leaves
  meaningful decisions to Claude Code or touches 3+ files; skip when
  prompt fully specifies behavior and follows existing patterns
- [x] **Architectural seam awareness** — sensing that `server.py` does two
  things (MCP server + Paprika API client) before being able to articulate
  it formally; Stage 2.5 will force the split
- [x] **Search system design — field ambiguity** — without semantic
  understanding, multi-field search adds noise not signal; the right
  solution is semantic search (Stage 4), not more fields
- [x] **Tool selection ambiguity as a design cost** — if the LLM has
  to guess between two tools on fuzzy signals, complexity moves into
  the tool boundary, which is invisible and harder to debug
- [x] **Test behavior contracts, not message copy** — assert the
  invariant, not specific wording; copy designed to change produces
  false negatives if tested literally
- [x] **GitHub README video embedding** — `<video>` tags only render
  with `user-attachments/assets/` URLs; drag-drop via issue editor is
  the only reliable method; 10MB limit requires compression first
- [x] **Git tag management** — deleting/moving remote tags; publishing
  Draft releases; `gh release list` for state inspection
- [x] **ffmpeg basics** — `libx264 -crf 28` for screen recording
  compression; CRF = quality/size tradeoff
- [ ] **Error handling patterns** — MCP-specific error surfacing vs. Python
  exceptions; when to return a string vs. raise
- [ ] **Tool docstring design** — docstrings as LLM contracts; how wording
  affects tool selection and parameter passing
- [ ] **Type annotation depth** — `dict | str`, `list[str] | str`; when to
  define a dataclass or TypedDict for richer structure
- [ ] **Context sizing intuition (calibration #1)** — first deliberate
  assessment of what "too large for context" means in practice; revisit
  at each stage until intuition is demonstrably accurate

---

## Stage 2 — Local Network Deployment (Next)

**Goal:** Understand client/server separation, network protocols, and
service configuration before cloud introduces additional abstraction.

### Concepts to learn
- [ ] **TCP/IP basics** — ports, sockets, IP addresses; why `localhost` ≠
  LAN IP; what "binding" a server means
- [ ] **HTTP as a protocol** — request/response cycle at the wire level;
  headers, status codes, body encoding
- [ ] **MCP transport layer** — stdio vs. SSE vs. HTTP; which transport to
  use for local network vs. cloud
- [ ] **Service configuration** — environment-based config; separating dev
  vs. prod settings
- [ ] **`systemd` or `launchd`** — running the server as a background
  service that survives reboots
- [ ] **Local network security** — binding to LAN IP vs. 0.0.0.0; firewall
  basics; why you don't expose auth endpoints on a LAN without protection
- [ ] **Tool/LLM boundary check-in #1** — with networking in place, do any
  new tool candidates emerge? Does the boundary look different from both
  sides of the network?

### Separation of concerns / state ownership (companion beat to networking)
> Added 2026-06-25 via the `server.py` refactor (Piece 0) — a deliberate, documented
> addition to Stage 2's networking focus.
- [x] **Structural vs logical refactor** — moving files (boundary) vs moving logic
  across a boundary (sealing); distinct operations and risk profiles.
- [x] **Make illegal states unrepresentable** — single-owner state enforced by
  architecture beats an invariant you must remember; correctness as structure.
- [x] **Separation of concerns, made provable** — a clean boundary is observable
  (`server.py` no longer importing `asyncio`/`httpx` is proof the boundary holds).
- [x] **Typed return contracts** — a dataclass at a layer boundary separates *what
  happened* from *how it is phrased*; assert fields, not message copy; on-ramp to
  Pydantic / SQLite models at 2.5.
- [x] **Import/monkeypatch discipline** — from-import only never-patched names;
  module-reference anything patched (the patch must resolve on the module dict at
  call time); the same missing-`global` error is silent on write-only, loud on read+write.
- [ ] **Factory test fixtures** — mutation-safe shared test data via a fixture factory
  in `tests/conftest.py`; flagged for just before the Stage 2.5 schema change.

### Config & design (Piece 1, 2026-07-16)
- [x] **Value-authoritative config selection** — unset→default, set→validate, unknown→raise; vs presence-only footgun.
- [x] **Pure injectable resolver** — `from_env(env: Mapping)`; unit-testable without monkeypatching; extends import/monkeypatch discipline.
- [x] **Alternative-constructor idiom** — `ServerConfig.from_env` classmethod; free-function equivalent is stylistic.
- [x] **Config record vs data record** — `ServerConfig` (validated + factory) vs `SyncResult` (pure data); same typed-contract family.
- [x] **Fail-closed defaults** — `127.0.0.1` over `0.0.0.0`; fail-closed > fail-open.
- [x] **Configuration vs domain constants** — `config.py` owns environment-varying config; split on cohesion/rule-of-three, not line count.
- [x] **Functions vs classes ladder** — pure fn → typed record (not state) → stateful class owning invariants → hierarchy/Protocol (rare).
- [x] **Invest at boundaries, defer internals** — disciplined-investment heuristic.

### Git & parallel-work model (Piece 1, 2026-07-16, via dialogue)
- [x] **Worktrees vs. `git stash`** — a worktree is a second working directory (isolated
  checkout over a shared object DB) for concurrent work; stash parks uncommitted changes
  and re-applies through three-way merge (clobber risk if the base moved). Isomorphic to
  parallel processes with independent working memory over a shared append-only log — the
  substrate under Claude Code subagent / parallel-session isolation.

---

## Stage 3 — Custom Client

**Goal:** Build a client that talks to the MCP server in code, without
relying on Claude Desktop's config format. Understand the client/server
contract from both sides.

### Concepts to learn
- [ ] **MCP client protocol** — how a client initializes a session, lists
  tools, and calls them; the JSON-RPC layer under FastMCP
- [ ] **HTTP client patterns** — `httpx` as a client (you've used it as a
  server-side caller); session management, retries, timeouts
- [ ] **Auth patterns** — bearer tokens from client perspective; storing
  and refreshing credentials safely
- [ ] **CLI design** — `argparse` or `typer`; building a usable command-line
  interface; help text as documentation
- [ ] **Configuration management** — `pydantic-settings` for typed,
  validated config from env + files
- [ ] **Context sizing check-in #1** — with a real client sending queries,
  what does actual context usage look like? Is relevance density intuition
  matching observed behavior?

---

## Stage 4 — Semantic Search & Embeddings

**Goal:** Implement embedding-based semantic search — highest-value,
lowest-infrastructure ML feature. Runs entirely locally.

### Concepts to learn
- [ ] **Sentence transformers** — embedding recipes into dense vectors;
  model selection tradeoffs; local inference speed vs. quality
- [ ] **Vector search** — FAISS locally; pgvector when Postgres arrives;
  same interface, swappable backend
- [ ] **Hybrid search** — combining deterministic substring with semantic
  search; configurable blend; when each wins
- [ ] **Embedding storage** — persisting vectors in SQLite; recompute
  strategy on recipe changes
- [ ] **Evaluation** — how do you know search is good? Relevance metrics,
  spot-checks, test cases with known results
- [ ] **Tool/LLM boundary reassessment** — with semantic search in place,
  which tool behaviors can move to native LLM reasoning?
- [ ] **Context sizing check-in #2** — with embedding results in context,
  is relevance density intuition matching observed behavior?

---

## Stage 5 — Recipe Recommender & Bayesian Inference

**Goal:** Build a personalized recommender using dinner history and
embedding infrastructure. Primary ML showcase.

### Concepts to learn
- [ ] **Exploratory analysis** — temporal patterns in 365+ day dinner
  history; preference drift, frequency, seasonal trends
- [ ] **Content-based filtering** — recipe similarity via embeddings
- [ ] **Bayesian preference model** — prior over preferences updated with
  each dinner; uncertainty-aware recommendations
- [ ] **Temporal modeling** — recency weighting; day-of-week and seasonal
  effects; time series on dinner history
- [ ] **MLOps foundations** — model versioning, reproducible training
  pipeline, basic drift detection
- [ ] **Tool/LLM boundary check-in #2** — with a full app in place, which
  current tools are candidates for native LLM reasoning?
- [ ] **Reasoning as a tool** — chain-of-thought as an inspectable,
  composable step; when structured scratchpads beat implicit reasoning

---

## Stage 6 — Cloud, App & MLOps

**Goal:** Package the ML system into a production-grade application.
Infrastructure wraps the ML — not the other way around.

### Concepts to learn
- [ ] **AWS fundamentals** — EC2, IAM, security groups, VPC, free tier
- [ ] **Docker** — containerization, reproducibility, `Dockerfile` anatomy
- [ ] **DNS and Route 53** — A records, TTL, dynamic IP; EC2 manager pattern
- [ ] **Reverse proxy** — nginx or Caddy; TLS termination
- [ ] **Secrets management** — AWS Secrets Manager vs. SSM vs. `.env`
- [ ] **CD pipeline** — GitHub Actions → build → push → deploy
- [ ] **Observability** — structured logging, metrics, health endpoints,
  dashboards; production metrics + ML metrics unified
- [ ] **Tool/LLM boundary check-in #3** — at this stage, LLM reasoning
  *is* the tool in many cases; how has the boundary shifted from Stage 1?
- [ ] **Context sizing check-in (final)** — is context design being made
  deliberately and accurately? Has intuition been demonstrated calibrated?

---

## Learning Anti-Patterns to Watch

- **Scope creep into future stages** — flag ideas, don't implement them early.
  *Refinement (2026-06-25):* scope discipline is not "do less," it is "be deliberate
  and **document** the decision." A reasoned choice to widen scope, recorded in the
  plan, is discipline; undocumented drift is the actual failure mode. The move is to
  update the plan to match the decision, not shrink the decision to match the plan.
- **Conceptual without implementation** — every concept should touch real code
- **Skipping the why** — if it's not clear why a pattern exists, ask before
  implementing
- **Underestimating progress** — Art has a strong tendency to undervalue
  what he's built; recalibrate frequently against the stage map above
- **Treating the tool/LLM boundary as fixed** — it shifts as models improve;
  reassess periodically rather than assuming Stage 1 answers hold forever
- **Optimizing for context size instead of relevance density** — bigger
  context is not better context; always ask "is this token earning its place?"
