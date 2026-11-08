# Changelog

Changes affecting skill behavior, compatibility, and maintenance are recorded
here. Unreleased work is not a published version.

## Unreleased

### Added

- Agent-specific installation and activation instructions, with a manual
  file-copy route and an optional shared installer.
- Agent-independent capability guidance and portability acceptance scenarios,
  including conversation-only and read-only delivery.
- MIT license and distribution guidance.
- Repository instructions for agents, contribution guidance, vulnerability
  reporting guidance, and a documented release process.
- Offline validation, negative tests, and 25 acceptance scenarios.
- Continuous validation and dependency updates for workflow actions.

### Changed

- Reworked the README and every skill reference and template for clearer
  navigation, consistent terminology, and explicit evidence requirements.
- Made checkpoints respect prior explicit delegation while retaining guided
  confirmation as the default.
- Made profile applicability, infrastructure defaults, and language coverage
  contextual, including static hosting, local stdio, and unsupported languages.
- Separated inventory health, finding severity, decision status, and control
  verification state.

### Fixed

- Restricted inspection to the authorized project, with explicit treatment
  of untrusted content, symlinks, secrets, and existing document updates.
- Required compatible supported stable dependency combinations, dated sources,
  withdrawn-release checks, and explicit partial-verification states.
- Corrected framework-dependent tooling, authentication and authorization,
  browser session protections, worker lifecycle, and deployment guidance.
- Separated untrusted pull-request checks from privileged release workflows.

The [validation guide](validation/README.md) describes reproducible checks
and their scope and limitations.
