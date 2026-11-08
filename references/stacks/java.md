# Java Stack Defaults

Opinionated defaults for Java profiles. Versions are deliberately NOT
recorded here — verify the latest stable at generation time (see
`decision-criteria.md`).

## Runtime & build

- **JDK:** latest LTS release (verify — 21 and 25 are the LTS lines as of
  writing). Distribution: Eclipse Temurin.
- **Version manager:** SDKMAN (default) or mise.
- **Build:** Gradle with Kotlin DSL (default for new projects) or Maven
  (when the org standard or team familiarity dictates). Always commit the
  wrapper. Target the latest LTS language level.

## Framework

- **Spring Boot** — default: ecosystem depth, hiring pool, maturity.
  HEALTHY. (Fast-moving majors — verify the current stable major line.)
- **Quarkus** — alternative for many small services: fast startup, low
  memory, developer joy, first-class container/native story. HEALTHY.
- **Micronaut** — AOT, low footprint; similar niche to Quarkus with a
  smaller community. HEALTHY alternative.

## Profile: REST API

- **Spring Web MVC** (default). WebFlux only with a real reactive
  justification — reactive for its own sake is a maintenance tax.
- **springdoc-openapi** for OpenAPI docs. **Jakarta Bean Validation** for
  input validation.

## Profile: gRPC service

- **grpc-java + protobuf-gradle-plugin** (official toolchain). HEALTHY.
- Spring lifecycle integration via the community `grpc-spring-boot-starter`
  (CAUTION: verify current health) or plain grpc-java managed by Spring.
- Cloud Run: enable HTTP/2; the server must accept h2c.

## Profile: GraphQL API

- **Spring for GraphQL** — default within Spring shops. HEALTHY.

## Profile: MCP server

- **Official MCP Java SDK** (modelcontextprotocol/java-sdk; Spring AI
  integration emerging). CAUTION: younger than the Python/TS SDKs — verify
  current state and transport support before recommending. If the server is
  nontrivial, say plainly that Python or TypeScript SDKs are more mature.

## Data layer

- **Database:** PostgreSQL (default) — Docker/compose locally, Cloud SQL on
  GCP.
- **ORM:** Spring Data JPA + Hibernate (default) / **jOOQ** (type-safe SQL
  codegen — strong pick for SQL-heavy domains).
- **Migrations:** Flyway (default) / Liquibase.
- **Mapping:** MapStruct for DTO/entity mapping.

## Testing

- **JUnit 5** (verify current major) + **AssertJ** + **Mockito**.
- Spring Boot Test slices for focused tests; **Testcontainers** — default
  for database/broker integration tests.
- REST: MockMvc or REST Assured.

## Code quality

- **Spotless** — formatting (default).
- **Error Prone + NullAway** — static analysis add-ons (default).
- Checkstyle/SonarQube when the org wants policy enforcement.
- Pre-commit hooks are uncommon in Java teams — run quality gates in CI.
- Commits: Conventional Commits.

## Observability

- **SLF4J + Logback** with a JSON encoder (logstash-logback-encoder) so
  Cloud Logging captures structured lines.
- **Micrometer + Spring Actuator** for metrics and health; OpenTelemetry
  Java agent for distributed tracing.

## Project structure

- Standard Maven/Gradle layout. Package-by-feature for domain packages in
  larger apps. Single module until size genuinely demands multi-module.

## Cloud Run notes

- Runtime base image: JRE-only (eclipse-temurin JRE), multi-stage build;
  Spring Boot layered jars for faster container pushes.
- `-XX:MaxRAMPercentage≈75` for container memory.
- `server.shutdown=graceful` + SIGTERM handling.
- Map Actuator liveness/readiness to Cloud Run probes.

## Avoid for new work

- Java EE/Jakarta application servers (WildFly, Payara) for new greenfield
  microservices; legacy `javax.*` namespace code; Spring Cloud Netflix
  legacy components (Hystrix, Zuul 1).
