# Contributing

Changes should make stack decisions clearer, recommendations more coherent,
audits better supported by evidence, generated project skeletons more
faithful to the approved stack, or agent teams better fitted to it. This
repository contains four agent skills, `stacks`, `architecture`, `scaffold`,
and `orchestration`, and their documentation; contributing does not require
application dependencies or a running cloud environment.

## Make a focused change

1. Read the [stacks SKILL.md](skills/stacks/SKILL.md), the
   [architecture SKILL.md](skills/architecture/SKILL.md), the
   [scaffold SKILL.md](skills/scaffold/SKILL.md), or the
   [orchestration SKILL.md](skills/orchestration/SKILL.md) and the resources
   relevant to your change. Each runtime package lives in its own `skills/<name>/`
   directory; repository documentation and tooling stay outside them.
2. Describe the behavior being improved with a concrete request or project
   situation. Keep unrelated wording and technology changes separate.
3. Update the instruction, reference, template and acceptance scenario together
   when they share a contract.
4. Run the local checks and record what was verified.

Keep examples portable and use synthetic data. Do not include credentials,
private project paths, customer information or copied proprietary code.
Follow [SECURITY.md](SECURITY.md) for potentially sensitive reports.

## Preserve the skill's contracts

- **Modes and activation:** distinguish stack definition from stack audit,
  and architecture design from architecture audit. Implementation and
  scaffolding requests alone should not start either interview. In this
  repository, `docs/architecture.md` is the user guide for the skill, not a
  skill output.
- **Questions and authorization:** ask one unresolved material decision at a
  time. Honor explicit delegation without interpreting silence as approval.
- **Layers:** retain L1–L12 in outputs and explain `N/A` entries. Check the
  layer applicability rules when adding a profile or changing a dependency.
- **Vocabulary:** keep decision status, inventory health, finding severity,
  verification state and security-control status distinct. Update their
  definitions, templates and scenarios together.
- **Evidence:** distinguish configuration from execution, declared from resolved
  or observed versions, and missing evidence from an established defect.
- **Recommendations:** treat language defaults as contextual starting points.
  A different framework is not a defect; compatibility, support and project
  requirements must drive recommendations.
- **Safety and scope:** preserve project boundaries, source restrictions,
  protection of secrets and existing documents, and the documentation-only
  output contract of `stacks`.
- **Scaffold execution:** `scaffold` requires an existing `docs/stack.md`,
  chooses no technologies, runs only the commands of an approved plan, never
  commits, pushes, deploys, or publishes images, and builds an image locally
  only when the approved plan names it. Do not widen these limits or add
  languages beyond Python and TypeScript without an owner decision.
- **Architecture outputs:** `architecture` writes only `docs/architecture.md`,
  `docs/architecture-audit.md`, and `docs/adr/`, runs no project commands,
  takes technology from `docs/stack.md` or manifests, keeps all twelve
  template sections at every depth, and keeps the headings and table headers
  that `scaffold` and `orchestration` read.
- **Orchestration writes:** `orchestration` requires an existing
  `docs/stack.md` and never changes it, runs no agents, package managers, or
  git, writes agent files and the `AGENTS.md` lead block only after an
  approved plan, and never writes host settings or user-level agent
  directories. Host formats live only in `references/hosts/`, with their
  official source and check date. Do not add a host without an owner decision.
- **Cross-skill contracts:** the skills do not link to each other. The block
  of secret-bearing file patterns must stay identical in the `stacks` security
  reference, the `scaffold` execution safety reference, and the
  `orchestration` and `architecture` safety references; every `docs/stack.md`
  field another skill reads or writes must exist in the `stacks` template;
  and every `docs/architecture.md` field `scaffold` or `orchestration` reads
  must exist in the `architecture` template. Change every side together; the validator checks them.

A change to a framework default must account for affected runtimes, packaging,
drivers, migrations, tests and deployment guidance. Avoid static claims about
the latest version or current provider capabilities; the skill verifies those
when used.

## Validate locally

From the repository root, with **Python 3.11+** and Git available:

```bash
python3 -B validation/check_skill.py
python3 -B -m unittest discover -s validation -p 'test_*.py'
git diff --check HEAD
```

The validator checks every `skills/*/` package. `git diff --check HEAD` also covers staged changes; run `git add -N <new files>`
first so untracked files are included. The validator uses the
Python standard library. No package installation,
application build or network access is required. It checks the local skill
structures and selected documentation contracts; it does not establish that an
agent follows every instruction.

Review the applicable [acceptance scenarios](validation/README.md), especially
when changing activation, checkpoints, source verification or inspection
boundaries. Add or adjust scenarios when a new failure case is introduced.

For a behavioral trial, use an isolated fixture and synthetic secrets as
described in the validation guide. Record the request, attempted tool access,
output and limitations. Keep structural checks, document walkthroughs and
actual agent trials separate in your results. `scaffold` trials run real
generators and install packages from public registries, so run them only on
your own machine, in a `validation/.trial-*` fixture, and never in CI.
`orchestration` trials write agent definitions; keep them in the same
fixtures and check the written files on disk. Do not label an unperformed
installation or runtime evaluation as tested.

## Submit a reviewable pull request

Lead with the user-visible problem and resulting behavior. Include:

- A concise explanation of the change and its reason.
- Relevant instructions, references or scenarios updated.
- Validation performed and any remaining limitations.

Use relative links for repository resources, keep executable commands
copyable, and avoid adding dependencies for checks the standard library can
perform. A documentation-only correction needs proportionate review; a change
to scope, verification or workflow needs evidence that the affected scenarios
still behave as intended.

The project uses the [MIT License](LICENSE). Include only material you are
entitled to contribute under those terms. If a contribution incorporates
third-party text or code, identify its source and preserve its notices.
