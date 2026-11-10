# Security guidance

Use this guide for L7 (authentication and authorization) and L12 (security).
Choose controls from the system's trust boundaries, data, and exposure. Private
networking supplements identity and authorization; it does not replace them.
For evidence and reporting rules, see the [audit guide](audit.md).

Jump to: [Secrets](#secrets-and-audit-evidence) ·
[Secret-bearing files](#secret-bearing-files) ·
[Dependencies](#dependency-and-supply-chain-scanning) ·
[Identity and access](#authentication-and-authorization-l7) ·
[MCP](#mcp-servers) ·
[Hardening](#api-and-browser-hardening) · [Checklist](#checklist-for-docsstackmd)

## Secrets and audit evidence

- Never put credentials in the repository, images, logs, or generated reports.
  Local `.env` files must be ignored; examples contain placeholders only.
  Use platform secret stores in CI and supported runtime secret injection.
- For a secret manager, distinguish environment-variable injection from file
  mounts; choose access controls, versions, and rotation behavior explicitly.
- In CI, start from the gitleaks CLI or the host's native secret scanning;
  verify the license terms of any wrapper action. Local hooks are optional
  reinforcement, not proof the CI gate exists.
- During an audit, apply the [secret-bearing file rule](#secret-bearing-files);
  never print secret values or copy them into evidence. Treat scanner output as
  sensitive and do not upload repository contents to external services without
  authorization. Suspected exposed credentials need revocation or rotation and
  investigation; deleting a file alone does not revoke them.

## Secret-bearing files

This rule applies in both modes.

<!-- shared:secret-bearing-files:start -->
- Do not open: `.env` and `.env.*` (except `.env.example`, `.env.sample`,
  `.env.template`), `*.pem`, `*.key`, SSH private keys such as `id_rsa`,
  `id_ecdsa`, or `id_ed25519` (not `*.pub`), `*.p12`, `*.pfx`, `*.tfvars`,
  `*.tfstate`, `.npmrc`, `.pypirc`, kubeconfig files, and `credentials` or
  `secrets` data files (`.json`, `.yaml`, `.yml`, `.toml`, `.ini`, or no
  extension). Source code with those names is not secret-bearing by name.
- Report only the path and a class (environment file, private key, keystore,
  infrastructure state or variables, registry or cluster credentials), assigned
  by name and path without opening the file.
- If a file being read shows an inline credential, stop quoting it and record
  only `path:line` and the credential class.
- Call such a file "tracked" only with version-control evidence; otherwise "present".
<!-- shared:secret-bearing-files:end -->

## Dependency and supply chain scanning

- **Python:** pip-audit or a compatible vulnerability scanner.
- **Node.js:** package-manager audit, a scanner supporting the lockfile, or both.
- **Java:** a maintained vulnerability scanner supporting resolved Gradle or Maven
  dependencies. OWASP Dependency-Check is impractically slow without an NVD
  API key (store it as a CI secret) and needs a data cache and a suppression
  policy; OSV-Scanner or SBOM scanning are alternatives.
  Dependency inventories and version-update tooling alone do not establish CVE coverage.
- **Go:** govulncheck (`govulncheck ./...`), which uses the Go vulnerability
  database and reports vulnerabilities reachable from the analyzed code.
  Results depend on the analyzed packages and build configuration.
- **.NET:** NuGet Audit runs during restore and reports NU1901–NU1904 warnings;
  `NuGetAuditMode` selects direct or transitive coverage, and its default
  depends on the target framework, so set it explicitly. Promote the selected
  severities to errors in CI, where a report command such as
  `dotnet list package --vulnerable --include-transitive` (`dotnet package
  list` in newer SDKs) can run. The stack workflow itself never runs it.
- **Containers:** trivy, grype, or the platform's supported image scanner when
  images are built. Scan the actual release artifact including base packages.
- Pin scanner actions, binaries, and images to a SHA or digest; scanners get
  no deployment credentials or production secrets.
- Malicious or compromised packages are a risk distinct from known CVEs: allowlist install
  scripts, consider a minimum release age, enforce lockfile integrity in CI,
  and review maintainer changes on critical dependencies. Verify which controls
  the selected package manager supports and its current defaults.
- Verify scanner maintenance, ecosystem coverage, advisory source, and failure
  policy. Findings need the affected version, applicable context, and remediation
  evidence; a clean scan does not establish the absence of vulnerabilities.
- Recommend dependency updates with tests and review proportionate to risk.
  Auto-merge only under an explicit team policy and passing applicable gates.
  Assess static application security testing (SAST), third-party action pinning,
  artifact provenance, and a software bill of materials (SBOM) according to
  distribution and assurance requirements; verify the current license of a
  selected SAST edition. See [CI/CD](deployment.md#cicd-l9)
  for release permissions and artifact promotion.

## Authentication and authorization (L7)

- Use maintained framework or provider implementations for password hashing,
  sessions, OAuth/OIDC, and token cryptography. Select user authentication,
  machine identity, local process permissions, or documented anonymous access
  according to the callers.
- Established OIDC providers are a starting point for interactive user auth.
  Compare existing identity systems, managed providers, or self-hosted options
  by enterprise login and provisioning needs, tenancy, residency, cost, and
  operational requirements. The cloud host does not dictate the user identity provider.
- Clients acting for a user use the authorization code flow with PKCE, never
  the implicit or password grants; machine clients use client credentials or
  workload identity federation. Public-client refresh tokens must be rotated
  or sender-constrained. Verify against RFC 9700 (OAuth security BCP) and the provider.
- For JWT-based schemes validate signature with trusted keys and allowed
  algorithms, issuer, audience, lifetime, and required claims using maintained
  libraries; handle key rotation and token type correctly. JWKS discovery must
  not trust attacker-chosen endpoints. Other schemes require their own verified
  protocol checks rather than assuming every credential is a JWT.
- Define authorization per action, resource, ownership, role, and tenant as
  applicable. Deny by default, enforce on the server, and test unauthorized
  and cross-user or cross-tenant access. Authentication alone does not grant access.
- Service-to-service calls need identities and least-privilege permissions;
  verify intended audience and caller authorization. Private ingress and network
  isolation are additional boundaries. For a local tool, document operating
  system and client permissions rather than adding an irrelevant web login.
- For browsers, a backend for frontend (BFF) or cookie sessions can reduce
  browser token exposure. Use Secure and HttpOnly cookie attributes, an appropriate
  SameSite policy, server-side invalidation and expiry, and CSRF protection for
  cookie-authenticated state changes.
  XSS controls are still required; CORS does not replace CSRF protection.

## MCP servers

Verify these against the current MCP specification and the selected SDK and
clients; record unverified details.

- **Streamable HTTP:** validate `Origin` on every connection and reject invalid
  ones. Bind local HTTP servers to loopback and authenticate; prefer stdio locally.
- **Authorization:** verify resource and authorization server discovery, flows,
  audience, and scopes. Accept only tokens issued for this server; no token
  passthrough. An OIDC proxy or cloud IAM policy is not MCP client compatibility.
- **Sessions:** a session ID is not authentication. Verify every request; use
  secure random session IDs bound to the authenticated user.
- **Proxies to third-party APIs:** require per-client consent before the
  third-party flow and exact redirect URI matching.
- **Clients:** treat OAuth metadata discovery URLs as untrusted; apply SSRF controls.

## API and browser hardening

- Use parameterized queries or the ORM's bound parameters; never build SQL or
  shell commands by concatenating input. Apply contextual output encoding
  through the template or framework layer.
- Validate inputs at trust boundaries as defense in depth, not a substitute
  for those controls. Add resource limits, timeouts, and rate limiting as needed.
  GraphQL, gRPC, and MCP require protocol-specific limits beyond HTTP middleware.
- Server-side fetches of user-influenced URLs need a destination allowlist;
  block internal ranges and metadata endpoints and validate redirects.
- CORS uses an exact origin allowlist: never reflect `Origin` unvalidated,
  allow `null`, use prefix/suffix/regex matching, or combine wildcard origins
  with credentials. Use CSP and other
  headers according to the frontend's actual resource and embedding model.
- Use appropriate TLS for network trust boundaries; configure secure external
  endpoints, redirects, and HSTS where suitable. Document controlled internal
  TLS termination and cleartext HTTP/2 (h2c) explicitly when required by the
  platform contract.
- Uploads need size and type checks, safe names and storage, scoped access, and malware
  scanning where the threat model requires it. Signed URLs must be bounded by
  operation, access policy, and expiration as supported.
- Minimize and redact personal data and secrets in logs, traces, and errors.
  Define retention and access. Restrict health, diagnostic, and admin endpoints
  as appropriate.
- Stateful systems need backups, access control, retention, and a documented
  restore test. A recommendation for backups is not evidence of recovery.

## Checklist for docs/stack.md

Record each control in a table with columns for **control**,
**applicability and reason**, **status**, and **evidence or planned validation**.
Use `planned`, `verified`, `pending verification`, or `not applicable` as status.
Use `verified` only for evidence actually inspected or a check actually run,
and describe exactly what it establishes. An inspected CI
configuration verifies configuration only, not successful execution or effective
enforcement. Do not mark recommendations as implemented. A skip needs a reason.

For example, a design proposal can record these controls before implementation:

| Control | Applicability and reason | Status | Evidence or planned validation |
|---|---|---|---|
| Tenant authorization | API serves several customers | planned | Test denied cross-tenant reads and writes. |
| Session CSRF protection | API accepts bearer tokens only, with no cookie authentication | not applicable | Reassess if browser sessions are introduced. |

Assess these controls when applicable:

- Secret exclusion, example placeholders, scanning, and rotation ownership.
- Dependency vulnerability coverage, malicious-package controls, update
  policy, review gates, and pinned scanners.
- Release image scanning, immutable artifact identity, and build provenance.
- User/machine identity, OAuth flow and token/session validation, and least privilege.
- Resource/tenant authorization and negative access tests.
- Cookie security and CSRF defense for browser sessions.
- Parameterized queries, output encoding, and SSRF destination allowlists.
- Input validation, resource limits, rate limiting, and CORS origin allowlist.
- TLS, frontend headers, and restricted diagnostic endpoints.
- Redacted telemetry, access control, retention, and data policy.
- Database/storage backups, recovery ownership, and restore-test evidence.
- Protocol-specific MCP, GraphQL, or gRPC security where used.
