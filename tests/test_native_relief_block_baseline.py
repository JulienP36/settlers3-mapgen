"""Golden outputs that protect the native Legacy relief path during refactors."""

from __future__ import annotations

import hashlib

from s3mapgen.generation.generators.legacy.native_terrain import (
    generate_primary_terrain,
)


def _sha256(array) -> str:
    return hashlib.sha256(array.tobytes()).hexdigest()


def test_native_legacy_relief_blocks_keep_reference_outputs():
    # Captured from the validated pre-R67 implementation. These fixtures lock
    # not only the height field but also the downstream terrain and markers.
    references = (
        (
            256,
            297650040,
            (
                "2e7cee495f3779c65bf70adc7909141c6e5ce4fd83a421aa13bce4c2808b51c8",
                "50009176ea4c30494acf8ad11574272670f0e2aa96d5df15c2d7a6136b4ddff7",
                "de2f256064a0af797747c2b97505dc0b9f3df0de4f489eac731c23ae9ca9cc31",
                "e726d1236cf791c3d0b85ecca848ce617869572920d682c3864c3476d8986bfe",
            ),
        ),
        (
            384,
            20260921,
            (
                "7f3370322c1442f5a9eeea56dcc9668183cef3518b98f98cfc1a45f1e04849c9",
                "79b0dd8e00a41150bf467f14bd266d2ff4b2dd3596a058f65271df726acdc41c",
                "8123c216413f82bbaa0339c27a43d9822c2a043e20662b27c97874429b996e9a",
                "3926343972cf4bb3d41cc094c74d37af4aca66b04d3451c2876c05375c481294",
            ),
        ),
        (
            768,
            2026081544,
            (
                "6dbe87bd14807631ec7e1fac1b22aa436868a652cab1bb6f7dc13e6347258531",
                "e3983a3eb589a869d043fd8d6f8b9c85923af68a4533c4bc7011bc903357d5bc",
                "250480ecefa3655c774b6a4e5d4eb16675ee4f181c2285c25020fac6e3aaf3b5",
                "f7c4943405dffab36badc8ad9f8d48adf8dc49517df72ce8a7b7082da457ea1d",
            ),
        ),
    )
    for side, seed, expected in references:
        result = generate_primary_terrain(side, seed)
        actual = tuple(
            _sha256(getattr(result, field))
            for field in ("height", "terrain", "variant", "marker")
        )
        assert actual == expected, (side, seed)
