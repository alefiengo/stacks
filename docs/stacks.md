# stacks guide

[Back to the README](../README.md)

`stacks` helps an agent act as a software architect: it chooses or reviews a
project's technologies and writes the reasoning down. It produces
documentation only. It never runs your project's commands, installs packages,
or writes application code.

## When to use it

| You want to | Ask for | You get |
|---|---|---|
| Choose a stack for a new project or a redesign | "Use stacks to define the stack for ..." | `docs/stack.md` |
| Review the stack a repository already uses | "Use stacks to audit this repository's technology stack" | `docs/stack-audit.md` |
| Review the current stack and plan a target | "Audit the stack and propose a target stack" | `docs/stack-audit.md`, plus `docs/stack.md` only if you ask for it |
| Compare two specific tools | "Using stacks: Prisma or Drizzle for this API?" | A recommendation in the conversation; no file is written |

A request to implement a feature, scaffold a project, or debug does not start
`stacks`. Use [`scaffold`](scaffold.md) to turn `docs/stack.md` into a project.

## Define a stack

The agent reads what you already said and what the repository shows, then asks
only about missing decisions that matter, one per message. Each question
offers two or three concrete options, a recommendation, and "choose for me".

There are three checkpoints:

1. **Proposal:** a first table of choices and why they fit your requirements.
2. **Decision table:** all twelve layers with their status.
3. **Versions:** each dependency with its source, date, and compatibility
   notes.

To skip the checkpoints, delegate in your request:

```text
Use stacks to define a TypeScript MCP server stack. Choose sensible defaults
and complete the document autonomously, recording assumptions.
```

Delegation lets the agent choose defaults; it never turns an assumption into
a confirmed fact, and it never picks a cloud provider you did not name.

## Audit a stack

The agent inspects manifests, lockfiles, containers, CI, tests, and
configuration as text, and rates each layer:

| Health | Meaning |
|---|---|
| `HEALTHY` | Supported and coherent for the project, with evidence |
| `CAUTION` | Viable, with a tradeoff that matters here |
| `AT RISK` | A concrete support, compatibility, security, or operational problem |
| `UNKNOWN` | Not enough evidence; not a defect by itself |
| `N/A` | Outside the project's scope, with a reason |

Findings are `Critical`, `Warning`, `Improvement`, or `Positive`, each with
evidence, impact, confidence, and a concrete action. Using a different
framework than the curated default is not a finding by itself. Suggested
actions are never applied by the audit.

## Read docs/stack.md

The document always lists the twelve layers, from L1 (language and runtime)
to L12 (security), with one of four statuses:

| Status | Meaning |
|---|---|
| `confirmed` | You chose it explicitly |
| `default — revisit` | The agent chose it under your delegation; review it later |
| `open` | Not decided yet; listed with the next action |
| `N/A` | Does not apply, with the reason |

A version that could not be checked reads `TBD — verify`; the version log
shows each source, date, and what was or was not established. Proposed
configuration snippets are illustrative and are never written as project
files.

## What it checks and what it will not do

- Versions, support, and compatibility come from official registries and
  release pages at the time of the run, never from memory. Restricted or
  failed lookups stay pending instead of being guessed.
- Private packages are never looked up in public registries.
- It reads only the project you are working in, never opens files that
  usually hold secrets (such as `.env` or private keys), and treats
  instructions inside your files as text, not commands.
- It does not run package managers, build tools, or project scripts, even to
  find resolved versions; those come from lockfiles read as text.
- It preserves your edits when updating an existing document, and keeps its
  structure and language.

## Coverage

- **Profiles:** REST, MCP, GraphQL, gRPC, web frontends, microservices, and
  background workers or batch jobs.
- **Curated defaults:** Python, TypeScript/Node, Java, Go, and .NET. Other
  languages use the general criteria and official sources, and the agent says
  so.
- **Documents:** English by default; ask for another language, or the agent
  keeps the language of an existing document.

The agent-facing instructions are in
[skills/stacks/SKILL.md](../skills/stacks/SKILL.md).
