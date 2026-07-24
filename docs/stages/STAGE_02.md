# Stage 2 — Local Network Deployment
## Implementation Plan & Architectural Decisions

> **Living document** — no date suffix; git supplies the history. Migrated in-repo
> 2026-07-23 from the desktop planning file (now archive, not source).
>
> **Status:** Pieces 0–2 complete; **Piece 3 (auth) next.**
>
> **Precedence rule:** where this file and the repo disagree on *current detail*,
> the repo wins (`config.py`, `server.py`, `docs/DEV_PLAN.md`, the Decision Log).
> This file is authoritative for **sequence and rationale**, not live implementation
> detail.

---

## Architectural Decisions

### Transport: Streamable HTTP
**Decision:** Build Streamable HTTP from the start. Do not use SSE.
**Rationale:** HTTP+SSE was deprecated by the MCP spec 2025-03-26, which introduced
Streamable HTTP; the spec still documents SSE backward-compatibility and FastMCP
3.2.4 still accepts `sse`. There is no protocol-wide removal date — 2026 deadlines
are vendor-specific (e.g. Keboola 2026-04-01, Atlassian Rovo 2026-06-30). Streamable
HTTP is the current standard and Claude Desktop supports it; building on it now
avoids a later migration with no learning benefit. *(The desktop source stated a hard
SSE cutoff date — a vendor deadline mistaken for a protocol removal; corrected in
`DEV_PLAN.md` at `945631b`.)*
**Key property:** Transport is transparent to tool logic — no tool code changes when
switching transports. Intentional separation of concerns (hexagonal architecture).

