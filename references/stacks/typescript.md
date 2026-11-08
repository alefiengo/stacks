# TypeScript and Node.js stack defaults

Use these defaults for TypeScript applications and Node.js services. Apply
the shared [decision criteria](../decision-criteria.md) for tool evaluation,
release verification, and audit health.

Jump to: [Runtime](#runtime-and-tooling) · [Profiles](#profile-rest-and-http-api) ·
[Data](#data-layer) · [Testing](#testing) ·
[Quality](#code-quality-and-structure) · [Operations](#observability-and-deployment)

## Runtime and tooling

- **Node.js:** select a compatible supported LTS line after checking the official
  release schedule, framework engines, build tooling, and hosting platform.
- Use fnm, Volta, or mise only when runtime switching is needed and supported
  on the developer platform; preserve an existing workable team convention.
- **pnpm** is the default for workspaces and dependency management; npm and
  Yarn are valid alternatives when compatible with the selected ecosystem.
  Commit the matching lockfile and make CI use frozen/immutable resolution.
- Prefer TypeScript strict checking. Decide ESM/CommonJS and build output from
  the target runtime and consumers; do not force ESM onto incompatible hosts.
  Use tsx, tsc, or a bundler according to development, library, or server needs.

## Profile: REST and HTTP API

- **Hono** is a lightweight starting point; verify the adapter for the target
  Node runtime and platform. **Fastify** fits plugin/schema-based APIs.
- **NestJS** fits teams needing framework-enforced modules and dependency
  injection. **Express** remains an option when its ecosystem and familiarity
  fit; explicitly select validation, error handling, and operational tooling.
- Choose zod, valibot, or TypeBox according to schema approach and framework
  compatibility. Do not combine incompatible validator/provider versions.

## Profile: web frontend

- **Next.js** is a starting point when server rendering or its server/client
  architecture solves a concrete requirement. Verify framework, React,
  runtime, deployment adapter, and cache behavior together.
- **Vite + React** fits browser applications consuming an API; choose routing
  and data-fetching libraries only as needed. Static build artifacts can deploy
  to a CDN without an application container or server runtime.
- **Astro** fits content-heavy sites; compare other frameworks when existing
  team expertise or constraints favor them.
- Tailwind CSS and sourced components such as shadcn/ui are optional styling
  choices. Include accessibility, ownership of copied code, and updates in
  the decision rather than assuming a component package meets those needs.

## Profile: MCP server

- Start with the official TypeScript MCP SDK; verify the current package/API
  layout, runtime requirements, and compatibility with the intended clients.
- Choose **stdio** for local client-launched processes or a supported remote
  transport such as **Streamable HTTP** for remote clients. Verify the current
  protocol and SDK; legacy HTTP+SSE is distinct from SSE streaming within a
  newer transport.
- For remote deployments, verify protocol authorization/discovery, client
  compatibility, sessions, streaming, reconnects, and scaling. An arbitrary
  OIDC proxy is not sufficient evidence that these requirements are met.
  See [authentication and authorization](../security.md#authentication-and-authorization-l7)
  and the [deployment guide](../deployment.md).

## Profile: GraphQL API

- **GraphQL Yoga** or **Apollo Server** are starting server choices.
  **Pothos** fits code-first schemas; choose schema-first tooling when needed.
- Verify server, GraphQL implementation, framework adapter, and code generator
  compatibility. Add client code generation when it serves actual consumers.
- Define complexity/depth limits and authorization at appropriate resource
  and field boundaries.

## Profile: gRPC service

- Compare **nice-grpc** or **@grpc/grpc-js** with an appropriate TypeScript
  generator. Verify generator/runtime compatibility and supported protocols.
- Consider **Connect** when browser clients or its protocol are required;
  verify the server adapter, generated clients, and platform support instead
  of assuming every gRPC/browser combination works.

## Internal TypeScript APIs

- **tRPC** fits consumers that can share TypeScript contracts and coordinate
  releases. It does not require a monorepo, and sharing a monorepo does not
  alone justify choosing it.
- **OpenAPI** with client generation fits language-neutral or externally
  consumed contracts. Preserve the ability to evolve contracts independently.

## Data layer

Add persistence, caches, and workers only for an identified requirement.

- **PostgreSQL** is the relational starting point; use Docker/Compose locally
  and a managed database or deliberately operated OCI service in production,
  subject to constraints. Embedded storage may fit simpler requirements.
- Compare **Drizzle**, **Prisma**, **Kysely**, or an existing ORM by SQL control,
  schema/migration workflow, runtime, driver support, and domain needs.
  Migration plans must consider existing data and rollback/roll-forward safety.
- Add **Redis** only for a concrete requirement. For jobs, compare **BullMQ**
  with a PostgreSQL-backed option such as **Graphile Worker** according to
  durability, retry, scheduling, and operational requirements.
- Background workers need an explicit execution platform and idempotency;
  do not assume work continues safely after an HTTP response.

## Testing

- **Vitest** is a starting runner for supported unit/component/integration
  workflows. Verify framework-specific setup rather than imposing it on
  unsupported server-component or platform boundaries.
- **Playwright** supports browser/end-to-end tests when a browser is in scope;
  Testing Library fits component behavior tests.
- Use framework in-process HTTP tests when available, such as Fastify inject
  or Hono request; add real-network tests for transport-specific behavior.
- Use Testcontainers, isolated CI service containers, or an approved managed
  test environment for database/broker integrations. Confirm execution access.

## Code quality and structure

- **Biome** is a lint/format starting point. Choose ESLint/Prettier when
  required framework rules, plugins, or conventions are not covered; verify
  current coverage. Type-check separately using the compatible compiler or
  framework tooling; do not mistake transpilation for type checking.
- lefthook, husky, or equivalent hooks are optional local conveniences. Enforce
  required gates in CI; choose a commit convention according to release needs.
- Use workspaces when shared tooling or coordinated packages justify them;
  `apps/` and `packages/` are a common layout. A single application can use
  feature modules in `src/`. Task orchestration is optional as the repo grows.

## Observability and deployment

- **pino** or framework-native structured logging is a starting point; redact
  secrets and sensitive fields. Select compatible OpenTelemetry instrumentation
  for the actual Node/browser runtime and define collection destinations.
- Browser telemetry and error tracking need a data policy and consent where
  applicable. They are optional, not mandatory dependencies for every profile.
- For HTTP containers, verify port/interface, shutdown, startup checks, and
  streaming requirements on the selected platform. Bundle only when native
  modules, dynamic assets, framework loaders, and source maps still work.
- Choose cold-start and concurrency settings from measured requirements;
  static hosting, serverless runtimes, and local stdio are distinct deployment
  models. Use the [deployment guide](../deployment.md) for platform verification.
