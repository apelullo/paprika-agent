# Development Plan

> Sequenced feature roadmap balancing natural project flow, portfolio impact,
> and learning goals. Each stage builds on the last — don't skip ahead.
> Updated as milestones are completed or priorities shift.

---

## Guiding Principles

1. **Working software at every stage** — each stage produces something real
   and demonstrable, not just scaffolding
2. **Portfolio visibility** — decisions consider how the project reads to
   a senior DS, analytics engineer, or AI engineer reviewing the repo
3. **Scope discipline** — one stage at a time; ideas for future stages are
   logged here, not implemented early
4. **Production quality throughout** — tests, CI, documentation, and clean
   architecture from day one, not retrofitted later
5. **ML before infrastructure** — cloud deployment wraps an impressive ML
   system; it is not a prerequisite for one; prioritize the differentiator

---

## Version Tag Map

Each stage completion gets a version tag. Tags drive the changelog — git-cliff
groups commits between tags into named releases rather than one `[Unreleased]`
bucket. Run `git-cliff` manually after tagging until Stage 4-5, when CI
automation of changelog generation on tag push becomes worth the overhead.

| Version | Stage | Description |
|---|---|---|
| `v0.1.0` | Stage 1 | MCP tool suite complete — four tools, CI, tested, documented, demo video |
| `v0.2.0` | Stage 2 + 2.5 | Local network deployment + SQLite DB + schema |
| `v0.3.0` | Stage 3 | Custom client — minimal Python client connecting to network server |
| `v0.4.0` | Stage 4 | Semantic search + embeddings — natural language recipe queries |
| `v0.5.0` | Stage 5 | Recipe recommender + Bayesian inference |
| `v1.0.0` | Stage 6 | Cloud deployment + standalone app + MLOps |

**To tag a release:**
```bash
git tag v0.1.0
git push origin v0.1.0
uv run git-cliff --output CHANGELOG.md  # regenerate with version groups
git add CHANGELOG.md && git commit -m "chore: update changelog for v0.1.0"
git push
```

**CI automation trigger (add at Stage 4-5):**
```yaml
on:
  push:
    tags:
      - 'v[0-9]*'
```

---

## Stage 1 — MCP Tool Suite ✅ COMPLETE

**Status: 100% — tagged v0.1.0**
**Released:** https://github.com/apelullo/paprika-agent/releases/tag/v0.1.0
**Portfolio signal:** API integration, caching design, async Python, test
discipline, CI/CD — strong engineering foundation.

### Completed
- [x] `list_recipes` — full cache population on first call
- [x] `get_recipe` — O(1) name lookup via inverted index
- [x] `search_recipes` — substring + token-order-independent title search
- [x] `_normalize()` — curly apostrophe handling
- [x] Module-level cache (`_recipe_cache`, `_name_index`)
- [x] Async semaphore throttling (Semaphore(5), timeout=30)
- [x] Full pytest suite (unit + async integration tests)
- [x] ruff lint + format + pre-commit hooks
- [x] GitHub Actions CI (ruff + pytest gates)
- [x] PostToolUse CI poll hook
- [x] `CLAUDE.md` with architecture and workflow docs
- [x] Conventional commit history
- [x] MIT license
- [x] README: Features, Quick Start, Architecture, Tech Stack, Roadmap
- [x] README staleness check (advisory pre-commit hook)
- [x] `git-cliff` + `CHANGELOG.md`

- [x] Tool input validation — `_validate_input_string` helper + `MAX_QUERY_LENGTH`
  constant; raises `ValueError` with tool/param context for empty or
  oversized inputs; 5 new tests (suite: 15 → 20)
- [x] `sync_recipes` — incremental (hash diff) + full refresh modes;
  `_cache_populated` flag fixes zero-recipe re-fetch bug; full refresh
  no-op bug caught and fixed; 10 new tests (suite: 20 → 30)
- [x] `search_recipes` empty-results message — honest scope hint on no match;
  expansion deferred to Stage 4 semantic search
