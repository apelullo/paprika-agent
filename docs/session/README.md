# Session scratchpads

Continuous typed capture, one file per author, one pair per pass. One writer per
file; both files are readable by both actors.

| File | Sole author | Read by |
|---|---|---|
| `code_scratchpad_<pass>.md` | Claude Code | both |
| `chat_scratchpad_<pass>.md` | project chat | both |
| `code_report_<pass>.md` | Claude Code (written at close) | both; the chat audits it from the archive |

`<pass>` is the pass identifier (SOP.md section 1). Lifecycle: archived at the close
of the pass into `docs/_archive/retired_<pass>/`. An empty `session/` (this README
only) means no pass is in flight. Creation is a property of the append. Neither actor
edits the other's file; the project chat reconciles its own entries against Claude
Code's (a logical merge, never a textual one). Contents are gitignored.
