# Design guide

Use this guide in both modes of the [core workflow](../SKILL.md): to design in
Mode A and as the comparison basis in Mode B. Depth comes from the
[intake guide](intake.md#depth). Recommendations are contextual starting
points; the project's drivers decide.

Jump to: [Drivers](#quality-drivers) · [Structure](#choosing-the-structure) ·
[Modules](#modules-and-boundaries) · [Dependencies](#dependency-rules) ·
[Data](#data-ownership) · [Integration](#integration-and-contracts) ·
[Contexts](#bounded-contexts-and-context-map) · [Conventions](#conventions) ·
[Code structure](#code-structure) · [Diagrams](#diagrams) ·
[Decisions](#decision-records)

## Quality drivers

- Start from the two or three quality attributes that matter most, written as
  scenarios simplified from the six-part SEI form (source, stimulus,
  environment, artifact, response, response measure): at least the stimulus,
  the environment, the expected response, and its measure, for example "a checkout request under normal load answers within 300 ms at the
  95th percentile". A goal without a measure is recorded as an assumption.
- Common drivers: changeability, testability, performance, availability,
  scalability, security, operability, cost, and time to market. Name the
  tradeoffs between them explicitly.
- Constraints (existing systems, compliance, team skills, deadlines) are not
  drivers; they narrow the options.

## Choosing the structure

`docs/stack.md` L3 records the pattern and repository layout; this guide
details the inside. Without that document, select the pattern here and say
that `stacks` normally records it.

| Structure | Fits when | Watch for |
|---|---|---|
| Layered (presentation, application, domain, infrastructure) | A small service with simple rules and one team | Business rules leaking into controllers or persistence |
| Ports and adapters (hexagonal, clean) | Rich domain logic, several delivery mechanisms or data sources, high testability needs | Ceremony in a CRUD service; adapters that duplicate the domain |
| Package by feature (vertical slices) | Many independent use cases that change separately | Shared code growing into an unowned "common" module |
| Modular monolith | Several capabilities with clear boundaries and one deployment, the usual start for a growing product | Boundaries kept only by convention; needs enforced dependency rules |
| Microservices | Independent scaling, release cadence, ownership by separate teams, or fault isolation that a monolith cannot meet | Distributed transactions, operational cost, chatty calls, shared databases |
| Event-driven integration | Decoupled reactions to state changes, auditability, or asynchronous workloads | Hidden coupling through event schemas, ordering, and duplicate delivery |

- Combine them: a modular monolith whose modules use ports and adapters is a
  common shape. The internal style of each module is this design's choice
  within the pattern L3 recorded; choose per module when modules differ in
  complexity, and record it in the dependency rules.
- Prefer the simplest structure that meets the drivers. Splitting into
  services needs a driver that one deployment cannot satisfy; if the user
  requires services anyway, honor it and record the operational cost.

## Modules and boundaries

- Draw modules around business capabilities, not technical layers: `billing`,
  `catalog`, `identity` rather than `services`, `models`, `utils`.
- Each module records: responsibility in one sentence, the data it owns, its
  public interface (operations, events, or API), and the modules it may
  depend on.
- High cohesion inside, few and explicit dependencies outside. A change to one
  capability should usually touch one module.
- Keep shared code minimal and stable: technical utilities may be shared; a
  shared domain model across modules is a coupling decision to record.
- Size: start coarse and split when a module's responsibility needs "and" to
  describe, or when two teams contend for it.

## Dependency rules

- The direction depends on the structure. In a layered design, each layer
  depends only on the layers below it. In ports and adapters or clean
  architecture, dependencies point inward: delivery and infrastructure depend
  on application and domain, never the reverse, with the domain defining the
  interfaces that infrastructure implements. Record which one applies.
- The module graph is acyclic. Break a cycle by moving the shared concept,
  inverting a dependency behind an interface, or communicating through events.
- Modules use each other only through their public interface; no reaching
  into another module's internals or tables.
- Record how each rule will be enforced: a language mechanism (for example
  Go `internal/` packages or Java modules), an architecture-test or
  import-boundary tool for the selected language, or review only. Verify the
  maintenance and license of a tool before recommending it; a rule enforced
  by review alone is recorded as such.

## Data ownership

- Every table, collection, or aggregate has exactly one owning module; only
  that module writes it. A small shared module for technical code, or a
  shared kernel of stable value types, owns no data and is recorded with the
  reason.
- Other modules read through the owner's interface, a published read model,
  or events. Cross-module joins in a shared database are a recorded exception
  with a reason.
- In a modular monolith, separate schemas or naming per module keep a later
  split possible. In microservices, each service owns its storage.
- Record transaction boundaries: what must be consistent immediately and what
  can be eventually consistent, with the mechanism (a local transaction, an
  outbox, a saga).

## Integration and contracts

- Choose synchronous calls when the caller needs an immediate answer, and
  asynchronous messages when the work can proceed independently or must
  survive outages.
- Contracts are explicit: OpenAPI, GraphQL schemas, protocol buffers, or
  AsyncAPI, as the stack decided. State the compatibility policy: versioning,
  or evolution through additive changes and deprecation periods, which is
  the usual GraphQL practice.
- Every remote interaction states its timeout, retry and backoff policy,
  idempotency mechanism, and failure behavior. Consumers are idempotent
  whenever an outbox, retries, or redelivery can occur, which is almost
  always: an outbox relay can publish a message more than once whatever the
  broker promises. A broker's exactly-once guarantee is bounded (for example
  by a deduplication window); rely on it only with that scope recorded.
- Publish events only for facts other modules need; an event schema is a
  public contract.
- At `extended` depth, protect the domain from external models with an
  anti-corruption layer where an external system's concepts differ.

## Bounded contexts and context map

At `extended` depth, group modules into bounded contexts: areas where one
model and vocabulary hold. For each pair of related contexts record the
relationship: customer and supplier, conformist, anti-corruption layer,
shared kernel, open host service, published language, partnership, separate
ways, or big ball of mud (the patterns in Evans's DDD Reference). Keep a short
glossary of terms that mean different things in different contexts.

## Conventions

Conventions are what every contributor, including coding agents, follows
without asking. Record only those that apply, each as a one-line rule:

- **Errors:** how failures are represented, mapped at boundaries, and shown
  to callers.
- **Logging and telemetry:** structure, correlation identifiers, and what is
  never logged.
- **Configuration:** where it comes from and how it is validated; secrets are
  never in code.
- **Naming:** modules, files, and public types.
- **Testing:** what each module tests at which level, and where tests live.
- **Transactions and time:** where transactions start, time zones, and
  identifier generation.
- **Security boundaries:** where authentication is checked and where
  authorization decisions are made, consistent with `docs/stack.md`.
- **Dependencies:** how a new library is approved.

## Code structure

Map every module to a path so that tools and agents can find and own it.
Record one row per component and one per module in section 10, with the
layout rule. Section 10 is the source of truth for paths: a module's row
uses the same name as in section 5, and the Path column of section 5 repeats
it exactly.

- Python: one package per module under the import package, for example
  `src/<import_name>/<module>/` with an `__init__.py`.
- Java and Kotlin: one package per module under the base package, or one
  build module per module when boundaries need compiler enforcement.
- TypeScript: one folder per module under `src/`, or one workspace package
  per module when they are released separately. A workspace alone does not
  stop deep imports; enforcement needs package `exports` with declared
  dependencies, TypeScript project references, or an import-boundary rule.
- Go: one directory tree per architecture module inside a single Go module
  (`go.mod`), with the module's private packages under `<module>/internal/`.
- .NET: one folder per module, or one project per module when boundaries need
  compiler enforcement.

Frameworks that impose structure decide what a module is:

- Django: a module that owns tables is a Django app, registered in
  `INSTALLED_APPS`, in Django's own layout rather than `src/`; its app label
  appears in table names and migrations.
- NestJS: a module is a feature module folder with its `*.module.ts`,
  imported by the root module.
- Next.js App Router: folders under `app/` are routes; keep domain modules
  outside `app/`, or in private `_folders`.
- Spring: one package per module under the base package; Spring Modulith can
  verify module boundaries when the stack adopts it.

Verify these conventions in the framework's current documentation. Paths are
relative to the project root. When modules live in several repositories,
write one document per repository, or qualify each path with its repository
and say which document is authoritative.

## Diagrams

Use Mermaid `flowchart` diagrams, which render widely, at the levels of the
C4 model: system context (the system, its users, and external systems),
containers (deployable units and data stores), and components (the modules
inside a container). At `compact` depth, one sentence can replace the
context diagram; `standard` adds a context and a container diagram;
`extended` adds component diagrams per bounded context. Label each arrow with
the interaction. A diagram summarizes the tables; it never contradicts
them.

## Evolving an existing system

When the design changes an existing codebase, plan the move in small,
reversible steps: introduce the new boundary next to the old code, route
callers through it, and retire the old path (the strangler approach). Record
the intermediate states and the first step in section 12; never assume a
rewrite.

## Decision records

Write a decision record for a choice that is hard to reverse, affects several
modules, or was contested: context, the decision, alternatives considered,
and consequences. At `compact` and `standard` depth, keep decisions in the
document's decision log; at `extended` depth or on request, also write one
file per decision under `docs/adr/`, numbered `0001-short-title.md`. A
superseded record is kept and marked superseded, never deleted.
