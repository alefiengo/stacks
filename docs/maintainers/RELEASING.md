# Release process

A release publishes an identified revision of the skill and its resources.
Preparing a release does not authorize pushing, tagging, or publishing it.
Proceed with those external actions only within the owner's stated scope.

## Prepare and validate

1. Review the [changelog](../../CHANGELOG.md). Describe user-visible behavior,
   compatibility changes, and migrations without claiming a release that has
   not occurred.
2. Confirm that [SKILL.md](../../skills/stacks/SKILL.md), references, and
   templates agree.
   Review the [acceptance scenarios](../../validation/README.md) affected by
   the change. Choose document review or targeted agent exercises in proportion
   to the behavior and risk being changed.
3. Run the local checks from the repository root:

   ```bash
   python3 -B validation/check_skill.py
   python3 -B -m unittest discover -s validation -p 'test_*.py'
   git diff --check HEAD
   ```

   Run them with Python 3.11 or later. The CI whitespace check covers the
   whole tree, not only the latest commit; to reproduce it locally, run
   `git diff --check "$(git hash-object -t tree /dev/null)" HEAD`.

4. Review the full diff, including untracked files. Remove only owned test
   fixtures and exclude caches, credentials, generated reports, and local
   environment data from the distribution.
5. Confirm that the [MIT license](../../LICENSE) and notices are retained,
   and that any incorporated third-party material has appropriate attribution.
6. Review the proposed public files and reachable Git history for credentials,
   private paths, internal notes, and unintended author or committer metadata.
   Removing a file from the latest tree does not remove its earlier revisions.

## Package and installation guidance

Confirm the public owner/repository and skill name before distributing the
installation command. The documented source is `alefiengo/stacks`; forks must
update the source identifier before distributing their installation command.

Keep the shared [installation guide](../INSTALLATION.md) consistent with the
distributable resources and the agent's own skill-loading procedure. The same
skill package is used across agents; installation instructions may differ by
host. Check that `skills/stacks/` includes the entry point, every routed reference,
both templates, and the license, and contains no maintainer files.

For packaging changes, check the installation in a disposable project and
exercise define and audit requests. Record the revision, environment, actions,
and output paths separately from document review.

Review relevant plain-text questions, supplied-evidence audits, no-write delivery
and unavailable-retrieval scenarios against the
[capability contract](../../skills/stacks/references/compatibility.md).

## Automation and publication

The [validation workflow](../../.github/workflows/validate.yml) defines the
repository checks for pushes and pull requests. It runs the validator, the
validator tests, and the whole-tree whitespace check above. It requests
read-only access, does not deploy, and does not use production secrets.
Actions are pinned to a commit SHA with the released version in a comment;
automated action updates are proposed through
[Dependabot](../../.github/dependabot.yml).

## Versioning

Releases follow [Semantic Versioning](https://semver.org/). A release is a Git
tag `vX.Y.Z` on the released revision; the tag is the only source of the
version, so it is not duplicated in `SKILL.md` frontmatter. In the changelog,
move the `## Unreleased` entries under a `## [X.Y.Z] - YYYY-MM-DD` heading
only when that release is published.

When publication is authorized, identify the release revision, finalize its
changelog entry, create the matching tag, then publish that revision. Keep a
record of checks and any known limitations.
Do not advertise a tested public install or skills.sh listing until observed.
