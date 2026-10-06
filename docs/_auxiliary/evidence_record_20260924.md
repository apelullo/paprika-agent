# Proposal: the Evidence Record (register, capture type, process edits)

**Status:** in-progress
**Closes when:** the process pass after Pass B ratifies or supersedes it
**Last updated:** 2026-10-05
**Origin:** chat draft, pass 20260924 (`docs/spec/draft_evidence_record_20260924.md`),
routed here at the pass close.
**Authority:** Art's design input of 2026-09-24, 2026-09-25 and 2026-09-27 (chat
scratchpad, pass 20260924); chat picks are marked as such and are his to strike.

## 1. Purpose

One record, two consumers:

1. **Calibration.** A dated log of instances where Art's judgement showed (hits) and
   where it missed, so progress is visible and intuition is built on evidence, not
   impression. Misses are required, or the record recalibrates nothing.
2. **Career narrative.** A curated subset, in STAR form, that explains this project
   to a recruiter or hiring manager by its most salient decisions.

Art's framing: "building in the open"; the record is a portfolio artifact in its own
right. No such record exists today: `DECISIONS.md` records what was decided, not who
saw it.

## 2. Files

| File | Class | Notes |
|---|---|---|
| `docs/registers/evidence.md` | Register | one record per instance; rows corrected in place with a date; IDs never reused |
| `docs/registers/evidence_reserve.md` | Register | overflow text keyed by record ID; append-only in lockstep with the register |

Location: **in-repo** (chat pick, consistent with "building in the open"; Art's
original stance was soft out-of-repo). Career Refresh aggregates across projects by
reading each project's register (a cross-project read, with Art's go-ahead) and maps
rows through the `Drew on` field to `skills_inventory.md`.

## 3. Record format (chat pick; the one deviation from the other registers)

The other registers are Markdown tables. This record has 16 fields, several up to
300 characters, and a table that wide does not render or diff well. Proposed: **one
record per block, fixed key order**, which is readable on GitHub, greppable per field
(`grep "^- Domain: process"`), and parses to a DataFrame in one pass. If Art prefers a
table for consistency, the same fields apply and the reserve carries every cell over
one line.

```
### ER-001
- Author: Chat
- Program: The Evidence Record
- Description: Caught an unverified test count presented as verified
- Event: hit
- Date: 2026-09-24 (time not recorded; predates the register)
- Discovery: Real-Time
- Context-a: The chat restated a carryover FLAG ("3 vs 5 tests") as its own finding.
- Context-b: "I always prefer we verify things from reading the source rather than inference, especially since I gave you secure-shell tools for targeted reads." (Art)
- Domain: process
- Subdomain: read-over-infer, verification
- Drew on: scientific method, data validation (skills_inventory: TBD)
- Enables: auditing AI-produced claims for provenance before acting on them
- New: n
- Evidence: scratchpad:chat 2026-09-24 MEMORY; file:tests/test_config.py; decisions:2026-09-25 validation order
- STAR: S: a test count was cited from memory | T: choose the validation order | A: required a source read first | R: the design's own count was wrong too; rule adopted for both actors
- Updated: 2026-09-28
```

## 4. Data dictionary

