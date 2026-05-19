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

Run `uv run git-cliff --unreleased --output CHANGELOG.md` to regenerate
the changelog from commit history.

## Architecture

All MCP tools live in `server.py`. The server authenticates with the Paprika API using email/password credentials from `.env` (`PAPRIKA_EMAIL`, `PAPRIKA_PASSWORD`), exchanging them for a bearer token on each cold start.

### Caching strategy

All recipes are fetched eagerly on first tool call via `_populate_cache()`, which is a no-op if the cache is already warm. Two module-level dicts are maintained:

- `_recipe_cache` — uid → full recipe dict
- `_name_index` — lowercase name → uid (for O(1) name lookups)

New tools that read recipe data should call `await _populate_cache()` first and read from these dicts rather than making their own API calls.

### Adding a new tool

Decorate an `async def` with `@mcp.tool()`. Tools that need recipe data should call `await _populate_cache()` and read from `_recipe_cache` / `_name_index`.

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
