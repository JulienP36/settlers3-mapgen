"""Executable, staged Continental Legacy v2 generator pipeline."""

from __future__ import annotations

from collections.abc import Callable

from ...core.request import GenerationRequest
from ...core.seed_streams import SeedStreams
from ....map_data.model import MapState
from .lakes import add_lakes
from .macro import create_macro_topology
from .coast import refine_coastal_bands
from .objects import add_building_stones, add_decorations, add_trees, finalize_accessibility
from .profile import load_profile
from .relief import add_relief, add_snow
from .resources import add_fish, add_minerals
from .rivers import add_rivers
from .starts import place_starts
from .terrain import add_mountains, add_other_terrains, add_swamps
from .validators import validate


Progress = Callable[[str, str], None] | None


def generate(request: GenerationRequest, progress: Progress = None) -> tuple[MapState, list]:
    """Generate one entirely procedural Continental Legacy map.

    Inputs are restricted to side, players and seed.  All calibration values
    come from the small JSON profile; no SAV, NPZ, image or prior generated
    map is ever read during this execution.
    """

    profile = load_profile()
    streams = SeedStreams(request.seed)

    def stage(key: str, detail: str, fn):
        if progress:
            progress(key, detail)
        return fn()

    terrain, macro_meta = stage(
        "continental_v2.macro", "continent et océan procéduraux",
        lambda: create_macro_topology(
            request.side, profile, streams.rng("macro"), players=request.players
        ),
    )
    state = MapState.empty(request.side)
    state.terrain[:] = terrain
    state.metadata.update(macro_meta)
    state.metadata.update(
        seed=int(request.seed), players=int(request.players), mode="Héritage (Legacy)", mode_key="legacy",
        archetype="Continental", archetype_key="continental", profile=profile["profile_name"],
        generator="continental_legacy_v2", runtime_native_inputs=0,
    )
    reservation = stage(
        "continental_v2.starts", "positions joueurs et zones techniques",
        lambda: place_starts(state, request.players, streams.rng("starts"), technical_clear=max(12, request.side // 52)),
    )
    state.metadata.update(stage(
        "continental_v2.mountains", "massifs et transitions rocheuses",
        lambda: add_mountains(state, profile, reservation, streams.rng("mountains")),
    ))
    state.metadata.update(stage(
        "continental_v2.relief", "relief côtier et massifs",
        lambda: add_relief(state, profile, streams.rng("relief")),
    ))
    state.metadata.update(stage(
        "continental_v2.snow", "sommets enneigés",
        lambda: add_snow(state, profile, streams.rng("snow")),
    ))
    state.metadata.update(stage(
        "continental_v2.lakes", "lacs internes et berges",
        lambda: add_lakes(state, profile, reservation, streams.rng("lakes")),
    ))
    state.metadata.update(stage(
        "continental_v2.coastal_bands", "bathymétrie côtière sous garde-fous",
        lambda: refine_coastal_bands(state, profile, streams.rng("coastal_bands")),
    ))
    state.metadata.update(stage(
        "continental_v2.rivers", "rivières reliées à l’eau",
        lambda: add_rivers(state, profile, reservation, streams.rng("rivers")),
    ))
    state.metadata.update(stage(
        "continental_v2.swamps", "zones de marais",
        lambda: add_swamps(state, profile, reservation, streams.rng("swamps")),
    ))
    state.metadata.update(stage(
        "continental_v2.surface", "autres terrains activés",
        lambda: add_other_terrains(state, profile, reservation, streams.rng("surface")),
    ))
    state.metadata.update(stage(
        "continental_v2.trees", "forêts et palmiers",
        lambda: add_trees(state, profile, reservation, streams.rng("trees")),
    ))
    state.metadata.update(stage(
        "continental_v2.stones", "pierres de construction",
        lambda: add_building_stones(state, profile, reservation, streams.rng("stones")),
    ))
    state.metadata.update(stage(
        "continental_v2.decorations", "objets décoratifs",
        lambda: add_decorations(state, profile, streams.rng("decorations")),
    ))
    state.metadata.update(stage(
        "continental_v2.minerals", "ressources de montagne",
        lambda: add_minerals(state, profile, streams.rng("minerals")),
    ))
    state.metadata.update(stage(
        "continental_v2.fish", "poissons côtiers et lacustres",
        lambda: add_fish(state, profile, streams.rng("fish")),
    ))
    state.metadata.update(stage(
        "continental_v2.accessibility", "accessibilité finale",
        lambda: finalize_accessibility(state),
    ))
    validations = stage("continental_v2.validate", "contrôle structurel", lambda: validate(state, profile))
    return state, validations


__all__ = ("generate",)
