# Java stack defaults

Use these defaults to assemble a Java stack with consistent framework and
build choices. Apply the shared [decision criteria](../decision-criteria.md)
for tool evaluation, release verification, and audit health.

Jump to: [Runtime](#runtime-and-build) · [Framework](#framework) ·
[Profiles](#profile-rest-api) · [Data](#data-layer) · [Testing](#testing) ·
[Quality](#code-quality-and-structure) · [Operations](#observability-and-deployment)

## Runtime and build

- **JDK:** choose a compatible supported LTS line. Verify the distribution's
  support policy, framework requirements, compiler target, build tool, and
  runtime image together; the latest JDK may precede ecosystem support.
  Eclipse Temurin is a starting distribution, subject to platform requirements.
- Use SDKMAN or mise only when supported and useful on the developer platform.
- **Gradle with Kotlin DSL** is a starting choice; **Maven** is equally viable
  when organization standards or team familiarity favor it. Commit and verify
  the wrapper; select a supported compatible tool version.
- Prefer framework dependency management/BOMs for coordinated dependencies.
  Record the managed versions; do not override them with independent latest
  artifacts without evidence of compatibility.

## Framework

- **Spring Boot** is a starting point for integrated application services.
- **Quarkus** or **Micronaut** may fit startup, memory, or ahead-of-time
  compilation requirements. Validate those benefits with the actual workload.
- Choosing a framework changes HTTP integration, configuration, dependency
  injection, persistence, migrations, testing, security, observability, and
  packaging. The Spring-specific options below apply only when Spring is
  selected; use and verify the chosen framework's supported equivalents.

## Profile: REST API

- In Spring, **Spring Web MVC** is the starting point. Choose WebFlux when
  end-to-end reactive execution and workload requirements justify it.
- Select compatible OpenAPI integration and Jakarta Bean Validation tooling.
  For Quarkus/Micronaut, use their supported HTTP and validation extensions.

## Profile: gRPC service

- **grpc-java** with protobuf and compatible build/code-generation plugins is
  the starting toolchain. Verify generated-code and runtime compatibility.
- When framework integration is needed, assess the maintained official or
  community integration for the selected framework, including lifecycle and
  security. Do not assume one starter works with every framework/version.
- Verify HTTP/2, ingress, connection lifecycle, and health-check support on
  the deployment platform before promising compatibility.

## Profile: GraphQL API

- **Spring for GraphQL** fits Spring applications. When another framework is
  selected, evaluate its supported GraphQL integration rather than importing
  Spring automatically. Define query limits and resource/field authorization.

## Profile: MCP server

- Evaluate the official MCP Java SDK and integrations according to current
  features, supported JDK/framework versions, and intended clients. Compare
  another language only when a documented required capability is unavailable;
  avoid unverified relative maturity claims.
- Choose local stdio or a currently supported remote transport according to
  client needs. Verify protocol authorization/discovery, streaming, sessions,
  and scaling for remote deployments. See the
  [security](../security.md#authentication-and-authorization-l7) and
  [deployment](../deployment.md) guidance. Local stdio uses process permissions
  and lifecycle rather than an HTTP container.

## Data layer

Add persistence, caches, and workers only for an identified requirement.

- **PostgreSQL** is the relational starting point: Docker/Compose locally and
  a managed database or deliberately operated OCI service in production,
  subject to constraints. Embedded storage can be sufficient for simpler cases.
- In Spring, **Spring Data JPA + Hibernate** is a starting ORM choice;
  **jOOQ** fits SQL-centric domains, subject to database edition/licensing and
  code-generation needs. Other frameworks use their supported persistence
  integrations and dependency management.
- Choose **Flyway** or **Liquibase** when migrations are needed; verify engine
  support and framework integration. Avoid two tools owning the same schema.
- DTO/entity mapping can be explicit or use **MapStruct** when complexity
  justifies code generation; validate annotation-processor/JDK compatibility.
- Add caches, queues, or object storage only when justified. Jobs require
  explicit execution, retries, idempotency, and operational ownership.

## Testing

- **JUnit**, **AssertJ**, and **Mockito** are starting choices where compatible
  with the framework's supported test platform and JDK. Verify release lines
  together rather than prescribing a frozen major version.
- Use Spring Boot Test slices only for Spring; select corresponding framework
  harnesses for Quarkus or Micronaut. Use MockMvc for appropriate MVC tests or
  an HTTP client such as REST Assured for network-level tests.
- **Testcontainers**, isolated CI service containers, or an approved managed
  test environment support database/broker integration tests. Confirm container
  execution access and isolate test data.

## Code quality and structure

- **Spotless** is a formatting starting point. Error Prone/NullAway are
  optional static analysis tools after checking JDK/compiler/build compatibility.
  Checkstyle or a maintained analysis platform may fit team policy.
- Local hooks are optional; required gates run in CI. A commit convention
  should serve the team's release workflow.
- Use standard Maven/Gradle layout, feature-oriented domain packages as
  complexity grows, and one module until clear boundaries justify more.

## Observability and deployment

- Use framework-compatible structured logging; in Spring, SLF4J/Logback with
  a compatible JSON encoder is an option. Redact secrets and sensitive fields.
- In Spring, Micrometer/Actuator can provide metrics and health. For other
  frameworks choose supported equivalents; select compatible OpenTelemetry
  instrumentation and define collection destinations. Avoid duplicate agents
  and instrumentation producing duplicate spans or metrics.
- Choose a supported runtime image and packaging for the selected framework:
  Spring layered jars, a custom runtime, or native compilation are conditional
  choices. Validate startup, memory, reflection, and resource requirements.
- Derive heap sizing from measured total memory including non-heap overhead;
  a fixed percentage is not a guarantee against container OOM termination.
- Verify port/interface, graceful shutdown, platform timeout, and appropriate
  HTTP/gRPC/TCP probes for the selected target. Provider-specific settings and
  lifecycle limits are covered by the [deployment guide](../deployment.md).
