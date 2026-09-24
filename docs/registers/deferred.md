# Deferred items

**Register.** Vetted items with a target stage or piece. Correct in place with a
date; closed rows move to Closed; numbers are never reused; reviewed at every close
for pull-forward (SOP.md section 4, step 2). Consolidated 2026-09-22 (pass 20260922)
from SUMMARY, DEV_PLAN, STAGE_02, project_development_plan, HANDOFF. Stage numbers
are the 1-7 numbering.

next number: 27

| # | Item | Target | Origin | Status |
|---|---|---|---|---|
| 1 | Full README review: executive summary (README.md intro and docs/SUMMARY.md `## Executive Summary`; scope clarified by Art 2026-09-23), four-module Architecture, Roadmap | Stage 2 Piece 3 close (Pass B) | Code FLAG 2026-07-25 | open |
| 2 | Deferred unit tests: `get_token` bad response shape; `fetch_recipe` non-404 HTTP error propagation | Stage 2 Piece 3 (3c) | project_development_plan | open |
| 3 | Live hash-verification test against the Test Recipe account (`live` marker) | Stage 2 Piece 3 (3c) | project_development_plan | open |
| 4 | `/mcp` default endpoint path in the remote config | Stage 2 Piece 7 | SUMMARY | open |
| 5 | fastmcp 3.4.4 available (running 3.2.4 via `uv.lock`); signature guards fail loudly on upgrade | Stage 2 close (evaluate before v0.2.0) | SUMMARY | open |
| 6 | Centralize test fixtures: factory fixture in `tests/conftest.py`, mutation-safe shared recipe data | Stage 3 start, before the schema change | SUMMARY, STAGE_02, DEV_PLAN | open |
| 7 | SQLite persistent cache; cache/DB warming on server startup | Stage 3 | SUMMARY, STAGE_02, DEV_PLAN | open |
| 8 | Two-way sync with deletion-protection flag ("safe sync only") | Stage 3 | SUMMARY, DEV_PLAN | open |
| 9 | `merge_recipes` tool: two-account merge with conflict strategies | Stage 3 | project_development_plan | open |
| 10 | Multi-account access (Art + wife): requirement undefined; pre-commitment is an owner key in the schema and cache so single-tenant is the one-key case | Stage 3, before schema lock | SUMMARY | open |
| 11 | Admin access for Art in the multi-user model: a role on the owner key; requirement otherwise undefined | Stage 3 | chat 2026-09-22 | open |
| 12 | `PaprikaClient` class encapsulation | Stage 3 | HANDOFF | open |
| 13 | 0-recipe account messaging: `list_recipes`/`get_recipe`/`search_recipes` return generic not-found for empty accounts | Stage 3 | project_development_plan | open |
| 14 | ORM vs raw SQL decision (SQLAlchemy, SQLModel, or `sqlite3`) | Stage 3 start | project_development_plan tooling roadmap | open |
| 15 | mypy or Pyright adoption; trigger met 2026-06-25 (cross-module calls) | decide at Stage 3 start; see open_questions Q4 | project_development_plan | open |
| 16 | Auto-sync on client connect | Stage 4 | SUMMARY, STAGE_02 | open |
| 17 | `search_recipes` expansion: ingredients, prep, source, nutrition, natural language | Stage 5 | SUMMARY, DEV_PLAN | open |
| 18 | Semantic search, embeddings, knowledge graph | Stage 5 | SUMMARY, DEV_PLAN | open |
| 19 | sentence-transformers + FAISS adoption | Stage 5 start | project_development_plan tooling roadmap | open |
| 20 | Windows desktop + RTX 3090 as distributed task-queue compute node | Stage 5 or 6 | SUMMARY, STAGE_02 | open |
| 21 | git-cliff changelog regeneration on tag push in CI | Stage 5 or 6 | DEV_PLAN, project_development_plan | open |
| 22 | Nutrition calculation tool | Stage 5 or 6 | DEV_PLAN | open |
| 23 | Full CLI with `typer`/`argparse`; `pydantic-settings` config | Stage 6 | DEV_PLAN | open |
| 24 | OAuth 2.1 (full auth hardening) | Stage 7 | STAGE_02, DEV_PLAN | open |
| 25 | Explicit `MCP_ALLOW_BIND_ALL` opt-in for `0.0.0.0`/`::` when containerized | Stage 7 | chat 2026-09-22 | open |
| 26 | AWS EC2 manager + Route 53 updater; MLOps and observability dashboards | Stage 7 | SUMMARY, DEV_PLAN | open |

## Closed

| # | Item | Closed | Resolution |
|---|---|---|---|
| - | `MCP_HOST` format validation; first `tests/integration/` suite; chat-side backup read path | 2026-09-22 | in Piece 3 scope (`MCP_HOST`, integration suite); secure-shell read set adopted (backup path). Not numbered: closed before the register existed |
