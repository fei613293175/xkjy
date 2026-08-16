# P00 Acceptance Record

This document is completed only from server and real-device evidence. It does not claim later-release features exist.

## Scope

- Repository, Docker Compose, PostgreSQL, Redis, Go API, Vue admin shell, Compose Android shell.
- Resource registry, V1.3.0 token application, migration ledger, OpenAPI, health checks, structured logs and visual-diff tooling.
- Excluded: account, game board, projects, mall, payment, wallet, identity and withdrawal workflows.

## Evidence Required Before P00 Completion

| Item | Evidence | Status |
| --- | --- | --- |
| Hardened repository validator | Server command output | Pending |
| Go unit tests | Server command output | Pending |
| Vue type check and production build | Server command output | Pending |
| Docker service health | healthz, readyz, migration ledger and redacted logs | Pending |
| Release APK | Server-built signed APK checksum and package metadata | Pending |
| Android real-device acceptance | Device state, install/launch, interaction path, logcat, screenshots | Pending |
| Visual acceptance | P00 manual layout review; later Page ID runs must score at least 90% | Pending |

## Visual Gate Boundary

P00 has no dedicated V1.3.0 native page baseline. The supplied 132 images correspond to later page IDs, so a numeric similarity result for the P00 diagnostic shell would be fabricated. P00 validates fixed dimensions, button height, no bitmap stretching, resource ratio rules and device screenshots manually. Starting with the first implemented page with a matching Android baseline image, the visual diff tool must report at least 90.0 percent similarity and every hard-fail condition in the V1.3.0 visual threshold specification must pass.
