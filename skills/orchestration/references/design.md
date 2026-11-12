# Team design

Use this guide in Phases 1 and 2 of the [core workflow](../SKILL.md). It
defines the host-neutral vocabulary of `docs/agents.md`; the host references
map it to files. Statuses come from the [input contract](input-contract.md#behavior-by-status).

Jump to: [Principles](#principles) · [Lead](#the-lead) ·
[Roles](#role-catalog) · [Capabilities](#capability-classes) ·
[Model tiers](#model-tiers-and-effort) · [Write scopes](#write-scopes-and-parallel-work) ·
[Specification](#role-specification) · [Flow](#orchestration-flow) ·
[Handoffs](#handoff-contract)

## Principles

- **Fewest roles that pay for themselves.** Each subagent starts with an empty
  context and costs its own model and tool work, so a delegation must save
  more than it costs. Justify a subagent by at least one of: it isolates noisy
  output (exploration, logs, test runs) from the lead; it needs narrower
  capabilities than the lead; it runs independent work in parallel.
- **One owner per decision.** The lead owns requirements, the plan, the user
  conversation, integration, and the final verification. A subagent owns one
  bounded task and returns evidence.
- **Derived from the stack, not from a catalog.** Each role cites the layers or
  components that justify it, for example `L2 (api)`, `L5`, or `L12`. A layer
  that is `N/A` or `open` justifies no specialist.
- **Shallow delegation.** The lead delegates; subagents never delegate in
  this version, so no role receives the delegate capability.
- **Same boundaries everywhere.** No role commits, pushes, tags, deploys,
  publishes, creates cloud resources, or reads secret-bearing files unless the
  user gives that instruction to the lead during the work.
- **Small teams are valid.** A small project may need the lead alone, or the
  lead and one or two subagents; record why more roles were not added.

## The lead

The lead is the main session of the host, guided by the lead block written to
the root `AGENTS.md`. It is not a subagent file: hosts give the main session
the user conversation, approvals, and delegation, which subagents lack.

The lead block states:

- the team, with one line per role on when to delegate to it;
- the delegation contract in [handoffs](#handoff-contract);
- which roles may run in parallel and which run one at a time;
- the user checkpoints: before changing scope, before any outward or
  irreversible action, and when a role reports a blocker;
- that the lead integrates results, reruns the verification role after the
  last change, and reports what was verified and what was not; without a
  verification role, the lead runs the section 5 commands of `docs/stack.md`
  itself or reports them as not verified;
- that a skill or workflow governing the current task, such as `stacks` or
  `scaffold`, takes precedence: the lead delegates or runs roles only when
  that workflow allows it.

List only materialized roles. Keep the block short; it loads into every
session of the project. Hosts can
also load it into subagents, so it opens by addressing the lead only and
telling any subagent to follow its own role instructions instead.

```markdown
<!-- orchestration:start -->
## Agent team

This section is for the lead, the main session. A subagent ignores it and
follows its own role instructions. The design is in docs/agents.md. When a
skill or workflow governs the current task, follow it first, and delegate or
run roles only when it allows.

Delegate to these roles; do the rest yourself:

- `<role_name>`: <when to delegate, in one line>.

Every delegation states the objective, inputs, constraints, expected output,
and done criteria. Run read-only roles in parallel; run editing roles one at
a time unless their write scopes are disjoint. After the last change,
<run `<verifier_role>` | run the checks in docs/stack.md section 5> and report
what was verified and what was not.

Ask the user before changing scope and before any commit, push, deployment,
or other outward or irreversible action. Never open secret-bearing files.
<!-- orchestration:end -->
```

## Role catalog

Starting points, adopted only when the stack justifies them. Rename them to
the project's vocabulary, drop what does not apply, and avoid the names each
target host reserves (its host reference lists them); for example
`code_explorer` rather than `explorer`.

| Role | Adopt when | Capabilities | Writes | Tier |
|---|---|---|---|---|
| Explorer | The codebase is large enough that mapping code paths before a change floods the lead | read | nothing | fast |
| Implementer (one per component) | A component has its own paths, language, or framework (`L2 (api)`, `L2 (web)`, a worker) | read, edit, shell | that component's paths | standard |
| Verifier | `docs/stack.md` defines lint, type, test, or build commands (L4, L5, section 5) | read, shell | nothing | fast |
| Reviewer | Changes need correctness and security review against L7 and L12 decisions | read | nothing | deep |
| Data specialist | L6 decided an engine with migrations and schema work is frequent | read, edit, shell | migration and schema paths | standard |
| Delivery specialist | L8 or L9 decided containers or CI and those files change often | read, edit | container, Compose, and CI files | standard |
| Researcher | L2 frameworks or protocols change quickly and the team must check official documentation | read, web | nothing | fast |

- A verifier runs the project's own commands and reports results; it does not
  fix code. Fixes go back to the owning implementer.
- A reviewer reports findings with evidence; it does not edit. Its findings
  feed the lead's next delegation.
- An implementer may run the commands needed to check its own change, within
  its paths; the verifier's run is the one the lead reports.
- No role deploys. Deployment stays with the user or a separate process.

## Capability classes

Host-neutral classes that the host references map to tools and settings:

| Class | Allows |
|---|---|
| read | Read and search files inside the project root |
| edit | Create and change files inside the role's write scope |
| shell | Run commands; a shell can also change files, so write scopes are advisory for any role with shell |
| web | Fetch official documentation and registries |
| delegate | Start other subagents; the lead only |

Grant the smallest set that completes the task. A role that only reports
needs read, plus shell only when it must execute checks.

**Enforcement status** records how a restriction holds on a host:

- **enforced** — the host removes the capability or blocks the action, as its
  official documentation states;
- **advisory** — only the role's instructions ask for it; the host does not
  prevent it.

Record enforcement per role and host in `docs/agents.md`. Never describe an
advisory restriction as a guarantee.

## Model tiers and effort

The design names a tier, not a model; the host reference maps tiers to
current models after verification.

| Tier | Use for |
|---|---|
| deep | Ambiguous, multi-step, or high-stakes reasoning: review, security, architecture, difficult debugging |
| standard | Implementation of a clear, bounded task |
| fast | Narrow, repeatable, or read-heavy work: exploration, verification, research summaries |
| inherit | No reason to differ from the lead's model |

Effort is `low`, `medium`, `high`, or `session` (left to the host session)
in the design, independent of the tier; use higher effort for roles that
trace complex logic or check assumptions. A host may support more
levels; map only what its documentation lists. Prefer `inherit` when the
user's account, provider, or plan makes model availability uncertain.

## Write scopes and parallel work

- Give every editing role a write scope: paths or globs taken from the L3
  structure and the project tree, disjoint from other editing roles. Shared
  files, such as a root manifest or lockfile, belong to one role or to the
  lead.
- Run read-only roles in parallel freely. Run editing roles in parallel only
  when their write scopes are disjoint and none changes a shared file;
  otherwise run them one at a time. A host-provided isolated copy of the
  repository, where documented, is an option the design may name.
- Write scopes are advisory unless a host reference states a mechanism that
  enforces them.

## Role specification

Every role in `docs/agents.md` has:

- **Name:** lowercase letters, digits, and underscores, unique in the team, the
  same on every host.
- **Description:** one or two sentences on when the lead delegates to it; the
  host uses this text to route work.
- **Mission:** the single responsibility, in one sentence.
- **Project context:** the project, its components, and the stack decisions
  that matter to the role, so a subagent without the conversation can work.
- **Serves:** the layers or components that justify it.
- **Capabilities and write scope:** classes from above and the paths it may
  change.
- **Model tier and effort.**
- **Inputs:** what the lead must pass: objective, paths, relevant decisions
  from `docs/stack.md`, constraints.
- **Procedure:** three to six steps specific to the stack, for example the
  exact verification commands from section 5.
- **Output and done criteria:** the format it returns and what must be true
  before it reports done.
- **Boundaries:** what it never does, including the shared boundaries.
- **Escalation:** when it stops and reports to the lead instead of guessing.
- **Status:** `confirmed`, `default — revisit`, `open`, or `N/A`.

Role instructions are written for a subagent that starts without the
conversation: state the project, its stack decisions that matter to the role,
and the paths, in the role itself. Do not rely on the subagent loading other
project instructions.

## Orchestration flow

Describe the usual flow as numbered phases, for example: understand and plan
(lead, explorer); implement (implementers, one per component, parallel only
with disjoint scopes); verify (verifier); review (reviewer); integrate and
report (lead). For each phase name the roles, what runs in parallel, the
handoff into the next phase, and the user checkpoint, if any. Add variants
only for frequent work, such as a bug fix that skips the explorer.

## Handoff contract

Every delegation from the lead states:

1. the objective and why it matters;
2. the inputs: paths, decisions, and prior findings;
3. the constraints: write scope, commands allowed, what not to touch;
4. the expected output and its format;
5. the done criteria.

Every result returned to the lead contains:

- a summary of what was done or found;
- evidence: files and lines, commands with exit codes, or sources with dates;
- files changed, or "none";
- open questions and blockers;
- what was not verified.

A result without evidence is a claim; the lead verifies it before reporting
it to the user.
