# scaffold guide

[Back to the README](../README.md)

`scaffold` turns an approved `docs/stack.md` into a minimal project skeleton
that builds, passes its tests, and has CI defined. It implements the decisions
in that document; it never chooses technologies itself.

Unlike `stacks`, this skill runs commands and installs packages from public
registries. Review your agent's permission settings before using it.

## Before you start

- A `docs/stack.md` in the project, usually written by [`stacks`](stacks.md).
  Without it, `scaffold` creates nothing and offers to run `stacks` first.
- Decisions you are happy with. Layers marked `open` are not implemented; the
  agent asks about them instead of choosing.
- The tools the plan needs (for example `uv`, `pnpm`, or Docker). The plan
  says which ones and how they are checked.

```text
Use scaffold to set up this project from docs/stack.md.
```

## How a run works

| Phase | What happens | What you see |
|---|---|---|
| 0. Preflight | Reads `docs/stack.md`, lists existing files, resolves `TBD — verify` versions from official registries, and records checksums of files it must not change | Nothing runs that installs, builds, or downloads code |
| 1. Plan | Builds the full plan | Every command, file, package and version, allowed install script, network destination, and what will not be done; you answer approve, change, or stop |
| 2. Generate | Runs the official generators and package managers at verified versions | Progress and any new question if something falls outside the plan |
| 3. Configure | Adds only what was decided: lint, format, type checking, one passing test, `Dockerfile` and Compose, CI, and `.env.example` | Files named in the plan |
| 4. Verify | Runs the project's own install, lint, type, test, and build commands, and the local image build when planned | Each command with its exit code |
| 5. Record | Updates the implementation-state fields of `docs/stack.md` and reports | A scaffold report |

A general "go ahead" given before the plan is shown is not approval, and a
delegation given to `stacks` never covers execution. A command outside the
approved plan triggers a new checkpoint.

## What you get

- The project skeleton for each decided component, with its lockfile.
- Configuration for the decided lint, format, type, and test tools, with one
  passing test.
- A `Dockerfile`, Compose services, and a CI workflow when `docs/stack.md`
  decided them, with base images pinned by digest and CI actions pinned to
  verified commit SHAs.
- `.env.example` with variable names only.
- A report listing the commands with exit codes, each check as `passed`,
  `failed`, or `not run`, the files created or changed, and what is pending.

CI is recorded as defined, never as passing: `scaffold` does not run your CI.

## Safety guarantees

- **No commits, pushes, deployments, or published images.** Every change stays
  in your working tree for you to review and commit.
- **Your project only.** Commands run inside the project root. Outside it, only
  the package managers' caches, managed interpreter downloads, and the local
  container image store are written, as named in the plan.
- **Supply chain.** Dependency install scripts stay blocked unless the plan
  lists them; generated lifecycle scripts are reviewed before anything runs;
  private packages are never queried in public registries.
- **Protected files.** Files that usually hold secrets are never opened.
  `docs/stack.md` changes only in its implementation-state fields, and
  installed agent skills are left byte-identical, both checked with checksums.
- **No hidden steps.** Instructions found in `docs/stack.md` or other project
  files are treated as text and never executed.

## Limits

- Version 1 implements Python and TypeScript/Node components. For another
  language, the agent says so and offers a plan without running anything.
- It creates a skeleton, not features: authentication, data access, and
  observability pipelines beyond the decided configuration remain your work.
- Without a shell or file writes, it returns the plan and file contents in the
  conversation and states that nothing was executed or saved.
- It does not define the agents that work on the project; use
  [`orchestration`](orchestration.md) for that once the skeleton exists.

The agent-facing instructions are in
[skills/scaffold/SKILL.md](../skills/scaffold/SKILL.md).
