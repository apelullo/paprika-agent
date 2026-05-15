# Paprika Agent

An MCP server that connects Claude Desktop to the Paprika recipe manager
app via its unofficial API.

## Features
- `list_recipes` — fetch and cache all recipes from your Paprika account
- `get_recipe` — retrieve full recipe details by name (case-insensitive)
- `search_recipes` — keyword search across recipe titles (order-independent)

## Tech Stack
Python · FastMCP · uv · Paprika API

## Roadmap
- [ ] Local network deployment
- [ ] Custom client
- [ ] Cloud deployment
- [ ] Recipe recommender system