| Field | Type | Values / format | Required | Origin |
|---|---|---|---|---|
| ID | string | `ER-NNN`, sequential, zero-padded, never reused | yes | Art (format: chat pick, matches his `CR-096`) |
| Author | enum | `Chat`, `Code`, `Art` (who wrote the record) | yes | Art |
| Program | string | `The Evidence Record` (constant for now; allows other programs later) | yes | Art |
| Description | string | one line, jogs memory; 120 characters max (chat pick) | yes | Art |
| Event | enum | `hit`, `miss`, `mixed` (`mixed` is a chat addition for instances like the ubuntu-latest premise) | yes | Art |
| Date | string | `YYYY-MM-DD HH:MM EDT`, read from the machine; date only when the time predates the register | yes | Art |
| Discovery | list | one or more of `Real-Time`, `Recap`, `Review`, `Retrospective`, `Close-Assessment` (Art: "Recap or Review or both if justified") | yes | Art |
| Context-a | string | relevant prior comments in sequence; 300 characters by `wc -c` (chat pick); overflow to the reserve as `[reserve ER-NNN a]` (Art's alternative: a preamble section) | no | Art |
| Context-b | string | the instance in Art's words; same cap and overflow | yes | Art |
| Domain | enum | `architecture`, `process`, `testing`, `security`, `scope`; extend by decision | yes | Art (chat's list, adopted as-is) |
| Subdomain | list | controlled vocabulary kept in the register header; starter set in section 5 | no | Art (emergent) |
| Drew on | list | existing skills or knowledge the instance rested on; carries the `skills_inventory.md` mapping (Art's column 13 folds in) | no | Art's reading (a) |
| Enables | list | what the instance unlocks next | no | Art's reading (b) |
| New | enum | `y`, `n`; `y` marks a skills_inventory candidate | yes | Art's reading (c) |
| Evidence | list | typed pointers, `kind:ref`; kinds: `git`, `decisions`, `register`, `scratchpad`, `file`, `std` (RFC, PEP, docs) | yes | Art |
| STAR | string | `S: ... \| T: ... \| A: ... \| R: ...`; Art's triplet maps S = what you saw, A = what you decided, R = what it prevented | no (required for `Discovery: Recap` and later) | Art |
| Updated | date | last in-place correction (register rule) | yes | chat pick |

Data-dictionary columns Art asked about (type, formatting) are this table; it lives
in the register header.

## 5. Subdomain starter vocabulary (chat pick; grows by use)

- architecture: separation of concerns; boundaries (module, layer, LLM vs tool);
  composition (injection vs mutation); fail-safe defaults; structural vs conventional
  invariants; interface contracts; DRY
- process: capture; routing; staleness; sequencing; roles; read-over-infer
- testing: isolation; tiers; guard tests; negative tests; locking vs changing behaviour
- security: secrets handling; auth; exposure; constant-time comparison
- scope: deliberate widening; deferral; drift detection

## 6. Capture and routing

- New scratchpad type **`EVIDENCE:`** (Art's `[EVIDENCE/DATA]`). Write action: a record
  in `docs/registers/evidence.md` (plus a reserve block when a cell overflows). The
  type is unique by write action, as SOP section 3 requires.
- Scratchpad form (one line): `- YYYY-MM-DD EVIDENCE: (hit|miss|mixed; Discovery)
  description; domain; evidence pointers; Art's words if available.` The full record
  is composed at routing.
- Writers: the chat and Code write `EVIDENCE:` lines in their own scratchpads during
  a pass; Art may write records directly into the register at any time.
- **ID allocation:** IDs are assigned only when a record is written to the register.
  Since both actors' lines are written at close through the spec (by Code), one
  writer allocates per pass; Art's direct records take the next free ID.
- **Discovery is the learning timeline:** `Real-Time` during a beat or a Code session;
  `Recap` at the learning close (piece recap); `Close-Assessment` at the project close;
  `Review` and `Retrospective` at the stage sync or later. A record gains Discovery
  values as it is revisited; the correction is dated in `Updated`.

## 7. Process edits (work order sketch for the process pass)

1. `CLAUDE.md`: file-class table gains both files (Register); ownership row: both
   actors append, the chat curates STAR and Discovery upgrades, Art decides
   promotion to career artifacts; the scratchpad types list gains `EVIDENCE:`.
2. `docs/SOP.md`: section 3 (types) gains the `EVIDENCE:` row; section 4 (close) gains
   a step before step 1: **learning close** (piece recap: beats, threads, cross-scale
   review; `Recap` and `Close-Assessment` records written); the stage sync gains
   `Review` and `Retrospective` records.
3. `docs/registers/evidence.md` and `evidence_reserve.md`: created with header, data
   dictionary, subdomain vocabulary, and the seed records in section 8.
4. Claude Code awareness: `CLAUDE.md` is read automatically, so the type reaches Code
   with item 1; add one line to `~/.claude/memory/working_principles.md` (MEMORY at
   close) so the practice is known across projects.
5. Cross-project: at the process pass open, with Art's go-ahead, read Career Refresh
   `skills_inventory.md` and `registers/content_reserve.md` (CR-096, CR-097) to fix the
   `Drew on` mapping format.

## 8. Seed records (from pass 20260924's IDEA candidates)

- ER-001 hit, Real-Time, process: caught the "3 vs 5 tests" restated as verified.
- ER-002 hit, Real-Time, architecture/testing: pushed back on the "moving target"
  objection to a `/health` version field; the real constraint surfaced.
- ER-003 mixed, Real-Time, process/scope: reasoned pin-vs-float for `ubuntu-latest`
  from first principles; right instinct, one wrong half.
- ER-004 hit, Real-Time, process: noticed the workflow drift to per-commit review,
  named its cost to his learning structure, asked why.
- ER-005 hit, Real-Time, process: identified the secure-shell contention root cause
  (two project chats) after the chat's wrong correlate.
- ER-006 hit, Recap, process: Art's Piece 3 recap accurate on every verifiable claim
  (2026-10-05).
- Backfill candidates (Retrospective, from `DECISIONS.md`): principled reversals of
  locked decisions; fail-safe defaults reached unprompted (the project instructions
  already cite these; the process pass sources the lines).

## 9. Open decisions for Art

1. Block records (chat pick) or a table like the other registers.
2. `Event` values: `hit`/`miss` only, or add `mixed`.
3. Subject: Art only, or any actor's instances (the chat's own misses, for example the
   unasked fold of beats into the review on 2026-09-27).
4. In-repo confirmed?
5. `X` = 300 characters per Context cell; ID format `ER-NNN`; `Description` 120 max.
6. Backfill history at the process pass, or start from ER-001.
7. Whether the teaching-method skill (separate proposal) and this register are one
   work order in the process pass or two.

Art's answers so far (2026-10-05): deferred row 28 approved; the SUMMARY Developer
line is his wording. Items 1 to 7 above are still open.
