# Paprika Agent

An MCP server that connects Claude Desktop to the Paprika recipe manager
app via its unofficial API. It runs locally over stdio, or as a network
server over Streamable HTTP with per-device bearer-token auth. The network
server itself is complete; the always-on deployment and the remote Claude
Desktop setup are the remaining Stage 2 work.

## Features
- `list_recipes` — fetch and cache all recipes from your Paprika account
- `get_recipe` — retrieve full recipe details by name (case-insensitive)
- `search_recipes` — keyword search across recipe titles (order-independent)
- `sync_recipes` — sync the in-memory cache with the Paprika API; incremental
  mode uses hash comparison to detect adds, edits, and deletes; full refresh
  mode wipes and repopulates the cache

## Demo

<video src="https://github.com/user-attachments/assets/214a9f09-ef78-420a-b58e-2ce75bc01412"
  controls autoplay loop muted
  style="max-width: 100%;">
</video>

Claude Desktop calling all four Paprika Agent tools — list, get, search, and sync.

## Quick Start

### Prerequisites
- Python 3.13+
- [uv](https://docs.astral.sh/uv/) — Python package manager
- [Claude Desktop](https://claude.ai/download)
- A [Paprika 3](https://www.paprikaapp.com/) account with cloud sync enabled

### Install

```bash
git clone https://github.com/apelullo/paprika-agent.git
cd paprika-agent
uv sync
```

### Configure credentials

Copy the template and fill in your Paprika credentials:

```bash
cp .env.example .env
```

```
PAPRIKA_EMAIL=your@email.com
PAPRIKA_PASSWORD=yourpassword
```

The optional `MCP_*` variables documented in `.env.example` configure network
mode (transport, bind address, per-device API keys). Ignore them for local
use; see Network mode below.

### Connect Claude Desktop

Open Claude Desktop → **Settings → Developer → Edit Config**. Add the
following to `claude_desktop_config.json`, replacing the paths with your
own (run `which uv` to find your `uv` binary):

```json
{
  "mcpServers": {
    "paprika": {
      "command": "/path/to/uv",
      "args": [
        "run",
        "--directory",
        "/absolute/path/to/paprika-agent",
        "python",
        "server.py"
      ]
    }
  }
}
```

Restart Claude Desktop. The paprika tools will be available in any new chat.

### Network mode (preview)

The server side of network mode is complete. In `.env`, set
`MCP_TRANSPORT=http`, set `MCP_HOST` to this machine's LAN IP (an IP literal;
bind-all is refused), and add one `MCP_API_KEY_<DEVICE>=<token>` line per
client device (generate a token with
`python -c "import secrets; print(secrets.token_urlsafe(32))"`). Start it with
`uv run python server.py` and check `curl http://<host>:8000/health`, which
returns `{"status": "ok"}` without a token. MCP clients connect to
`http://<host>:8000/mcp` with `Authorization: Bearer <token>`. This is plain
HTTP for a trusted home LAN; TLS and full auth hardening are later stages
(see `docs/DEV_PLAN.md` Stage 7 and `docs/registers/deferred.md`). The
always-on service and the remote Claude Desktop configuration land with the
last Stage 2 pieces.

## Architecture

Paprika Agent is built around a single guiding principle: **every design
decision should extend naturally, not require replacement as the project grows.**

The server is four modules with enforced boundaries:

- **`server.py`** — the MCP layer and nothing else: the four tool definitions,
  the `create_server` factory that wires them together with auth and a
  `GET /health` route at construction, and the entry point. It never calls the
  Paprika API and owns no state.
- **`config.py`** — environment-driven server configuration. A frozen
  `ServerConfig` is resolved via `ServerConfig.from_env`: leave `MCP_TRANSPORT`
  unset for local stdio, or set `http` for network mode. Selection is
  value-authoritative — unknown values fail loudly —
  and network settings fail closed: the host defaults to `127.0.0.1`, must be
  an IP literal, and can never be bind-all (`0.0.0.0`, `::`); network mode
  refuses to start without at least one per-device API key. Full contract in
  `.env.example`.
- **`auth.py`** — per-device bearer-token verification for network mode. Each
  client device gets its own token; tokens are compared as bytes with
  `hmac.compare_digest`, never `==`, and the matching device becomes the
  authenticated client. Revoking a device is removing its key and restarting
  the server (keys load at startup).
- **`paprika_client.py`** — the Paprika API client: authentication, recipe
  fetching, input validation, sync, and the in-memory cache it exclusively owns.

On first tool call, the server eagerly fetches all recipes from the Paprika
API and populates two module-level structures in `paprika_client`: `_recipe_cache` (uid → full
recipe data) and `_name_index` (normalized name → uid). Subsequent calls are
pure in-memory lookups — zero additional API calls. This cache is the
foundation all current tools share and the natural predecessor to a persistent
local database. A `_cache_populated` flag tracks whether the cache has been
populated at least once, keeping the no-op guard correct for accounts with
zero recipes.

Tools are thin by design. The read tools call `_populate_cache()`, read from
the shared cache, and return a result; `sync_recipes` delegates to the
client's `sync()` and formats what it returns. `search_recipes` today does substring
matching over titles; tomorrow it does semantic search over embeddings — same
tool interface, smarter implementation underneath. The architecture doesn't
change; the sophistication grows inside it.

## Testing

Tests are organized by the boundary they cross. Unit tests (`tests/`) need no
network or credentials. In-process HTTP tests (`tests/integration/`, marker
`integration`) drive the real ASGI app through Starlette's `TestClient`, so
auth is tested where it lives. Tests that need a socket or real credentials
carry the `live` marker and are excluded in CI. Markers are strict: an
unregistered marker is a collection error. Run everything with
`uv run pytest tests/ -v`; CI runs `uv run pytest tests/ -v -m "not live"`.

## Tech Stack
Python 3.13 · FastMCP · Starlette · httpx · uv · pytest · ruff · pre-commit ·
GitHub Actions · Paprika API

## Roadmap
- [x] Stage 1: MCP tool suite (v0.1.0)
- [ ] Stage 2: Local network deployment (v0.2.0), in progress: config,
  transport, auth, health, and CI gate done; always-on service and remote
  client setup remaining
- [ ] Stage 3: Local recipe database and schema (v0.3.0)
- [ ] Stage 4: Custom client (v0.4.0)
- [ ] Stage 5: Semantic search and embeddings (v0.5.0)
- [ ] Stage 6: Bayesian recipe recommender (v0.6.0)
- [ ] Stage 7: Cloud deployment and MLOps (v1.0.0)

## Project documentation

This project is built in the open, and its process is part of the portfolio.
`DECISIONS.md` is the decision ledger (choice, what it reversed, reason).
`docs/SUMMARY.md` is the narrative history; `docs/DEV_PLAN.md` and
`docs/stages/` hold the plan and its rationale; `docs/registers/` holds
deferred items and open questions; `docs/SOP.md` and `CLAUDE.md` describe how
the two-actor development process (project chat for design, Claude Code for
implementation) runs.
