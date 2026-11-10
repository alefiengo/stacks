# .NET stack defaults

Use these defaults to assemble a .NET (C#) stack around the project's profile
and constraints. Apply the shared [decision criteria](../decision-criteria.md)
for tool evaluation, release verification, and audit health.

Jump to: [Runtime](#sdk-runtime-and-packages) · [Profiles](#profile-rest-api) ·
[Worker](#profile-worker-and-batch-jobs) · [Data](#data-layer) · [Testing](#testing) ·
[Quality](#code-quality-and-structure) · [Operations](#observability-and-deployment)

## SDK, runtime, and packages

- **Runtime:** start from a supported LTS release; choose STS only for a
  needed feature when the team will upgrade within its shorter window. Verify
  the official support policy, end-of-support dates, and framework, driver,
  and base-image support. Support requires staying on the latest patch.
- **SDK:** commit a `global.json` with an exact `sdk.version` and explicit
  `rollForward`, and install that SDK in CI. With lock files, use
  `rollForward: disable` so implicit SDK package references cannot break
  locked restores.
- **Central Package Management:** with several projects, declare versions in
  `Directory.Packages.props` (`ManagePackageVersionsCentrally`). Enable
  transitive pinning only for a concrete need: packing a library promotes
  pinned packages to dependencies. Map package sources when there are several.
- **Lock files:** for applications, set `RestorePackagesWithLockFile`, commit
  `packages.lock.json`, avoid floating versions, and run
  `dotnet restore --locked-mode` in CI. A library's lock file does not govern
  its consumers. Auditing follows the
  [dependency scanning guidance](../security.md#dependency-and-supply-chain-scanning).

## Profile: REST API

- **ASP.NET Core Minimal APIs** are the starting point, as the framework
  documentation recommends for new projects. Choose controllers for model
  binding or validation extensibility, application parts, OData, or an
  established MVC codebase.
- `Microsoft.AspNetCore.OpenApi` generates the OpenAPI document; it provides
  no UI, so select a UI or client generator separately and restrict exposure
  per environment. Assess existing Swashbuckle or NSwag use by maintenance
  and migration cost.
- Use the built-in DataAnnotations validation where the selected version
  supports it for Minimal APIs, or FluentValidation when rule complexity
  justifies it. Return ProblemDetails and apply the
  [API hardening guidance](../security.md#api-and-browser-hardening).

## Profile: web frontend

- Follow the [TypeScript reference](typescript.md#profile-web-frontend).
  **Blazor** is an option, not the default, when the team wants C# on client
  and server; compare render modes, the real-time connection of interactive
  server rendering, and WebAssembly download size.

## Profile: MCP server

- Start with the official MCP C# SDK: `ModelContextProtocol` (hosting and
  dependency injection), `ModelContextProtocol.AspNetCore` (HTTP), or
  `ModelContextProtocol.Core` (low-level). Verify its release, protocol
  revision, and features against the intended clients.
- Choose **stdio** for a client-launched local process or **Streamable HTTP**
  for remote clients; keep legacy SSE for clients that require it. Verify the
  default HTTP session mode: stateful sessions allow unsolicited
  notifications but need affinity or shared state to scale.
- Apply the [MCP security requirements](../security.md#mcp-servers) and the
  [deployment](../deployment.md) guidance; for stdio, assess process
  permissions and lifecycle instead.

## Profile: GraphQL API

- **Hot Chocolate** is a starting point. Verify the license of each selected
  package and hosted tool; adopt federation only for separately deployed
  subgraphs. Define cost or depth limits and field-level authorization.

## Profile: gRPC service

- **grpc-dotnet** (`Grpc.AspNetCore`) with `Grpc.Tools` code generation is the
  starting toolchain. Verify generator, runtime, and protobuf compatibility.
- For browsers, use gRPC-Web with a generated Protobuf client, or JSON
  transcoding (`Microsoft.AspNetCore.Grpc.JsonTranscoding`) for REST callers;
  transcoding supports only server streaming.
- Verify HTTP/2, TLS when HTTP/1.1 and HTTP/2 share a port, ingress, and gRPC
  health checks on the platform.

## Profile: worker and batch jobs

Apply the shared [worker and job guidance](../deployment.md#workers-scheduled-work-and-batch-jobs)
for execution platforms, delivery semantics, and alerting.

- **Host:** a Worker Service with a `BackgroundService` for persistent
  consumers; a Generic Host console app returning an exit code for
  run-to-completion batch jobs.
- **Library:** compare a database-backed option, **Hangfire** or
  **Quartz.NET** with a persistent job store, with a broker-backed option,
  **MassTransit**, **Wolverine**, or the broker's SDK. A database queue avoids
  a broker; a broker fits throughput, routing, or fan-out. Licensing changed
  between major versions of some of these: verify the current license of the
  selected library, edition, and storage or transport package.
- **Retries:** make handlers idempotent, bound retries, and route exhausted
  work to a dead-letter queue or failed-job state with an owner. Verify when
  messages are acknowledged relative to completion.
- **Scheduling:** use clustered or recurring scheduling from the library or
  the platform scheduler; a timer in each replica duplicates runs.
- **Shutdown and concurrency:** pass the stopping `CancellationToken` through
  all work and keep `HostOptions.ShutdownTimeout` within the platform grace
  period. An unhandled exception stops the host by default
  (`BackgroundServiceExceptionBehavior`). Bound parallelism by downstream
  limits; `DbContext` is not thread-safe, so use one per unit of work.
- **Observability:** log job IDs and attempts, emit spans and metrics through
  `ActivitySource` and `Meter`, and adopt a library's OpenTelemetry
  integration only after verifying its maintenance.

## Data layer

Add persistence, caches, and workers only for an identified requirement.

- **PostgreSQL** with **Npgsql** is the relational starting point, with the
  local and production options in the [deployment guide](../deployment.md).
- **EF Core** with the Npgsql provider fits domain models; **Dapper** fits
  SQL-centric code. Both can coexist on one connection configuration.
- Ship EF Core migrations as a migration bundle for automated deployment, or
  an idempotent SQL script when review is required, run by a deployment
  identity with schema rights. Runtime `Migrate` is a deliberate tradeoff;
  check pending model changes in CI. Without EF Core, verify a migration tool;
  never let two tools own one schema.

## Testing

- **xUnit**, **NUnit**, or **MSTest**: keep the team's framework. With no
  preference, start with xUnit, which the ASP.NET Core integration-test
  samples use. Verify VSTest or Microsoft.Testing.Platform support.
- `WebApplicationFactory` (`Microsoft.AspNetCore.Mvc.Testing`) runs in-process
  HTTP tests. Use **Testcontainers for .NET** or isolated CI services for
  PostgreSQL and brokers; the EF Core in-memory provider does not reproduce
  provider behavior.
- Use framework assertions, **Shouldly**, or **AwesomeAssertions**.
  FluentAssertions changed its license terms in a recent major; verify before
  adopting or upgrading. Add **NSubstitute** or **Moq** only for test doubles,
  after the same license check.

## Code quality and structure

- `dotnet format` with `.editorconfig` is the formatting default; CI runs
  `dotnet format --verify-no-changes`.
- Use the SDK's .NET analyzers with an explicit `AnalysisLevel` or
  `AnalysisMode`, and `EnforceCodeStyleInBuild` for IDE rules in CI.
  Third-party analyzers are optional after a maintenance check.
- Enable nullable reference types and treat warnings as errors in CI. Decide
  whether NuGet audit warnings fail every build or a dedicated audit job.
- Share settings in `Directory.Build.props`; keep one project per deployable
  plus tests until boundaries justify more.

## Observability and deployment

- Use `ILogger` message templates and the JSON console formatter; add Serilog
  only for a required sink or enricher. Redact secrets and sensitive fields.
- Use OpenTelemetry .NET hosting extensions, instrumentation for the selected
  frameworks, and an OTLP exporter with a defined destination. Do not combine
  automatic and manual instrumentation that duplicates spans.
- Build on the official `sdk` image; run on `aspnet`, `runtime`, or
  `runtime-deps`. Chiseled and Azure Linux distroless variants run non-root
  without a shell and lack ICU and time zone data: use an `extra` variant or
  invariant globalization. Regular variants run as root unless the provided
  `app` user is set. Verify the default port (`ASPNETCORE_HTTP_PORTS`) and pin
  digests per the [deployment guide](../deployment.md).
- Framework-dependent publishing is the starting point. Self-contained,
  trimmed, or Native AOT output needs a measured startup or size reason: AOT
  forbids dynamic loading and runtime code generation, requires trimming, and
  supports only part of ASP.NET Core. Check dependencies with the AOT and trim
  analyzers.
- The GC derives its heap limit from the container memory limit. Size memory
  from measured total usage, including non-heap memory, and choose
  workstation or server GC from measurements.
- Verify health endpoints, probes, and the shutdown timeout against the
  platform grace period in the [deployment guide](../deployment.md).
