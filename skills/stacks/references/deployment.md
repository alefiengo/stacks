# Deployment, containers, and CI/CD

Use this guide for layers L8–L10 and distributed systems. Choose delivery and
operations around the workload, user constraints, and team ownership. Apply
the [release verification policy](decision-criteria.md)
and [security guidance](security.md) to the selected platform.

Jump to: [Local environment](#deployment-model-and-local-environment-l8) ·
[Containers](#application-container-patterns) · [CI/CD](#cicd-l9) ·
[Managed containers](#managed-container-platforms) ·
[Workers and jobs](#workers-scheduled-work-and-batch-jobs) ·
[Microservices](#distributed-systems-and-microservices) ·
[Infrastructure](#infrastructure-and-environments-l10)

## Deployment model and local environment (L8)

- Default to Docker Compose for local database, cache, queue, broker, and search
  services. If containers are unavailable or prohibited, document a managed
  development service or another suitable alternative, including parity limits.
  Embedded libraries and databases do not automatically need separate services.
- Prefer managed production dependencies or explicitly operated OCI services.
  Document operational ownership, persistent storage, backups, restore, network
  access, upgrades, and availability; a container alone does not supply them.
- OCI application containers are a starting point for backend services when
  supported. Static frontends on a CDN, function runtimes, client-launched
  stdio programs, and platform-specific packaging can use other delivery models.
  Developer compilers, package managers, and CLIs can run natively.
- Document the minimal local service catalog with readiness checks. Add a
  database, cache, broker, or object store only when a requirement calls for it.
- Local object storage must match the API under test. S3-compatible storage is
  not proof of GCS compatibility; record emulator and adapter limitations.
- Commit an example configuration containing placeholders only; keep real
  secrets out of the repository and generated documents. An application may
  run natively for development or in Compose according to team constraints.

## Application container patterns

- Use multi-stage builds, cache dependency layers, and keep build-only tools out of
  runtime images. Use a minimal supported base, a non-root user where possible,
  and an explicit policy for writable filesystem paths.
- Match packaging to the application: Python wheels and runtime dependencies,
  Node.js assets, native modules, and framework loaders, or Java packaging and
  runtime requirements. A single bundle or JRE-only image is conditional.
- Mutable tags identify a release channel, not immutable content. For released
  images record an exact version and digest; deploy the same built artifact
  across environments. Schedule updates and rebuilds, then scan the result.
  Do not use `:latest` as a reproducibility policy.
- Pass build-time credentials only through BuildKit secret or SSH mounts;
  never through `ARG`, `ENV`, or copied files, which persist in image layers or
  metadata. Maintain a `.dockerignore` that excludes secret-bearing files and
  local artifacts from the build context.
- Verify image architecture, runtime support, port and listening interface,
  startup time, health protocol, resource limits, and graceful shutdown.

## CI/CD (L9)

Use the existing host and CI platform where suitable. GitHub Actions is a
starting choice for a new GitHub repository. Separate validation from deployment:

1. **Pull requests:** resolve dependencies from locks or equivalent constraints,
   then run applicable lint, format, type, test, and build checks.
   Run integration services only in isolated approved environments. Apply
   dependency review, secret scanning, and container scanning when relevant;
   pin scanner actions, binaries, and images to a SHA or digest, and give
   scanning jobs no deployment credentials or production secrets.
2. **Untrusted contributions:** no production secrets, write credentials, or
   deployment. Do not execute untrusted code in privileged workflows. Scope
   token permissions, caches, and artifact access to their trust boundary.
3. **Protected release branch or tag:** build and scan a releasable artifact;
   record provenance and digest, then promote that artifact through environments.
   Verify third-party actions and plugins, pin immutable revisions when supported,
   and maintain an update policy.
4. **Deployment:** use narrowly scoped workload identity or OIDC federation
   where available. Restrict permitted repositories, refs, and environments;
   grant least privilege and avoid long-lived cloud keys. Follow the production
   approval policy; propose a manual gate when none is established.

Recommend automated dependency updates and branch protection according to the
host and team. Select remediation thresholds for scanner findings; record
exceptions with scope, owner, and expiry. A recommended gate is not evidence
that it already runs.

## Managed container platforms

When a managed container platform is selected (for example Google Cloud Run,
Amazon ECS on AWS Fargate, or Azure Container Apps), verify its current
runtime contract and the capabilities of the selected service, job, or worker model using permitted
official sources. Keep unavailable or disallowed lookups pending verification.

- Distinguish request-serving HTTP/gRPC services from batch jobs, scheduled
  work, and persistent workers; apply the
  [worker and job guidance](#workers-scheduled-work-and-batch-jobs) to the latter.
- Choose region, minimum and maximum instances, concurrency, CPU, memory, and
  database connection budgets from latency, cost, availability, and workload.
  Do not prescribe a universal numeric concurrency or instance default.
- Verify the required port, listening interface, and transport. HTTP, gRPC, and
  TCP have different health and lifecycle requirements; use supported probes and avoid
  dependencies that cause cascading liveness restarts.
- For gRPC, verify end-to-end HTTP/2 and cleartext container-side requirements,
  streaming limits, client reconnect behavior, and ingress configuration.
- For remote MCP, verify SDK and protocol authorization and discovery,
  supported clients, streaming, reconnects, session routing and state, and scaling,
  and apply the [MCP security requirements](security.md#mcp-servers).
  An OIDC or identity-aware proxy, or an ordinary browser login, does not by itself establish
  protocol compatibility. Local stdio servers use a process lifecycle instead.
- Use least-privilege identities and authenticate service-to-service calls;
  verify token audience and caller permissions. Network ingress restrictions
  supplement authentication and authorization rather than replacing them.
- Choose supported private connectivity for actual dependencies. Verify current
  direct networking and connector options, routing, quotas, cost, and egress
  policy; do not assume a connector is always needed.
- Choose secret injection through environment variables or mounted files as
  separate mechanisms; verify version selection, access controls, and rotation.
- Verify domains, TLS, load balancing, authentication, and rate limiting
  as a complete routing design. Record applicable regional/product constraints.

## Workers, scheduled work, and batch jobs

Apply this section to the worker and batch jobs profile and to background work
inside other profiles. The language references choose the job library; this
section covers execution and operations.

- **Execution model:** choose a persistent worker for continuous queue
  consumption, a run-to-completion job for batch/ETL or event-triggered units
  of work, and a scheduler or cron trigger for periodic work. Examples include
  Cloud Run worker pools and jobs, Azure Container Apps apps and jobs, and a
  Kubernetes Job or CronJob. Verify the selected model's maximum duration,
  retry and parallelism settings, timeouts, scaling triggers, and pricing.
- **No hidden background work:** do not run durable work in a request handler
  after the response or in a process the platform may throttle or stop. Use a
  durable queue, job record, or platform job execution instead.
- **Delivery semantics:** design for at-least-once execution, including
  platform retries and interruption during maintenance. Use idempotency keys,
  deduplication, or upserts for side effects. When a job must be enqueued with
  a database change, enqueue in the same transaction through a database-backed
  queue that supports it, or use a transactional outbox.
- **Retries and dead-letter handling:** bound attempts with backoff and jitter,
  separate permanent from transient failures, and move exhausted work to a
  dead-letter queue or failed-job state with an owner, alert, and replay
  procedure.
- **Scheduling:** state the time zone, overlap policy (for example, a
  Kubernetes CronJob `concurrencyPolicy`), missed-run behavior, and how only one
  scheduler fires each run. Several replicas each running an in-process
  scheduler duplicate work unless locking or deduplication prevents it.
- **Graceful shutdown:** on the platform's termination signal, stop accepting
  work and finish, checkpoint, or release in-flight items within the verified
  grace period. Keep acknowledgment, lease, or visibility timeouts longer than
  the processing time, and checkpoint long batches so a restart resumes them.
- **Concurrency and scaling:** derive worker concurrency from downstream
  limits such as database connections, API quotas, and memory; scale on queue
  depth or lag where the platform supports it. Do not prescribe universal values.
- **Health and observability:** HTTP probes are N/A unless the platform
  requires them or the worker already exposes an endpoint. Track queue depth,
  age of the oldest item, throughput, duration, retries, failures, dead-letter
  volume, and the last successful run of each scheduled job; alert on a growing
  backlog, a missed or failed schedule, and new dead-letter items. Propagate
  trace context from producer to consumer when tracing is in scope.
- **Identity and data:** run workers under a dedicated least-privilege workload
  identity for the queue, database, and APIs. Keep secrets and unnecessary
  personal data out of job payloads, and re-check authorization for actions
  performed on a user's behalf. See [security guidance](security.md).

## Distributed systems and microservices

- Start with a modular monolith when independent scaling, ownership, releases,
  or isolation do not justify distributed operations. If microservices are a
  firm requirement, honor it and document boundaries and operational costs.
- When split, record which deployable units exist and that each owns its
  storage; the detailed boundaries, data ownership, and contracts belong to an
  architecture design (`docs/architecture.md`). Avoid shared mutable domain
  models and cross-service database ownership that defeats independent
  releases.
- Choose monorepo or separate repos by ownership and release workflow, not
  team size alone. Shared tooling need not imply shared runtime/domain models.
- Select synchronous calls when an immediate response or consistency contract
  requires them; select events when asynchronous decoupling serves the product.
  Define retries, timeouts, backpressure, idempotency, ordering, deduplication,
  dead-letter handling, and tracing for the chosen communication pattern.
- Choose managed services or an orchestrator from concrete networking,
  lifecycle, scheduling, availability, and ownership requirements. Avoid adding
  a gateway, broker, or Kubernetes merely because multiple services exist.

## Infrastructure and environments (L10)

- Prefer versioned infrastructure when repeatability, multiple environments,
  compliance, or operational complexity justify it. Terraform is a starting
  option; compare OpenTofu and verify the current license of the selected tool
  and release against organization policy. Existing IaC standards or a small
  documented platform workflow may fit.
- Separate test, staging, and production according to blast radius and data policy.
  Small internal tools still need safe validation and recovery appropriate to
  their impact; do not infer safety from their audience alone.
- Separate environment configuration from immutable application artifacts.
  Non-secret static configuration can be packaged when intentional; secrets
  must not be embedded. Document rollback and roll-forward, migrations, backups,
  restore tests, and who operates the system.
