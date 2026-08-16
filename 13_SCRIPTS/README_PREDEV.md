# Pre-Development Script Policy

## Permitted baseline scripts

- `validate_hardened_package.py` checks the sanitized repository structure and boundaries.
- `render_ui_chromium_v130.py` and `validate_visual_v130.py` are V1.3.0 Android HTML baseline tools.

Run validation and rendering only on the connected server. They do not prove a Compose implementation or replace real-device acceptance.

## Non-authoritative generation scripts

The other historical `generate_*` and generic validation scripts are retained as source provenance. Several carry V1.1.0 defaults, so they must not overwrite this repository's release files, create a new visual gate, or be used as a P00 acceptance authority.
