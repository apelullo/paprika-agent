# CLAUDE.md

This file is the shared conventions reference for both actors working on this
repository — Claude Code (claude.ai/code) and the project chat. It carries the
ownership matrix, the scratchpad protocol, and the pointer to the full doc process
(`docs/DOC_PROCESS.md`). Read it at session start.

## Running the server

```bash
uv run python server.py
```

Dependencies are managed with `uv`. To install them:

```bash
uv sync
```

## Running tests

```bash
uv run pytest tests/ -v
```

Tests live in `tests/test_server.py` (tools) and `tests/test_config.py`
(`ServerConfig.from_env`). Unit tests cover pure functions and require no
credentials or network access.

## CI

GitHub Actions runs the test suite on every push and PR to `master`
(`.github/workflows/ci.yml`). Check the Actions tab for results.

## CI Notes

CI status is reported automatically after each `git push` by the
PostToolUse hook in `.claude/settings.json` — no manual polling needed.

**Do not put command-content patterns in the hook's `matcher` field.**
`matcher` filters on *tool name* only (`"Bash"`); content filtering goes
in the handler's `if` field, which uses permission-rule syntax
(`"Bash(git push*)"`) and is evaluated against each subcommand, so a
compound `git add && git commit && git push` matches. A `matcher` of
`"Bash(*git push*)"` silently never fires — this was misdiagnosed as
upstream issue #55889 (stale-closed, not planned) from 2026-06-01 until
2026-07-21. Settings changes take effect without a session restart.

**`if` alone over-fires.** A pattern more specific than a bare command
name also runs the hook on any command containing `$VAR`, `$()`, or
backticks (documented conservative fallback). The hook therefore opens
with a `python3` gate that reads its stdin payload and exits silently
unless `tool_input.command` really contains `git push`. Keep both: `if`
is the cheap prefilter, the gate is authoritative.

## Changelog

Run `uv run git-cliff --output CHANGELOG.md` to regenerate the changelog
from commit history.

**Stage completion release workflow:**
```bash
uv run git-cliff --output CHANGELOG.md
git add CHANGELOG.md && git commit -m "chore: update changelog for vX.Y.Z"
git push
gh release create vX.Y.Z --title "vX.Y.Z — Title" --notes "Release notes."
```
Run `gh release create` last — it creates the git tag at HEAD immediately;
running it before all commits are in tags the wrong commit.

## Architecture

The codebase is three modules:

- `server.py` — MCP layer only: `load_dotenv()`, `mcp = FastMCP("Paprika")`, the four `@mcp.tool()` defs, the `_run_kwargs(config)` adapter, and the `__main__` entry point (which resolves `ServerConfig.from_env(os.environ)` and calls `mcp.run(**_run_kwargs(config))`). Imports `os`, `typing`, `dotenv`, `fastmcp`, `config`, and `paprika_client` — no `httpx`/`asyncio`, so the MCP layer knows nothing about the Paprika HTTP API. **`_run_kwargs` omits host/port entirely in stdio mode** — `run()` forwards `**kwargs` to `run_stdio_async()`, which raises `TypeError` on unexpected keywords, so omission is required rather than stylistic.
- `config.py` — env-driven server config: frozen `ServerConfig` dataclass + `ServerConfig.from_env(env)`. Transport selection is value-authoritative (`MCP_TRANSPORT` unset → stdio; set → validated; unknown → `ValueError`). Host/port resolution and validation are scoped to the `http` branch only — stdio never inspects `MCP_HOST`/`MCP_PORT`. `from_env` operates solely on the injected mapping, never `os.environ`. See `.env.example` for the full env-var contract.
- `paprika_client.py` — the Paprika API client: authentication, the in-memory cache, recipe fetching, input validation, and sync orchestration (`sync()` → `SyncResult`).

Authentication uses email/password credentials from `.env` (`PAPRIKA_EMAIL`, `PAPRIKA_PASSWORD`), exchanged for a bearer token on each cold start via `paprika_client.get_token()`.

### Caching strategy

All recipes are fetched eagerly on first tool call via `paprika_client._populate_cache()`, a no-op if the cache is already warm. Three module-level structures live in `paprika_client`:

- `_recipe_cache` — uid → full recipe dict
- `_name_index` — lowercase name → uid (for O(1) name lookups)
- `_cache_populated` — bool flag; separates "never populated" from "populated but empty" (fixes zero-recipe account re-fetch bug)

Read tools call `await paprika_client._populate_cache()` first and read from these dicts rather than making their own API calls. **All cache mutation lives in `paprika_client`:** `_populate_cache()` and `sync()` are the only writers of `_cache_populated`, so `server.py` never touches it — the cache-reset invariant (clearing `_recipe_cache`/`_name_index` also resets `_cache_populated`) is enforced structurally, not by a convention callers must remember. `sync_recipes` is now a thin MCP wrapper: it validates input, delegates to `paprika_client.sync()` (which returns a `SyncResult`), and formats the result; it does not call `_populate_cache()` itself.

### Adding a new tool

