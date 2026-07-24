# Session scratchpads

Continuous typed capture, one file per author. **One writer per file; both files are
readable by both actors.**

| File | Sole author | Read by |
|---|---|---|
| `code_session_update.md` | Claude Code | Claude Code, project chat |
| `chat_session_update.md` | project chat | project chat, Claude Code |

**Lifecycle: delete-on-consume.** Both are consumed and deleted at the batch pass.
An empty `session/` (this README only) means the boundary was fully processed.
Creation is a property of the append — if a file is missing, the first append
recreates it.

Neither actor edits the other's file. The project chat reconciles *its own* entries
against Claude Code's (delete redundant · add for gaps · annotate overlaps) — a
logical merge, never a textual one.
