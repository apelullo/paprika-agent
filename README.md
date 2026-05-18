# Paprika Agent

An MCP server that connects Claude Desktop to the Paprika recipe manager
app via its unofficial API.

## Features
- `list_recipes` — fetch and cache all recipes from your Paprika account
- `get_recipe` — retrieve full recipe details by name (case-insensitive)
- `search_recipes` — keyword search across recipe titles (order-independent)

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

## Tech Stack
Python · FastMCP · uv · Paprika API

## Roadmap
- [ ] Local network deployment
- [ ] Custom client
- [ ] Cloud deployment
- [ ] Recipe recommender system
