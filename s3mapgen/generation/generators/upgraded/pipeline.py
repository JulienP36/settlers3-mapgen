"""Independent Upgraded generator.

The selected archetype supplies the neutral map context.  From that point on
this module owns a complete copy of the native terrain sequence and applies
the Upgraded content pass; it never dispatches through ``generators.legacy``.
"""

from __future__ import annotations

from collections.abc import Callable
import random
from pathlib import Path

import numpy as np

from ...archetypes import get_archetype
from ...archetypes.continental import ContinentalV1, assemble_continental_state
from ...contracts import GenerationOutput
from ...core.request import GenerationRequest
from ...core.seed_streams import SeedStreams
from .content import UpgradedContent
from .native_terrain import generate_primary_terrain
from .starts import place_starts
from .profile import load_profile
from .validators import validate


Progress = Callable[[str, str], None] | None


def _stage(progress: Progress, log: list[str], name: str, detail: str, fn):
    log.append(name + (f" — {detail}" if detail else ""))
    if progress is not None:
        progress(name, detail)
    return fn()


def generate(
    request: GenerationRequest,
    progress: Progress = None,
    *,
    mirror_mode: int = 0,
    archetype: str = "continental",
    profile_path: Path | str | None = None,
) -> tuple[object, list]:
    """Generate an Upgraded map from the independent copied pipeline."""

    arch_spec = get_archetype(archetype)
    if not arch_spec.implemented:
        raise NotImplementedError(f"L'archétype {arch_spec.label} n'est pas implémenté")
    if arch_spec.key != "continental":
        raise NotImplementedError("Le pipeline Upgraded natif ne porte pour l'instant que Continental")
    ContinentalV1().prepare(request.side, request.players)
    if int(mirror_mode) not in (0, 1, 2, 3):
        raise ValueError("Le mode miroir doit être compris entre 0 et 3")

    profile = load_profile(profile_path) if profile_path is not None else load_profile()

    events: list[str] = []
    result = _stage(
        progress,
        events,
        "continental_upgraded.native_terrain",
        "copie indépendante du relief, des surfaces et des rivières",
        lambda: generate_primary_terrain(
            request.side,
            request.seed,
            mirror_mode,
            progress=(lambda name: progress(f"continental_upgraded.native.{name}", "") if progress else None),
        ),
    )

    state = assemble_continental_state(
        request.side,
        result.height,
        result.terrain,
        metadata={
            "seed": int(request.seed),
            "players": int(request.players),
            "mode": "Upgraded",
            "mode_key": "upgraded",
            "archetype": arch_spec.label,
            "archetype_key": arch_spec.key,
            "profile": profile["profile_name"],
            "generator": "continental_upgraded_native",
            "engine_revision": "continental_upgraded-native-v1",
            "upgraded_base_pipeline": "independent_copy_of_continental_legacy_native",
            "upgraded_mud_generation": False,
            "upgraded_start_content_deferred": True,
            "upgraded_start_bonus_rules": profile.get("start_bonus", {}),
            **result.metadata,
        },
    )

    # Start placement is intentionally an isolated provisional bridge.  It is
    # not allowed to become an implicit source of start resources or settlers.
    _stage(
        progress,
        events,
        "continental_upgraded.starts_bridge",
        "positionnement provisoire, à recalibrer séparément",
        lambda: place_starts(
            state,
            request.players,
            SeedStreams(request.seed).rng("upgraded_starts_bridge"),
            technical_clear=max(12, request.side // 52),
        ),
    )
    state.metadata.update(
        starts_status="provisional_bridge_not_upgraded_native",
        starts_placed_early=False,
        starts_placed_provisionally=True,
        start_placement_deferred=True,
    )

    content = UpgradedContent(
        profile,
        progress=lambda name, detail: _stage(progress, events, f"continental_upgraded.{name}", detail, lambda: None),
    )
    rng = np.random.default_rng(int(request.seed))
    pr = random.Random(int(request.seed))
    content_meta = content.generate(state, rng, pr)
    state.metadata.update(content_meta)

    validations = validate(state, profile)
    state.metadata["pipeline"] = [
        "archetype.macro_layout",
        "upgraded.native_terrain_copy",
        "upgraded.starts_bridge",
        "resources.upgraded_minerals_v7",
        "resources.upgraded_fish",
        "objects.upgraded_decorations",
        "objects.upgraded_trees",
        "objects.upgraded_building_stones",
        "accessibility.upgraded_finalize",
        "validators.upgraded",
    ]
    state.metadata["upgraded_provenance"] = {
        "terrain": "independent copy of Legacy native terrain sequence",
        "minerals": "retained calibrated v7 no-gap routine",
        "fish": "retained upgraded shore-band routine",
        "objects": "retained upgraded trees/decorations/building-stones routines",
        "mud": "disabled",
        "starts": "provisional bridge; separate future pass",
    }
    return state, validations


__all__ = ("generate",)
