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

- Use _cache_populated flag to correctly handle zero-recipe accounts

_recipe_cache being empty was indistinguishable from a cold cache,
  causing _populate_cache to re-fetch on every call for accounts with
  no recipes. A dedicated boolean flag decouples "has been populated"
  from "contains recipes".

- Reset _cache_populated before full refresh in sync_recipes

_populate_cache() now guards on _cache_populated rather than _recipe_cache,
  so clearing the cache without resetting the flag left it permanently empty
  after a full refresh.


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

- Add git-cliff for automated changelog generation

Generates CHANGELOG.md from conventional commit history.
  Configured to group by type: feat, fix, docs, ci, test, chore.

- Mark git-cliff as completed in dev plan

- Update dev plan — Stage 1 ~95%, git-cliff added, version tag map

- Add docs/session_update.md to .gitignore


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

- Add Changelog section to CLAUDE.md

- Sync DEV_PLAN.md and SUMMARY.md for 2026-05-19 session

Adds Version Tag Map (v0.1.0–v1.0.0) with target tags per stage,
  bumps Stage 1 to ~95%, marks completed items, documents git-cliff
  workflow and concepts learned, updates Open Items for v0.1.0 target.

- Move CI hook bug workaround into CLAUDE.md

- Add HANDOFF.md for new chat context handoff

- Note HANDOFF.md in CLAUDE.md Planning section

- Update dev plan — input validation complete, Stage 1 ~97%

- Update dev plan — reflect _validate_input_string rename

- Note deferred network-layer tests in dev plan

- Add merge_recipes to Stage 2.5, clarify sync_recipes scope, note account similarity idea

- Add Step 4 to doc update process — regenerate HANDOFF.md

- Sync all docs/ files for 2026-05-21 session

- SUMMARY.md: add 2026-05-21 session entry; redesign doc update process
    (Step 0 added, HANDOFF.md integrated into Step 1, Claude Code prompt
    updated); mark input validation TODO complete
  - LEARNING_PLAN.md: mark input validation, unit vs. integration tests,
    and constants vs. config files as completed
  - DEV_PLAN.md: bump Stage 1 to ~97%; mark input validation complete;
    clarify sync_recipes as single-account
  - HANDOFF.md: update state to ~97%; add validation section and test
    count; add merge_recipes and account similarity to deferred ideas;
    update "Where to pick up" to sync_recipes

- Bump dev plan date to 2026-05-21

- Add _validate_input_string guidance to CLAUDE.md adding-a-tool section

- Update dev plan for sync_recipes and zero-recipe deferred note

- Update README for sync_recipes and _cache_populated flag

- Update dev plan for sync_recipes test suite

- Sync all docs/ files for 2026-05-22 session

- Add live integration test plan to deferred tests

- Update CLAUDE.md for _cache_populated flag and sync_recipes cache contract

Three module-level structures now (not two); _cache_populated flag documented
  with its invariant — any code clearing the cache must reset the flag. sync_recipes
  noted as the exception to the _populate_cache() call convention.

- Prompt Step 2 of doc update process to create new global memory files

- Add demo video to README via v0.1.0 release asset

- Update demo video src to GitHub user-attachments CDN URL


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

- Add input validation to get_recipe and search_recipes

Add MAX_QUERY_LENGTH constant and _validate_query_string helper that
  raises ValueError with tool/param context for empty or oversized inputs.
  Update test_search_recipes_empty_query to expect ValueError.

- Add sync_recipes tool with incremental and full modes

Uses hash comparison against the Paprika recipe list endpoint to detect
  additions, edits, and deletions without re-fetching the entire library.

- **search_recipes:** Improve no-match message with scope and hint

- Add demo video and assets directory structure


### Refactoring

- Rename _validate_query_string to _validate_input_string


### Tests

- Add list_recipes and get_recipe tests with mocked cache

- Add apostrophe integration test and _normalize edge cases

- Add _populate_cache integration test with mocked HTTP

- Add fetch_recipe 404 test

- Add test_get_recipe_empty_name to cover input validation

- Add MAX_QUERY_LENGTH boundary tests for get_recipe and search_recipes

- Add test_populate_cache_already_warm to verify no-op on warm cache

- Add direct whitespace-only test for _validate_input_string

- Add sync_recipes test suite (10 tests)

Covers cold cache, incremental add/edit/unchanged/delete/rename,
  full refresh, zero-recipe full refresh, flag reset regression, and
  invalid mode validation.



