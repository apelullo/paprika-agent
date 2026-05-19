# Changelog

All notable changes to this project will be documented in this file.
## [Unreleased]

### Bug Fixes

- Return descriptive message from get_recipe when name not found

Update return type hint from dict | None to dict | str and revise
  docstring to reflect the new not-found behavior.

- Normalize curly apostrophes in recipe name lookups

Paprika stores recipe names with Unicode curly quotes (‘/’),
  but user input arrives as straight apostrophes ('), causing name
  lookups to fail silently.


### CI/CD

- Add GitHub Actions workflow to run pytest on push and PR

- Bump actions/checkout to v6 and setup-uv to v8 for Node.js 24 support

- Fix setup-uv version tag to v8.1.0

- Add PostToolUse hook to auto-watch CI after git push

- Add ruff lint and format checks to CI workflow

- Replace gh run watch with poll loop in PostToolUse hook

- Fix PostToolUse hook to match git push in chained commands

The previous pattern `Bash(git push *)` only matched commands starting
  with `git push`, missing chained invocations like `git add && git commit
  && git push`. Updated to `Bash(*git push*)` to match anywhere in the
  command string.

- Surface CI poll output into conversation via additionalContext

Wraps gh run view output in JSON so the PostToolUse hook feeds the
  result back into the chat instead of discarding it.

- Fix CI poll hook by moving pattern to matcher field

The `if` field inside the hook definition was never spawning the hook
  process ("Watching CI..." never appeared). Moved Bash(*git push*) to
  the outer matcher field, which is the documented filtering mechanism.

- Update CI poll hook to SHA-based lookup and correct hookSpecificOutput format

Hook currently does not fire due to Claude Code bug #55889 (PostToolUse Bash
  matchers broken). Updated to correct SHA-based run lookup and hookSpecificOutput
  JSON format so it works automatically when the bug is fixed.

- Add README staleness warning pre-commit hook


### Chores

- Remove unused scaffold and Claude Code settings from repo

Deleted main.py (uv project scaffold, unused). Added .claude/ and main.py
  to .gitignore to prevent Claude Code internals from being tracked. Removed
  both from git history tracking via git rm --cached.

- Add ruff linting and pre-commit hook

Configure ruff (lint + format) as a dev dependency with pycodestyle,
  pyflakes, and isort rules. Wire it up via pre-commit to run on every
  commit.

- Expand ruff lint rules with bugbear, pyupgrade, and pep8 naming

- Add MIT license

Adds LICENSE file with Art Pelullo copyright 2026. Required before
  promoting the repo publicly.

- Update project_development_plan.md to new stage order

Stage roadmap revised to match docs/DEV_PLAN.md: Stage 2 compressed,
  Stage 2.5 (local DB) added, Stage 4 = semantic search, Stage 5 =
  recommender, Stage 6 = cloud/ops. Next actions trimmed to Stage 1
  remaining items only.

- Update dev plan — mark Architecture section and staleness hook complete


### Documentation

- Add CLAUDE.md with architecture and setup guidance

Documents the caching strategy, how to add new tools, and environment
  setup for future Claude Code sessions.

- Add commit workflow convention to CLAUDE.md

- Document test suite in CLAUDE.md

- Document CI workflow in CLAUDE.md

- Update README to reflect current features and roadmap

- Add project development plan and reference it in CLAUDE.md

- Add docs/ planning folder and update CLAUDE.md

Add three human-facing planning documents under docs/:
  - DEV_PLAN.md: sequenced 6-stage feature roadmap
  - LEARNING_PLAN.md: learning goals anchored to each project stage
  - SUMMARY.md: chronological development and learning log

  Update CLAUDE.md to distinguish project_development_plan.md (Claude
  Code's operational memory) from docs/ (human-facing artifacts), and
  add a guard against modifying docs/ without explicit instruction.

- Note PostToolUse hook glob fix in dev plan

- Update SUMMARY and DEV_PLAN for session 2026-05-15

Log docs/ creation, CLAUDE.md planning update, and PostToolUse hook
  glob fix in SUMMARY.md. Note hook fix on completed item in DEV_PLAN.md.

- Add Quick Start section to README

Covers prerequisites, install, .env configuration, and Claude Desktop
  connection via claude_desktop_config.json.

- Update SUMMARY with 2026-05-16 session notes

- Restructure roadmap and document tool design philosophy (2026-05-16 session)

Stage order revised: Stage 2 compressed, Stage 2.5 (local DB) added,
  Stage 4 = semantic search, Stage 5 = recommender, Stage 6 = cloud/ops.
  Learning plan updated with recurring check-ins and completed concepts.
  Doc update process formalized in SUMMARY.md.

- Add Architecture section to README

- Sync SUMMARY.md and LEARNING_PLAN.md to reflect current state

Trims redundant prose in both files, marks recently completed learning
  items (Architecture, README staleness check, MIT license, AI tool
  division of labor), restructures Stages 4–6 to match the ML-first
  roadmap reorder, and updates Open Items to reflect what's done.


### Features

- Add module-level recipe cache and populate helper

Introduced a module-level `_recipe_cache` dict (uid → recipe data) so
  that recipe data is fetched from the Paprika API only once per server
  lifetime. Extracted the fetch-all-recipes logic into a `_populate_cache`
  helper that is a no-op when the cache is already warm. `list_recipes`
  now delegates to this helper and reads directly from the cache.

  Updated README to remove `get_recipe` from the Features section (not yet
  implemented) and reflect the caching behaviour of `list_recipes`.

- Add get_recipe tool with name index for O(1) lookup

Added a module-level _name_index (lowercase name → uid) populated
  alongside _recipe_cache. get_recipe does a single dictionary lookup
  via the index rather than looping through all recipes.

- Add pytest and initial test suite for _normalize

- Add search_recipes tool with substring + token order matching


### Tests

- Add list_recipes and get_recipe tests with mocked cache

- Add apostrophe integration test and _normalize edge cases

- Add _populate_cache integration test with mocked HTTP

- Add fetch_recipe 404 test



