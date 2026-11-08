# Python Stack Defaults

Opinionated defaults for Python profiles. Versions are deliberately NOT
recorded here — verify the latest stable at generation time (see
`decision-criteria.md`). Health classes as defined there.

## Language & runtime

- **Python:** latest stable minor release (verify at python.org). Avoid
  running on a minor in its final months before EOL.
- **Version & package management:** uv (default — manages Python itself,
  fast resolution, lockfile, workspaces; no pyenv/venv juggling).
  Alternatives: Poetry (mature; fine if the org standard), pip-tools
  (minimal; CAUTION — no environment management).

## Profile: REST API

- **FastAPI** — default. Async, Pydantic-native, OpenAPI built in, huge
  ecosystem. HEALTHY.
- **Litestar** — compare when dependency injection, performance, or a more
  structured larger app matter. HEALTHY.
- **Django (+ DRF or django-ninja)** — when batteries matter: admin, mature
  auth, ORM-first workflows. HEALTHY but heavier; changes several other
  defaults (Django ORM, its migrations, its settings system).
- ASGI server: **uvicorn** (default). Settings: **pydantic-settings**. HTTP
  client: **httpx**.

## Profile: MCP server

- **Official `mcp` SDK** (modelcontextprotocol/python-sdk, includes the
  FastMCP interface) — default. HEALTHY (young but official).
- **FastMCP 2.x** (jlowin/fastmcp) — when you need composition, proxies, or
  auth middleware beyond the official SDK. CAUTION (fast-moving; verify
  current stability).
- **Transport:** stdio for local agents; **Streamable HTTP** for remote
  deployments (SSE transport is deprecated). On Cloud Run: Streamable HTTP
  in a container.

## Profile: GraphQL API

- **Strawberry** — default (code-first, type-friendly, ASGI-native). HEALTHY.
- **Ariadne** — schema-first alternative. HEALTHY.
- **Graphene** — legacy; AVOID for new work.

## Profile: gRPC service

- **grpcio + grpcio-tools + protobuf** — official toolchain. HEALTHY.
- Buf for codegen/CLI DX is a reasonable add-on.
- Cloud Run: enable HTTP/2; the service must accept h2c.

## Data layer

- **Database:** PostgreSQL (default). Local: Docker/compose. Prod on GCP:
  Cloud SQL.
- **ORM:** SQLAlchemy 2.x (default) + **Alembic** migrations; asyncpg driver
  for async apps. SQLModel — thin FastAPI-flavored alternative; CAUTION for
  complex domains. Django ORM when Django was chosen.
- **Cache/sessions:** Redis (Memorystore on GCP).
- **Background jobs:** arq (default — async, Redis-based, simple) / Celery
  (mature, feature-rich, heavier, sync model) / Dramatiq (middle ground).
  Pick by requirements: scheduling, retries, routing complexity.
- **Blob storage:** GCS on GCP; MinIO via Docker for local parity.

## Testing

- **pytest** (default) + pytest-asyncio for async code; coverage via
  pytest-cov.
- **Integration:** Testcontainers-python (default when DB/Redis/broker
  involved).
- **HTTP testing:** httpx ASGI transport against the app (no live server).
- Fixtures/factories: polyfactory or factory-boy.

## Code quality

- **ruff** — lint + format (single tool). Default.
- **Type checking:** pyright (default) or mypy (ecosystem standard, slower).
  ty (Astral) is promising — CAUTION until stable; verify status.
- **pre-commit** hooks running ruff (+ type checker). Default: yes.
- Commits: Conventional Commits.

## Observability

- **structlog** — JSON structured logging (default).
- **OpenTelemetry** SDK + FastAPI instrumentation for traces/metrics.
- Sentry SDK for error tracking (optional, ask).

## Project structure

- `src/` layout; `pyproject.toml` as the single configuration surface (uv,
  ruff, pyright, pytest).
- Package-by-feature inside `app/` for anything nontrivial; flat modules
  acceptable for small services.

## Cloud Run notes

- Listen on `$PORT`; scale workers via `WEB_CONCURRENCY`.
- Graceful shutdown on SIGTERM (FastAPI/Starlette lifespan).
- `/healthz` endpoint for startup/liveness probes.
- min-instances 0 (cost) vs 1 (latency-sensitive public APIs).

## Avoid for new work

- Flask for new async APIs (fine for tiny sync tools).
- pipenv (stagnant), setup.py-only packaging, Graphene (new work).
