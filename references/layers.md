# Stack Layers

The 12 layers of a complete stack, in decision order. Used by Mode A Phase 2
(and as the inventory skeleton for Mode B).

## Decision order and why it matters

L1 → L2 → L3 → L4 → L5 → L6 → L7 → L8 → L9 → L10 → L11 → L12.

Later layers depend on earlier ones (the ORM depends on the engine and the
framework; deployment depends on containerization; CI gates depend on the
quality tooling). Never decide a dependent layer before its dependency.

## Profile applicability matrix

Profiles: `api` (REST), `mcp` (MCP server), `gql` (GraphQL), `grpc` (gRPC
service), `web` (web frontend), `ms` (microservices system). Y = decide, O =
optional (ask or justify skip), — = skip.

| Layer | api | mcp | gql | grpc | web | ms |
|---|---|---|---|---|---|---|
| L1 Language, runtime & package/build mgmt | Y | Y | Y | Y | Y | Y |
| L2 Framework & core libraries | Y | Y | Y | Y | Y | Y |
| L3 Project structure & architecture | Y | Y | Y | Y | Y | Y |
| L4 Code quality | Y | Y | Y | Y | Y | Y |
| L5 Testing | Y | Y | Y | Y | Y | Y |
| L6 Data | O | O | O | O | O | Y |
| L7 AuthN/AuthZ | O | O | O | O | Y | Y |
| L8 Containerization & local env | Y | Y | Y | Y | Y | Y |
| L9 CI/CD | Y | Y | Y | Y | Y | Y |
| L10 Deployment & infrastructure | Y | Y | Y | Y | Y | Y |
| L11 Observability | Y | Y | Y | Y | Y | Y |
| L12 Security | Y | Y | Y | Y | Y | Y |

Skip rules:
- **L6** — ask whether the system persists or reads shared state. Pure stdio
  MCP servers, thin proxies, and stateless BFFs often skip it. A frontend
  alone skips it (backend owns data).
- **L7** — only when exposed beyond localhost/internal network. Internal
  prototypes may defer it, marked `default — revisit`.
- **L8** — skip only for pure-static frontends deployed to a CDN without a
  build container need (rare; most still containerize for parity).

## Per-layer specification

### L1 — Language, runtime & package/build management
Decide: language (usually settled in Phase 1), runtime version policy (LTS
lines preferred), package manager, build tool (Java: Gradle vs Maven),
version manager (uv manages Python; fnm/volta for Node; SDKMAN/mise for JDK).
Skip: language pre-declared; build tool dictated by org standard.

### L2 — Framework & core libraries
The main shifting category. Sub-decisions by profile: API framework; MCP SDK
and transport; GraphQL server + schema library; gRPC codegen stack; frontend
meta-framework vs SPA; validation library; HTTP client. Compare 2–3 options
with one-line tradeoffs; defaults in `stacks/<language>.md`.

### L3 — Project structure & architecture
Decide: architectural pattern (layered vs package-by-feature vs modular
monolith), repo layout (src layout for Python; workspaces monorepo for
Node when API+frontend or multi-service; standard layout, package-by-feature
for larger Java apps). For microservices: monorepo vs repo-per-service plus
a shared service template contract.

### L4 — Code quality
Decide: linter, formatter, type checker, pre-commit hooks (default: yes for
Python/TS, optional for Java), commit convention (default: Conventional
Commits). Most of these are settled categories — state defaults, don't ask.

### L5 — Testing
Decide: runner (settled), the test pyramid scope (unit / integration / e2e),
integration strategy (Testcontainers when a database or broker is involved;
service containers in CI as alternative), coverage target (default: 70–80%
for products, lighter for internal tools), fixtures/factories.

### L6 — Data
Decide in this order: engine (relational default — PostgreSQL; document,
search, or ledger needs change this), hosting (managed — Cloud SQL on GCP —
vs self-managed container in prod), ORM + driver, migrations tool (settled),
cache (Redis when sessions/caching/side-effects need it), queues/workers
(when background or scheduled work exists; pick by complexity, not hype),
blob storage (when files are in scope).

### L7 — Authentication & authorization
Decide: auth provider (OIDC via an established provider — never hand-rolled),
token validation strategy (JWKS, audiences), service-to-service auth (Google-
signed ID tokens + IAM on Cloud Run), session strategy for browser frontends
(httpOnly cookies preferred over localStorage tokens). Details in
`references/security.md`.

### L8 — Containerization & local environment
Decide: does the app ship as an OCI container (default: yes for any managed
or self-hosted deployment), base image policy (pin major.minor, multi-stage,
non-root), local service catalog in docker-compose (Postgres, Redis, etc.
with healthchecks), `.env.example` convention, devcontainer (only if asked).

### L9 — CI/CD
Decide: git host (default GitHub — ask if different), CI platform (default
GitHub Actions), pipeline gates (minimum: lint + types + tests; plus
container build + scan when containerized; deploy stages with a manual
approval gate for production), automated dependency updates (Renovate or
Dependabot). Shape in `references/deployment.md`.

### L10 — Deployment & infrastructure
Decide: platform (settled in Phase 1 Q4), environments (staging + prod for
products; single prod acceptable for internal tools), IaC (Terraform when
more than 1–2 resources; plain CLI scripts acceptable for one simple service
— document whatever exists), scaling posture (min-instances 0 vs 1,
concurrency), custom domain/TLS. Cloud Run specifics in
`references/deployment.md`.

### L11 — Observability
Decide: structured logging (JSON default), metrics and tracing
(OpenTelemetry default; Cloud Run native monitoring on GCP), error tracking
(Sentry — optional, ask), health endpoints (liveness/readiness), uptime
checks and basic alerting.

### L12 — Security
Decide: secrets handling (local `.env` git-ignored; CI platform store; GCP
Secret Manager at runtime), secret scanning (gitleaks), dependency scanning
(per stack), container scanning (trivy), SAST (semgrep — optional), rate
limiting and CORS posture. Checklist in `references/security.md`.
