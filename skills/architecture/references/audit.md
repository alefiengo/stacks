# Audit guide (Mode B)

Use this guide in Mode B of the [core workflow](../SKILL.md). Reconstruct the
architecture the code actually has, compare it with the project's own drivers
and documents, and report findings supported by evidence. Apply the
[safety guide](safety.md) to every read.

## Scope and inspection

- Establish the root and the user's scope. Without code or manifests in that
  scope, report that the architecture cannot be audited from the evidence and
  offer Mode A; do not produce an all-unknown report as if complete.
- Inspect, as text: the tree and module or package layout, entry points,
  imports and references between modules, configuration, data access and
  migrations, integration code (clients, consumers, published contracts),
  tests and their layout, and existing architecture documents and decision
  records.
- In a large codebase, identify deployable units and modules first, then
  sample; record what was sampled and what was not.
- Read `docs/stack.md` and an existing `docs/architecture.md` as the
  intended design when present. Without them, the drivers come from the user
  or remain unknown.

## Reconstruction

Build the as-is map before judging it:

- modules with their paths and apparent responsibility;
- the dependency graph from imports read as text, with its limits stated:
  dynamic loading, reflection, dependency injection, and generated code can
  hide edges;
- data ownership: which module writes which tables or collections, from
  migrations, models, and queries;
- integration styles and contracts in use;
- conventions observed in errors, logging, configuration, and tests.

Mark each element `observed` (seen in inspected files), `inferred` (deduced
from names or partial evidence), or `unknown`.

## Coverage

Record each area as `inspected`, `partial`, `not inspected`, or `N/A`.
`not inspected` is not evidence of absence. Absence claims state the paths
and patterns searched.

## Findings

Severities follow the `stacks` audit vocabulary, applied to architecture:

- **Critical:** evidence of severe impact now, such as a boundary bypass that
  exposes data across tenants.
- **Warning:** a demonstrated material problem needing planned work, such as
  a design that cannot meet a stated hard requirement, a dependency cycle
  between core modules, several modules writing the same
  table, or a contract change without versioning that breaks consumers.
- **Improvement:** a justified gain without a demonstrated failure, such as
  enforcing an existing rule with a tool or documenting an implicit
  convention.
- **Positive:** an inspected practice worth keeping.

Each finding records an ID, severity, area, evidence (`path:line` or a
scoped search), impact in this project, a concrete action, and confidence
(High, Medium, or Low, with inferences identified). A pattern that differs
from a textbook default is not a finding; a mismatch with the project's own
drivers, documents, or demonstrated problems is. No category has a quota.

## Target architecture

Only when the user asks for a target: describe the destination per area,
the migration steps in dependency order, and the first reversible step.
Write `docs/architecture.md` only when that document is requested, after the
audit, through Mode A with the audit as intake.

## Checkpoint and delivery

Present the as-is map, findings, and scope limits; seek context where it
changes a conclusion. An explicit request to complete the report without
checkpoints covers the write; record it. Deliver the
[audit template](../templates/architecture-audit.md) as
`docs/architecture-audit.md`, following the publication warning in the
[safety guide](safety.md#writes). Suggested actions are never applied by the
audit.
