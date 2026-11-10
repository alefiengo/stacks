# Stack layers

Use these 12 layers for decisions in Mode A and the inventory in Mode B.
The [core workflow](../SKILL.md) defines authorization, scope, and outputs;
the [decision criteria](decision-criteria.md) define statuses and version policy.

## Decision order and why it matters

Presentation order: L1 → L2 → L3 → L4 → L5 → L6 → L7 → L8 → L9 → L10 →
L11 → L12.

Use this as presentation order, while respecting actual dependencies: the
ORM depends on the engine and framework, container choices depend on the
hosting target, and CI gates depend on quality tooling. Revisit affected
decisions after any upstream change; the order is not a reason to freeze
an incompatible choice.

## Applicability

**Always** means assess for every profile; **conditional** means decide or
justify `N/A` from the rules below. Profiles include REST API, MCP server,
GraphQL API, gRPC service, web frontend, microservices, and worker and batch
jobs (queue consumers, scheduled jobs, and batch/ETL jobs without their own
request server). The table guides assessment rather than imposing unnecessary
infrastructure.

| Layer | Applicability |
|---|---|
| L1 Language, runtime and package management | always |
| L2 Framework and core libraries | always |
| L3 Project structure and architecture | always |
| L4 Code quality | always |
| L5 Testing | always |
| L6 Data | conditional |
| L7 Authentication and authorization | conditional |
| L8 Containerization and local environment | conditional |
| L9 CI/CD | conditional |
| L10 Deployment and infrastructure | conditional |
| L11 Observability | always |
| L12 Security | always |

Combined profiles and multi-component systems keep one L1–L12 table. When a
component's choice differs, add a row labeled with the layer and component,
such as `L2 (api)` and `L2 (web)`, beneath the shared layer row, and record
the language per component. Outputs stay under the authorized root; write
per-package documents only when requested.

Applicability rules (retain all 12 rows; use `N/A` plus a reason when skipped):

- **L6** — determine whether the system persists or reads shared state. Pure stdio
  MCP servers, thin proxies, and stateless BFFs often skip it. A frontend
  alone skips it (backend owns data).
- **L7** — assess identities, trust boundaries, sensitive data, and privileged
  actions even on localhost or an internal network. Network placement alone
  never justifies skipping auth. A public static site without protected data
  or actions can justify N/A; document any intentional deferral and its risk.
- **L8** — services use local containers or managed dependencies by default.
  Static hosting, local stdio tools, and function platforms need not ship an
  application container. SSR frontends still need an appropriate runtime.
- **L9/L10** — local-only prototypes may defer hosted CI or deployment; record
  scope and rationale rather than inventing a cloud platform or pipeline.
- **L11/L12** — scale practices to the profile: a stdio MCP server must keep
  protocol stdout clear and may log to stderr; HTTP endpoints, container scans,
  and CORS are N/A when those surfaces do not exist. Security assessment remains
  relevant even when individual controls are not applicable.
