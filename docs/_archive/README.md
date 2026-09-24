# Archive

Frozen record of closed passes. `retired_<pass>/` holds each closed pass's
transients (both scratchpads, every consumed spec and carryover);
`auxiliary/closed_<pass>/` holds temporary files whose status flipped to
`closed` at that pass. Nothing sits at this folder's root. Read it; add a
folder at a close; nothing else. Contents are gitignored; git history is the
backstop for anything that was ever committed. Process: docs/SOP.md section 5.
