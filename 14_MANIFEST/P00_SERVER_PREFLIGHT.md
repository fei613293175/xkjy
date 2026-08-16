# P00 Server Preflight

Checked on `obx-test` on 2026-08-17 against repository commit `5ee44706f771280b21a4a1b4233b74c62f50c66a`. This is a preflight record, not a P00 completion report.

| Check | Result | Evidence |
| --- | --- | --- |
| Repository checkout | Pass | `/srv/xkjy` is clean at `5ee4470`. |
| Git LFS assets | Pass | Server installed Git LFS and checked out 614 LFS objects. |
| Hardened baseline validator | Pass | 132 Android PNG files and 132 matching HTML files; no forbidden paths found. |
| Docker engine and Compose | Pass | Docker `26.1.3`, Compose `v2.27.0`, overlay2 driver. |
| JDK 17 | Pass | `/usr/lib/jvm/java-17-openjdk-17.0.1.0.12-2.el8_5.x86_64`. |
| Android build image | Conditionally available | `hhy2-android-builder:latest` includes JDK 17, Gradle 8.10.2, and Android SDK environment variables. It has not yet been used to build this project. |
| Host Android SDK / Gradle / ADB | Not ready | `/opt/android-sdk` has no installed components; host `gradle` and `adb` are absent. The build image must be verified during P00. |
| PostgreSQL 16 image | Not ready | `postgres:16` is absent. |
| Redis 7 image | Not ready | `redis:7` is absent. |
| Server secret store | Blocked for private integrations | `/run/secrets` exists but is empty and mode `0755`; no project secrets were inspected or exposed. |

## Result

The sanitized repository baseline is valid and the server has adequate disk capacity. P00 may create the service and client shells, but it must not claim a build, database/Redis integration, payment/identity/storage/email/withdrawal integration, or real-device test pass until the listed missing prerequisites have been resolved and rechecked.

The next engineering action is to validate the existing Android build image and create the P00 repository skeleton on the server. Runtime secrets remain blocked until a restricted server-only secret store is provisioned.
