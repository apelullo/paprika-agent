# Doc Update Process (v3)

> The single source of truth for how docs and memory stay in sync. Roles live in
> `CLAUDE.md` (`## Document ownership`); this file defines the *process*. Any other
> location that restates the process will drift — those hold pointers only.

Two tiers. **Continuous:** both actors append typed bullets to their own scratchpad
as work happens. **Batch:** at each piece boundary the project chat reconciles and
authors a spec, Claude Code applies + commits, and the transient files are deleted.
The scratchpads prevent loss continuously, so the batch pass stays small and never
reconstructs from memory.

## Tier 1 — Continuous capture (both actors)

Each actor appends a dated, typed bullet to **its own file** in `docs/session/` the
moment something notable happens — never reconstructed at session end:

- Claude Code → `docs/session/code_session_update.md`
- project chat → `docs/session/chat_session_update.md`

**One writer per file; both files are readable by both actors.** Neither edits the
other's file. If a file does not exist (a prior batch pass consumed it), the first
append recreates it — creation is a property of the append. Both are gitignored and
ephemeral. Format: `- YYYY-MM-DD PREFIX: one line.`

**A scratchpad holds un-routed material only.** Once a bullet reaches its destination
it leaves the scratchpad — delete-on-consume applies at the bullet level, not just the
file level. When seeding or retro-seeding, exclude anything already routed in the same
pass, or the next batch pass will route it twice and duplicate entries in an
append-only ledger.

| Prefix | Captures | Routes to (at batch pass) |
|---|---|---|
| `SHIPPED:` | built / committed | SUMMARY "What was built" |
| `DECISION:` | choice + reason/principle | SUMMARY "Design decisions" + Decision Log |
| `LEARNED:` | concept learned in dialogue | SUMMARY "Concepts learned" + LEARNING_PLAN |
| `EXTERNAL:` | outside fact changed | CLAUDE.md / DEV_PLAN as relevant |
| `FLAG:` | forward flag / deferred idea | SUMMARY "Deferred ideas" |
| `MEMORY:` | durable cross-project principle / user insight | `~/.claude/memory/*` (Claude Code authors) |

Both actors capture their own dialogue learnings — this is the v3 change: the v2 rule
that "the project chat's learnings are NOT written to the scratchpad" was the lossy
channel, and it is gone. `SHIPPED:` is Code-only in practice (the chat does not ship);
that asymmetry is expected, not a problem.

## Tier 2 — Batch pass (piece boundary)

```
chat  reads both scratchpads + target docs
      reconciles its OWN scratchpad against Code's
        (delete redundant · add for gaps · annotate overlaps — logical merge only)
      authors a transient spec → docs/spec/
   ↓
Code  reads the spec + both scratchpads + target files
      cross-references spec against sources for accuracy + completeness
      authors and executes the changes
      apostrophe-greps, commits
      deletes consumed specs + both scratchpads
```

**Ordering constraint.** Claude Code must not append to its scratchpad between the
chat's reconciliation and the apply. Entries added in that window roll to the *next*
pass rather than being silently overwritten by a stale reconciliation.

**Process-change rollout.** A process change installed by a pass cannot govern that
pass. When a capture rule ships, plan a one-time retro-seed of any scratchpad that was
ungoverned during it — treat this as part of the rollout, not as a repair.

**Scratchpad vs. spec.** The scratchpad is *raw captured input*; the spec is *routed
instructions*. Code reads the spec to know what to do, the scratchpads to verify the
spec against source. The spec must not become a second log.

**Trigger.** A piece/stage completes or changes scope; roadmap order changes; new
concepts learned; career/portfolio framing shifts; a new tool/pattern/workflow is
adopted; any doc or memory file goes stale. Plus, mechanically: a non-empty
`docs/spec/` or `docs/session/` (beyond the README keepers) means a boundary is
pending; both empty means processed.

**Reading moments (idempotent by construction).** Session start: read `CLAUDE.md`
once. Batch pass: read this file. No other scheduled reads — overlapping pointers
(HANDOFF, project instructions) are reminders of these two, not additional directives.

**Apply mechanics** follow the executor rule in `CLAUDE.md`: in-repo ⇒ Claude Code
applies + apostrophe-greps + commits (atomic where git lives); out-of-repo memory ⇒
Claude Code writes directly, no commit; auto-memory ⇒ the memory system. The
apostrophe grep is the commit gate.

## Type taxonomy — review discipline

**Discriminator:** does a candidate type route somewhere the existing types don't? A
distinct *sink* makes a real type; a distinct *flavor* does not.

- **`MEMORY:` — ADDED (2026-07-23).** Routes to the memory files, a sink no existing
  type has. Subsumes an earlier "progress calibration" candidate (strengths/growth
  assessments) — same destination, so not split out.
- **teaching/concept — rejected.** Routes to SUMMARY "Concepts learned" +
  LEARNING_PLAN, identical to `LEARNED`. A flavor, not a sink.
- **check-in — undecided.** Arguably routes to the recurring check-ins list (a
  distinct sink), but evidence is one instance. Revisit next pass.

## Transfer-efficacy check (first 2–3 passes)

After each of the next few batch passes, scan the conversation for chat-origin
learnings that never reached `chat_session_update.md`. If the file is consistently
thin while good material sits only in scrollback, the file is not the fix and the
capture ritual needs rethinking. This makes the lossy-channel risk measurable rather
than assumed away.

## Installation checklist (anti-drift — verify on any process change)

- [ ] `CLAUDE.md` → "Scratchpad protocol" section present and matching this file
- [ ] `CLAUDE.md` → ownership matrix rows for `docs/session/*`, `docs/spec/*`
- [ ] `CLAUDE.md` → `docs/` carve-out exempts the transient folders
- [ ] `docs/HANDOFF.md` → session-start pointer to `CLAUDE.md`
- [ ] Project instructions (UI, Art applies) → session-start pointer to `CLAUDE.md`
- [ ] `~/.claude/memory/working_principles.md` → executor rule + type list current

## Pointers, not copies

This file is the **only** place the process is defined. `CLAUDE.md` holds roles plus a
two-line actionable summary; `HANDOFF.md` and the project instructions are pure
pointers. Any level that restates the process will drift — so it doesn't.

## Decision Log

The ledger lives in `docs/SUMMARY.md` `## Decision Log` (append-only; format
`YYYY-MM-DD — what · reversed-from (if any) · reason/principle`). Append one line per
reversed/notable decision; grep at piece/stage boundaries. Promote to ADRs when
volume warrants.

## What this is NOT

- Not a replacement for the scratchpads — Tier 1 is where capture happens; Tier 2 routes.
- Not needed for trivial changes (typos, one-line fixes).
