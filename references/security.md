# Security guidance

Use this guide for L7 (authentication and authorization) and L12 (security).
Choose controls from the system's trust boundaries, data, and exposure. Private
networking supplements identity and authorization; it does not replace them.
For evidence and reporting rules, see the [audit guide](audit.md).

Jump to: [Secrets](#secrets-and-audit-evidence) ·
[Dependencies](#dependency-and-supply-chain-scanning) ·
[Identity and access](#authentication-and-authorization-l7) ·
[Hardening](#api-and-browser-hardening) · [Checklist](#checklist-for-docsstackmd)

## Secrets and audit evidence

- Never put credentials in the repository, images, logs, or generated reports.
  Local `.env` files must be ignored; examples contain placeholders only.
  Use platform secret stores in CI and supported runtime secret injection.
- For a secret manager, distinguish environment-variable injection from file
  mounts; choose access controls, versions, and rotation behavior explicitly.
- Recommend a secret scanner such as gitleaks in applicable CI workflows.
  Local hooks are optional reinforcement, not proof the CI gate exists.
- During an audit, do not print secret values or copy them into evidence.
  Record the path, line, and secret type with values redacted. Treat scanner
  output as sensitive; summarize safely and do not upload repository contents
  to external services without authorization. Suspected exposed credentials need revocation or rotation
  and investigation; deleting a file alone does not revoke them.

## Dependency and supply chain scanning

- **Python:** pip-audit or a compatible vulnerability scanner.
- **Node.js:** package-manager audit, a scanner supporting the lockfile, or both.
- **Java:** a maintained vulnerability scanner supporting resolved Gradle or Maven
  dependencies, such as OWASP Dependency-Check where suitable. Dependency
  inventories and version-update tooling alone do not establish CVE coverage.
- **Containers:** trivy, grype, or the platform's supported image scanner when
  images are built. Scan the actual release artifact including base packages.
- Verify scanner maintenance, ecosystem coverage, advisory source, and failure
  policy. Findings need the affected version, applicable context, and remediation
  evidence; a clean scan does not establish the absence of vulnerabilities.
- Recommend dependency updates with tests and review proportionate to risk.
  Auto-merge only under an explicit team policy and passing applicable gates.
  Assess static application security testing (SAST), third-party action pinning,
  artifact provenance, and a software bill of materials (SBOM) according to
  distribution and assurance requirements. See [CI/CD](deployment.md#cicd-l9)
  for release permissions and artifact promotion.

## Authentication and authorization (L7)

- Use maintained framework or provider implementations for passwords, sessions,
  OAuth/OIDC, and token cryptography. Select user authentication, machine identity,
  local process permissions, or documented anonymous access according to the callers.
- Established OIDC providers are a starting point for interactive user auth.
  Compare existing identity systems, managed providers, or self-hosted options
  by enterprise login and provisioning needs, tenancy, residency, cost, and
  operational requirements. The cloud host does not dictate the user identity provider.
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
  Select refresh-token handling according to the provider and client protocol.
- Remote MCP authorization must match the current protocol, SDK, and clients:
  verify resource and authorization discovery, OAuth flows, token audience, scopes,
  and supported security requirements. Do not equate an arbitrary OIDC proxy
  or Cloud IAM policy with MCP client compatibility. Record unverified details.

## API and browser hardening

- Validate inputs at trust boundaries with framework-compatible validation.
  Add resource limits, request and body timeouts, and rate limiting where needed.
  GraphQL, gRPC, and MCP require protocol-specific limits beyond HTTP middleware.
- Configure explicit CORS origins where cross-origin browser access is needed;
  never combine wildcard origins with credentialed requests. Use CSP and other
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
- Dependency vulnerability coverage, update policy, and review gates.
- Release image scanning, immutable artifact identity, and build provenance.
- User/machine identity, token/session validation, and least privilege.
- Resource/tenant authorization and negative access tests.
- Cookie security and CSRF defense for browser sessions.
- Input validation, resource limits, rate limiting, and CORS policy.
- TLS, frontend headers, and restricted diagnostic endpoints.
- Redacted telemetry, access control, retention, and data policy.
- Database/storage backups, recovery ownership, and restore-test evidence.
- Protocol-specific MCP, GraphQL, or gRPC security where used.
