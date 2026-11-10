# Security

This skill guides an agent's inspection and documentation of a technology
stack. Security reports are especially useful when its instructions can cause
an agent to exceed the authorized scope, expose sensitive data or present an
unsupported security conclusion as established fact.

## What to report

Examples include:

- Prompt injection in project files or retrieved content that overrides the
  user's request or expands authorized access.
- Reads or writes outside the project boundary, including through symlinks.
- Secret values or private project content appearing in tool output, reports
  or external requests.
- Execution of project scripts, dependency installation or deployment during
  a documentation-only task.
- Misleading verification claims that could affect a security decision, such
  as reporting an unchecked dependency as safe or configured tests as passed.

An alternative technology preference or ordinary documentation defect can be
reported through the normal issue or contribution workflow.

## Report safely

Report privately through GitHub's
[private vulnerability reporting](https://github.com/alefiengo/stacks/security/advisories/new).
If that form is unavailable, open a minimal public issue requesting private
coordination without technical details. State only the general category and
affected revision, and agree on a private channel before sharing sensitive
details.

The project does not promise a response time. The supported revision is the
latest commit on `main`; no releases have been published.

Do not put credentials, private code, customer data, exploitable details about
a live system or actual personal configuration paths in a public issue.
Do not test a suspected credential or reproduce an access violation against
another person's environment.

Once an appropriate channel is agreed, a useful report contains:

- The affected revision and agent environment, where known.
- The request, relevant skill instruction and observed behavior.
- A minimal reproduction using an isolated fixture and synthetic data.
- The expected boundary, actual impact and any conditions needed to reproduce.
- A proposed correction or mitigation, if available.

Preserve enough detail to explain the issue while redacting sensitive values.
For a symlink reproduction, use a nonexistent external target and record the
attempted access rather than pointing at real credential files.

## If information was exposed

Stop the affected workflow and contain the exposure. Revoke or rotate exposed
credentials through their owner, review unintended writes or external
transmissions, and preserve a redacted account of what happened. Deleting a
report does not by itself invalidate a leaked credential.

The skill's instructions and validation reduce known failure modes; they do
not establish a security certification or an exhaustive review. Documented
controls, successful local checks and observed agent behavior are different
forms of evidence.
