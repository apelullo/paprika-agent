# Transient specs

Design specs handed from the project chat to Claude Code for a single piece.

**Lifecycle: delete-on-consume.** Claude Code implements from these; the batch pass
deletes them. An empty `spec/` (this README only) means the last piece boundary was
fully processed — the emptiness is the signal.

Contents are gitignored; this README is the tracked folder-keeper. Do not author
durable facts here — decisions belong in SUMMARY.md's Decision Log.
