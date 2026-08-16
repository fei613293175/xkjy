#!/usr/bin/env python3
"""Compare normalized screenshots and enforce the repository visual threshold."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from PIL import Image, ImageChops, ImageStat

BASELINE_SIZE = (1080, 2280)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("baseline", type=Path)
    parser.add_argument("actual", type=Path)
    parser.add_argument("--threshold", type=float, default=90.0)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()

    with Image.open(args.baseline) as baseline, Image.open(args.actual) as actual:
        baseline_rgb = baseline.convert("RGB")
        actual_rgb = actual.convert("RGB")
        errors: list[str] = []
        if baseline_rgb.size != BASELINE_SIZE:
            errors.append(f"baseline_size={baseline_rgb.size}, expected={BASELINE_SIZE}")
        if actual_rgb.size != baseline_rgb.size:
            errors.append(f"actual_size={actual_rgb.size}, baseline_size={baseline_rgb.size}")
        if errors:
            result = {"status": "FAIL", "similarity_percent": None, "errors": errors}
        else:
            difference = ImageChops.difference(baseline_rgb, actual_rgb)
            normalized_error = sum(ImageStat.Stat(difference).mean) / (255.0 * 3.0)
            similarity = round((1.0 - normalized_error) * 100.0, 4)
            result = {"status": "PASS" if similarity >= args.threshold else "FAIL", "similarity_percent": similarity, "threshold_percent": args.threshold, "errors": []}
    output = json.dumps(result, ensure_ascii=False, indent=2)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(output + "\n", encoding="utf-8")
    print(output)
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
