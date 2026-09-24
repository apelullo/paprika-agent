# Transient specs

Work orders handed from the project chat to Claude Code, one per pass:
`spec_<subject>_<pass>.md`. Claude Code applies them; the close archives them into
`docs/_archive/retired_<pass>/`. An empty `spec/` (this README only) means no pass is
in flight. Contents are gitignored; this README is the tracked keeper. Do not author
durable facts here: decisions belong in `DECISIONS.md`, deferred items in
`docs/registers/deferred.md`.
