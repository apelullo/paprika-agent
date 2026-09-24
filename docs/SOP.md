# SOP - Standard Operating Procedures (doc process v4)

> Procedures executed at a moment. Roles and rules live in `CLAUDE.md` (ownership
> matrix, file-class table); this file defines the how and the order. Any other
> location that restates a procedure will drift; those hold pointers only.
> Supersedes DOC_PROCESS.md v3 (2026-09-22, pass 20260922; v3 is in git history).

## 1. Pass identity

- A **pass** is one work order: one spec in `docs/spec/`, one piece or one process
  change. A **session** is one chat, and one Claude Code session.
- A pass may span days. It resumes in the **same chat and the same Claude Code
  session** until closed. A chat never spans passes. A new chat that finds a pass in
  flight stops and reports to Art.
- **Identifier:** the START date, `YYYYMMDD`, plus `_pN` for the Nth pass of that
  date (`_p2` for the second). Every transient of the pass carries it:
  `chat_scratchpad_<pass>.md`, `code_scratchpad_<pass>.md`,
  `spec_<subject>_<pass>.md`, `carryover_<pass>.md`, `_archive/retired_<pass>/`.
- **Detection:** `docs/session/` or `docs/spec/` non-empty beyond the README keepers
  means a pass is in flight; its identifier is in the existing filenames. Both empty
  means a new pass: count `docs/_archive/retired_<today>*` and add one.
- **Dates** are read from the machine (`date '+%Y-%m-%d %H:%M %Z (%A)'`) at open, at
  every resumption, and at close. A scratchpad entry is stamped with the day it is
  written; the pass identifier never changes.

## 2. Session-start actions

The seed prompt, in full: *"Read CLAUDE.md in ~/dev/paprika-agent and execute its
session-start actions."* CLAUDE.md points here.

| # | Project chat | Why |
|---|---|---|
| 1 | Read the date from the machine and state it | dates inferred from files were wrong (2026-09-22) |
| 2 | `ls` `docs/session/`, `docs/spec/`, `docs/_inbox/`, `docs/_archive/`; decide in-flight vs new pass and the identifier per section 1 | every transient filename depends on it |
| 3 | Sweep `docs/_inbox/`: read each `carryover_*.md`; its items enter this pass's scratchpad; the file archives with this pass | post-session thoughts otherwise never re-enter |
| 4 | Create `docs/session/chat_scratchpad_<pass>.md` (the first append creates it) | capture needs a file before work starts |
| 5 | Read, in order: `project_development_plan.md`; `docs/registers/deferred.md` (rows targeting the current stage and piece) and `open_questions.md`; the current `docs/stages/STAGE_0N.md`; every `docs/_auxiliary/` file with `Status: in-progress` that names this pass; `docs/session/code_scratchpad_<pass>.md` if present | these are the sources; there is no view |
| 6 | State the pass scope in one line before design work begins | anything outside it is DEFERRED or IDEA, never silently in |

Claude Code reads CLAUDE.md automatically, then runs steps 1, 2, and 4 (its own
scratchpad), then reads `docs/spec/spec_*_<pass>.md` if present and the chat's
scratchpad.

## 3. Continuous capture

Each actor appends dated typed bullets to its own file in `docs/session/` as work
happens, never reconstructed at session end. One writer per file; both readable by
both. Format: `- YYYY-MM-DD PREFIX: one line.`

| Prefix | Captures | Routes to (at close) |
|---|---|---|
| `SHIPPED:` | built / committed | SUMMARY "What was built" |
| `DECISION:` | choice · reversed-from · reason | `DECISIONS.md` (one line) + SUMMARY "Design decisions" |
| `LEARNED:` | concept learned in dialogue | SUMMARY "Concepts learned" + LEARNING_PLAN |
| `EXTERNAL:` | outside fact changed | CLAUDE.md / DEV_PLAN / SUMMARY as relevant |
| `FLAG:` | needs the other actor's call | resolved in-pass: a DECISION; unresolved at close: `docs/registers/open_questions.md` |
| `DEFERRED:` | vetted item with a target stage or piece | `docs/registers/deferred.md` |
| `IDEA:` | unvetted idea or proposal | a new or existing file in `docs/_auxiliary/` |
| `MEMORY:` | durable cross-project principle or user insight | `~/.claude/memory/*` (Claude Code authors) |

- **Floor:** capture if it would change a decision or be lost otherwise.
- **Post-reconciliation:** once the chat records its reconciliation timestamp in the
  spec header, Claude Code appends further entries under a `## Post-reconciliation`
  heading in its own file. The in-flight pass ignores them; at close they move to
  `docs/_inbox/carryover_<pass>.md`.
- **Type discipline:** a new type needs a unique write action, not a unique file.
- **Transfer check, first two v4 passes:** if a scratchpad is thin while good material
  sits in scrollback, the ritual needs fixing, not the file.

