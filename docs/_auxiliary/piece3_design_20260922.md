# Piece 3 design proposal: auth, health, CI gate

**Status:** in-progress
**Closes when:** Pass B's spec (`docs/spec/spec_stage2_piece3_<pass>.md`) is written
from this file and consumed
**Last updated:** 2026-09-24

Chat-authored design for Stage 2 Piece 3, settled in pass `20260922` (2026-09-22 to
2026-09-23). Every decision here has a `DECISIONS.md` line dated 2026-09-22 or
2026-09-23. Pass B (a new chat, first pass under doc process v4) turns this into the
spec; nothing below is implemented yet.

## 1. Verified against installed source (FastMCP 3.2.4, Starlette, CPython 3.12/3.13)

| Fact | Where |
|---|---|
| `TokenVerifier.verify_token(token) -> AccessToken \| None` is the extension point; `AccessToken` needs `token`, `client_id`, `scopes` | `fastmcp/server/auth/auth.py` |
| `create_streamable_http_app` wraps only the MCP route in `RequireAuthMiddleware`; `custom_route`s are added outside it; `AuthenticationMiddleware` + `AuthContextMiddleware` are app-level and never reject | `fastmcp/server/http.py` |
| `RequireAuthMiddleware` returns 401 + `WWW-Authenticate` on missing header or `verify_token() is None`; `BearerAuthBackend.authenticate` returns `None` rather than raising | `fastmcp/server/auth/middleware.py`, `mcp/server/auth/middleware/bearer_auth.py` |
| `FastMCP(auth=...)` is stored as `self.auth` and read at `http_app()` time inside `run_http_async`; stdio never touches it | `fastmcp/server/mixins/transport.py` |
| `StaticTokenVerifier` does `self.tokens.get(token)` (dict lookup) and self-documents as not for production | `fastmcp/server/auth/providers/jwt.py` |
| `hmac.compare_digest('abc', 'abc')` works; non-ASCII `str` raises `TypeError`; bytes always work | run on 2026-09-22 |
| Starlette `TestClient.__enter__` starts lifespan | `starlette/testclient.py:687` |
| Existing tests call tool functions directly (`asyncio.run(list_recipes())`) | `tests/test_server.py` |
| `pyproject.toml` registers no pytest markers; `ci.yml:18` runs `uv run pytest tests/ -v` unfiltered | Code, 2026-08-01 |
| `FastMCP.http_app()` accepts `json_response=` | `fastmcp/server/mixins/transport.py` |

## 2. Decisions (ratified)

| # | Decision |
|---|---|
| D1 | New fourth module `auth.py`: `DeviceTokenVerifier(TokenVerifier)`. `config.py` stays framework-free; `server.py` stays MCP-only |
| D2 | `config.py`: frozen `DeviceKey(device: str, token: str = field(repr=False))`; `ServerConfig.api_keys: tuple[DeviceKey, ...]`, sorted by device, populated only in the `http` branch from every `MCP_API_KEY_<DEVICE>` in the injected mapping. Bytes encoding happens in `auth.py` (adapter into the `hmac` boundary) |
| D3 | `create_server(config: ServerConfig) -> FastMCP` factory in `server.py`: tools become plain module-level `async def`s registered inside the factory via `mcp.tool(fn)`; `mcp` leaves module scope; `auth=` and the health route are attached at construction; `__main__` becomes `config = ServerConfig.from_env(os.environ); create_server(config).run(**_run_kwargs(config))`. Structural commit, before auth. Existing tests import the functions and stay unchanged |
| D4 | `http` mode with zero keys raises `ValueError` at `from_env` |
| B5 | Empty device suffix (`MCP_API_KEY_=`), empty token, or a token shared by two devices raises `ValueError`. No minimum length; `.env.example` documents `python -c "import secrets; print(secrets.token_urlsafe(32))"` |
| B6 | `MCP_HOST`: `ipaddress.ip_address` (IP literals only; hostnames including `localhost` raise) and reject `0.0.0.0` / `::`. Own commit |
| B7 | `/health` bypass locked by a guard test (same app: `/mcp` without a token → 401, `/health` → 200) |
| B8 | Markers `integration` (CI runs; `-m integration` selects) and `live` (CI excludes via `-m "not live"`); HTTP tests via `TestClient(mcp.http_app(json_response=True))`; no new dependency |
| fold | Pieces 4 and 5 are inside this piece; 6 and 7 keep their numbers |

