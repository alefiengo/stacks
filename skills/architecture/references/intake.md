# Intake (Mode A)

Use this guide in Mode A of the [core workflow](../SKILL.md). Collect what
the design needs, select the depth, and ask only what remains unknown and
material.

Jump to: [Inputs](#inputs) · [Fields read from docs/stack.md](#fields-read-from-docsstackmd) ·
[Depth](#depth) · [Questions](#questions) · [Checkpoints](#checkpoints)

## Inputs

1. The user's request and stated requirements: record them as answered.
2. `docs/stack.md`, when present, read with the rules below.
3. An existing `docs/architecture.md`, `docs/architecture-audit.md`, or
   `docs/adr/`: read them before proposing anything; an audit produced in
   this conversation is intake, and its findings are not asked again.
4. Bounded repository evidence, under the [safety guide](safety.md): the
   tree, manifests, entry points, and existing module layout. In an existing
   codebase, a design that ignores the current structure needs an explicit
   redesign request.

Without `docs/stack.md`, infer the technology from manifests read as text,
or ask for the language and main framework in one question. When the
technology is still undecided, recommend `stacks` and continue
technology-neutral: modules, rules, data, and contracts can be designed,
while paths stay `open` (status `open` in section 5, a section 12 row) until
the language is known. Never choose the
technology here.

## Fields read from docs/stack.md

These headings, rows, and labels come from the `stacks` stack template.
Match them literally; a document in another language or structure is read on
a best-effort basis, and anything unreadable is treated as unknown.

- `## 1. Project profile`: profiles, components, audience and scale,
  constraints.
- `## 2. Stack summary`, with the table header
  `| # | Layer | Decision | Version | Status |`: decisions and their status,
  including component rows such as `L2 (api)`.
- `## 3. Decisions and rationale`: the L3 decision (pattern and repository
  layout) and the `**Authority and implementation state:**` text, which says
  whether code exists.
- `## 8. Security checklist`: trust boundaries and controls that shape
  module boundaries.
- `## 10. Open decisions, assumptions and next steps`: open items that limit
  the design.

Decision statuses are defined by `stacks`: `confirmed`,
`default — revisit`, `open`, and `N/A`. This skill uses the same four values
for architecture decisions, quality drivers, modules, rules, and
conventions. An `open` layer that a decision depends on keeps that decision
`open`.

`stacks` owns the pattern and the number of deployable services (L3 and its
service-scope question); this skill owns everything inside them, including
which capabilities each service holds.

- L3 decided: take it as given. A request to change it, or to compare it
  with another pattern, is answered by stating the recorded decision and
  suggesting `stacks` to revisit it; the design continues on the recorded
  pattern unless the user changes `docs/stack.md`.
- L3 `open` or unreadable: recommend a pattern in the shape checkpoint,
  marked `open` and pending `stacks`, and continue with modules that do not
  depend on it.
- No `docs/stack.md`: select the pattern here with the
  [design guide](design.md#choosing-the-structure) and say that `stacks`
  normally records it.

## Depth

Select the depth from evidence and state why; the user can override it.

| Depth | Typical signals | Sections with full content |
|---|---|---|
| `compact` | One deployable component, one team, a narrow domain, no strict compliance or availability targets | 1, 2, 5 (the same table with few rows), 6, 9, 10, 11, 12; 3 as one sentence; 7 whenever any remote interaction exists |
| `standard` | Several modules or components, a domain with distinct capabilities, more than one integration, or a team that will grow | All twelve, with a context diagram and a container diagram; no bounded-context map or ADR files |
| `extended` | Several teams or services, a broad domain, demanding quality attributes, regulated data, or a long-lived enterprise system | All twelve, adding bounded contexts and a context map, component diagrams per context, and ADR files |

- When signals conflict, ask one question with the depth recommendation.
- A section outside the depth stays in the document with one line: "Not
  detailed at compact depth", or a reason it does not apply.
- Raising the depth later adds detail; it never discards confirmed
  decisions.
- Section 5 and section 10 always keep their tables, whatever the depth:
  other skills read them.

## Questions

One decision per message, only when unknown and material. Skip what the
request, `docs/stack.md`, or the repository already answers.

1. **Domain and capabilities:** what the system does, in terms of its main
   business capabilities, and which are core versus supporting.
2. **Quality attributes:** the two or three that drive the design, each with
   a measurable target when one exists (for example latency, availability,
   throughput, recovery time, change frequency). "Unknown" is a valid answer
   and becomes an assumption.
3. **Team and ownership:** how many teams, and whether modules need separate
   owners or release cycles.
4. **Integrations:** external systems, other services, and whether work is
   synchronous, asynchronous, or batch.
5. **Constraints:** existing systems to respect, compliance, data residency,
   or organizational standards.
6. **Depth:** only when the signals conflict.

## Checkpoints

- **Checkpoint 1 — shape** and **Checkpoint 2 — architecture** follow the
  [core workflow](../SKILL.md). Each offers concrete choices, a
  recommendation, and free text.
- "Use as is" confirms the presented decisions; items presented as
  assumptions keep `default — revisit`.
- An explicit request to complete the document without checkpoints covers
  both checkpoints and the write; record the delegation in the document.
- If the user wants to stop, offer to write with the remaining items `open`.
  Without a reply, write nothing and summarize the state.
