# V1.3.0-PREDEV-HARDENED Repository Report

## Scope

This repository was created from the original `星矿纪元_V1.3.0_游戏视觉重建完整开发包.zip` on 2026-08-17. The original archive SHA-256 is:

```text
50ad0380d4d4104d67f4d66352401a67b5d39e99fc282666c4b25eaa770b3d1e
```

The original archive had 1,905 files. The initial whitelist import retained 1,756 files and excluded 149 files.

## Exclusions

| Category | Count | Reason |
| --- | ---: | --- |
| Rejected V1.2.0 archive | 124 | Not a development or visual fact source. |
| Legacy V1.2.0 contacts, references, and manifests | 17 | Prevents accidental reuse of rejected visuals. |
| Private configuration and certificate material | 7 | Must live only in server-side secret storage. |
| Nested private mother-template ZIP | 1 | Avoids duplicate distribution of private material. |
| Mother-template raw reference directory | 7 | GitHub push protection detected a Cloudflare token in a historical raw export; the full non-authoritative directory was removed. |

The old `FILE_MANIFEST.txt` and `SHA256SUMS.txt` were deliberately removed because their hashes reference excluded files and cannot validate this sanitized repository.

## Retained Facts

- 212 cross-platform Page IDs and 244 required page states.
- 132 V1.3.0 Android PNG baselines and 132 matching HTML sources.
- Android baseline: `360x760 dp`, rendered as `1080x2280 px`.
- 107 inherited admin states at `1440x900 px` and 5 H5 states at `780x1688 px`.
- 36 V1.3.0 miner SVG/PNG pairs, VFX, BGM, SFX, design tokens, API contracts, and core schema.

## Current Gate

The baseline is ready for P00 server preflight only. The V1.3.0 source visual validation remains evidence for the HTML baseline, not evidence that a native Android implementation exists or passes real-device acceptance.
