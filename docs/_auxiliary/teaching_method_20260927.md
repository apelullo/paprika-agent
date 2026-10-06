# Teaching method (proposal)

**Status:** in-progress
**Closes when:** the process pass writes the SOP cadence section and the teaching-method
skill v1
**Last updated:** 2026-10-05

Art's teaching framework and its calibration, captured during pass 20260924 (chat
scratchpad, MEMORY entries of 2026-09-27 and 2026-09-28), routed here at the pass
close. Art's words are quoted verbatim; everything else is labelled with its source.
The method becomes a skill; the cadence (when and who) becomes an SOP section.

## 1. The framework (Art, 2026-09-27, verbatim where quoted)

"Let's do it this way *as we design* in the next design session (i.e. not all at once
at the end)."

1. **Objectives first.** State what we will design/learn and what he will be able to
   do with it (SWBAT, informal), mapped immediately to the design task. The
   implementation session in Claude Code is the follow-up lesson "reinforcing the same
   concepts from a completely different but highly related angle"; "it's more than
   'learning by doing' - it's learning ***while*** doing".
2. **A hierarchy, high level first.** His physics analogy: units, chapters, lessons,
   concepts/beats/facts, then connections across the hierarchy, which "loops
   indefinitely".
3. **Theory, application, practice.** "The 'theory' and the 'practice/engineering' are
   you and code's respective specialties ... the 'application' is the piece that ties
   our work on the project and the teaching together *across the two-/multi-actor
   boundary*"; the close and the sync are where recap and cross-scale connection
   happen (pass, project, and field; not mutually exclusive).
4. **Synthesis at the final stages,** with hits and misses acknowledged, is where
   "intuition and insight are born, nurtured, refined, and sharpened".

## 2. Calibration (Art, 2026-09-27, verbatim)

"draw connections across beats as we go, where appropriate ... This isn't a request to
be more verbose or add more detail; it's a calibration on how teaching/learning
progresses, focusing on atomic facts and concepts and their integration at increasing
scales/scopes/spans of content/conversation." His model of learning: "absorbing,
retaining, and integrating [the step that never ends]", building "intuition, insight,
and 'wisdom'" for short-term decisions, long-term planning, and the interaction
between the two.

## 3. Anomalies and the pared-down sequence (Art, 2026-09-28)

- "in anomalous situations like that I prefer to be asked what I would like to do
  next." (Context: Claude Code ran commits 3 to 7 before their beats; the chat chose a
  path instead of asking.)
- His choice for the beats that followed: (1) a pared-down but structurally identical
  beat per design step; (2) the cross-beat threads review at the end of each beat;
  (3) then the learning analogue of close and sync, a concise but comprehensive piece
  review and cross-scale review.

## 4. Skill vs SOP (chat, 2026-09-27; Art asked whether it should be a skill)

- The skill holds the method: objectives and SWBAT, the hierarchy,
  theory/application/practice, running threads, synthesis.
- The SOP (or CLAUDE.md) holds the when and who: the design lesson in the chat, the
  implementation lesson in Claude Code, synthesis at the close and the sync.
- Codify after evidence: run it through the rest of Pass B and the next design
  session, then write it in the process pass.

## 5. Observations from pass 20260924 (chat)

- **The theory/practice boundary runs both ways.** Starlette's latin-1 header decoding
  and pytest 9's `strict_markers` were practice findings in Claude Code that changed
  the design.
- **Recall, n=1** (confounded by order and fatigue): commits taught with full beats
  (1, 2) produced detailed recall in Art's recap; pared-down beats (3 to 6) produced
  titles only. Input for the skill, not yet a rule.

## 6. Running threads A to J (chat, pass 20260924)

| Thread | Name | One line |
|---|---|---|
| A | Read both sides of the seam | Before writing against a framework hook, read what the framework does before and after it (async `verify_token`; latin-1 headers). |
| B | Configuration-time work belongs at construction | Wire dependencies when the object is built, never by mutation afterwards (the `create_server` composition root). |
| C | Deny is a deliberate path | Rejection is designed and tested like success (fail-closed defaults, otherwise-valid negative tests). |
| D | Threat model decides | The same operation is safe or unsafe by context (`==` at config load, `compare_digest` on the auth path). |
| E | State a guarantee's exact scope | Say what a protection covers and what it does not (`repr=False` vs `asdict`, debuggers, locals). |
| F | Parse with the owning type | Let the type that owns the format validate it, then decide policy (`ipaddress.ip_address`, then `is_unspecified`). |
| G | Prove the test can fail | A test earns trust when breaking the code breaks it (the mutation checks). |
| H | Own it or pin it | Behaviour we rely on but do not own gets a guard test (the `/health` bypass). |
| I | Lock, decide, change | Characterize current behaviour, decide, then change the behaviour and its lock together (`get_token`). |
| J | Bind each surface to its trigger | Each documentation surface updates on its own trigger: commit, close, or stage sweep. |