### Config: Env vars + value-authoritative resolution
**Decision:** Machine-specific `.env` files; no config files until Stage 6. A frozen
`ServerConfig` resolved by `ServerConfig.from_env(env)`.
**Rationale:** Env vars are the twelve-factor standard for separating config from
code, and `.env` is already the project convention. Encrypted credential storage in a
database (Stage 6) stays compatible — the env var holds the key or DSN; the database
holds the secrets.
**Resolution is value-authoritative** (shipped in Piece 1, superseding the desktop
source's presence-based sketch):
- `MCP_TRANSPORT` unset → `stdio`; set → validated against `{stdio, http}`;
  unknown/empty → `ValueError`.
- Host/port resolution + validation are scoped to the `http` branch only — stdio
  never inspects `MCP_HOST`/`MCP_PORT`.
- Fail-closed default host `127.0.0.1`; default port `8000`; port range `1–65535`.
- `from_env(env: Mapping)` reads only the injected mapping, never `os.environ`
  directly — a pure, unit-testable resolver.

**Dev machine:** `MCP_TRANSPORT` absent or `stdio` → runs locally, unchanged.
**Server machine:** transport + host/port set → serves over network.

### Security: Static LAN IP + per-device bearer tokens
**Decision:** Bind to static LAN IP (not `0.0.0.0`); authenticate via HTTP bearer
token; one key per device; OAuth 2.1 deferred to Stage 6.
**Rationale:** Binding to a specific interface limits exposure to the home network.
Bearer tokens are the direct precursor to OAuth — learning them now makes Stage 6 a
natural upgrade, not a rewrite. Per-device keys enable revocation without disrupting
other users. `0.0.0.0` exposes the server on all interfaces, including any untrusted
networks the machine may join.
**Static IP vs mDNS:** Static IP (DHCP reservation in router) chosen over mDNS
`.local` for Stage 2 — it builds the correct mental model (IP is the address; DNS is
an abstraction on top), and Windows mDNS support is inconsistent (relevant when the
desktop joins at Stage 4). mDNS revisitable as a convenience layer later.

### Server machine: MacBook Air + launchd
**Decision:** MacBook Air as always-on server; `launchd` for process management.
**Rationale:** `launchd` is macOS's native service manager — boot startup, crash
recovery, logging. Right tool for persistent services (vs. cron, for scheduled
tasks). The server process is network-agnostic: it binds to the LAN IP and listens;
if the network drops and returns, the server keeps running and MCP clients reconnect.

---

## Implementation Pieces

### Piece 0 — Refactor: split `server.py` ✅ (2026-06-25)
**Why first:** Stage 2 adds transport config, middleware, and a health endpoint to
the MCP side; adding all that to a single-file server produces an unmanageable file.
Easier to split while the code is stable and tests are green.

| File | Responsibility |
|---|---|
| `paprika_client.py` | Paprika API calls, `_recipe_cache`, `_name_index`, `_cache_populated`, `_populate_cache`, `_normalize`, `_validate_input_string`, semaphore, timeout constant |
| `server.py` | FastMCP app instance, MCP tool definitions (delegate to `paprika_client`), transport startup, auth middleware, health endpoint |

Two commits: `24c9d45` (structural split) + `090c099` (Option B — sync orchestration
extracted into `paprika_client.sync()` returning a `SyncResult`; `sync_recipes`
reduced to validate→delegate→format). `server.py` imports only
`dotenv`/`fastmcp`/`paprika_client` (no `asyncio`/`httpx`); `paprika_client` is the
sole mutator of `_cache_populated`, making the cache invariant structural. 33 tests,
CI green.

### Piece 1 — Config: `.env` schema + value-authoritative resolution ✅ (`35517e5`)
**Env vars:**
```
MCP_TRANSPORT=http            # unset or "stdio" → local dev mode
MCP_HOST=192.168.x.x          # static LAN IP of server machine (http mode only)
MCP_PORT=8000                 # explicit; never hardcoded (http mode only)
MCP_API_KEY_MACBOOK_PRO=...   # per-device key (reserved; loaded at Piece 3)
MCP_API_KEY_WIFE_LAPTOP=...   # per-device key
# add keys as devices are onboarded
```

Shipped as a frozen `ServerConfig` + `ServerConfig.from_env(env)` in `config.py` —
value-authoritative (see Architectural Decisions above), not the presence-based
sketch the desktop source showed. `.env.example` documents the full
contract; `.env` verified in `.gitignore`. Suite 33 → 46.

### Piece 2 — Transport: Streamable HTTP startup ✅ (`3e21a04`, `bd5462e`)
Wire FastMCP to start with the transport determined by Piece 1's config. Stdio path
unchanged — local dev unaffected. A `_run_kwargs(config)` adapter feeds
`mcp.run(**kwargs)`; **host/port are omitted (not `None`) in stdio mode**, because
`run()` forwards `**kwargs` to `run_stdio_async()`, which has no such params and
raises `TypeError` on unexpected keywords. Transport is passed explicitly so a stray
`FASTMCP_TRANSPORT` in `.env` cannot redirect (FastMCP reads the same `.env` with
prefix `FASTMCP_`). Contract value renamed `streamable-http` → `http`. Suite 46 → 51.
**What this taught:** how FastMCP exposes transport config; what binding to a
host:port means at the socket level.

### Piece 3 — Auth middleware: bearer token + per-device keys  ◄ NEXT
A request interceptor that runs before any tool call or endpoint handler (except
health — see Piece 4).

**Behavior:**
- Checks `Authorization: Bearer <key>` on every incoming request.
- Validates against the list of active per-device keys from `.env`.
- Returns `401` if the header is missing or the key is unrecognized.

**Security note:** compare the supplied token against each valid key with
`hmac.compare_digest`, never `==`. Constant-time comparison avoids leaking key length
or contents through timing. Apply from the first implementation.

**Revocation:** remove the key from `.env`, restart the server. Simple, explicit, a
direct conceptual precursor to OAuth token revocation in Stage 6.

**Also carries:** `MCP_HOST` format validation (`ipaddress` stdlib — currently
unvalidated, fails late at uvicorn bind); the first `tests/integration/` suite.

**What this teaches:** authentication (who are you?) vs. authorization (what are you
allowed to do?) — auth middleware handles the former; the latter arrives in Stage 6
with OAuth 2.1.

### Piece 4 — Health endpoint: unauthenticated `GET /health`
```json
{"status": "ok"}
```
**Critical design decision:** this endpoint explicitly bypasses auth middleware.
Health checks must be reachable by monitoring tools and manual debugging without
credentials. Document the bypass as intentional in code comments.

**Why it matters:** `curl http://192.168.x.x:8000/health` isolates the failure layer —
response → server up, problem in auth/MCP; no response → server down or network
broken; `401` → auth running but health bypass misconfigured.

### Piece 5 — Tests + CI updates
**New tests:** auth middleware (valid key passes; missing header → 401; wrong key →
401; per-device key independently valid; revoked key → 401); health endpoint
(reachable without auth; expected shape); transport resolution (stdio default when
`MCP_TRANSPORT` absent; http mode when set).
**Existing tests:** all pass unchanged (transport transparency).
**CI:** network/integration tests marked and excluded: `pytest -m "not integration
and not network"`.

**This is the gate before touching the MacBook Air. Do not proceed to Piece 6 until
CI is green.**

### Piece 6 — MacBook Air setup *(first time leaving the repo)*
**6a. Static IP — router admin panel.** Assign by MAC address. One-time. Do this
first — you need the IP before configuring anything else.
**6b. Environment check + repo setup.**
```bash
python3 --version   # verify 3.13
uv --version        # install if absent
git clone https://github.com/apelullo/paprika-agent
cd paprika-agent
uv sync
```
**6c. `.env` on the Air.** Populate with the static IP from 6a plus all server-mode
vars and per-device keys.
**6d. `launchd` plist.** Start on boot, restart on crash, log stdout/stderr to file.
⚠️ **Absolute paths required** — `launchd` does not inherit your shell environment; a
relative path produces a silent failure.
⚠️ **`.env` discovery under launchd** — `load_dotenv()` searches from the process
working directory, which launchd sets to `/`, not the repo. Set `WorkingDirectory` in
the plist *or* pass an explicit `load_dotenv(dotenv_path=...)`, or the server starts
with no credentials.
**6e. macOS firewall check.** When the server first binds to its port, macOS may
prompt to allow or block incoming connections. Allow it. If no prompt appears, verify
in System Settings → Network → Firewall.

### Piece 7 — Claude Desktop config *(client side, each machine)*
Add a remote MCP entry to `claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "paprika-remote": {
      "url": "http://192.168.x.x:8000/mcp",
      "headers": { "Authorization": "Bearer <device-key>" }
    }
  }
}
```
Default endpoint path is `/mcp`. **Keep the existing stdio entry** — both coexist:
`paprika-remote` (network use) and `paprika-local` (existing stdio, for isolated
debugging when the failure source is unknown).

---

## Full Sequence

```
Piece 0  Refactor (server.py → server.py + paprika_client.py)          ✅
   │
Piece 1  Config (.env schema, value-authoritative resolver, .gitignore) ✅
   │
Piece 2  Transport (Streamable HTTP startup in server.py)              ✅
   │
Piece 3  Auth middleware (bearer token + per-device keys)             ◄ NEXT
   │
Piece 4  Health endpoint (unauthenticated GET /health)
   │
Piece 5  Tests + CI  ◄── gate: all green before leaving the repo
   │
Piece 6  MacBook Air setup
         6a. Static IP (router)
         6b. Environment check + clone + uv sync
         6c. .env on the Air
         6d. launchd plist (absolute paths, logging, crash recovery)
         6e. macOS firewall check
   │
Piece 7  Claude Desktop config (remote entry + keep stdio entry)
```

---

## Key Architectural Properties

1. **Transport transparency:** tool logic has no knowledge of how requests arrive or
   responses leave. Swapping transports requires zero changes to tool code.
2. **Separation of concerns:** each piece has one job. Transport doesn't know about
   auth; auth doesn't know about tools; the health bypass is explicit, not accidental.
3. **Infrastructure vs. application config:** static IP lives in the router, not the
   repo. `.env` holds runtime config. Code holds no secrets and no environment
   assumptions.
4. **Progressive security:** bearer tokens now → OAuth 2.1 at Stage 6. Each stage
   teaches the concept the next builds on.
5. **Gate discipline:** tests must be green before deployment. The repo is always in a
   deployable state.

---

## Deferred (do not implement in Stage 2)

- Auto-sync on client connect (natural follow-on to the `_cache_populated` sentinel —
  revisit at Stage 3)
- Cache/database warming on server startup (revisit at Stage 2.5)
- Centralize test fixtures (factory fixture in `tests/conftest.py`) — just before the
  Stage 2.5 schema change; mutation-safe shared recipe data
- Windows desktop as compute offload node (Stage 4 — distributed task queue)
- mDNS `.local` hostname (convenience layer — revisit if static IP becomes painful)
- OAuth 2.1 (Stage 6)
