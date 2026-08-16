# P00 Acceptance Record

This document is completed only from server and real-device evidence. It does not claim later-release features exist.

## Scope

- Repository, Docker Compose, PostgreSQL, Redis, Go API, Vue admin shell, Compose Android shell.
- Resource registry, V1.3.0 token application, migration ledger, OpenAPI, health checks, structured logs and visual-diff tooling.
- Excluded: account, game board, projects, mall, payment, wallet, identity and withdrawal workflows.

## Evidence Required Before P00 Completion

| Item | Evidence | Status |
| --- | --- | --- |
| Hardened repository validator | `python3 13_SCRIPTS/validate_hardened_package.py` on `obx-test`: PASS, 132 Android PNG and 132 HTML sources | Pass |
| Go unit tests | `golang:1.24` server container: `go test ./...` passed (`config`, `migrate`, API and command packages) | Pass |
| Vue type check and production build | `node:22-alpine` server container: `npm ci`, `npm run check`, `npm run build`; audit reports 0 vulnerabilities after Vite 6.4.3 update | Pass |
| Docker service health | PostgreSQL, Redis, backend and admin containers healthy; `/healthz`, `/api/healthz`, `/api/readyz`, `/api/v1/baseline` returned expected P00 responses; migration ledger checksum verified | Pass |
| Release APK | Server Android builder completed `:app:testDebugUnitTest :app:assembleRelease`; signed APK verified with `apksigner` | Pass |
| Android real-device acceptance | vivo X21 (`bf09c6f7`, Android 9, 1080x2280) installed, launched, scrolled, accepted input, dismissed keyboard, ran self-check, returned to launcher; logcat had no fatal, ANR or app exception match | Pass |
| Visual acceptance | Manual P00 diagnostic-shell review on the 1080x2280 baseline device: text, icons, paths, spacing, button and scroll states showed no clipping, stretching, overlap or broken alignment | Pass, manual only |

## Visual Gate Boundary

P00 has no dedicated V1.3.0 native page baseline. The supplied 132 images correspond to later page IDs, so a numeric similarity result for the P00 diagnostic shell would be fabricated. P00 validates fixed dimensions, button height, no bitmap stretching, resource ratio rules and device screenshots manually. Starting with the first implemented page with a matching Android baseline image, the visual diff tool must report at least 90.0 percent similarity and every hard-fail condition in the V1.3.0 visual threshold specification must pass.

## Completion Evidence

- Android source commit: `9b3016bc5c97cf07258f80bcb5608444a780eb18`. The server Gradle run completed successfully in 8m 4s.
- APK: `/srv/xkjy-delivery/p00/xkjy-p00-0.0.1-release.apk`, package `cc.orbexa.xkjy`, version `0.0.1-p00` (code `1`), SHA-256 `d70975d315d3513bfd88284039b9e35a6573dd0e8216950a2c0e95fa0ae43f64`.
- Signing: APK Signature Scheme v2 verified; the release certificate is a generated server-only RSA-4096 key. No signing secret is stored in Git.
- Migration ledger: version `1`, `0001_xkjy_core_schema.sql`, SHA-256 `7876dbf0d3074b01be64b27e8b475282f5114bdfce9a98115d2d55d26a63a026`.
- Server evidence directory: `/srv/xkjy-delivery/p00/`. It contains the final APK, build/test outputs, device screenshots, logcat and this release's test record.

## Real-Device Path

1. Confirmed all attached devices were in strict `device` state and reserved `bf09c6f7`, the 1080x2280 vivo X21 baseline device.
2. Installed the signed APK, confirmed `versionName=0.0.1-p00`, and launched `cc.orbexa.xkjy/.MainActivity` successfully (`TotalTime: 746ms`).
3. Captured the initial resource screen, scrolled the complete registered-resource list, entered `P00-acceptance`, dismissed the keyboard, ran the base self-check, and confirmed the status copy updated.
4. Returned from the root activity, then explicitly returned the device to Launcher and released it. The captured logcat contains no `FATAL EXCEPTION`, `AndroidRuntime`, `ANR in`, or application exception match.

The diagnostic shell has no corresponding official Page ID image, so it has no fabricated numeric visual score. The 90.0 percent visual-diff gate remains mandatory for every future implementation with a matching baseline. P00 is complete only as the scoped engineering baseline; P01 and all account, game, payment, wallet, identity and withdrawal work remain unstarted.
