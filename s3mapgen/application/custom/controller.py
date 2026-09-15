"""Tk editor for declarative Custom generator profiles."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from ...generation.archetypes import ARCHETYPES
from ...generation.custom import (
    START_PACKAGE_CATALOG,
    CustomGenerationConfig,
    MINERAL_ALGORITHMS,
    MINERAL_SPECS,
    FOREST_TREE_COUNT_MAX,
    FOREST_TREE_COUNT_MIN,
    FOREST_TREE_VARIATION_MAX,
    FOREST_TREE_VARIATION_MIN,
    RESOURCE_MAXIMUM,
    RESOURCE_MINIMUM,
    STONE_QUANTITY_MAXIMUM,
    STONE_QUANTITY_MINIMUM,
    STONE_QUANTITY_STEP,
    START_SWAMP_RADIUS_MAX,
    START_SWAMP_RADIUS_MIN,
    START_SWAMP_SHAPES,
    START_FOREST_COUNT_MAX,
    START_FOREST_COUNT_MIN,
    START_STONE_ANCHOR_MAX,
    START_STONE_ANCHOR_MIN,
    START_BONUS_DISTANCE_MAX,
    START_BONUS_DISTANCE_MIN,
    START_BONUS_FISH_FILL_MAX,
    START_BONUS_FISH_FILL_MIN,
    START_BONUS_RADIUS_MAX,
    START_BONUS_RADIUS_MIN,
    START_LAKE_SHAPES,
    START_ROCKY_RADIUS_MAX,
    START_ROCKY_SHAPES,
    START_ROCKY_SURFACE_MODES,
    START_ROCKY_CORE_CELLS_MIN,
    START_ROCKY_CORE_CELLS_MAX,
    rocky_total_cells_max,
    rocky_equal_core_cells,
    rocky_equivalent_radius,
    rocky_proportional_targets,
    START_BONUS_RIVER_TARGET_MAX,
    START_BONUS_RIVER_TARGET_MIN,
    START_BONUS_WATER_PROXIMITY_MAX,
    START_BONUS_WATER_PROXIMITY_MIN,
    STONE_GROUP_COUNT_MAX,
    STONE_GROUP_COUNT_MIN,
    STONE_GROUP_VARIATION_MAX,
    STONE_GROUP_VARIATION_MIN,
    RIVER_RATE_MAX,
    RIVER_RATE_MIN,
    RIVER_RATE_STEP,
    DECORATION_FAMILY_KEYS,
    DECORATION_RATE_MAX,
    DECORATION_RATE_MIN,
    SEMANTIC_DENSITY_MAX,
    SEMANTIC_DENSITY_MIN,
    TERRAIN_FAMILY_KEYS,
    TERRAIN_ENABLED_RATE_MIN,
    TERRAIN_RATE_MAX,
    TERRAIN_RATE_MIN,
    TERRAIN_FAMILY_KEYS,
    TERRAIN_RATE_MAX,
    TERRAIN_RATE_MIN,
    SIZE_VARIATIONS,
    TREE_QUOTA_MAX,
    TREE_PLACEMENTS,
    build_custom_config,
    default_sections,
    normalize_sections,
    set_path,
)
from ..ui.i18n.common import _lang_text
from ..ui.i18n.shell import ARCHETYPE_LABELS, MODE_LABELS
from ..ui.widgets.icons import mineral_icon
from .i18n import (
    archetype_description,
    custom_section_text,
    mineral_label,
    parameter_group,
    parameter_label,
)


class CustomGeneratorController:
    """Build and maintain the DEV6 generator/archetype parameter tabs.

    The controller is deliberately a UI adapter.  The immutable configuration
    object it edits is owned by ``s3mapgen.generation.custom`` and is passed to
    the facade, cache and batch workflow without importing Tk there.
    """

    def _build_custom_parameter_tabs(self):
        self._custom_config: CustomGenerationConfig | None = None
        self._custom_last_concrete_mode = "upgraded"
        self._custom_last_concrete_archetype = "continental"
        self._custom_last_ui_mode: str | None = None
        self._custom_last_ui_archetype: str | None = None
        self._custom_last_render_digest: str | None = None
        self._custom_section_vars: dict[str, tk.Variable] = {}
        self._custom_package_vars: dict[str, tk.BooleanVar] = {}
        self._custom_start_bonus_control_widgets: dict[str, list[tk.Widget]] = {}
        self._custom_status_var = tk.StringVar(value="")
        self._custom_provenance_var = tk.StringVar(value="")
        self._custom_generator_tab = self._scroll_notebook_tab("Générateur")
        self._custom_archetype_tab = self._scroll_notebook_tab("Archétype")
        self._custom_selection_changed()

    def _custom_language(self) -> str:
        return self.prefs.get("language", "fr")

    def _custom_config_digest(self) -> str:
        """Expose the active profile identity to generation/cache workflows."""

        return self._custom_config.digest if self._custom_config is not None else self._custom_ensure_config().digest

    def _custom_current_mode(self) -> str:
        return self._mode_key() if hasattr(self, "mode") else "upgraded"

    def _custom_current_archetype(self) -> str:
        return self._arch_key() if hasattr(self, "arch") else "continental"

    def _custom_generator_scroll_position(self):
        """Capture the visible generator area before rebuilding its controls."""

        tab = getattr(self, "_custom_generator_tab", None)
        canvas = getattr(tab, "_scroll_canvas", None)
        if canvas is None:
            return None
        try:
            return tuple(canvas.yview())
        except tk.TclError:
            return None

    def _custom_restore_generator_scroll_position(self, position) -> None:
        """Restore a captured position after Tk has measured new controls."""

        if position is None:
            return
        tab = getattr(self, "_custom_generator_tab", None)
        canvas = getattr(tab, "_scroll_canvas", None)
        if canvas is None:
            return
        try:
            if getattr(self, "_custom_scroll_restore_after", None) is not None:
                canvas.after_cancel(self._custom_scroll_restore_after)
        except tk.TclError:
            pass

        def restore():
            self._custom_scroll_restore_after = None
            try:
                canvas.update_idletasks()
                canvas.yview_moveto(max(0.0, min(1.0, float(position[0]))))
            except (tk.TclError, TypeError, ValueError):
                pass

        try:
            self._custom_scroll_restore_after = canvas.after_idle(restore)
        except tk.TclError:
            restore()

    def _custom_preset_config(self, mode: str, archetype: str) -> CustomGenerationConfig:
        # DEV6 exposes the Continental profile.  The archetype contract tab is
        # already present for future island profiles, so the same profile can
        # be inspected while those engines remain explicitly unavailable.
        # Built-in Legacy/Upgraded presets do not carry Custom start packages:
        # each bonus is explicitly opted into from its own panel.
        return build_custom_config(mode, archetype, start_packages=())

    def _custom_ensure_config(
        self,
        base_mode: str | None = None,
        base_archetype: str | None = None,
    ) -> CustomGenerationConfig:
        mode = base_mode or self._custom_last_concrete_mode
        archetype = base_archetype or self._custom_last_concrete_archetype
        if mode == "custom":
            mode = self._custom_last_concrete_mode
        if self._custom_config is None:
            self._custom_config = self._custom_preset_config(mode, archetype)
        elif (
            self._custom_config.base_mode != mode
            or self._custom_config.base_archetype != archetype
        ):
            self._custom_config = self._custom_preset_config(mode, archetype)
        return self._custom_config

    def _custom_profile_for_display(self) -> CustomGenerationConfig:
        mode = self._custom_current_mode()
        archetype = self._custom_current_archetype()
        if mode == "custom":
            return self._custom_ensure_config()
        if mode in ("legacy", "upgraded"):
            self._custom_last_concrete_mode = mode
            self._custom_last_concrete_archetype = archetype
            return self._custom_preset_config(mode, archetype)
        return self._custom_ensure_config()

    def _custom_render_custom_mode(self, config: CustomGenerationConfig) -> None:
        language = self._custom_language()
        base_mode = MODE_LABELS.get(language, MODE_LABELS["en"])[config.base_mode]
        base_arch = ARCHETYPE_LABELS.get(language, ARCHETYPE_LABELS["en"])[config.base_archetype]
        self._custom_provenance_var.set(
            _lang_text(
                language,
                f"Base : {base_mode} / {base_arch} · profil {config.profile.get('profile_name', 'sans nom')} · empreinte {config.digest[:12]}",
                f"Base: {base_mode} / {base_arch} · profile {config.profile.get('profile_name', 'unnamed')} · fingerprint {config.digest[:12]}",
                f"Basis: {base_mode} / {base_arch} · Profil {config.profile.get('profile_name', 'ohne Namen')} · Fingerabdruck {config.digest[:12]}",
                f"Base: {base_mode} / {base_arch} · perfil {config.profile.get('profile_name', 'sin nombre')} · huella {config.digest[:12]}",
            )
        )

    def _custom_refresh_fish_controls(self) -> None:
        """Keep the coastal thickness input synchronized with its switch.

        Once the editor is already in Custom, parameter edits intentionally do
        not rebuild the whole tab.  Dependent widgets therefore need this
        small in-place refresh, otherwise a Legacy-derived profile can leave
        the coastal thickness input disabled after enabling the coastal band.
        """

        widget = getattr(self, "_custom_fish_band_thickness_widget", None)
        if widget is None or self._custom_config is None:
            return
        try:
            fish = self._custom_config.semantic_sections().get("fish", {})
            widget.configure(state="normal" if bool(fish.get("near_shore", False)) else "disabled")
        except tk.TclError:
            # The complete parameter tab may be between two renders.  The new
            # widget will receive its initial state when that render completes.
            pass

    def _custom_refresh_start_bonus_controls(self) -> None:
        """Enable detailed bonus controls only when their package is active."""

        for key, widgets in getattr(self, "_custom_start_bonus_control_widgets", {}).items():
            variable = self._custom_package_vars.get(key)
            enabled = bool(variable.get()) if variable is not None else True
            for widget in widgets:
                try:
                    # A package switch must not make a selector editable.  The
                    # old blanket "normal" state changed readonly comboboxes
                    # back into entry-like controls whenever a bonus panel
                    # was toggled.
                    if enabled:
                        state = "readonly" if isinstance(widget, ttk.Combobox) else "normal"
                    else:
                        state = "disabled"
                    widget.configure(state=state)
                except tk.TclError:
                    pass
        # Some packages have a second dependency layer inside their panel.
        # Reapply it after the package-wide switch so a mode-specific control
        # cannot be re-enabled merely because its parent bonus was toggled.
        rocky_refresh = getattr(self, "_custom_refresh_rocky_controls", None)
        if rocky_refresh is not None:
            rocky_refresh()

    def _render_custom_parameter_tabs(self):
        if not hasattr(self, "_custom_generator_tab"):
            return
        config = self._custom_profile_for_display()
        generator_scroll_position = self._custom_generator_scroll_position()
        root = self._custom_generator_tab
        for child in root.winfo_children():
            child.destroy()
        root.columnconfigure(0, weight=1)
        root.columnconfigure(1, weight=0)
        language = self._custom_language()
        mode = self._custom_current_mode()
        archetype = self._custom_current_archetype()

        ttk.Label(root, text=_lang_text(language, "Générateur", "Generator", "Generator", "Generador"), style="Section.TLabel").grid(
            row=0, column=0, sticky="w", pady=(0, 3)
        )
        ttk.Label(
            root,
            text=_lang_text(
                language,
                "Les presets intégrés sont modifiables par dérivation : la première modification sélectionne Custom. Les paramètres non encore raccordés sont signalés par le moteur.",
                "Built-in presets are edited by derivation: the first change selects Custom. Parameters not wired yet are reported by the engine.",
                "Integrierte Presets werden durch Ableitung bearbeitet: Die erste Änderung wählt Custom. Noch nicht verbundene Parameter werden von der Engine gemeldet.",
                "Los presets integrados se editan por derivación: la primera modificación selecciona Custom. El motor informa de los parámetros aún no conectados.",
            ),
            style="Hint.TLabel",
            wraplength=620,
            justify="left",
        ).grid(row=1, column=0, sticky="w", pady=(0, 8))
        ttk.Label(root, textvariable=self._custom_provenance_var, style="Hint.TLabel", wraplength=720).grid(
            row=2, column=0, sticky="w", pady=(0, 8)
        )

        actions = ttk.Frame(root)
        actions.grid(row=3, column=0, sticky="ew", pady=(0, 9))
        ttk.Button(
            actions,
            text=_lang_text(language, "Réinitialiser le Custom", "Reset Custom", "Custom zurücksetzen", "Restablecer Custom"),
            command=self._custom_reset,
        ).pack(side="left")
        ttk.Label(actions, textvariable=self._custom_status_var, style="Hint.TLabel", wraplength=540).pack(
            side="left", padx=(10, 0)
        )

        # Each bonus panel owns its activation switch.  Keeping the switch at
        # the top of the corresponding settings avoids a detached package
        # list and makes the Legacy/Upgraded preset default (all OFF) obvious.
        self._custom_package_vars = {}
        active_packages = set(config.start_packages)
        for spec in START_PACKAGE_CATALOG:
            var = tk.BooleanVar(value=spec.key in active_packages)
            self._custom_package_vars[spec.key] = var

        sections_frame = ttk.Frame(root)
        sections_frame.grid(row=4, column=0, sticky="ew", pady=(0, 10))
        sections_frame.columnconfigure(0, weight=1)
        sections = config.semantic_sections()
        self._custom_section_vars = {}
        self._custom_mineral_icon_widgets: dict[str, list[tk.Widget]] = {
            key: [] for key, _family in MINERAL_SPECS
        }
        self._custom_mineral_icon_buttons: dict[str, list[tk.Widget]] = {
            key: [] for key, _family in MINERAL_SPECS
        }
        self._custom_start_bonus_control_widgets = {
            key: []
            for key in (
                "start_forest",
                "start_building_stones",
                "start_mini_swamp",
                "start_rocky_minerals",
                "start_lake_fish_river",
            )
        }
        self._custom_refresh_terrain_dependencies = None
        self._custom_refresh_rocky_controls = None
        self._custom_materialize_rocky_state = None

        def bind_text(widget, path, variable):
            widget.bind(
                "<Return>",
                lambda event, p=path, v=variable: self._custom_section_changed(p, v.get()),
            )
            widget.bind(
                "<FocusOut>",
                lambda event, p=path, v=variable: self._custom_section_changed(p, v.get()),
            )

        def _display_number(value):
            number = float(value)
            return str(int(number)) if number.is_integer() else f"{number:g}"

        def add_spin(
            parent,
            row,
            label,
            path,
            value,
            low,
            high,
            increment=1,
            unit="",
            *,
            column=0,
            columnspan=1,
            variable=None,
        ):
            line = ttk.Frame(parent)
            line.grid(row=row, column=column, columnspan=columnspan, sticky="w", pady=2)
            ttk.Label(line, text=label).grid(row=0, column=0, sticky="w", padx=(0, 8))
            if variable is None:
                variable = tk.StringVar(value=_display_number(value))
            widget = ttk.Spinbox(
                line,
                from_=low,
                to=high,
                increment=increment,
                textvariable=variable,
                width=9,
                command=lambda p=path, v=variable: self._custom_section_changed(p, v.get()),
            )
            widget.grid(row=0, column=1, sticky="w")
            maximum = _display_number(high)
            if unit:
                maximum = f"{maximum} {unit}"
                unit_text = f"{unit} · {custom_section_text('max_value', language, value=maximum)}"
            else:
                unit_text = custom_section_text("max_value", language, value=maximum)
            ttk.Label(line, text=unit_text, style="Hint.TLabel").grid(
                row=0, column=2, sticky="w", padx=(4, 0)
            )
            bind_text(widget, path, variable)
            self._custom_section_vars[".".join(path)] = variable
            return widget

        def add_aligned_spin(
            parent,
            row,
            label,
            path,
            value,
            low,
            high,
            increment=1,
            unit="",
            *,
            variable=None,
            icon=None,
            icon_key=None,
        ):
            """Add a resource control in the shared icon/input/name/max grid."""

            if variable is None:
                variable = tk.StringVar(value=_display_number(value))
            widget = ttk.Spinbox(
                parent,
                from_=low,
                to=high,
                increment=increment,
                textvariable=variable,
                width=9,
                command=lambda p=path, v=variable: self._custom_section_changed(p, v.get()),
            )
            column = 0
            if icon is not None:
                icon_label = ttk.Label(parent, image=icon)
                icon_label.grid(
                    row=row, column=column, sticky="w", padx=(0, 4), pady=2
                )
                if icon_key is not None:
                    self._custom_mineral_icon_widgets.setdefault(icon_key, []).append(icon_label)
                column += 1
            widget.grid(row=row, column=column, sticky="w", pady=2)
            column += 1
            if unit:
                ttk.Label(parent, text=unit, style="Hint.TLabel").grid(
                    row=row, column=column, sticky="w", padx=(5, 10), pady=2
                )
                column += 1
            ttk.Label(parent, text=label).grid(
                row=row, column=column, sticky="w", padx=(0, 8), pady=2
            )
            column += 1
            maximum = _display_number(high)
            if unit:
                maximum = f"{maximum} {unit}"
            ttk.Label(
                parent,
                text=custom_section_text("max_value", language, value=maximum),
                style="Hint.TLabel",
            ).grid(row=row, column=column, sticky="w", pady=2)
            bind_text(widget, path, variable)
            self._custom_section_vars[".".join(path)] = variable
            return widget

        def add_decoration_spin(
            parent,
            row,
            label,
            path,
            value,
            low,
            high,
            increment=1,
            unit="",
            *,
            column=0,
            variable=None,
        ):
            """Add a decoration rate with a reserved 16×16 icon slot.

            The slot is deliberately empty for now: the user is preparing the
            pixel-art family icons separately.  Keeping it in the row already
            fixes the final geometry without changing the 22 px Spinbox line
            height when the sprites are added later.
            """

            line = ttk.Frame(parent)
            line.grid(row=row, column=column, sticky="w", pady=2)
            line.columnconfigure(0, minsize=16)
            icon_slot = ttk.Frame(line, width=16, height=16)
            icon_slot.grid(row=0, column=0, sticky="w", padx=(0, 5))
            icon_slot.grid_propagate(False)
            if not hasattr(self, "_custom_decoration_icon_slots"):
                self._custom_decoration_icon_slots = {}
            self._custom_decoration_icon_slots[path[-1]] = icon_slot
            if variable is None:
                variable = tk.StringVar(value=_display_number(value))
            widget = ttk.Spinbox(
                line,
                from_=low,
                to=high,
                increment=increment,
                textvariable=variable,
                width=9,
                command=lambda p=path, v=variable: self._custom_section_changed(p, v.get()),
            )
            widget.grid(row=0, column=1, sticky="w")
            ttk.Label(line, text=unit, style="Hint.TLabel").grid(
                row=0, column=2, sticky="w", padx=(5, 10)
            )
            ttk.Label(line, text=label).grid(
                row=0, column=3, sticky="w", padx=(0, 8)
            )
            maximum = _display_number(high)
            if unit:
                maximum = f"{maximum} {unit}"
            ttk.Label(
                line,
                text=custom_section_text("max_value", language, value=maximum),
                style="Hint.TLabel",
            ).grid(row=0, column=4, sticky="w")
            bind_text(widget, path, variable)
            self._custom_section_vars[".".join(path)] = variable
            self._custom_decoration_rate_vars[path[-1]] = variable
            self._custom_decoration_rate_widgets[path[-1]] = widget
            return widget

        minerals = ttk.LabelFrame(
            sections_frame,
            text=custom_section_text("minerals", language),
            padding=8,
        )
        minerals.grid(row=1, column=0, sticky="ew", pady=(0, 8))
        minerals.columnconfigure(0, weight=0)
        minerals.columnconfigure(1, weight=0)
        mineral_values = sections["minerals"]
        self._custom_mineral_icons = {
            key: mineral_icon(self, key)
            for key, _family in MINERAL_SPECS
        }
        self._custom_mineral_disabled_icons = {
            key: mineral_icon(self, key, disabled=True)
            for key, _family in MINERAL_SPECS
        }
        algorithm_line = ttk.Frame(minerals)
        algorithm_line.grid(row=0, column=0, columnspan=2, sticky="w", pady=2)
        ttk.Label(algorithm_line, text=custom_section_text("mineral_algorithm", language)).grid(
            row=0, column=0, sticky="w", padx=(0, 8)
        )
        algorithm_labels = {
            "legacy": custom_section_text("legacy_algorithm", language),
            "upgraded": custom_section_text("upgraded_algorithm", language),
            "random": custom_section_text("random_algorithm", language),
        }
        algorithm_var = tk.StringVar(value=algorithm_labels[mineral_values["algorithm"]])
        algorithm_combo = ttk.Combobox(
            algorithm_line,
            textvariable=algorithm_var,
            values=[algorithm_labels[key] for key in MINERAL_ALGORITHMS],
            state="readonly",
            width=18,
        )
        algorithm_combo.grid(row=0, column=1, sticky="w")
        algorithm_combo.bind(
            "<<ComboboxSelected>>",
            lambda event: self._custom_section_changed(
                ("minerals", "algorithm"),
                next(key for key, label in algorithm_labels.items() if label == algorithm_var.get()),
            ),
        )
        algorithm_hint = _lang_text(
            language,
            "Legacy : motifs historiques. Upgraded : gisements compacts sans trous. Pixels aléatoires : cases dispersées.",
            "Legacy: historical patterns. Upgraded: compact deposits without gaps. Random pixels: scattered cells.",
            "Legacy: historische Muster. Upgraded: kompakte Lagerstätten ohne Lücken. Zufällige Pixel: verstreute Zellen.",
            "Legacy: patrones históricos. Upgraded: yacimientos compactos sin huecos. Píxeles aleatorios: celdas dispersas.",
        )
        ttk.Label(minerals, text=algorithm_hint, style="Hint.TLabel", wraplength=560).grid(
            row=1, column=0, columnspan=2, sticky="w", pady=(0, 5)
        )

        mineral_grid = ttk.Frame(minerals)
        mineral_grid.grid(row=2, column=0, columnspan=2, sticky="nw", pady=(0, 1))
        # Keep the paired controls adjacent instead of stretching each half
        # across the full tab; the surrounding scroll surface still provides
        # the responsive fallback when the window becomes narrow.
        mineral_grid.columnconfigure(0, weight=0)
        mineral_grid.columnconfigure(1, weight=0)

        occupancy_frame = ttk.Frame(mineral_grid)
        occupancy_frame.grid(row=0, column=0, sticky="nw", padx=(0, 6))
        add_spin(
            occupancy_frame,
            0,
            custom_section_text("occupancy_percent", language),
            ("minerals", "occupancy_percent"),
            mineral_values["occupancy_percent"],
            0,
            100,
            0.1,
            custom_section_text("percent_unit", language),
        )

        variation_frame = ttk.Frame(mineral_grid)
        variation_frame.grid(row=0, column=1, sticky="nw", padx=(6, 0))
        ttk.Label(variation_frame, text=custom_section_text("size_variation", language)).grid(
            row=0, column=0, sticky="w", padx=(0, 8), pady=2
        )
        variation_labels = {key: custom_section_text(key, language) for key in SIZE_VARIATIONS}
        variation_var = tk.StringVar(value=variation_labels[mineral_values["size_variation"]])
        variation_combo = ttk.Combobox(
            variation_frame,
            textvariable=variation_var,
            values=[variation_labels[key] for key in SIZE_VARIATIONS],
            state="readonly",
            width=12,
        )
        variation_combo.grid(row=0, column=1, sticky="w", pady=2)
        variation_combo.bind(
            "<<ComboboxSelected>>",
            lambda event: self._custom_section_changed(
                ("minerals", "size_variation"),
                next(key for key, label in variation_labels.items() if label == variation_var.get()),
            ),
        )

        shares_frame = ttk.LabelFrame(
            mineral_grid,
            text=custom_section_text("mineral_shares", language),
            padding=6,
        )
        shares_frame.grid(row=1, column=0, sticky="nw", padx=(0, 6), pady=(5, 0))
        shares_frame.columnconfigure(1, minsize=24)
        share_vars: dict[str, tk.StringVar] = {}
        for row, (key, _family) in enumerate(MINERAL_SPECS):
            # The model keeps calibrated shares at full precision so a
            # preset-equivalent Custom generation is reproducible.  The
            # control stays short and ergonomic for users.
            variable = tk.StringVar(value=f"{float(mineral_values['shares'].get(key, 0.0)):.1f}")
            share_vars[key] = variable
            add_aligned_spin(
                shares_frame,
                row,
                mineral_label(key, language),
                ("minerals", "shares", key),
                variable.get(),
                0,
                100,
                0.1,
                custom_section_text("percent_unit", language),
                variable=variable,
                icon=self._custom_mineral_icons[key],
                icon_key=key,
            )
        self._custom_mineral_share_vars = share_vars
        share_total_var = tk.StringVar(value="")
        self._custom_section_share_total_var = share_total_var

        def refresh_share_total(*_args):
            total = 0.0
            for variable in share_vars.values():
                try:
                    total += float(variable.get())
                except (TypeError, ValueError):
                    pass
            share_total_var.set(custom_section_text("shares_total", language, value=f"{total:.1f}"))

        for variable in share_vars.values():
            variable.trace_add("write", refresh_share_total)
        ttk.Label(shares_frame, textvariable=share_total_var, style="Hint.TLabel").grid(
            row=len(MINERAL_SPECS), column=0, columnspan=5, sticky="w", pady=(4, 0)
        )
        refresh_share_total()

        quantity_frame = ttk.LabelFrame(
            mineral_grid,
            text=custom_section_text("average_quantity", language),
            padding=6,
        )
        quantity_frame.grid(row=1, column=1, sticky="nw", padx=(6, 0), pady=(5, 0))
        for row, (key, _family) in enumerate(MINERAL_SPECS):
            add_aligned_spin(
                quantity_frame,
                row,
                mineral_label(key, language),
                ("minerals", "average_quantity", key),
                mineral_values["average_quantity"].get(key, 10),
                RESOURCE_MINIMUM,
                RESOURCE_MAXIMUM,
                1,
                icon=self._custom_mineral_icons[key],
                icon_key=key,
            )
        ttk.Label(quantity_frame, text=custom_section_text("resource_hint", language), style="Hint.TLabel").grid(
            row=len(MINERAL_SPECS), column=0, columnspan=5, sticky="w", pady=(4, 0)
        )

        fish = ttk.LabelFrame(
            sections_frame,
            text=custom_section_text("fish", language),
            padding=8,
        )
        fish.grid(row=2, column=0, sticky="ew")
        fish.columnconfigure(0, weight=0)
        fish.columnconfigure(1, weight=0)
        fish_values = sections["fish"]
        fish_grid = ttk.Frame(fish)
        fish_grid.grid(row=0, column=0, columnspan=2, sticky="nw")
        fish_grid.columnconfigure(0, weight=0)
        fish_grid.columnconfigure(1, weight=0)
        add_spin(
            fish_grid,
            0,
            custom_section_text("fill_percent", language),
            ("fish", "fill_percent"),
            fish_values["fill_percent"],
            0,
            100,
            0.1,
            custom_section_text("percent_unit", language),
            column=0,
        )
        add_spin(
            fish_grid,
            0,
            custom_section_text("average_quantity", language),
            ("fish", "average_quantity"),
            fish_values["average_quantity"],
            RESOURCE_MINIMUM,
            RESOURCE_MAXIMUM,
            1,
            column=1,
        )
        near_shore_var = tk.BooleanVar(value=bool(fish_values["near_shore"]))
        near_shore = ttk.Checkbutton(
            fish,
            text=custom_section_text("near_shore", language),
            variable=near_shore_var,
            command=lambda: self._custom_section_changed(("fish", "near_shore"), near_shore_var.get()),
        )
        near_shore.grid(row=1, column=0, columnspan=2, sticky="w", pady=(5, 2))
        band_thickness = add_spin(
            fish_grid,
            2,
            custom_section_text("band_thickness", language),
            ("fish", "band_thickness"),
            fish_values["band_thickness"],
            1,
            4096,
            1,
            custom_section_text("cells_unit", language),
            column=0,
        )
        self._custom_fish_band_thickness_widget = band_thickness
        band_thickness.configure(state="normal" if fish_values["near_shore"] else "disabled")
        ttk.Label(fish, text=custom_section_text("coast_hint", language), style="Hint.TLabel", wraplength=620).grid(
            row=3, column=0, columnspan=2, sticky="w", pady=(5, 0)
        )

        rivers = ttk.LabelFrame(
            sections_frame,
            text=custom_section_text("rivers", language),
            padding=8,
        )
        rivers.grid(row=3, column=0, sticky="ew", pady=(8, 8))
        rivers.columnconfigure(0, weight=0)
        river_values = sections["rivers"]
        add_spin(
            rivers,
            0,
            custom_section_text("river_rate", language),
            ("rivers", "rate_percent"),
            river_values["rate_percent"],
            RIVER_RATE_MIN,
            RIVER_RATE_MAX,
            RIVER_RATE_STEP,
            custom_section_text("percent_unit", language),
            column=0,
        )
        ttk.Label(
            rivers,
            text=custom_section_text("river_hint", language),
            style="Hint.TLabel",
            wraplength=620,
        ).grid(row=1, column=0, sticky="w", pady=(5, 0))

        terrains = ttk.LabelFrame(
            sections_frame,
            text=custom_section_text("terrains", language),
            padding=8,
        )
        terrains.grid(row=4, column=0, sticky="ew", pady=(8, 8))
        terrain_values = sections["terrains"]
        terrain_rate_vars: dict[str, tk.StringVar] = {}
        terrain_rate_widgets = {}
        for row, terrain_key in enumerate(TERRAIN_FAMILY_KEYS):
            entry = terrain_values[terrain_key]
            line = ttk.Frame(terrains)
            line.grid(row=row, column=0, sticky="w", pady=2)
            enabled_var = tk.BooleanVar(value=bool(entry["enabled"]))
            rate_var = tk.StringVar(
                value=_display_number(entry["rate_percent"] if entry["enabled"] else 0)
            )
            ttk.Checkbutton(
                line,
                text=custom_section_text(f"terrain_{terrain_key}", language),
                variable=enabled_var,
                command=lambda key=terrain_key, variable=enabled_var: (
                    self._custom_section_changed(("terrains", key, "enabled"), variable.get()),
                    self._custom_refresh_terrain_dependencies() if self._custom_refresh_terrain_dependencies else None,
                ),
            ).grid(row=0, column=0, sticky="w", padx=(0, 8))
            widget = ttk.Spinbox(
                line,
                from_=TERRAIN_ENABLED_RATE_MIN if entry["enabled"] else TERRAIN_RATE_MIN,
                to=TERRAIN_RATE_MAX,
                increment=1,
                textvariable=rate_var,
                width=9,
                command=lambda key=terrain_key, variable=rate_var: self._custom_section_changed(
                    ("terrains", key, "rate_percent"), variable.get()
                ),
            )
            widget.grid(row=0, column=1, sticky="w")
            ttk.Label(line, text=custom_section_text("percent_unit", language), style="Hint.TLabel").grid(
                row=0, column=2, sticky="w", padx=(5, 10)
            )
            ttk.Label(
                line,
                text=custom_section_text("max_value", language, value="500 %"),
                style="Hint.TLabel",
            ).grid(row=0, column=3, sticky="w")
            bind_text(widget, ("terrains", terrain_key, "rate_percent"), rate_var)
            self._custom_section_vars[f"terrains.{terrain_key}.rate_percent"] = rate_var
            terrain_rate_vars[terrain_key] = rate_var
            terrain_rate_widgets[terrain_key] = widget

        ttk.Label(
            terrains,
            text=custom_section_text("terrain_hint", language),
            style="Hint.TLabel",
            wraplength=620,
        ).grid(row=len(TERRAIN_FAMILY_KEYS), column=0, sticky="w", pady=(5, 0))

        trees = ttk.LabelFrame(
            sections_frame,
            text=custom_section_text("trees", language),
            padding=8,
        )
        trees.grid(row=5, column=0, sticky="ew", pady=(0, 8))
        trees.columnconfigure(0, weight=0)
        trees.columnconfigure(1, weight=0)
        tree_values = sections["trees"]
        sapling_values = tree_values["saplings"]
        forest_values = tree_values["forests"]
        tree_quota_grid = ttk.Frame(trees)
        tree_quota_grid.grid(row=0, column=0, columnspan=2, sticky="nw")
        tree_quota_grid.columnconfigure(0, weight=0)
        tree_quota_grid.columnconfigure(1, weight=0)
        add_spin(
            tree_quota_grid,
            0,
            custom_section_text("tree_base_quota", language),
            ("trees", "base_quota_percent"),
            tree_values["base_quota_percent"],
            SEMANTIC_DENSITY_MIN,
            TREE_QUOTA_MAX,
            1,
            custom_section_text("percent_unit", language),
            column=0,
        )
        palm_widget = add_spin(
            tree_quota_grid,
            0,
            custom_section_text("tree_palm_quota", language),
            ("trees", "palm_quota_percent"),
            tree_values["palm_quota_percent"],
            SEMANTIC_DENSITY_MIN,
            TREE_QUOTA_MAX,
            1,
            custom_section_text("percent_unit", language),
            column=1,
        )

        saplings = ttk.LabelFrame(trees, text=custom_section_text("tree_saplings", language), padding=6)
        saplings.grid(row=1, column=0, columnspan=2, sticky="nw", pady=(6, 6))
        saplings.columnconfigure(0, weight=0)
        saplings.columnconfigure(1, weight=0)
        saplings_enabled_var = tk.BooleanVar(value=bool(sapling_values["enabled"]))
        saplings_enabled = ttk.Checkbutton(
            saplings,
            text=custom_section_text("tree_saplings_enabled", language),
            variable=saplings_enabled_var,
            command=lambda: self._custom_section_changed(("trees", "saplings", "enabled"), saplings_enabled_var.get()),
        )
        saplings_enabled.grid(row=0, column=0, columnspan=2, sticky="w", pady=1)
        in_global_var = tk.BooleanVar(value=bool(sapling_values["in_global_pool"]))
        in_global = ttk.Checkbutton(
            saplings,
            text=custom_section_text("tree_saplings_global_pool", language),
            variable=in_global_var,
            command=lambda: self._custom_section_changed(("trees", "saplings", "in_global_pool"), in_global_var.get()),
        )
        in_global.grid(row=1, column=0, columnspan=2, sticky="w", pady=1)
        global_share_widget = add_spin(
            saplings,
            2,
            custom_section_text("tree_saplings_global_share", language),
            ("trees", "saplings", "global_share_percent"),
            sapling_values["global_share_percent"],
            0,
            100,
            1,
            custom_section_text("percent_unit", language),
            column=0,
        )
        sapling_quota_widget = add_spin(
            saplings,
            2,
            custom_section_text("tree_saplings_separate_quota", language),
            ("trees", "saplings", "quota_percent"),
            sapling_values["quota_percent"],
            SEMANTIC_DENSITY_MIN,
            SEMANTIC_DENSITY_MAX,
            1,
            custom_section_text("percent_unit", language),
            column=1,
        )
        placement_labels = {key: custom_section_text(f"tree_placement_{key}", language) for key in TREE_PLACEMENTS}
        placement_var = tk.StringVar(value=placement_labels.get(sapling_values["placement"], placement_labels["everywhere"]))
        placement_combo = ttk.Combobox(
            saplings,
            textvariable=placement_var,
            values=[placement_labels[key] for key in TREE_PLACEMENTS],
            state="readonly",
            width=20,
        )
        ttk.Label(saplings, text=custom_section_text("tree_saplings_placement", language)).grid(
            row=3, column=0, sticky="w", padx=(0, 8), pady=1
        )
        placement_combo.grid(row=3, column=1, sticky="w", pady=1)
        placement_combo.bind(
            "<<ComboboxSelected>>",
            lambda event: self._custom_section_changed(
                ("trees", "saplings", "placement"),
                next(key for key, label in placement_labels.items() if label == placement_var.get()),
            ),
        )

        def refresh_sapling_controls(*_args):
            enabled = bool(saplings_enabled_var.get())
            in_global_pool = bool(in_global_var.get())
            in_global.configure(state="normal" if enabled else "disabled")
            global_share_widget.configure(state="normal" if enabled and in_global_pool else "disabled")
            sapling_quota_widget.configure(state="normal" if enabled and not in_global_pool else "disabled")
            placement_combo.configure(state="readonly" if enabled else "disabled")

        saplings_enabled_var.trace_add("write", refresh_sapling_controls)
        in_global_var.trace_add("write", refresh_sapling_controls)
        refresh_sapling_controls()

        forests = ttk.LabelFrame(trees, text=custom_section_text("tree_forests", language), padding=6)
        forests.grid(row=2, column=0, columnspan=2, sticky="nw", pady=(0, 6))
        forests.columnconfigure(0, weight=0)
        forests.columnconfigure(1, weight=0)
        forests_enabled_var = tk.BooleanVar(value=bool(forest_values["enabled"]))
        forests_enabled = ttk.Checkbutton(
            forests,
            text=custom_section_text("tree_forests_enabled", language),
            variable=forests_enabled_var,
            command=lambda: self._custom_section_changed(("trees", "forests", "enabled"), forests_enabled_var.get()),
        )
        forests_enabled.grid(row=0, column=0, columnspan=2, sticky="w", pady=1)
        forest_share_widget = add_spin(
            forests,
            1,
            custom_section_text("tree_forest_share", language),
            ("trees", "forests", "share_percent"),
            forest_values["share_percent"],
            0,
            100,
            1,
            custom_section_text("percent_unit", language),
            column=0,
        )
        forest_average_widget = add_spin(
            forests,
            1,
            custom_section_text("tree_forest_average", language),
            ("trees", "forests", "trees_per_forest"),
            forest_values["trees_per_forest"],
            FOREST_TREE_COUNT_MIN,
            FOREST_TREE_COUNT_MAX,
            0.1,
            custom_section_text("trees_unit", language),
            column=1,
        )
        forest_variation_widget = add_spin(
            forests,
            2,
            custom_section_text("tree_forest_variation", language),
            ("trees", "forests", "tree_count_variation_percent"),
            forest_values["tree_count_variation_percent"],
            FOREST_TREE_VARIATION_MIN,
            FOREST_TREE_VARIATION_MAX,
            1,
            custom_section_text("percent_unit", language),
            column=0,
        )
        ttk.Label(trees, text=custom_section_text("tree_hint", language), style="Hint.TLabel", wraplength=620).grid(
            row=3, column=0, columnspan=2, sticky="w", pady=(5, 0)
        )

        def refresh_forest_controls(*_args):
            enabled = bool(forests_enabled_var.get())
            state = "normal" if enabled else "disabled"
            forest_share_widget.configure(state=state)
            forest_average_widget.configure(state=state)
            forest_variation_widget.configure(state=state)

        forests_enabled_var.trace_add("write", refresh_forest_controls)
        refresh_forest_controls()

        building_stones = ttk.LabelFrame(
            sections_frame,
            text=custom_section_text("building_stones", language),
            padding=8,
        )
        building_stones.grid(row=6, column=0, sticky="ew")
        building_stones.columnconfigure(0, weight=0)
        building_stones.columnconfigure(1, weight=0)
        stone_values = sections["building_stones"]
        stone_group_values = stone_values["groups"]
        stone_grid = ttk.Frame(building_stones)
        stone_grid.grid(row=0, column=0, columnspan=2, sticky="nw")
        stone_grid.columnconfigure(0, weight=0)
        stone_grid.columnconfigure(1, weight=0)
        add_spin(
            stone_grid,
            0,
            custom_section_text("building_stone_anchor_density", language),
            ("building_stones", "anchor_density_percent"),
            stone_values["anchor_density_percent"],
            SEMANTIC_DENSITY_MIN,
            SEMANTIC_DENSITY_MAX,
            1,
            custom_section_text("percent_unit", language),
            column=0,
        )
        add_spin(
            stone_grid,
            0,
            custom_section_text("building_stone_average", language),
            ("building_stones", "average_quantity"),
            stone_values["average_quantity"],
            STONE_QUANTITY_MINIMUM,
            STONE_QUANTITY_MAXIMUM,
            STONE_QUANTITY_STEP,
            custom_section_text("stone_unit", language),
            column=1,
        )
        groups = ttk.LabelFrame(building_stones, text=custom_section_text("building_stone_groups", language), padding=6)
        groups.grid(row=1, column=0, columnspan=2, sticky="nw", pady=(6, 0))
        groups.columnconfigure(0, weight=0)
        groups.columnconfigure(1, weight=0)
        stone_groups_var = tk.BooleanVar(value=bool(stone_group_values["enabled"]))
        ttk.Checkbutton(
            groups,
            text=custom_section_text("building_stone_groups_enabled", language),
            variable=stone_groups_var,
            command=lambda: self._custom_section_changed(
                ("building_stones", "groups", "enabled"), stone_groups_var.get()
            ),
        ).grid(row=0, column=0, columnspan=2, sticky="w", pady=1)
        stone_share_widget = add_spin(
            groups,
            1,
            custom_section_text("building_stone_group_share", language),
            ("building_stones", "groups", "share_percent"),
            stone_group_values["share_percent"],
            0,
            100,
            1,
            custom_section_text("percent_unit", language),
            column=0,
        )
        stone_group_average_widget = add_spin(
            groups,
            1,
            custom_section_text("building_stone_group_average", language),
            ("building_stones", "groups", "stones_per_group"),
            stone_group_values["stones_per_group"],
            STONE_GROUP_COUNT_MIN,
            STONE_GROUP_COUNT_MAX,
            0.1,
            custom_section_text("stones_unit", language),
            column=1,
        )
        stone_group_variation_widget = add_spin(
            groups,
            2,
            custom_section_text("building_stone_group_variation", language),
            ("building_stones", "groups", "stone_count_variation_percent"),
            stone_group_values["stone_count_variation_percent"],
            STONE_GROUP_VARIATION_MIN,
            STONE_GROUP_VARIATION_MAX,
            1,
            custom_section_text("percent_unit", language),
            column=0,
        )
        def refresh_stone_controls(*_args):
            state = "normal" if stone_groups_var.get() else "disabled"
            stone_share_widget.configure(state=state)
            stone_group_average_widget.configure(state=state)
            stone_group_variation_widget.configure(state=state)

        stone_groups_var.trace_add("write", refresh_stone_controls)
        refresh_stone_controls()
        ttk.Label(
            building_stones,
            text=custom_section_text("building_stone_hint", language),
            style="Hint.TLabel",
            wraplength=620,
        ).grid(row=2, column=0, columnspan=2, sticky="w", pady=(5, 0))

        decorations = ttk.LabelFrame(
            sections_frame,
            text=custom_section_text("decorations", language),
            padding=8,
        )
        decorations.grid(row=7, column=0, sticky="ew", pady=(8, 0))
        decorations.columnconfigure(0, weight=0)
        decorations.columnconfigure(1, weight=0)
        decoration_grid = ttk.Frame(decorations)
        decoration_grid.grid(row=1, column=0, columnspan=2, sticky="nw")
        decoration_grid.columnconfigure(0, weight=0)
        decoration_grid.columnconfigure(1, weight=0)
        self._custom_decoration_icon_slots = {}
        self._custom_decoration_rate_vars = {}
        self._custom_decoration_rate_widgets = {}
        decoration_values = sections["decorations"]
        object_values = sections.get("objects", {})
        grass_object_var = tk.BooleanVar(value=bool(
            object_values.get("grass_compatible_on_dry_and_details", False)
            if isinstance(object_values, dict) else False
        ))
        ttk.Checkbutton(
            decorations,
            text=custom_section_text("objects_grass_compatible", language),
            variable=grass_object_var,
            command=lambda: self._custom_section_changed(
                ("objects", "grass_compatible_on_dry_and_details"),
                grass_object_var.get(),
            ),
        ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 4))
        for index, family_key in enumerate(DECORATION_FAMILY_KEYS):
            add_decoration_spin(
                decoration_grid,
                index // 2,
                custom_section_text(f"decoration_{family_key}", language),
                ("decorations", family_key),
                decoration_values[family_key],
                DECORATION_RATE_MIN,
                DECORATION_RATE_MAX,
                1,
                custom_section_text("percent_unit", language),
                column=index % 2,
            )

        def refresh_terrain_dependencies(*_args):
            current = self._custom_config.semantic_sections() if self._custom_config is not None else sections
            current_terrain_values = current.get("terrains", {})
            for key in TERRAIN_FAMILY_KEYS:
                entry = current_terrain_values.get(key, {})
                enabled = bool(entry.get("enabled", True))
                terrain_rate_vars[key].set(
                    _display_number(entry.get("rate_percent", 100.0)) if enabled else "0"
                )
                terrain_rate_widgets[key].configure(
                    state="normal" if enabled else "disabled",
                    from_=TERRAIN_ENABLED_RATE_MIN if enabled else TERRAIN_RATE_MIN,
                )

            effective_rates = {
                key: float(current_terrain_values.get(key, {}).get("rate_percent", 100.0))
                if bool(current_terrain_values.get(key, {}).get("enabled", True))
                else 0.0
                for key in TERRAIN_FAMILY_KEYS
            }
            dependency_keys = {
                "desert": ("cacti", "dead_trees", "skeletons"),
                "swamp": ("reeds",),
            }
            current_decorations = current.get("decorations", {})
            for terrain_key, decoration_keys in dependency_keys.items():
                active = effective_rates.get(terrain_key, 0.0) > 0.0
                for decoration_key in decoration_keys:
                    widget = self._custom_decoration_rate_widgets.get(decoration_key)
                    variable = self._custom_decoration_rate_vars.get(decoration_key)
                    if widget is None or variable is None:
                        continue
                    widget.configure(state="normal" if active else "disabled")
                    variable.set(
                        _display_number(current_decorations.get(decoration_key, 100.0))
                        if active else "0"
                    )

        self._custom_refresh_terrain_dependencies = refresh_terrain_dependencies
        refresh_terrain_dependencies()
        ttk.Label(
            decorations,
            text=custom_section_text("decoration_hint", language),
            style="Hint.TLabel",
            wraplength=620,
        ).grid(row=2, column=0, columnspan=2, sticky="w", pady=(5, 0))

        # Start-bonus values are deliberately kept in a dedicated semantic
        # section.  Each panel starts with its own on/off switch; quantities
        # therefore never need a zero sentinel to disable a package.
        start_bonus = ttk.LabelFrame(
            sections_frame,
            text=custom_section_text("start_bonus", language),
            padding=8,
        )
        start_bonus.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        start_bonus.columnconfigure(0, weight=0)
        start_bonus.columnconfigure(1, weight=0)
        start_values = sections["start_bonus"]

        def register_start_control(package_key, widget):
            self._custom_start_bonus_control_widgets.setdefault(package_key, []).append(widget)
            return widget

        def add_start_spin(*args, package_key, **kwargs):
            return register_start_control(package_key, add_spin(*args, **kwargs))

        def add_start_switch(parent, package_key, *, row=0, column=0, columnspan=1):
            variable = self._custom_package_vars[package_key]
            check = ttk.Checkbutton(
                parent,
                text=custom_section_text("start_bonus_enabled", language),
                variable=variable,
                command=lambda key=package_key, value=variable: self._custom_package_changed(key, value),
                state="normal" if next(
                    spec for spec in START_PACKAGE_CATALOG if spec.key == package_key
                ).implemented else "disabled",
            )
            check.grid(row=row, column=column, columnspan=columnspan, sticky="w", pady=(0, 4))
            return check

        add_spin(
            start_bonus,
            0,
            custom_section_text("start_bonus_distance", language),
            ("start_bonus", "distance_from_border"),
            start_values["distance_from_border"],
            START_BONUS_DISTANCE_MIN,
            START_BONUS_DISTANCE_MAX,
            1,
            "HEX6",
        )
        force_extended_var = tk.BooleanVar(
            value=bool(start_values.get("force_extended_radius", False))
        )
        ttk.Checkbutton(
            start_bonus,
            text=custom_section_text("start_bonus_force_extended", language),
            variable=force_extended_var,
            command=lambda: self._custom_section_changed(
                ("start_bonus", "force_extended_radius"),
                force_extended_var.get(),
            ),
        ).grid(row=1, column=0, columnspan=2, sticky="w", pady=(0, 3))
        # Distance is common to all five packages, so it stays editable even
        # when a particular package is disabled.
        ttk.Label(
            start_bonus,
            text=custom_section_text("start_bonus_hint", language),
            style="Hint.TLabel",
            wraplength=720,
            justify="left",
        ).grid(row=2, column=0, columnspan=2, sticky="w", pady=(3, 7))

        forest_bonus = ttk.LabelFrame(
            start_bonus,
            text=custom_section_text("start_bonus_forest", language),
            padding=6,
        )
        forest_bonus.grid(row=3, column=0, sticky="nw", padx=(0, 6), pady=(0, 7))
        forest_bonus.columnconfigure(0, weight=0)
        forest_values = start_values["forest"]
        add_start_switch(forest_bonus, "start_forest")
        add_start_spin(
            forest_bonus,
            1,
            custom_section_text("start_bonus_adult_trees", language),
            ("start_bonus", "forest", "adult_trees_per_player"),
            forest_values["adult_trees_per_player"],
            START_FOREST_COUNT_MIN,
            START_FOREST_COUNT_MAX,
            1,
            custom_section_text("trees_unit", language),
            package_key="start_forest",
        )
        add_start_spin(
            forest_bonus,
            2,
            custom_section_text("start_bonus_saplings", language),
            ("start_bonus", "forest", "saplings_per_player"),
            forest_values["saplings_per_player"],
            START_FOREST_COUNT_MIN,
            START_FOREST_COUNT_MAX,
            1,
            custom_section_text("trees_unit", language),
            package_key="start_forest",
        )
        ttk.Label(
            forest_bonus,
            text=custom_section_text("start_bonus_forest_radius_derived", language),
            style="Hint.TLabel",
            wraplength=360,
            justify="left",
        ).grid(row=3, column=0, sticky="w", pady=(3, 0))

        stone_bonus = ttk.LabelFrame(
            start_bonus,
            text=custom_section_text("start_bonus_stones", language),
            padding=6,
        )
        stone_bonus.grid(row=3, column=1, sticky="nw", padx=(6, 0), pady=(0, 7))
        stone_values = start_values["building_stones"]
        add_start_switch(stone_bonus, "start_building_stones")
        stone_anchor_var = tk.StringVar(value=_display_number(stone_values["anchors_per_player"]))
        stone_average_var = tk.StringVar(value=_display_number(stone_values["average_quantity"]))
        add_start_spin(
            stone_bonus,
            1,
            custom_section_text("start_bonus_anchors", language),
            ("start_bonus", "building_stones", "anchors_per_player"),
            stone_values["anchors_per_player"],
            START_STONE_ANCHOR_MIN,
            START_STONE_ANCHOR_MAX,
            1,
            custom_section_text("stones_unit", language),
            package_key="start_building_stones",
            variable=stone_anchor_var,
        )
        add_start_spin(
            stone_bonus,
            2,
            custom_section_text("start_bonus_average_quantity", language),
            ("start_bonus", "building_stones", "average_quantity"),
            stone_values["average_quantity"],
            STONE_QUANTITY_MINIMUM,
            STONE_QUANTITY_MAXIMUM,
            STONE_QUANTITY_STEP,
            custom_section_text("stone_unit", language),
            package_key="start_building_stones",
            variable=stone_average_var,
        )
        stock_preview_var = tk.StringVar(value="")

        def refresh_start_stock_preview(*_args):
            try:
                anchors = float(stone_anchor_var.get())
                average = float(stone_average_var.get())
                stock = int(anchors * average + 0.5)
            except (TypeError, ValueError):
                stock = int(stone_values.get("stock_units_per_player", 150))
            stock_preview_var.set(custom_section_text("start_bonus_stock_preview", language, value=stock))

        stone_anchor_var.trace_add("write", refresh_start_stock_preview)
        stone_average_var.trace_add("write", refresh_start_stock_preview)
        ttk.Label(stone_bonus, textvariable=stock_preview_var, style="Hint.TLabel").grid(
            row=3, column=0, sticky="w", pady=(3, 0)
        )
        ttk.Label(
            stone_bonus,
            text=custom_section_text("start_bonus_native_shape", language),
            style="Hint.TLabel",
        ).grid(row=4, column=0, sticky="w", pady=(2, 0))
        refresh_start_stock_preview()

        swamp_bonus = ttk.LabelFrame(
            start_bonus,
            text=custom_section_text("start_bonus_swamp", language),
            padding=6,
        )
        swamp_bonus.grid(row=4, column=0, sticky="nw", padx=(0, 6), pady=(0, 7))
        swamp_values = start_values["mini_swamp"]
        add_start_switch(swamp_bonus, "start_mini_swamp")
        swamp_shape_labels = {
            key: custom_section_text(f"start_bonus_swamp_shape_{key}", language)
            for key in START_SWAMP_SHAPES
        }
        swamp_shape_var = tk.StringVar(
            value=swamp_shape_labels.get(
                swamp_values.get("shape", "native"),
                swamp_shape_labels["native"],
            )
        )
        swamp_shape_line = ttk.Frame(swamp_bonus)
        swamp_shape_line.grid(row=1, column=0, columnspan=2, sticky="w", pady=1)
        swamp_shape_combo = ttk.Combobox(
            swamp_shape_line,
            textvariable=swamp_shape_var,
            values=[swamp_shape_labels[key] for key in START_SWAMP_SHAPES],
            state="readonly",
            width=22,
        )
        ttk.Label(
            swamp_shape_line,
            text=custom_section_text("start_bonus_swamp_shape", language),
        ).grid(row=0, column=0, sticky="w")
        swamp_shape_combo.grid(row=0, column=1, sticky="w", padx=(4, 0))
        swamp_shape_combo.bind(
            "<<ComboboxSelected>>",
            lambda event: self._custom_section_changed(
                ("start_bonus", "mini_swamp", "shape"),
                next(
                    key for key, label in swamp_shape_labels.items()
                    if label == swamp_shape_var.get()
                ),
            ),
        )
        register_start_control("start_mini_swamp", swamp_shape_combo)
        add_start_spin(
            swamp_bonus,
            2,
            custom_section_text("start_bonus_swamp_radius", language),
            ("start_bonus", "mini_swamp", "radius"),
            swamp_values["radius"],
            START_SWAMP_RADIUS_MIN,
            START_SWAMP_RADIUS_MAX,
            1,
            "HEX6",
            package_key="start_mini_swamp",
        )
        ttk.Label(
            swamp_bonus,
            text=custom_section_text("start_bonus_swamp_derived", language),
            style="Hint.TLabel",
            wraplength=360,
            justify="left",
        ).grid(row=3, column=0, columnspan=2, sticky="w", pady=(3, 0))

        rocky_bonus = ttk.LabelFrame(
            start_bonus,
            text=custom_section_text("start_bonus_rocky", language),
            padding=5,
        )
        rocky_bonus.grid(row=4, column=1, sticky="nw", padx=(6, 0), pady=(0, 7))
        for column in range(4):
            rocky_bonus.columnconfigure(column, weight=0)
        rocky_values = start_values["rocky_minerals"]
        add_start_switch(rocky_bonus, "start_rocky_minerals", columnspan=4)
        shape_labels = {
            key: custom_section_text(f"start_bonus_rocky_shape_{key}", language)
            for key in START_ROCKY_SHAPES
        }
        shape_var = tk.StringVar(
            value=shape_labels.get(rocky_values.get("shape", "hexagon"), shape_labels["hexagon"])
        )
        ttk.Label(
            rocky_bonus,
            text=custom_section_text("start_bonus_rocky_shape", language),
        ).grid(row=1, column=0, sticky="w", pady=1)
        shape_combo = ttk.Combobox(
            rocky_bonus,
            textvariable=shape_var,
            values=[shape_labels[key] for key in START_ROCKY_SHAPES],
            state="readonly",
            width=13,
        )
        shape_combo.grid(row=1, column=1, sticky="w", padx=(4, 9), pady=1)
        shape_combo.bind(
            "<<ComboboxSelected>>",
            lambda event: self._custom_section_changed(
                ("start_bonus", "rocky_minerals", "shape"),
                next(key for key, label in shape_labels.items() if label == shape_var.get()),
            ),
        )
        register_start_control("start_rocky_minerals", shape_combo)
        mode_labels = {
            key: custom_section_text(f"start_bonus_rocky_surface_{key}", language)
            for key in START_ROCKY_SURFACE_MODES
        }
        mode_var = tk.StringVar(
            value=mode_labels.get(rocky_values.get("surface_mode", "equal"), mode_labels["equal"])
        )
        ttk.Label(
            rocky_bonus,
            text=custom_section_text("start_bonus_rocky_surface", language),
        ).grid(row=2, column=0, sticky="w", pady=1)
        mode_combo = ttk.Combobox(
            rocky_bonus,
            textvariable=mode_var,
            values=[mode_labels[key] for key in START_ROCKY_SURFACE_MODES],
            state="readonly",
            width=13,
        )
        mode_combo.grid(row=2, column=1, sticky="w", padx=(4, 9), pady=1)
        mode_combo.bind(
            "<<ComboboxSelected>>",
            lambda event: self._custom_section_changed(
                ("start_bonus", "rocky_minerals", "surface_mode"),
                next(key for key, label in mode_labels.items() if label == mode_var.get()),
            ),
        )
        register_start_control("start_rocky_minerals", mode_combo)

        rocky_cells_unit = custom_section_text("cells_unit", language)

        def rocky_max_text(value, unit=""):
            shown = _display_number(value)
            if unit:
                shown = f"{shown} {unit}"
            return custom_section_text("max_value", language, value=shown)

        def add_rocky_spin(
            row,
            column,
            path,
            value,
            low,
            high,
            increment=1,
            *,
            unit="",
            maximum_var=None,
        ):
            """Add a compact input with its unit and maximum beside it."""

            variable = tk.StringVar(value=_display_number(value))
            line = ttk.Frame(rocky_bonus)
            line.grid(row=row, column=column, sticky="w", padx=(3, 4), pady=1)
            widget = ttk.Spinbox(
                line,
                from_=low,
                to=high,
                increment=increment,
                textvariable=variable,
                width=7,
                command=lambda p=path, v=variable: self._custom_section_changed(p, v.get()),
            )
            widget.grid(row=0, column=0, sticky="w")
            next_column = 1
            if unit:
                ttk.Label(line, text=unit, style="Hint.TLabel").grid(
                    row=0, column=next_column, sticky="w", padx=(3, 5)
                )
                next_column += 1
            max_label = ttk.Label(line, style="Hint.TLabel")
            if maximum_var is None:
                max_label.configure(text=rocky_max_text(high, unit))
            else:
                max_label.configure(textvariable=maximum_var)
            max_label.grid(row=0, column=next_column, sticky="w")
            bind_text(widget, path, variable)
            self._custom_section_vars[".".join(path)] = variable
            register_start_control("start_rocky_minerals", widget)
            return widget

        ttk.Label(
            rocky_bonus,
            text=custom_section_text("start_bonus_rocky_radius", language),
        ).grid(row=3, column=0, sticky="w", pady=1)
        radius_var = None
        radius_widget = add_rocky_spin(
            3,
            1,
            ("start_bonus", "rocky_minerals", "radius_min"),
            rocky_values["radius_min"],
            START_BONUS_RADIUS_MIN,
            START_ROCKY_RADIUS_MAX,
            unit="HEX6",
        )

        ttk.Label(
            rocky_bonus,
            text=custom_section_text("start_bonus_rocky_total_surface", language),
        ).grid(row=4, column=0, sticky="w", pady=1)
        total_max_var = tk.StringVar(value=rocky_max_text(rocky_total_cells_max(3), rocky_cells_unit))
        total_widget = add_rocky_spin(
            4,
            1,
            ("start_bonus", "rocky_minerals", "total_core_cells"),
            rocky_values.get("total_core_cells", 183),
            START_ROCKY_CORE_CELLS_MIN,
            rocky_total_cells_max(3),
            unit=rocky_cells_unit,
            maximum_var=total_max_var,
        )

        ttk.Label(
            rocky_bonus,
            text=custom_section_text("start_bonus_rocky_family_header", language),
            style="Hint.TLabel",
        ).grid(row=5, column=0, sticky="w", pady=(1, 0))
        ttk.Label(
            rocky_bonus,
            text=custom_section_text("start_bonus_rocky_core_header", language),
            style="Hint.TLabel",
        ).grid(row=5, column=1, sticky="w", padx=(4, 0), pady=(1, 0))
        ttk.Label(
            rocky_bonus,
            text=custom_section_text("start_bonus_rocky_quantity_header", language),
            style="Hint.TLabel",
        ).grid(row=5, column=2, columnspan=2, sticky="w", padx=(4, 0), pady=(1, 0))

        family_vars = {}
        rocky_core_widgets = {}
        rocky_quantity_widgets = {}
        rocky_core_vars = {}
        family_icon_widgets = {}
        for index, family in enumerate(("coal", "iron", "gold")):
            row = 6 + index
            family_values = rocky_values[family]
            family_var = tk.BooleanVar(value=bool(family_values["enabled"]))
            family_vars[family] = family_var
            family_check = ttk.Checkbutton(
                rocky_bonus,
                text=custom_section_text(f"start_bonus_{family}", language),
                image=self._custom_mineral_icons[family],
                compound="left",
                variable=family_var,
                command=lambda f=family, v=family_var: self._custom_section_changed(
                    ("start_bonus", "rocky_minerals", f, "enabled"), v.get()
                ),
            )
            family_check.grid(row=row, column=0, sticky="w", pady=1)
            register_start_control("start_rocky_minerals", family_check)
            family_icon_widgets[family] = family_check
            self._custom_mineral_icon_buttons.setdefault(family, []).append(family_check)
            rocky_core_widgets[family] = add_rocky_spin(
                row,
                1,
                ("start_bonus", "rocky_minerals", family, "core_cells"),
                family_values.get("core_cells", 61),
                START_ROCKY_CORE_CELLS_MIN,
                START_ROCKY_CORE_CELLS_MAX,
                unit=rocky_cells_unit,
            )
            rocky_core_vars[family] = self._custom_section_vars[
                f"start_bonus.rocky_minerals.{family}.core_cells"
            ]
            rocky_quantity_widgets[family] = add_rocky_spin(
                row,
                2,
                ("start_bonus", "rocky_minerals", family, "average_quantity"),
                family_values.get("average_quantity", 10),
                RESOURCE_MINIMUM,
                RESOURCE_MAXIMUM,
                maximum_var=None,
            )

        def rocky_mode_key():
            return next(
                (key for key, label in mode_labels.items() if label == mode_var.get()),
                "equal",
            )

        rocky_total_var = self._custom_section_vars[
            "start_bonus.rocky_minerals.total_core_cells"
        ]
        rocky_radius_var = self._custom_section_vars[
            "start_bonus.rocky_minerals.radius_min"
        ]
        refreshing_rocky = False
        last_rocky_mode = rocky_mode_key()

        # Keep one shared snapshot for the panel.  The visible values are the
        # source of truth while it is open: changing a radius or total derives
        # the other cells, and switching modes carries that exact update into
        # the next allocation mode instead of restoring an older profile.
        rocky_state = {}

        def _number_var(variable, default=0):
            try:
                return int(round(float(variable.get())))
            except (TypeError, ValueError):
                return int(default)

        def _read_rocky_state():
            return {
                "radius": _number_var(rocky_radius_var, 4),
                "total": _number_var(rocky_total_var, 0),
                "cores": {
                    family: _number_var(rocky_core_vars[family], 0)
                    for family in family_vars
                },
            }

        def _capture_rocky_state():
            rocky_state.clear()
            rocky_state.update(_read_rocky_state())

        _capture_rocky_state()

        def _share_value(family):
            variable = share_vars.get(family)
            try:
                return float(variable.get()) if variable is not None else 0.0
            except (TypeError, ValueError):
                return 0.0

        def materialize_rocky_state(sections):
            """Copy the values currently visible in the rocky panel into sections."""

            try:
                start_bonus = sections.setdefault("start_bonus", {})
                rocky = start_bonus.setdefault("rocky_minerals", {})
                state = rocky_state or _read_rocky_state()
                radius = max(
                    START_BONUS_RADIUS_MIN,
                    min(START_ROCKY_RADIUS_MAX, int(state.get("radius", 4))),
                )
                rocky["radius"] = radius
                rocky["radius_min"] = radius
                rocky["radius_max"] = radius
                rocky["total_core_cells"] = max(0, int(state.get("total", 0)))
                cores = state.get("cores", {})
                for family in family_vars:
                    entry = rocky.setdefault(family, {})
                    entry["core_cells"] = max(0, int(cores.get(family, 0)))
            except (AttributeError, TypeError, ValueError):
                # A language switch or a complete tab rebuild can briefly
                # leave the callback without live Tk variables.  The normal
                # section path remains valid in that narrow transition.
                return sections
            return sections

        def refresh_mineral_icon_states(*_args):
            package_var = self._custom_package_vars.get("start_rocky_minerals")
            package_enabled = bool(package_var.get()) if package_var is not None else True
            for key, widgets in self._custom_mineral_icon_widgets.items():
                # In the global mineral controls a zero share is the explicit
                # disabled state; quantity rows follow the same visual cue.
                image = (
                    self._custom_mineral_icons[key]
                    if _share_value(key) > 0
                    else self._custom_mineral_disabled_icons[key]
                )
                for widget in widgets:
                    try:
                        widget.configure(image=image)
                    except tk.TclError:
                        pass
            for family, widget in family_icon_widgets.items():
                active = package_enabled and bool(family_vars[family].get())
                image = (
                    self._custom_mineral_icons[family]
                    if active
                    else self._custom_mineral_disabled_icons[family]
                )
                try:
                    widget.configure(image=image)
                except tk.TclError:
                    pass

        def refresh_rocky_controls(*_args):
            nonlocal last_rocky_mode, refreshing_rocky
            if refreshing_rocky:
                return
            refreshing_rocky = True
            try:
                package_var = self._custom_package_vars.get("start_rocky_minerals")
                package_enabled = bool(package_var.get()) if package_var is not None else True
                mode = rocky_mode_key()
                mode_changed = mode != last_rocky_mode
                # The trace fires after a field or selector changes.  Capture
                # the complete visible state before deriving the next mode so
                # radius/total/core edits survive a repartition switch.
                _capture_rocky_state()
                active = tuple(family for family, variable in family_vars.items() if bool(variable.get()))
                active_count = len(active)
                total_max = rocky_total_cells_max(active_count)
                total_widget.configure(to=total_max)
                total_max_var.set(rocky_max_text(total_max, rocky_cells_unit))
                radius_state = "normal" if package_enabled and mode == "equal" and active_count else "disabled"
                total_state = "normal" if package_enabled and mode == "proportional" and active_count else "disabled"
                custom_state = "normal" if package_enabled and mode == "custom" else "disabled"
                radius_widget.configure(state=radius_state)
                total_widget.configure(state=total_state)

                if mode == "equal":
                    radius = max(
                        START_BONUS_RADIUS_MIN,
                        min(
                            START_ROCKY_RADIUS_MAX,
                            _number_var(rocky_radius_var, rocky_state.get("radius", 4)),
                        ),
                    )
                    equal_area = rocky_equal_core_cells(radius)
                    rocky_radius_var.set(_display_number(radius))
                    for family in active:
                        rocky_core_vars[family].set(_display_number(equal_area))
                    rocky_total_var.set(_display_number(equal_area * active_count))
                elif mode == "proportional" and active:
                    requested_total = _number_var(
                        rocky_total_var,
                        int(rocky_state.get("total", active_count * rocky_equal_core_cells(4))),
                    )
                    requested_total = max(
                        active_count * START_ROCKY_CORE_CELLS_MIN,
                        min(total_max, requested_total),
                    )
                    radius = rocky_equivalent_radius(
                        requested_total,
                        active_count,
                        rocky_state.get("radius", 4),
                    )
                    rocky_radius_var.set(_display_number(radius))
                    rocky_total_var.set(_display_number(requested_total))
                    targets = rocky_proportional_targets(
                        requested_total,
                        active,
                        {family: _share_value(family) for family in active},
                    )
                    for family in active:
                        rocky_core_vars[family].set(_display_number(targets.get(family, 0)))
                elif mode == "custom" and active:
                    if mode_changed:
                        for family in active:
                            rocky_core_vars[family].set(
                                _display_number(
                                    max(
                                        START_ROCKY_CORE_CELLS_MIN,
                                        int(rocky_state.get("cores", {}).get(family, 1)),
                                    )
                                )
                            )
                    total = 0
                    for family in active:
                        try:
                            total += int(round(float(rocky_core_vars[family].get())))
                        except (TypeError, ValueError):
                            pass
                    total = max(0, total)
                    radius = rocky_equivalent_radius(
                        total,
                        active_count,
                        rocky_state.get("radius", 4),
                    )
                    rocky_radius_var.set(_display_number(radius))
                    rocky_total_var.set(_display_number(total))
                elif not active:
                    rocky_total_var.set("0")

                for family, variable in family_vars.items():
                    enabled = bool(variable.get())
                    rocky_core_widgets[family].configure(
                        state=custom_state if enabled else "disabled"
                    )
                    rocky_quantity_widgets[family].configure(
                        state="normal" if package_enabled and enabled else "disabled"
                    )
                refresh_mineral_icon_states()
                _capture_rocky_state()
                last_rocky_mode = mode
            finally:
                refreshing_rocky = False

        mode_var.trace_add("write", refresh_rocky_controls)
        rocky_radius_var.trace_add("write", refresh_rocky_controls)
        rocky_total_var.trace_add("write", refresh_rocky_controls)
        for family_var in family_vars.values():
            family_var.trace_add("write", refresh_rocky_controls)
        for variable in share_vars.values():
            variable.trace_add("write", refresh_rocky_controls)
        self._custom_materialize_rocky_state = materialize_rocky_state
        self._custom_refresh_rocky_controls = refresh_rocky_controls
        refresh_rocky_controls()

        lake_bonus = ttk.LabelFrame(
            start_bonus,
            text=custom_section_text("start_bonus_lake", language),
            padding=5,
        )
        lake_bonus.grid(row=5, column=0, columnspan=2, sticky="ew", pady=(0, 0))
        for column in range(2):
            lake_bonus.columnconfigure(column, weight=0)
        lake_values = start_values["lake_fish_river"]
        add_start_switch(lake_bonus, "start_lake_fish_river", columnspan=2)
        lake_shape_labels = {
            key: custom_section_text(f"start_bonus_lake_shape_{key}", language)
            for key in START_LAKE_SHAPES
        }
        lake_shape_var = tk.StringVar(
            value=lake_shape_labels.get(
                lake_values.get("shape", "native"),
                lake_shape_labels["native"],
            )
        )
        lake_shape_line = ttk.Frame(lake_bonus)
        lake_shape_line.grid(row=1, column=0, columnspan=2, sticky="w", pady=1)
        lake_shape_combo = ttk.Combobox(
            lake_shape_line,
            textvariable=lake_shape_var,
            values=[lake_shape_labels[key] for key in START_LAKE_SHAPES],
            state="readonly",
            width=15,
        )
        ttk.Label(
            lake_shape_line,
            text=custom_section_text("start_bonus_lake_shape", language),
        ).grid(row=0, column=0, sticky="w")
        lake_shape_combo.grid(row=0, column=1, sticky="w", padx=(4, 0))
        lake_shape_combo.bind(
            "<<ComboboxSelected>>",
            lambda event: self._custom_section_changed(
                ("start_bonus", "lake_fish_river", "shape"),
                next(
                    key for key, label in lake_shape_labels.items()
                    if label == lake_shape_var.get()
                ),
            ),
        )
        register_start_control("start_lake_fish_river", lake_shape_combo)
        add_start_spin(
            lake_bonus,
            2,
            custom_section_text("start_bonus_radius_min", language),
            ("start_bonus", "lake_fish_river", "radius_min"),
            lake_values["radius_min"],
            START_BONUS_RADIUS_MIN,
            START_BONUS_RADIUS_MAX,
            1,
            "HEX6",
            package_key="start_lake_fish_river",
            column=0,
        )
        add_start_spin(
            lake_bonus,
            3,
            custom_section_text("start_bonus_radius_max", language),
            ("start_bonus", "lake_fish_river", "radius_max"),
            lake_values["radius_max"],
            START_BONUS_RADIUS_MIN,
            START_BONUS_RADIUS_MAX,
            1,
            "HEX6",
            package_key="start_lake_fish_river",
            column=0,
        )
        add_start_spin(
            lake_bonus,
            4,
            custom_section_text("start_bonus_lake_proximity", language),
            ("start_bonus", "lake_fish_river", "water_proximity_from_territory_border"),
            lake_values["water_proximity_from_territory_border"],
            START_BONUS_WATER_PROXIMITY_MIN,
            START_BONUS_WATER_PROXIMITY_MAX,
            1,
            "HEX6",
            package_key="start_lake_fish_river",
            column=0,
        )
        add_start_spin(
            lake_bonus,
            5,
            custom_section_text("start_bonus_river_target", language),
            ("start_bonus", "lake_fish_river", "river_target_per_lake"),
            lake_values["river_target_per_lake"],
            START_BONUS_RIVER_TARGET_MIN,
            START_BONUS_RIVER_TARGET_MAX,
            1,
            custom_section_text("rivers", language),
            package_key="start_lake_fish_river",
            column=0,
        )
        add_start_spin(
            lake_bonus,
            6,
            custom_section_text("start_bonus_fish_fill", language),
            ("start_bonus", "lake_fish_river", "fish_fill_percent"),
            lake_values["fish_fill_percent"],
            START_BONUS_FISH_FILL_MIN,
            START_BONUS_FISH_FILL_MAX,
            0.1,
            custom_section_text("percent_unit", language),
            package_key="start_lake_fish_river",
            column=0,
        )
        ttk.Label(
            lake_bonus,
            text=custom_section_text("start_bonus_lake_hint", language),
            style="Hint.TLabel",
            wraplength=720,
            justify="left",
        ).grid(row=7, column=0, columnspan=2, sticky="w", pady=(3, 0))

        self._custom_refresh_start_bonus_controls()

        self._custom_render_custom_mode(config) if mode == "custom" else self._custom_provenance_var.set(
            _lang_text(
                language,
                f"Lecture du preset {MODE_LABELS['fr'][mode]} / {ARCHETYPE_LABELS['fr'][archetype]} · modifiez un champ pour créer Custom.",
                f"Viewing preset {MODE_LABELS['en'][mode]} / {ARCHETYPE_LABELS['en'][archetype]} · edit a field to create Custom.",
                f"Preset {MODE_LABELS['de'][mode]} / {ARCHETYPE_LABELS['de'][archetype]} · ändern Sie ein Feld, um Custom zu erstellen.",
                f"Viendo preset {MODE_LABELS['es'][mode]} / {ARCHETYPE_LABELS['es'][archetype]} · edite un campo para crear Custom.",
            )
        )
        self._render_custom_archetype_tab()
        self._custom_last_render_digest=config.digest
        self._custom_restore_generator_scroll_position(generator_scroll_position)

    def _custom_activate(self, config: CustomGenerationConfig):
        # A parameter edit already happens while the Custom tab exists.  Do
        # not re-run the global selection workflow in that case: it destroys
        # every editor widget, steals focus and makes the tab visibly flash.
        # The first edit from a built-in preset still needs one selection pass
        # so the mode selector and the surrounding UI enter Custom mode.
        already_custom = self._custom_current_mode() == "custom"
        self._custom_config = config
        self._custom_last_concrete_mode = config.base_mode
        self._custom_last_concrete_archetype = config.base_archetype
        language = self._custom_language()
        if not already_custom:
            self.mode.set(MODE_LABELS[language]["custom"])
            self._selection_changed()
        elif hasattr(self, "_custom_provenance_var"):
            # Refresh only the small provenance text in place.  The controls
            # themselves keep their identity, focus and pending edit.
            self._custom_render_custom_mode(config)
            self._custom_last_render_digest=config.digest
        self._custom_refresh_fish_controls()
        self._custom_status_var.set(
            _lang_text(language, "Custom actif · cache invalidé par l’empreinte.", "Custom active · cache is keyed by the fingerprint.", "Custom aktiv · Cache wird über den Fingerabdruck getrennt.", "Custom activo · la caché usa la huella.")
        )

    def _custom_package_changed(self, key: str, variable: tk.BooleanVar):
        mode = self._custom_current_mode()
        arch = self._custom_current_archetype()
        config = self._custom_ensure_config(mode if mode in ("legacy", "upgraded") else None, arch)
        materialize_rocky = getattr(self, "_custom_materialize_rocky_state", None)
        sections = config.semantic_sections()
        if callable(materialize_rocky):
            sections = materialize_rocky(sections)
        config = config.with_sections(sections)
        keys = set(config.start_packages)
        if variable.get():
            keys.add(key)
        else:
            keys.discard(key)
        ordered = [spec.key for spec in START_PACKAGE_CATALOG if spec.key in keys]
        self._custom_activate(config.with_start_packages(ordered))
        self._custom_refresh_start_bonus_controls()

    def _custom_section_changed(self, path, raw):
        """Apply one curated user-facing value and switch to Custom."""

        language = self._custom_language()
        try:
            key = str(path[-1])
            if path[:1] == ("decorations",):
                value = float(str(raw).strip())
            elif key in {
                "occupancy_percent",
                "fill_percent",
                "base_quota_percent",
                "global_share_percent",
                "quota_percent",
                "share_percent",
                "tree_count_variation_percent",
                "palm_quota_percent",
                "anchor_density_percent",
                "share_percent",
                "stone_count_variation_percent",
                "rate_percent",
            } or path[-2:] == ("shares", path[-1]):
                value = float(str(raw).strip())
            elif key == "average_quantity" and (
                path[:1] == ("building_stones",)
                or path[:3] == ("start_bonus", "building_stones", "average_quantity")
            ):
                value = float(str(raw).strip())
            elif key in {"average_quantity", "band_thickness"}:
                value = int(round(float(str(raw).strip())))
            elif key in {"trees_per_forest", "stones_per_group"}:
                value = float(str(raw).strip())
            elif key in {
                "near_shore",
                "enabled",
                "in_global_pool",
                "groups_enabled",
                "grass_compatible_on_dry_and_details",
                "force_extended_radius",
            }:
                value = bool(raw)
            else:
                value = str(raw)
            config = self._custom_ensure_config(
                self._custom_current_mode()
                if self._custom_current_mode() in ("legacy", "upgraded")
                else None,
                self._custom_current_archetype(),
            )
            fallback = default_sections(config.profile, config.base_mode)
            sections = config.semantic_sections()
            materialize_rocky = getattr(self, "_custom_materialize_rocky_state", None)
            if callable(materialize_rocky):
                sections = materialize_rocky(sections)
            sections = set_path(sections, path, value)
            if tuple(path) == ("start_bonus", "rocky_minerals", "radius_min"):
                # The equal-surface editor exposes one common radius.  Keep
                # the legacy min/max keys synchronized so a profile saved from
                # the compact panel cannot reintroduce a range on reload.
                sections = set_path(
                    sections,
                    ("start_bonus", "rocky_minerals", "radius_max"),
                    value,
                )
            sections = normalize_sections(sections, fallback=fallback)
            self._custom_activate(config.with_sections(sections))
        except (TypeError, ValueError) as exc:
            self._custom_status_var.set(
                _lang_text(language, f"Valeur invalide : {exc}", f"Invalid value: {exc}", f"Ungültiger Wert: {exc}", f"Valor no válido: {exc}")
            )

    def _custom_reset(self):
        mode = self._custom_current_mode()
        base_mode = self._custom_config.base_mode if mode == "custom" and self._custom_config else (
            mode if mode in ("legacy", "upgraded") else self._custom_last_concrete_mode
        )
        arch = self._custom_config.base_archetype if mode == "custom" and self._custom_config else self._custom_current_archetype()
        self._custom_config = self._custom_preset_config(base_mode, arch)
        self.mode.set(MODE_LABELS[self._custom_language()]["custom"])
        self._selection_changed()

    def _custom_selection_changed(self):
        mode = self._custom_current_mode()
        arch = self._custom_current_archetype()
        mode_changed = mode != self._custom_last_ui_mode
        archetype_changed = arch != self._custom_last_ui_archetype
        if mode in ("legacy", "upgraded"):
            self._custom_last_concrete_mode = mode
            self._custom_last_concrete_archetype = arch
            if (
                self._custom_config is None
                or mode_changed
                or archetype_changed
                or self._custom_config.base_mode != mode
                or self._custom_config.base_archetype != arch
            ):
                # A newly selected built-in generator is the source profile
                # displayed by the editor.  Do not leave an older Custom
                # derivative silently attached to the selector.
                self._custom_config = self._custom_preset_config(mode, arch)
        elif mode == "custom":
            config = self._custom_ensure_config()
            if config.base_archetype != arch:
                self._custom_config = CustomGenerationConfig(
                    config.base_mode,
                    arch,
                    config.profile,
                    config.start_packages,
                    config.schema_version,
                    config.sections,
                )
        self._custom_last_ui_mode = mode
        self._custom_last_ui_archetype = arch
        if mode_changed and hasattr(self, "nb"):
            try:
                self.nb.select(self._custom_generator_tab)
            except tk.TclError:
                pass
        if mode_changed or archetype_changed or self._custom_last_render_digest!=self._custom_config.digest:
            self._render_custom_parameter_tabs()

    def _custom_refresh_after_language(self):
        if hasattr(self, "_custom_generator_tab"):
            self._render_custom_parameter_tabs()

    def _render_custom_archetype_tab(self):
        root = self._custom_archetype_tab
        for child in root.winfo_children():
            child.destroy()
        root.columnconfigure(0, weight=1)
        language = self._custom_language()
        key = self._custom_current_archetype()
        spec = ARCHETYPES[key]
        labels = ARCHETYPE_LABELS.get(language, ARCHETYPE_LABELS["en"])
        ttk.Label(root, text=_lang_text(language, "Archétype", "Archetype", "Archetyp", "Arquetipo"), style="Section.TLabel").grid(row=0, column=0, sticky="w", pady=(0, 8))
        ttk.Label(
            root,
            text=_lang_text(
                language,
                f"Sélection actuelle : {labels[key]}",
                f"Current selection: {labels[key]}",
                f"Aktuelle Auswahl: {labels[key]}",
                f"Selección actual: {labels[key]}",
            ),
        ).grid(row=1, column=0, sticky="w", pady=3)
        ttk.Label(
            root,
            text=archetype_description(key, language),
            style="Hint.TLabel",
            wraplength=680,
            justify="left",
        ).grid(row=2, column=0, sticky="w", pady=(0, 12))
        contract = (
            _lang_text(
                language,
                "Continental DEV6 : masse terrestre principale admissible ; exclusion des micro-îles ; solveur exact des cellules de départ reporté à DEV7.",
                "Continental DEV6: main landmass admissible; micro-islands excluded; exact start-cell solver deferred to DEV7.",
                "Continental DEV6: zulässige Hauptlandmasse; Mikroinseln ausgeschlossen; exakter Startzellensolver auf DEV7 verschoben.",
                "Continental DEV6: masa terrestre principal admisible; microislas excluidas; el solucionador exacto de celdas iniciales queda para DEV7.",
            )
            if key == "continental"
            else _lang_text(
                language,
                "Contrat de distribution réservé : cet archétype n’est pas encore implémenté.",
                "Distribution contract reserved: this archetype is not implemented yet.",
                "Verteilungsvertrag reserviert: Dieser Archetyp ist noch nicht implementiert.",
                "Contrato de distribución reservado: este arquetipo aún no está implementado.",
            )
        )
        ttk.Label(root, text=contract, style="Hint.TLabel", wraplength=680, justify="left").grid(
            row=3, column=0, sticky="w", pady=3
        )
        ttk.Label(
            root,
            text=_lang_text(
                language,
                "Les paramètres de macro-géographie et la répartition des joueurs appartiennent à l’archétype ; le générateur exécutera le contrat.",
                "Macro-geography and player distribution belong to the archetype; the generator executes the contract.",
                "Makrogeografie und Spielerverteilung gehören zum Archetyp; die Engine führt den Vertrag aus.",
                "La macrogeografía y la distribución de jugadores pertenecen al arquetipo; el generador ejecuta el contrato.",
            ),
            style="Hint.TLabel",
            wraplength=680,
            justify="left",
        ).grid(row=4, column=0, sticky="w", pady=(12, 0))


__all__ = ("CustomGeneratorController",)