- [x] README: Demo section — MP4 via GitHub user-attachments CDN
- [x] `assets/` directory structure — zero-padded stage folders, archive gitignored
- [x] v0.1.0 tagged and released

### Stage 2 next

### Deferred (flagged for later stages)
- Local SQLite persistent cache — Stage 2.5
- Two-way sync with deletion protection flag — Stage 2.5-3
- Semantic search / embeddings — Stage 4
- Nutrition calculation tool — Stage 4-5

---

## Stage 2 — Local Network Deployment (Compressed)

**Target tag: combined with Stage 2.5 → `v0.2.0`**
**Goal:** Move the MCP server to a second machine on the local network.
First separation of client and server into distinct physical hosts.
Deliberately minimal — full service configuration deferred to Stage 6.
**Portfolio signal:** Networking fundamentals, service configuration,
ops awareness — rare for a DS candidate.

### Planned work
- [x] Choose MCP transport — **Streamable HTTP**. HTTP+SSE was deprecated by MCP spec 2025-03-26, which introduced Streamable HTTP; the spec still documents SSE backward-compatibility and FastMCP 3.2.4 still accepts `sse`. There is no protocol-wide removal date — 2026 deadlines are vendor-specific (e.g. Keboola 2026-04-01, Atlassian Rovo 2026-06-30). The earlier "dropped April 2026" note conflated a vendor deadline with a protocol removal.
- [x] Refactor `server.py` → `server.py` + `paprika_client.py` (Piece 0; 33 tests, CI green)
- [x] Piece 1 — env-driven `ServerConfig` + value-authoritative transport auto-detection (`config.py`, `test_config.py`; suite 33→46; CI green `35517e5`)
- [x] Piece 2 — transport wiring from config; `_run_kwargs` adapter; suite 46→51; CI green (`3e21a04`, `bd5462e`)
- [ ] Bind server to LAN IP (not just localhost)
- [ ] Configure Claude Desktop on primary machine to connect to remote server
- [ ] Document network configuration and basic security considerations

### Scope decisions (2026-06-25 — deliberate, documented)
- **`launchd` service setup pulled forward into Stage 2** (Piece 6). An always-on
  server that survives reboot is the real Stage 2 deliverable; without it the server
  is "run manually," not deployed. *Full* service hardening still deferred to Stage 6.
- **Per-device bearer-token auth added in Stage 2** (Piece 3). *Full* auth hardening
  (OAuth 2.1) still deferred to Stage 6.
- **`server.py` split pulled forward from Stage 2.5 into Piece 0** — done (commits
  `24c9d45`, `090c099`); cleaner MCP-only surface before Stage 2's MCP-side additions.
- **Health endpoint (`GET /health`) added in Stage 2** (Piece 4) — unauthenticated;
  isolates failure layers during network debugging.

### Architecture decision points
- Transport protocol selection (stdio only works locally)
- Config separation — dev (localhost) vs. local-network vs. cloud

---

## Stage 2.5 — Local Database & Schema (NEW)

**Target tag: combined with Stage 2 → `v0.2.0`**
**Goal:** Design and implement a local SQLite database for persistent
recipe storage and dinner history. The real prerequisite for all ML
features — queryable, structured data that survives server restarts.
**Portfolio signal:** Data modeling, schema design, analytics engineering
instincts — directly relevant to DS, analytics engineer, and AI engineer
roles.

### Planned work
- [ ] **Centralize test fixtures first** — factory fixture in `tests/conftest.py`
  for mutation-safe shared recipe data; do this just before the schema change, when
  the recipe shape is about to grow anyway (deferred from the 2026-06-25 refactor).
- [ ] **Schema design discussion** — review whiteboard design; finalize
  tables, primary keys, foreign keys, indices, and triggers
- [ ] **Recipe table** — uid, name, ingredients, instructions, source,
  nutrition, timestamps; designed for downstream ML feature extraction
- [ ] **Dinner history table** — date, recipe uid, ratings/notes if
  available; enables time series and preference modeling
