# Paprika Agent

An MCP server that connects Claude Desktop to the Paprika recipe manager
app via its unofficial API.

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

Create a `.env` file in the repo root:

```
PAPRIKA_EMAIL=your@email.com
PAPRIKA_PASSWORD=yourpassword
```

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

## Architecture

Paprika Agent is built around a single guiding principle: **every design
decision should extend naturally, not require replacement as the project grows.**

On first tool call, the server eagerly fetches all recipes from the Paprika
API and populates two module-level structures: `_recipe_cache` (uid → full
recipe data) and `_name_index` (normalized name → uid). Subsequent calls are
pure in-memory lookups — zero additional API calls. This cache is the
foundation all current tools share and the natural predecessor to a persistent
local database. A `_cache_populated` flag tracks whether the cache has been
populated at least once, keeping the no-op guard correct for accounts with
zero recipes.

Tools are thin by design. Each one calls `_populate_cache()`, reads from the
shared cache, and returns a result. `search_recipes` today does substring
matching over titles; tomorrow it does semantic search over embeddings — same
tool interface, smarter implementation underneath. The architecture doesn't
change; the sophistication grows inside it.

## Tech Stack
Python · FastMCP · uv · Paprika API

## Roadmap
- [ ] Local network deployment
- [ ] Custom client
- [ ] Cloud deployment
- [ ] Recipe recommender system
