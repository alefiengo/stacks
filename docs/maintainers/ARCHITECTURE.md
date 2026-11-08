# Skill architecture

`stacks` turns project requirements or repository evidence into technology
stack documentation. It is a knowledge package, not an application generator.

## Resource boundaries

| Resource | Responsibility | Loaded when |
|---|---|---|
| [SKILL.md](../../SKILL.md) | Activation, operating contract, modes, routing | Skill activation |
| [Compatibility](../../references/compatibility.md) | Host capability contract and safe fallbacks | Host adaptation or missing capabilities |
| [Interview](../../references/interview.md) | Missing requirements, guided decisions, release verification | Define mode |
| [Layers](../../references/layers.md) | Twelve-layer inventory and applicability | Decisions or inventory |
| [Decision criteria](../../references/decision-criteria.md) | Tradeoffs, health, support, compatibility | Recommendation or audit |
| Language references | Contextual Python, TypeScript/Node, and Java defaults | Selected or inspected component |
| [Deployment](../../references/deployment.md) and [security](../../references/security.md) | Cross-cutting operational decisions | Applicable layers |
| [Audit guide](../../references/audit.md) | Inspection, evidence, severity, prioritized actions | Audit mode |
| [Templates](../../templates/stack.md) | Output structure and rendering instructions | Writing project documents |
| [Validation](../../validation/README.md) | Repository checks and acceptance scenarios | Maintainer work |

References are loaded on demand. The entry point should route rather than
repeat every detail. Resource paths are relative to the installed skill;
project inputs and outputs are relative to the separately authorized target.

The runtime is independent of a particular agent or API. Native skill loading,
file tools, retrieval, structured questions, and planning UI are capabilities
that the host may provide. Missing capabilities use explicit fallbacks: ordinary
conversation, supplied evidence, pending external checks, or a complete document
returned without claiming a file was saved. Maintainer tooling and AGENTS.md
are not runtime dependencies.

## Modes and artifacts

Define mode combines declared constraints, a bounded intake, contextual
defaults, and permitted official verification sources. It writes
`docs/stack.md`. Audit mode combines scoped repository evidence and permitted
external checks, then writes `docs/stack-audit.md`. A target stack document
is optional and requires a request or prior authorization.

Both modes preserve existing user content and write documentation only.
Without safe file writes, they return the complete intended document in the
conversation and explicitly state that it has not been saved.
They do not install dependencies, execute project scripts, create application
configuration, or deploy. Maintainer validation scripts belong to this
repository and are separate from the installed skill's project workflow.

## Shared contracts

The skill and both templates retain L1–L12 in their summary inventories.
Applicability is contextual: mark an irrelevant layer N/A and explain why.
Decision status, inventory health, finding severity, and control status have
different meanings; use their canonical definitions instead of merging them.

Guided checkpoints require an explicit reply unless prior authorization
already covers the choice and writing. Unknown facts remain unknown even
when the user delegates a decision. Available package versions are not
automatically compatible, supported, stable, or verified.

## Design choices

- Curated defaults reduce repeated research while preserving user constraints.
  They are starting points, not a basis for negative findings on their own.
- Docker is a useful local default for networked service dependencies; delivery
  requirements decide whether the application needs a container.
- Verification happens at recommendation time rather than through a stale
  catalog of current versions embedded in Markdown.
- Evidence and coverage are explicit so a partial audit remains useful without
  claiming a complete assessment.
- Maintainer checks use the Python standard library. Adding a toolchain should
  solve a demonstrated maintenance problem.

For change validation, see [CONTRIBUTING.md](../../CONTRIBUTING.md). For
publication, see [RELEASING.md](RELEASING.md).
