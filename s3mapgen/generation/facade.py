"""Public generation facade dispatching independent mode engines."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .core import GenerationRequest
from .generators.legacy import generate as generate_legacy
from .contracts import GenerationOutput
from .generators.upgraded import generate as generate_upgraded


class MapGenerator:
    """Generate through the selected, fully independent mode engine."""

    def __init__(
        self,
        profile_path: Path | str,
        native_library_path: Path | str,
        upgraded_profile_path: Path | str | None = None,
        upgraded_reference_path: Path | str | None = None,
        progress_callback=None,
    ) -> None:
        # Keep the historical three-argument source API usable:
        # MapGenerator(upgraded_profile, library, upgraded_reference).
        if (
            upgraded_reference_path is None
            and upgraded_profile_path is not None
            and str(upgraded_profile_path).lower().endswith(".edm")
        ):
            upgraded_reference_path = upgraded_profile_path
            upgraded_profile_path = None
        self.profile_path = Path(profile_path)
        self.native_library_path = Path(native_library_path)
        self.upgraded_profile_path = Path(upgraded_profile_path or profile_path)
        self.upgraded_reference_path = Path(upgraded_reference_path) if upgraded_reference_path else None
        self.progress_callback = progress_callback
        self.stage_log: list[str] = []
        self.current_mode = "upgraded"

    def generate(
        self,
        players: int,
        seed: int,
        mode: str = "upgraded",
        archetype: str = "continental",
        side: int = 768,
        progress_callback=None,
        **kwargs: Any,
    ):
        mirror_mode = int(kwargs.pop("mirror_mode", 0))
        if mode == "legacy":
            if archetype != "continental":
                raise NotImplementedError(
                    "Native Legacy v1 currently implements the Continental archetype only"
                )
            request = GenerationRequest(
                side=int(side),
                players=int(players),
                seed=int(seed),
            )
            callback = progress_callback or self.progress_callback
            events: list[str] = []

            def report(stage: str, detail: str = "") -> None:
                events.append(stage + (f" — {detail}" if detail else ""))
                if callback is not None:
                    try:
                        callback(stage, detail, len(events))
                    except Exception:
                        pass

            if mirror_mode not in (0, 1, 2, 3):
                raise ValueError("mirror_mode doit être compris entre 0 et 3")
            report("continental_legacy_native.begin", "terrain natif récupéré")
            state, validations = generate_legacy(
                request,
                progress=report,
                mirror_mode=mirror_mode,
            )
            report("continental_legacy_native.complete", "terrain natif terminé")
            self.stage_log = list(events)
            self.current_mode = "legacy"
            return GenerationOutput(state, validations, list(events))

        if mode == "custom":
            raise NotImplementedError("Le mode Custom n'est pas encore implémenté")
        if mode != "upgraded":
            raise ValueError(f"Mode de génération inconnu : {mode}")
        if mirror_mode not in (0, 1, 2, 3):
            raise ValueError("mirror_mode doit être compris entre 0 et 3")
        callback = progress_callback or self.progress_callback
        events: list[str] = []

        def report(stage: str, detail: str = "") -> None:
            events.append(stage + (f" — {detail}" if detail else ""))
            if callback is not None:
                try:
                    callback(stage, detail, len(events))
                except Exception:
                    pass

        state, validations = generate_upgraded(
            GenerationRequest(side=int(side), players=int(players), seed=int(seed)),
            progress=report,
            mirror_mode=mirror_mode,
            archetype=archetype,
            profile_path=self.upgraded_profile_path,
        )
        self.stage_log = events
        self.current_mode = "upgraded"
        return GenerationOutput(state, validations, list(events))
