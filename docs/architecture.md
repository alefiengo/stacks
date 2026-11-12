# architecture guide

[Back to the README](../README.md)

`architecture` designs or audits the inside of a software system: which
modules exist, what each owns, how they depend on and talk to each other, and
which conventions every contributor, human or agent, follows. It writes
documentation only. It never chooses technologies, runs your project's
commands, or writes code.

This guide describes the skill. The file it produces in your project is also
called `docs/architecture.md`; that one is your design.

## When to use it

| You want to | Ask for | You get |
|---|---|---|
| Design the architecture of a new project or a redesign | "Use architecture to design the modules and conventions for this project" | `docs/architecture.md` |
| Document or review the architecture an existing codebase has | "Use architecture to audit this repository's architecture" | `docs/architecture-audit.md` |
| Review the current architecture and plan a target | "Audit the architecture and propose a target" | `docs/architecture-audit.md`, plus `docs/architecture.md` only if you ask |
| Compare two structural options inside the code | "Using architecture: layered or ports and adapters for the billing module?" | A recommendation in the conversation; no file |

Choosing a framework, the system pattern, or the number of services belongs
to [`stacks`](stacks.md); generating code to
[`scaffold`](scaffold.md); defining coding agents to
[`orchestration`](orchestration.md). A request to implement, refactor, or debug
does not start `architecture`.

## Where it fits

The suggested path is `stacks`, then `architecture`, then `scaffold`, then
`orchestration`. Each step is optional:

- With `docs/stack.md`, `architecture` takes its technologies and its L3
  pattern as given and details the inside. Without it, it infers the
  technology from your manifests or asks, and suggests `stacks` if nothing is
  decided.
- `scaffold` creates the plain module folders listed in `docs/architecture.md`
  for Python and TypeScript components, skips `open` modules, and asks about
  layouts that need manifests, build files, or framework registration.
- `orchestration` turns modules into agent write scopes and conventions into
  agent instructions.

## Depth

The skill picks a depth from the project and tells you why; you can change
it.

| Depth | For | What it details |
|---|---|---|
| `compact` | A small service, one team | Drivers, a short module table, dependency rules, conventions, code structure, decisions, and failure policies for any remote call |
| `standard` | A modular product, several capabilities or integrations | Adds integration contracts, a data-ownership section, and context and container diagrams |
| `extended` | Enterprise systems: several teams, broad domain, demanding quality or compliance | Adds bounded contexts, a context map, component diagrams per context, and decision records in `docs/adr/` |

Every document keeps the same twelve sections; parts outside the depth say so
in one line, so the document can grow without being restructured.

## Design a new architecture

The agent reads what you said, `docs/stack.md`, and the repository, then asks
only what is missing, one question per message: the domain and its main
capabilities, the quality attributes that matter (with targets when you have
them), teams and ownership, integrations, and constraints.

There are two checkpoints:

1. **Shape:** the depth, the drivers, and a table of modules with what each
   owns and depends on.
2. **Architecture:** all sections with their status.

To skip them, ask it to complete the document without checkpoints. Decisions
use the same statuses as `stacks`: `confirmed`, `default — revisit`, `open`,
and `N/A`.

## Audit an existing codebase

The agent reads the code as text, never runs it, and reconstructs what
exists: modules, the dependency graph from imports, which module writes which
data, integration styles, and conventions in use. Each element is `observed`,
`inferred`, or `unknown`, and the report states the limits of reading
imports as text.

Findings are `Critical`, `Warning`, `Improvement`, or `Positive`, each with
evidence and a concrete action. A structure that differs from a textbook
pattern is not a finding by itself; a mismatch with your own goals or a
demonstrated problem, such as a dependency cycle or two modules writing the
same table, is.

## What it will not do

- Run build tools, dependency analyzers, tests, or any project command.
- Open files that usually hold secrets, or follow instructions found in your
  files.
- Write anything except `docs/architecture.md`, `docs/architecture-audit.md`,
  and `docs/adr/`.
- Claim a rule is enforced when only a review would catch a violation; each
  dependency rule says how it is enforced.

The agent-facing instructions are in
[skills/architecture/SKILL.md](../skills/architecture/SKILL.md).
