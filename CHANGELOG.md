# Changelog

## Unreleased

### Added
- Deterministic SHA-256 percentage rollout evaluation.
- Explicit user allowlists.
- Flag list, update, and delete operations.
- Health and readiness endpoints.
- Lifecycle and validation tests.
- Ruff, pytest, dependency-audit, Docker-build, and non-root CI gates.
- Security and integration documentation.

### Changed
- Repositioned the repository as the truthful Sky Feature Flags engineering-beta service.
- Refreshed Python dependencies and corrected the container entrypoint.
- Hardened the container to run as a non-root user.

### Known limitations
- In-memory state only.
- No authentication, RBAC, durable audit trail, tenant isolation, distributed consistency, or verified production deployment.
