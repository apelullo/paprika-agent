# Stage 2 — Local Network Deployment
## Implementation Plan & Architectural Decisions

> **Living document** — no date suffix; git supplies the history. Migrated in-repo
> 2026-07-23 from the desktop planning file (now archive, not source).
> Amended 2026-09-22/23 (pass 20260922): stage numbers 1-7; Pieces 4-5 folded into 3;
> Piece 3 extension point corrected to `TokenVerifier`; `MCP_HOST` rule recorded.
>
> **Status:** Pieces 0-2 complete; **Piece 3 (auth, health, CI gate) next**, as Pass B.
> Pieces 4 and 5 were folded into Piece 3 on 2026-09-22; Pieces 6 and 7 keep their
> numbers.
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
**Decision:** Machine-specific `.env` files; no config files until Stage 7. A frozen
`ServerConfig` resolved by `ServerConfig.from_env(env)`.
**Rationale:** Env vars are the twelve-factor standard for separating config from
code, and `.env` is already the project convention. Encrypted credential storage in a
database (Stage 7) stays compatible — the env var holds the key or DSN; the database
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
token; one key per device; OAuth 2.1 deferred to Stage 7.
**Rationale:** Binding to a specific interface limits exposure to the home network.
Bearer tokens are the direct precursor to OAuth — learning them now makes Stage 7 a
natural upgrade, not a rewrite. Per-device keys enable revocation without disrupting
other users. `0.0.0.0` exposes the server on all interfaces, including any untrusted
networks the machine may join.
**Static IP vs mDNS:** Static IP (DHCP reservation in router) chosen over mDNS
`.local` for Stage 2 — it builds the correct mental model (IP is the address; DNS is
an abstraction on top), and Windows mDNS support is inconsistent (relevant when the
desktop joins at Stage 5). mDNS revisitable as a convenience layer later.
**`MCP_HOST` validation (decided 2026-09-23, ships in Piece 3):** IP literals only
via `ipaddress.ip_address`; hostnames including `localhost` raise at startup;
`0.0.0.0` and `::` are rejected outright. An explicit opt-in for bind-all is
deferred to Stage 7.

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
| `server.py` | FastMCP app instance, MCP tool definitions (delegate to `paprika_client`), transport startup, auth (a `TokenVerifier` wired at construction), health endpoint |

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

### Piece 3 — Auth, health, CI gate  ◄ NEXT (Pass B)
Per-device bearer-token auth, the unauthenticated health endpoint, and the CI gate,
folded together 2026-09-22: the health bypass is a framework property that needs a
guard test, and a `tests/integration/` suite runs unfiltered in CI until markers
exist. Design proposal and commit plan: `docs/_auxiliary/piece3_design_20260922.md`.

**3a. Auth.** FastMCP's extension point is a `TokenVerifier` subclass in a new
`auth.py` (`verify_token(token) -> AccessToken | None`), not middleware: FastMCP's
`Middleware` class operates on MCP messages and never sees HTTP headers, while the
framework's own `RequireAuthMiddleware` wraps the MCP route, calls the verifier, and
returns `401` with `WWW-Authenticate` when the header is missing or the verifier
returns `None`. Keys load from `MCP_API_KEY_<DEVICE>` into
`ServerConfig.api_keys: tuple[DeviceKey, ...]` (http branch only; at least one
required; an empty suffix, an empty token, or a duplicate token is a `ValueError`;
`DeviceKey.token` is excluded from `repr`). The device name is returned as
`AccessToken.client_id`. A `create_server(config)` factory builds the app with `auth=`
at construction, in a structural commit before the auth commit.

**Security note:** tokens are compared as bytes with `hmac.compare_digest`, never
`==`. Each comparison is constant-time in the token contents; looping the configured
keys still varies with their number and stops at the first match. On a home LAN with
a handful of devices that leak is immaterial and is accepted, not hidden behind an
unqualified "constant-time".

**Revocation:** remove the key from `.env`, restart the server. A direct conceptual
precursor to OAuth token revocation in Stage 7.

**`MCP_HOST` validation** (own commit): `ipaddress.ip_address`, IP literals only;
`localhost` and other hostnames raise at startup; `0.0.0.0` and `::` are rejected
outright. An explicit opt-in for bind-all is deferred to Stage 7.

**3b. Health.** `@mcp.custom_route("/health", methods=["GET"])` returning
`{"status": "ok"}`. Custom routes are added outside `RequireAuthMiddleware` by
construction, so the bypass is free, and a comment cannot fail: a guard test locks it
(same app instance: `/mcp` without a token → 401, `/health` → 200).

**Why it matters:** `curl http://192.168.x.x:8000/health` isolates the failure layer:
response → server up, problem in auth/MCP; no response → server down or network
broken; `401` → the guard test is wrong or the route moved.

**3c. Tests + CI.** Unit: config key parsing (branch scoping, the three `ValueError`
cases, zero keys); `verify_token` (valid → device name; unknown or empty → `None`).
HTTP (`tests/integration/`, marker `integration`, runs in CI): missing header → 401;
wrong token → 401; each device's token independently valid; the health guard. Driven
through Starlette's `TestClient` against `mcp.http_app(json_response=True)` (lifespan
runs on `__enter__`); the in-process `fastmcp.Client` bypasses HTTP and cannot test
auth. Markers `integration` and `live` registered in `pyproject.toml`; CI runs
`-m "not live"`. Existing tool tests pass unchanged (transport transparency); the four
config tests that resolve http mode gain a key, since zero keys is now a `ValueError`.
Two cases carried from the old Piece 5 list: the `/health` body is exactly
`{"status": "ok"}`; a key removed from the environment is rejected on the next config
resolve (revocation).

**What this teaches:** the composition root (dependency injection at construction vs
mutation after); authentication (who are you?) vs authorization (what may you do?),
the latter arriving with OAuth 2.1 in Stage 7; test tiers by I/O boundary and the
difference between a comment and a guard.

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
Piece 3  Auth + health + tests/CI  (3a auth · 3b /health · 3c gate)  ◄ NEXT (Pass B)
   │     ◄── gate: all green before leaving the repo
   │     Pieces 4 and 5 folded in 2026-09-22; 6 and 7 keep their numbers
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
   auth; auth doesn't know about tools; the health bypass is a framework property
   locked by a guard test, not a comment.
3. **Infrastructure vs. application config:** static IP lives in the router, not the
   repo. `.env` holds runtime config. Code holds no secrets and no environment
   assumptions.
4. **Progressive security:** bearer tokens now → OAuth 2.1 at Stage 7. Each stage
   teaches the concept the next builds on.
5. **Gate discipline:** tests must be green before deployment. The repo is always in a
   deployable state.

---

## Deferred (do not implement in Stage 2)

Deferred items live in [docs/registers/deferred.md](../registers/deferred.md) and unvetted ideas in [docs/_auxiliary/ideas_20260922.md](../_auxiliary/ideas_20260922.md) (consolidated 2026-09-22, pass 20260922).