## 3. Commit plan (Pass B)

| # | Kind | Commit |
|---|---|---|
| 1 | structural | `refactor(server): create_server factory; tools registered at construction` |
| 2 | logical | `feat(auth): per-device bearer tokens via TokenVerifier` (auth.py, config.py keys, server wiring, unit tests) |
| 3 | logical | `feat(config): validate MCP_HOST as an IP literal; reject bind-all` |
| 4 | logical | `feat(server): unauthenticated GET /health with auth-bypass guard test` |
| 5 | tooling | `test: integration and live markers; CI excludes live; HTTP auth suite` |
| 6 | docs | `.env.example` (key contract, generator command), `CLAUDE.md` Architecture (four modules, factory), README (Architecture, Roadmap), `project_development_plan.md` |

Each commit leaves the suite green. Commit 1 must not change behaviour (verify: 51
tests pass before the next commit).

## 4. Test plan

**Unit, `tests/test_config.py`:** keys ignored in stdio; keys parsed in http (device
name from suffix, order by device); zero keys → `ValueError`; empty suffix → `ValueError`;
empty token → `ValueError`; duplicate token → `ValueError`; `repr(config)` contains no
token; four existing http tests gain one key. `MCP_HOST`: valid v4 and v6 literals pass;
`localhost` raises; `0.0.0.0` and `::` raise.

**Unit, `tests/test_auth.py`:** `verify_token` returns `AccessToken(client_id=<device>)`
for each configured token; `None` for unknown, empty, and a prefix of a valid token;
non-ASCII input does not raise.

**HTTP, `tests/integration/test_auth_http.py` (`integration` marker):** app from
`create_server(config)` with two device keys, `json_response=True`; missing header →
401 with `WWW-Authenticate`; wrong token → 401; each device's token → initialize
succeeds; health guard (same app instance, both assertions); the `/health` body is
exactly `{"status": "ok"}`; a key removed from the environment is rejected on the next
config resolve (revocation). One `live`-marked placeholder is not needed; the marker is
registered for the deferred live tests (deferred.md items 2 and 3).

**Guard tests (signature):** `create_server` returns a `FastMCP` whose `auth` is a
`TokenVerifier` in http mode and `None` in stdio mode.

## 5. Teaching beats for Pass B (in order)

1. Composition root: why constructor injection beats mutating `mcp.auth`, and why the
   framework's lazy read would have made the mutation *work* while still being wrong.
2. The three layers (MCP-message middleware, ASGI middleware, verifier policy) and how
   to locate an extension point by reading the framework, not its docs.
3. `hmac.compare_digest` semantics: constant-time per comparison; the N-key loop leak;
   why bytes.
4. Structural bypass vs explicit bypass, and why a guard test is the honest form.
5. Test tiers by I/O boundary: unit / integration-in-process / live; why the in-process
   client cannot test auth; why `json_response=True` is a test choice, not a behaviour change.
6. `repr=False` and secrets in tracebacks.

## 6. Open for Pass B

- Exact `DeviceKey` field order and whether `ServerConfig.api_keys` defaults to `()`.
- Whether commit 2's unit tests and commit 5's HTTP tests land together or apart
  (recommendation: apart, so the marker change is its own diff).
- Whether the `/health` response should carry a version field (recommendation: no;
  Stage 7 observability decides).

## 7. Already applied by Pass A

`docs/stages/STAGE_02.md` Piece 3 section (3a/3b/3c), the Security decision's
`MCP_HOST` rule, and the Full Sequence block were amended in pass `20260922`; Pass B
does not restate them.
