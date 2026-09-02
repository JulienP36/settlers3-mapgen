"""Continental Legacy pipeline backed by the recovered native terrain core."""

from __future__ import annotations

from collections.abc import Callable

import numpy as np

from ...core.request import GenerationRequest
from ...core.seed_streams import SeedStreams
from ....map_data.constants import SNOW, SNOW_TRANS, WATER_IDS
from ....map_data.hexgrid import neighbor_count
from ...archetypes.continental import assemble_continental_state
from .native_terrain import generate_primary_terrain
from .native_validators import validate
from .objects import finalize_accessibility
from .profile import load_profile
from .starts import place_starts


Progress = Callable[[str, str], None] | None


def generate(
    request: GenerationRequest,
    progress: Progress = None,
    *,
    mirror_mode: int = 0,
) -> tuple[object, list]:
    """Generate one Continental Legacy map with native-calibrated content.

    The recovered executable owns the terrain morphology and the global
    object/resource pass.  Only player-start objects/resources, settlers and
    SAV records stay deferred; the native global content is copied directly
    into the MAP/EDM six-channel state.
    """

    def stage(key: str, detail: str, fn):
        if progress:
            progress(key, detail)
        return fn()

    result = stage(
        "continental_legacy.native_terrain",
        "relief, surfaces, rivières et transitions natives",
        lambda: generate_primary_terrain(
            request.side,
            request.seed,
            mirror_mode,
            progress=lambda name: progress(f"continental_legacy.native.{name}", "") if progress else None,
        ),
    )
    profile = load_profile()
    state = assemble_continental_state(
        request.side,
        result.height,
        result.terrain,
        metadata={
            "seed": int(request.seed),
            "players": int(request.players),
            "mode": "Legacy",
            "mode_key": "legacy",
            "archetype": "Continental",
            "archetype_key": "continental",
            "profile": profile["profile_name"],
            "generator": "continental_legacy_native_content",
            "engine_revision": "continental_legacy_native-legacy-v1",
            "runtime_native_inputs": 0,
            "native_deferred_layers": (
                "starts_native", "settlers", "sav_writer"
            ),
            **result.metadata,
        },
    )
    if result.objects is None or result.resources is None:
        raise RuntimeError("Le cœur natif n'a pas renvoyé ses couches de contenu")
    state.objects[:] = result.objects
    state.resources[:] = result.resources

    # The current export format still expects a PlayerInfo coordinate list.
    # Keep the old deterministic bridge isolated after terrain generation; it
    # cannot influence the native field and is explicitly marked provisional.
    reservation = stage(
        "continental_legacy.starts_bridge",
        "coordonnées provisoires pour le scaffold MAP/EDM",
        lambda: place_starts(
            state,
            request.players,
            SeedStreams(request.seed).rng("starts_bridge"),
            technical_clear=max(12, request.side // 52),
        ),
    )
    state.metadata.update(
        starts_status="provisional_bridge_not_native",
        starts_placed_early=True,
        start_placement_deferred=False,
    )

    water = np.isin(state.terrain, WATER_IDS)
    state.height[water] = 0
    state.accessibility[water] = 1
    snow = np.isin(state.terrain, (SNOW_TRANS, SNOW))
    state.accessibility[snow] = 1
    state.metadata["native_variant_field_checksum"] = int(result.variant.astype(np.uint64).sum())
    state.metadata["native_auxiliary_fields_deferred"] = False
    state.metadata["native_river_water_facing_cells"] = int(
        np.count_nonzero((state.terrain >= 0x60) & (state.terrain <= 0x63) & (neighbor_count(water) > 0))
    )
    native_content = result.metadata.get("native_content", {})
    if not isinstance(native_content, dict):
        native_content = {}
    for layer, detail in (
        ("minerals", "gisements de montagne"),
        ("fish", "poissons sur eaux hors rivières"),
        ("trees", "arbres et palmiers"),
        ("stones", "pierres de construction"),
        ("decorations", "objets statiques et décorations"),
    ):
        # Keep the established UI/progress contract while the actual native
        # work has already run in the shared executable PRNG pass.
        state.metadata.update(stage(
            f"continental_legacy.{layer}",
            detail,
            lambda layer=layer: native_content.get(layer, {}),
        ))
    state.metadata.update(stage(
        "continental_legacy.accessibility",
        "accessibilité finale",
        lambda: finalize_accessibility(state),
    ))
    validations = stage(
        "continental_legacy.native_validate",
        "terrain, ressources et objets",
        lambda: validate(state, mode=mirror_mode),
    )
    state.metadata["native_content_provenance"] = {
        "minerals": "routines globales récupérées de S3.EXE (0x51AD40), sans ressources de départ",
        "fish": "boucle globale récupérée de S3.EXE, sans ressources de départ",
        "objects": "appels statiques/rangés récupérés de S3.EXE (0x51B010/0x51B1A0)",
        "decorations": "objets statiques globaux récupérés de S3.EXE, hors objets de départ SAV",
    }
    return state, validations


__all__ = ("generate",)
