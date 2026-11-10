# Python stack defaults

Use these defaults to assemble a Python stack around the project's profile
and constraints. Apply the shared [decision criteria](../decision-criteria.md)
for tool evaluation, release verification, and audit health.

Jump to: [Runtime](#language-and-runtime) · [Profiles](#profile-rest-api) ·
[Worker](#profile-worker-and-batch-jobs) · [Data](#data-layer) · [Testing](#testing) ·
[Quality](#code-quality-and-structure) · [Operations](#observability-and-deployment)

## Language and runtime

- **Python:** choose the latest compatible, supported stable release after
  checking runtime support and the selected frameworks, drivers, deployment
  platform, and build wheels. Do not select a minor approaching EOL.
- **Version & package management:** uv is the default for runtime management,
  resolution, lockfiles, and workspaces. Poetry or pip-tools are reasonable
  when team conventions or a simpler dependency workflow justify them;
  document environment management separately when the tool does not own it.
- Commit the lockfile and make CI fail on a stale lock instead of updating
  it: `uv sync --locked` with uv, or the selected tool's equivalent check.

## Profile: REST API

- **FastAPI** is the default for typed ASGI APIs with OpenAPI requirements.
  Litestar is an alternative when its framework structure or dependency
  injection fits the project; compare the actual requirements.
- **Django with DRF or django-ninja** fits products needing an integrated
  admin, authentication, ORM, and migrations. Choosing Django replaces the
  default SQLAlchemy/Alembic pair and requires framework-specific settings,
  testing, deployment, and instrumentation decisions.
- **Flask** is viable for synchronous services when its simpler model and
  team experience fit. Async needs are a reason to compare ASGI frameworks,
  not evidence that an existing Flask application is unhealthy.
- For an ASGI application, uvicorn is a starting server choice. Add
  pydantic-settings for typed configuration or httpx for outbound HTTP when
  needed; these libraries are independent decisions.

## Profile: MCP server

- Start with the official MCP Python SDK. Compare a separate FastMCP package
  only when required composition, proxying, or authentication features justify
  it. Verify package identity, current APIs, stability, and SDK compatibility.
- Choose **stdio** for a client-launched local process or a supported remote
  transport such as **Streamable HTTP** for remote clients. Verify current
  protocol and SDK support; do not confuse legacy HTTP+SSE transport with SSE
  streaming used inside another transport.
- Remote or local HTTP deployments require compatible protocol authorization,
  `Origin` validation, loopback binding for local HTTP, no token passthrough,
  and sessions that are not used as authentication. Apply the
  [MCP security requirements](../security.md#mcp-servers) and the
  [deployment](../deployment.md) guidance. For stdio, assess local process
  permissions and lifecycle instead of HTTP requirements.

## Profile: GraphQL API

- **Strawberry** is a starting point for code-first typed schemas;
  **Ariadne** fits schema-first workflows. Assess Graphene or another existing
  framework by maintenance, integration, and migration cost.
- Document query complexity/depth limits and authorization at resource and
  field boundaries where needed.

## Profile: gRPC service

- **grpcio + grpcio-tools + protobuf** is the starting toolchain. Verify
  compatible generator/runtime versions and generated-code expectations.
- Buf is optional for schema checks and code generation workflows.
- Validate HTTP/2, connection lifecycle, ingress, and health-check support on
  the selected deployment platform before promising compatibility.

## Profile: worker and batch jobs

Apply the shared [worker and job guidance](../deployment.md#workers-scheduled-work-and-batch-jobs)
for execution platforms, delivery semantics, and alerting.

- **Library:** compare a broker-backed library, **Celery** (RabbitMQ or Redis)
  or **Dramatiq**, with a PostgreSQL-backed queue such as **Procrastinate**.
  The database-backed option avoids a broker and may enqueue in the same
  transaction as the business change; verify that capability. A broker fits
  higher throughput, routing, or fan-out. Verify maintenance, release activity, and the current
  license of the selected library and broker. A batch/ETL job run by the
  platform's job model can be a plain entry point without a queue library.
- **Idempotency and retries:** make tasks safe to run more than once, use the
  library's bounded retry and backoff settings, and route exhausted tasks to a
  dead-letter queue or failed-job state that someone owns and can replay.
  Verify when the library acknowledges a message relative to task completion.
- **Scheduling:** use the library's periodic-task feature or the platform's
  scheduler, with a single scheduler or a lock so replicas do not duplicate runs.
- **Shutdown and concurrency:** handle the platform's termination signal by
  stopping intake and finishing or releasing in-flight tasks within the grace
  period. Choose processes, threads, or async execution from the workload (CPU
  versus I/O) and the selected driver; keep worker and pool sizes within the
  database connection budget.
- **Observability:** log task identifiers and attempts in structured logs,
  export queue and task metrics, and select OpenTelemetry instrumentation for
  the chosen library only after verifying that a maintained one exists.

## Data layer

Add persistence, caches, and workers only for an identified requirement.

- **PostgreSQL** is the relational starting point. Use Docker/Compose locally
  and a managed database or deliberately operated OCI service in production,
  subject to user constraints. Embedded storage can be sufficient when sharing,
  durability, concurrency, and deployment requirements permit it.
- **SQLAlchemy + Alembic** fits non-Django relational applications; choose a
  driver compatible with synchronous or asynchronous execution. SQLModel is an
  alternative if its model approach fits the domain. Django uses its own ORM
  and migrations unless a documented integration justifies otherwise.
- Add **Redis** or a compatible server such as Valkey only for a concrete
  cache/session/coordination requirement; verify the current license of the
  selected server and edition against organization policy.
- Background jobs and their queue backend follow the
  [worker and batch jobs profile](#profile-worker-and-batch-jobs).
- Use the selected provider's object-storage API. An S3-compatible local
  service is suitable for an S3 integration; it does not establish parity with
  a GCS API. Record emulator/adapter limitations and integration coverage.

## Testing

- **pytest** is the default; add an async plugin matching the async library
  and version. Use pytest-cov when coverage reporting helps the quality gate.
- Use Django's testing integrations when Django is selected; account for its
  transaction, settings, and async behavior rather than assuming ASGI fixtures.
- **Testcontainers** or isolated CI service containers support database/broker
  integration tests. Confirm Docker availability; document managed test
  environments when the execution environment prohibits containers.
- httpx ASGI transport fits in-process ASGI tests. Test application lifespan
  explicitly where the transport does not manage it. Add real-network tests
  only for behavior that requires the server/protocol boundary.
- Choose factories and fixtures to fit the domain; they are optional.

## Code quality and structure

- **ruff** is the default linter/formatter. **mypy** is the default type
  checker, especially when framework plugins such as Django's or Pydantic's
  matter; choose **pyright** when editor integration or check speed favor it.
  Verify current plugin support for the selected frameworks.
- pre-commit is an optional local convenience; enforce required gates in CI.
  Adopt a commit convention only when it supports the release workflow.
- Prefer a `src/` package layout and `pyproject.toml` for supported tooling.
  Use feature modules as complexity grows; preserve Django's conventions when
  Django is selected. Do not require every tool's settings to fit one file.

## Observability and deployment

- Structured JSON logging via structlog or standard-library logging is a
  starting point. Redact secrets and sensitive fields.
- Select OpenTelemetry instrumentation for the framework actually chosen,
  with compatible exporters and a defined metrics/tracing destination.
  Error tracking is optional based on operational needs and data policy.
- For HTTP containers, verify the platform's required port, listening
  interface, startup checks, and shutdown contract. Derive workers and
  concurrency from workload measurements and resource limits.
- HTTP probes, containers, and Cloud Run are conditional deployment choices;
  local stdio tools need a process lifecycle and stderr logging strategy.
  Use the [deployment guide](../deployment.md) for platform verification.