## 4. Session-close (the batch pass)

Trigger: the work order is done, or Art calls the close. The order is Art's; no step
runs early, is skipped, or is reordered without his consent given in chat first.

| # | Actor | Step | Why |
|---|---|---|---|
| 1 | Chat | Reconcile its own scratchpad against Code's (delete redundant, add for gaps, annotate overlaps); write the reconciliation timestamp into the spec header | a stale reconciliation silently drops entries |
| 2 | Chat | Review `docs/registers/deferred.md` and in-progress `docs/_auxiliary/` files for items due at the next piece; pull them into the spec or name them as the next pass's input | deferred items were forgotten when only a view listed them |
| 3 | Chat | Author `docs/spec/spec_<subject>_<pass>.md`: numbered concrete items, a commit plan, and a destination for every scratchpad entry | prose instructions get dropped; spec items must be spec items |
| 4 | Code | Read the spec and both scratchpads; cross-reference the spec against the sources; discrepancies go in the commit message body | the loop must close through a durable sink |
| 5 | Code | Apply and commit per the commit plan; apostrophe-grep before each commit | the grep is the commit gate |
| 6 | Code | Route every typed entry to its destination per section 3; verify by type count: every type present in a scratchpad has been routed | a zero count is a claim, not a pass |
| 7 | Code | Sweep `docs/_auxiliary/`: every file carries `**Status:**` and `**Closes when:**`; report `closed` candidates; flips are Art's decision; files marked `closed` move to `docs/_archive/auxiliary/closed_<pass>/` | an untagged temporary file has no lifecycle |
| 8 | Code | Move `## Post-reconciliation` entries to `docs/_inbox/carryover_<pass>.md` | the holding place for material that surfaced mid-apply |
| 9 | Code | Update `project_development_plan.md` (current state, next actions); commit | the next session's first read must be current |
| 10 | Code | Write the close report to `docs/session/code_report_<pass>.md`: HEAD, commits, test count, every cross-reference discrepancy, carryover, routing table by type, `_auxiliary` sweep, completion greps; completion greps are path-scoped (`--include='*.md' --exclude-dir=_archive --exclude='SUMMARY.md'` and so on), never a line-content `grep -v` | a report in chat scrollback is lost; a file archives with the pass |
| 11 | Chat | Audit the report against the spec and both scratchpads; approve the close, or append items under `## Close amendments` at the end of the spec | an executor closing a pass without the author's sign-off is the loop closing through one actor; a defect found after archive can only be fixed in a different pass |
| 12 | Code | Apply each amendment round as one commit; update the report; return to step 11 until the chat approves | a finding needs a place to become a commit inside the pass that owns it |
| 13 | Code | Archive: `docs/_archive/retired_<pass>/` receives both scratchpads, the close report, every consumed spec and carryover; verify both ends (destination holds the file, source is gone) | a move that checks one end can hide a collision |
| 14 | Code | Push; CI green; tell the chat the pass is archived | a close that is not pushed is not closed |

`docs/session/` and `docs/spec/` empty beyond their READMEs means closed.

## 5. Archive conventions

- `docs/_archive/` is gitignored (README keeper tracked). Git history is the backstop
  for anything that was ever committed.
- One folder per pass: `retired_<pass>/`. Closed temporary files:
  `auxiliary/closed_<pass>/`. Nothing at the `_archive/` root.
- Frozen once written: read it, add a folder at a close, nothing else.

## 6. Temporary files (`docs/_auxiliary/`)

Committed. Each file's header carries, in this order: `**Status:** in-progress |
closed`, `**Closes when:** <criterion>`, `**Last updated:** YYYY-MM-DD`. While
in-progress: the chat drafts, Code applies via the spec, replace in place; a change
that is a decision gets a DECISIONS.md line. Once closed: frozen, moved at the next
close (section 4, step 7). Creation is a property of the append: an `IDEA:` entry may
create the file it routes to.

## 7. Installation checklist (verify on any process change)

- [ ] CLAUDE.md session-start block present and pointing here
- [ ] CLAUDE.md ownership matrix rows for `DECISIONS.md`, `docs/registers/*`,
      `docs/_auxiliary/*`, `docs/_inbox/*`, `docs/_archive/*`, both scratchpads, specs
- [ ] CLAUDE.md file-class table matches sections 3 to 6
- [ ] `.gitignore`: `docs/session/*`, `docs/spec/*`, `docs/_inbox/*`, `docs/_archive/*`,
      each with its README exception
- [ ] Project instructions (UI, Art applies): session-start pointer to CLAUDE.md
- [ ] `~/.claude/memory/working_principles.md`: type list and executor rule current

## 8. What this is not

Not a replacement for the scratchpads (Tier 1 captures; Tier 2 routes). Not needed
for trivial changes. Not a rule book: rules and roles live in CLAUDE.md.
