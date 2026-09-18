"""Tk editor for declarative Custom generator profiles."""

from __future__ import annotations

import math
import tkinter as tk
from tkinter import ttk
from copy import deepcopy

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
from ..ui.widgets.icons import info_icons, mineral_icon
from .i18n import (
    archetype_description,
    custom_section_text,
    mineral_label,
    parameter_group,
    parameter_label,
)


def _read_preview_number(value, default=0.0):
    """Read either a Tk variable or a raw profile scalar for a preview."""

    try:
        raw_value = value.get() if hasattr(value, "get") else value
        return float(raw_value)
    except (AttributeError, TypeError, ValueError):
        return float(default)


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
        self._custom_section_keys = (
            "start_bonus",
            "minerals",
            "fish",
            "rivers",
            "terrains",
            "trees",
            "building_stones",
            "decorations",
        )
        saved_sections = self.prefs.get("custom_sections_expanded", {})
        self._custom_section_expanded = {
            key: bool(saved_sections.get(key, False))
            for key in self._custom_section_keys
        } if isinstance(saved_sections, dict) else {
            key: False for key in self._custom_section_keys
        }
        self._custom_start_bonus_control_widgets: dict[str, list[tk.Widget]] = {}
        self._custom_section_baseline: dict[str, object] = {}
        self._custom_status_var = tk.StringVar(value="")
        self._custom_provenance_var = tk.StringVar(value="")
        self._custom_generator_tab = self._scroll_notebook_tab("Générateur")
        # The generator owns a responsive grid.  Let its scroll surface fit
        # the viewport instead of preserving the widest one-column request;
        # otherwise the canvas keeps a horizontal natural width and the grid
        # never receives the narrow width that should trigger its reflow.
        self._custom_generator_tab._scroll_fit_width = True
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
            enabled = bool(fish.get("near_shore", False))
            widget.configure(state="normal" if enabled else "disabled")
        except tk.TclError:
            # The complete parameter tab may be between two renders.  The new
            # widget will receive its initial state when that render completes.
            pass

    def _custom_clear_preview_size_trace(self) -> None:
        """Remove the previous live preview listener before rebuilding the tab."""

        trace_id = getattr(self, "_custom_preview_size_trace", None)
        if trace_id is None or not hasattr(self, "size"):
            return
        try:
            self.size.trace_remove("write", trace_id)
        except (AttributeError, tk.TclError):
            pass
        self._custom_preview_size_trace = None

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

    def _custom_section_is_modified(self, key: str) -> bool:
        """Return whether one visible section differs from its base profile."""

        config = getattr(self, "_custom_config", None)
        if config is None:
            return False
        baseline = getattr(self, "_custom_section_baseline", None)
        if not isinstance(baseline, dict) or not baseline:
            baseline = default_sections(config.profile, config.base_mode)
        current = config.semantic_sections()
        if key == "start_bonus":
            return bool(config.start_packages) or current.get(key, {}) != baseline.get(key, {})
        if key == "decorations":
            return (
                current.get("decorations", {}) != baseline.get("decorations", {})
                or current.get("objects", {}) != baseline.get("objects", {})
            )
        return current.get(key, {}) != baseline.get(key, {})

    def _custom_refresh_section_headers(self) -> None:
        """Refresh arrows, modified markers and per-section reset actions."""

        for entry in getattr(self, "_custom_section_frames", {}).values():
            try:
                entry[3]()
            except (IndexError, tk.TclError):
                pass

    def _custom_reset_section(self, key: str) -> None:
        """Restore one editor section while preserving all other changes."""

        config = getattr(self, "_custom_config", None)
        if config is None or not self._custom_section_is_modified(key):
            return
        baseline = default_sections(config.profile, config.base_mode)
        sections = config.semantic_sections()
        if key == "decorations":
            sections["decorations"] = deepcopy(baseline.get("decorations", {}))
            sections["objects"] = deepcopy(baseline.get("objects", {}))
        elif key in sections:
            sections[key] = deepcopy(baseline.get(key, {}))
        packages = () if key == "start_bonus" else config.start_packages
        self._custom_config = config.with_sections(sections).with_start_packages(packages)
        language = self._custom_language()
        if self._custom_current_mode() != "custom":
            self.mode.set(MODE_LABELS[language]["custom"])
        self._selection_changed()

    def _render_custom_parameter_tabs(self):
        if not hasattr(self, "_custom_generator_tab"):
            return
        self._custom_clear_preview_size_trace()
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
        self._custom_section_baseline = default_sections(config.profile, config.base_mode)

        ttk.Label(root, text=_lang_text(language, "Générateur", "Generator", "Generator", "Generador"), style="Section.TLabel").grid(
            row=0, column=0, sticky="w", pady=(0, 3)
        )
        ttk.Label(root, textvariable=self._custom_provenance_var, style="Hint.TLabel", wraplength=720).grid(
            row=1, column=0, sticky="w", pady=(0, 8)
        )

        actions = ttk.Frame(root)
        actions.grid(row=2, column=0, sticky="ew", pady=(0, 9))
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
        sections_frame.grid(row=3, column=0, sticky="ew", pady=(0, 10))
        for column in range(3):
            sections_frame.columnconfigure(column, weight=0)
        self._custom_section_frames = {}
        section_order = (
            "start_bonus",
            "minerals",
            "fish",
            "rivers",
            "trees",
            "building_stones",
            "decorations",
            "terrains",
        )
        section_preferred_rows = (
            ("fish", "rivers"),
            ("trees", "building_stones"),
            # Terrains is a dense block; pair it with Decorations when the
            # viewport can carry both.  The denser block stays on the left.
            ("decorations", "terrains"),
        )
        section_layout_frames = {}
        section_layout_job = None
        section_layout_gap = 16
        section_layout_safety_margin = 32

        def section_full_width_keys(column_count):
            """Keep the two densest sections alone at every width."""

            return {"start_bonus", "minerals"}

        def section_natural_width(key):
            shell, body = section_layout_frames[key]
            # The body keeps its requested size even when the section is
            # collapsed.  Using it prevents a collapse/expand action from
            # changing the column count and moving every following section.
            return max(shell.winfo_reqwidth(), body.winfo_reqwidth())

        def section_pair_required_width(keys):
            return sum(section_natural_width(key) for key in keys) + section_layout_gap * max(
                0, len(keys) - 1
            )

        def section_pair_fits(keys, available_width):
            return (
                section_pair_required_width(keys) + section_layout_safety_margin
                <= available_width
            )

        def section_rows(column_count, available_width):
            full_width = section_full_width_keys(column_count)
            rows = [["start_bonus"], ["minerals"]]
            for pair in section_preferred_rows:
                pair_fits = (
                    column_count > 1
                    and section_pair_fits(pair, available_width)
                )
                if pair_fits:
                    rows.append(list(pair))
                else:
                    rows.extend([[key] for key in pair])
            return rows, full_width

        def section_layout_fits(column_count, available_width):
            if column_count <= 1:
                return True
            return any(
                section_pair_fits(pair, available_width)
                for pair in section_preferred_rows
            )

        def relayout_sections():
            nonlocal section_layout_job
            section_layout_job = None
            try:
                # The scroll helper may keep the content's natural request
                # wider than the viewport.  The inner tab width is the real
                # responsive constraint; use it so a narrow window can force
                # pairs back to one column.
                available_width = max(0, root.winfo_width() - 28)
            except tk.TclError:
                return
            if available_width <= 1 or len(section_layout_frames) != len(section_order):
                return

            column_count = 1
            for candidate in (2,):
                if section_layout_fits(candidate, available_width):
                    column_count = candidate
                    break

            for column in range(3):
                sections_frame.columnconfigure(column, weight=0)
            rows, full_width = section_rows(column_count, available_width)
            for row_index, row in enumerate(rows):
                if len(row) == 1 and row[0] in full_width:
                    shell = section_layout_frames[row[0]][0]
                    shell.grid_configure(
                        row=row_index,
                        column=0,
                        columnspan=column_count,
                        sticky="nw",
                        padx=0,
                    )
                    continue
                for column, key in enumerate(row):
                    section_layout_frames[key][0].grid_configure(
                        row=row_index,
                        column=column,
                        columnspan=1,
                        sticky="nw",
                        padx=(
                            0,
                            section_layout_gap if column < len(row) - 1 else 0,
                        ),
                    )

        def schedule_section_relayout(_event=None):
            nonlocal section_layout_job
            if section_layout_job is not None:
                return
            try:
                section_layout_job = sections_frame.after_idle(relayout_sections)
            except tk.TclError:
                section_layout_job = None

        sections = config.semantic_sections()
        self._custom_section_vars = {}
        self._custom_mineral_icon_widgets: dict[str, list[tk.Widget]] = {
            key: [] for key, _family in MINERAL_SPECS
        }
        self._custom_mineral_icon_buttons: dict[str, list[tk.Widget]] = {
            key: [] for key, _family in MINERAL_SPECS
        }
        self._custom_info_icons = info_icons(self)
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

        def add_tooltip(widget, text, key=None):
            """Attach a contextual tooltip to a control or its temporary marker."""

            if not text:
                return
            widget.bind(
                "<Enter>",
                lambda event, w=widget, value=text, marker=key: self._show_ui_tooltip(
                    w, value, key=marker
                ),
                add="+",
            )
            widget.bind(
                "<Leave>",
                lambda event: self._hide_ui_tooltip(),
                add="+",
            )

        def add_info(parent, row, text, *, column=2, columnspan=1, key=None, pady=2):
            """Place a 16×16 ``?`` marker with no extra horizontal gap."""

            marker = ttk.Label(parent, image=self._custom_info_icons[1], cursor="question_arrow")
            marker.grid(
                row=row,
                column=column,
                columnspan=columnspan,
                sticky="w",
                padx=0,
                pady=pady,
            )
            add_tooltip(marker, text, key=key)
            marker.bind("<Enter>", lambda event, w=marker: w.configure(image=self._custom_info_icons[2]), add="+")
            marker.bind("<Leave>", lambda event, w=marker: w.configure(image=self._custom_info_icons[1]), add="+")
            return marker

        def add_collapsible_section(key, row, title, *, pady=(0, 8)):
            """Create a compact section header and its persisted body."""

            shell = ttk.Frame(sections_frame)
            shell.grid(row=row, column=0, sticky="nw", pady=pady)
            shell.columnconfigure(0, weight=0)
            shell.columnconfigure(1, weight=0)
            body = ttk.Frame(shell, padding=8)
            body.columnconfigure(0, weight=0)
            body.columnconfigure(1, weight=0)
            header_line = ttk.Frame(shell)
            header_line.grid(row=0, column=0, columnspan=2, sticky="w")

            def refresh():
                expanded = bool(self._custom_section_expanded.get(key, False))
                arrow = "▼" if expanded else "▶"
                modified = self._custom_section_is_modified(key)
                header.configure(text=f"{arrow}  {title}")
                if modified:
                    modified_label.configure(
                        text=custom_section_text("section_modified", language)
                    )
                    modified_label.grid(row=0, column=1, sticky="w", padx=(6, 0))
                    reset_button.grid(row=0, column=2, sticky="w", padx=(6, 0))
                else:
                    modified_label.grid_remove()
                    reset_button.grid_remove()
                if expanded:
                    body.grid(
                        row=1,
                        column=0,
                        columnspan=2,
                        sticky="nw",
                        pady=(1, 0),
                    )
                else:
                    body.grid_remove()
                schedule_section_relayout()

            def toggle():
                self._custom_section_expanded[key] = not bool(
                    self._custom_section_expanded.get(key, False)
                )
                self.prefs["custom_sections_expanded"] = dict(self._custom_section_expanded)
                schedule = getattr(self, "_schedule_prefs_save", None)
                if callable(schedule):
                    schedule()
                refresh()

            header = ttk.Button(
                header_line,
                style="SectionToggle.TButton",
                command=toggle,
                cursor="hand2",
            )
            header.grid(row=0, column=0, sticky="w")
            modified_label = ttk.Label(header_line, style="Modified.TLabel")
            reset_button = ttk.Button(
                header_line,
                text=_lang_text(language, "Réinitialiser", "Reset", "Zurücksetzen", "Restablecer"),
                command=lambda section=key: self._custom_reset_section(section),
                cursor="hand2",
                padding=(4, 1),
            )
            section_layout_frames[key] = (shell, body)
            self._custom_section_frames[key] = (shell, header, body, refresh)
            refresh()
            return body

        def _display_number(value):
            number = float(value)
            return str(int(number)) if number.is_integer() else f"{number:g}"

        def _read_number(value, default=0.0):
            return _read_preview_number(value, default)

        def tip(fr, en, de, es):
            return _lang_text(language, fr, en, de, es)

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
            tooltip=None,
            tooltip_after_label=True,
            maximum_var=None,
        ):
            line = ttk.Frame(parent)
            line.grid(row=row, column=column, columnspan=columnspan, sticky="w", pady=2)
            label_padx = (0, 0) if tooltip and tooltip_after_label else (0, 8)
            ttk.Label(line, text=label).grid(row=0, column=0, sticky="w", padx=label_padx)
            next_column = 1
            if tooltip and tooltip_after_label:
                add_info(line, 0, tooltip, column=next_column, pady=0)
                next_column += 1
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
            widget.grid(
                row=0,
                column=next_column,
                sticky="w",
                padx=(4, 0) if tooltip and tooltip_after_label else 0,
            )
            maximum = _display_number(high)
            if unit:
                maximum = f"{maximum} {unit}"
                unit_text = f"{unit} · {custom_section_text('max_value', language, value=maximum)}"
            else:
                unit_text = custom_section_text("max_value", language, value=maximum)
            next_column += 1
            if tooltip and not tooltip_after_label:
                add_info(line, 0, tooltip, column=next_column, pady=0)
                next_column += 1
            maximum_label = ttk.Label(line, style="Hint.TLabel")
            if maximum_var is None:
                maximum_label.configure(text=unit_text)
            else:
                maximum_label.configure(textvariable=maximum_var)
            maximum_label.grid(
                row=0, column=next_column, sticky="w", padx=(4, 0)
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
            tooltip=None,
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
            if tooltip:
                add_info(parent, row, tooltip, column=column, pady=2)
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
            tooltip=None,
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
            next_column = 2
            ttk.Label(line, text=unit, style="Hint.TLabel").grid(
                row=0, column=next_column, sticky="w", padx=(5, 10)
            )
            next_column += 1
            ttk.Label(line, text=label).grid(
                row=0,
                column=next_column,
                sticky="w",
                padx=(0, 0) if tooltip else (0, 8),
            )
            next_column += 1
            if tooltip:
                add_info(line, 0, tooltip, column=next_column, pady=0)
                next_column += 1
            maximum = _display_number(high)
            if unit:
                maximum = f"{maximum} {unit}"
            ttk.Label(
                line,
                text=custom_section_text("max_value", language, value=maximum),
                style="Hint.TLabel",
            ).grid(row=0, column=next_column, sticky="w")
            bind_text(widget, path, variable)
            self._custom_section_vars[".".join(path)] = variable
            self._custom_decoration_rate_vars[path[-1]] = variable
            self._custom_decoration_rate_widgets[path[-1]] = widget
            return widget

        minerals = add_collapsible_section(
            "minerals", 1, custom_section_text("minerals", language), pady=(0, 8)
        )
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
            row=0, column=0, sticky="w", padx=(0, 0)
        )
        algorithm_tooltip = tip(
            "Legacy : motifs historiques.\nUpgraded : gisements compacts.\nPixels aléatoires : cases dispersées.",
            "Legacy: historical patterns.\nUpgraded: compact deposits.\nRandom pixels: scattered cells.",
            "Legacy: historische Muster.\nUpgraded: kompakte Lagerstätten.\nZufällige Pixel: verstreute Zellen.",
            "Legacy: patrones históricos.\nUpgraded: yacimientos compactos.\nPíxeles aleatorios: celdas dispersas.",
        )
        add_info(algorithm_line, 0, algorithm_tooltip, column=1, pady=2)
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
        algorithm_combo.grid(row=0, column=2, sticky="w", padx=(4, 0))
        algorithm_combo.bind(
            "<<ComboboxSelected>>",
            lambda event: self._custom_section_changed(
                ("minerals", "algorithm"),
                next(key for key, label in algorithm_labels.items() if label == algorithm_var.get()),
            ),
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
            tooltip=tip(
                "Part de la carte occupée par les cases minéralisées.",
                "Share of the map occupied by mineral-bearing cells.",
                "Anteil der Karte mit mineralhaltigen Zellen.",
                "Parte del mapa ocupada por casillas mineralizadas.",
            ),
        )

        variation_frame = ttk.Frame(mineral_grid)
        variation_frame.grid(row=0, column=1, sticky="nw", padx=(6, 0))
        ttk.Label(variation_frame, text=custom_section_text("size_variation", language)).grid(
            row=0, column=0, sticky="w", padx=(0, 0), pady=2
        )
        variation_tooltip = tip(
            "Variation appliquée à la taille des gisements.",
            "Variation applied to deposit size.",
            "Variation der Lagerstättengröße.",
            "Variación aplicada al tamaño de los yacimientos.",
        )
        add_info(variation_frame, 0, variation_tooltip, column=1, pady=2)
        variation_labels = {key: custom_section_text(key, language) for key in SIZE_VARIATIONS}
        variation_var = tk.StringVar(value=variation_labels[mineral_values["size_variation"]])
        variation_combo = ttk.Combobox(
            variation_frame,
            textvariable=variation_var,
            values=[variation_labels[key] for key in SIZE_VARIATIONS],
            state="readonly",
            width=12,
        )
        variation_combo.grid(row=0, column=2, sticky="w", padx=(4, 0), pady=2)
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
                custom_section_text("resource_unit", language),
                tooltip=custom_section_text("resource_hint", language),
                icon=self._custom_mineral_icons[key],
                icon_key=key,
            )
        ttk.Label(
            quantity_frame,
            text=tip(
                "Quantité moyenne par case minéralisée.",
                "Average quantity per mineral-bearing cell.",
                "Durchschnitt je mineralhaltiger Zelle.",
                "Cantidad media por casilla mineralizada.",
            ),
            style="Hint.TLabel",
        ).grid(row=len(MINERAL_SPECS), column=0, columnspan=5, sticky="w", pady=(4, 0))
        fish = add_collapsible_section(
            "fish", 2, custom_section_text("fish", language), pady=(0, 8)
        )
        fish.columnconfigure(0, weight=0)
        fish_values = sections["fish"]
        fish_grid = ttk.Frame(fish)
        fish_grid.grid(row=0, column=0, sticky="nw")
        fish_grid.columnconfigure(0, weight=0)
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
            1,
            custom_section_text("average_quantity", language),
            ("fish", "average_quantity"),
            fish_values["average_quantity"],
            RESOURCE_MINIMUM,
            RESOURCE_MAXIMUM,
            1,
            custom_section_text("resource_unit", language),
            column=0,
        )
        near_shore_var = tk.BooleanVar(value=bool(fish_values["near_shore"]))
        near_shore_line = ttk.Frame(fish_grid)
        near_shore_line.grid(row=2, column=0, sticky="w", pady=(5, 2))
        near_shore = ttk.Checkbutton(
            near_shore_line,
            text=custom_section_text("near_shore", language),
            variable=near_shore_var,
            command=lambda: self._custom_section_changed(("fish", "near_shore"), near_shore_var.get()),
        )
        near_shore.grid(row=0, column=0, sticky="w")
        add_info(
            near_shore_line,
            0,
            custom_section_text("coast_hint", language),
            column=1,
            pady=0,
        )
        band_thickness = add_spin(
            fish_grid,
            3,
            custom_section_text("band_thickness", language),
            ("fish", "band_thickness"),
            fish_values["band_thickness"],
            1,
            4096,
            1,
            custom_section_text("cells_unit", language),
            column=0,
            tooltip_after_label=True,
            tooltip=tip(
                "Largeur de la bande côtière, en cases HEX6.\nDisponible seulement si « Près des côtes » est actif.",
                "Width of the coastal band, in HEX6 cells.\nAvailable only when “Near shore” is enabled.",
                "Breite des Küstenbands in HEX6-Zellen.\nNur verfügbar, wenn „Küstennah“ aktiv ist.",
                "Anchura de la franja costera, en casillas HEX6.\nDisponible solo si «Cerca de la costa» está activo.",
            ),
        )
        self._custom_fish_band_thickness_widget = band_thickness
        band_thickness.configure(state="normal" if fish_values["near_shore"] else "disabled")

        rivers = add_collapsible_section(
            "rivers", 3, custom_section_text("rivers", language), pady=(0, 8)
        )
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
            tooltip=custom_section_text("river_hint", language),
        )

        terrains = add_collapsible_section(
            "terrains", 4, custom_section_text("terrains", language), pady=(0, 8)
        )
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

        trees = add_collapsible_section(
            "trees", 5, custom_section_text("trees", language), pady=(0, 8)
        )
        trees.columnconfigure(0, weight=0)
        tree_values = sections["trees"]
        sapling_values = tree_values["saplings"]
        forest_values = tree_values["forests"]
        tree_quota_grid = ttk.Frame(trees)
        tree_quota_grid.grid(row=0, column=0, sticky="nw")
        tree_quota_grid.columnconfigure(0, weight=0)
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
            tooltip=custom_section_text("tree_hint", language),
        )
        palm_widget = add_spin(
            tree_quota_grid,
            1,
            custom_section_text("tree_palm_quota", language),
            ("trees", "palm_quota_percent"),
            tree_values["palm_quota_percent"],
            SEMANTIC_DENSITY_MIN,
            TREE_QUOTA_MAX,
            1,
            custom_section_text("percent_unit", language),
            column=0,
        )

        saplings = ttk.LabelFrame(trees, text=custom_section_text("tree_saplings", language), padding=6)
        saplings.grid(row=1, column=0, sticky="nw", pady=(6, 6))
        saplings.columnconfigure(0, weight=0)
        saplings_enabled_var = tk.BooleanVar(value=bool(sapling_values["enabled"]))
        saplings_enabled = ttk.Checkbutton(
            saplings,
            text=custom_section_text("tree_saplings_enabled", language),
            variable=saplings_enabled_var,
            command=lambda: self._custom_section_changed(("trees", "saplings", "enabled"), saplings_enabled_var.get()),
        )
        saplings_enabled.grid(row=0, column=0, sticky="w", pady=1)
        in_global_var = tk.BooleanVar(value=bool(sapling_values["in_global_pool"]))
        in_global = ttk.Checkbutton(
            saplings,
            text=custom_section_text("tree_saplings_global_pool", language),
            variable=in_global_var,
            command=lambda: self._custom_section_changed(("trees", "saplings", "in_global_pool"), in_global_var.get()),
        )
        in_global.grid(row=1, column=0, sticky="w", pady=1)
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
            3,
            custom_section_text("tree_saplings_separate_quota", language),
            ("trees", "saplings", "quota_percent"),
            sapling_values["quota_percent"],
            SEMANTIC_DENSITY_MIN,
            SEMANTIC_DENSITY_MAX,
            1,
            custom_section_text("percent_unit", language),
            column=0,
        )
        placement_labels = {key: custom_section_text(f"tree_placement_{key}", language) for key in TREE_PLACEMENTS}
        placement_var = tk.StringVar(value=placement_labels.get(sapling_values["placement"], placement_labels["everywhere"]))
        placement_line = ttk.Frame(saplings)
        placement_line.grid(row=4, column=0, sticky="w", pady=1)
        placement_combo = ttk.Combobox(
            placement_line,
            textvariable=placement_var,
            values=[placement_labels[key] for key in TREE_PLACEMENTS],
            state="readonly",
            width=20,
        )
        ttk.Label(placement_line, text=custom_section_text("tree_saplings_placement", language)).grid(
            row=0, column=0, sticky="w", padx=(0, 8)
        )
        placement_combo.grid(row=0, column=1, sticky="w")
        placement_combo.bind(
            "<<ComboboxSelected>>",
            lambda event: self._custom_section_changed(
                ("trees", "saplings", "placement"),
                next(key for key, label in placement_labels.items() if label == placement_var.get()),
            ),
        )

        sapling_reason_var = tk.StringVar(value="")

        def refresh_sapling_controls(*_args):
            enabled = bool(saplings_enabled_var.get())
            in_global_pool = bool(in_global_var.get())
            in_global.configure(state="normal" if enabled else "disabled")
            global_share_widget.configure(state="normal" if enabled and in_global_pool else "disabled")
            sapling_quota_widget.configure(state="normal" if enabled and not in_global_pool else "disabled")
            placement_combo.configure(state="readonly" if enabled else "disabled")
            if not enabled:
                message = ""
            elif in_global_pool:
                message = _lang_text(
                    language,
                    "Quota global : le quota séparé des pousses est désactivé.",
                    "Global pool: the separate sapling quota is disabled.",
                    "Globaler Pool: Das separate Setzlingskontingent ist deaktiviert.",
                    "Cupo global: el cupo separado de retoños está desactivado.",
                )
            else:
                message = _lang_text(
                    language,
                    "Quota séparé : la part du quota global est désactivée.",
                    "Separate quota: the global-pool share is disabled.",
                    "Separates Kontingent: Der Anteil am globalen Pool ist deaktiviert.",
                    "Cupo separado: la parte del cupo global está desactivada.",
                )
            sapling_reason_var.set(message)

        saplings_enabled_var.trace_add("write", refresh_sapling_controls)
        in_global_var.trace_add("write", refresh_sapling_controls)
        ttk.Label(
            saplings,
            textvariable=sapling_reason_var,
            style="Hint.TLabel",
            wraplength=560,
            justify="left",
        ).grid(row=5, column=0, sticky="w", pady=(2, 0))
        refresh_sapling_controls()

        forests = ttk.LabelFrame(trees, text=custom_section_text("tree_forests", language), padding=6)
        forests.grid(row=2, column=0, sticky="nw", pady=(0, 6))
        forests.columnconfigure(0, weight=0)
        forests_enabled_var = tk.BooleanVar(value=bool(forest_values["enabled"]))
        forests_enabled = ttk.Checkbutton(
            forests,
            text=custom_section_text("tree_forests_enabled", language),
            variable=forests_enabled_var,
            command=lambda: self._custom_section_changed(("trees", "forests", "enabled"), forests_enabled_var.get()),
        )
        forests_enabled.grid(row=0, column=0, sticky="w", pady=1)
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
            2,
            custom_section_text("tree_forest_average", language),
            ("trees", "forests", "trees_per_forest"),
            forest_values["trees_per_forest"],
            FOREST_TREE_COUNT_MIN,
            FOREST_TREE_COUNT_MAX,
            0.1,
            custom_section_text("trees_unit", language),
            column=0,
        )
        forest_variation_widget = add_spin(
            forests,
            3,
            custom_section_text("tree_forest_variation", language),
            ("trees", "forests", "tree_count_variation_percent"),
            forest_values["tree_count_variation_percent"],
            FOREST_TREE_VARIATION_MIN,
            FOREST_TREE_VARIATION_MAX,
            1,
            custom_section_text("percent_unit", language),
            column=0,
        )
        def refresh_forest_controls(*_args):
            enabled = bool(forests_enabled_var.get())
            state = "normal" if enabled else "disabled"
            forest_share_widget.configure(state=state)
            forest_average_widget.configure(state=state)
            forest_variation_widget.configure(state=state)

        forests_enabled_var.trace_add("write", refresh_forest_controls)

        refresh_forest_controls()

        building_stones = add_collapsible_section(
            "building_stones", 6, custom_section_text("building_stones", language), pady=(0, 8)
        )
        building_stones.columnconfigure(0, weight=0)
        stone_values = sections["building_stones"]
        stone_group_values = stone_values["groups"]
        stone_grid = ttk.Frame(building_stones)
        stone_grid.grid(row=0, column=0, sticky="nw")
        stone_grid.columnconfigure(0, weight=0)
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
            tooltip=custom_section_text("building_stone_hint", language),
        )
        add_spin(
            stone_grid,
            1,
            custom_section_text("building_stone_average", language),
            ("building_stones", "average_quantity"),
            stone_values["average_quantity"],
            STONE_QUANTITY_MINIMUM,
            STONE_QUANTITY_MAXIMUM,
            STONE_QUANTITY_STEP,
            custom_section_text("stone_unit", language),
            column=0,
            tooltip=custom_section_text("building_stone_average_hint", language),
        )
        groups = ttk.LabelFrame(building_stones, text=custom_section_text("building_stone_groups", language), padding=6)
        groups.grid(row=1, column=0, sticky="nw", pady=(6, 0))
        groups.columnconfigure(0, weight=0)
        stone_groups_var = tk.BooleanVar(value=bool(stone_group_values["enabled"]))
        ttk.Checkbutton(
            groups,
            text=custom_section_text("building_stone_groups_enabled", language),
            variable=stone_groups_var,
            command=lambda: self._custom_section_changed(
                ("building_stones", "groups", "enabled"), stone_groups_var.get()
            ),
        ).grid(row=0, column=0, sticky="w", pady=1)
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
            2,
            custom_section_text("building_stone_group_average", language),
            ("building_stones", "groups", "stones_per_group"),
            stone_group_values["stones_per_group"],
            STONE_GROUP_COUNT_MIN,
            STONE_GROUP_COUNT_MAX,
            0.1,
            custom_section_text("stones_unit", language),
            column=0,
        )
        stone_group_variation_widget = add_spin(
            groups,
            3,
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
            enabled = bool(stone_groups_var.get())
            state = "normal" if enabled else "disabled"
            stone_share_widget.configure(state=state)
            stone_group_average_widget.configure(state=state)
            stone_group_variation_widget.configure(state=state)

        stone_groups_var.trace_add("write", refresh_stone_controls)
        refresh_stone_controls()

        stone_preview_vars = {
            key: tk.StringVar(value="")
            for key in ("size", "global", "active", "stock", "groups")
        }
        # Keep the historical singular name as an alias for the first line;
        # the preview is rendered as a compact, reusable panel like Trees.
        stone_preview_var = stone_preview_vars["size"]
        stone_preview_frame = ttk.LabelFrame(building_stones, padding=6)
        stone_preview_title = ttk.Frame(stone_preview_frame)
        ttk.Label(
            stone_preview_title,
            text=custom_section_text("estimated_preview", language),
        ).grid(row=0, column=0, sticky="w")
        add_info(
            stone_preview_title,
            0,
            custom_section_text("preview_placement_note", language),
            column=1,
            pady=0,
        )
        stone_preview_frame.configure(labelwidget=stone_preview_title)
        stone_preview_frame.grid(row=2, column=0, sticky="w", pady=(6, 0))
        for row, key in enumerate(("size", "global", "active", "stock", "groups")):
            ttk.Label(
                stone_preview_frame,
                textvariable=stone_preview_vars[key],
                style="Hint.TLabel",
            ).grid(row=row, column=0, sticky="w")
        def refresh_stone_preview(*_args):
            profile = (
                self._custom_config.profile
                if self._custom_config is not None
                else config.profile
            )
            profile_stones = profile.get("building_stones", {})
            profile_stones = profile_stones if isinstance(profile_stones, dict) else {}
            legacy_content = profile.get("legacy_content", {})
            legacy_stones = (
                legacy_content.get("building_stones", {})
                if isinstance(legacy_content, dict)
                else {}
            )
            if not isinstance(legacy_stones, dict):
                legacy_stones = {}
            anchor_profile = _read_number(
                profile_stones.get(
                    "global_anchor_target_768",
                    profile_stones.get(
                        "global_anchor_target",
                        legacy_stones.get("global_anchor_target_768", 0),
                    ),
                )
            )
            exhausted_profile = _read_number(
                profile_stones.get(
                    "global_exhausted_anchor_target",
                    legacy_stones.get("global_exhausted_anchor_target", 0),
                )
            )
            try:
                side = max(1, int(self.size.get()))
            except (AttributeError, TypeError, ValueError):
                side = 768
            scale = (side / 768.0) ** 2
            requested = round(
                anchor_profile
                * scale
                * _read_number(
                    self._custom_section_vars.get("building_stones.anchor_density_percent"),
                    100.0,
                )
                / 100.0
            )
            exhausted = round(exhausted_profile * scale)
            active = max(0, requested - exhausted)
            average = _read_number(
                self._custom_section_vars.get("building_stones.average_quantity"),
                1.0,
            )
            stock = round(active * average)
            groups_enabled = bool(stone_groups_var.get())
            group_share = (
                _read_number(
                    self._custom_section_vars.get("building_stones.groups.share_percent"),
                    0.0,
                )
                if groups_enabled
                else 0.0
            )
            stones_per_group = max(
                1.0,
                _read_number(
                    self._custom_section_vars.get("building_stones.groups.stones_per_group"),
                    1.0,
                ),
            )
            group_count = (
                int(math.ceil(requested * group_share / 100.0 / stones_per_group))
                if requested and group_share > 0
                else 0
            )
            stone_preview_vars["size"].set(
                custom_section_text("preview_map_size", language, value=f"{side}×{side}")
            )
            stone_preview_vars["global"].set(
                custom_section_text("preview_global_stones", language, value=requested)
            )
            stone_preview_vars["active"].set(
                custom_section_text("preview_active_stones", language, value=active)
            )
            stone_preview_vars["stock"].set(
                custom_section_text("preview_stock_units", language, value=stock)
            )
            stone_preview_vars["groups"].set(
                custom_section_text(
                    "preview_groups" if groups_enabled else "preview_groups_disabled",
                    language,
                    value=(
                        group_count
                        if groups_enabled
                        else 0
                    ),
                )
            )
        for preview_path in (
            "building_stones.anchor_density_percent",
            "building_stones.average_quantity",
            "building_stones.groups.share_percent",
            "building_stones.groups.stones_per_group",
        ):
            variable = self._custom_section_vars.get(preview_path)
            if variable is not None:
                variable.trace_add("write", refresh_stone_preview)
        stone_groups_var.trace_add("write", refresh_stone_preview)
        refresh_stone_preview()

        def refresh_custom_previews_for_size(*_args):
            refresh_stone_preview()

        if hasattr(self, "size"):
            self._custom_preview_size_trace = self.size.trace_add(
                "write", refresh_custom_previews_for_size
            )

        decorations = add_collapsible_section(
            "decorations", 7, custom_section_text("decorations", language), pady=(0, 8)
        )
        decorations.columnconfigure(0, weight=0)
        decoration_grid = ttk.Frame(decorations)
        decoration_grid.grid(row=1, column=0, sticky="nw")
        decoration_grid.columnconfigure(0, weight=0)
        decoration_grid.columnconfigure(1, weight=0)
        self._custom_decoration_icon_slots = {}
        self._custom_decoration_rate_vars = {}
        self._custom_decoration_rate_widgets = {}
        decoration_values = sections["decorations"]
        object_values = sections.get("objects", {})
        decoration_dependency_var = tk.StringVar(value="")
        grass_object_var = tk.BooleanVar(value=bool(
            object_values.get("grass_compatible_on_dry_and_details", False)
            if isinstance(object_values, dict) else False
        ))
        objects_line = ttk.Frame(decorations)
        objects_line.grid(row=0, column=0, sticky="w", pady=(0, 4))
        ttk.Checkbutton(
            objects_line,
            text=custom_section_text("objects_grass_compatible", language),
            variable=grass_object_var,
            command=lambda: self._custom_section_changed(
                ("objects", "grass_compatible_on_dry_and_details"),
                grass_object_var.get(),
            ),
        ).grid(row=0, column=0, sticky="w")
        add_info(
            objects_line,
            0,
            tip(
                "Étend les supports des arbres, pierres et décorations compatibles avec l’herbe à Herbe sèche et Détails d’herbe 1 & 2. Le terrain rocheux reste exclu.",
                "Extends grass-compatible support for trees, stones and decorations to Dry grass and Grass details 1 & 2. Rocky terrain remains excluded.",
                "Erweitert die Gras-Unterstützung für Bäume, Steine und Dekorationen auf Trockengras und Grasdetails 1 & 2. Felsiges Gelände bleibt ausgeschlossen.",
                "Amplía el soporte de hierba para árboles, piedras y decoraciones a Hierba seca y Detalles de hierba 1 y 2. El terreno rocoso sigue excluido.",
            ),
            column=1,
            pady=0,
        )
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

        ttk.Label(
            decorations,
            textvariable=decoration_dependency_var,
            style="Hint.TLabel",
            wraplength=680,
            justify="left",
        ).grid(
            row=(len(DECORATION_FAMILY_KEYS) + 1) // 2 + 1,
            column=0,
            sticky="w",
            pady=(4, 0),
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
            dependency_messages = [custom_section_text("decoration_hint", language)]
            for terrain_key, decoration_keys in dependency_keys.items():
                active = effective_rates.get(terrain_key, 0.0) > 0.0
                if not active:
                    dependency_messages.append(
                        _lang_text(
                            language,
                            "Cactus, arbres morts et squelettes nécessitent un désert actif."
                            if terrain_key == "desert"
                            else "Les roseaux nécessitent un marais actif.",
                            "Cacti, dead trees and skeletons require an active desert."
                            if terrain_key == "desert"
                            else "Reeds require an active swamp.",
                            "Kakteen, tote Bäume und Skelette benötigen eine aktive Wüste."
                            if terrain_key == "desert"
                            else "Schilf benötigt einen aktiven Sumpf.",
                            "Cactus, árboles muertos y esqueletos requieren un desierto activo."
                            if terrain_key == "desert"
                            else "Los juncos requieren un pantano activo.",
                        )
                    )
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
            decoration_dependency_var.set("\n".join(dependency_messages))

        self._custom_refresh_terrain_dependencies = refresh_terrain_dependencies
        refresh_terrain_dependencies()
        # Start-bonus values are deliberately kept in a dedicated semantic
        # section.  Each panel starts with its own on/off switch; quantities
        # therefore never need a zero sentinel to disable a package.
        start_bonus = add_collapsible_section(
            "start_bonus", 0, custom_section_text("start_bonus", language), pady=(0, 8)
        )
        start_bonus.columnconfigure(0, weight=0)
        start_bonus.columnconfigure(1, weight=0)
        start_values = sections["start_bonus"]
        bonus_panel_layout_gap = 16
        bonus_panel_layout_job = None
        bonus_panel_frames = {}

        def bonus_panel_natural_width(key):
            return bonus_panel_frames[key].winfo_reqwidth()

        def bonus_group_fits(keys, available_width):
            required = sum(bonus_panel_natural_width(key) for key in keys)
            required += bonus_panel_layout_gap * max(0, len(keys) - 1)
            return required <= available_width

        def layout_bonus_group(keys, column_count, start_row=0):
            for index, key in enumerate(keys):
                row = start_row + index // column_count
                column = index % column_count
                bonus_panel_frames[key].grid_configure(
                    row=row,
                    column=column,
                    columnspan=1,
                    sticky="nw",
                    padx=(
                        0,
                        bonus_panel_layout_gap
                        if column < min(column_count, len(keys)) - 1
                        else 0,
                    ),
                )

        def relayout_bonus_panels():
            nonlocal bonus_panel_layout_job
            bonus_panel_layout_job = None
            if len(bonus_panel_frames) != 5:
                return
            try:
                available_width = max(0, root.winfo_width() - 28)
            except tk.TclError:
                return
            if available_width <= 1:
                return

            object_columns = 2 if bonus_group_fits(("forest", "stones"), available_width) else 1
            layout_bonus_group(("forest", "stones"), object_columns)
            if bonus_group_fits(("lake", "rocky", "swamp"), available_width):
                layout_bonus_group(("lake", "rocky", "swamp"), 3)
            elif bonus_group_fits(("lake", "rocky"), available_width):
                layout_bonus_group(("lake", "rocky"), 2)
                layout_bonus_group(("swamp",), 1, start_row=1)
            else:
                layout_bonus_group(("lake", "rocky", "swamp"), 1)

        def schedule_bonus_panel_relayout(_event=None):
            nonlocal bonus_panel_layout_job
            if bonus_panel_layout_job is not None:
                return
            try:
                bonus_panel_layout_job = sections_frame.after_idle(relayout_bonus_panels)
            except tk.TclError:
                bonus_panel_layout_job = None

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

        def add_start_panel(parent, title, *, padding=6, tooltip=None):
            """Create one natural-width bonus panel with optional title help."""

            panel = ttk.LabelFrame(parent, padding=padding)
            panel.columnconfigure(0, weight=0)
            if tooltip:
                title_line = ttk.Frame(panel)
                ttk.Label(title_line, text=title).grid(row=0, column=0, sticky="w")
                add_info(title_line, 0, tooltip, column=1, pady=0)
                panel.configure(labelwidget=title_line)
            else:
                panel.configure(text=title)
            return panel

        common_bonus = add_start_panel(
            start_bonus,
            custom_section_text("start_bonus_common", language),
            tooltip=custom_section_text("start_bonus_hint", language),
        )
        common_bonus.grid(row=0, column=0, sticky="w", pady=(0, 7))

        add_spin(
            common_bonus,
            0,
            custom_section_text("start_bonus_distance", language),
            ("start_bonus", "distance_from_border"),
            start_values["distance_from_border"],
            START_BONUS_DISTANCE_MIN,
            START_BONUS_DISTANCE_MAX,
            1,
            "HEX6",
            tooltip=tip(
                "Distance cible du centre du bonus depuis la bordure du territoire.",
                "Target distance from the territory border to the bonus centre.",
                "Zielabstand der Bonusmitte von der Gebietsgrenze.",
                "Distancia objetivo desde el borde del territorio al centro del bono.",
            ),
        )
        force_extended_var = tk.BooleanVar(
            value=bool(start_values.get("force_extended_radius", False))
        )
        force_extended_line = ttk.Frame(common_bonus)
        force_extended_line.grid(row=1, column=0, sticky="w", pady=(0, 3))
        ttk.Checkbutton(
            force_extended_line,
            text=custom_section_text("start_bonus_force_extended", language),
            variable=force_extended_var,
            command=lambda: self._custom_section_changed(
                ("start_bonus", "force_extended_radius"),
                force_extended_var.get(),
            ),
        ).grid(row=0, column=0, sticky="w")
        add_info(
            force_extended_line,
            0,
            tip(
                "Cherche les couronnes suivantes si la distance normale est impossible.",
                "Searches successive distance rings when the normal distance is impossible.",
                "Prüft weitere Entfernungsringe, wenn die normale Distanz unmöglich ist.",
                "Busca anillos sucesivos si la distancia normal es imposible.",
            ),
            column=1,
            pady=0,
        )
        # Distance is common to all five packages, so it stays editable even
        # when a particular package is disabled.

        ttk.Separator(start_bonus, orient="horizontal").grid(
            row=1, column=0, sticky="ew", pady=(1, 4)
        )
        ttk.Label(
            start_bonus,
            text=custom_section_text("start_bonus_objects", language),
            style="Section.TLabel",
        ).grid(row=2, column=0, sticky="w", pady=(0, 4))
        bonus_objects_grid = ttk.Frame(start_bonus)
        bonus_objects_grid.grid(row=3, column=0, sticky="w")
        for column in range(2):
            bonus_objects_grid.columnconfigure(column, weight=0)

        forest_bonus = add_start_panel(
            bonus_objects_grid,
            custom_section_text("start_bonus_forest", language),
            tooltip=custom_section_text("start_bonus_forest_radius_derived", language),
        )
        forest_bonus.grid(row=0, column=0, sticky="nw", pady=(0, 7))
        bonus_panel_frames["forest"] = forest_bonus
        forest_values = start_values["forest"]
        add_start_switch(forest_bonus, "start_forest")
        forest_adult_var = tk.StringVar(
            value=_display_number(forest_values["adult_trees_per_player"])
        )
        forest_sapling_var = tk.StringVar(
            value=_display_number(forest_values["saplings_per_player"])
        )
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
            variable=forest_adult_var,
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
            variable=forest_sapling_var,
        )
        stone_bonus = add_start_panel(
            bonus_objects_grid,
            custom_section_text("start_bonus_stones", language),
            tooltip=custom_section_text("start_bonus_native_shape", language),
        )
        stone_bonus.grid(row=0, column=1, sticky="nw", pady=(0, 7))
        bonus_panel_frames["stones"] = stone_bonus
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
        ttk.Separator(start_bonus, orient="horizontal").grid(
            row=4, column=0, sticky="ew", pady=(1, 4)
        )
        ttk.Label(
            start_bonus,
            text=custom_section_text("start_bonus_terrain_resources", language),
            style="Section.TLabel",
        ).grid(row=5, column=0, sticky="w", pady=(0, 4))
        bonus_resources_grid = ttk.Frame(start_bonus)
        bonus_resources_grid.grid(row=6, column=0, sticky="w")
        for column in range(3):
            bonus_resources_grid.columnconfigure(column, weight=0)

        swamp_bonus = add_start_panel(
            bonus_resources_grid,
            custom_section_text("start_bonus_swamp", language),
            tooltip=custom_section_text("start_bonus_swamp_derived", language),
        )
        swamp_bonus.grid(row=0, column=2, sticky="nw", pady=(0, 7))
        bonus_panel_frames["swamp"] = swamp_bonus
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
        swamp_shape_line.grid(row=1, column=0, columnspan=3, sticky="w", pady=1)
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
        add_info(
            swamp_shape_line,
            0,
            tip(
                "Forme native du générateur ou hexagone régulier.",
                "Generator-native shape or regular hexagon.",
                "Generatornative Form oder regelmäßiges Sechseck.",
                "Forma nativa del generador o hexágono regular.",
            ),
            column=1,
            pady=0,
        )
        swamp_shape_combo.grid(row=0, column=2, sticky="w", padx=(4, 0))
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
        swamp_radius_var = tk.StringVar(
            value=_display_number(swamp_values["radius"])
        )
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
            variable=swamp_radius_var,
        )
        rocky_bonus = add_start_panel(
            bonus_resources_grid,
            custom_section_text("start_bonus_rocky", language),
            tooltip=custom_section_text("start_bonus_rocky_limits", language),
        )
        rocky_bonus.grid(row=0, column=1, sticky="nw", pady=(0, 7))
        bonus_panel_frames["rocky"] = rocky_bonus
        rocky_values = start_values["rocky_minerals"]
        add_start_switch(rocky_bonus, "start_rocky_minerals", columnspan=4)
        shape_labels = {
            key: custom_section_text(f"start_bonus_rocky_shape_{key}", language)
            for key in START_ROCKY_SHAPES
        }
        shape_var = tk.StringVar(
            value=shape_labels.get(rocky_values.get("shape", "hexagon"), shape_labels["hexagon"])
        )
        shape_line = ttk.Frame(rocky_bonus)
        shape_line.grid(row=1, column=0, sticky="w", pady=1)
        ttk.Label(
            shape_line,
            text=custom_section_text("start_bonus_rocky_shape", language),
        ).grid(row=0, column=0, sticky="w")
        add_info(
            shape_line,
            0,
            tip(
                "Hexagone régulier ou forme organique du cœur minéralisé.",
                "Regular hexagon or organic shape for the mineralized core.",
                "Regelmäßiges Sechseck oder organische Form des mineralisierten Kerns.",
                "Hexágono regular o forma orgánica del núcleo mineralizado.",
            ),
            column=1,
            pady=0,
        )
        shape_combo = ttk.Combobox(
            shape_line,
            textvariable=shape_var,
            values=[shape_labels[key] for key in START_ROCKY_SHAPES],
            state="readonly",
            width=13,
        )
        shape_combo.grid(row=0, column=2, sticky="w", padx=(4, 0))
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
        mode_line = ttk.Frame(rocky_bonus)
        mode_line.grid(row=2, column=0, sticky="w", pady=1)
        ttk.Label(
            mode_line,
            text=custom_section_text("start_bonus_rocky_surface", language),
        ).grid(row=0, column=0, sticky="w")
        add_info(
            mode_line,
            0,
            tip(
                "Égal : un rayon commun. Prorata : surface selon la répartition globale. Par minerai : valeurs libres.",
                "Equal: one common radius. Prorata: surface follows global shares. Per mineral: free values.",
                "Gleich: ein gemeinsamer Radius. Anteile: Fläche folgt den globalen Anteilen. Je Mineral: freie Werte.",
                "Igual: un radio común. Prorrata: superficie según el reparto global. Por mineral: valores libres.",
            ),
            column=1,
            pady=0,
        )
        mode_combo = ttk.Combobox(
            mode_line,
            textvariable=mode_var,
            values=[mode_labels[key] for key in START_ROCKY_SURFACE_MODES],
            state="readonly",
            width=13,
        )
        mode_combo.grid(row=0, column=2, sticky="w", padx=(4, 0))
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
            tooltip=None,
        ):
            """Add a compact input with its unit and maximum beside it."""

            variable = tk.StringVar(value=_display_number(value))
            line = ttk.Frame(rocky_matrix)
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
            next_column = 0
            if tooltip:
                add_info(line, 0, tooltip, column=next_column, pady=0)
                next_column += 1
            widget.grid(row=0, column=next_column, sticky="w")
            next_column += 1
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

        rocky_radius_var = tk.StringVar(
            value=_display_number(rocky_values["radius_min"])
        )
        radius_widget = add_start_spin(
            rocky_bonus,
            3,
            custom_section_text("start_bonus_rocky_radius", language),
            ("start_bonus", "rocky_minerals", "radius_min"),
            rocky_values["radius_min"],
            START_BONUS_RADIUS_MIN,
            START_ROCKY_RADIUS_MAX,
            unit="HEX6",
            package_key="start_rocky_minerals",
            variable=rocky_radius_var,
        )

        total_max_var = tk.StringVar(value=rocky_max_text(rocky_total_cells_max(3), rocky_cells_unit))
        rocky_total_var = tk.StringVar(
            value=_display_number(rocky_values.get("total_core_cells", 183))
        )
        total_widget = add_start_spin(
            rocky_bonus,
            4,
            custom_section_text("start_bonus_rocky_total_surface", language),
            ("start_bonus", "rocky_minerals", "total_core_cells"),
            rocky_values.get("total_core_cells", 183),
            START_ROCKY_CORE_CELLS_MIN,
            rocky_total_cells_max(3),
            unit=rocky_cells_unit,
            package_key="start_rocky_minerals",
            variable=rocky_total_var,
            maximum_var=total_max_var,
            tooltip=tip(
                "Surface totale des cœurs ; elle devient la cible en mode prorata.",
                "Total core surface; it is the target in prorata mode.",
                "Gesamtfläche der Kerne; sie ist das Ziel im Anteilsmodus.",
                "Superficie total de los núcleos; es el objetivo en modo prorrata.",
            ),
        )

        rocky_matrix = ttk.Frame(rocky_bonus, padding=(0, 2, 0, 0))
        rocky_matrix.grid(row=5, column=0, sticky="w")
        for matrix_column in range(4):
            rocky_matrix.columnconfigure(matrix_column, weight=0)

        ttk.Label(
            rocky_matrix,
            text=custom_section_text("start_bonus_rocky_family_header", language),
            style="Hint.TLabel",
        ).grid(row=5, column=0, sticky="w", pady=(1, 0))
        ttk.Label(
            rocky_matrix,
            text=custom_section_text("start_bonus_rocky_core_header", language),
            style="Hint.TLabel",
        ).grid(row=5, column=1, sticky="w", padx=(4, 0), pady=(1, 0))
        quantity_header = ttk.Frame(rocky_matrix)
        quantity_header.grid(row=5, column=2, columnspan=2, sticky="w", padx=(4, 0), pady=(1, 0))
        ttk.Label(
            quantity_header,
            text=custom_section_text("start_bonus_rocky_quantity_header", language),
            style="Hint.TLabel",
        ).grid(row=0, column=0, sticky="w")
        add_info(
            quantity_header,
            0,
            custom_section_text("start_bonus_global_mean", language),
            column=1,
            pady=0,
        )

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
                rocky_matrix,
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
                unit=custom_section_text("resource_unit", language),
                maximum_var=None,
            )

        def rocky_mode_key():
            return next(
                (key for key, label in mode_labels.items() if label == mode_var.get()),
                "equal",
            )

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

        lake_bonus = add_start_panel(
            bonus_resources_grid,
            custom_section_text("start_bonus_lake", language),
            tooltip=custom_section_text("start_bonus_lake_hint", language),
        )
        lake_bonus.grid(row=0, column=0, sticky="nw", pady=(0, 0))
        bonus_panel_frames["lake"] = lake_bonus
        lake_values = start_values["lake_fish_river"]
        add_start_switch(lake_bonus, "start_lake_fish_river")
        ttk.Label(
            lake_bonus,
            text=custom_section_text("start_bonus_lake_settings", language),
            style="Section.TLabel",
        ).grid(row=1, column=0, sticky="w", pady=(2, 3))
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
        lake_shape_line.grid(row=2, column=0, columnspan=3, sticky="w", pady=1)
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
        add_info(
            lake_shape_line,
            0,
            tip(
                "Forme native arrondie ou hexagone régulier pour le lac.",
                "Rounded generator-native shape or regular hexagon for the lake.",
                "Abgerundete generatornative Form oder regelmäßiges Sechseck für den See.",
                "Forma nativa redondeada o hexágono regular para el lago.",
            ),
            column=1,
            pady=0,
        )
        lake_shape_combo.grid(row=0, column=2, sticky="w", padx=(4, 0))
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
        lake_radius_min_var = tk.StringVar(
            value=_display_number(lake_values["radius_min"])
        )
        add_start_spin(
            lake_bonus,
            3,
            custom_section_text("start_bonus_radius_min", language),
            ("start_bonus", "lake_fish_river", "radius_min"),
            lake_values["radius_min"],
            START_BONUS_RADIUS_MIN,
            START_BONUS_RADIUS_MAX,
            1,
            "HEX6",
            package_key="start_lake_fish_river",
            column=0,
            variable=lake_radius_min_var,
        )
        lake_radius_max_var = tk.StringVar(
            value=_display_number(lake_values["radius_max"])
        )
        add_start_spin(
            lake_bonus,
            4,
            custom_section_text("start_bonus_radius_max", language),
            ("start_bonus", "lake_fish_river", "radius_max"),
            lake_values["radius_max"],
            START_BONUS_RADIUS_MIN,
            START_BONUS_RADIUS_MAX,
            1,
            "HEX6",
            package_key="start_lake_fish_river",
            column=0,
            variable=lake_radius_max_var,
        )
        add_start_spin(
            lake_bonus,
            5,
            custom_section_text("start_bonus_lake_proximity", language),
            ("start_bonus", "lake_fish_river", "water_proximity_from_territory_border"),
            lake_values["water_proximity_from_territory_border"],
            START_BONUS_WATER_PROXIMITY_MIN,
            START_BONUS_WATER_PROXIMITY_MAX,
            1,
            "HEX6",
            package_key="start_lake_fish_river",
            column=0,
            tooltip=tip(
                "Rayon autour de la bordure du territoire où l’on cherche de l’eau native. Si de l’eau est trouvée dans ce rayon, aucun lac bonus n’est généré. 0 = aucun contrôle.",
                "Radius around the territory border where existing native water is searched. If water is found in this radius, no bonus lake is generated. 0 = no check.",
                "Radius um die Gebietsgrenze zur Prüfung auf vorhandenes natives Wasser. 0 = keine Prüfung: Der See darf auch nahe am Wasser entstehen.",
                "Radio alrededor del borde del territorio para comprobar agua nativa existente. 0 = sin control: el lago puede generarse aunque el inicio esté cerca del agua.",
            ),
        )
        ttk.Separator(lake_bonus, orient="horizontal").grid(
            row=6, column=0, sticky="ew", pady=(5, 3)
        )
        ttk.Label(
            lake_bonus,
            text=custom_section_text("start_bonus_river_settings", language),
            style="Section.TLabel",
        ).grid(row=7, column=0, sticky="w", pady=(0, 3))
        lake_river_target_var = tk.StringVar(
            value=_display_number(lake_values["river_target_per_lake"])
        )
        add_start_spin(
            lake_bonus,
            8,
            custom_section_text("start_bonus_river_target", language),
            ("start_bonus", "lake_fish_river", "river_target_per_lake"),
            lake_values["river_target_per_lake"],
            START_BONUS_RIVER_TARGET_MIN,
            START_BONUS_RIVER_TARGET_MAX,
            1,
            custom_section_text("rivers", language),
            package_key="start_lake_fish_river",
            column=0,
            variable=lake_river_target_var,
            tooltip=tip(
                "Nombre visé de petites rivières attachées au lac ; le moteur peut en placer moins si le terrain bloque.",
                "Target number of small rivers attached to the lake; terrain may legally yield fewer.",
                "Zielzahl kleiner Flüsse am See; das Gelände kann legal weniger zulassen.",
                "Número objetivo de ríos pequeños conectados al lago; el terreno puede permitir menos.",
            ),
        )
        ttk.Separator(lake_bonus, orient="horizontal").grid(
            row=9, column=0, sticky="ew", pady=(5, 3)
        )
        ttk.Label(
            lake_bonus,
            text=custom_section_text("start_bonus_fish_settings", language),
            style="Section.TLabel",
        ).grid(row=10, column=0, sticky="w", pady=(0, 3))
        lake_fish_fill_var = tk.StringVar(
            value=_display_number(lake_values["fish_fill_percent"])
        )
        add_start_spin(
            lake_bonus,
            11,
            custom_section_text("start_bonus_fish_fill", language),
            ("start_bonus", "lake_fish_river", "fish_fill_percent"),
            lake_values["fish_fill_percent"],
            START_BONUS_FISH_FILL_MIN,
            START_BONUS_FISH_FILL_MAX,
            0.1,
            custom_section_text("percent_unit", language),
            package_key="start_lake_fish_river",
            column=0,
            variable=lake_fish_fill_var,
            tooltip=custom_section_text("start_bonus_fish_fill_hint", language),
        )
        self._custom_refresh_start_bonus_controls()
        sections_frame.bind("<Configure>", schedule_section_relayout, add="+")
        sections_frame.bind("<Configure>", schedule_bonus_panel_relayout, add="+")
        root.bind("<Configure>", schedule_section_relayout, add="+")
        root.bind("<Configure>", schedule_bonus_panel_relayout, add="+")
        schedule_section_relayout()
        schedule_bonus_panel_relayout()

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
        # The first edit from a built-in preset only needs the mode selector,
        # status and bookkeeping to enter Custom mode.  The editor is already
        # showing the edited configuration, so rebuilding it here would steal
        # focus and recreate the very widget that received the edit.
        already_custom = self._custom_current_mode() == "custom"
        self._custom_config = config
        self._custom_last_concrete_mode = config.base_mode
        self._custom_last_concrete_archetype = config.base_archetype
        language = self._custom_language()
        if not already_custom:
            self._custom_enter_custom_mode_without_render(config)
        elif hasattr(self, "_custom_provenance_var"):
            # Refresh only the small provenance text in place.  The controls
            # themselves keep their identity, focus and pending edit.
            self._custom_render_custom_mode(config)
            self._custom_last_render_digest=config.digest
        self._custom_refresh_fish_controls()
        self._custom_status_var.set(
            _lang_text(language, "Custom actif · cache invalidé par l’empreinte.", "Custom active · cache is keyed by the fingerprint.", "Custom aktiv · Cache wird über den Fingerabdruck getrennt.", "Custom activo · la caché usa la huella.")
        )
        self._custom_refresh_section_headers()

    def _custom_enter_custom_mode_without_render(
        self, config: CustomGenerationConfig
    ) -> None:
        """Switch a preset-backed editor to Custom without rebuilding it."""

        language = self._custom_language()
        self.mode.set(MODE_LABELS[language]["custom"])
        self._custom_last_ui_mode = "custom"
        self._custom_last_ui_archetype = self._custom_current_archetype()
        # The existing widgets already represent ``config`` because the edit
        # was applied to one of them.  Mark that render state as current so a
        # later unrelated selection does not rebuild the tab just to catch up.
        self._custom_last_render_digest = config.digest
        if hasattr(self, "_custom_provenance_var"):
            self._custom_render_custom_mode(config)
        refresh_feedback = getattr(self, "_refresh_selection_feedback", None)
        if callable(refresh_feedback):
            refresh_feedback()

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
