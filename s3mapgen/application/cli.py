from __future__ import annotations
import argparse, json
from pathlib import Path

from .paths import LEGACY_PROFILE, UPGRADED_PROFILE, UPGRADED_REFERENCE, LIBRARY, EDM_SCAFFOLD, MAP_SCAFFOLD
from ..generation import MapGenerator
from ..generation.core import NATIVE_PLAYER_LIMITS, native_size_warning_kind
from ..map_data.binary import export_with_scaffold
from ..version import SOURCE_CANDIDATE_LABEL
from .rendering.preview import render


def main():
    ap = argparse.ArgumentParser(description='Settlers III MapGen Continental Legacy v2')
    ap.add_argument('--side', type=int, default=768, choices=tuple(NATIVE_PLAYER_LIMITS))
    ap.add_argument('--players', type=int, default=4)
    ap.add_argument('--seed', type=int, required=True)
    ap.add_argument('--mode', choices=['legacy','upgraded','custom'], default='legacy')
    ap.add_argument('--archetype', choices=['continental','large_islands','small_islands'], default='continental')
    ap.add_argument('--mirror-mode', type=int, choices=(0, 1, 2, 3), default=0, help='Miroir natif : 1 Axe long, 2 Axe court, 3 Les deux')
    ap.add_argument('--out', type=Path, default=Path('output'))
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)

    g = MapGenerator(LEGACY_PROFILE, LIBRARY, UPGRADED_PROFILE, UPGRADED_REFERENCE)
    res = g.generate(args.players, args.seed, mode=args.mode, archetype=args.archetype, side=args.side, mirror_mode=args.mirror_mode)
    hard = [v for v in res.validations if v.hard and not v.passed]
    print('\n'.join(v.label() for v in res.validations))
    if hard:
        print(
            f'WARNING: {len(hard)} validation(s) are not passing; '
            'generation and export remain enabled so the candidate can be tested.'
        )

    warning_kind = (
        native_size_warning_kind(args.side)
        if args.mode == 'legacy' and args.archetype == 'continental'
        else None
    )
    if warning_kind == 'small':
        print(
            f"WARNING: {args.side}×{args.side} est valide dans l'éditeur mais inférieur à 384×384; "
            f'génération native potentiellement peu viable (max {NATIVE_PLAYER_LIMITS[args.side]} joueurs).'
        )
    elif warning_kind == 'extended':
        print(
            f"WARNING: {args.side}×{args.side} est pris en charge par l'éditeur Settlers United "
            f"mais dépasse le maximum natif de 768×768; "
            f"viabilité en jeu non garantie (max {NATIVE_PLAYER_LIMITS[args.side]} joueurs)."
        )

    mirror_suffix = f'_mirror{args.mirror_mode}' if args.mirror_mode else ''
    base = f'S3_{args.archetype}_{args.mode}_{args.players}P_{args.side}x{args.side}_seed_{args.seed}{mirror_suffix}_MapGenV2_0_{SOURCE_CANDIDATE_LABEL}'
    # The 768 files are format scaffolds; the writer adapts their Area payload
    # to every supported native side so non-768 candidates can be tested.
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
