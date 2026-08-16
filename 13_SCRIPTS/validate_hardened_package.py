#!/usr/bin/env python3
"""Validate the sanitized V1.3.0 repository before P00 server work."""
from __future__ import annotations

import argparse
import json
import struct
import sys
from pathlib import Path


EXPECTED_FILES = (
    "README.md",
    "SECURITY.md",
    "00_README/PREDEV_HARDENING.md",
    "03_SPECS/PREDEV_BASELINE.yaml",
    "03_SPECS/SECURITY_BOUNDARY.yaml",
    "03_SPECS/CURRENT_RELEASE.yaml",
    "03_SPECS/PAGE_INDEX.yaml",
    "03_SPECS/DESIGN_TOKENS_GAME_V130.json",
    "04_UI/APP/APP-GAME-002__DEFAULT.png",
    "10_HTML/APP/APP-GAME-002__DEFAULT.html",
    "10_HTML/shared/styles_v130.css",
    "13_SCRIPTS/validate_visual_v130.py",
)

FORBIDDEN_PATH_PARTS = (
    "99_ARCHIVE",
    "CONTACTS_V120",
    "V120_REFERENCE",
    "PRIVATE_CREDENTIALS",
)

FORBIDDEN_SUFFIXES = {".pem", ".key", ".p12", ".pfx", ".zip"}
FORBIDDEN_FILENAMES = {"private_integrations.env", "private_integrations.yaml"}


def png_size(path: Path) -> tuple[int, int]:
    with path.open("rb") as handle:
        header = handle.read(24)
    if header[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError("not a PNG file")
    return struct.unpack(">II", header[16:24])


def is_forbidden(path: Path) -> str | None:
    lower_parts = {part.lower() for part in path.parts}
    if any(part.lower() in lower_parts for part in FORBIDDEN_PATH_PARTS):
        return "legacy_or_private_directory"
    if path.suffix.lower() in FORBIDDEN_SUFFIXES:
        return "forbidden_suffix"
    if path.name.lower() in FORBIDDEN_FILENAMES:
        return "forbidden_filename"
    if "v120" in path.as_posix().lower():
        return "legacy_v120_path"
    return None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", nargs="?", default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    root = Path(args.root).resolve()
    errors: list[str] = []

    for relative in EXPECTED_FILES:
        if not (root / relative).is_file():
            errors.append(f"missing required file: {relative}")

    for path in root.rglob("*"):
        if not path.is_file() or ".git" in path.parts:
            continue
        reason = is_forbidden(path.relative_to(root))
        if reason:
            errors.append(f"{reason}: {path.relative_to(root)}")

    app_pngs = sorted((root / "04_UI/APP").glob("*.png"))
    app_html = sorted((root / "10_HTML/APP").glob("*.html"))
    if len(app_pngs) != 132:
        errors.append(f"Android PNG count is {len(app_pngs)}, expected 132")
    if len(app_html) != 132:
        errors.append(f"Android HTML count is {len(app_html)}, expected 132")

    for path in app_pngs:
        try:
            size = png_size(path)
        except ValueError as exc:
            errors.append(f"invalid PNG {path.relative_to(root)}: {exc}")
            continue
        if size != (1080, 2280):
            errors.append(f"wrong Android PNG size {path.relative_to(root)}: {size}")

    baseline = root / "03_SPECS/PREDEV_BASELINE.yaml"
    if baseline.is_file() and "READY_FOR_P00_SERVER_PREFLIGHT" not in baseline.read_text(encoding="utf-8"):
        errors.append("pre-development baseline status is not ready for server preflight")

    summary = {
        "root": root.name,
        "status": "PASS" if not errors else "FAIL",
        "app_png_count": len(app_pngs),
        "app_html_count": len(app_html),
        "errors": errors,
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
