# Go stack defaults

Use these defaults to assemble a Go stack around the project's profile and
constraints. Apply the shared [decision criteria](../decision-criteria.md)
for tool evaluation, release verification, and audit health.

Jump to: [Toolchain](#toolchain-and-modules) · [Profiles](#profile-rest-api) ·
[Worker](#profile-worker-and-batch-jobs) · [Data](#data-layer) · [Testing](#testing) ·
[Quality](#code-quality-and-structure) · [Operations](#observability-and-deployment)

## Toolchain and modules

- **Go:** each major release is supported until two newer major releases
  exist; verify the current pair in the official release history. Choose the
  latest supported release that the dependencies and build platform support.
- The `go` directive in `go.mod` is an enforced minimum and sets the language
  version; it also selects GODEBUG runtime defaults, so raising it can change
  runtime behavior. The `toolchain` directive only suggests a newer toolchain.
  A library should not raise `go` beyond what it needs.
- With the default `GOTOOLCHAIN=auto`, the `go` command may download a newer
  toolchain. In CI, install the intended release and set `GOTOOLCHAIN=local`
  so a mismatch fails instead of switching silently.
- Commit `go.mod` and `go.sum`; run `go mod tidy -diff` in CI to fail on drift
  and `go mod verify` to check the module cache. Set `GOPRIVATE` for private
  modules so they bypass the public proxy and checksum database, and apply the
  private-registry rule in the decision criteria.
- Track generators with `go.mod` `tool` directives unless a tool recommends
  binary installation.

## Profile: REST API

- **net/http with `ServeMux`** is the starting point: its patterns support
  methods and wildcards with `Request.PathValue`. Set `http.Server` timeouts
  and request body limits explicitly.
- Add **chi** when route groups and middleware composition justify a router
  that keeps standard `net/http` handlers. Choose **Echo** or **Gin** for team
  familiarity; their handler and context types shape middleware and tests, so
  verify the current major and its migration notes.
- For contract-first OpenAPI, oapi-codegen generates server interfaces and
  types. Validate input explicitly or with go-playground/validator.

## Profile: MCP server

- Start with the official MCP Go SDK (`modelcontextprotocol/go-sdk`). Compare
  a community SDK such as mcp-go only when a documented required capability is
  unavailable. Verify the protocol versions the SDK release supports.
- Use the SDK's stdio transport for a client-launched process and its
  Streamable HTTP handler for remote clients; keep the legacy SSE transport
  for older peers only. Verify the SDK's bearer-token middleware and OAuth
  helpers against the intended clients.
- Verify whether the SDK version validates `Origin`; otherwise add it. Bind
  local HTTP to loopback, never pass tokens through, and do not treat sessions
  as authentication. Apply the
  [MCP security requirements](../security.md#mcp-servers) and the
  [deployment](../deployment.md) guidance; stdio servers need process
  permissions and stderr logging instead.

## Profile: GraphQL API

- **gqlgen** is a starting point for schema-first servers with generated
  resolvers. Configure its complexity limit and weight expensive list fields.
- Enforce authorization at resource and field boundaries; batch data loading
  to avoid N+1 queries.

## Profile: gRPC service

- **grpc-go with protobuf-go** is the starting toolchain. Verify that the
  generator plugins and runtime libraries are compatible.
- Buf is optional for schema lint, breaking-change checks, and generation.
- Choose **Connect** (connect-go) when browser or HTTP/JSON callers need the
  same services without a proxy; it serves gRPC, gRPC-Web, and Connect and
  interoperates with grpc-go.
- Register the gRPC health service, use `GracefulStop` on shutdown, and verify
  HTTP/2, ingress, and health-check support on the deployment platform.

## Profile: worker and batch jobs

Apply the shared [worker and job guidance](../deployment.md#workers-scheduled-work-and-batch-jobs)
for execution platforms, delivery semantics, and alerting.

- **Library:** compare **River**, a PostgreSQL-backed queue that can enqueue
  in the same transaction as the business change, with **asynq**, a
  Redis-backed queue that fits an existing Redis deployment. Check each
  library's release maturity, supported Redis topologies, and which features
  need a commercial tier. Verify the current license of each library and the
  Redis server.
  A platform-run batch job can be a plain `main` without a queue library.
- **Idempotency and retries:** make handlers safe to repeat and bound
  retries. Exhausted work ends in a failed state (River's discarded jobs,
  asynq's archive) that needs an owner, alert, and replay procedure; check
  whether dead-letter handling needs a paid tier. Verify defaults before
  relying on them.
- **Scheduling:** use the library's periodic jobs or the platform scheduler,
  with one scheduler or a lock so replicas do not duplicate runs.
- **Shutdown:** derive a context from `signal.NotifyContext`, pass it to every
  job, and return `ctx.Err()` when cancelled; a nil return marks success.
  Use River's soft stop timeout or asynq's `ShutdownTimeout` within the
  platform grace period, and close the database pool after workers stop.
- **Concurrency:** size River queue workers, asynq `Concurrency`, or an
  `errgroup` limit from downstream limits and the connection pool.
- **Observability:** log job IDs and attempts with `slog`; River has an
  OpenTelemetry middleware in rivercontrib. Verify instrumentation for asynq.

## Data layer

Add persistence, caches, and workers only for an identified requirement.

- **PostgreSQL with pgx** is the relational starting point; use `pgxpool` for
  concurrent access, or `database/sql` through pgx's adapter when a library
  requires that interface. Use Docker/Compose locally and a managed database
  or deliberately operated OCI service in production, subject to constraints.
- **sqlc** generates typed Go from SQL and supports pgx; hand-written queries
  are viable for small schemas. Evaluate an ORM only for a concrete need.
- Choose **goose** (SQL and Go migrations), **golang-migrate** (CLI and
  library), or **Atlas** (declarative or versioned) for migrations. Atlas's
  Community Edition and its standard distribution have different licenses.
  One tool owns the schema; integrate River's migrations into it.
- Background jobs follow the
  [worker and batch jobs profile](#profile-worker-and-batch-jobs).

## Testing

- **`go test`** with table-driven subtests (`t.Run`) is the default. Run
  `-race` in CI; it requires cgo and a C compiler and increases memory and run
  time, so size the CI job accordingly.
- Use `net/http/httptest` for handlers and in-process servers.
- **testcontainers-go** (PostgreSQL and Redis modules) or isolated CI service
  containers support integration tests; it needs a Docker-compatible runtime.
- testify is optional when the team prefers assertion helpers.

## Code quality and structure

- **gofmt** is required; goimports also manages imports. `go vet` runs in CI.
- **golangci-lint** is a starting runner that includes govet, staticcheck, and
  formatters; install the binary as its documentation recommends and verify
  its license against tool policy. Run staticcheck directly for a smaller set.
- Scan with govulncheck as the
  [dependency scanning guidance](../security.md#dependency-and-supply-chain-scanning)
  describes. Source mode reports vulnerable functions reachable from the
  code; binary mode is less precise; reflection and `unsafe` can hide calls.
  Findings cannot be suppressed, and JSON or SARIF output exits 0.
- Use `cmd/<command>` for binaries and `internal/` for server packages; split
  modules only when other projects need shared code.

## Observability and deployment

- **`log/slog`** with its JSON handler is the logging starting point. Redact
  secrets and sensitive fields.
- Use OpenTelemetry Go with otelhttp and the otelslog bridge as needed; verify
  each signal's current stability and define the destination. Never expose
  `net/http/pprof` publicly.
- With `CGO_ENABLED=0`, pure Go code builds a static binary for distroless
  static or scratch. Cgo is on by default for native builds with a C compiler,
  so set it explicitly; with cgo the image needs the C library the binary
  links against.
- Distroless static includes CA certificates, tzdata, and a `nonroot` tag. On
  scratch, copy CA certificates, embed `time/tzdata`, and set a numeric
  non-root user. Pin images by digest per the decision criteria.
- **GOMAXPROCS:** when the main module's `go` directive is 1.25 or later, the
  Linux default follows the cgroup CPU limit (not CPU requests) and updates
  periodically; with 1.24 or earlier it is the logical CPU count. Setting
  `GOMAXPROCS` disables this behavior.
- **GOMEMLIMIT** is a soft limit for total runtime memory, not an OOM guarantee.
  When the process owns the container, leave about 5–10% headroom per the GC
  guide; measure for thrashing near the limit.
- On SIGTERM call `http.Server.Shutdown` within the platform grace period.
  Platform settings are covered by the [deployment guide](../deployment.md).
