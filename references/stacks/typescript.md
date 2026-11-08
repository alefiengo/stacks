# TypeScript / Node Stack Defaults

Opinionated defaults for TypeScript profiles. Versions are deliberately NOT
recorded here — verify the latest stable at generation time (see
`decision-criteria.md`).

## Runtime & tooling

- **Node:** current active LTS line (verify the nodejs.org release schedule).
- **Version manager:** fnm or volta (mise when the machine is polyglot).
- **Package manager:** pnpm (default — strict, fast, workspaces). npm is
  fine for tiny libraries; yarn — CAUTION for new projects.
- **TypeScript:** `strict: true` always; ESM (`"type": "module"`) for new
  packages; tsx for dev running; tsdown/tsup or tsc for builds.

## Profile: REST / HTTP API

- **Hono** — default on Cloud Run: fast, TS-first, portable, tiny. HEALTHY.
- **Fastify** — mature, plugin ecosystem, schema-based validation. HEALTHY.
- **NestJS** — for large teams/domains wanting structure, DI, modules.
  HEALTHY with a weight tradeoff; overkill for small services.
- **Express** — AVOID for new work (legacy TypeScript story, no built-in
  validation).
- **Validation:** zod (default; verify current major) / valibot (smaller
  footprint) / TypeBox (JSON Schema-first).

## Profile: web frontend

- **Next.js** — default when the app needs SSR/RSC or is product-grade.
  HEALTHY but fast-moving; verify current major stability before
  recommending.
- **Vite + React + TanStack Router/Query** — default for an SPA behind an
  API (simpler ops: static hosting/CDN). HEALTHY.
- **Astro** — when content-heavy sites dominate.
- **Styling:** Tailwind CSS (default) + shadcn/ui for component sourcing.

## Profile: MCP server

- **Official `@modelcontextprotocol/sdk`** — default. HEALTHY.
- Transport: stdio (local) / **Streamable HTTP** (remote; SSE deprecated).
  On Cloud Run: Streamable HTTP container; consider OAuth/OIDC in front.

## Profile: GraphQL API

- **Server:** GraphQL Yoga (default — Envelop plugin ecosystem) or Apollo
  Server (mature alternative).
- **Schema:** Pothos (code-first, TS-native) default; graphql-codegen for
  client-side typing.

## Profile: gRPC service

- **nice-grpc** (TS-native codegen) or **@grpc/grpc-js + protobuf-ts**.
- **Connect (connect-es)** — recommended when browser clients are in scope
  (Connect protocol + gRPC compatibility). CAUTION: verify current
  ecosystem state before recommending.

## TS-to-TS internal APIs

- **tRPC** — default when client and server share a pnpm monorepo
  (end-to-end types, no schema duplication).
- **OpenAPI + openapi-typescript** — when the contract must be
  language-neutral or externally consumed.

## Data layer

- **Database:** PostgreSQL (default) — same policy as the Python stack.
- **ORM:** Drizzle (default — SQL-like control, light runtime, bundled
  migrations) or Prisma (model-first DX, schema DSL, heavier runtime).
  Choose by taste: Drizzle for SQL control, Prisma for DX. Kysely when only
  a type-safe query builder is wanted. TypeORM — AVOID for new work.
- **Cache:** Redis.
- **Queues:** BullMQ (Redis-based, default) / Graphile Worker (when staying
  PostgreSQL-only).

## Testing

- **Vitest** — unit/integration (default).
- **Playwright** — e2e and browser tests (default).
- **Testing Library** for components; Fastify `app.inject` / Hono
  `app.request` for HTTP tests without a live server.
- Integration DB: Testcontainers-node or a compose-backed test environment.

## Code quality

- **Biome** — default (lint + format in one fast tool, single config).
- **ESLint + Prettier** — when a required plugin is missing from Biome
  (verify current plugin coverage).
- Types in CI: `tsc --noEmit`.
- Hooks: lefthook (default) or husky + lint-staged.
- Commits: Conventional Commits.

## Observability

- **pino** — structured logging (default).
- **OpenTelemetry** (`@opentelemetry/sdk-node` + auto-instrumentations).
- Sentry for error tracking (optional, ask).

## Project structure

- **pnpm workspaces monorepo** when API + frontend or multiple services:
  `apps/` + `packages/`. Turborepo optional as task orchestration grows.
- Single app: `src/` with feature modules.

## Cloud Run notes

- Listen on `PORT`; handle SIGTERM (stop accepting, drain, close).
- Health endpoint for startup/liveness probes.
- Cold starts: bundle to a single build artifact (esbuild/tsdown) and/or set
  min-instances 1 for latency-sensitive public services.

## Avoid for new work

- Express (new projects), JavaScript without types for anything nontrivial,
  moment.js (use dayjs or Temporal polyfills), NestJS for tiny services.
