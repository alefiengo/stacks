# Security Defaults

Guidance for layers L7 (auth) and L12 (security), plus the checklist that
lands in every `docs/stack.md`.

## Secrets

- Never in the repo, CI logs, or images. Local: `.env` (git-ignored) +
  committed `.env.example`. CI: platform secret store. Runtime on GCP:
  **Secret Manager** mounted as environment variables.
- **gitleaks** — secret scanning in pre-commit + CI. Default, non-negotiable.
- Rotate anything that ever touched a shared channel (chat, tickets, git
  history).

## Dependency & supply chain scanning

- **Python:** pip-audit (or osv-scanner) in CI.
- **Node:** pnpm audit + osv-scanner.
- **Java:** OWASP dependency-check or Gradle/Maven dependency analysis;
  GitHub dependency-review action on PRs.
- **Containers:** trivy (default) or grype in the CI pipeline.
- **SAST:** semgrep — recommended, light config; optional by user ask.
- **Automated updates:** Renovate (default; Dependabot acceptable) with
  sensible grouping; security updates auto-merge where policies allow.

## Authentication & authorization (L7)

- **Never hand-roll** password storage, session management, or token
  cryptography.
- **Exposed apps:** OIDC via an established provider:
  - GCP Identity Platform / Firebase Auth — default when deploying to
    Cloud Run.
  - Keycloak — self-hosted default, via Docker (compose locally; managed
    VM/cluster in prod).
  - Auth0 / WorkOS — SaaS when enterprise features (SSO, SCIM) are needed
    without ops investment.
- **Tokens:** short-lived JWTs validated via JWKS with audience and issuer
  checks; refresh token rotation for browser apps.
- **Service-to-service (Cloud Run):** Google-signed ID tokens + IAM invoker
  bindings; private ingress between internal services.
- **Browser frontends:** prefer a BFF or httpOnly cookie sessions; avoid
  localStorage-stored tokens where the architecture allows; state the
  tradeoff when recommending.

## API hardening

- Validate **all** input at the boundary (the validation library chosen in
  L2 — pydantic / zod / Jakarta Bean Validation).
- **Rate limiting:** Cloud Armor (GCP) or application middleware.
- **CORS:** explicit allowlist, never `*` with credentials.
- **Security headers** for frontends: HSTS, CSP, frame options.
- **TLS everywhere** — Cloud Run terminates TLS by default; require HTTPS
  redirects on custom domains.
- **File uploads:** size/type limits, malware scanning for untrusted
  sources, signed URLs for object storage access.

## Standard checklist (include in docs/stack.md)

- [ ] No secrets in repo — gitleaks runs in CI
- [ ] `.env` git-ignored; `.env.example` committed
- [ ] Dependencies scanned in CI (stack-appropriate tool)
- [ ] Containers scanned (trivy) before deploy
- [ ] Automated dependency updates enabled (Renovate/Dependabot)
- [ ] Auth via an established OIDC provider; JWKS validation with audience
      checks
- [ ] Service-to-service calls authenticated; private ingress where
      possible
- [ ] Least-privilege service accounts (one per service)
- [ ] Input validated at every boundary
- [ ] Rate limiting on public endpoints
- [ ] CORS allowlist explicit
- [ ] Structured logs free of PII and secrets
- [ ] TLS everywhere; HSTS on custom domains
- [ ] Database backups configured and restore tested
