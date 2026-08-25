# Security Policy

## Current boundary

Sky Feature Flags is an engineering-beta, local-first service. Its HTTP API has no authentication or authorization layer and its state is in-memory. Do not expose it directly to untrusted networks or use it as the sole control plane for security-sensitive authorization decisions.

## Secure operating guidance

- Bind behind an authenticated gateway when used outside local development.
- Treat flag administration endpoints as privileged operations.
- Do not store secrets, credentials, access tokens, or personal data in flag descriptions or allowlists.
- Keep rollout identifiers pseudonymous where practical.
- Run the supplied container as its non-root user.
- Review dependency-audit results before releases.

## Unsupported security claims

The current repository does not provide RBAC, tenant isolation, signed flag bundles, tamper-evident audit logs, encryption-at-rest, distributed consistency, or production deployment validation.

## Reporting

Use the repository's private vulnerability-reporting channel when available. Avoid publishing exploit details before a remediation is available.
