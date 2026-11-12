# Verification

Phase 4 — Verify establishes that the skeleton builds, its tests pass, and CI
is defined. Load this guide before Phase 4 — Verify and when recording
results. Use the [failure procedure](execution-safety.md#when-a-command-fails)
when a check does not pass.

## Check results

Each check has exactly one result. These values apply to executed checks
only; they are separate from the `stacks` verification states, which describe
versions and claims.

| Result | Meaning |
|---|---|
| `passed` | The command ran to completion after the last change to the files it covers and exited with code 0 |
| `failed` | The command exited with a nonzero code, was interrupted, or timed out |
| `not run` | The command did not run; the record states why, such as an `open` layer, a missing tool, or a host without a shell |

- Exit code 0 is necessary, not sufficient: a run that collected no tests,
  checked no files, or skipped the build is `failed`, with that reason.
- A rerun after a fix replaces the earlier result only when it covers the
  same files. Keep the earlier failure in the command log.
- Warnings do not change the result; list them when they matter to the user.

## What to check

Run the project's own commands, as the language reference and the generated
configuration define them, and not a tool's global defaults:

1. Dependency installation from the lockfile without updating it, after the
   lockfile was generated.
2. Lint and format check, in check mode; never let a check rewrite files
   during verification.
3. Type checking, when L4 decided a type checker.
4. Tests, with at least one test collected and passing.
5. The build or package step, when the stack has one.
6. The local container image build, only when L8 decided an image and the
   approved plan names the build.
7. Protected paths: `docs/stack.md`, the agent skill and agent
   configuration directories inside the root, and the root agent instruction
   files (`AGENTS.md`, `CLAUDE.md`) are byte-identical to their Phase 0
   checksums. `docs/stack.md` changes only in Phase 5 — Record, which
   confirms by comparison with the Phase 0 content that only the fields the
   [input contract](input-contract.md#fields-that-scaffold-writes) allows
   changed. A difference is `failed` and must be reported; restore nothing
   silently.

Configure CI to run the same commands. CI is recorded as `defined`, never as
passing: `scaffold` does not trigger or observe a CI run. A local syntax check
of the workflow counts only if the plan names it, and it verifies syntax only.

## Container image

- Build locally with a tag that the plan names and that identifies the
  project. The build never pushes, logs in to a registry, or publishes.
- Record the build command, exit code, date, and the local image identifier
  that the engine reported.
- A skipped build is `not run` with its reason; a failed build is `failed`.
  Neither is reported as built.
- Starting a container or Compose services is not part of verification unless
  the plan names it, together with the command that stops them.

## Recording

For every executed command, record:

- the command as run, with secrets redacted;
- the working directory relative to the project root;
- the exit code;
- the date, in ISO 8601 from the host clock, or `unknown`;
- for checks, the result and a short excerpt of evidence, such as the test
  count or the first error.

Record every version verified during the run with its exact source URL,
retrieval date, and item state. Report what configuration establishes
separately from what an executed command established: a written workflow,
linter configuration, or `Dockerfile` is not evidence that it runs.

The [scaffold report](../templates/scaffold-report.md) carries these records
to the user, and Phase 5 — Record copies the summary into the fields of
`docs/stack.md` that the [input contract](input-contract.md#fields-that-scaffold-writes)
allows.