- [ ] **Cache layer integration** — on server start, check DB first;
  fall back to API only for missing/stale records; write-through on
  new API fetches
- [ ] **Incremental sync** — ID set diff against DB state; only fetch
  what's new or changed
- [ ] **Deletion protection flag** — "safe sync only" mode; never delete
  from DB without explicit override; configurable in `.env`
- [ ] **dbt basics** — transformation layer on top of SQLite; analytics
  views for downstream ML feature engineering
- [ ] **Migration strategy** — schema versioning from day one; SQLite →
  Postgres migration path documented

### Architecture decision points
- ORM vs. raw SQL — SQLAlchemy, SQLModel, or plain `sqlite3`
- Trigger-based audit log vs. application-level history tracking
- Feature table design — precomputed ML features vs. compute-on-read

---

## Stage 3 — Custom Client (Compressed)

**Target tag: `v0.3.0`**
**Goal:** Build a minimal Python client that connects to the MCP server
programmatically without Claude Desktop. One focused session.
**Portfolio signal:** Protocol understanding, client/server architecture.

### Planned work
- [ ] Understand MCP client protocol (JSON-RPC session, tool listing, calling)
- [ ] Build minimal Python script: connect, list tools, call a tool,
  display result
- [ ] Connect to Stage 2 network server by IP/hostname
- [ ] Auth handling from client side
- [ ] Config: server address from env or CLI flag

### Deliberately deferred from original Stage 3
- Full CLI with `typer`/`argparse` — revisit at Stage 5
- `pydantic-settings` config management — revisit at Stage 5

---

## Stage 4 — Semantic Search & Embeddings (PULLED FORWARD)

**Target tag: `v0.4.0`**
**Goal:** Implement embedding-based semantic search over recipes.
Runs entirely locally. No cloud required.
**Portfolio signal:** Applied NLP, vector search, production ML thinking —
core AI engineer and senior DS differentiator.

### Planned work
- [ ] **Sentence transformers** — embed recipe titles, ingredients,
  instructions into dense vectors; `sentence-transformers` library
- [ ] **Vector index** — FAISS locally; pgvector when Postgres arrives
  at Stage 6; same interface, swappable backend
- [ ] **`search_recipes` evolution** — same tool, smarter implementation;
  natural language queries ("something light with what's in my fridge")
- [ ] **Embedding storage** — persist vectors in SQLite (Stage 2.5 DB);
  recompute only on recipe changes
- [ ] **Hybrid search** — combine substring (deterministic) with semantic
  (probabilistic); configurable blend
- [ ] **Evaluation** — relevance metrics, manual spot-checks, test cases
- [ ] **Tool/LLM boundary reassessment** — with semantic search in place,
  which current tool behaviors can move to native LLM reasoning?
- [ ] **Wire git-cliff to CI on tag push** — add tag-triggered changelog
  regeneration to `ci.yml`; automate what was previously manual

### Architecture decision points
- Embedding model selection — balance quality vs. local inference speed
- Index rebuild strategy — full rebuild vs. incremental append
- Hybrid search blend — configurable weight vs. learned weight

---

## Stage 5 — Recipe Recommender & Bayesian Inference

**Target tag: `v0.5.0`**
**Goal:** Build a personalized recipe recommender using dinner history
(Stage 2.5) and embedding infrastructure (Stage 4). Primary ML showcase.
**Portfolio signal:** Bayesian inference, collaborative filtering, temporal
modeling, and production engineering — the rarest DS portfolio combination.

### Planned work
- [ ] **Exploratory analysis** — temporal patterns in 365+ day dinner history
- [ ] **Content-based filtering** — recipe similarity via embeddings
- [ ] **Bayesian preference model** — uncertainty-aware recommendations
- [ ] **Temporal modeling** — recency weighting; day-of-week and seasonal
  effects; time series on dinner history
- [ ] **Collaborative signals** — implicit feedback modeling if multi-user
- [ ] **`recommend_recipes` tool** — new MCP tool; context-aware ranked
  suggestions with reasoning
