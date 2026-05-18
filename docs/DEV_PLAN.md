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

## Stage 1 — MCP Tool Suite (Current)

**Status: ~85% complete**
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
- [x] README: Features, Quick Start, Tech Stack, Roadmap

### Remaining
- [ ] **README: Architecture section** — one paragraph + optional diagram
- [ ] **README: Demo section** — GIF or screenshot; highest recruiter
  impact per effort; defer until full Stage 1 feature set complete
- [ ] **README staleness check** — pre-commit hook or CI job
- [ ] **`git-cliff` / CHANGELOG** — automated changelog from conventional
  commits; portfolio artifact + commit discipline enforcer
- [ ] **Tool input validation** — explicit FastMCP/Pydantic validation
- [ ] **`sync_recipes` tool** — incremental (ID set diff) + full refresh
- [ ] **`search_recipes` expansion** — ingredients, source, prep
  instructions; discuss scope before implementing

### Deferred (flagged for later stages)
- Local SQLite persistent cache — Stage 2.5
- Two-way sync with deletion protection flag — Stage 2.5-3
- Semantic search / embeddings — Stage 4
- Nutrition calculation tool — Stage 4-5

---

## Stage 2 — Local Network Deployment (Compressed)

**Goal:** Move the MCP server to a second machine on the local network.
First separation of client and server into distinct physical hosts.
Deliberately minimal — full service configuration deferred to Stage 6
when cloud deployment adds real value.
**Portfolio signal:** Networking fundamentals, service configuration,
ops awareness — rare for a DS candidate.

### Planned work
- [ ] Choose MCP transport for network use (SSE or streamable HTTP)
- [ ] Bind server to LAN IP (not just localhost)
- [ ] Configure Claude Desktop on primary machine to connect to remote server
- [ ] Document network configuration and basic security considerations

### Deliberately deferred from original Stage 2
- `launchd`/`systemd` service setup — revisit at Stage 6 with cloud
- Full auth hardening on LAN — revisit at Stage 6

### Architecture decision points
- Transport protocol selection (stdio only works locally)
- Config separation — dev (localhost) vs. local-network vs. cloud

---

## Stage 2.5 — Local Database & Schema (NEW)

**Goal:** Design and implement a local SQLite database for persistent
recipe storage and dinner history. The real prerequisite for all ML
features — queryable, structured data that survives server restarts.
This stage is squarely in the data engineering comfort zone and produces
an immediately useful artifact.
**Portfolio signal:** Data modeling, schema design, analytics engineering
instincts — directly relevant to DS, analytics engineer, and AI engineer
roles.

### Planned work
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
  views for downstream ML feature engineering; connects naturally to
  DS background
- [ ] **Migration strategy** — schema versioning from day one; SQLite →
  Postgres migration path documented

### Architecture decision points
- ORM vs. raw SQL — SQLAlchemy, SQLModel, or plain `sqlite3`; discuss
  when closer; raw SQL first is likely right for learning
- Trigger-based audit log vs. application-level history tracking
- Feature table design — precomputed ML features vs. compute-on-read

---

## Stage 3 — Custom Client (Compressed)

**Goal:** Build a minimal Python client that connects to the MCP server
programmatically without Claude Desktop. Understand the client/server
contract from both sides. One focused session — not a full application.
**Portfolio signal:** Protocol understanding, client/server architecture.

### Planned work
- [ ] Understand MCP client protocol (JSON-RPC session, tool listing,
  calling)
- [ ] Build minimal Python script: connect, list tools, call a tool,
  display result
- [ ] Connect to Stage 2 network server by IP/hostname
- [ ] Auth handling from client side
- [ ] Config: server address from env or CLI flag

### Deliberately deferred from original Stage 3
- Full CLI with `typer`/`argparse` — revisit at Stage 5 with full app
- `pydantic-settings` config management — revisit at Stage 5

---

## Stage 4 — Semantic Search & Embeddings (PULLED FORWARD)

**Goal:** Implement embedding-based semantic search over recipes — the
highest-value, lowest-infrastructure ML feature. Runs entirely locally.
No cloud required. This is the first place where Art's data science
background becomes an explicit force multiplier.
**Portfolio signal:** Applied NLP, vector search, production ML thinking —
core AI engineer and senior DS differentiator.

### Planned work
- [ ] **Sentence transformers** — embed recipe titles, ingredients,
  instructions into dense vectors; `sentence-transformers` library
- [ ] **Vector index** — FAISS locally; pgvector when Postgres arrives
  at Stage 6; same interface, swappable backend
- [ ] **`search_recipes` evolution** — same tool, smarter implementation;
  natural language queries ("something light with what's in my fridge",
  "spicy vegetarian under 30 minutes")
- [ ] **Embedding storage** — persist vectors in SQLite (Stage 2.5 DB);
  recompute only on recipe changes
- [ ] **Hybrid search** — combine substring (deterministic) with semantic
  (probabilistic) for best of both; configurable blend
- [ ] **Evaluation** — how do you know the search is good? Relevance
  metrics, manual spot-checks, test cases with known good results
- [ ] **Tool/LLM boundary reassessment** — with semantic search in place,
  which current tool behaviors can move to native LLM reasoning?

### Architecture decision points
- Embedding model selection — balance quality vs. local inference speed
- Index rebuild strategy — full rebuild vs. incremental append
- Hybrid search blend — configurable weight vs. learned weight

---

## Stage 5 — Recipe Recommender & Bayesian Inference

**Goal:** Build a personalized recipe recommender using the dinner history
data (Stage 2.5) and embedding infrastructure (Stage 4). This is the
project's primary ML showcase and the clearest demonstration of data
science depth applied to a production system.
**Portfolio signal:** The rarest combination for a DS portfolio — Bayesian
inference, collaborative filtering, temporal modeling, and production
engineering in one system.

### Planned work
- [ ] **Exploratory analysis** — temporal patterns in 365+ day dinner
  history; preference drift, frequency analysis, seasonal trends
- [ ] **Content-based filtering** — recipe similarity via embeddings;
  "more like this" recommendations
- [ ] **Bayesian preference model** — prior over cuisine/ingredient
  preferences updated with each dinner; uncertainty-aware recommendations
- [ ] **Temporal modeling** — time series on dinner history; recency
  weighting; day-of-week and seasonal effects
- [ ] **Collaborative signals** — if multi-user data exists, implicit
  feedback modeling
- [ ] **Recommendation tool** — new MCP tool: `recommend_recipes`;
  takes context (time of day, recent history, pantry) and returns ranked
  suggestions with reasoning
- [ ] **MLOps foundations** — model versioning (MLflow or simple
  versioned artifacts); reproducible training pipeline; basic drift
  detection
- [ ] **Analytics dashboard** — temporal trends, preference drift,
  nutritional patterns; BI-style presentation; business-value framing

### Architecture decision points
- Model serving — in-process vs. separate inference service
- Retraining trigger — on new dinner data vs. scheduled vs. on-demand
- Dashboard framework — Streamlit, Grafana, Evidence, or Observable

---

## Stage 6 — Cloud, App & MLOps (Infrastructure Wraps ML)

**Goal:** Package the ML system into a production-grade, publicly
accessible application. Infrastructure now wraps something genuinely
impressive rather than being a prerequisite for it.
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
