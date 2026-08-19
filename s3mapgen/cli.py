from __future__ import annotations
import argparse, json
from pathlib import Path

from .app_paths import LEGACY_PROFILE, UPGRADED_PROFILE, UPGRADED_REFERENCE, LIBRARY, EDM_SCAFFOLD, MAP_SCAFFOLD
from .generator import MapGenerator
from .binary import export_with_scaffold
from .preview import render


def main():
    ap = argparse.ArgumentParser(description='Settlers III MapGen v1.5')
    ap.add_argument('--players', type=int, default=4)
    ap.add_argument('--seed', type=int, required=True)
    ap.add_argument('--mode', choices=['legacy','upgraded','custom'], default='legacy')
    ap.add_argument('--archetype', choices=['continental','large_islands','small_islands'], default='continental')
    ap.add_argument('--out', type=Path, default=Path('output'))
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)

    g = MapGenerator(LEGACY_PROFILE, LIBRARY, UPGRADED_PROFILE, UPGRADED_REFERENCE)
    res = g.generate(args.players, args.seed, mode=args.mode, archetype=args.archetype)
    hard = [v for v in res.validations if v.hard and not v.passed]
    print('\n'.join(v.label() for v in res.validations))
    if hard:
        raise SystemExit(f'Export refused: {len(hard)} hard validation failure(s)')

    base = f'S3_{args.archetype}_{args.mode}_{args.players}P_768x768_seed_{args.seed}_MapGenV1_5'
    export_with_scaffold(res.state, EDM_SCAFFOLD, args.out / (base + '.edm'))
    export_with_scaffold(res.state, MAP_SCAFFOLD, args.out / ('1-' + base + '.map'))
    render(res.state, args.out / (base + '_preview.png'))
    (args.out / (base + '_report.json')).write_text(
        json.dumps({
            'metadata': res.state.metadata,
            'pipeline': res.stage_log,
            'validations': [v.__dict__ for v in res.validations],
        }, indent=2),
        encoding='utf-8',
    )
    print('Exported to', args.out)
