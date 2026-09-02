"""Public generation facade.

The historical validated pipeline remains the Upgraded implementation. The
public facade dispatches the native Legacy engine while keeping the protected
Upgraded module stable.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .core import GenerationRequest
from .generators.legacy import generate as generate_legacy
from .contracts import GenerationOutput
from .validated import MapGenerator as UpgradedMapGenerator


class MapGenerator(UpgradedMapGenerator):
    """Generate either the native Legacy map or the retained Upgraded map."""

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
        super().__init__(
            upgraded_profile_path or profile_path,
            native_library_path,
            upgraded_reference_path,
            progress_callback=progress_callback,
        )

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

        if mirror_mode:
            raise ValueError("Le mode mirror natif est disponible uniquement pour Legacy/Continental")
        return super().generate(
            players=players,
            seed=seed,
            archetype=archetype,
            mode=mode,
            side=side,
            progress_callback=progress_callback,
            **kwargs,
        )
