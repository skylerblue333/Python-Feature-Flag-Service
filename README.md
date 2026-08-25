# Sky Feature Flags

A focused Python/FastAPI feature-flag service for deterministic local evaluation. The repository is an engineering-beta component, not a hosted control plane or production feature-management platform.

## Implemented behavior

- Create, list, read, update, and delete named flags.
- Global enable/disable switch per flag.
- Deterministic percentage rollout based on SHA-256 of flag name and user ID.
- Explicit per-user allowlist that takes precedence over percentage rollout.
- Validation for flag names, descriptions, rollout percentages, and bounded allowlist size.
- `/health` and `/ready` operational endpoints.
- Conservative evaluation behavior: unknown flags evaluate disabled rather than enabled.
- Non-root container image.

All state is currently process-local memory. Restarting the service clears flags.

## Run locally

```bash
python -m pip install -r requirements.txt
uvicorn src.service:app --host 127.0.0.1 --port 8000
```

Example flag:

```json
{
  "name": "new_checkout",
  "description": "Gradual checkout rollout",
  "rule": {
    "enabled": true,
    "percentage": 25,
    "user_ids": ["internal-user"]
  }
}
```

Evaluate it with `GET /evaluate/new_checkout/<user-id>`.

## Verification

CI requires Python compilation, Ruff, pytest, dependency auditing, container build, and a non-root runtime check.

Local checks:

```bash
python -m compileall -q src tests
ruff check src tests
pytest -q
pip-audit -r requirements.txt
docker build -t sky-feature-flags .
docker run --rm --entrypoint id sky-feature-flags -u
```

## Architecture

The HTTP layer and evaluation logic live in `src/service.py`. Flag definitions are validated with Pydantic. Percentage assignment is deterministic and requires no external randomness or network dependency. This makes the current component useful for local services and integration experiments while keeping its operational boundary explicit.

## SKYCOIN4444 integration

A SKYCOIN4444 service can consume this component through its HTTP API rather than copying the implementation. Suitable uses include controlled rollout of UI, API, feed, marketplace, or experimental features. A production integration should add durable storage, authentication/authorization, audit history, tenant isolation, caching strategy, and rollout governance before relying on it for high-impact controls.

## Status and limitations

**Status: Engineering Beta.** Implementation and automated verification are being hardened, but deployment is not verified.

This repository does **not** currently provide durable persistence, distributed consistency, multi-region replication, RBAC, tenant isolation, signed configuration, approval workflows, audit-log durability, SDKs, streaming updates, or a production deployment. It should not be described as GA, enterprise-ready, or production-ready without evidence for those capabilities.

See `SECURITY.md` for security boundaries and `CHANGELOG.md` for productization history.
