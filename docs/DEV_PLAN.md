# Development Plan

> Sequenced feature roadmap balancing natural project flow, portfolio impact,
> and learning goals. Each stage builds on the last — don't skip ahead.
> Updated as milestones are completed or priorities shift.

---

## Guiding Principles

1. **Working software at every stage** — each stage produces something real
   and demonstrable, not just scaffolding
2. **Portfolio visibility** — decisions consider how the project reads to
   a senior engineer or hiring manager reviewing the repo
3. **Scope discipline** — one stage at a time; ideas for future stages are
   logged here, not implemented early
4. **Production quality throughout** — tests, CI, documentation, and clean
   architecture from day one, not retrofitted later

---

## Stage 1 — MCP Tool Suite (Current)

**Status: ~75% complete**
**Portfolio signal:** Shows API integration, caching design, async Python,
test discipline, and CI/CD — strong foundation.

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
- [x] PostToolUse CI poll hook (glob fixed: `Bash(*git push*)` to match chained commands)
- [x] `CLAUDE.md` with architecture and workflow docs
- [x] Conventional commit history

### Remaining
- [ ] **MIT license** — required before promoting the repo publicly
- [ ] **README: Demo section** — GIF or screenshot of Claude using the tools;
  highest recruiter impact per effort
- [ ] **README: Quick Start section** — install + run in <5 minutes
- [ ] **README: Architecture section** — one paragraph + optional diagram
- [ ] **README staleness check** — pre-commit hook or CI job
- [ ] **`git-cliff` / CHANGELOG** — automated changelog from conventional
  commits; portfolio artifact + commit discipline enforcer
- [ ] **`search_recipes` expansion** — search across ingredients, source,
  prep instructions (title-only is limiting); discuss scope before implementing
- [ ] **Tool input validation** — explicit FastMCP/Pydantic validation with
  clear error messages
- [ ] **`sync_recipes` tool** — refresh cache without restarting server;
  incremental (ID set diff) + full refresh modes

### Deferred to later stages (flagged here for reference)
- Local SQLite persistent cache — Stage 2 trigger
- Two-way sync with deletion protection flag — Stage 2-3
- Semantic search / embeddings — Stage 6
- Nutrition calculation tool — Stage 5-6

---

## Stage 2 — Local Network Deployment

**Goal:** Move the MCP server to a second machine on the local network.
First separation of client and server into distinct physical hosts.
**Portfolio signal:** Shows networking fundamentals, service configuration,
and ops awareness.

### Planned work
- [ ] Choose MCP transport for network use (SSE or streamable HTTP)
- [ ] Bind server to LAN IP (not just localhost)
- [ ] Configure Claude Desktop on primary machine to connect to remote server
- [ ] Run server as a background service (launchd on macOS, systemd on Linux)
- [ ] Document network configuration and security considerations
- [ ] Local SQLite DB for persistent cache (eliminates cold-start API calls
  across server restarts) — natural fit here since server is now remote

### Architecture decision points
- Transport protocol selection (stdio only works locally)
- Auth on the local network — is bearer token enough, or add network-level
  protection?
- Config separation — dev (localhost) vs. local-network vs. cloud

---

## Stage 3 — Custom Client

**Goal:** Build a client that connects to the MCP server programmatically,
without Claude Desktop. Define the server address in code.
**Portfolio signal:** Shows protocol understanding from both sides,
CLI/application design, and client/server architecture.

### Planned work
- [ ] Understand MCP client protocol (JSON-RPC session, tool listing, calling)
- [ ] Build minimal Python CLI client (`typer` or `argparse`)
- [ ] Connect to Stage 2 network server by IP/hostname
- [ ] Support: list tools, call tool by name, display result
- [ ] Auth handling from client side
- [ ] Config: server address from env or CLI flag

### Architecture decision points
- CLI vs. minimal web UI (Streamlit/FastHTML) — discuss when closer
- Session management — stateless calls vs. persistent connection

---

## Stage 4 — Cloud Deployment

**Goal:** Deploy the server to AWS; make it accessible over the internet
with a real domain name.
**Portfolio signal:** Shows cloud fundamentals, DevOps, security awareness —
rare combination with strong data science background.

