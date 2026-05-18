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

---

## Stage 1 — MCP Foundations (Current)

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
- [x] Pre-commit hooks (ruff lint + format)
- [x] GitHub Actions CI pipeline
- [x] Race condition awareness (CI polling solution)
- [x] Tool design philosophy — why tools beat LLM reasoning for retrieval
      (context scarcity, determinism, composability, latency/cost)
- [x] The shifting tool/LLM boundary — current rule of thumb and why it
      must be periodically reassessed
- [x] Relevance density — context quality is signal-to-token ratio, not
      raw size; a foundational concept for all future context design
- [x] Function composition via structured tool output vs. probabilistic
      reasoning output

### Remaining (before Stage 2)
- [ ] **Tool input validation** — what happens when the LLM passes bad
  input? FastMCP's validation behavior; Pydantic under the hood
- [ ] **Error handling patterns** — MCP-specific error surfacing vs. Python
  exceptions; when to return a string vs. raise
- [ ] **Tool docstring design** — docstrings as LLM contracts; how wording
  affects tool selection and parameter passing
- [ ] **Type annotation depth** — `dict | str`, `list[str] | str`; when to
  define a dataclass or TypedDict for richer structure
- [ ] **`git-cliff` setup** — automated CHANGELOG from conventional commits;
  reinforces commit discipline with visible output
- [ ] **Context sizing intuition (calibration #1)** — first deliberate
  assessment of what "too large for context" means in practice; revisit
  at each stage until intuition is demonstrably accurate

---

## Stage 2 — Local Network Deployment

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

## Stage 4 — Cloud Deployment

**Goal:** Deploy a real service to AWS; understand infrastructure, networking,
and ops basics at the level a senior data scientist should know.

### Concepts to learn
- [ ] **AWS fundamentals** — EC2, IAM, security groups, VPC basics; free
  tier constraints and gotchas
- [ ] **Linux server administration** — SSH, file permissions, process
  management, log inspection
- [ ] **DNS and Route 53** — A records, TTL, dynamic IP problem; Art's
  EC2 manager + Route 53 updater idea (excellent, revisit here)
- [ ] **Reverse proxy** — nginx or Caddy in front of the MCP server;
  TLS termination; why you don't expose app servers directly
- [ ] **Secrets management** — AWS Secrets Manager vs. SSM Parameter Store
  vs. `.env`; never hardcode credentials
- [ ] **Docker basics** — containerizing the server; why containers matter
  for reproducibility; `Dockerfile` anatomy
- [ ] **Deployment pipeline** — GitHub Actions → build → push → deploy;
  CD as an extension of the CI you already have

---

## Stage 5 — Standalone App

**Goal:** Build a complete, self-contained product. Understand frontend/backend
separation, UX design basics, and what "production-ready" really means.

### Concepts to learn
- [ ] **API design** — REST vs. other patterns; versioning; error contracts
- [ ] **Database design** — schema design for recipe data; SQLite → Postgres
  migration path; when to use an ORM vs. raw SQL
- [ ] **dbt basics** — transformation layer on top of the DB; why it matters
  for analytics; connects to Art's data science background naturally
- [ ] **Frontend basics** — enough HTML/CSS/JS or a Python UI framework
  (Streamlit, Gradio, or FastHTML) to build an interface
- [ ] **Observability** — structured logging, metrics, health endpoints;
  knowing what your app is doing in production
- [ ] **Tool/LLM boundary check-in #2** — with a full app in place, which
  current tools are candidates for native LLM reasoning? Which LLM steps
  are candidates for tools?
- [ ] **Reasoning as a tool** — chain-of-thought as an inspectable,
  composable step; when structured scratchpads beat implicit reasoning

---

## Stage 6 — AI/ML Features

**Goal:** Apply Art's data science depth to production ML systems. This is
where the data science background becomes a force multiplier.

### Concepts to learn
- [ ] **Embeddings and vector search** — sentence transformers, FAISS or
  pgvector; semantic search over recipes; `search_recipes` evolution from
  substring to semantic (same architecture, smarter implementation)
- [ ] **Knowledge graphs** — recipe → ingredient → technique relationships;
  graph traversal for recommendation
- [ ] **Recommendation systems** — collaborative filtering, content-based,
  hybrid; Bayesian inference on 365+ day dinner history; temporal trend
  modeling
- [ ] **MLOps** — model versioning, serving, monitoring, drift detection;
  connecting to the observability foundation from Stage 5
- [ ] **Fine-tuning and RAG** — when to fine-tune vs. retrieve; building
  a RAG pipeline over recipe data
- [ ] **Continuous learning** — updating models as new dinner data arrives;
  temporal trends in the 365+ day dataset
- [ ] **Tool/LLM boundary check-in #3** — at this stage, LLM reasoning
  *is* the tool in many cases (semantic search, RAG); how has the boundary
  shifted from Stage 1? What's the final mental model?
- [ ] **Context sizing check-in (final)** — with embeddings, RAG, and rich
  recipe data in play, is context design being made deliberately and
  accurately? Has intuition been demonstrated to be calibrated?

---

## Learning Anti-Patterns to Watch

- **Scope creep into future stages** — flag ideas, don't implement them early
- **Conceptual without implementation** — every concept should touch real code
- **Skipping the why** — if it's not clear why a pattern exists, ask before
  implementing
- **Underestimating progress** — Art has a strong tendency to undervalue
  what he's built; recalibrate frequently against the stage map above
- **Treating the tool/LLM boundary as fixed** — it shifts as models improve;
  reassess periodically rather than assuming Stage 1 answers hold forever
- **Optimizing for context size instead of relevance density** — bigger
  context is not better context; always ask "is this token earning its place?"
