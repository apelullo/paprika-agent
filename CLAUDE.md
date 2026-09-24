# CLAUDE.md

This file is the shared conventions reference for both actors working on this
repository, Claude Code (claude.ai/code) and the project chat. It opens with the
session-start block, then carries the ownership matrix, the file-class table, the
scratchpad protocol, and the pointer to the procedures (`docs/SOP.md`). Read it at
session start.

## Session start (both actors)

The seed prompt for a new project chat is one line: *"Read CLAUDE.md in
~/dev/paprika-agent and execute its session-start actions."* Claude Code reads this
file automatically. The actions are `docs/SOP.md` section 2, in order: read the date
from the machine; determine the pass identifier; sweep `docs/_inbox/`; create your
scratchpad; read the sources. A pass resumes in the same chat and the same Claude
Code session until it is closed (SOP section 1).

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

`docs/` contains human-facing planning, learning, and process documents:
- `docs/SUMMARY.md`: chronological learning and development log
- `docs/LEARNING_PLAN.md`: sequenced learning goals by stage
- `docs/DEV_PLAN.md`: sequenced feature roadmap by stage
- `docs/SOP.md`: procedures (pass identity, session start, capture, close, archive)
- `docs/stages/STAGE_0N.md`: living per-stage implementation plans
- `docs/registers/`: `deferred.md`, `open_questions.md` (living lists; rows close)
- `docs/_auxiliary/`: status-tagged temporary proposals (committed; files close)
- `docs/session/`: author-scoped scratchpads (transient, gitignored)
- `docs/spec/`: transient pass specs (gitignored)
- `docs/_inbox/`: between-session carryovers (transient, gitignored)
- `docs/_archive/`: closed passes (gitignored; frozen)

`DECISIONS.md` at the repo root is the append-only decision ledger.

Do not modify files in `docs/` unless explicitly asked — this protects chat-authored
documents. The transient folders `docs/session/`, `docs/spec/`, and `docs/_inbox/` are
exempt: they are gitignored, their writers are named by the matrix, and continuous
modification is their purpose.

## Document ownership

> Authored/ratified by the project chat (the orchestrator); Claude Code applies
> edits to this section but does not originate them. Canonical location — other
> docs reference this table, never duplicate it.

| Artifact | Class | Author (content authority) | Executor (applies + commits) | Trigger |
|---|---|---|---|---|
| `README.md` | Authored | narrative: project chat; technical accuracy: Claude Code | Claude Code | staleness hook; stage ships |
| `CHANGELOG.md` | Ledger | Claude Code (git-cliff) | Claude Code | stage release |
| `DECISIONS.md` | Ledger | both propose via `DECISION:` entries; the spec names what is written | Claude Code | batch pass |
| `CLAUDE.md` | Authored | Claude Code (session-start, ownership, file-class, scratchpad, and tools sections: project chat) | Claude Code | arch/workflow change |
| `project_development_plan.md` | Authored | Claude Code | Claude Code | milestone / tool / arch / close |
| `cliff.toml`, `.github/workflows/*`, `.claude/settings.json` | Authored | Claude Code | Claude Code | tooling change |
| `docs/SUMMARY.md` | Ledger | project chat | Claude Code | batch pass |
| `docs/LEARNING_PLAN.md`, `docs/DEV_PLAN.md` | Authored | project chat | Claude Code | batch pass |
| `docs/SOP.md` | Authored | project chat | Claude Code | process change |
| `docs/stages/STAGE_0N.md` | Authored | project chat | Claude Code | stage start; piece boundary |
| `docs/registers/*.md` | Register | project chat (destinations named in the spec) | Claude Code | batch pass |
| `docs/_auxiliary/*.md` | Temporary | project chat drafts; Art decides status flips | Claude Code (via the spec); Art directly for his own files | continuous; swept at close |
| `docs/_inbox/carryover_<pass>.md` | Transient | Art (between sessions) or Claude Code (post-reconciliation moves) | writer creates; Claude Code archives | between sessions; close |
| `docs/_archive/**` | Archive | Claude Code (moves at close) | Claude Code | close |
| `docs/session/code_scratchpad_<pass>.md` | Transient | Claude Code (sole) | Claude Code | continuous |
| `docs/session/code_report_<pass>.md` | Transient | Claude Code (sole) | Claude Code writes at close; archived with the pass | close |
| `docs/session/chat_scratchpad_<pass>.md` | Transient | project chat (sole) | chat writes; Claude Code archives at close | continuous |
| `docs/spec/*` | Transient | project chat (sole) | Claude Code consumes + archives | close |
| every folder `README.md` | Readme | project chat | Claude Code | folder convention change |
| `~/.claude/memory/{user_background,feedback_recaps,working_principles}.md` | Authored | **Claude Code (sole)**; both actors propose via `MEMORY:` entries | Claude Code | batch pass |
| `~/.claude/memory/MEMORY.md`, `projects/<p>/memory/*` | Authored | Claude Code (auto) | memory system (not hand-edited) | automatic |
| `~/.claude/CLAUDE.md` (global) | Authored | Art | Art | as needed |

