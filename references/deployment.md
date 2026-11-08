# Deployment, Containers & CI/CD

Cross-cutting guidance for layers L8–L10 and the microservices profile.
The Docker-first rule from SKILL.md applies throughout.

## Docker-first rule (binding)

- Any **service component** — database, cache, queue, broker, search — runs
  via Docker/compose locally or a managed cloud service in production.
  Never propose native or host installs for them.
- The **application itself** ships as an OCI container for any non-trivial
  deployment (Cloud Run, VMs, K8s). Dev tooling (compilers, package
  managers, CLIs) may be native.

## Local environment (L8)

- `docker-compose.yaml` with the service catalog + healthchecks; app runs
  natively for a fast loop or inside compose for parity — document both.
- **Service catalog defaults** (pin `major.minor`, verify current versions
  at generation time): PostgreSQL, Redis, RabbitMQ (when needed), Redpanda
  or Kafka (only at real scale), MinIO (S3-compatible blobs), Mailpit
  (email catching).
- `.env.example` committed; real secrets never.

## Application container patterns

- Multi-stage builds; dependency layers cached before code is copied.
- Python: slim base + uv; non-root user.
- Node: slim base + pnpm fetch stage; single-bundle artifacts reduce image
  size and cold starts.
- Java: multi-stage with layered jars (Spring Boot) and a JRE-only runtime
  stage; jlink optional for smaller images.
- Pin base images to `major.minor`; never `:latest`; rebuild images
  regularly for base-image CVEs (noted in CI).

## CI/CD (L9 — GitHub Actions default)

Pipeline shape, PR and main:

1. Setup (cache: uv, pnpm store, Gradle).
2. Lint + format check.
3. Type check (pyright/tsc where applicable).
4. Tests — unit; integration via Testcontainers or service containers.
5. Build/package.
6. Container build + vulnerability scan (trivy).
7. Deploy to environments; **manual approval gate for production**.

Additional gates: secret scanning (gitleaks), dependency review on PRs,
automated dependency updates (Renovate default; Dependabot acceptable),
branch protection on main.

## Google Cloud Run (primary managed target)

- **Deploy from CI via Workload Identity Federation** — no exported service
  account keys, ever.
- Region close to users; `--min-instances 0` (cost) vs `1` (cold-start
  latency); concurrency default 80 (tune for CPU-bound work).
- Startup + liveness probes against the HTTP health endpoint; **graceful
  SIGTERM handling is mandatory**.
- Secrets: GCP Secret Manager mounted as environment variables.
- Service accounts: one per service, least privilege; internal service-to-
  service calls use Google-signed ID tokens + IAM invoker bindings, private
  ingress.
- **gRPC services:** enable HTTP/2; container must listen with h2c.
- **Remote MCP servers:** Streamable HTTP transport; put OIDC/IAP auth in
  front.
- VPC Connector only when private resources must be reached.
- Custom domain + managed TLS via domain mapping or a load balancer.

## Microservices guidance

- **Default: modular monolith.** When a small team asks for microservices,
  say this explicitly and ask what pain they expect splitting to solve
  (org coordination, independent deploys, blast radius). Split when those
  pressures are real, not aspirational.
- When split: one bounded context per service; contracts (protobuf /
  OpenAPI) versioned as artifacts; no shared domain models across services.
- Repo strategy: monorepo for small teams (shared tooling, atomic changes);
  repo-per-service when org boundaries demand independent ownership.
- Integration: prefer events (Pub/Sub on GCP) over sync call chains; avoid
  building a distributed monolith.
- Platform: multiple Cloud Run services + an API gateway/LB covers most
  needs; GKE only when orchestration needs genuinely outgrow managed
  (stateful add-ons, custom operators, large fleets).

## IaC & environments (L10)

- **Terraform** (default) when there is more than 1–2 resources or multiple
  services/environments; plain CLI scripts acceptable for a single simple
  service — document whatever exists in `docs/stack.md`.
- Environments: dev (local compose), staging, prod for products; a single
  prod is acceptable for internal tools.
- Configuration via environment variables (12-factor); no config in images.