### Planned work
- [ ] AWS free tier EC2 instance (t2.micro or t3.micro)
- [ ] IAM setup — least-privilege principle from day one
- [ ] Security group configuration — only expose necessary ports
- [ ] Docker containerization of the MCP server
- [ ] GitHub Actions CD pipeline — push to master → build → deploy
- [ ] Nginx reverse proxy + TLS (Let's Encrypt / Caddy)
- [ ] Domain name + Route 53 A record
- [ ] **EC2 manager pattern** (Art's idea — revisit here):
  - Cron job monitors dynamic EC2 IP
  - Updates Route 53 A record automatically
  - Keeps domain pointed to current IP without manual intervention
  - Extend to monitor and restart other dynamic components
- [ ] Secrets management — AWS Secrets Manager or SSM Parameter Store
- [ ] Basic observability — CloudWatch logs, uptime monitoring

### Architecture decision points
- Single EC2 instance vs. container service (ECS/Fargate) — start simple
- Persistent DB: SQLite on EC2 vs. RDS — cost vs. ops complexity
- CD strategy: simple SSH deploy vs. container registry

---

## Stage 5 — Standalone App

**Goal:** Build a complete, self-contained product with a real UI and
database backend. The project becomes something people can actually use.
**Portfolio signal:** Full-stack data product — rare and valuable for a
senior DS role.

### Planned work
- [ ] Database schema design for recipe data (SQLite → Postgres path)
- [ ] dbt transformation layer for analytics
- [ ] REST API layer (FastAPI) wrapping the MCP tools
- [ ] Frontend — Streamlit, Gradio, or FastHTML (decide when closer)
- [ ] User authentication (if multi-user)
- [ ] Structured logging + metrics + health endpoint
- [ ] Observability dashboard (Grafana or similar)
- [ ] Full test suite expansion: API tests, UI smoke tests

### Architecture decision points
- MCP server vs. REST API vs. both — what role does MCP play long-term?
- ORM vs. raw SQL — SQLAlchemy, SQLModel, or plain `sqlite3`
- Frontend framework — optimize for speed-to-demo vs. learning value

---

## Stage 6 — AI/ML Features

**Goal:** Apply Art's data science depth to production ML systems. This is
the endgame and the most differentiated part of the portfolio.
**Portfolio signal:** The rarest combination — production engineering +
applied ML + domain expertise. This is a lead DS portfolio piece.

### Planned work
- [ ] **Semantic search** — sentence-transformer embeddings over recipe
  titles, ingredients, instructions; FAISS or pgvector index
- [ ] **Recipe recommender** — content-based + collaborative filtering;
  Bayesian inference on 365+ day dinner history; temporal trend modeling
- [ ] **Knowledge graph** — recipe → ingredient → technique → cuisine
  relationships; graph embeddings for similarity
- [ ] **RAG pipeline** — retrieval-augmented generation over recipe corpus;
  natural language queries ("something light with what's in my fridge")
- [ ] **Vision features** — ingredient prediction from fridge photos;
  recipe matching from dish images
- [ ] **MLOps layer** — model versioning (MLflow), serving, monitoring,
  drift detection
- [ ] **Continuous fine-tuning** — update models as new dinner data arrives
- [ ] **Analytics dashboards** — temporal trends, preference drift,
  nutritional patterns over time; business-intelligence style presentation

### Data assets available
- 365+ days of structured dinner tracking
- Recipe corpus with ingredients, instructions, source, nutrition
- Temporal structure enables time series and causal analysis

---

## Cross-Cutting Concerns (Apply at Every Stage)

- **Tests** — every new feature gets tests before the PR is closed
- **CI** — no feature ships without green CI
- **Documentation** — README, CLAUDE.md, and docs/ updated with each milestone
- **Conventional commits** — `feat:`, `fix:`, `docs:`, `ci:`, `test:`,
  `chore:`; include the *why* on non-obvious changes
- **Scope discipline** — ideas for future stages go in this doc, not in code
- **Security** — credentials in `.env`, never hardcoded; `.gitignore` verified
  before every new secret is added

---

## Portfolio Narrative (The Story This Project Tells)

> "I built a production-grade AI-integrated system from scratch — starting
> with a clean MCP server, adding networking and cloud deployment, and
> culminating in a personalized recipe recommender powered by a year of
> real dinner data. Every stage was tested, documented, and shipped with
> the discipline of a production engineering team."

This narrative works for: senior DS roles, ML engineering roles, data
platform roles, and technical lead positions. It demonstrates creative
problem-finding, end-to-end execution, and the rare ability to operate
across the full stack from model to infrastructure.
