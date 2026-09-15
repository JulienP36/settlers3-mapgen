"""Public generation facade dispatching independent mode engines."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .core import GenerationRequest
from .archetypes import get_archetype
from .generators.legacy import generate as generate_legacy
from .contracts import GenerationOutput
from .generators.upgraded import generate as generate_upgraded
from .custom import CustomGenerationConfig, build_custom_config


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
        # Active Upgraded defaults are code-owned.  Keep a path only for an
        # explicit external override supplied by a caller.
        self.upgraded_profile_path = (
            Path(upgraded_profile_path)
            if upgraded_profile_path is not None
            else None
        )
        self.upgraded_reference_path = Path(upgraded_reference_path) if upgraded_reference_path else None
        self.progress_callback = progress_callback
        self.stage_log: list[str] = []
        self.current_mode = "upgraded"

    def _resolve_route_config(
        self,
        base_mode: str | None,
        archetype: str,
        custom_config,
        custom_profile,
    ) -> tuple[CustomGenerationConfig, bool]:
        """Resolve the shared Custom route and whether it was explicit.

        A built-in Legacy/Upgraded selection is a preset on this route.  An
        explicitly supplied configuration is an editable Custom route even
        when the public mode argument remains ``legacy`` or ``upgraded``.
        """

        if custom_config is None:
            if base_mode is None:
                raise ValueError("Le mode de base est requis pour créer un profil Custom")
            return (
                build_custom_config(
                    base_mode,
                    archetype,
                    profile=custom_profile,
                    legacy_path=self.profile_path,
                    upgraded_path=self.upgraded_profile_path,
                    start_packages=(),
                ),
                custom_profile is not None,
            )
        if isinstance(custom_config, dict):
            custom_config = CustomGenerationConfig.from_dict(custom_config)
        if not isinstance(custom_config, CustomGenerationConfig):
            raise TypeError("custom_config doit être une CustomGenerationConfig ou un objet JSON")
        if base_mode is not None and custom_config.base_mode != base_mode:
            raise ValueError(
                f"Le mode public {base_mode} doit utiliser un profil Custom {base_mode}"
            )
        if custom_config.base_archetype != archetype:
            raise ValueError(
                "L’archétype sélectionné ne correspond pas à l’archétype du profil Custom"
            )
        return custom_config, True

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
        custom_config = kwargs.pop("custom_config", None)
        custom_profile = kwargs.pop("custom_profile", None)
        custom_base_mode = str(kwargs.pop("custom_base_mode", "upgraded"))
        if mode == "legacy":
            if archetype != "continental":
                raise NotImplementedError(
                    "Native Legacy v1 currently implements the Continental archetype only"
                )
            route_config, explicit_config = self._resolve_route_config(
                "legacy",
                archetype,
                custom_config,
                custom_profile,
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
            report("continental_legacy_native.begin", "terrain natif")
            state, validations = generate_legacy(
                request,
                progress=report,
                mirror_mode=mirror_mode,
                profile=route_config.runtime_profile(
                    execution_kind="custom" if explicit_config else "preset"
                ),
            )
            report("continental_legacy_native.complete", "terrain natif terminé")
            self.stage_log = list(events)
            self.current_mode = "legacy"
            return GenerationOutput(state, validations, list(events))

        if mode == "custom":
            arch_spec = get_archetype(archetype)
            if not arch_spec.implemented:
                raise NotImplementedError(f"L'archétype {arch_spec.label} n'est pas implémenté")
            custom_config, _ = self._resolve_route_config(
                None,
                archetype,
                custom_config,
                custom_profile,
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
            report(
                "custom.begin",
                f"profil dérivé de {custom_config.base_mode} · {custom_config.digest[:12]}",
            )
            runtime_profile = custom_config.runtime_profile()
            if custom_config.base_mode == "legacy":
                state, validations = generate_legacy(
                    request,
                    progress=report,
                    mirror_mode=mirror_mode,
                    profile=runtime_profile,
                )
            else:
                state, validations = generate_upgraded(
                    request,
                    progress=report,
                    mirror_mode=mirror_mode,
                    archetype=archetype,
                    profile=runtime_profile,
                )
            report("custom.complete", "profil Custom terminé")
            self.stage_log = list(events)
            self.current_mode = "custom"
            return GenerationOutput(state, validations, list(events))
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
            profile=self._resolve_route_config(
                "upgraded",
                archetype,
                custom_config,
                custom_profile,
            )[0].runtime_profile(
                execution_kind=(
                    "custom"
                    if custom_config is not None or custom_profile is not None
                    else "preset"
                )
            ),
        )
        self.stage_log = events
        self.current_mode = "upgraded"
        return GenerationOutput(state, validations, list(events))
