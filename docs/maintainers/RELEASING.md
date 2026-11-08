# Release process

A release publishes an identified revision of the skill and its resources.
Preparing a release does not authorize pushing, tagging, or publishing it.
Proceed with those external actions only within the owner's stated scope.

## Prepare and validate

1. Review the [changelog](../../CHANGELOG.md). Describe user-visible behavior,
   compatibility changes, and migrations without claiming a release that has
   not occurred.
2. Confirm that [SKILL.md](../../SKILL.md), references, and templates agree.
   Review relevant [acceptance scenarios](../../validation/README.md) and
   repeat agent exercises when workflow changes justify them.
3. Run the local checks from the repository root:

   ```bash
   python3 -B validation/check_skill.py
   python3 -B -m unittest discover -s validation -p 'test_*.py'
   git diff --check
   ```

4. Review the full diff, including untracked files. Remove only owned test
   fixtures and exclude caches, credentials, generated reports, and local
   environment data from the distribution.
5. Confirm that the [MIT license](../../LICENSE) and notices are retained,
   and that any incorporated third-party material has appropriate attribution.
6. Review the proposed public files and reachable Git history for credentials,
   private paths, internal notes, and unintended author or committer metadata.
   Removing a file from the latest tree does not remove its earlier revisions.

## Verify distribution

Confirm the public owner/repository and skill name before distributing the
installation command. The documented source is `alefiengo/stacks`; forks must
update the source identifier before distributing their installation command.

In a clean, disposable agent environment, install the intended published
revision using the [Skills CLI](https://skills.sh/docs/cli) or the agent's
manual skill installation procedure. Keep this verification separate from
development work and follow the owner's environment restrictions.

Verify that the installed package includes the entry point, every routed
reference, both templates, and the license. Run a define and an audit request;
inspect the resulting document paths and scope behavior. Record the revision,
agent, environment, commands, and observed outcome. A documentation review
does not replace this installation test.

For portability claims, repeat the relevant checks in independently identified
hosts or host configurations. Include plain-text questions, supplied-evidence
audits, no-write delivery, and unavailable retrieval. Record each result rather
than inferring universal host support from one successful agent exercise.
The [compatibility guide](../../references/compatibility.md) defines the required
fallback behavior; it does not require installing every host locally.

## Automation and publication

The [validation workflow](../../.github/workflows/validate.yml) runs repository
checks on pushes and pull requests. It requests read-only repository access,
does not deploy, and does not use production secrets. The checkout action is
pinned to an immutable revision; automated action updates are proposed through
[Dependabot](../../.github/dependabot.yml).

The initial checkout pin was observed in a
[skills.sh workflow example](https://skills.sh/thaddeusjiang/coding-skills/github-actions).
It is an identified example, not a claim that it is the latest upstream release.
Review action changes and observe hosted workflow results before reporting CI
as passing. The local validator checks the workflow's bounded policy; it does
not execute GitHub Actions.

When publication is authorized, identify the release revision, finalize its
changelog entry and version/tag using the repository's release convention,
then publish that revision. Keep a record of checks and any known limitations.
Do not advertise a tested public install or skills.sh listing until observed.
