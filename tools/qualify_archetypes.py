"""Run the deterministic first-pass archetype/provider qualification."""

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
        QUALIFICATION_REPRESENTATIVE_SIZES,
        RELIEF_SOURCE_OPTIONS,
        qualification_report,
    )

    parser = argparse.ArgumentParser(
        description="Qualify deterministic macro previews for relief providers."
    )
    parser.add_argument("--seed", type=int, default=20260920)
    parser.add_argument("--mirror", type=int, default=0, choices=(0, 1, 2, 3))
    parser.add_argument(
        "--side",
        type=int,
        action="append",
        dest="sides",
        help="Map size to test; repeat for multiple sizes (default: 384, 512, 768).",
    )
    parser.add_argument(
        "--source",
        action="append",
        dest="sources",
        choices=RELIEF_SOURCE_OPTIONS,
        help="Relief source to test; repeat for multiple sources (default: all).",
    )
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    sizes = tuple(args.sides or QUALIFICATION_REPRESENTATIVE_SIZES)
    sources = tuple(args.sources or RELIEF_SOURCE_OPTIONS)
    report = qualification_report(
        sizes=sizes,
        seed=args.seed,
        mirror_mode=args.mirror,
        sources=sources,
    )
    payload = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.output is None:
        print(payload, end="")
    else:
        args.output.write_text(payload, encoding="utf-8")
        print(json.dumps(report["summary"], ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