Decorate an `async def` with `@mcp.tool()` in `server.py`. Tools that need recipe data should call `await paprika_client._populate_cache()` and read from `paprika_client._recipe_cache` / `paprika_client._name_index`. Tools that accept string parameters should call `paprika_client._validate_input_string(value, param, tool)` immediately — raises `ValueError` for empty/whitespace-only or oversized inputs (`MAX_QUERY_LENGTH = 200`). Reference moved names via the `paprika_client.` prefix (module import), never `from paprika_client import …` for cache state or patched helpers — tests monkeypatch them on the module.

## Planning

`project_development_plan.md` in the repo root is Claude Code's operational
memory. Update it when:
- A milestone is completed
- A new tool or feature is added
- Architecture decisions change
- Tooling is added or modified

`docs/` contains human-facing planning and learning documents:
- `docs/SUMMARY.md` — chronological learning and development log
- `docs/LEARNING_PLAN.md` — sequenced learning goals by stage
- `docs/DEV_PLAN.md` — sequenced feature roadmap by stage
- `docs/DOC_PROCESS.md` — the doc update process (single source of truth)
- `docs/stages/STAGE_0N.md` — living per-stage implementation plans
- `docs/session/` — author-scoped scratchpads (transient, gitignored)
- `docs/spec/` — transient piece specs (delete-on-consume, gitignored)

Do not modify files in `docs/` unless explicitly asked — this protects chat-authored
documents. The transient folders `docs/session/` and `docs/spec/` are exempt: they are
gitignored, single-author by the matrix, and continuous modification is their purpose.

`docs/HANDOFF.md` — paste as the first message when starting a new project chat to restore full context.

## Document ownership

> Authored/ratified by the project chat (the orchestrator); Claude Code applies
> edits to this section but does not originate them. Canonical location — other
> docs reference this table, never duplicate it.

| Artifact | Author (content authority) | Executor (applies + commits) | Trigger |
|---|---|---|---|
| `README.md` | narrative → project chat; technical-accuracy → Claude Code | Claude Code | staleness hook; stage ships |
| `CHANGELOG.md` | Claude Code (git-cliff) | Claude Code | stage release |
| `CLAUDE.md` | Claude Code (this ownership section → project chat) | Claude Code | arch/workflow change |
| `project_development_plan.md` | Claude Code | Claude Code | milestone / tool / arch |
| `cliff.toml`, `.github/workflows/*`, `.claude/settings.json` | Claude Code | Claude Code | tooling change |
| `docs/SUMMARY.md`, `LEARNING_PLAN.md`, `DEV_PLAN.md` | project chat | Claude Code | batch pass |
| `docs/HANDOFF.md` | project chat (regenerated VIEW) | Claude Code | batch pass |
| `docs/DOC_PROCESS.md` | project chat | Claude Code | process change |
| `docs/stages/STAGE_0N.md` | project chat | Claude Code | stage start |
| `docs/session/code_session_update.md` | Claude Code (sole) | Claude Code | continuous |
| `docs/session/chat_session_update.md` | project chat (sole) | chat writes; Code deletes at pass | continuous |
| `docs/spec/*` | project chat (sole) | Code consumes + deletes | piece boundary |
| `~/.claude/memory/{user_background,feedback_recaps,working_principles}.md` | **Claude Code (sole)** — both actors propose via their own scratchpads | Claude Code | batch pass |
| `~/.claude/memory/MEMORY.md`, `projects/<p>/memory/*` | Claude Code (auto) | memory system (not hand-edited) | automatic |
| `~/.claude/CLAUDE.md` (global) | Art | Art | as needed |

> **Executor rule.** Every artifact has exactly one author, assigned by principle. The
> git boundary is a *proxy* for this: in-repo ⇒ Claude Code applies + apostrophe-greps
> + commits, keeping apply/verify/commit atomic where git lives. Where there is no
> commit (out-of-repo memory, gitignored transients), the proxy does not bind and the
> author is named explicitly — memory files are Claude Code's, with both actors
> proposing via their own scratchpads. Auto-memory remains the memory system's.
> **Two-way visibility, one-way write:** each actor reads the other's scratchpad;
> neither writes to it. The Executor column must obey this rule — that's the audit.

Principle: settled *project* conventions live in-repo where every actor and Art can
see them; memory holds *cross-project* principles (settled but repo-agnostic — a
single repo cannot be the source for a convention that outlives it) plus
provisional/in-flight facts. Promote a settled project convention from memory into
this file; keep trans-project principles in memory.

## Scratchpad protocol

Both actors append dated typed bullets to their own file in `docs/session/` as work
happens (`SHIPPED` / `DECISION` / `LEARNED` / `EXTERNAL` / `FLAG` / `MEMORY`). Neither
edits the other's file. Full process: `docs/DOC_PROCESS.md` — read at session start
(this file) and at the batch pass (that file).

## Commit workflow

Before committing: show the git diff and proposed commit message for review.
Once confirmed, run `git add`, `git commit`, and `git push` together without
asking again.

## Environment

Requires a `.env` file with:

```
PAPRIKA_EMAIL=...
PAPRIKA_PASSWORD=...
```