> **Executor rule.** Every artifact has exactly one author, assigned by principle. The
> git boundary is a *proxy* for this: in-repo ⇒ Claude Code applies + apostrophe-greps
> + commits, keeping apply/verify/commit atomic where git lives. Where there is no
> commit (out-of-repo memory; gitignored transients in `docs/session/`, `docs/spec/`,
> `docs/_inbox/`, `docs/_archive/`), the proxy does not bind and the author is named
> explicitly — memory files are Claude Code's, with both actors proposing via their
> own scratchpads. Auto-memory remains the memory system's.
> **Two-way visibility, one-way write:** each actor reads the other's scratchpad;
> neither writes to it. The Executor column must obey this rule — that's the audit.

Principle: settled *project* conventions live in-repo where every actor and Art can
see them; memory holds *cross-project* principles (settled but repo-agnostic — a
single repo cannot be the source for a convention that outlives it) plus
provisional/in-flight facts. Promote a settled project convention from memory into
this file; keep trans-project principles in memory.

## File classes

> Class is a file's maintenance behaviour; ownership is who authors it. A file has
> exactly one class. Procedures that act on a class: `docs/SOP.md`.

| Class | Files | Lifecycle and edit rule |
|---|---|---|
| Authored | `CLAUDE.md`, `README.md`, `project_development_plan.md`, `docs/SOP.md`, `docs/DEV_PLAN.md`, `docs/LEARNING_PLAN.md`, `docs/stages/*`, `.env.example`, `.gitignore`, `cliff.toml`, workflows, memory files | Replace in place; a changed decision gets a `DECISIONS.md` line |
| Ledger | `DECISIONS.md`, `CHANGELOG.md`, `docs/SUMMARY.md` | Append-only within its structure; never reflow or rewrite; correct by appending a dated line |
| Register | `docs/registers/*.md` | Rows have a lifecycle; correct in place with a date; closed rows move to the file's Closed section; numbers are never reused; the file never closes |
| Temporary | `docs/_auxiliary/*.md` (not its README) | Status-tagged; replace in place while `in-progress`; frozen and archived once `closed` |
| Transient | `docs/session/*`, `docs/spec/*`, `docs/_inbox/*` (not READMEs) | Pass-scoped; gitignored; archived at close |
| Archive | `docs/_archive/**` (not its README) | Frozen once written; gitignored |
| Readme | every folder `README.md` | Static; edited only when the folder's convention changes |
| Code | `*.py`, `tests/`, `pyproject.toml`, `uv.lock` | Governed by the commit workflow and CI, not by the doc process |

## Scratchpad protocol

Both actors append dated typed bullets to their own file in `docs/session/` as work
happens: `SHIPPED` / `DECISION` / `LEARNED` / `EXTERNAL` / `FLAG` / `DEFERRED` /
`IDEA` / `MEMORY`. Files are named `<actor>_scratchpad_<pass>.md`. Neither edits the
other's file. Capture if it would change a decision or be lost otherwise. Full
process: `docs/SOP.md` sections 3 and 4.

## Tools on Art's machine (project chat)

The chat reads and writes Art's machine through the `Filesystem` connector
(`Filesystem:*` tools; never the container's `create_file`/`bash`, which succeed on the
wrong machine). The read-only fallback is `secure-shell` with this set only: `date ls
cat head tail grep wc stat diff cmp realpath basename dirname which du shasum md5sum
cut tr safe-find`. The chat never runs `safe-git` or any `safe-*` writer; Claude Code
owns git. Verify a write with a follow-up listing rather than the tool's return value.
`Filesystem:edit_file` can silently curl straight apostrophes; prefer Claude Code's
`str_replace` plus the apostrophe grep for any file that will be committed. Ask before
the first read or write in a directory this project has not visited.

## Commit workflow

Before committing: show the git diff and proposed commit message for review.
Once confirmed, run `git add`, `git commit`, and `git push` together without
asking again.

Exception: `docs/session/code_scratchpad_<pass>.md` is exempt from the
show-diff-and-await-approval rule (Art, 2026-08-01). It is sole-authored, gitignored,
and never committed; appends happen the moment material surfaces.

## Environment

Requires a `.env` file with:

```
PAPRIKA_EMAIL=...
PAPRIKA_PASSWORD=...
```