- [ ] **MLOps foundations** — model versioning, reproducible pipeline,
  basic drift detection
- [ ] **Analytics dashboard** — temporal trends, preference drift,
  nutritional patterns; BI-style; business-value framing

### Architecture decision points
- Model serving — in-process vs. separate inference service
- Retraining trigger — on new data vs. scheduled vs. on-demand
- Dashboard framework — Streamlit, Grafana, Evidence, or Observable

---

## Stage 6 — Cloud, App & MLOps (Infrastructure Wraps ML)

**Target tag: `v1.0.0`**
**Goal:** Package the ML system into a production-grade, publicly
accessible application. Infrastructure wraps something genuinely impressive.
**Portfolio signal:** Full end-to-end production system — engineering
depth + ML depth + ops awareness. Lead DS / AI engineer portfolio piece.

### Planned work

#### Cloud deployment
- [ ] AWS free tier EC2 instance (t2.micro or t3.micro)
- [ ] IAM setup — least-privilege from day one
- [ ] Docker containerization of full system
- [ ] GitHub Actions CD pipeline — push to master → build → deploy
- [ ] Nginx reverse proxy + TLS (Let's Encrypt / Caddy)
- [ ] Domain name + Route 53 A record
- [ ] **EC2 manager pattern** (Art's idea):
  - Cron job monitors dynamic EC2 IP
  - Updates Route 53 A record automatically
  - Extends to monitor and restart dynamic components
- [ ] Secrets management — AWS Secrets Manager or SSM Parameter Store
- [ ] Postgres migration — move from SQLite; pgvector for embeddings

#### Standalone app
- [ ] REST API layer (FastAPI) wrapping MCP tools
- [ ] Full frontend — Streamlit, Gradio, or FastHTML (decide when closer)
- [ ] User authentication
- [ ] Full `launchd`/`systemd` service setup (deferred from Stage 2)
- [ ] Full CLI with `typer` (deferred from Stage 3)

#### MLOps & observability
- [ ] CloudWatch logs + uptime monitoring
- [ ] Model serving infrastructure
- [ ] Drift detection and retraining pipeline
- [ ] Structured logging + metrics + health endpoints
- [ ] Observability dashboard (production metrics + ML metrics unified)

#### Advanced ML (if not completed in Stage 5)
- [ ] Knowledge graph — recipe → ingredient → technique → cuisine
- [ ] RAG pipeline over recipe corpus
- [ ] Vision features — ingredient prediction from fridge photos
- [ ] Continuous fine-tuning as new dinner data arrives

### Architecture decision points
- Single EC2 instance vs. ECS/Fargate — start simple
- MCP server vs. REST API vs. both — long-term role of MCP
- Embedding index — FAISS → pgvector migration

---

## Cross-Cutting Concerns (Apply at Every Stage)

- **Tests** — every new feature gets tests before the PR is closed
- **CI** — no feature ships without green CI
- **Documentation** — README, CLAUDE.md, and docs/ updated each milestone
- **Conventional commits** — include the *why* on non-obvious changes
- **Scope discipline** — ideas for future stages go in this doc, not code
- **Security** — credentials in `.env`; `.gitignore` verified before any
  new secret is added
- **Relevance density** — every design decision asks: is this earning
  its place in the system?
- **Version tags** — tag each stage completion; run git-cliff after tagging

---

## Portfolio Narrative (The Story This Project Tells)

> "I built a production-grade AI system end-to-end — starting with a clean
> MCP server and progressing through data modeling, semantic search, and a
> Bayesian recipe recommender trained on a year of real dinner data. Every
> stage was tested, documented, and shipped with production engineering
> discipline. The infrastructure wraps the ML — not the other way around."

This narrative works for: **senior DS roles, AI engineer roles, analytics
engineer roles, and data platform/ML engineering roles.** It demonstrates
creative problem-finding, end-to-end execution, and the ability to operate
across the full stack from model design to infrastructure — without being
positioned as a software engineer.