- **Worker and batch jobs** — L8–L10 follow the execution platform: a managed
  job, a persistent worker, or a cron/scheduler trigger. L7 covers the
  worker's machine identity toward queues, databases, and APIs even without
  end users. L11 tracks queue and job metrics with alerts. HTTP probes are N/A
  unless the platform requires them or the worker exposes an endpoint. See
  [workers and jobs](deployment.md#workers-scheduled-work-and-batch-jobs).

## Per-layer specification

### L1 — Language, runtime and package management

Decide: language (usually settled in Phase 1), runtime version policy (LTS
lines preferred), package manager, build tool (Java: Gradle vs Maven), and
version manager (uv manages Python; fnm or mise for Node; SDKMAN or mise for
the JDK). In audits, verify the maintenance status of the observed version
manager rather than assuming it. Do not re-ask a pre-declared language or an
organization-mandated build tool; record it as confirmed and still assess
runtime/tool compatibility.

### L2 — Framework and core libraries

The main shifting category. Sub-decisions by profile: API framework; MCP SDK
and transport; GraphQL server + schema library; gRPC codegen stack; frontend
meta-framework vs SPA; job/queue library or plain batch entry point for
workers; validation library; HTTP client. Compare 2–3 options
with one-line tradeoffs; use the applicable curated stack reference when
available, otherwise use general criteria and permitted official evidence.

### L3 — Project structure and architecture

Decide: architectural pattern (layered vs package-by-feature vs modular
monolith) and repo layout (src layout for Python; Node workspaces when shared
tooling or coordinated releases justify them; standard layout and
package-by-feature for larger Java apps). For microservices: monorepo vs
repo-per-service plus a shared service template contract.

### L4 — Code quality

Decide: linter, formatter, and type checker appropriate to the framework.
Local hooks are optional reinforcement; enforce required gates in CI.
Choose a commit convention when it serves the release workflow. Most quality
tools are settled categories — state contextual defaults, do not re-ask.

### L5 — Testing

Decide: runner (settled), the test pyramid scope (unit / integration / e2e),
integration strategy (Testcontainers when a database or broker is involved;
service containers in CI as alternative), coverage policy based on critical
behavior and risk (a percentage alone does not establish test quality), and
fixtures/factories. Describe proposed checks; never report tests as executed
without execution evidence.

### L6 — Data

Decide in this order: engine (relational default — PostgreSQL; document,
search, or ledger needs change this), hosting (the selected platform's
managed service, for example Cloud SQL on GCP, vs a self-managed container in
production), ORM and driver, migrations tool (settled), cache (only for a
concrete shared cache, session, or coordination need; verify the license of
the selected engine and compare compatible alternatives), queues/workers (when
background or scheduled work exists; compare a database-backed queue with a
message broker by operational requirements), and blob storage (when files are
in scope).

### L7 — Authentication and authorization

Decide: trust boundaries and required identities, auth provider (OIDC via an
established provider where applicable — never custom cryptographic protocols),
token validation strategy (including JWKS and audiences where applicable),
service-to-service and worker machine identity, and browser session strategy. Assess the
selected platform's workload identity and service-to-service token model (for
example, Google-signed ID tokens on Cloud Run); consider `HttpOnly` cookies to
reduce browser token exposure. Use the [security guide](security.md) for the
full control requirements and protocol-specific limits.

### L8 — Containerization and local environment

Decide: whether the target accepts an OCI container (default for suitable
backend service hosting), base image policy (verified readable tag plus digest,
multi-stage, non-root), local service catalog in compose (database, cache, etc.
only when needed, with healthchecks), `.env.example` convention, and
devcontainer (only if asked). Mark unverified digests `TBD — verify`; never
invent them. Document static/CDN, function, and local stdio exceptions
explicitly.

### L9 — CI/CD

Decide: existing git host and compatible CI platform (GitHub Actions is a
starting choice for a new GitHub repository), applicable lint/type/test/build
gates, and container build/scan only when containerized. Separate untrusted
PR validation from privileged protected releases. Follow the organization's
production approval policy; propose a manual gate if none is established.
Choose dependency updates and protection rules for the host and team. Use the
[deployment guide](deployment.md) for pipeline design.

### L10 — Deployment and infrastructure

Decide: platform (settled in Phase 1 Q4; an unnamed cloud provider stays
`open`, never a delegated default), environment isolation, versioned
infrastructure, and recovery proportional to impact, repeatability, and
ownership. Preserve workable IaC standards; for a new choice, compare IaC tools
such as Terraform and OpenTofu and verify the current license of the selected
release. Derive capacity, concurrency, connection budgets, and instance bounds
from the workload, latency, and cost requirements; verify platform limits
before choosing values. Include domain/TLS, worker lifecycle, and
rollback/migration behavior where relevant. Use the
[deployment guide](deployment.md) for details.

### L11 — Observability

Decide: structured logging (JSON for applicable services, stderr for stdio
protocols), metrics/tracing destinations and compatible instrumentation,
optional error tracking, applicable health protocols, uptime checks, and
alerting. For workers and jobs, track queue depth and age, failures, retries,
dead-letter volume, and missed schedules. Scale to the operational need; do
not prescribe HTTP health endpoints or tracing dependencies for every profile. Ask only unresolved material choices.

### L12 — Security

Decide: secrets handling (local `.env` git-ignored; the CI platform's secret
store; the selected platform's secret manager at runtime), secret scanning
(for example, gitleaks or the git host's native scanning), dependency scanning
(per stack), container scanning when containerized (for example, trivy, grype,
or the platform's scanner), optional SAST (for example, semgrep; verify the
license of the selected edition), rate limiting, and CORS posture. Pin scanner
actions, binaries, and images to a commit SHA or digest, and run scanners
without deployment credentials or production secrets. Apply the
[security checklist](security.md) to the actual surfaces; selecting a tool does
not establish that a control is enforced.
