"""Qualify the provisional R51 Continental profile and player-start gate."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def main() -> int:
    from s3mapgen.generation.archetypes import (
        CONTINENTAL_CALIBRATION_MIRROR_MODES,
        CONTINENTAL_CALIBRATION_SEEDS,
        CONTINENTAL_CALIBRATION_SIZES,
        continental_calibration_report,
    )

    parser = argparse.ArgumentParser(
        description="Qualify the provisional R51 Continental profile and its starts."
    )
    parser.add_argument(
        "--mode",
        choices=("legacy", "upgraded"),
        default="legacy",
        help="Custom base engine for the player-start gate (default: legacy).",
    )
    parser.add_argument(
        "--side",
        type=int,
        action="append",
        dest="sizes",
        help="Native map size; repeat for multiple sizes (default: 384, 512, 768).",
    )
    parser.add_argument(
        "--seed",
        type=int,
        action="append",
        dest="seeds",
        help="Seed; repeat for multiple seeds (default: 20260920, 20260921, 20260922).",
    )
    parser.add_argument(
        "--mirror",
        type=int,
        action="append",
        dest="mirrors",
        choices=(0, 1, 2, 3),
        help="Native mirror mode; repeat for multiple modes (default: 0, 3).",
    )
    parser.add_argument(
        "--players",
        type=int,
        action="append",
        help="Player count; repeat to override the per-size default cases.",
    )
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    report = continental_calibration_report(
        base_mode=args.mode,
        sizes=tuple(args.sizes or CONTINENTAL_CALIBRATION_SIZES),
        seeds=tuple(args.seeds or CONTINENTAL_CALIBRATION_SEEDS),
        mirror_modes=tuple(args.mirrors or CONTINENTAL_CALIBRATION_MIRROR_MODES),
        players=tuple(args.players) if args.players else None,
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
