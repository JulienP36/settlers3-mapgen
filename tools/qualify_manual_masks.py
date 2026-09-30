"""Qualify a drawable/imported mask over a deterministic test matrix."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def _load_grid(path: Path) -> np.ndarray:
    """Load one image with the same grayscale/resampling contract as the UI."""

    from PIL import Image

    from s3mapgen.generation.archetypes import MASK_LAYER_MANUAL_GRID_SIDE

    with Image.open(path) as image:
        resized = image.convert("L").resize(
            (MASK_LAYER_MANUAL_GRID_SIDE, MASK_LAYER_MANUAL_GRID_SIDE),
            Image.Resampling.LANCZOS,
        )
        return np.asarray(resized, dtype=np.uint8)


def main() -> int:
    from s3mapgen.generation.archetypes import (
        MANUAL_MASK_QUALIFICATION_MIRROR_MODES,
        MANUAL_MASK_QUALIFICATION_SEEDS,
        MANUAL_MASK_QUALIFICATION_SIZES,
        manual_mask_fixture_grid,
        manual_mask_profile,
        manual_mask_report,
    )

    parser = argparse.ArgumentParser(
        description="Qualify one deterministic manual mask over sizes, seeds and mirrors."
    )
    parser.add_argument(
        "--mask",
        type=Path,
        help="Image to import as grayscale; without it, use the deterministic fixture.",
    )
    parser.add_argument(
        "--side",
        type=int,
        action="append",
        dest="sizes",
        help="Map size to test; repeat for multiple sizes (default: 384, 512, 768).",
    )
    parser.add_argument(
        "--seed",
        type=int,
        action="append",
        dest="seeds",
        help="Seed to test; repeat for multiple seeds (default: 20260920, 20260921, 20260922).",
    )
    parser.add_argument(
        "--mirror",
        type=int,
        action="append",
        dest="mirrors",
        choices=(0, 1, 2, 3),
        help="Native mirror mode; repeat for multiple modes (default: 0, 1, 2, 3).",
    )
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    grid = _load_grid(args.mask) if args.mask is not None else manual_mask_fixture_grid()
    profile = manual_mask_profile(grid)
    report = manual_mask_report(
        profile,
        sizes=tuple(args.sizes or MANUAL_MASK_QUALIFICATION_SIZES),
        seeds=tuple(args.seeds or MANUAL_MASK_QUALIFICATION_SEEDS),
        mirror_modes=tuple(args.mirrors or MANUAL_MASK_QUALIFICATION_MIRROR_MODES),
    )
    report["run"]["mask_source"] = (
        str(args.mask) if args.mask is not None else "fixture:asymmetric_organic"
    )
    payload = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.output is None:
        print(payload, end="")
    else:
        args.output.write_text(payload, encoding="utf-8")
        print(json.dumps(report["summary"], ensure_ascii=False))
    return 0 if report["summary"]["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
