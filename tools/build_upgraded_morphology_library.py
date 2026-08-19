from __future__ import annotations
import argparse
from pathlib import Path

from s3mapgen.morphology import UpgradedMorphologyLibrary


def main():
    ap = argparse.ArgumentParser(
        description='Extract compact terrain+height morphology from an Upgraded reference EDM.'
    )
    ap.add_argument('source', type=Path)
    ap.add_argument('output', type=Path)
    args = ap.parse_args()
    lib = UpgradedMorphologyLibrary(args.source)
    lib.save_npz(args.output)
    print(f'Wrote {args.output} ({len(lib.terrain)} template(s), side={lib.side})')


if __name__ == '__main__':
    main()
