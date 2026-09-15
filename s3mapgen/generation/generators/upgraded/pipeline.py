"""Independent Upgraded generator.

The selected archetype supplies the neutral map context.  From that point on
this module owns a complete copy of the native terrain sequence and applies
the Upgraded content pass; it never dispatches through ``generators.legacy``.
"""

from __future__ import annotations

from collections.abc import Callable
from copy import deepcopy
import random
from pathlib import Path

import numpy as np

from ...archetypes import get_archetype
from ...archetypes.continental import ContinentalV1, assemble_continental_state
from ...contracts import GenerationOutput
from ...core.request import GenerationRequest
from ...core.seed_streams import SeedStreams
from .content import UpgradedContent
from .native_terrain import generate_primary_terrain, resume_deferred_terrain
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
    profile: dict | None = None,
) -> tuple[object, list]:
    """Generate an Upgraded map from the independent copied pipeline.

    ``profile`` is the in-memory entry point used by DEV6 Custom.  The normal
    Upgraded call loads the active code-owned profile defaults.
    """

    arch_spec = get_archetype(archetype)
    if not arch_spec.implemented:
        raise NotImplementedError(f"L'archétype {arch_spec.label} n'est pas implémenté")
    if arch_spec.key != "continental":
        raise NotImplementedError("Le pipeline Upgraded natif ne porte pour l'instant que Continental")
    ContinentalV1().prepare(request.side, request.players)
    if int(mirror_mode) not in (0, 1, 2, 3):
        raise ValueError("Le mode miroir doit être compris entre 0 et 3")

    profile = (
        deepcopy(profile)
        if profile is not None
        else load_profile(profile_path) if profile_path is not None else load_profile()
    )
    custom_runtime = profile.get("_custom_runtime", {})
    is_custom = (
        isinstance(custom_runtime, dict)
        and bool(custom_runtime)
        and custom_runtime.get("execution_kind", "custom") != "preset"
    )
    if is_custom and custom_runtime.get("base_mode") not in (None, "upgraded"):
        raise ValueError("Un profil Custom Upgraded doit conserver Upgraded comme moteur de base")
    mode_label = "Custom" if is_custom else "Upgraded"
    mode_key = "custom" if is_custom else "upgraded"
    generator_name = "continental_custom_upgraded" if is_custom else "continental_upgraded_native"
    engine_revision = (
        f"continental_custom_upgraded-v1:{custom_runtime.get('configuration_digest', '')}"
        if is_custom else "continental_upgraded-native-v1"
    )

    custom_sections = (
        custom_runtime.get("sections")
        if isinstance(custom_runtime, dict)
        and isinstance(custom_runtime.get("sections"), dict)
        and custom_runtime.get("sections")
        else None
    )
    active_start_packages = (
        tuple(str(value) for value in custom_runtime.get("start_packages", ()))
        if is_custom and isinstance(custom_runtime.get("start_packages", ()), (list, tuple))
        else ()
    )
    priority_bonus_route = bool(active_start_packages)

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
            surface_rates=custom_sections,
            defer_non_archetype=priority_bonus_route,
        ),
    )

    state = assemble_continental_state(
        request.side,
        result.height,
        result.terrain,
        metadata={
            "seed": int(request.seed),
            "players": int(request.players),
            "mode": mode_label,
            "mode_key": mode_key,
            "archetype": arch_spec.label,
            "archetype_key": arch_spec.key,
            "profile": profile["profile_name"],
            "generator": generator_name,
            "engine_revision": engine_revision,
            "upgraded_base_pipeline": "independent_copy_of_continental_legacy_native",
            "upgraded_mud_generation": bool(
                isinstance(custom_sections, dict)
                and isinstance(custom_sections.get("terrains"), dict)
                and bool(custom_sections["terrains"].get("mud", {}).get("enabled", False))
                and float(custom_sections["terrains"].get("mud", {}).get("rate_percent", 0.0)) > 0.0
            ),
            "upgraded_start_content_deferred": False,
            "start_bonus_priority_route": priority_bonus_route,
            "active_start_packages": list(active_start_packages),
            "upgraded_start_bonus_rules": profile.get("start_bonus", {}),
            "upgraded_start_bonus_controls": (
                custom_sections.get("start_bonus", {})
                if isinstance(custom_sections, dict)
                else {}
            ),
            "custom_base_mode": custom_runtime.get("base_mode") if is_custom else None,
            "custom_configuration_digest": custom_runtime.get("configuration_digest") if is_custom else None,
            "custom_start_packages": custom_runtime.get("start_packages", []) if is_custom else None,
            "generator_route": (
                "custom_preset"
                if isinstance(custom_runtime, dict)
                and custom_runtime.get("execution_kind") == "preset"
                else "custom"
                if is_custom
                else "native"
            ),
            **result.metadata,
        },
    )

    # Start placement remains an isolated provisional bridge.  Dev 5 now
    # consumes those coordinates for content bonuses without recalculating
    # or otherwise changing the positions themselves.
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
    if priority_bonus_route:
        terrain_bonus_meta = content.begin_prioritized_terrain_bonuses(state, pr)
        resumed = resume_deferred_terrain(
            result,
            height=state.height,
            terrain=state.terrain,
            objects=state.objects,
            resources=state.resources,
            protected_mask=terrain_bonus_meta["protected_mask"],
            progress=(lambda name: progress(f"continental_upgraded.native.{name}", "") if progress else None),
        )
        state.height[:] = resumed.height
        state.terrain[:] = resumed.terrain
        state.objects[:] = resumed.objects
        state.resources[:] = resumed.resources
        state.metadata.update(resumed.metadata)
        state.metadata["upgraded_start_bonus_terrain_before_global"] = True
        content_meta = content.generate_prioritized(state, rng, pr)
    else:
        content_meta = content.generate(state, rng, pr)
    state.metadata.update(content_meta)

    if is_custom:
        state.metadata["custom_profile_applied"] = True
        applied_sections = {
            "fish",
            "rivers",
            "minerals",
            "trees",
            "building_stones",
            "decorations",
            "objects",
            "terrains",
            "decor",
            "starts",
            "start_bonus",
        }
        state.metadata["custom_profile_diagnostics"] = {
            "base_mode": custom_runtime.get("base_mode", "upgraded"),
            "base_archetype": custom_runtime.get("base_archetype", archetype),
            "configuration_digest": custom_runtime.get("configuration_digest"),
            "active_start_packages": list(custom_runtime.get("start_packages", [])),
            "custom_controls": custom_runtime.get("sections", {}),
            "effective_start_bonus_controls": (
                custom_runtime.get("sections", {}).get("start_bonus", {})
                if isinstance(custom_runtime.get("sections", {}), dict)
                else {}
            ),
            "profile_sections": sorted(
                key for key in profile
                if not str(key).startswith("_")
            ),
            "applied_sections": sorted(
                key for key in profile
                if not str(key).startswith("_") and key in applied_sections
            ),
            "unapplied_sections": sorted(
                key for key in profile
                if not str(key).startswith("_") and key not in applied_sections
            ),
            "application_status": "partial",
            "note": "Les sections Terrains/Minerais/Poissons/Rivières/Arbres/Pierres/Décorations/Objets et les cinq bonus de départ sont raccordés ; les lacs natifs, la neige et les paramètres structurels restent ceux du cœur Upgraded.",
        }

    validations = validate(state, profile)
    state.metadata["pipeline"] = (
        [
            "archetype.macro_layout",
            "upgraded.native_terrain_archetype",
            "upgraded.starts_bridge",
            "biomes.upgraded_start_mini_swamps",
            "resources.upgraded_start_rocky_minerals",
            "hydrology.upgraded_start_lake_fish_river",
            "upgraded.native_terrain_non_archetype",
            "resources.upgraded_minerals_v7",
            "resources.upgraded_start_rocky_minerals_fill",
            "resources.upgraded_fish",
            "resources.upgraded_start_lake_fish",
            "objects.upgraded_start_building_stones",
            "objects.upgraded_trees_with_start_forest_first",
            "objects.upgraded_decorations",
            "objects.upgraded_building_stones_global",
            "accessibility.upgraded_finalize",
            "validators.upgraded",
        ]
        if priority_bonus_route
        else [
            "archetype.macro_layout",
            "upgraded.native_terrain_copy",
            "upgraded.starts_bridge",
            "biomes.upgraded_start_mini_swamps",
            "resources.upgraded_start_rocky_minerals",
            "hydrology.upgraded_start_lake_fish_river",
            "resources.upgraded_minerals_v7",
            "resources.upgraded_start_rocky_minerals_fill",
            "resources.upgraded_fish",
            "resources.upgraded_start_lake_fish",
            "objects.upgraded_decorations",
            "objects.upgraded_trees",
            "objects.upgraded_building_stones",
            "accessibility.upgraded_finalize",
            "validators.upgraded",
        ]
    )
    state.metadata["upgraded_provenance"] = {
        "terrain": "independent copy of Legacy native terrain sequence",
        "minerals": "retained calibrated v7 no-gap routine",
        "fish": "direct uniform coastal-band routine shared with Custom",
        "objects": "Legacy static families plus upgraded reefs, start forests and stone clusters",
        "mud": "native parameter 0; configurable in Custom",
        "starts": "provisional bridge coordinates retained; five start bonuses restored with separate reservations",
    }
    return state, validations


__all__ = ("generate",)
