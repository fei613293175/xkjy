# V1.3.0 Pre-Development Hardening

## Purpose

This repository is a sanitized development baseline created from the original V1.3.0 delivery archive. It is the only repository fact source for P00 and later implementation work. The original archive remains an external audit source and must not be re-imported wholesale.

## What Was Retained

- V1.1.0 business rules, API contracts, database schema, and release plan.
- V1.3.0 Android visual baselines, HTML sources, CSS, design tokens, and game assets.
- Inherited admin, H5, audio, and mother-template rule documents without private values.
- Reference Compose tokens and components.

## What Was Excluded

- All rejected V1.2.0 visual archives, contact sheets, reference images, and manifests.
- Non-empty private integration configuration.
- Alipay private key and certificate files.
- The nested private mother-template ZIP.
- The mother-template `12_原始参考资料` directory because it contains historical raw exports rather than implementation rules.
- Source-package file manifests and hashes because they refer to excluded files and are no longer valid for this repository.

## Authoritative Versions

| Concern | Version or contract |
| --- | --- |
| Development baseline | `V1.3.0-PREDEV-HARDENED` |
| Business rules and data/API contracts | `V1.1.0` |
| Android visual baseline | `V1.3.0` |
| Private mother-template rules | `V1.4.2` |
| Android visual output | `1080x2280 px` from a `360x760 dp` baseline |
| H5 visual output | `780x1688 px` |
| Admin visual output | `1440x900 px` |

The old generic validation script has V1.1.0 defaults and is not an authority for Android V1.3.0 dimensions. Only the V1.3.0 visual scripts and the repository validation contract may gate Android baseline work.

## P00 Gate

P00 may start only after the connected server passes repository checkout, secret-presence, Docker/PostgreSQL/Redis, and Android signing preflight. No actual credential value is stored here. A failed server preflight blocks only the affected integration and must be recorded with redacted evidence.

P00 completion does not mean business features are complete. It is limited to repository structure, server infrastructure, service shells, Android shell, admin shell, migrations, health checks, logging, resource registration, and the visual-diff framework.
