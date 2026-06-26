# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

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

Tests live in `tests/test_server.py`. Unit tests cover pure functions and
require no credentials or network access.

## CI

GitHub Actions runs the test suite on every push and PR to `master`
(`.github/workflows/ci.yml`). Check the Actions tab for results.

## CI Notes

**Known bug:** PostToolUse Bash matcher hooks do not fire in Claude Code
v2.1.123+ (GitHub issue #55889, open as of 2026-05-18). After each
`git push`, manually poll CI:

```bash
gh run list --commit <SHA> --repo apelullo/paprika-agent
```

The hook in `.claude/settings.json` is already configured correctly
(SHA-based lookup, `hookSpecificOutput` format) and will fire
automatically once #55889 is fixed. Check the issue at the start of
each session.

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

The codebase is two modules:

- `server.py` — MCP layer only: `load_dotenv()`, `mcp = FastMCP("Paprika")`, the four `@mcp.tool()` defs, and the `__main__` entry point. Imports `dotenv`, `fastmcp`, and `paprika_client` — no `httpx`/`asyncio`/`os`, so the MCP layer knows nothing about HTTP.
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

Do not modify files in `docs/` unless explicitly asked to do so.

`docs/HANDOFF.md` — paste as the first message when starting a new project chat to restore full context.

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
