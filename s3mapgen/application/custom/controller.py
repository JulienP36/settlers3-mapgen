"""Tk editor for declarative Custom generator profiles."""

from __future__ import annotations

import math
import threading
import tkinter as tk
from collections import OrderedDict
from copy import deepcopy
from tkinter import filedialog, ttk

import numpy as np
from PIL import Image, ImageTk

from ...generation.archetypes import (
    ARCHETYPES,
    CONTINENTAL_CUSTOM_PROFILE_KEY,
    MACRO_PALETTE,
    NATIVE_NOISE_MINIMUM,
    NOISE_LAYER_COUNT,
    NOISE_LAYER_COUNT_BOUNDS,
    NOISE_LAYER_FAMILY_OPTIONS,
    NOISE_LAYER_OPERATION_OPTIONS,
    NOISE_LAYER_STRENGTH_BOUNDS,
    NOISE_MASK_BOUNDS,
    NOISE_MASK_DEFAULTS,
    NOISE_MASK_INCREMENTS,
    NOISE_MASK_SOURCE_OPTIONS,
    NOISE_MASK_TYPE_OPTIONS,
    MASK_LAYER_COUNT,
    MASK_LAYER_COUNT_BOUNDS,
    MASK_LAYER_COMMON_BOUNDS,
    MASK_LAYER_COMMON_DEFAULTS,
    MASK_LAYER_COMMON_INCREMENTS,
    MASK_LAYER_MANUAL_GRID_SIDE,
    MASK_LAYER_OPERATION_OPTIONS,
    MASK_LAYER_STRENGTH_BOUNDS,
    MASK_LAYER_TYPE_OPTIONS,
    NOISE_SOURCE_SETTING_BOUNDS,
    NOISE_SOURCE_SETTING_DEFAULTS,
    NOISE_SOURCE_SETTING_INCREMENTS,
    SHAPE_TEMPLATE_BOUNDS,
    SHAPE_TEMPLATE_DEFAULTS,
    SHAPE_TEMPLATE_INCREMENTS,
    SHAPE_TEMPLATE_TYPE_OPTIONS,
    RELIEF_SOURCE_DEFAULT,
    RELIEF_SOURCE_CUSTOM_LEGACY,
    thresholds_on_relief_source_change,
    RELIEF_SOURCE_OPTIONS,
    ArchetypePreview,
    continental_legacy_blocks_profile,
    default_archetype_profile,
    duplicate_mask_layer,
    duplicate_noise_layer,
    generate_archetype_preview,
    generate_noise_component_previews,
    generate_mask_component_previews,
    generate_shape_template_preview,
    iter_archetype_parameter_descriptors,
    macro_percentages,
    macro_rgb,
    noise_rgb,
    noise_delta_rgb,
    noise_source_setting_applies,
    project_preview_rgb,
    raw_height_rgb,
    remove_noise_layer,
    remove_mask_layer,
    reorder_mask_layers,
    reorder_noise_layers,
)
from ...generation.custom import (
    DECORATION_FAMILY_KEYS,
    DECORATION_RATE_MAX,
    DECORATION_RATE_MIN,
    FOREST_TREE_COUNT_MAX,
    FOREST_TREE_COUNT_MIN,
    FOREST_TREE_VARIATION_MAX,
    FOREST_TREE_VARIATION_MIN,
    MINERAL_ALGORITHMS,
    MINERAL_SPECS,
    RESOURCE_MAXIMUM,
    RESOURCE_MINIMUM,
    RIVER_RATE_MAX,
    RIVER_RATE_MIN,
    RIVER_RATE_STEP,
    SEMANTIC_DENSITY_MAX,
    SEMANTIC_DENSITY_MIN,
    SIZE_VARIATIONS,
    START_BONUS_DISTANCE_MAX,
    START_BONUS_DISTANCE_MIN,
    START_BONUS_FISH_FILL_MAX,
    START_BONUS_FISH_FILL_MIN,
    START_BONUS_RADIUS_MAX,
    START_BONUS_RADIUS_MIN,
    START_BONUS_RIVER_TARGET_MAX,
    START_BONUS_RIVER_TARGET_MIN,
    START_BONUS_WATER_PROXIMITY_MAX,
    START_BONUS_WATER_PROXIMITY_MIN,
    START_FOREST_COUNT_MAX,
    START_FOREST_COUNT_MIN,
    START_LAKE_SHAPES,
    START_PACKAGE_CATALOG,
    START_ROCKY_CORE_CELLS_MAX,
    START_ROCKY_CORE_CELLS_MIN,
    START_ROCKY_RADIUS_MAX,
    START_ROCKY_SHAPES,
    START_ROCKY_SURFACE_MODES,
    START_STONE_ANCHOR_MAX,
    START_STONE_ANCHOR_MIN,
    START_SWAMP_RADIUS_MAX,
    START_SWAMP_RADIUS_MIN,
    START_SWAMP_SHAPES,
    STONE_GROUP_COUNT_MAX,
    STONE_GROUP_COUNT_MIN,
    STONE_GROUP_VARIATION_MAX,
    STONE_GROUP_VARIATION_MIN,
    STONE_QUANTITY_MAXIMUM,
    STONE_QUANTITY_MINIMUM,
    STONE_QUANTITY_STEP,
    TERRAIN_ENABLED_RATE_MIN,
    TERRAIN_FAMILY_KEYS,
    TERRAIN_RATE_MAX,
    TERRAIN_RATE_MIN,
    TREE_PLACEMENTS,
    TREE_QUOTA_MAX,
    CustomGenerationConfig,
    build_custom_config,
    default_sections,
    get_path,
    normalize_sections,
    rocky_equal_core_cells,
    rocky_equivalent_radius,
    rocky_proportional_targets,
    rocky_total_cells_max,
    set_path,
)
from ..ui.i18n.common import _lang_text
from ..ui.i18n.shell import ARCHETYPE_INPUT_LABELS, ARCHETYPE_LABELS, MODE_LABELS
from ..ui.theme.palettes import THEME_PALETTES
from ..ui.widgets.icons import info_icons, mineral_icon
from .i18n import (
    archetype_description,
    custom_section_text,
    mineral_label,
)


def _read_preview_number(value, default=0.0):
    """Read either a Tk variable or a raw profile scalar for a preview."""

    try:
        raw_value = value.get() if hasattr(value, "get") else value
        return float(raw_value)
    except (AttributeError, TypeError, ValueError):
        return float(default)


def _archetype_effective_preview_profile(profile: dict) -> dict:
    """Copy a profile with disabled fusion and mask slots removed.

    These slots still need component thumbnails, but they do not participate
    in the composed relief. Keeping their settings out of this comparison lets
    the controller refresh the small component cards without regenerating the
    general map preview.
    """

    effective = deepcopy(profile)
    morphology = effective.get("morphology")
    if not isinstance(morphology, dict):
        return effective
    for layer_key, count_key in (
        ("noise_layers", "noise_layer_count"),
        ("mask_layers", "mask_layer_count"),
    ):
        layers = morphology.get(layer_key, ())
        if not isinstance(layers, (list, tuple)):
            layers = ()
        try:
            count = max(0, min(len(layers), int(morphology.get(count_key, 0))))
        except (TypeError, ValueError):
            count = 0
        active = []
        for index, layer in enumerate(layers[:count]):
            if not isinstance(layer, dict):
                continue
            try:
                strength = int(layer.get("strength_percent", 0))
            except (TypeError, ValueError):
                strength = 0
            if bool(layer.get("enabled", False)) and strength > 0:
                # Noise layers derive their deterministic seed from their
                # slot, so moving an active layer can change the output.
                active.append((index, layer))
        morphology[layer_key] = active
        morphology[count_key] = len(active)
    return effective


def _archetype_ui_parameter_descriptors(profile: dict):
    """Return visible controls, omitting two Legacy rows from the UI."""

    hidden_paths = {
        ("morphology", "native_sculpture_attempts_percent"),
        ("morphology", "native_relaxation_strength_percent"),
    }
    return tuple(
        descriptor
        for descriptor in iter_archetype_parameter_descriptors(profile)
        if descriptor.path not in hidden_paths
    )


def _configure_integer_spinbox_steps(
    widget,
    variable,
    minimum,
    maximum,
    callback,
    *,
    arrow_step=1,
    wheel_step=5,
):
    """Use single increments on the arrows and coarser steps on the wheel."""

    widget.configure(increment=int(arrow_step))

    def on_wheel(event, direction=None):
        if direction is None:
            button = getattr(event, "num", None)
            if button == 4:
                direction = 1
                notches = 1
            elif button == 5:
                direction = -1
                notches = 1
            else:
                try:
                    delta = int(getattr(event, "delta", 0))
                except (TypeError, ValueError):
                    delta = 0
                direction = 1 if delta > 0 else -1 if delta < 0 else 0
                if direction:
                    notches = max(1, abs(delta) // 120)
                else:
                    notches = 1
        else:
            notches = 1
        try:
            current = int(round(float(variable.get())))
        except (TypeError, ValueError):
            return "break"
        target = max(
            int(minimum),
            min(
                int(maximum),
                current + direction * int(wheel_step) * notches,
            ),
        )
        if target != current:
            variable.set(str(target))
            callback()
        return "break"

    widget.bind("<MouseWheel>", on_wheel, add="+")
    widget.bind("<Button-4>", lambda event: on_wheel(event, 1), add="+")
    widget.bind("<Button-5>", lambda event: on_wheel(event, -1), add="+")
    return widget


_ARCHETYPE_PREVIEW_INDICATIVE_PROGRESS = 0.15
_ARCHETYPE_PREVIEW_EXACT_PROGRESS_SPAN = 0.80
_ARCHETYPE_COMPONENT_PREVIEW_SIZE = 128


class _ArchetypePreviewSuperseded(Exception):
    """Internal signal used to stop a preview request that is no longer current."""


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
        self._custom_archetype_baseline: dict[str, object] = {}
        self._custom_archetype_vars: dict[str, tk.Variable] = {}
        self._custom_archetype_spinboxes: dict[str, ttk.Spinbox] = {}
        self._custom_archetype_max_labels: dict[str, ttk.Label] = {}
        self._custom_archetype_noise_layer_vars: dict[int, dict[str, tk.Variable]] = {}
        self._custom_archetype_noise_layer_setting_widgets: dict[
            int, dict[str, tk.Widget]
        ] = {}
        self._custom_archetype_noise_layer_cards: dict[int, ttk.LabelFrame] = {}
        self._custom_archetype_noise_layer_action_widgets: dict[
            int, dict[str, ttk.Button]
        ] = {}
        self._custom_archetype_noise_group_expanded: dict[
            str, dict[str, bool]
        ] = {}
        self._custom_archetype_noise_group_widgets: dict[
            str, dict[str, tuple[ttk.Frame, ttk.LabelFrame, ttk.Button | None]]
        ] = {}
        self._custom_archetype_noise_layer_solo: int | None = None
        self._custom_archetype_noise_layer_count_var = tk.StringVar(value="0")
        self._custom_archetype_mask_layer_vars: dict[int, dict[str, tk.Variable]] = {}
        self._custom_archetype_mask_layer_setting_widgets: dict[
            int, dict[str, tk.Widget]
        ] = {}
        self._custom_archetype_mask_layer_cards: dict[int, ttk.LabelFrame] = {}
        self._custom_archetype_mask_layer_action_widgets: dict[
            int, dict[str, ttk.Button]
        ] = {}
        self._custom_archetype_mask_layer_count_var = tk.StringVar(value="0")
        self._custom_archetype_relief_source_vars: dict[str, tk.Variable] = {}
        self._custom_archetype_size_adaptive_frequency_var = tk.BooleanVar(
            value=False
        )
        self._custom_archetype_relief_mask_vars: dict[str, tk.Variable] = {}
        self._custom_archetype_shape_vars: dict[str, tk.Variable] = {}
        self._custom_archetype_shape_widgets: dict[str, tk.Widget] = {}
        self._custom_archetype_shape_canvas: tk.Canvas | None = None
        self._custom_archetype_shape_photo: ImageTk.PhotoImage | None = None
        self._custom_archetype_shape_image_item: int | None = None
        self._custom_archetype_relief_setting_widgets: list[tk.Widget] = []
        self._custom_archetype_relief_setting_widget_map: dict[str, tk.Widget] = {}
        self._custom_archetype_editor_editable = True
        self._custom_archetype_modified_label: ttk.Label | None = None
        self._custom_archetype_reset_button: ttk.Button | None = None
        self._custom_archetype_morphology_reset_button: ttk.Button | None = None
        self._custom_archetype_noise_reset_button: ttk.Button | None = None
        self._custom_archetype_preview_trace_ids: list[tuple[tk.Variable, str]] = []
        self._custom_archetype_preview_after = None
        self._custom_archetype_preview_poll_after = None
        self._custom_archetype_preview_refresh_pending = False
        self._custom_archetype_preview_refresh_main_pending = False
        self._custom_archetype_preview_request_id = 0
        self._custom_archetype_preview_request = None
        self._custom_archetype_preview_completed = None
        self._custom_archetype_preview_noise_completed = None
        self._custom_archetype_components_completed = None
        self._custom_archetype_preview_lock = threading.Lock()
        self._custom_archetype_preview_worker: threading.Thread | None = None
        self._custom_archetype_preview_canvases: dict[str, tk.Canvas] = {}
        self._custom_archetype_preview_status_var = tk.StringVar(value="")
        self._custom_archetype_preview_stats_var = tk.StringVar(value="")
        self._custom_archetype_preview_photos: dict[str, ImageTk.PhotoImage] = {}
        self._custom_archetype_preview_image_items: dict[str, int] = {}
        self._custom_archetype_component_canvases: dict[str, tk.Canvas] = {}
        self._custom_archetype_component_photos: dict[str, ImageTk.PhotoImage] = {}
        self._custom_archetype_component_image_items: dict[str, int] = {}
        self._custom_archetype_preview_last_result: ArchetypePreview | None = None
        self._custom_archetype_preview_last_snapshot = None
        self._custom_archetype_preview_last_lab = None
        self._custom_archetype_preview_noise_cache = OrderedDict()
        self._custom_archetype_preview_raw_noise_cache = OrderedDict()
        self._custom_archetype_component_cache = OrderedDict()
        self._custom_archetype_preview_progress = None
        self._custom_archetype_preview_display_progress = 0.0
        self._custom_archetype_preview_progress_bar: ttk.Progressbar | None = None
        self._custom_archetype_preview_projection_key = "square"
        self._custom_archetype_preview_size_key = "compact"
        self._custom_archetype_legacy_blocks_expanded = False
        self._custom_archetype_preview_layout_after = None
        self._custom_archetype_preview_last_dimensions = None
        # Preview-only performance preference; native generation always keeps
        # relief relaxation enabled.
        self._custom_archetype_preview_relaxation_var = tk.BooleanVar(value=True)
        # Rebuilding the generator tab destroys its section widgets while an
        # older after_idle layout callback may still be queued.  The render
        # generation lets those callbacks become harmless no-ops.
        self._custom_layout_generation = 0
        self._custom_archetype_preview_projection_var = tk.StringVar()
        self._custom_archetype_preview_size_var = tk.StringVar()
        self._custom_status_var = tk.StringVar(value="")
        self._custom_provenance_var = tk.StringVar(value="")
        self._custom_generator_tab = self._scroll_notebook_tab("Générateur")
        # The generator owns a responsive grid.  Let its scroll surface fit
        # the viewport instead of preserving the widest one-column request;
        # otherwise the canvas keeps a horizontal natural width and the grid
        # never receives the narrow width that should trigger its reflow.
        self._custom_generator_tab._scroll_fit_width = True
        self._custom_archetype_tab = self._scroll_notebook_tab("Archétype")
        self.nb.bind(
            "<<NotebookTabChanged>>",
            self._custom_archetype_notebook_tab_changed,
            add="+",
        )
        self._custom_archetype_tab.bind(
            "<Configure>",
            self._custom_archetype_preview_surface_changed,
            add="+",
        )
        archetype_scroll_canvas = getattr(
            self._custom_archetype_tab,
            "_scroll_canvas",
            None,
        )
        if archetype_scroll_canvas is not None:
            archetype_scroll_canvas.bind(
                "<Configure>",
                self._custom_archetype_preview_surface_changed,
                add="+",
            )
            archetype_scroll_host = getattr(
                self._custom_archetype_tab,
                "_scroll_host",
                None,
            )
            if archetype_scroll_host is not None:
                archetype_scroll_host.bind(
                    "<Configure>",
                    self._custom_archetype_preview_surface_changed,
                    add="+",
                )
        self._custom_selection_changed()

    def _custom_language(self) -> str:
        return self.prefs.get("language", "fr")

    def _custom_config_digest(self) -> str:
        """Expose the active profile identity to generation/cache workflows."""

        mode = self._custom_current_mode()
        archetype = self._custom_current_archetype()
        config = self._custom_config_for_generation(mode, archetype)
        return config.digest if config is not None else ""

    def _custom_config_for_generation(
        self, mode: str | None = None, archetype: str | None = None
    ) -> CustomGenerationConfig | None:
        """Return a runtime config for Generator Custom or a custom archetype."""

        mode = str(mode or self._custom_current_mode())
        archetype = str(archetype or self._custom_current_archetype())
        config = getattr(self, "_custom_config", None)
        if config is None or config.base_archetype != archetype:
            return None
        if mode == "custom":
            return config
        if mode not in {"legacy", "upgraded"} or config.base_mode != mode:
            return None
        baseline = default_archetype_profile(archetype)
        return config if config.archetype_profile != baseline else None

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
            current = getattr(self, "_custom_config", None)
            if (
                current is not None
                and current.base_mode == mode
                and current.base_archetype == archetype
                and current.archetype_profile != default_archetype_profile(archetype)
            ):
                return current
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

    def _custom_clear_archetype_preview_traces(self) -> None:
        """Stop old archetype preview listeners before rebuilding the tab."""

        for variable, trace_id in getattr(
            self, "_custom_archetype_preview_trace_ids", []
        ):
            try:
                variable.trace_remove("write", trace_id)
            except (AttributeError, tk.TclError):
                pass
        self._custom_archetype_preview_trace_ids = []
        for attribute in (
            "_custom_archetype_preview_after",
            "_custom_archetype_preview_poll_after",
            "_custom_archetype_preview_layout_after",
        ):
            after_id = getattr(self, attribute, None)
            if after_id is None:
                continue
            try:
                self._custom_archetype_tab.after_cancel(after_id)
            except (AttributeError, tk.TclError):
                pass
            setattr(self, attribute, None)
        with self._custom_archetype_preview_lock:
            self._custom_archetype_preview_request_id += 1
            self._custom_archetype_preview_request = None
            self._custom_archetype_preview_completed = None
            self._custom_archetype_preview_noise_completed = None
            self._custom_archetype_components_completed = None
            self._custom_archetype_preview_progress = None
        self._custom_archetype_preview_canvases = {}
        self._custom_archetype_preview_photos = {}
        self._custom_archetype_preview_image_items = {}
        self._custom_archetype_component_canvases = {}
        self._custom_archetype_component_photos = {}
        self._custom_archetype_component_image_items = {}
        self._custom_archetype_component_cache = OrderedDict()
        self._custom_archetype_preview_last_result = None
        self._custom_archetype_preview_last_snapshot = None
        self._custom_archetype_preview_last_lab = None
        self._custom_archetype_preview_last_dimensions = None
        self._custom_archetype_preview_display_progress = 0.0
        self._custom_archetype_preview_progress_bar = None
        self._custom_archetype_preview_stats_var.set("")

    def _custom_archetype_preview_projection_options(self, language: str) -> dict[str, str]:
        return {
            "square": _lang_text(
                language,
                "Carrée",
                "Square",
                "Quadratisch",
                "Cuadrada",
            ),
            "parallelogram": _lang_text(
                language,
                "Parallélogramme",
                "Parallelogram",
                "Parallelogramm",
                "Paralelogramo",
            ),
        }

    def _custom_archetype_preview_size_options(self, language: str) -> dict[str, str]:
        return {
            "compact": _lang_text(
                language,
                "Petite",
                "Small",
                "Klein",
                "Pequeña",
            ),
            "standard": _lang_text(
                language,
                "Grande",
                "Large",
                "Groß",
                "Grande",
            ),
            "large": _lang_text(
                language,
                "Très grande",
                "Extra large",
                "Sehr groß",
                "Muy grande",
            ),
            "adaptive": _lang_text(
                language,
                "Adaptative",
                "Fit to tab",
                "An Tab anpassen",
                "Adaptativa",
            ),
        }

    def _custom_archetype_noise_family_options(self, language: str) -> dict[str, str]:
        labels = {
            RELIEF_SOURCE_DEFAULT: _lang_text(language, "Natif Legacy", "Native Legacy", "Legacy nativ", "Legacy nativo"),
            "white": _lang_text(language, "Bruit blanc", "White noise", "Weißes Rauschen", "Ruido blanco"),
            "value": _lang_text(language, "Bruit de valeur", "Value noise", "Value Noise", "Ruido de valor"),
            "perlin": "Perlin",
            "simplex": "Simplex",
            "fbm": "fBm",
            "hybrid_fbm": _lang_text(language, "Hybrid fBm / multifractal", "Hybrid fBm / multifractal", "Hybrides fBm / Multifraktal", "fBm híbrido / multifractal"),
            "heterogeneous_fbm": _lang_text(language, "fBm hétérogène / relief", "Heterogeneous fBm / relief", "Heterogenes fBm / Relief", "fBm heterogéneo / relieve"),
            "billow": _lang_text(language, "Billow / ondulations", "Billow", "Billow", "Billow"),
            "turbulence": _lang_text(language, "Turbulence", "Turbulence", "Turbulenz", "Turbulencia"),
            "ridged": _lang_text(language, "Ridged / crêtes", "Ridged", "Ridged", "Ridged"),
            "ridged_multifractal": _lang_text(language, "Ridged multifractal / crêtes", "Ridged multifractal / ridges", "Ridged-Multifraktal / Grate", "Ridged multifractal / crestas"),
            "worley": _lang_text(language, "Worley / cellulaire", "Worley / cellular", "Worley / Zellen", "Worley / celular"),
            "worley_f1": _lang_text(language, "Worley F1", "Worley F1", "Worley F1", "Worley F1"),
            "worley_f2": _lang_text(language, "Worley F2", "Worley F2", "Worley F2", "Worley F2"),
            "worley_f2_minus_f1": _lang_text(language, "Worley F2−F1", "Worley F2−F1", "Worley F2−F1", "Worley F2−F1"),
            "domain_warp": _lang_text(language, "Domain warp", "Domain warp", "Domain Warp", "Domain warp"),
        }
        return {
            key: labels[key]
            for key in NOISE_LAYER_FAMILY_OPTIONS
            if key in labels
        }

    def _custom_archetype_noise_mask_options(self, language: str) -> dict[str, str]:
        labels = {
            "none": _lang_text(language, "Aucun", "None", "Keine", "Ninguno"),
            "height": _lang_text(language, "Hauteur", "Height", "Höhe", "Altura"),
            "edge": _lang_text(language, "Bordure", "Edge", "Rand", "Borde"),
            "band_x": _lang_text(language, "Bande X", "X band", "X-Band", "Banda X"),
            "band_y": _lang_text(language, "Bande Y", "Y band", "Y-Band", "Banda Y"),
            "direction": _lang_text(language, "Direction", "Direction", "Richtung", "Dirección"),
            "slope": _lang_text(language, "Pente", "Slope", "Neigung", "Pendiente"),
            "curvature": _lang_text(language, "Courbure", "Curvature", "Krümmung", "Curvatura"),
            "noise": _lang_text(language, "Autre noise", "Other noise", "Anderes Rauschen", "Otro ruido"),
        }
        return {key: labels[key] for key in NOISE_MASK_TYPE_OPTIONS if key in labels}

    def _custom_archetype_shape_options(self, language: str) -> dict[str, str]:
        labels = {
            "none": _lang_text(language, "Aucun", "None", "Keine", "Ninguno"),
            "ellipse": _lang_text(language, "Ellipse", "Ellipse", "Ellipse", "Elipse"),
            "ring": _lang_text(language, "Anneau", "Ring", "Ring", "Anillo"),
            "star": _lang_text(language, "Étoile", "Star", "Stern", "Estrella"),
            "dome": _lang_text(language, "Dôme", "Dome", "Kuppel", "Cúpula"),
        }
        return {
            key: labels[key]
            for key in SHAPE_TEMPLATE_TYPE_OPTIONS
            if key in labels
        }

    def _custom_archetype_mask_type_options(self, language: str) -> dict[str, str]:
        """Return the available mask providers without provider-only settings."""

        shape_options = self._custom_archetype_shape_options(language)
        shape_options["manual"] = _lang_text(
            language,
            "Dessin libre",
            "Freehand",
            "Freihand",
            "Dibujo libre",
        )
        return {
            key: shape_options[key]
            for key in MASK_LAYER_TYPE_OPTIONS
            if key in shape_options
        }

    def _custom_archetype_mask_operation_options(self, language: str) -> dict[str, str]:
        labels = {
            "blend": _lang_text(language, "Mélanger", "Blend", "Mischen", "Mezclar"),
            "add": custom_section_text("archetype_noise_add", language),
            "subtract": custom_section_text("archetype_noise_subtract", language),
            "multiply": _lang_text(language, "Multiplier", "Multiply", "Multiplizieren", "Multiplicar"),
            "min": "Minimum",
            "max": "Maximum",
            "replace": _lang_text(language, "Remplacer", "Replace", "Ersetzen", "Reemplazar"),
        }
        return {
            key: labels[key]
            for key in MASK_LAYER_OPERATION_OPTIONS
            if key in labels
        }

    def _custom_archetype_relief_source_options(self, language: str) -> dict[str, str]:
        labels = {
            RELIEF_SOURCE_DEFAULT: _lang_text(language, "Natif Legacy", "Native Legacy", "Legacy nativ", "Legacy nativo"),
            RELIEF_SOURCE_CUSTOM_LEGACY: custom_section_text(
                "archetype_relief_source_custom_legacy",
                language,
            ),
            **self._custom_archetype_noise_family_options(language),
        }
        return {
            key: labels[key]
            for key in RELIEF_SOURCE_OPTIONS
            if key in labels
        }

    def _custom_archetype_profile_options(self, language: str) -> dict[str, str]:
        """Return the named macro compositions offered by the Archetype tab."""

        options = {
            "native": custom_section_text("archetype_profile_classic", language),
        }
        if self._custom_current_archetype() == "continental":
            options[CONTINENTAL_CUSTOM_PROFILE_KEY] = custom_section_text(
                "archetype_profile_continental",
                language,
            )
        options["edited"] = custom_section_text(
            "archetype_profile_edited",
            language,
        )
        return options

    def _custom_archetype_profile_presets(self) -> dict[str, dict]:
        """Return fresh profiles for the named composition selector."""

        presets = {
            "native": default_archetype_profile(self._custom_current_archetype())
        }
        if self._custom_current_archetype() == "continental":
            presets[CONTINENTAL_CUSTOM_PROFILE_KEY] = continental_legacy_blocks_profile()
        return presets

    def _custom_archetype_profile_selection_key(self, profile: dict) -> str:
        """Identify whether the current payload is native, named or edited."""

        for key, preset in self._custom_archetype_profile_presets().items():
            if profile == preset:
                return key
        return "edited"

    def _custom_main_archetype_input_key(self) -> str:
        """Map the displayed profile choice to the current macro profile."""

        archetype = self._custom_current_archetype()
        if archetype != "continental":
            return archetype
        config = self._custom_profile_for_display()
        profile_key = self._custom_archetype_profile_selection_key(
            config.archetype_profile
        )
        return {
            "native": "classic",
            CONTINENTAL_CUSTOM_PROFILE_KEY: "continental",
        }.get(profile_key, "edited")

    def _custom_main_archetype_input_options(self, language: str) -> dict[str, str]:
        """Expose base profiles in the main selector and retain island slots."""

        labels = ARCHETYPE_INPUT_LABELS.get(language, ARCHETYPE_INPUT_LABELS["en"])
        selected = self._custom_main_archetype_input_key()
        keys = ["classic", "continental", "large_islands", "small_islands"]
        options = {key: labels[key] for key in keys}
        if selected == "edited":
            # The selector uses the same concise term as Mode; feedback and
            # the Archetype tab retain the clearer “Custom profile” status.
            options["edited"] = labels["edited_option"]
        return options

    def _custom_refresh_main_archetype_input(self) -> None:
        """Keep the header selector synchronized with the active base profile."""

        variable = getattr(self, "arch_input", None)
        combo = getattr(self, "arch_combo", None)
        if variable is None or combo is None:
            return
        language = self._custom_language()
        options = self._custom_main_archetype_input_options(language)
        selected = self._custom_main_archetype_input_key()
        variable.set(options.get(selected, options["classic"]))
        try:
            combo.configure(values=list(options.values()))
        except tk.TclError:
            pass

    def _custom_main_archetype_input_changed(self) -> None:
        """Apply the selected named profile without changing the content mode."""

        variable = getattr(self, "arch_input", None)
        if variable is None:
            return
        language = self._custom_language()
        options = self._custom_main_archetype_input_options(language)
        selected = next(
            (key for key, label in options.items() if label == variable.get()),
            None,
        )
        if selected == "edited" or selected is None:
            self._custom_refresh_main_archetype_input()
            return
        if selected in ("classic", "continental"):
            self.arch.set(ARCHETYPE_LABELS[language]["continental"])
            mode = self._custom_current_mode()
            config = self._custom_ensure_config(
                mode if mode in ("legacy", "upgraded") else None,
                "continental",
            )
            profile = (
                default_archetype_profile("continental")
                if selected == "classic"
                else continental_legacy_blocks_profile()
            )
            self._custom_config = config.with_archetype_profile(
                profile,
                base_archetype="continental",
            )
            self._custom_last_concrete_archetype = "continental"
        else:
            self.arch.set(ARCHETYPE_LABELS[language][selected])
        self._selection_changed()

    def _custom_archetype_profile_changed(self) -> None:
        """Apply one complete inspectable composition from the selector."""

        variable = getattr(self, "_custom_archetype_profile_var", None)
        if variable is None:
            return
        language = self._custom_language()
        options = self._custom_archetype_profile_options(language)
        selected = next(
            (key for key, label in options.items() if label == variable.get()),
            "edited",
        )
        if selected == "edited":
            return
        mode = self._custom_current_mode()
        config = self._custom_ensure_config(
            mode if mode in ("legacy", "upgraded") else None,
            self._custom_current_archetype(),
        )
        current = self._custom_archetype_profile_selection_key(
            config.archetype_profile
        )
        if selected == current:
            return
        preset = self._custom_archetype_profile_presets()[selected]
        self._custom_config = config.with_archetype_profile(preset)
        self._selection_changed()

    def _custom_archetype_noise_operation_options(self, language: str) -> dict[str, str]:
        labels = {
            "replace": _lang_text(language, "Remplacer", "Replace", "Ersetzen", "Reemplazar"),
            "blend": _lang_text(language, "Mélanger", "Blend", "Mischen", "Mezclar"),
            "add": custom_section_text("archetype_noise_add", language),
            "subtract": custom_section_text("archetype_noise_subtract", language),
            "multiply": _lang_text(language, "Multiplier", "Multiply", "Multiplizieren", "Multiplicar"),
            "min": "Minimum",
            "max": "Maximum",
        }
        return {
            key: labels[key]
            for key in NOISE_LAYER_OPERATION_OPTIONS
            if key in labels
        }

    def _custom_archetype_preview_available_width(self) -> int:
        canvas = getattr(self._custom_archetype_tab, "_scroll_canvas", None)
        width = 0
        if canvas is not None:
            try:
                width = int(canvas.winfo_width())
            except tk.TclError:
                width = 0
        if width <= 1:
            try:
                width = int(self._custom_archetype_tab.winfo_width())
            except tk.TclError:
                width = 0
        if width <= 1:
            width = 760
        return max(360, width - 28)

    def _custom_archetype_preview_dimensions(self) -> tuple[int, int]:
        base = {
            # R3's former largest preview becomes the smallest fixed choice.
            "compact": 240,
            "standard": 320,
            "large": 400,
        }.get(self._custom_archetype_preview_size_key, 280)
        if self._custom_archetype_preview_size_key == "adaptive":
            base = min(
                480,
                max(160, (self._custom_archetype_preview_available_width() - 16) // 3),
            )
        if self._custom_archetype_preview_projection_key == "parallelogram":
            return base, max(140, round(base * 2 / 3))
        return base, base

    def _custom_archetype_preview_surface_changed(self, *_args) -> None:
        """Resize an adaptive preview after the scroll surface settles."""

        if self._custom_archetype_preview_size_key != "adaptive":
            return
        previous = self._custom_archetype_preview_layout_after
        if previous is not None:
            try:
                self._custom_archetype_tab.after_cancel(previous)
            except tk.TclError:
                pass
        try:
            self._custom_archetype_preview_layout_after = self._custom_archetype_tab.after(
                100,
                self._custom_resize_archetype_preview_canvases,
            )
        except tk.TclError:
            self._custom_archetype_preview_layout_after = None

    @staticmethod
    def _custom_archetype_preview_canvas_dimensions(canvas: tk.Canvas) -> tuple[int, int]:
        try:
            requested_width = int(canvas.cget("width"))
            requested_height = int(canvas.cget("height"))
            if requested_width > 1 and requested_height > 1:
                return requested_width, requested_height
            width = int(canvas.winfo_width())
            height = int(canvas.winfo_height())
            if width > 1 and height > 1:
                return width, height
            return int(canvas.cget("width")), int(canvas.cget("height"))
        except (TypeError, tk.TclError):
            return 280, 280

    def _custom_archetype_preview_projection_changed(self, *_args) -> None:
        options = self._custom_archetype_preview_projection_options(
            self._custom_language()
        )
        selected = self._custom_archetype_preview_projection_var.get()
        self._custom_archetype_preview_projection_key = next(
            (key for key, label in options.items() if label == selected),
            self._custom_archetype_preview_projection_key,
        )
        self._custom_resize_archetype_preview_canvases()

    def _custom_archetype_preview_size_changed(self, *_args) -> None:
        options = self._custom_archetype_preview_size_options(self._custom_language())
        selected = self._custom_archetype_preview_size_var.get()
        self._custom_archetype_preview_size_key = next(
            (key for key, label in options.items() if label == selected),
            self._custom_archetype_preview_size_key,
        )
        self._custom_resize_archetype_preview_canvases()
        self._custom_archetype_preview_surface_changed()

    def _custom_archetype_preview_relaxation_changed(self) -> None:
        """Refresh the exact macro preview with or without native smoothing."""

        # Cancel the previous state immediately.  Otherwise a result computed
        # with the old checkbox value can arrive during the debounce window
        # and make the toggle appear to do nothing.
        self._custom_cancel_archetype_preview_work()
        self._custom_archetype_preview_noise_cache.clear()
        self._custom_archetype_preview_raw_noise_cache.clear()
        self._custom_schedule_archetype_preview_refresh()

    def _custom_resize_archetype_preview_canvases(self) -> None:
        self._custom_archetype_preview_layout_after = None
        width, height = self._custom_archetype_preview_dimensions()
        dimensions = (width, height)
        if dimensions == self._custom_archetype_preview_last_dimensions:
            return
        self._custom_archetype_preview_last_dimensions = dimensions
        for canvas in self._custom_archetype_preview_canvases.values():
            try:
                canvas.configure(width=width, height=height)
            except tk.TclError:
                continue
        snapshot = self._custom_archetype_preview_last_snapshot
        if snapshot is not None:
            noise, macro, side, seed = snapshot
            self._custom_render_archetype_preview_rasters(
                noise,
                macro,
                side,
                seed,
                noise_lab=getattr(self, "_custom_archetype_preview_last_lab", None),
                include_neutral_contribution=True,
            )

    def _custom_archetype_tab_is_active(self) -> bool:
        """Return whether Tk is currently displaying the Archétype tab."""

        notebook = getattr(self, "nb", None)
        inner = getattr(self, "_custom_archetype_tab", None)
        if notebook is None or inner is None:
            return False
        host = getattr(inner, "_scroll_host", inner)
        try:
            selected = notebook.select()
            return bool(selected) and str(selected) == str(host)
        except (AttributeError, tk.TclError):
            return False

    def _custom_cancel_archetype_preview_work(self) -> None:
        """Invalidate queued/finished preview work without clearing canvases."""

        after_id = getattr(self, "_custom_archetype_preview_after", None)
        if after_id is not None:
            try:
                self._custom_archetype_tab.after_cancel(after_id)
            except (AttributeError, tk.TclError):
                pass
            self._custom_archetype_preview_after = None
        poll_after = getattr(self, "_custom_archetype_preview_poll_after", None)
        if poll_after is not None:
            try:
                self._custom_archetype_tab.after_cancel(poll_after)
            except (AttributeError, tk.TclError):
                pass
            self._custom_archetype_preview_poll_after = None
        with self._custom_archetype_preview_lock:
            self._custom_archetype_preview_request_id += 1
            self._custom_archetype_preview_request = None
            self._custom_archetype_preview_completed = None
            self._custom_archetype_preview_noise_completed = None
            self._custom_archetype_components_completed = None
            self._custom_archetype_preview_progress = None

    def _custom_archetype_notebook_tab_changed(self, *_args) -> None:
        """Pause previews off-tab and resume one latest request on return."""

        if not self._custom_archetype_tab_is_active():
            self._custom_archetype_preview_refresh_pending = True
            self._custom_cancel_archetype_preview_work()
            self._custom_set_archetype_preview_progress(0.0, reset=True)
            self._custom_archetype_preview_status_var.set(
                custom_section_text(
                    "archetype_preview_paused",
                    self._custom_language(),
                )
            )
            return
        if (
            self._custom_archetype_preview_refresh_pending
            or self._custom_archetype_preview_last_result is None
        ):
            self._custom_archetype_preview_refresh_pending = False
            self._custom_schedule_archetype_preview_refresh(
                refresh_main=(
                    getattr(
                        self,
                        "_custom_archetype_preview_refresh_main_pending",
                        False,
                    )
                    or self._custom_archetype_preview_last_result is None
                )
            )
        else:
            preview = self._custom_archetype_preview_last_result
            if preview is not None:
                self._custom_archetype_preview_status_var.set(
                    custom_section_text(
                        "archetype_preview_meta",
                        self._custom_language(),
                        side=preview.side,
                        seed=preview.seed,
                    )
                )
                self._custom_archetype_preview_stats_var.set(
                    self._custom_archetype_preview_summary(preview)
                )

    def _custom_schedule_archetype_preview_refresh(
        self,
        *_args,
        refresh_main: bool = True,
    ) -> None:
        """Queue a fast component refresh and, when needed, a full map pass."""

        refresh_main = bool(refresh_main) or (
            getattr(self, "_custom_archetype_preview_last_result", None) is None
        )
        self._custom_archetype_preview_refresh_main_pending = (
            getattr(self, "_custom_archetype_preview_refresh_main_pending", False)
            or refresh_main
        )

        if not getattr(self, "_custom_archetype_preview_canvases", None):
            return
        if not self._custom_archetype_tab_is_active():
            self._custom_archetype_preview_refresh_pending = True
            self._custom_cancel_archetype_preview_work()
            return
        self._custom_archetype_preview_refresh_pending = False
        previous = getattr(self, "_custom_archetype_preview_after", None)
        if previous is not None:
            try:
                self._custom_archetype_tab.after_cancel(previous)
            except tk.TclError:
                pass
        try:
            self._custom_archetype_preview_after = self._custom_archetype_tab.after(
                120
                if self._custom_archetype_preview_refresh_main_pending
                else 16,
                self._custom_queue_archetype_preview,
            )
        except tk.TclError:
            self._custom_archetype_preview_after = None

    def _custom_archetype_preview_profile(
        self,
        profile: dict,
    ) -> dict:
        """Return the preview-only profile for the optional Solo focus.

        Solo keeps the selected layer's own ``Activer`` state.  Its purpose is
        to isolate one already-active fusion while retaining the primary
        source context; it must never turn a disabled layer on behind the
        editor's back.
        """

        solo = getattr(self, "_custom_archetype_noise_layer_solo", None)
        if solo is None:
            return profile
        try:
            morphology = profile["morphology"]
            count = int(morphology["noise_layer_count"])
            layers = morphology["noise_layers"]
            solo = int(solo)
        except (KeyError, TypeError, ValueError):
            return profile
        if not 0 <= solo < count or not isinstance(layers, list):
            return profile
        # Solo is deliberately preview-only.  It does not pass through
        # _custom_activate_archetype and therefore cannot alter the saved
        # generator profile or the actual map-generation route.  Preserve the
        # selected layer's activation flag instead of forcing it to True.
        for index, layer in enumerate(layers[:count]):
            if isinstance(layer, dict):
                if index != solo:
                    layer["enabled"] = False
        return profile

    def _custom_queue_archetype_preview(self) -> None:
        """Queue one pure preview calculation without blocking Tk redraws."""

        self._custom_archetype_preview_after = None
        if not self._custom_archetype_tab_is_active():
            self._custom_archetype_preview_refresh_pending = True
            self._custom_cancel_archetype_preview_work()
            return
        refresh_main = bool(
            getattr(self, "_custom_archetype_preview_refresh_main_pending", True)
        ) or getattr(self, "_custom_archetype_preview_last_result", None) is None
        self._custom_archetype_preview_refresh_main_pending = False
        if refresh_main:
            self._custom_set_archetype_preview_progress(0.0, reset=True)
        key = self._custom_current_archetype()
        if not ARCHETYPES[key].implemented:
            self._custom_set_archetype_preview_placeholder(
                custom_section_text(
                    "archetype_preview_unimplemented",
                    self._custom_language(),
                )
            )
            return
        try:
            side = int(str(self.size.get()).strip())
            seed = int(str(self.seed.get()).strip())
            mirror_mode = self._mirror_key()
        except (AttributeError, TypeError, ValueError):
            self._custom_set_archetype_preview_placeholder(
                custom_section_text("archetype_preview_invalid", self._custom_language())
            )
            return

        profile = deepcopy(self._custom_profile_for_display().archetype_profile)
        profile = self._custom_archetype_preview_profile(profile)
        relax_macro = bool(self._custom_archetype_preview_relaxation_var.get())
        with self._custom_archetype_preview_lock:
            self._custom_archetype_preview_request_id += 1
            request_id = self._custom_archetype_preview_request_id
            self._custom_archetype_preview_request = (
                request_id,
                profile,
                side,
                seed,
                mirror_mode,
                relax_macro,
                refresh_main,
            )
            self._custom_archetype_preview_completed = None
            self._custom_archetype_preview_noise_completed = None
            self._custom_archetype_components_completed = None
            self._custom_archetype_preview_progress = None
            worker = self._custom_archetype_preview_worker
            if worker is None or not worker.is_alive():
                worker = threading.Thread(
                    target=self._custom_archetype_preview_worker_loop,
                    name="settlers3-archetype-preview",
                    daemon=True,
                )
                self._custom_archetype_preview_worker = worker
                worker.start()
        if refresh_main:
            self._custom_archetype_preview_status_var.set(
                _lang_text(
                    self._custom_language(),
                    "Calcul de l’aperçu…",
                    "Calculating preview…",
                    "Vorschau wird berechnet…",
                    "Calculando vista previa…",
                )
            )
        self._custom_schedule_archetype_preview_poll()

    def _custom_archetype_preview_worker_loop(self) -> None:
        """Consume the latest preview request on a daemon worker thread."""

        while True:
            with self._custom_archetype_preview_lock:
                request = self._custom_archetype_preview_request
                self._custom_archetype_preview_request = None
                if request is None:
                    self._custom_archetype_preview_worker = None
                    return
            if len(request) == 6:
                request_id, profile, side, seed, mirror_mode, relax_macro = request
                refresh_main = True
            else:
                (
                    request_id,
                    profile,
                    side,
                    seed,
                    mirror_mode,
                    relax_macro,
                    refresh_main,
                ) = request

            def report_progress(
                fraction,
                noise,
                *,
                request_id=request_id,
            ) -> None:
                with self._custom_archetype_preview_lock:
                    if request_id != self._custom_archetype_preview_request_id:
                        raise _ArchetypePreviewSuperseded
                    self._custom_archetype_preview_progress = (
                        request_id,
                        float(fraction),
                    )

            try:
                component_source, component_layers = (
                    generate_noise_component_previews(
                        profile,
                        _ARCHETYPE_COMPONENT_PREVIEW_SIZE,
                        seed,
                        mirror_mode=mirror_mode,
                        include_principal=False,
                        domain_side=side,
                        component_cache=getattr(
                            self, "_custom_archetype_component_cache", None
                        ),
                    )
                )
                mask_previews = generate_mask_component_previews(
                    profile,
                    _ARCHETYPE_COMPONENT_PREVIEW_SIZE,
                    seed,
                    mirror_mode=mirror_mode,
                    domain_side=side,
                    component_cache=getattr(
                        self, "_custom_archetype_component_cache", None
                    ),
                )
                error = None
            except Exception as exc:  # pragma: no cover - surfaced in the UI
                error = str(exc)
                component_source = None
                component_layers = ()
                mask_previews = ()
            with self._custom_archetype_preview_lock:
                if request_id != self._custom_archetype_preview_request_id:
                    continue
                self._custom_archetype_components_completed = (
                    request_id,
                    component_source,
                    component_layers,
                    mask_previews,
                    error,
                )
            if not refresh_main:
                if error is not None:
                    with self._custom_archetype_preview_lock:
                        if request_id == self._custom_archetype_preview_request_id:
                            self._custom_archetype_preview_completed = (
                                request_id,
                                None,
                                error,
                            )
                continue

            try:
                # The reduced component fields are posted first, so their
                # cards do not wait for the much more expensive full-size map
                # preview. The previous complete triptych stays visible until
                # the authoritative result is ready.
                preview = generate_archetype_preview(
                    profile,
                    side,
                    seed,
                    mirror_mode,
                    noise_cache=self._custom_archetype_preview_noise_cache,
                    progress=report_progress,
                    relax_macro=relax_macro,
                )
                error = None
            except Exception as exc:  # pragma: no cover - surfaced in the UI
                preview = None
                error = str(exc)
            with self._custom_archetype_preview_lock:
                if request_id == self._custom_archetype_preview_request_id:
                    self._custom_archetype_preview_completed = (
                        request_id,
                        preview,
                        error,
                        component_source,
                        component_layers,
                        mask_previews,
                    )

    def _custom_schedule_archetype_preview_poll(self) -> None:
        if not self._custom_archetype_tab_is_active():
            self._custom_archetype_preview_refresh_pending = True
            return
        if getattr(self, "_custom_archetype_preview_poll_after", None) is not None:
            return
        try:
            self._custom_archetype_preview_poll_after = self._custom_archetype_tab.after(
                33,
                self._custom_poll_archetype_preview,
            )
        except tk.TclError:
            self._custom_archetype_preview_poll_after = None

    def _custom_poll_archetype_preview(self) -> None:
        self._custom_archetype_preview_poll_after = None
        if not self._custom_archetype_tab_is_active():
            self._custom_archetype_preview_refresh_pending = True
            self._custom_cancel_archetype_preview_work()
            return
        with self._custom_archetype_preview_lock:
            completed = self._custom_archetype_preview_completed
            self._custom_archetype_preview_completed = None
            noise_completed = self._custom_archetype_preview_noise_completed
            self._custom_archetype_preview_noise_completed = None
            components_completed = self._custom_archetype_components_completed
            self._custom_archetype_components_completed = None
            progress = self._custom_archetype_preview_progress
            self._custom_archetype_preview_progress = None
            worker = self._custom_archetype_preview_worker
            pending = self._custom_archetype_preview_request is not None
        if components_completed is not None:
            (
                request_id,
                component_source,
                component_layers,
                mask_previews,
                component_error,
            ) = components_completed
            if (
                request_id == self._custom_archetype_preview_request_id
                and component_error is None
                and component_source is not None
            ):
                self._custom_render_archetype_component_previews(
                    component_source,
                    component_layers,
                    mask_layers=mask_previews,
                    render_source=False,
                )
        if noise_completed is not None:
            (
                request_id,
                noise,
                macro,
                side,
                seed,
                noise_lab,
                component_source,
                component_layers,
            ) = noise_completed
            if request_id == self._custom_archetype_preview_request_id:
                self._custom_apply_archetype_noise_preview(
                    noise,
                    macro,
                    side,
                    seed,
                    noise_lab,
                    component_source,
                    component_layers,
                )
        if progress is not None:
            request_id, fraction = progress
            if request_id == self._custom_archetype_preview_request_id:
                try:
                    display_fraction = max(0.0, min(1.0, float(fraction)))
                    self._custom_set_archetype_preview_progress(display_fraction)
                    self._custom_archetype_preview_status_var.set(
                        custom_section_text(
                            "archetype_preview_progress",
                            self._custom_language(),
                            percent=round(display_fraction * 100),
                        )
                    )
                except (TypeError, ValueError, tk.TclError):
                    pass
        if completed is not None:
            if len(completed) == 3:
                request_id, preview, error = completed
                exact_component_source = None
                exact_component_layers = ()
                exact_mask_previews = ()
            elif len(completed) == 5:
                (
                    request_id,
                    preview,
                    error,
                    exact_component_source,
                    exact_component_layers,
                ) = completed
                exact_mask_previews = ()
            else:
                (
                    request_id,
                    preview,
                    error,
                    exact_component_source,
                    exact_component_layers,
                    exact_mask_previews,
                ) = completed
            if request_id == self._custom_archetype_preview_request_id:
                if error is not None or preview is None:
                    self._custom_set_archetype_preview_placeholder(
                        _lang_text(
                            self._custom_language(),
                            f"Aperçu indisponible : {error or 'erreur inconnue'}",
                            f"Preview unavailable: {error or 'unknown error'}",
                            f"Vorschau nicht verfügbar: {error or 'unbekannter Fehler'}",
                            f"Vista previa no disponible: {error or 'error desconocido'}",
                        )
                    )
                else:
                    self._custom_apply_archetype_preview(
                        preview,
                        component_source=exact_component_source,
                        component_layers=exact_component_layers,
                        mask_previews=exact_mask_previews,
                    )
        if pending or (worker is not None and worker.is_alive()):
            self._custom_schedule_archetype_preview_poll()

    def _custom_set_archetype_preview_placeholder(self, text: str) -> None:
        # An invalid/interrupted request must not erase the last complete
        # result.  The placeholder is only needed before the first commit;
        # once a triptych exists, keep it visible while reporting the issue.
        has_committed_preview = (
            getattr(self, "_custom_archetype_preview_last_snapshot", None) is not None
        )
        self._custom_archetype_preview_status_var.set(text)
        self._custom_set_archetype_preview_progress(0.0, reset=True)
        if has_committed_preview:
            return
        self._custom_archetype_preview_last_lab = None
        self._custom_archetype_preview_stats_var.set("")
        self._custom_archetype_preview_image_items = {}
        for canvas in self._custom_archetype_preview_canvases.values():
            try:
                width, height = self._custom_archetype_preview_canvas_dimensions(canvas)
                canvas.delete("all")
                canvas.create_text(
                    width // 2,
                    height // 2,
                    text=text,
                    width=max(100, width - 30),
                    fill="#c5c8cc",
                    justify="center",
                )
            except tk.TclError:
                pass

    def _custom_set_archetype_preview_progress(
        self,
        fraction: float,
        *,
        reset: bool = False,
    ) -> None:
        """Paint a monotone progress value for the current preview request."""

        try:
            value = float(fraction)
        except (TypeError, ValueError):
            return
        if not math.isfinite(value):
            return
        value = max(0.0, min(1.0, value))
        previous = 0.0 if reset else float(
            getattr(self, "_custom_archetype_preview_display_progress", 0.0)
        )
        value = max(previous, value)
        self._custom_archetype_preview_display_progress = value
        progress_bar = getattr(self, "_custom_archetype_preview_progress_bar", None)
        if progress_bar is None:
            return
        try:
            progress_bar.configure(value=value * 100.0)
        except tk.TclError:
            pass

    def _custom_archetype_preview_summary(self, preview: ArchetypePreview) -> str:
        """Format the first macro distribution diagnostic for the tab."""

        language = self._custom_language()
        values = macro_percentages(preview.macro)
        formatted = []
        for value in values:
            rendered = f"{value:.1f}"
            if language in {"fr", "de"}:
                rendered = rendered.replace(".", ",")
            formatted.append(rendered)
        stats = custom_section_text(
            "archetype_preview_stats",
            language,
            water=formatted[0],
            beach=formatted[1],
            grass=formatted[2],
            mountain=formatted[3],
            snow=formatted[4],
        )
        return stats

    def _custom_apply_archetype_noise_preview(
        self,
        noise: np.ndarray,
        macro: np.ndarray,
        side: int,
        seed: int,
        noise_lab=None,
        component_source=None,
        component_layers=(),
        mask_previews=(),
    ) -> None:
        """Commit fast panels independently while the exact macro continues."""

        # Each image item is replaced in place.  The old raster therefore
        # remains visible until its own successor is ready, with no blank
        # frame and no need to wait for native relaxation.
        self._custom_render_archetype_preview_rasters(
            noise,
            None,
            side,
            seed,
            noise_lab=noise_lab,
            include_neutral_contribution=noise_lab is None,
        )
        if component_source is not None:
            self._custom_render_archetype_component_previews(
                component_source,
                component_layers,
                primary_noise=noise,
                mask_layers=mask_previews,
            )
        self._custom_render_archetype_preview_rasters(
            None,
            macro,
            side,
            seed,
        )
        self._custom_archetype_preview_last_snapshot = (noise, macro, side, seed)
        self._custom_archetype_preview_last_lab = noise_lab
        self._custom_archetype_preview_status_var.set(
            custom_section_text(
                "archetype_preview_noise_ready",
                self._custom_language(),
            )
        )
        self._custom_set_archetype_preview_progress(
            _ARCHETYPE_PREVIEW_INDICATIVE_PROGRESS
        )

    def _custom_apply_archetype_preview(
        self,
        preview: ArchetypePreview,
        *,
        component_source=None,
        component_layers=(),
        mask_previews=(),
    ) -> None:
        """Commit one complete preview triptych without rebuilding tabs."""

        committed = self._custom_render_archetype_preview_rasters(
            preview.noise,
            preview.macro,
            preview.side,
            preview.seed,
            noise_lab=preview.noise_lab,
            include_neutral_contribution=preview.noise_lab is None,
            progress=1.0,
        )
        if not committed:
            return
        if component_source is not None:
            self._custom_render_archetype_component_previews(
                component_source,
                component_layers,
                primary_noise=(
                    getattr(preview, "source_noise", None)
                    if getattr(preview, "source_noise", None) is not None
                    else preview.noise
                ),
                mask_layers=mask_previews,
            )
        # Update the bookkeeping only after all three panels have accepted the
        # new photos.  Resize callbacks therefore always redraw the last
        # complete triptych, never a half-applied result.
        self._custom_archetype_preview_last_result = preview
        self._custom_archetype_preview_last_snapshot = (
            preview.noise,
            preview.macro,
            preview.side,
            preview.seed,
        )
        self._custom_archetype_preview_last_lab = preview.noise_lab
        language = self._custom_language()
        self._custom_archetype_preview_status_var.set(
            custom_section_text(
                "archetype_preview_meta",
                language,
                side=preview.side,
                seed=preview.seed,
            )
        )
        self._custom_archetype_preview_stats_var.set(
            self._custom_archetype_preview_summary(preview)
        )

    def _custom_render_archetype_preview_rasters(
        self,
        noise,
        macro,
        side: int,
        seed: int,
        *,
        noise_lab=None,
        include_neutral_contribution: bool = False,
        progress: float | None = None,
    ) -> bool:
        """Prepare then commit one raster snapshot without rebuilding panels.

        Photo conversion happens completely off the visible canvas items.  If
        conversion of any panel fails, no panel is updated and the previous
        complete triptych remains visible.
        """

        projection = self._custom_archetype_preview_projection_key
        images = []
        if noise is not None:
            images.append(("noise", noise_rgb(noise)))
        if macro is not None:
            images.append(("macro", macro_rgb(macro)))
        if noise_lab is not None:
            images.append(("contribution", noise_delta_rgb(noise_lab.layer_delta)))
        elif include_neutral_contribution:
            images.append(
                (
                    "contribution",
                    noise_delta_rgb(np.zeros((int(side), int(side)), dtype=np.float32)),
                )
            )
        prepared = []
        for key, rgb in images:
            canvas = self._custom_archetype_preview_canvases.get(key)
            if canvas is None:
                continue
            try:
                image = self._custom_archetype_preview_display_image(
                    rgb,
                    canvas,
                    projection,
                )
                canvas_width, canvas_height = self._custom_archetype_preview_canvas_dimensions(
                    canvas
                )
                available_width = max(32, canvas_width - 8)
                available_height = max(32, canvas_height - 8)
                scale = min(
                    available_width / max(1, image.width),
                    available_height / max(1, image.height),
                )
                displayed_size = (
                    max(1, round(image.width * scale)),
                    max(1, round(image.height * scale)),
                )
                displayed = image.resize(displayed_size, Image.Resampling.NEAREST)
                photo = ImageTk.PhotoImage(displayed)
                prepared.append(
                    (
                        key,
                        canvas,
                        photo,
                        canvas_width // 2,
                        canvas_height // 2,
                    )
                )
            except tk.TclError:
                return False
        for key, canvas, photo, center_x, center_y in prepared:
            self._custom_archetype_preview_photos[key] = photo
            self._custom_update_archetype_preview_image_item(
                key,
                canvas,
                photo,
                center_x,
                center_y,
            )
        if progress is not None:
            self._custom_set_archetype_preview_progress(progress)
        return True

    def _custom_update_archetype_preview_image_item(
        self,
        key: str,
        canvas: tk.Canvas,
        photo: ImageTk.PhotoImage,
        center_x: int,
        center_y: int,
    ) -> None:
        """Replace a panel image without deleting the visible canvas item."""

        item_id = self._custom_archetype_preview_image_items.get(key)
        if item_id is None:
            self._custom_archetype_preview_image_items[key] = canvas.create_image(
                center_x,
                center_y,
                image=photo,
                anchor="center",
            )
            return
        try:
            canvas.itemconfigure(item_id, image=photo)
            canvas.coords(item_id, center_x, center_y)
        except tk.TclError:
            # A tab rebuild may have destroyed the old canvas item between
            # scheduling and painting.  Recreate only that item; do not clear
            # the whole panel, which is what caused the visible flash.
            self._custom_archetype_preview_image_items[key] = canvas.create_image(
                center_x,
                center_y,
                image=photo,
                anchor="center",
            )

    def _custom_render_archetype_shape_preview(self, shape_mask: np.ndarray) -> bool:
        """Paint the cheap shape-domain raster without clearing its canvas."""

        canvas = getattr(self, "_custom_archetype_shape_canvas", None)
        if canvas is None:
            return False
        try:
            width = int(canvas.cget("width"))
            height = int(canvas.cget("height"))
            if width <= 1 or height <= 1:
                width = int(canvas.winfo_width())
                height = int(canvas.winfo_height())
            width = max(16, width)
            height = max(16, height)
            image = Image.fromarray(
                np.repeat(np.asarray(shape_mask, dtype=np.uint8)[:, :, None], 3, axis=2),
                "RGB",
            ).resize((width, height), Image.Resampling.NEAREST)
            photo = ImageTk.PhotoImage(image)
            self._custom_archetype_shape_photo = photo
            item = getattr(self, "_custom_archetype_shape_image_item", None)
            if item is None:
                self._custom_archetype_shape_image_item = canvas.create_image(
                    width // 2,
                    height // 2,
                    image=photo,
                    anchor="center",
                )
            else:
                canvas.itemconfigure(item, image=photo)
                canvas.coords(item, width // 2, height // 2)
            return True
        except tk.TclError:
            return False

    def _custom_render_archetype_component_previews(
        self,
        principal: np.ndarray,
        layers,
        *,
        primary_noise: np.ndarray | None = None,
        mask_layers=(),
        render_source: bool = True,
    ) -> bool:
        """Commit component thumbnails without blanking old images.

        The primary card is intentionally a reduced copy of the exact
        ``Bruit / hauteur`` raster.  A separately regenerated native field can
        be useful as a diagnostic, but it is not the same image once the
        requested size, morphology or mirror has been applied.
        """

        fields = [("source", principal)] if render_source else []
        fields.extend(
            (f"layer:{index}", field) for index, field in enumerate(layers)
        )
        fields.extend(
            (f"mask:{index}", field) for index, field in enumerate(mask_layers)
        )
        prepared = []
        for key, field in fields:
            canvas = self._custom_archetype_component_canvases.get(key)
            if canvas is None:
                continue
            try:
                width, height = self._custom_archetype_preview_canvas_dimensions(canvas)
                if key == "source" and primary_noise is not None:
                    image = self._custom_archetype_preview_display_image(
                        noise_rgb(primary_noise),
                        canvas,
                        self._custom_archetype_preview_projection_key,
                    )
                    scale = min(
                        max(32, width - 8) / max(1, image.width),
                        max(32, height - 8) / max(1, image.height),
                    )
                    displayed = image.resize(
                        (
                            max(1, round(image.width * scale)),
                            max(1, round(image.height * scale)),
                        ),
                        Image.Resampling.NEAREST,
                    )
                else:
                    image = Image.fromarray(raw_height_rgb(field), "RGB")
                    displayed = image.resize(
                        (max(1, width), max(1, height)),
                        Image.Resampling.NEAREST,
                    )
                prepared.append(
                    (
                        key,
                        canvas,
                        ImageTk.PhotoImage(displayed),
                        width // 2,
                        height // 2,
                    )
                )
            except tk.TclError:
                return False
        for key, canvas, photo, center_x, center_y in prepared:
            self._custom_archetype_component_photos[key] = photo
            item_id = self._custom_archetype_component_image_items.get(key)
            if item_id is None:
                item_id = canvas.create_image(
                    center_x,
                    center_y,
                    image=photo,
                    anchor="center",
                )
                self._custom_archetype_component_image_items[key] = item_id
                continue
            try:
                canvas.itemconfigure(item_id, image=photo)
                canvas.coords(item_id, center_x, center_y)
            except tk.TclError:
                self._custom_archetype_component_image_items[key] = canvas.create_image(
                    center_x,
                    center_y,
                    image=photo,
                    anchor="center",
                )
        return True

    def _custom_archetype_preview_display_image(
        self,
        rgb,
        canvas: tk.Canvas,
        projection: str,
    ) -> Image.Image:
        """Downsample large snapshots before projection and Tk conversion."""

        canvas_width, canvas_height = self._custom_archetype_preview_canvas_dimensions(
            canvas
        )
        source = Image.fromarray(rgb, "RGB")
        if projection == "parallelogram":
            available_side = min(canvas_width / 3, canvas_height / 2)
        else:
            available_side = min(canvas_width, canvas_height)
        target_side = min(
            source.width,
            max(96, round(available_side)),
        )
        if target_side != source.width:
            source = source.resize((target_side, target_side), Image.Resampling.NEAREST)
        projected = project_preview_rgb(np.asarray(source), projection)
        return Image.fromarray(projected, "RGB")

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

    def _custom_archetype_is_modified(self) -> bool:
        """Return whether the macro profile differs from its built-in base."""

        config = getattr(self, "_custom_config", None)
        if config is None:
            return False
        baseline = getattr(self, "_custom_archetype_baseline", None)
        if not isinstance(baseline, dict) or not baseline:
            baseline = default_archetype_profile(config.base_archetype)
        return config.archetype_profile != baseline

    def _custom_refresh_archetype_header(self) -> None:
        """Refresh the macro profile status without rebuilding its controls."""

        config = getattr(self, "_custom_config", None)
        profile_var = getattr(self, "_custom_archetype_profile_var", None)
        if config is not None and profile_var is not None:
            options = self._custom_archetype_profile_options(self._custom_language())
            selection = self._custom_archetype_profile_selection_key(
                config.archetype_profile
            )
            if selection in options:
                profile_var.set(options[selection])
                combo = getattr(self, "_custom_archetype_profile_combo", None)
                if combo is not None:
                    try:
                        combo.configure(values=list(options.values()))
                    except tk.TclError:
                        pass
        self._custom_refresh_main_archetype_input()
        label = getattr(self, "_custom_archetype_modified_label", None)
        button = getattr(self, "_custom_archetype_reset_button", None)
        if label is None or button is None:
            return
        try:
            if self._custom_archetype_is_modified():
                label.configure(text=custom_section_text("section_modified", self._custom_language()))
                label.grid()
                button.grid()
            else:
                label.grid_remove()
                button.grid_remove()
        except tk.TclError:
            pass

    def _custom_refresh_archetype_ranges(self) -> None:
        """Keep relational relief Spinbox bounds synchronized in place."""

        config = getattr(self, "_custom_config", None)
        if config is None:
            return
        try:
            descriptors = iter_archetype_parameter_descriptors(
                config.archetype_profile
            )
        except (TypeError, ValueError):
            return
        language = self._custom_language()
        spinboxes = getattr(self, "_custom_archetype_spinboxes", {})
        max_labels = getattr(self, "_custom_archetype_max_labels", {})
        for descriptor in descriptors:
            widget = spinboxes.get(descriptor.key)
            if widget is None:
                continue
            try:
                widget.configure(
                    from_=descriptor.minimum,
                    to=descriptor.maximum,
                    increment=(
                        1
                        if descriptor.value_type == "int" and descriptor.increment > 1
                        else descriptor.increment
                    ),
                )
                max_label = max_labels.get(descriptor.key)
                if max_label is not None:
                    max_label.configure(
                        text=custom_section_text(
                            "max_value",
                            language,
                            value=str(descriptor.maximum),
                        )
                    )
            except tk.TclError:
                continue

    def _custom_reset_archetype(self) -> None:
        """Restore only the selected archetype's built-in macro profile."""

        config = getattr(self, "_custom_config", None)
        if config is None or not self._custom_archetype_is_modified():
            return
        self._custom_config = config.with_archetype_profile(
            default_archetype_profile(config.base_archetype)
        )
        self._selection_changed()

    @staticmethod
    def _custom_archetype_section_paths(key: str) -> tuple[tuple[str, ...], ...]:
        """Return the profile paths owned by one local archetype reset."""

        if key == "morphology":
            return (
                ("morphology", "shape_scale_percent"),
                ("morphology", "relief_contrast_percent"),
                ("morphology", "native_coarse_variation_percent"),
                ("morphology", "native_refinement_percent"),
                ("morphology", "native_large_scale_refinement_percent"),
                ("morphology", "native_fine_scale_refinement_percent"),
                ("morphology", "native_sculpture_attempts_percent"),
                ("morphology", "native_relaxation_strength_percent"),
                ("morphology", "frame_margin_percent"),
                ("morphology", "edge_falloff_percent"),
                ("morphology", "relief_source"),
                ("morphology", "relief_source_settings"),
                ("morphology", "relief_source_mask"),
                ("relief", "water_threshold"),
                ("relief", "mountain_threshold"),
                ("relief", "snow_threshold"),
            )
        if key == "noise_editor":
            return (
                ("morphology", "size_adaptive_frequency"),
                ("morphology", "noise_layer_count"),
                ("morphology", "noise_layers"),
            )
        if key == "mask_editor":
            return (
                ("morphology", "mask_layer_count"),
                ("morphology", "mask_layers"),
            )
        return ()

    def _custom_archetype_section_is_modified(self, key: str) -> bool:
        """Return whether a local archetype block differs from its base."""

        config = getattr(self, "_custom_config", None)
        if config is None:
            return False
        paths = self._custom_archetype_section_paths(key)
        if not paths:
            return False
        baseline = default_archetype_profile(config.base_archetype)
        current = config.archetype_profile
        try:
            return any(
                get_path(current, path) != get_path(baseline, path)
                for path in paths
            )
        except (KeyError, TypeError):
            return False

    def _custom_refresh_archetype_section_reset_buttons(self) -> None:
        """Keep the two local reset actions discoverable but unobtrusive."""

        editable = bool(getattr(self, "_custom_archetype_editor_editable", True))
        buttons = (
            ("morphology", getattr(self, "_custom_archetype_morphology_reset_button", None)),
            ("noise_editor", getattr(self, "_custom_archetype_noise_reset_button", None)),
            ("mask_editor", getattr(self, "_custom_archetype_mask_reset_button", None)),
        )
        for key, button in buttons:
            if button is None:
                continue
            try:
                button.configure(
                    state=(
                        "normal"
                        if editable and self._custom_archetype_section_is_modified(key)
                        else "disabled"
                    )
                )
            except tk.TclError:
                pass

    @staticmethod
    def _custom_archetype_display_number(value) -> str:
        number = float(value)
        return str(int(number)) if number.is_integer() else f"{number:g}"

    def _custom_sync_archetype_editor_values(self) -> None:
        """Update visible archetype controls after a local reset in place."""

        config = getattr(self, "_custom_config", None)
        if config is None:
            return
        profile = config.archetype_profile
        for key, variable in getattr(self, "_custom_archetype_vars", {}).items():
            try:
                variable.set(str(get_path(profile, tuple(key.split(".")))))
            except (KeyError, TypeError, ValueError, tk.TclError):
                pass
        try:
            language = self._custom_language()
            self._custom_archetype_size_adaptive_frequency_var.set(
                bool(profile["morphology"].get("size_adaptive_frequency", False))
            )
            source = str(
                profile["morphology"].get("relief_source", RELIEF_SOURCE_DEFAULT)
            )
            source_options = self._custom_archetype_relief_source_options(language)
            self._custom_archetype_relief_source_var.set(source_options[source])
            settings = profile["morphology"].get("relief_source_settings", {})
            for key, variable in getattr(
                self, "_custom_archetype_relief_source_vars", {}
            ).items():
                variable.set(
                    self._custom_archetype_display_number(
                        settings.get(key, NOISE_SOURCE_SETTING_DEFAULTS[key])
                    )
                )
            shape_options = self._custom_archetype_shape_options(language)
            shape_settings = profile["morphology"].get(
                "shape_template", SHAPE_TEMPLATE_DEFAULTS
            )
            for key, variable in getattr(
                self, "_custom_archetype_shape_vars", {}
            ).items():
                value = shape_settings.get(key, SHAPE_TEMPLATE_DEFAULTS[key])
                if key == "type":
                    value = shape_options[str(value)]
                variable.set(
                    self._custom_archetype_display_number(value)
                    if isinstance(value, (int, float))
                    else str(value)
                )
            mask_options = self._custom_archetype_noise_mask_options(language)
            mask_settings = profile["morphology"].get(
                "relief_source_mask", NOISE_MASK_DEFAULTS
            )
            source_options_for_mask = self._custom_archetype_noise_family_options(language)
            for key, variable in getattr(
                self, "_custom_archetype_relief_mask_vars", {}
            ).items():
                value = mask_settings.get(key, NOISE_MASK_DEFAULTS[key])
                if key == "type":
                    value = mask_options[str(value)]
                elif key == "source":
                    value = source_options_for_mask[str(value)]
                variable.set(
                    self._custom_archetype_display_number(value)
                    if isinstance(value, (int, float))
                    else str(value)
                )
            count = int(profile["morphology"]["noise_layer_count"])
            self._custom_archetype_noise_layer_count_var.set(str(count))
            mask_count = int(profile["morphology"].get("mask_layer_count", 0))
            self._custom_archetype_mask_layer_count_var.set(str(mask_count))
        except (AttributeError, KeyError, TypeError, ValueError, tk.TclError):
            source = RELIEF_SOURCE_DEFAULT
            count = NOISE_LAYER_COUNT_BOUNDS[0]
            mask_count = MASK_LAYER_COUNT_BOUNDS[0]
        self._custom_sync_archetype_noise_layer_variables()
        self._custom_refresh_archetype_noise_layer_cards(count)
        self._custom_sync_archetype_mask_layer_variables()
        self._custom_refresh_archetype_mask_layer_cards(mask_count)
        self._custom_refresh_archetype_noise_setting_states(source)
        self._custom_refresh_archetype_mask_layer_states()
        self._custom_refresh_archetype_noise_layer_action_states()
        self._custom_refresh_archetype_ranges()
        self._custom_refresh_archetype_header()
        self._custom_refresh_archetype_section_reset_buttons()

    def _custom_reset_archetype_section(self, key: str) -> None:
        """Restore one archetype block while preserving every other block."""

        config = getattr(self, "_custom_config", None)
        paths = self._custom_archetype_section_paths(key)
        if config is None or not paths or not self._custom_archetype_section_is_modified(key):
            return
        baseline = default_archetype_profile(config.base_archetype)
        profile = deepcopy(config.archetype_profile)
        for path in paths:
            profile = set_path(profile, path, deepcopy(get_path(baseline, path)))
        if key == "noise_editor":
            # Solo is preview-only state, but it belongs to the editor stack's
            # reset semantics rather than surviving a reset by accident.
            self._custom_archetype_noise_layer_solo = None
        self._custom_activate_archetype(config.with_archetype_profile(profile))
        self._custom_sync_archetype_editor_values()

    def _custom_refresh_archetype_mask_layer_cards(self, count: int) -> None:
        """Show the requested independent mask slots."""

        count = max(MASK_LAYER_COUNT_BOUNDS[0], min(MASK_LAYER_COUNT, int(count)))
        for index, card in getattr(self, "_custom_archetype_mask_layer_cards", {}).items():
            try:
                if int(index) < count:
                    card.grid(
                        row=int(index) + 1,
                        column=0,
                        sticky="nw",
                        pady=(0, 6),
                    )
                else:
                    card.grid_remove()
            except tk.TclError:
                pass
        self._custom_refresh_archetype_mask_layer_action_states()

    def _custom_sync_archetype_mask_layer_variables(self) -> None:
        """Synchronize visible mask controls after a stack edit or reset."""

        config = getattr(self, "_custom_config", None)
        if config is None:
            return
        try:
            layers = config.archetype_profile["morphology"].get("mask_layers", ())
        except (KeyError, TypeError):
            return
        language = self._custom_language()
        type_options = self._custom_archetype_mask_type_options(language)
        operation_options = self._custom_archetype_mask_operation_options(language)
        for index, variables in getattr(self, "_custom_archetype_mask_layer_vars", {}).items():
            try:
                layer = layers[int(index)]
                variables["enabled"].set(bool(layer["enabled"]))
                variables["type"].set(type_options[str(layer["type"])])
                variables["operation"].set(operation_options[str(layer["operation"])])
                variables["strength"].set(str(layer["strength_percent"]))
                settings = layer.get("settings", {})
                for key, default in MASK_LAYER_COMMON_DEFAULTS.items():
                    value = settings.get(key, default)
                    variables[key].set(self._custom_archetype_display_number(value))
            except (KeyError, IndexError, TypeError, ValueError, tk.TclError):
                continue

    def _custom_commit_archetype_mask_layer_stack(
        self,
        config: CustomGenerationConfig,
        layers,
        count: int,
    ) -> None:
        """Persist one mask stack edit and refresh only its dependent UI."""

        profile = deepcopy(config.archetype_profile)
        profile["morphology"]["mask_layers"] = deepcopy(list(layers))
        profile["morphology"]["mask_layer_count"] = int(count)
        self._custom_activate_archetype(config.with_archetype_profile(profile))
        self._custom_archetype_mask_layer_count_var.set(str(int(count)))
        self._custom_sync_archetype_mask_layer_variables()
        self._custom_refresh_archetype_mask_layer_cards(int(count))
        self._custom_refresh_archetype_mask_layer_states()
        self._custom_refresh_archetype_mask_layer_action_states()

    def _custom_refresh_archetype_mask_layer_action_states(self) -> None:
        """Keep mask stack actions bounded to visible editable slots."""

        try:
            count = int(self._custom_archetype_mask_layer_count_var.get())
        except (AttributeError, TypeError, ValueError):
            count = 0
        count = max(MASK_LAYER_COUNT_BOUNDS[0], min(MASK_LAYER_COUNT, count))
        editable = bool(getattr(self, "_custom_archetype_editor_editable", True))
        try:
            configured_layers = self._custom_config.archetype_profile["morphology"].get(
                "mask_layers", ()
            )
        except (AttributeError, KeyError, TypeError):
            configured_layers = ()
        for index, widgets in getattr(
            self, "_custom_archetype_mask_layer_action_widgets", {}
        ).items():
            active = editable and int(index) < count
            for action, widget in widgets.items():
                enabled = active
                if action == "up":
                    enabled = enabled and int(index) > 0
                elif action == "down":
                    enabled = enabled and int(index) + 1 < count
                elif action == "duplicate":
                    enabled = enabled and count < MASK_LAYER_COUNT
                elif action == "delete":
                    enabled = enabled and count > 0
                elif action == "edit":
                    try:
                        enabled = enabled and str(
                            configured_layers[int(index)].get("type", "")
                        ) == "manual"
                    except (IndexError, AttributeError, TypeError):
                        enabled = False
                try:
                    widget.configure(state="normal" if enabled else "disabled")
                except tk.TclError:
                    pass

    def _custom_refresh_archetype_mask_layer_states(self) -> None:
        """Enable the provider-independent controls for every mask row."""

        editable = bool(getattr(self, "_custom_archetype_editor_editable", True))
        widgets_by_index = getattr(
            self, "_custom_archetype_mask_layer_setting_widgets", {}
        )
        for widgets in widgets_by_index.values():
            for widget in widgets.values():
                try:
                    widget.configure(state="normal" if editable else "disabled")
                except tk.TclError:
                    pass

    def _custom_archetype_mask_layer_count_changed(self) -> None:
        """Resize the independent mask stack without rebuilding the tab."""

        language = self._custom_language()
        config = None
        try:
            count = int(round(float(self._custom_archetype_mask_layer_count_var.get())))
            if not MASK_LAYER_COUNT_BOUNDS[0] <= count <= MASK_LAYER_COUNT_BOUNDS[1]:
                raise ValueError(
                    f"{MASK_LAYER_COUNT_BOUNDS[0]}..{MASK_LAYER_COUNT_BOUNDS[1]}"
                )
            config = self._custom_ensure_config(
                self._custom_current_mode()
                if self._custom_current_mode() in ("legacy", "upgraded")
                else None,
                self._custom_current_archetype(),
            )
            current = int(
                config.archetype_profile["morphology"].get("mask_layer_count", 0)
            )
            self._custom_refresh_archetype_mask_layer_cards(count)
            if count == current:
                return
            profile = deepcopy(config.archetype_profile)
            profile["morphology"]["mask_layer_count"] = count
            self._custom_activate_archetype(config.with_archetype_profile(profile))
            self._custom_refresh_archetype_mask_layer_action_states()
        except (AttributeError, KeyError, TypeError, ValueError) as exc:
            self._custom_status_var.set(
                _lang_text(
                    language,
                    f"Nombre de masques invalide : {exc}",
                    f"Invalid mask count: {exc}",
                    f"Ungültige Anzahl Masken: {exc}",
                    f"Número de máscaras no válido: {exc}",
                )
            )
            if config is not None:
                try:
                    current = int(
                        config.archetype_profile["morphology"].get(
                            "mask_layer_count", 0
                        )
                    )
                    self._custom_archetype_mask_layer_count_var.set(str(current))
                    self._custom_refresh_archetype_mask_layer_cards(current)
                except (KeyError, TypeError, ValueError, tk.TclError):
                    pass

    def _custom_archetype_mask_layer_changed(self, index: int) -> None:
        """Apply one independent shape-mask modulation layer."""

        language = self._custom_language()
        variables = self._custom_archetype_mask_layer_vars.get(int(index), {})
        config = None
        try:
            config = self._custom_ensure_config(
                self._custom_current_mode()
                if self._custom_current_mode() in ("legacy", "upgraded")
                else None,
                self._custom_current_archetype(),
            )
            profile = deepcopy(config.archetype_profile)
            layers = deepcopy(profile["morphology"].get("mask_layers", ()))
            type_options = self._custom_archetype_mask_type_options(language)
            operation_options = self._custom_archetype_mask_operation_options(language)
            mask_type = next(
                key for key, label in type_options.items()
                if label == variables["type"].get()
            )
            operation = next(
                key for key, label in operation_options.items()
                if label == variables["operation"].get()
            )
            current_layer = layers[int(index)]
            settings = {}
            for key in MASK_LAYER_COMMON_DEFAULTS:
                settings[key] = int(round(float(variables[key].get())))
            layers[int(index)] = {
                "enabled": bool(variables["enabled"].get()),
                "type": mask_type,
                "operation": operation,
                "strength_percent": int(round(float(variables["strength"].get()))),
                "order": int(current_layer.get("order", index)),
                "settings": settings,
                "provider_settings": deepcopy(
                    current_layer.get("provider_settings", {})
                ),
            }
            count = int(profile["morphology"].get("mask_layer_count", 0))
            self._custom_commit_archetype_mask_layer_stack(config, layers, count)
        except (KeyError, TypeError, ValueError) as exc:
            self._custom_status_var.set(
                _lang_text(
                    language,
                    f"Masque invalide : {exc}",
                    f"Invalid mask: {exc}",
                    f"Ungültige Maske: {exc}",
                    f"Máscara no válida: {exc}",
                )
            )
            if config is not None:
                self._custom_sync_archetype_mask_layer_variables()

    def _custom_archetype_mask_layer_edit(self, index: int) -> None:
        """Open the small deterministic editor for one freehand mask."""

        config = getattr(self, "_custom_config", None)
        if config is None:
            return
        try:
            profile = config.archetype_profile
            layers = profile["morphology"].get("mask_layers", ())
            layer = layers[int(index)]
            if str(layer.get("type", "")) != "manual":
                return
        except (AttributeError, KeyError, IndexError, TypeError):
            return

        side = MASK_LAYER_MANUAL_GRID_SIDE
        provider_settings = layer.get("provider_settings", {})
        raw_grid = (
            provider_settings.get("grid")
            if isinstance(provider_settings, dict)
            else None
        )
        if isinstance(raw_grid, (list, tuple)) and len(raw_grid) == side * side:
            try:
                grid = np.asarray(raw_grid, dtype=np.uint8).reshape(side, side).copy()
            except (TypeError, ValueError):
                grid = np.zeros((side, side), dtype=np.uint8)
        else:
            grid = np.zeros((side, side), dtype=np.uint8)

        language = self._custom_language()
        window = tk.Toplevel(self)
        window.title(
            _lang_text(
                language,
                f"Masque {int(index) + 1} — dessin libre",
                f"Mask {int(index) + 1} — freehand",
                f"Maske {int(index) + 1} — Freihand",
                f"Máscara {int(index) + 1} — dibujo libre",
            )
        )
        window.transient(self)
        window.resizable(False, False)
        theme_name = "dark" if self.prefs.get("theme", "dark") == "dark" else "light"
        theme_colors = getattr(
            self,
            "_ui_theme_colors",
            THEME_PALETTES.get(theme_name, THEME_PALETTES["dark"]),
        )
        window.configure(background=theme_colors.get("window", "#202124"))
        canvas_size = 384
        canvas = tk.Canvas(
            window,
            width=canvas_size,
            height=canvas_size,
            background=theme_colors.get("canvas", "#111214"),
            highlightthickness=1,
            highlightbackground=theme_colors.get("border", "#5f6368"),
            borderwidth=0,
        )
        canvas.grid(row=0, column=0, columnspan=2, padx=8, pady=(8, 4))
        image_state: dict[str, object] = {"photo": None, "item": None}
        brush_var = tk.StringVar(value="4")

        def redraw() -> None:
            image = Image.fromarray(grid, mode="L").resize(
                (canvas_size, canvas_size),
                Image.Resampling.NEAREST,
            ).convert("RGB")
            photo = ImageTk.PhotoImage(image, master=window)
            image_state["photo"] = photo
            item = image_state.get("item")
            if item is None:
                image_state["item"] = canvas.create_image(
                    0, 0, anchor="nw", image=photo
                )
            else:
                canvas.itemconfigure(item, image=photo)

        def brush_radius() -> int:
            try:
                return max(1, min(16, int(round(float(brush_var.get())))))
            except (TypeError, ValueError):
                return 4

        def paint(event: tk.Event, value: int) -> None:
            x = max(0, min(side - 1, int(round(event.x / canvas_size * (side - 1)))))
            y = max(0, min(side - 1, int(round(event.y / canvas_size * (side - 1)))))
            radius = brush_radius()
            rows, columns = np.ogrid[:side, :side]
            mask = (rows - y) ** 2 + (columns - x) ** 2 <= radius * radius
            grid[mask] = int(value)
            redraw()

        canvas.bind("<Button-1>", lambda event: paint(event, 255))
        canvas.bind("<B1-Motion>", lambda event: paint(event, 255))
        canvas.bind("<Button-3>", lambda event: paint(event, 0))
        canvas.bind("<B3-Motion>", lambda event: paint(event, 0))

        controls = ttk.Frame(window)
        controls.grid(row=1, column=0, columnspan=2, sticky="w", padx=8, pady=4)
        ttk.Label(
            controls,
            text=_lang_text(language, "Pinceau", "Brush", "Pinsel", "Pincel"),
        ).grid(row=0, column=0, sticky="w", padx=(0, 4))
        ttk.Spinbox(
            controls,
            from_=1,
            to=16,
            increment=1,
            textvariable=brush_var,
            width=4,
        ).grid(row=0, column=1, sticky="w", padx=(0, 8))

        def clear_grid() -> None:
            grid.fill(0)
            redraw()

        ttk.Button(
            controls,
            text=_lang_text(language, "Effacer", "Clear", "Leeren", "Borrar"),
            command=clear_grid,
            padding=(4, 1),
        ).grid(row=0, column=2, sticky="w", padx=(0, 4))

        def import_grid() -> None:
            path = filedialog.askopenfilename(
                parent=window,
                title=_lang_text(
                    language,
                    "Importer un masque en niveaux de gris",
                    "Import grayscale mask",
                    "Graustufenmaske importieren",
                    "Importar máscara en escala de grises",
                ),
                filetypes=(
                    (_lang_text(language, "Images", "Images", "Bilder", "Imágenes"), "*.png *.jpg *.jpeg *.bmp"),
                    (_lang_text(language, "Tous les fichiers", "All files", "Alle Dateien", "Todos los archivos"), "*.*"),
                ),
            )
            if not path:
                return
            try:
                imported = Image.open(path).convert("L").resize(
                    (side, side),
                    Image.Resampling.LANCZOS,
                )
                grid[:, :] = np.asarray(imported, dtype=np.uint8)
                redraw()
                self._custom_status_var.set(
                    _lang_text(
                        language,
                        "Masque importé dans l’éditeur ; cliquez sur Enregistrer pour l’appliquer.",
                        "Mask imported into the editor; click Save to apply it.",
                        "Maske importiert; zum Anwenden Speichern klicken.",
                        "Máscara importada; pulse Guardar para aplicarla.",
                    )
                )
            except (OSError, ValueError) as exc:
                self._custom_status_var.set(str(exc))

        ttk.Button(
            controls,
            text=_lang_text(language, "Importer", "Import", "Importieren", "Importar"),
            command=import_grid,
            padding=(4, 1),
        ).grid(row=0, column=3, sticky="w", padx=(0, 4))

        def export_grid() -> None:
            path = filedialog.asksaveasfilename(
                parent=window,
                defaultextension=".png",
                filetypes=(("PNG", "*.png"),),
                title=_lang_text(
                    language,
                    "Exporter le masque",
                    "Export mask",
                    "Maske exportieren",
                    "Exportar máscara",
                ),
            )
            if not path:
                return
            try:
                Image.fromarray(grid, mode="L").save(path)
                self._custom_status_var.set(
                    _lang_text(
                        language,
                        "Masque exporté.",
                        "Mask exported.",
                        "Maske exportiert.",
                        "Máscara exportada.",
                    )
                )
            except (OSError, ValueError) as exc:
                self._custom_status_var.set(str(exc))

        ttk.Button(
            controls,
            text=_lang_text(language, "Exporter", "Export", "Exportieren", "Exportar"),
            command=export_grid,
            padding=(4, 1),
        ).grid(row=0, column=4, sticky="w")
        ttk.Label(
            window,
            text=_lang_text(
                language,
                "Clic gauche : peindre · clic droit : effacer · gris = influence du masque",
                "Left click: paint · right click: erase · gray = mask influence",
                "Linksklick: malen · Rechtsklick: löschen · Grau = Maskeneinfluss",
                "Clic izquierdo: pintar · clic derecho: borrar · gris = influencia",
            ),
            style="Hint.TLabel",
        ).grid(row=2, column=0, columnspan=2, sticky="w", padx=8, pady=(0, 4))

        buttons = ttk.Frame(window)
        buttons.grid(row=3, column=0, columnspan=2, sticky="e", padx=8, pady=(4, 8))

        def save_grid() -> None:
            try:
                profile = deepcopy(config.archetype_profile)
                layers = deepcopy(profile["morphology"].get("mask_layers", ()))
                current = deepcopy(layers[int(index)])
                current_provider = current.get("provider_settings", {})
                provider = (
                    deepcopy(dict(current_provider))
                    if isinstance(current_provider, dict)
                    else {}
                )
                provider["grid"] = grid.reshape(-1).astype(np.uint8).tolist()
                provider["grid_side"] = side
                current["type"] = "manual"
                current["provider_settings"] = provider
                layers[int(index)] = current
                count = int(profile["morphology"].get("mask_layer_count", 0))
                self._custom_commit_archetype_mask_layer_stack(config, layers, count)
                window.destroy()
            except (AttributeError, IndexError, KeyError, TypeError, ValueError) as exc:
                self._custom_status_var.set(str(exc))

        ttk.Button(
            buttons,
            text=_lang_text(language, "Annuler", "Cancel", "Abbrechen", "Cancelar"),
            command=window.destroy,
            padding=(6, 1),
        ).grid(row=0, column=0, padx=(0, 4))
        ttk.Button(
            buttons,
            text=_lang_text(language, "Enregistrer", "Save", "Speichern", "Guardar"),
            command=save_grid,
            padding=(6, 1),
        ).grid(row=0, column=1)
        window.protocol("WM_DELETE_WINDOW", window.destroy)
        redraw()
        window.grab_set()
        window.focus_set()

    def _custom_archetype_mask_layer_reorder(self, index: int, direction: int) -> None:
        config = getattr(self, "_custom_config", None)
        if config is None:
            return
        try:
            profile = config.archetype_profile
            count = int(profile["morphology"].get("mask_layer_count", 0))
            layers = reorder_mask_layers(
                profile["morphology"].get("mask_layers", ()),
                count,
                index,
                direction,
            )
            self._custom_commit_archetype_mask_layer_stack(config, layers, count)
        except (IndexError, TypeError, ValueError) as exc:
            self._custom_status_var.set(str(exc))

    def _custom_archetype_mask_layer_duplicate(self, index: int) -> None:
        config = getattr(self, "_custom_config", None)
        if config is None:
            return
        try:
            profile = config.archetype_profile
            count = int(profile["morphology"].get("mask_layer_count", 0))
            layers, count = duplicate_mask_layer(
                profile["morphology"].get("mask_layers", ()),
                count,
                index,
            )
            self._custom_commit_archetype_mask_layer_stack(config, layers, count)
        except (IndexError, TypeError, ValueError) as exc:
            self._custom_status_var.set(str(exc))

    def _custom_archetype_mask_layer_remove(self, index: int) -> None:
        config = getattr(self, "_custom_config", None)
        if config is None:
            return
        try:
            profile = config.archetype_profile
            count = int(profile["morphology"].get("mask_layer_count", 0))
            layers, count = remove_mask_layer(
                profile["morphology"].get("mask_layers", ()),
                count,
                index,
            )
            self._custom_commit_archetype_mask_layer_stack(config, layers, count)
        except (IndexError, TypeError, ValueError) as exc:
            self._custom_status_var.set(str(exc))

    def _custom_activate_archetype(self, config: CustomGenerationConfig) -> None:
        """Commit an archetype edit without changing the Generator selector."""

        previous = getattr(self, "_custom_config", None)
        refresh_main = (
            previous is None
            or previous.base_archetype != config.base_archetype
            or _archetype_effective_preview_profile(
                previous.archetype_profile
            )
            != _archetype_effective_preview_profile(config.archetype_profile)
        )
        self._custom_config = config
        self._custom_last_concrete_archetype = config.base_archetype
        self._custom_last_render_digest = config.digest
        if self._custom_current_mode() == "custom" and hasattr(
            self, "_custom_provenance_var"
        ):
            self._custom_render_custom_mode(config)
        self._custom_refresh_archetype_header()
        self._custom_refresh_archetype_ranges()
        self._custom_refresh_archetype_section_reset_buttons()
        self._custom_status_var.set(
            _lang_text(
                self._custom_language(),
                "Archétype personnalisé actif · mode Générateur inchangé.",
                "Custom archetype active · Generator mode unchanged.",
                "Benutzerdefinierter Archetyp aktiv · Generatormodus unverändert.",
                "Arquetipo personalizado activo · modo Generador sin cambios.",
            )
        )
        self._custom_schedule_archetype_preview_refresh(
            refresh_main=refresh_main
        )

    def _custom_archetype_changed(self, path, raw) -> None:
        """Apply one macro-layout parameter and enter Custom in place."""

        language = self._custom_language()
        config = None
        variable = self._custom_archetype_vars.get(".".join(path))
        try:
            value = int(round(float(str(raw).strip())))
            config = self._custom_ensure_config(
                self._custom_current_mode()
                if self._custom_current_mode() in ("legacy", "upgraded")
                else None,
                self._custom_current_archetype(),
            )
            current_value = int(round(float(get_path(config.archetype_profile, path))))
            if value == current_value:
                return
            self._custom_activate_archetype(config.with_archetype_value(path, value))
        except (TypeError, ValueError) as exc:
            self._custom_status_var.set(
                _lang_text(
                    language,
                    f"Valeur d’archétype invalide : {exc}",
                    f"Invalid archetype value: {exc}",
                    f"Ungültiger Archetypwert: {exc}",
                    f"Valor de arquetipo no válido: {exc}",
                )
            )
            if variable is not None and config is not None:
                try:
                    variable.set(str(get_path(config.archetype_profile, path)))
                except (KeyError, TypeError, ValueError):
                    pass

    def _custom_refresh_archetype_noise_layer_cards(self, count: int) -> None:
        """Show the requested fusion slots while retaining hidden settings."""

        count = max(NOISE_LAYER_COUNT_BOUNDS[0], min(NOISE_LAYER_COUNT, int(count)))
        for index, card in getattr(
            self,
            "_custom_archetype_noise_layer_cards",
            {},
        ).items():
            try:
                if int(index) < count:
                    card.grid(
                        row=int(index) + 3,
                        column=0,
                        sticky="nw",
                        pady=(0, 6),
                    )
                else:
                    card.grid_remove()
            except tk.TclError:
                pass
        self._custom_refresh_archetype_noise_layer_action_states()

    def _custom_archetype_size_adaptive_frequency_changed(self) -> None:
        """Commit the profile-level frequency scaling switch."""

        config = getattr(self, "_custom_config", None)
        variable = getattr(
            self,
            "_custom_archetype_size_adaptive_frequency_var",
            None,
        )
        if config is None or variable is None:
            return
        try:
            enabled = bool(variable.get())
            current = bool(
                config.archetype_profile["morphology"].get(
                    "size_adaptive_frequency",
                    False,
                )
            )
            if enabled == current:
                return
            profile = deepcopy(config.archetype_profile)
            profile["morphology"]["size_adaptive_frequency"] = enabled
            self._custom_activate_archetype(
                config.with_archetype_profile(profile)
            )
        except (AttributeError, KeyError, TypeError, ValueError) as exc:
            self._custom_status_var.set(
                _lang_text(
                    self._custom_language(),
                    f"Réglage d’échelle invalide : {exc}",
                    f"Invalid scale setting: {exc}",
                    f"Ungültige Skalierungseinstellung: {exc}",
                    f"Ajuste de escala no válido: {exc}",
                )
            )
            try:
                variable.set(
                    bool(
                        config.archetype_profile["morphology"].get(
                            "size_adaptive_frequency",
                            False,
                        )
                    )
                )
            except (AttributeError, KeyError, TypeError, tk.TclError):
                pass

    def _custom_sync_archetype_noise_layer_variables(self) -> None:
        """Synchronize persistent Tk variables after a stack edit."""

        config = getattr(self, "_custom_config", None)
        if config is None:
            return
        try:
            layers = config.archetype_profile["morphology"]["noise_layers"]
        except (KeyError, TypeError):
            return
        language = self._custom_language()
        family_options = self._custom_archetype_noise_family_options(language)
        operation_options = self._custom_archetype_noise_operation_options(language)
        for index, variables in getattr(
            self,
            "_custom_archetype_noise_layer_vars",
            {},
        ).items():
            try:
                layer = layers[int(index)]
                variables["enabled"].set(bool(layer["enabled"]))
                variables["family"].set(family_options[str(layer["family"])] )
                variables["operation"].set(operation_options[str(layer["operation"])] )
                variables["strength"].set(str(layer["strength_percent"]))
                settings = layer.get("settings", {})
                for key, default in NOISE_SOURCE_SETTING_DEFAULTS.items():
                    value = settings.get(key, default)
                    number = float(value)
                    variables[key].set(
                        str(int(number)) if number.is_integer() else f"{number:g}"
                    )
                mask_settings = layer.get("mask_settings", NOISE_MASK_DEFAULTS)
                mask_options = self._custom_archetype_noise_mask_options(language)
                for key, default in NOISE_MASK_DEFAULTS.items():
                    variable = variables.get(f"mask_{key}")
                    if variable is None:
                        continue
                    value = mask_settings.get(key, default)
                    if key == "type":
                        value = mask_options[str(value)]
                    elif key == "source":
                        value = family_options[str(value)]
                    variable.set(
                        self._custom_archetype_display_number(value)
                        if isinstance(value, (int, float))
                        else str(value)
                    )
            except (KeyError, IndexError, TypeError, ValueError, tk.TclError):
                continue

    def _custom_commit_archetype_noise_layer_stack(
        self,
        config: CustomGenerationConfig,
        layers,
        count: int,
    ) -> None:
        """Persist one complete stack edit and refresh only dependent widgets."""

        profile = deepcopy(config.archetype_profile)
        profile["morphology"]["noise_layers"] = deepcopy(list(layers))
        profile["morphology"]["noise_layer_count"] = int(count)
        self._custom_activate_archetype(config.with_archetype_profile(profile))
        self._custom_archetype_noise_layer_count_var.set(str(int(count)))
        self._custom_sync_archetype_noise_layer_variables()
        self._custom_refresh_archetype_noise_layer_cards(int(count))
        self._custom_refresh_archetype_noise_setting_states()
        self._custom_refresh_archetype_noise_layer_action_states()

    def _custom_refresh_archetype_noise_layer_action_states(self) -> None:
        """Keep stack actions bounded to visible, editable fusion slots."""

        try:
            count = int(self._custom_archetype_noise_layer_count_var.get())
        except (AttributeError, TypeError, ValueError):
            count = 0
        count = max(NOISE_LAYER_COUNT_BOUNDS[0], min(NOISE_LAYER_COUNT, count))
        editable = bool(getattr(self, "_custom_archetype_editor_editable", True))
        solo = getattr(self, "_custom_archetype_noise_layer_solo", None)
        if solo is not None and not 0 <= int(solo) < count:
            self._custom_archetype_noise_layer_solo = None
            solo = None
        try:
            configured_layers = self._custom_config.archetype_profile["morphology"][
                "noise_layers"
            ]
        except (AttributeError, KeyError, TypeError):
            configured_layers = ()
        if solo is not None:
            try:
                solo_layer = configured_layers[int(solo)]
                solo_enabled = bool(solo_layer.get("enabled", False)) and int(
                    solo_layer.get("strength_percent", 0)
                ) > 0
            except (IndexError, KeyError, TypeError, ValueError):
                solo_enabled = False
            if not solo_enabled:
                self._custom_archetype_noise_layer_solo = None
                solo = None
        language = self._custom_language()
        for index, widgets in getattr(
            self,
            "_custom_archetype_noise_layer_action_widgets",
            {},
        ).items():
            active = editable and int(index) < count
            try:
                layer = configured_layers[int(index)]
                layer_enabled = bool(layer.get("enabled", False)) and int(
                    layer.get("strength_percent", 0)
                ) > 0
            except (IndexError, KeyError, TypeError, ValueError):
                layer_enabled = False
            states = {
                "up": active and int(index) > 0,
                "down": active and int(index) + 1 < count,
                "duplicate": active and count < NOISE_LAYER_COUNT,
                "delete": active,
                "solo": active and layer_enabled,
            }
            for action, widget in widgets.items():
                try:
                    widget.configure(state="normal" if states.get(action, False) else "disabled")
                except tk.TclError:
                    pass
            solo_button = widgets.get("solo")
            if solo_button is not None:
                try:
                    solo_button.configure(
                        text=(
                            _lang_text(
                                language,
                                "Quitter solo",
                                "Exit solo",
                                "Solo beenden",
                                "Salir de solo",
                            )
                            if solo == int(index)
                            else _lang_text(
                                language,
                                "Solo",
                                "Solo",
                                "Solo",
                                "Solo",
                            )
                        )
                    )
                except tk.TclError:
                    pass

    def _custom_archetype_noise_layer_reorder(
        self,
        index: int,
        direction: int,
    ) -> None:
        """Move one fusion and keep Solo attached to the same layer."""

        config = None
        try:
            config = self._custom_ensure_config(
                self._custom_current_mode()
                if self._custom_current_mode() in ("legacy", "upgraded")
                else None,
                self._custom_current_archetype(),
            )
            count = int(config.archetype_profile["morphology"]["noise_layer_count"])
            target = int(index) + int(direction)
            solo = getattr(self, "_custom_archetype_noise_layer_solo", None)
            layers = reorder_noise_layers(
                config.archetype_profile["morphology"]["noise_layers"],
                count,
                int(index),
                int(direction),
            )
            if solo == int(index):
                self._custom_archetype_noise_layer_solo = target
            elif solo == target:
                self._custom_archetype_noise_layer_solo = int(index)
            self._custom_commit_archetype_noise_layer_stack(config, layers, count)
        except (KeyError, TypeError, ValueError, IndexError) as exc:
            self._custom_status_var.set(
                _lang_text(
                    self._custom_language(),
                    f"Réorganisation impossible : {exc}",
                    f"Unable to reorder fusions: {exc}",
                    f"Fusionen konnten nicht neu geordnet werden: {exc}",
                    f"No se pueden reordenar las fusiones: {exc}",
                )
            )

    def _custom_archetype_noise_layer_duplicate(self, index: int) -> None:
        """Insert a copy immediately after a fusion card."""

        try:
            config = self._custom_ensure_config(
                self._custom_current_mode()
                if self._custom_current_mode() in ("legacy", "upgraded")
                else None,
                self._custom_current_archetype(),
            )
            count = int(config.archetype_profile["morphology"]["noise_layer_count"])
            solo = getattr(self, "_custom_archetype_noise_layer_solo", None)
            layers, new_count = duplicate_noise_layer(
                config.archetype_profile["morphology"]["noise_layers"],
                count,
                int(index),
            )
            if solo is not None and solo > int(index):
                self._custom_archetype_noise_layer_solo = int(solo) + 1
            self._custom_commit_archetype_noise_layer_stack(config, layers, new_count)
        except (KeyError, TypeError, ValueError, IndexError) as exc:
            self._custom_status_var.set(
                _lang_text(
                    self._custom_language(),
                    f"Duplication impossible : {exc}",
                    f"Unable to duplicate fusion: {exc}",
                    f"Fusion konnte nicht dupliziert werden: {exc}",
                    f"No se puede duplicar la fusión: {exc}",
                )
            )

    def _custom_archetype_noise_layer_remove(self, index: int) -> None:
        """Remove a fusion, compacting the visible stack."""

        try:
            config = self._custom_ensure_config(
                self._custom_current_mode()
                if self._custom_current_mode() in ("legacy", "upgraded")
                else None,
                self._custom_current_archetype(),
            )
            count = int(config.archetype_profile["morphology"]["noise_layer_count"])
            solo = getattr(self, "_custom_archetype_noise_layer_solo", None)
            layers, new_count = remove_noise_layer(
                config.archetype_profile["morphology"]["noise_layers"],
                count,
                int(index),
            )
            if solo == int(index):
                self._custom_archetype_noise_layer_solo = None
            elif solo is not None and solo > int(index):
                self._custom_archetype_noise_layer_solo = int(solo) - 1
            self._custom_commit_archetype_noise_layer_stack(config, layers, new_count)
        except (KeyError, TypeError, ValueError, IndexError) as exc:
            self._custom_status_var.set(
                _lang_text(
                    self._custom_language(),
                    f"Suppression impossible : {exc}",
                    f"Unable to delete fusion: {exc}",
                    f"Fusion konnte nicht gelöscht werden: {exc}",
                    f"No se puede eliminar la fusión: {exc}",
                )
            )

    def _custom_archetype_noise_layer_solo_changed(self, index: int) -> None:
        """Toggle a preview-only single-fusion focus."""

        variables = getattr(self, "_custom_archetype_noise_layer_vars", {}).get(
            int(index),
            {},
        )
        try:
            if not bool(variables["enabled"].get()) or int(
                round(float(variables["strength"].get()))
            ) <= 0:
                self._custom_archetype_noise_layer_solo = None
                self._custom_refresh_archetype_noise_layer_action_states()
                self._custom_schedule_archetype_preview_refresh()
                return
        except (KeyError, TypeError, ValueError):
            self._custom_archetype_noise_layer_solo = None
            self._custom_refresh_archetype_noise_layer_action_states()
            return
        current = getattr(self, "_custom_archetype_noise_layer_solo", None)
        self._custom_archetype_noise_layer_solo = None if current == int(index) else int(index)
        self._custom_refresh_archetype_noise_layer_action_states()
        self._custom_schedule_archetype_preview_refresh()

    def _custom_archetype_noise_layer_count_changed(self) -> None:
        """Resize the visible fusion stack without rebuilding preview widgets."""

        language = self._custom_language()
        config = None
        try:
            count = int(
                round(float(self._custom_archetype_noise_layer_count_var.get()))
            )
            if not NOISE_LAYER_COUNT_BOUNDS[0] <= count <= NOISE_LAYER_COUNT_BOUNDS[1]:
                raise ValueError(
                    f"{NOISE_LAYER_COUNT_BOUNDS[0]}..{NOISE_LAYER_COUNT_BOUNDS[1]}"
                )
            config = self._custom_ensure_config(
                self._custom_current_mode()
                if self._custom_current_mode() in ("legacy", "upgraded")
                else None,
                self._custom_current_archetype(),
            )
            current = int(
                config.archetype_profile["morphology"]["noise_layer_count"]
            )
            self._custom_refresh_archetype_noise_layer_cards(count)
            if (
                self._custom_archetype_noise_layer_solo is not None
                and self._custom_archetype_noise_layer_solo >= count
            ):
                self._custom_archetype_noise_layer_solo = None
            if count == current:
                self._custom_refresh_archetype_noise_layer_action_states()
                return
            profile = deepcopy(config.archetype_profile)
            profile["morphology"]["noise_layer_count"] = count
            self._custom_activate_archetype(config.with_archetype_profile(profile))
            self._custom_refresh_archetype_noise_layer_action_states()
        except (AttributeError, KeyError, TypeError, ValueError) as exc:
            self._custom_status_var.set(
                _lang_text(
                    language,
                    f"Nombre de fusions invalide : {exc}",
                    f"Invalid fusion count: {exc}",
                    f"Ungültige Anzahl Fusionen: {exc}",
                    f"Número de fusiones no válido: {exc}",
                )
            )
            if config is not None:
                try:
                    current = int(
                        config.archetype_profile["morphology"]["noise_layer_count"]
                    )
                    self._custom_archetype_noise_layer_count_var.set(str(current))
                    self._custom_refresh_archetype_noise_layer_cards(current)
                    self._custom_refresh_archetype_noise_layer_action_states()
                except (KeyError, TypeError, ValueError, tk.TclError):
                    pass

    def _custom_archetype_noise_layer_changed(self, index: int) -> None:
        """Apply one optional procedural noise layer without rebuilding the tab."""

        language = self._custom_language()
        variables = self._custom_archetype_noise_layer_vars.get(int(index), {})
        config = None
        try:
            config = self._custom_ensure_config(
                self._custom_current_mode()
                if self._custom_current_mode() in ("legacy", "upgraded")
                else None,
                self._custom_current_archetype(),
            )
            profile = deepcopy(config.archetype_profile)
            layers = deepcopy(profile["morphology"]["noise_layers"])
            family_options = self._custom_archetype_noise_family_options(language)
            operation_options = self._custom_archetype_noise_operation_options(language)
            family = next(
                key for key, label in family_options.items()
                if label == variables["family"].get()
            )
            operation = next(
                key for key, label in operation_options.items()
                if label == variables["operation"].get()
            )
            current_layer = layers[int(index)]
            settings = {}
            for key, default in NOISE_SOURCE_SETTING_DEFAULTS.items():
                raw_value = variables[key].get()
                numeric = float(raw_value)
                settings[key] = int(round(numeric)) if isinstance(default, int) else numeric
            mask_options = self._custom_archetype_noise_mask_options(language)
            mask_source_options = self._custom_archetype_noise_family_options(language)
            mask_settings = {}
            for key, default in NOISE_MASK_DEFAULTS.items():
                raw_value = variables[f"mask_{key}"].get()
                if key == "type":
                    value = next(
                        mask_key
                        for mask_key, label in mask_options.items()
                        if label == raw_value
                    )
                elif key == "source":
                    value = next(
                        source_key
                        for source_key, label in mask_source_options.items()
                        if label == raw_value
                    )
                else:
                    value = int(round(float(raw_value)))
                mask_settings[key] = value
            layers[int(index)] = {
                "enabled": bool(variables["enabled"].get()),
                "source": family,
                "family": family,
                "role": "full_field",
                "mask": "finite_domain",
                "operation": operation,
                "stage": "source_composition",
                "order": int(current_layer.get("order", index)),
                "scale_percent": int(round(float(settings["frequency"]))),
                "strength_percent": int(round(float(variables["strength"].get()))),
                "mask_settings": mask_settings,
                "settings": settings,
            }
            profile["morphology"]["noise_layers"] = layers
            if self._custom_archetype_noise_layer_solo == int(index) and not (
                bool(layers[int(index)]["enabled"])
                and int(layers[int(index)]["strength_percent"]) > 0
            ):
                self._custom_archetype_noise_layer_solo = None
            self._custom_activate_archetype(config.with_archetype_profile(profile))
            self._custom_refresh_archetype_noise_setting_states()
            self._custom_refresh_archetype_noise_layer_action_states()
        except (KeyError, TypeError, ValueError) as exc:
            self._custom_status_var.set(
                _lang_text(
                    language,
                    f"Couche de bruit invalide : {exc}",
                    f"Invalid noise layer: {exc}",
                    f"Ungültige Rauschschicht: {exc}",
                    f"Capa de ruido no válida: {exc}",
                )
            )
            if config is not None:
                try:
                    layer = config.archetype_profile["morphology"]["noise_layers"][int(index)]
                    family_options = self._custom_archetype_noise_family_options(language)
                    operation_options = self._custom_archetype_noise_operation_options(language)
                    variables["enabled"].set(bool(layer["enabled"]))
                    variables["family"].set(family_options[str(layer["family"])])
                    variables["operation"].set(operation_options[str(layer["operation"])])
                    variables["strength"].set(str(layer["strength_percent"]))
                    for key, value in layer["settings"].items():
                        variables[key].set(str(value))
                    mask_settings = layer.get("mask_settings", NOISE_MASK_DEFAULTS)
                    mask_options = self._custom_archetype_noise_mask_options(language)
                    for key, default in NOISE_MASK_DEFAULTS.items():
                        value = mask_settings.get(key, default)
                        if key == "type":
                            value = mask_options[str(value)]
                        elif key == "source":
                            value = self._custom_archetype_noise_family_options(language)[str(value)]
                        variables[f"mask_{key}"].set(str(value))
                except (KeyError, IndexError, TypeError, ValueError):
                    pass

    def _custom_refresh_archetype_noise_setting_states(
        self,
        primary_source: str | None = None,
    ) -> None:
        """Disable controls that the selected noise family does not consume."""

        editable = bool(getattr(self, "_custom_archetype_editor_editable", True))
        if primary_source is None:
            config = getattr(self, "_custom_config", None)
            if config is not None:
                try:
                    primary_source = str(
                        config.archetype_profile["morphology"].get(
                            "relief_source",
                            RELIEF_SOURCE_DEFAULT,
                        )
                    )
                except (KeyError, TypeError, AttributeError):
                    primary_source = RELIEF_SOURCE_DEFAULT
            else:
                primary_source = RELIEF_SOURCE_DEFAULT
        primary_source = str(primary_source)
        is_legacy_source = primary_source in {
            RELIEF_SOURCE_DEFAULT,
            RELIEF_SOURCE_CUSTOM_LEGACY,
        }
        uses_complete_noise_source = not is_legacy_source
        shape_scale_widget = getattr(self, "_custom_archetype_spinboxes", {}).get(
            "morphology.shape_scale_percent"
        )
        if shape_scale_widget is not None:
            try:
                shape_scale_widget.configure(
                    state=(
                        "disabled"
                        if primary_source == RELIEF_SOURCE_CUSTOM_LEGACY
                        else "normal" if editable else "disabled"
                    )
                )
            except tk.TclError:
                pass

        primary_widgets = getattr(
            self,
            "_custom_archetype_relief_setting_widget_map",
            {},
        )
        mask_options = self._custom_archetype_noise_mask_options(self._custom_language())
        mask_variables = getattr(self, "_custom_archetype_relief_mask_vars", {})
        mask_label = mask_variables.get("type").get() if mask_variables.get("type") else ""
        mask_type = next(
            (key for key, value in mask_options.items() if value == mask_label),
            "none",
        )
        for setting_key, widget in primary_widgets.items():
            if setting_key.startswith("mask_"):
                mask_key = setting_key[5:]
                applies = uses_complete_noise_source
                if mask_key in {"source", "seed_offset"}:
                    applies = applies and mask_type == "noise"
                elif mask_key == "angle_degrees":
                    applies = applies and mask_type == "direction"
            else:
                applies = (
                    uses_complete_noise_source
                    and noise_source_setting_applies(primary_source, setting_key)
                )
            try:
                widget.configure(state="normal" if editable and applies else "disabled")
            except tk.TclError:
                pass

        # Frame margin and edge falloff belong to the finite independent
        # source domain. They do not constrain either native-derived source.
        for key in (
            "native_coarse_variation_percent",
            "native_refinement_percent",
            "native_large_scale_refinement_percent",
            "native_fine_scale_refinement_percent",
            "native_sculpture_attempts_percent",
            "native_relaxation_strength_percent",
        ):
            widget = getattr(self, "_custom_archetype_spinboxes", {}).get(
                f"morphology.{key}"
            )
            if widget is None:
                continue
            try:
                widget.configure(
                    state="normal" if editable and is_legacy_source else "disabled"
                )
            except tk.TclError:
                pass

        # These settings describe the finite rectangle used only by complete
        # independent providers.
        for setting_key in (
            "morphology.frame_margin_percent",
            "morphology.edge_falloff_percent",
        ):
            widget = getattr(self, "_custom_archetype_spinboxes", {}).get(setting_key)
            if widget is None:
                continue
            applies = uses_complete_noise_source
            try:
                widget.configure(state="normal" if editable and applies else "disabled")
            except tk.TclError:
                pass

        family_options = self._custom_archetype_noise_family_options(
            self._custom_language()
        )
        for index, widgets in getattr(
            self,
            "_custom_archetype_noise_layer_setting_widgets",
            {},
        ).items():
            variables = getattr(self, "_custom_archetype_noise_layer_vars", {}).get(
                index,
                {},
            )
            label = variables.get("family").get() if variables.get("family") else ""
            source = next(
                (key for key, value in family_options.items() if value == label),
                "",
            )
            mask_options = self._custom_archetype_noise_mask_options(self._custom_language())
            mask_label = variables.get("mask_type").get() if variables.get("mask_type") else ""
            mask_type = next(
                (key for key, value in mask_options.items() if value == mask_label),
                "none",
            )
            for setting_key, widget in widgets.items():
                if setting_key.startswith("mask_"):
                    mask_key = setting_key[5:]
                    applies = True
                    if mask_key in {"source", "seed_offset"}:
                        applies = mask_type == "noise"
                    elif mask_key == "angle_degrees":
                        applies = mask_type == "direction"
                else:
                    applies = noise_source_setting_applies(source, setting_key)
                try:
                    widget.configure(
                        state="normal" if editable and applies else "disabled"
                    )
                except tk.TclError:
                    pass

    def _custom_refresh_archetype_shape_states(self) -> None:
        """Enable only the parameters consumed by the selected shape."""

        editable = bool(getattr(self, "_custom_archetype_editor_editable", True))
        variables = getattr(self, "_custom_archetype_shape_vars", {})
        widgets = getattr(self, "_custom_archetype_shape_widgets", {})
        options = self._custom_archetype_shape_options(self._custom_language())
        label = variables.get("type").get() if variables.get("type") else ""
        shape_type = next(
            (key for key, value in options.items() if value == label),
            "none",
        )
        common = {
            "width_percent",
            "height_percent",
            "offset_x_percent",
            "offset_y_percent",
            "rotation_degrees",
            "softness_percent",
        }
        specific = {
            "star": {"points", "inner_radius_percent"},
            "ring": {"thickness_percent"},
            "dome": {"crater_percent", "relief_percent"},
        }
        for key, widget in widgets.items():
            applies = key == "type" or (
                shape_type != "none"
                and (key in common or key in specific.get(shape_type, set()))
            )
            try:
                if isinstance(widget, ttk.Combobox):
                    widget.configure(
                        state="readonly" if editable and applies else "disabled"
                    )
                else:
                    widget.configure(state="normal" if editable and applies else "disabled")
            except tk.TclError:
                pass

    def _custom_archetype_shape_changed(self) -> None:
        """Commit the archetype-level parametric shape template."""

        language = self._custom_language()
        config = None
        try:
            config = self._custom_ensure_config(
                self._custom_current_mode()
                if self._custom_current_mode() in ("legacy", "upgraded")
                else None,
                self._custom_current_archetype(),
            )
            variables = getattr(self, "_custom_archetype_shape_vars", {})
            options = self._custom_archetype_shape_options(language)
            shape_type = next(
                key for key, label in options.items() if label == variables["type"].get()
            )
            settings: dict[str, int | str] = {"type": shape_type}
            for key, default in SHAPE_TEMPLATE_DEFAULTS.items():
                if key == "type":
                    continue
                settings[key] = int(round(float(variables[key].get())))
            profile = deepcopy(config.archetype_profile)
            current = profile["morphology"].get(
                "shape_template", SHAPE_TEMPLATE_DEFAULTS
            )
            if current == settings:
                self._custom_refresh_archetype_shape_states()
                return
            profile["morphology"]["shape_template"] = settings
            self._custom_activate_archetype(config.with_archetype_profile(profile))
            self._custom_refresh_archetype_shape_states()
        except (AttributeError, KeyError, TypeError, ValueError) as exc:
            self._custom_status_var.set(
                _lang_text(
                    language,
                    f"Gabarit de forme invalide : {exc}",
                    f"Invalid shape template: {exc}",
                    f"Ungültiges Formgitter: {exc}",
                    f"Plantilla de forma no válida: {exc}",
                )
            )
            if config is not None:
                self._custom_sync_archetype_editor_values()

    def _custom_archetype_relief_source_changed(self) -> None:
        """Select the complete raw elevation source for the archetype."""

        language = self._custom_language()
        config = None
        variable = getattr(self, "_custom_archetype_relief_source_var", None)
        try:
            config = self._custom_ensure_config(
                self._custom_current_mode()
                if self._custom_current_mode() in ("legacy", "upgraded")
                else None,
                self._custom_current_archetype(),
            )
            profile = deepcopy(config.archetype_profile)
            source_options = self._custom_archetype_relief_source_options(language)
            source = next(
                key for key, label in source_options.items()
                if label == variable.get()
            )
            self._custom_refresh_archetype_noise_setting_states(source)
            current = str(
                profile["morphology"].get(
                    "relief_source",
                    RELIEF_SOURCE_DEFAULT,
                )
            )
            if source == current:
                current_settings = profile["morphology"].get(
                    "relief_source_settings", NOISE_SOURCE_SETTING_DEFAULTS
                )
            else:
                current_settings = None
                thresholds = profile["relief"]
                mountain, snow = thresholds_on_relief_source_change(
                    current, source,
                    thresholds["mountain_threshold"], thresholds["snow_threshold"],
                )
                thresholds["mountain_threshold"] = mountain
                thresholds["snow_threshold"] = snow
            profile["morphology"]["relief_source"] = source
            settings = {}
            variables = getattr(self, "_custom_archetype_relief_source_vars", {})
            for key, default in NOISE_SOURCE_SETTING_DEFAULTS.items():
                numeric = float(variables[key].get())
                settings[key] = int(round(numeric)) if isinstance(default, int) else numeric
            mask_options = self._custom_archetype_noise_mask_options(language)
            mask_source_options = self._custom_archetype_noise_family_options(language)
            mask_settings = {}
            mask_variables = getattr(self, "_custom_archetype_relief_mask_vars", {})
            for key, default in NOISE_MASK_DEFAULTS.items():
                raw_value = mask_variables[key].get()
                if key == "type":
                    value = next(
                        mask_key
                        for mask_key, label in mask_options.items()
                        if label == raw_value
                    )
                elif key == "source":
                    value = next(
                        source_key
                        for source_key, label in mask_source_options.items()
                        if label == raw_value
                    )
                else:
                    value = int(round(float(raw_value)))
                mask_settings[key] = value
            current_mask = profile["morphology"].get(
                "relief_source_mask", NOISE_MASK_DEFAULTS
            )
            if (
                current_settings == settings
                and current_mask == mask_settings
                and source == current
            ):
                return
            profile["morphology"]["relief_source_settings"] = settings
            profile["morphology"]["relief_source_mask"] = mask_settings
            self._custom_activate_archetype(config.with_archetype_profile(profile))
        except (AttributeError, KeyError, TypeError, ValueError) as exc:
            self._custom_status_var.set(
                _lang_text(
                    language,
                    f"Source de relief invalide : {exc}",
                    f"Invalid relief source: {exc}",
                    f"Ungültige Reliefquelle: {exc}",
                    f"Fuente de relieve no válida: {exc}",
                )
            )
            if config is not None and variable is not None:
                try:
                    current = str(
                        config.archetype_profile["morphology"].get(
                            "relief_source",
                            RELIEF_SOURCE_DEFAULT,
                        )
                    )
                    variable.set(
                        self._custom_archetype_relief_source_options(language)[current]
                    )
                    mask_options = self._custom_archetype_noise_mask_options(language)
                    mask_source_options = self._custom_archetype_noise_family_options(language)
                    mask_settings = config.archetype_profile["morphology"].get(
                        "relief_source_mask", NOISE_MASK_DEFAULTS
                    )
                    for key, default in NOISE_MASK_DEFAULTS.items():
                        value = mask_settings.get(key, default)
                        if key == "type":
                            value = mask_options[str(value)]
                        elif key == "source":
                            value = mask_source_options[str(value)]
                        self._custom_archetype_relief_mask_vars[key].set(str(value))
                except (KeyError, TypeError, ValueError):
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
        self._custom_layout_generation = getattr(self, "_custom_layout_generation", 0) + 1
        layout_generation = self._custom_layout_generation
        self._custom_clear_preview_size_trace()
        config = self._custom_profile_for_display()
        generator_scroll_position = self._custom_generator_scroll_position()
        root = self._custom_generator_tab
        for child in root.winfo_children():
            child.destroy()
        root.columnconfigure(0, weight=0)
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
            try:
                if not shell.winfo_exists() or not body.winfo_exists():
                    return 0
                return max(shell.winfo_reqwidth(), body.winfo_reqwidth())
            except tk.TclError:
                return 0

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
            # A parameter/language/mode refresh can destroy these widgets
            # before Tk delivers the queued idle callback from the previous
            # render.  Never let that stale callback inspect old Tcl paths.
            if layout_generation != getattr(self, "_custom_layout_generation", None):
                return
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
            try:
                if any(
                    not shell.winfo_exists() or not body.winfo_exists()
                    for shell, body in section_layout_frames.values()
                ):
                    return
            except tk.TclError:
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
            try:
                panel = bonus_panel_frames[key]
                return panel.winfo_reqwidth() if panel.winfo_exists() else 0
            except tk.TclError:
                return 0

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
            if layout_generation != getattr(self, "_custom_layout_generation", None):
                return
            if len(bonus_panel_frames) != 5:
                return
            try:
                available_width = max(0, root.winfo_width() - 28)
            except tk.TclError:
                return
            if available_width <= 1:
                return
            try:
                if any(not panel.winfo_exists() for panel in bonus_panel_frames.values()):
                    return
            except tk.TclError:
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
        self._custom_refresh_archetype_header()
        self._custom_refresh_archetype_ranges()
        self._custom_schedule_archetype_preview_refresh()

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
                or archetype_changed
                or self._custom_config.base_mode != mode
                or self._custom_config.base_archetype != arch
            ):
                # A newly selected built-in generator is the source profile
                # displayed by the editor.  Do not leave an older Custom
                # derivative silently attached to the selector.
                previous = self._custom_config
                next_config = self._custom_preset_config(mode, arch)
                if (
                    previous is not None
                    and not archetype_changed
                    and previous.base_archetype == arch
                    and previous.archetype_profile != default_archetype_profile(arch)
                ):
                    next_config = next_config.with_archetype_profile(
                        previous.archetype_profile
                    )
                self._custom_config = next_config
        elif mode == "custom":
            config = self._custom_ensure_config()
            if config.base_archetype != arch:
                self._custom_config = config.with_archetype_profile(
                    default_archetype_profile(arch),
                    base_archetype=arch,
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
        self._custom_clear_archetype_preview_traces()
        for child in root.winfo_children():
            child.destroy()
        root.columnconfigure(0, weight=0)
        root.columnconfigure(1, weight=0)
        language = self._custom_language()

        def display_setting(value):
            number = float(value)
            return str(int(number)) if number.is_integer() else f"{number:g}"

        key = self._custom_current_archetype()
        spec = ARCHETYPES[key]
        config = self._custom_profile_for_display()
        archetype_profile = config.archetype_profile
        self._custom_archetype_baseline = default_archetype_profile(key)
        self._custom_archetype_size_adaptive_frequency_var = tk.BooleanVar(
            value=bool(
                archetype_profile["morphology"].get(
                    "size_adaptive_frequency",
                    False,
                )
            )
        )
        self._custom_archetype_vars = {}
        self._custom_archetype_spinboxes = {}
        self._custom_archetype_max_labels = {}
        self._custom_archetype_noise_layer_vars = {}
        self._custom_archetype_noise_layer_setting_widgets = {}
        self._custom_archetype_noise_layer_cards = {}
        self._custom_archetype_noise_layer_action_widgets = {}
        self._custom_archetype_mask_layer_vars = {}
        self._custom_archetype_mask_layer_setting_widgets = {}
        self._custom_archetype_mask_layer_cards = {}
        self._custom_archetype_mask_layer_action_widgets = {}
        self._custom_archetype_noise_group_widgets = {}
        self._custom_archetype_noise_layer_solo = None
        self._custom_archetype_component_canvases = {}
        self._custom_archetype_component_photos = {}
        self._custom_archetype_component_image_items = {}
        self._custom_archetype_relief_source_vars = {}
        self._custom_archetype_relief_mask_vars = {}
        self._custom_archetype_shape_vars = {}
        self._custom_archetype_shape_widgets = {}
        self._custom_archetype_shape_canvas = None
        self._custom_archetype_shape_photo = None
        self._custom_archetype_shape_image_item = None
        self._custom_archetype_relief_setting_widgets = []
        self._custom_archetype_relief_setting_widget_map = {}
        self._custom_archetype_relief_source_var = None
        labels = ARCHETYPE_LABELS.get(language, ARCHETYPE_LABELS["en"])

        ttk.Label(
            root,
            text=_lang_text(language, "Archétype", "Archetype", "Archetyp", "Arquetipo"),
            style="Section.TLabel",
        ).grid(row=0, column=0, sticky="w", pady=(0, 4))
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

        profile_header = ttk.Frame(root)
        profile_header.grid(row=3, column=0, sticky="w", pady=(0, 8))
        ttk.Label(
            profile_header,
            text=custom_section_text("archetype_base_profile", language),
        ).grid(row=0, column=0, sticky="w")
        profile_options = self._custom_archetype_profile_options(language)
        profile_key = self._custom_archetype_profile_selection_key(
            archetype_profile
        )
        profile_preset_var = tk.StringVar(value=profile_options[profile_key])
        self._custom_archetype_profile_var = profile_preset_var
        profile_preset_combo = ttk.Combobox(
            profile_header,
            textvariable=profile_preset_var,
            values=list(profile_options.values()),
            state="readonly",
            width=42,
        )
        self._custom_archetype_profile_combo = profile_preset_combo
        profile_preset_combo.grid(row=0, column=1, sticky="w", padx=(6, 0))
        if not spec.implemented:
            profile_preset_combo.configure(state="disabled")
        profile_preset_combo.bind(
            "<<ComboboxSelected>>",
            lambda _event: self._custom_archetype_profile_changed(),
        )
        ttk.Label(
            profile_header,
            text=custom_section_text("archetype_profile_hint", language),
            style="Hint.TLabel",
            wraplength=360,
            justify="left",
        ).grid(row=0, column=2, sticky="w", padx=(6, 0))
        modified_label = ttk.Label(profile_header, style="Modified.TLabel")
        modified_label.grid(row=0, column=3, sticky="w", padx=(6, 0))
        reset_button = ttk.Button(
            profile_header,
            text=_lang_text(language, "Réinitialiser", "Reset", "Zurücksetzen", "Restablecer"),
            command=self._custom_reset_archetype,
            cursor="hand2",
            padding=(4, 1),
        )
        reset_button.grid(row=0, column=4, sticky="w", padx=(6, 0))
        self._custom_archetype_modified_label = modified_label
        self._custom_archetype_reset_button = reset_button

        def profile_value(path):
            try:
                return get_path(archetype_profile, path)
            except KeyError:
                return ""

        def add_compact_info(parent, row, column, text, *, padx=(4, 0), pady=0):
            """Attach a small contextual explanation without spending a row."""

            icons = getattr(self, "_custom_info_icons", None)
            if icons is None:
                icons = info_icons(self)
                self._custom_info_icons = icons
            marker = ttk.Label(parent, image=icons[1], cursor="question_arrow")
            marker.grid(
                row=row,
                column=column,
                sticky="w",
                padx=padx,
                pady=pady,
            )
            marker.bind(
                "<Enter>",
                lambda event, widget=marker, value=text: self._show_ui_tooltip(
                    widget,
                    value,
                ),
                add="+",
            )
            marker.bind(
                "<Leave>",
                lambda event: self._hide_ui_tooltip(),
                add="+",
            )
            marker.bind(
                "<Enter>",
                lambda event, widget=marker: widget.configure(image=icons[2]),
                add="+",
            )
            marker.bind(
                "<Leave>",
                lambda event, widget=marker: widget.configure(image=icons[1]),
                add="+",
            )
            return marker

        morphology_box = ttk.LabelFrame(root, padding=6)
        morphology_title = ttk.Frame(morphology_box)
        ttk.Label(
            morphology_title,
            text=custom_section_text("archetype_morphology_group", language),
        ).grid(row=0, column=0, sticky="w")
        morphology_reset_button = ttk.Button(
            morphology_title,
            text=_lang_text(language, "Réinitialiser", "Reset", "Zurücksetzen", "Restablecer"),
            command=lambda: self._custom_reset_archetype_section("morphology"),
            cursor="hand2",
            padding=(4, 1),
        )
        morphology_reset_button.grid(row=0, column=1, sticky="w", padx=(8, 0))
        self._custom_archetype_morphology_reset_button = morphology_reset_button
        morphology_box.configure(labelwidget=morphology_title)
        # Relief thresholds are semantically distinct from the source/morphing
        # controls, but they belong to the same compact visual block.  Nesting
        # the threshold frame keeps it beside morphology instead of producing
        # the large empty column that was visible at 1080p.
        morphology_box.grid(
            row=9,
            column=0,
            columnspan=2,
            sticky="nw",
            pady=(0, 8),
        )
        morphology_controls = ttk.Frame(morphology_box)
        morphology_controls.grid(row=0, column=0, sticky="nw")
        relief_box = ttk.LabelFrame(
            morphology_box,
            text=custom_section_text("archetype_relief_group", language),
            padding=6,
        )
        relief_box.grid(
            row=0,
            column=1,
            sticky="nw",
            padx=(14, 0),
        )

        legacy_blocks_shell = ttk.Frame(morphology_box)
        legacy_blocks_shell.grid(
            row=1,
            column=0,
            columnspan=2,
            sticky="nw",
            pady=(8, 0),
        )
        legacy_blocks_toggle = ttk.Button(
            legacy_blocks_shell,
            style="SectionToggle.TButton",
            padding=(4, 0),
            command=lambda: toggle_legacy_blocks(),
            cursor="hand2",
        )
        legacy_blocks_toggle.grid(row=0, column=0, sticky="w")
        legacy_blocks_box = ttk.LabelFrame(legacy_blocks_shell, padding=6)

        def refresh_legacy_blocks():
            expanded = bool(self._custom_archetype_legacy_blocks_expanded)
            if expanded:
                legacy_blocks_box.grid(row=1, column=0, sticky="nw")
            else:
                legacy_blocks_box.grid_remove()
            arrow = "▼" if expanded else "▶"
            legacy_blocks_toggle.configure(
                text=f"{arrow}  {custom_section_text('archetype_legacy_blocks_group', language)}"
            )

        def toggle_legacy_blocks():
            self._custom_archetype_legacy_blocks_expanded = (
                not self._custom_archetype_legacy_blocks_expanded
            )
            refresh_legacy_blocks()

        refresh_legacy_blocks()

        parameter_boxes = {
            "morphology": morphology_controls,
            "legacy_blocks": legacy_blocks_box,
            "relief": relief_box,
        }
        parameter_rows = {group: 0 for group in parameter_boxes}
        editable = bool(spec.implemented)
        self._custom_archetype_editor_editable = editable

        relief_source_options = self._custom_archetype_relief_source_options(language)
        relief_source = str(
            archetype_profile["morphology"].get(
                "relief_source",
                RELIEF_SOURCE_DEFAULT,
            )
        )
        relief_source_var = tk.StringVar(value=relief_source_options[relief_source])
        self._custom_archetype_relief_source_var = relief_source_var
        source_line = ttk.Frame(morphology_controls)
        source_line.grid(row=0, column=0, sticky="w")
        ttk.Label(
            source_line,
            text=custom_section_text("archetype_relief_source", language),
        ).grid(row=0, column=0, sticky="w")
        relief_source_combo = ttk.Combobox(
            source_line,
            textvariable=relief_source_var,
            values=list(relief_source_options.values()),
            state="readonly",
            width=max(map(len, relief_source_options.values())) + 2,
        )
        relief_source_combo.grid(row=0, column=1, sticky="w", padx=(6, 0))
        if not editable:
            relief_source_combo.configure(state="disabled")
        relief_source_combo.bind(
            "<<ComboboxSelected>>",
            lambda _event: self._custom_archetype_relief_source_changed(),
        )
        add_compact_info(
            source_line,
            0,
            2,
            custom_section_text("archetype_relief_source_hint", language),
        )
        parameter_rows["morphology"] = 1

        descriptors = _archetype_ui_parameter_descriptors(archetype_profile)

        def add_archetype_spin(parent, row, descriptor):
            path = descriptor.path
            variable = tk.StringVar(value=str(profile_value(path)))
            self._custom_archetype_vars[descriptor.key] = variable
            line = ttk.Frame(parent)
            line.grid(row=row, column=0, sticky="w", pady=2)
            ttk.Label(
                line,
                text=custom_section_text(descriptor.label_key, language),
            ).grid(row=0, column=0, sticky="w")
            info_icons_map = getattr(self, "_custom_info_icons", None)
            if info_icons_map is None:
                info_icons_map = info_icons(self)
            info = ttk.Label(
                line,
                image=info_icons_map[1],
                cursor="question_arrow",
            )
            info.grid(row=0, column=1, sticky="w", padx=(4, 0))
            info_text = custom_section_text(f"{descriptor.label_key}_hint", language)
            info.bind(
                "<Enter>",
                lambda event, widget=info, text=info_text: self._show_ui_tooltip(widget, text),
                add="+",
            )
            info.bind("<Leave>", lambda event: self._hide_ui_tooltip(), add="+")
            info.bind(
                "<Enter>",
                lambda event, widget=info, icons=info_icons_map: widget.configure(
                    image=icons[2]
                ),
                add="+",
            )
            info.bind(
                "<Leave>",
                lambda event, widget=info, icons=info_icons_map: widget.configure(
                    image=icons[1]
                ),
                add="+",
            )
            widget = ttk.Spinbox(
                line,
                from_=descriptor.minimum,
                to=descriptor.maximum,
                increment=descriptor.increment,
                textvariable=variable,
                width=8,
                state="normal" if editable else "disabled",
                command=lambda p=path, v=variable: self._custom_archetype_changed(p, v.get()),
            )
            if descriptor.value_type == "int" and descriptor.increment > 1:
                _configure_integer_spinbox_steps(
                    widget,
                    variable,
                    descriptor.minimum,
                    descriptor.maximum,
                    lambda p=path, v=variable: self._custom_archetype_changed(
                        p, v.get()
                    ),
                )
            widget.grid(row=0, column=2, sticky="w", padx=(6, 0))
            self._custom_archetype_spinboxes[descriptor.key] = widget
            max_label = ttk.Label(
                line,
                text=(
                    "%"
                    if descriptor.group in ("morphology", "legacy_blocks")
                    else custom_section_text("archetype_height_unit", language)
                ),
                style="Hint.TLabel",
            )
            max_label.grid(row=0, column=3, sticky="w", padx=(5, 8))
            limit_label = ttk.Label(
                line,
                text=custom_section_text("max_value", language, value=str(descriptor.maximum)),
                style="Hint.TLabel",
            )
            limit_label.grid(row=0, column=4, sticky="w")
            self._custom_archetype_max_labels[descriptor.key] = limit_label
            for event_name in ("<Return>", "<FocusOut>"):
                widget.bind(
                    event_name,
                    lambda event, p=path, v=variable: self._custom_archetype_changed(p, v.get()),
                )

        for descriptor in descriptors:
            parent = parameter_boxes.get(descriptor.group, relief_box)
            row = parameter_rows.get(descriptor.group, 0)
            add_archetype_spin(parent, row, descriptor)
            parameter_rows[descriptor.group] = row + 1

        if not editable:
            ttk.Label(
                relief_box,
                text=custom_section_text("archetype_unimplemented_hint", language),
                style="Hint.TLabel",
                wraplength=620,
                justify="left",
            ).grid(
                row=parameter_rows.get("relief", 0),
                column=0,
                sticky="w",
                pady=(6, 0),
            )

        noise_box = ttk.LabelFrame(root, padding=6)
        noise_title = ttk.Frame(noise_box)
        ttk.Label(
            noise_title,
            text=_lang_text(
                language,
                "Éditeur de noisemaps",
                "Noisemap editor",
                "Noisemap-Editor",
                "Editor de noisemaps",
            ),
        ).grid(row=0, column=0, sticky="w")
        noise_hint = "\n".join(
            (
                custom_section_text("archetype_noise_layers_hint", language),
                custom_section_text("archetype_shape_templates_hint", language),
                custom_section_text(
                    "archetype_noise_setting_applicability_hint",
                    language,
                ),
            )
        )
        add_compact_info(noise_title, 0, 1, noise_hint, padx=(4, 0), pady=0)
        noise_reset_button = ttk.Button(
            noise_title,
            text=_lang_text(language, "Réinitialiser", "Reset", "Zurücksetzen", "Restablecer"),
            command=lambda: self._custom_reset_archetype_section("noise_editor"),
            cursor="hand2",
            padding=(4, 1),
        )
        noise_reset_button.grid(row=0, column=2, sticky="w", padx=(8, 0))
        self._custom_archetype_noise_reset_button = noise_reset_button
        noise_box.configure(labelwidget=noise_title)
        noise_box.grid(row=10, column=0, columnspan=2, sticky="nw", pady=(0, 8))
        adaptive_frequency_line = ttk.Frame(noise_box)
        adaptive_frequency_line.grid(row=0, column=0, sticky="w", pady=(0, 4))
        ttk.Checkbutton(
            adaptive_frequency_line,
            text=custom_section_text(
                "archetype_noise_adaptive_frequency",
                language,
            ),
            variable=self._custom_archetype_size_adaptive_frequency_var,
            state="normal" if editable else "disabled",
            command=self._custom_archetype_size_adaptive_frequency_changed,
        ).grid(row=0, column=0, sticky="w")
        add_compact_info(
            adaptive_frequency_line,
            0,
            1,
            custom_section_text(
                "archetype_noise_adaptive_frequency_hint",
                language,
            ),
            padx=(4, 0),
        )
        family_options = self._custom_archetype_noise_family_options(language)
        operation_options = self._custom_archetype_noise_operation_options(language)
        mask_options = self._custom_archetype_noise_mask_options(language)
        mask_source_options = {
            key: family_options[key]
            for key in NOISE_MASK_SOURCE_OPTIONS
            if key in family_options
        }
        setting_labels = {
            "frequency": _lang_text(language, "Fréquence", "Frequency", "Frequenz", "Frecuencia"),
            "octaves": _lang_text(language, "Octaves", "Octaves", "Oktaven", "Octavas"),
            "lacunarity": _lang_text(language, "Lacunarité", "Lacunarity", "Lacunarität", "Lacunaridad"),
            "gain": _lang_text(language, "Gain", "Gain", "Gain", "Ganancia"),
            "rotation_degrees": _lang_text(language, "Rotation °", "Rotation °", "Drehung °", "Rotación °"),
            "stretch_percent": _lang_text(language, "Étirement %", "Stretch %", "Streckung %", "Estiramiento %"),
            "bias_percent": _lang_text(language, "Décalage %", "Bias %", "Versatz %", "Sesgo %"),
            "contrast_percent": _lang_text(language, "Contraste %", "Contrast %", "Kontrast %", "Contraste %"),
            "warp_strength_percent": _lang_text(language, "Warp %", "Warp %", "Warp %", "Warp %"),
            "warp_frequency": _lang_text(language, "Fréq. warp", "Warp freq.", "Warp-Freq.", "Frec. warp"),
            "seed_offset": _lang_text(language, "Décalage seed", "Seed offset", "Seed-Versatz", "Desfase seed"),
            "inversion_percent": _lang_text(language, "Inversion %", "Invert %", "Invertierung %", "Inversión %"),
            "absolute_percent": _lang_text(language, "Absolu %", "Absolute %", "Absolut %", "Absoluto %"),
            "gamma_percent": _lang_text(language, "Gamma %", "Gamma %", "Gamma %", "Gamma %"),
            "terrace_steps": _lang_text(language, "Terrasses", "Terraces", "Terrassen", "Terrazas"),
            "terrace_blend_percent": _lang_text(language, "Mélange terrasses %", "Terrace blend %", "Terrassenmischung %", "Mezcla de terrazas %"),
            "remap_low_percent": _lang_text(language, "Point noir %", "Black point %", "Schwarzpunkt %", "Punto negro %"),
            "remap_high_percent": _lang_text(language, "Point blanc %", "White point %", "Weißpunkt %", "Punto blanco %"),
            "threshold_low_percent": _lang_text(language, "Seuil bas %", "Low threshold %", "Untere Schwelle %", "Umbral bajo %"),
            "threshold_high_percent": _lang_text(language, "Seuil haut %", "High threshold %", "Obere Schwelle %", "Umbral alto %"),
            "threshold_softness_percent": _lang_text(language, "Douceur seuil %", "Threshold softness %", "Schwellenweichheit %", "Suavidad umbral %"),
            "clamp_low_percent": _lang_text(language, "Plancher %", "Clamp floor %", "Untergrenze %", "Suelo %"),
            "clamp_high_percent": _lang_text(language, "Plafond %", "Clamp ceiling %", "Obergrenze %", "Techo %"),
            "curve_bias_percent": _lang_text(language, "Courbe asym. %", "Curve bias %", "Kurvenbias %", "Sesgo de curva %"),
            "offset_x_percent": _lang_text(language, "Décalage X %", "Offset X %", "Versatz X %", "Desfase X %"),
            "offset_y_percent": _lang_text(language, "Décalage Y %", "Offset Y %", "Versatz Y %", "Desfase Y %"),
            "scale_x_percent": _lang_text(language, "Échelle X %", "Scale X %", "Skala X %", "Escala X %"),
            "scale_y_percent": _lang_text(language, "Échelle Y %", "Scale Y %", "Skala Y %", "Escala Y %"),
            "repeat_x": _lang_text(language, "Répétition X", "Repeat X", "Wiederholung X", "Repetición X"),
            "repeat_y": _lang_text(language, "Répétition Y", "Repeat Y", "Wiederholung Y", "Repetición Y"),
            "symmetry_x_percent": _lang_text(language, "Symétrie X %", "Symmetry X %", "Symmetrie X %", "Simetría X %"),
            "symmetry_y_percent": _lang_text(language, "Symétrie Y %", "Symmetry Y %", "Symmetrie Y %", "Simetría Y %"),
            "mask_type": _lang_text(language, "Masque", "Mask", "Maske", "Máscara"),
            "mask_source": _lang_text(language, "Source masque", "Mask source", "Maskenquelle", "Fuente máscara"),
            "mask_strength_percent": _lang_text(language, "Influence %", "Influence %", "Einfluss %", "Influencia %"),
            "mask_invert_percent": _lang_text(language, "Inversion %", "Invert %", "Invertierung %", "Inversión %"),
            "mask_center_percent": _lang_text(language, "Centre %", "Center %", "Mitte %", "Centro %"),
            "mask_width_percent": _lang_text(language, "Largeur %", "Width %", "Breite %", "Anchura %"),
            "mask_angle_degrees": _lang_text(language, "Angle °", "Angle °", "Winkel °", "Ángulo °"),
            "mask_softness_percent": _lang_text(language, "Douceur %", "Softness %", "Weichheit %", "Suavidad %"),
            "mask_seed_offset": _lang_text(language, "Seed masque", "Mask seed", "Masken-Seed", "Seed máscara"),
        }

        noise_setting_groups = (
            (
                "base",
                _lang_text(language, "Fondamentaux", "Core", "Grundlagen", "Base"),
                (
                    "frequency",
                    "octaves",
                    "lacunarity",
                    "gain",
                    "rotation_degrees",
                    "stretch_percent",
                    "bias_percent",
                    "contrast_percent",
                    "warp_strength_percent",
                    "warp_frequency",
                    "seed_offset",
                ),
            ),
            (
                "output",
                _lang_text(
                    language,
                    "Transformations de sortie",
                    "Output transforms",
                    "Ausgabe-Transformationen",
                    "Transformaciones de salida",
                ),
                (
                    "inversion_percent",
                    "absolute_percent",
                    "gamma_percent",
                    "terrace_steps",
                    "terrace_blend_percent",
                ),
            ),
            (
                "remapping",
                _lang_text(language, "Remappage", "Remapping", "Remapping", "Remapeo"),
                (
                    "remap_low_percent",
                    "remap_high_percent",
                    "threshold_low_percent",
                    "threshold_high_percent",
                    "threshold_softness_percent",
                    "clamp_low_percent",
                    "clamp_high_percent",
                    "curve_bias_percent",
                ),
            ),
            (
                "coordinates",
                _lang_text(language, "Coordonnées", "Coordinates", "Koordinaten", "Coordenadas"),
                (
                    "offset_x_percent",
                    "offset_y_percent",
                    "scale_x_percent",
                    "scale_y_percent",
                    "repeat_x",
                    "repeat_y",
                    "symmetry_x_percent",
                    "symmetry_y_percent",
                ),
            ),
        )
        noise_group_labels = {
            group_key: group_label
            for group_key, group_label, _keys in noise_setting_groups
        }

        def noise_group_is_expanded(source_key, group_key):
            states = self._custom_archetype_noise_group_expanded.setdefault(
                source_key,
                {},
            )
            return bool(states.get(group_key, group_key == "base"))

        def refresh_noise_group(source_key, group_key):
            entry = self._custom_archetype_noise_group_widgets.get(source_key, {}).get(
                group_key
            )
            if entry is None:
                return
            _group_box, content, toggle_button = entry
            expanded = noise_group_is_expanded(source_key, group_key)
            try:
                if expanded:
                    content.grid(row=1, column=0, sticky="w")
                else:
                    content.grid_remove()
                if toggle_button is not None:
                    arrow = "▼" if expanded else "▶"
                    toggle_button.configure(
                        text=f"{arrow}  {noise_group_labels[group_key]}"
                    )
            except tk.TclError:
                pass

        def toggle_noise_group(source_key, group_key):
            states = self._custom_archetype_noise_group_expanded.setdefault(
                source_key,
                {},
            )
            states[group_key] = not noise_group_is_expanded(source_key, group_key)
            refresh_noise_group(source_key, group_key)

        def add_source_settings(parent, start_row, variables, callback, source_key):
            widgets = {}
            group_widgets = self._custom_archetype_noise_group_widgets.setdefault(
                source_key,
                {},
            )
            for group_index, (group_key, group_label, keys) in enumerate(
                noise_setting_groups
            ):
                group_shell = ttk.Frame(parent)
                group_shell.grid(
                    row=start_row + group_index,
                    column=0,
                    sticky="w",
                    pady=(0, 1),
                )
                group_title = ttk.Frame(group_shell)
                group_title.grid(row=0, column=0, sticky="w")
                group_button = ttk.Button(
                    group_title,
                    style="SectionToggle.TButton",
                    state="normal" if editable else "disabled",
                    padding=(4, 0),
                    command=lambda source=source_key, group=group_key: toggle_noise_group(
                        source,
                        group,
                    ),
                    cursor="hand2",
                )
                group_button.grid(row=0, column=0, sticky="w")
                content = ttk.LabelFrame(group_shell, padding=(4, 2))
                content.grid(row=1, column=0, sticky="w")
                group_widgets[group_key] = (group_shell, content, group_button)
                for position, setting_key in enumerate(keys):
                    row = position // 4
                    column = (position % 4) * 2
                    setting_default = None
                    setting_increment = 1
                    ttk.Label(
                        content,
                        text=setting_labels[setting_key],
                        style="Hint.TLabel",
                    ).grid(
                        row=row,
                        column=column,
                        sticky="w",
                        padx=(0 if column == 0 else 10, 4),
                        pady=2,
                    )
                    if setting_key == "mask_type":
                        widget = ttk.Combobox(
                            content,
                            textvariable=variables[setting_key],
                            values=list(mask_options.values()),
                            state="readonly",
                            width=max(map(len, mask_options.values())) + 1,
                        )
                    elif setting_key == "mask_source":
                        widget = ttk.Combobox(
                            content,
                            textvariable=variables[setting_key],
                            values=list(mask_source_options.values()),
                            state="readonly",
                            width=max(map(len, mask_source_options.values())) + 1,
                        )
                    elif setting_key.startswith("mask_"):
                        mask_key = setting_key[5:]
                        low, high = NOISE_MASK_BOUNDS[mask_key]
                        widget = ttk.Spinbox(
                            content,
                            from_=low,
                            to=high,
                            increment=NOISE_MASK_INCREMENTS[mask_key],
                            textvariable=variables[setting_key],
                            width=7,
                            state="normal" if editable else "disabled",
                            command=callback,
                        )
                        setting_default = NOISE_MASK_DEFAULTS[mask_key]
                        setting_increment = NOISE_MASK_INCREMENTS[mask_key]
                    else:
                        low, high = NOISE_SOURCE_SETTING_BOUNDS[setting_key]
                        widget = ttk.Spinbox(
                            content,
                            from_=low,
                            to=high,
                            increment=NOISE_SOURCE_SETTING_INCREMENTS[setting_key],
                            textvariable=variables[setting_key],
                            width=7,
                            state="normal" if editable else "disabled",
                            command=callback,
                        )
                        setting_default = NOISE_SOURCE_SETTING_DEFAULTS[setting_key]
                        setting_increment = NOISE_SOURCE_SETTING_INCREMENTS[setting_key]
                    if (
                        isinstance(widget, ttk.Spinbox)
                        and isinstance(setting_default, int)
                        and not isinstance(setting_default, bool)
                        and setting_increment > 1
                    ):
                        _configure_integer_spinbox_steps(
                            widget,
                            variables[setting_key],
                            low,
                            high,
                            callback,
                        )
                    if not editable and isinstance(widget, ttk.Combobox):
                        widget.configure(state="disabled")
                    widget.grid(row=row, column=column + 1, sticky="w", pady=2)
                    widgets[setting_key] = widget
                    if isinstance(widget, ttk.Combobox):
                        widget.bind(
                            "<<ComboboxSelected>>",
                            lambda _event, action=callback: action(),
                        )
                    for event_name in ("<Return>", "<FocusOut>"):
                        widget.bind(
                            event_name,
                            lambda _event, action=callback: action(),
                        )
                refresh_noise_group(source_key, group_key)
            return widgets

        base_card = ttk.LabelFrame(
            noise_box,
            text=_lang_text(language, "Source principale", "Primary source", "Hauptquelle", "Fuente principal"),
            padding=6,
        )
        count_line = ttk.Frame(noise_box)
        count_line.grid(row=1, column=0, sticky="w", pady=(0, 6))
        ttk.Label(
            count_line,
            text=custom_section_text("archetype_noise_layer_count", language),
        ).grid(row=0, column=0, sticky="w", padx=(0, 6))
        layer_count = int(archetype_profile["morphology"]["noise_layer_count"])
        self._custom_archetype_noise_layer_count_var.set(str(layer_count))
        layer_count_widget = ttk.Spinbox(
            count_line,
            from_=NOISE_LAYER_COUNT_BOUNDS[0],
            to=NOISE_LAYER_COUNT_BOUNDS[1],
            increment=1,
            textvariable=self._custom_archetype_noise_layer_count_var,
            width=5,
            state="normal" if editable else "disabled",
            command=self._custom_archetype_noise_layer_count_changed,
        )
        layer_count_widget.grid(row=0, column=1, sticky="w")
        for event_name in ("<Return>", "<FocusOut>"):
            layer_count_widget.bind(
                event_name,
                lambda _event: self._custom_archetype_noise_layer_count_changed(),
            )

        base_card.grid(row=2, column=0, sticky="nw", pady=(0, 6))
        base_settings_frame = ttk.Frame(base_card)
        base_settings_frame.grid(row=0, column=0, sticky="nw")
        base_settings = archetype_profile["morphology"]["relief_source_settings"]
        self._custom_archetype_relief_source_vars = {
            setting_key: tk.StringVar(value=display_setting(base_settings[setting_key]))
            for setting_key in NOISE_SOURCE_SETTING_DEFAULTS
        }
        base_mask = archetype_profile["morphology"].get(
            "relief_source_mask", NOISE_MASK_DEFAULTS
        )
        self._custom_archetype_relief_mask_vars = {}
        for key, default in NOISE_MASK_DEFAULTS.items():
            value = base_mask.get(key, default)
            if key == "type":
                value = mask_options[str(value)]
            elif key == "source":
                value = mask_source_options[str(value)]
            self._custom_archetype_relief_mask_vars[key] = tk.StringVar(
                value=display_setting(value) if isinstance(value, (int, float)) else str(value)
            )
        base_variables = {
            **self._custom_archetype_relief_source_vars,
            **{
                f"mask_{key}": variable
                for key, variable in self._custom_archetype_relief_mask_vars.items()
            },
        }
        self._custom_archetype_relief_setting_widgets = add_source_settings(
            base_settings_frame,
            0,
            base_variables,
            self._custom_archetype_relief_source_changed,
            "primary",
        )
        self._custom_archetype_relief_setting_widget_map = dict(
            self._custom_archetype_relief_setting_widgets
        )
        self._custom_archetype_relief_setting_widgets = list(
            self._custom_archetype_relief_setting_widget_map.values()
        )
        source_canvas = tk.Canvas(
            base_card,
            width=_ARCHETYPE_COMPONENT_PREVIEW_SIZE,
            height=_ARCHETYPE_COMPONENT_PREVIEW_SIZE,
            background="#202328",
            highlightthickness=1,
            highlightbackground="#5b6068",
            borderwidth=0,
        )
        source_canvas.grid(
            row=0,
            column=1,
            rowspan=1,
            sticky="ne",
            padx=(12, 0),
        )
        self._custom_archetype_component_canvases["source"] = source_canvas

        layer_values = archetype_profile["morphology"]["noise_layers"]
        for index, layer in enumerate(layer_values):
            card = ttk.LabelFrame(
                noise_box,
                text=_lang_text(language, f"Fusion {index + 1}", f"Fusion {index + 1}", f"Fusion {index + 1}", f"Fusión {index + 1}"),
                padding=6,
            )
            card.grid(row=index + 3, column=0, sticky="nw", pady=(0, 6))
            self._custom_archetype_noise_layer_cards[index] = card
            if index >= layer_count:
                card.grid_remove()
            enabled_var = tk.BooleanVar(value=bool(layer["enabled"]))
            family_var = tk.StringVar(value=family_options[str(layer["family"])])
            operation_var = tk.StringVar(value=operation_options[str(layer["operation"])])
            strength_var = tk.StringVar(value=str(layer["strength_percent"]))
            layer_mask = layer.get("mask_settings", NOISE_MASK_DEFAULTS)
            variables = {
                "enabled": enabled_var,
                "family": family_var,
                "operation": operation_var,
                "strength": strength_var,
                **{
                    setting_key: tk.StringVar(value=display_setting(layer["settings"][setting_key]))
                    for setting_key in NOISE_SOURCE_SETTING_DEFAULTS
                },
            }
            variables.update(
                {
                    "mask_type": tk.StringVar(
                        value=mask_options[str(layer_mask.get("type", "none"))]
                    ),
                    "mask_source": tk.StringVar(
                        value=mask_source_options[str(layer_mask.get("source", "perlin"))]
                    ),
                    **{
                        f"mask_{key}": tk.StringVar(
                            value=display_setting(layer_mask.get(key, default))
                        )
                        for key, default in NOISE_MASK_DEFAULTS.items()
                        if key not in {"type", "source"}
                    },
                }
            )
            self._custom_archetype_noise_layer_vars[index] = variables
            callback = lambda layer_index=index: self._custom_archetype_noise_layer_changed(layer_index)
            fusion_header = ttk.Frame(card)
            fusion_header.grid(row=0, column=0, sticky="w")
            ttk.Checkbutton(
                fusion_header,
                text=_lang_text(language, "Activer", "Enable", "Aktivieren", "Activar"),
                variable=enabled_var,
                state="normal" if editable else "disabled",
                command=callback,
            ).grid(row=0, column=0, sticky="w", padx=(0, 8))
            family_combo = ttk.Combobox(
                fusion_header,
                textvariable=family_var,
                values=list(family_options.values()),
                state="readonly",
                width=max(map(len, family_options.values())) + 1,
            )
            family_combo.grid(row=0, column=1, sticky="w", padx=(0, 8))
            if not editable:
                family_combo.configure(state="disabled")
            family_combo.bind("<<ComboboxSelected>>", lambda _event, action=callback: action())
            operation_combo = ttk.Combobox(
                fusion_header,
                textvariable=operation_var,
                values=list(operation_options.values()),
                state="readonly",
                width=max(map(len, operation_options.values())) + 1,
            )
            operation_combo.grid(row=0, column=2, sticky="w", padx=(0, 8))
            if not editable:
                operation_combo.configure(state="disabled")
            operation_combo.bind("<<ComboboxSelected>>", lambda _event, action=callback: action())
            ttk.Label(fusion_header, text=_lang_text(language, "Force %", "Strength %", "Stärke %", "Fuerza %")).grid(
                row=0, column=3, sticky="w", padx=(0, 4)
            )
            strength_widget = ttk.Spinbox(
                fusion_header,
                from_=NOISE_LAYER_STRENGTH_BOUNDS[0],
                to=NOISE_LAYER_STRENGTH_BOUNDS[1],
                increment=5,
                textvariable=strength_var,
                width=7,
                state="normal" if editable else "disabled",
                command=callback,
            )
            _configure_integer_spinbox_steps(
                strength_widget,
                strength_var,
                NOISE_LAYER_STRENGTH_BOUNDS[0],
                NOISE_LAYER_STRENGTH_BOUNDS[1],
                callback,
            )
            strength_widget.grid(row=0, column=4, sticky="w")
            for event_name in ("<Return>", "<FocusOut>"):
                strength_widget.bind(event_name, lambda _event, action=callback: action())
            fusion_settings = ttk.Frame(card)
            fusion_settings.grid(row=1, column=0, sticky="w")
            self._custom_archetype_noise_layer_setting_widgets[index] = dict(
                add_source_settings(
                    fusion_settings,
                    0,
                    variables,
                    callback,
                    f"layer:{index}",
                )
            )
            action_row = 2
            action_line = ttk.Frame(card)
            action_line.grid(
                row=action_row,
                column=0,
                sticky="w",
                pady=(4, 0),
            )
            action_widgets = {
                "up": ttk.Button(
                    action_line,
                    text="↑",
                    width=3,
                    command=lambda layer_index=index: self._custom_archetype_noise_layer_reorder(
                        layer_index,
                        -1,
                    ),
                ),
                "down": ttk.Button(
                    action_line,
                    text="↓",
                    width=3,
                    command=lambda layer_index=index: self._custom_archetype_noise_layer_reorder(
                        layer_index,
                        1,
                    ),
                ),
                "duplicate": ttk.Button(
                    action_line,
                    text=_lang_text(
                        language,
                        "Dupliquer",
                        "Duplicate",
                        "Duplizieren",
                        "Duplicar",
                    ),
                    command=lambda layer_index=index: self._custom_archetype_noise_layer_duplicate(
                        layer_index,
                    ),
                ),
                "delete": ttk.Button(
                    action_line,
                    text=_lang_text(
                        language,
                        "Supprimer",
                        "Delete",
                        "Löschen",
                        "Eliminar",
                    ),
                    command=lambda layer_index=index: self._custom_archetype_noise_layer_remove(
                        layer_index,
                    ),
                ),
                "solo": ttk.Button(
                    action_line,
                    text=_lang_text(
                        language,
                        "Solo",
                        "Solo",
                        "Solo",
                        "Solo",
                    ),
                    command=lambda layer_index=index: self._custom_archetype_noise_layer_solo_changed(
                        layer_index,
                    ),
                ),
            }
            for position, widget in enumerate(action_widgets.values()):
                widget.grid(row=0, column=position, sticky="w", padx=(0, 4))
            solo_button = action_widgets["solo"]
            solo_hint = _lang_text(
                language,
                "Solo isole cette fusion active tout en conservant la source principale. Il ne force jamais Activer.",
                "Solo isolates this active fusion while keeping the primary source. It never forces Enable on.",
                "Solo isoliert diese aktive Fusion und behält die Hauptquelle. Aktivieren wird nie erzwungen.",
                "Solo aísla esta fusión activa y conserva la fuente principal. Nunca fuerza Activar.",
            )
            solo_button.bind(
                "<Enter>",
                lambda event, widget=solo_button, text=solo_hint: self._show_ui_tooltip(
                    widget,
                    text,
                ),
                add="+",
            )
            solo_button.bind(
                "<Leave>",
                lambda event: self._hide_ui_tooltip(),
                add="+",
            )
            self._custom_archetype_noise_layer_action_widgets[index] = action_widgets
            component_canvas = tk.Canvas(
                card,
                width=_ARCHETYPE_COMPONENT_PREVIEW_SIZE,
                height=_ARCHETYPE_COMPONENT_PREVIEW_SIZE,
                background="#202328",
                highlightthickness=1,
                highlightbackground="#5b6068",
                borderwidth=0,
            )
            component_canvas.grid(
                row=0,
                column=1,
                rowspan=action_row + 1,
                sticky="ne",
                padx=(12, 0),
            )
            self._custom_archetype_component_canvases[
                f"layer:{index}"
            ] = component_canvas
        self._custom_refresh_archetype_noise_setting_states(relief_source)
        self._custom_refresh_archetype_noise_layer_action_states()

        mask_box = ttk.LabelFrame(root, padding=6)
        mask_title = ttk.Frame(mask_box)
        ttk.Label(
            mask_title,
            text=custom_section_text("archetype_mask_group", language),
        ).grid(row=0, column=0, sticky="w")
        add_compact_info(
            mask_title,
            0,
            1,
            "\n".join(
                (
                    custom_section_text("archetype_mask_subtitle", language),
                    custom_section_text("archetype_mask_hint", language),
                )
            ),
            padx=(4, 0),
        )
        mask_reset_button = ttk.Button(
            mask_title,
            text=_lang_text(language, "Réinitialiser", "Reset", "Zurücksetzen", "Restablecer"),
            command=lambda: self._custom_reset_archetype_section("mask_editor"),
            cursor="hand2",
            padding=(4, 1),
        )
        mask_reset_button.grid(row=0, column=2, sticky="w", padx=(8, 0))
        self._custom_archetype_mask_reset_button = mask_reset_button
        mask_box.configure(labelwidget=mask_title)
        mask_box.grid(row=11, column=0, columnspan=2, sticky="nw", pady=(0, 8))

        mask_count_line = ttk.Frame(mask_box)
        mask_count_line.grid(row=0, column=0, sticky="w", pady=(0, 6))
        ttk.Label(
            mask_count_line,
            text=custom_section_text("archetype_mask_layer_count", language),
        ).grid(row=0, column=0, sticky="w", padx=(0, 6))
        mask_count = int(archetype_profile["morphology"].get("mask_layer_count", 0))
        self._custom_archetype_mask_layer_count_var.set(str(mask_count))
        mask_count_widget = ttk.Spinbox(
            mask_count_line,
            from_=MASK_LAYER_COUNT_BOUNDS[0],
            to=MASK_LAYER_COUNT_BOUNDS[1],
            increment=1,
            textvariable=self._custom_archetype_mask_layer_count_var,
            width=5,
            state="normal" if editable else "disabled",
            command=self._custom_archetype_mask_layer_count_changed,
        )
        mask_count_widget.grid(row=0, column=1, sticky="w")
        for event_name in ("<Return>", "<FocusOut>"):
            mask_count_widget.bind(
                event_name,
                lambda _event: self._custom_archetype_mask_layer_count_changed(),
            )

        mask_type_options = self._custom_archetype_mask_type_options(language)
        mask_operation_options = self._custom_archetype_mask_operation_options(language)
        mask_common_labels = {
            "width_percent": custom_section_text("archetype_shape_width", language),
            "height_percent": custom_section_text("archetype_shape_height", language),
            "offset_x_percent": custom_section_text("archetype_shape_offset_x", language),
            "offset_y_percent": custom_section_text("archetype_shape_offset_y", language),
            "rotation_degrees": custom_section_text("archetype_shape_rotation", language),
            "softness_percent": custom_section_text("archetype_shape_softness", language),
        }
        mask_shape_layout = (
            ("width_percent", 0, 0),
            ("height_percent", 0, 2),
            ("offset_x_percent", 1, 0),
            ("offset_y_percent", 1, 2),
            ("rotation_degrees", 2, 0),
            ("softness_percent", 2, 2),
        )
        mask_layer_values = archetype_profile["morphology"].get("mask_layers", ())
        for index, layer in enumerate(mask_layer_values):
            card = ttk.LabelFrame(
                mask_box,
                text=custom_section_text("archetype_mask_layer", language, index=index + 1),
                padding=6,
            )
            self._custom_archetype_mask_layer_cards[index] = card
            if index >= mask_count:
                card.grid_remove()
            enabled_var = tk.BooleanVar(value=bool(layer.get("enabled", False)))
            mask_type = str(layer.get("type", "star"))
            operation = str(layer.get("operation", "blend"))
            type_var = tk.StringVar(value=mask_type_options.get(mask_type, mask_type))
            operation_var = tk.StringVar(
                value=mask_operation_options.get(operation, operation)
            )
            strength_var = tk.StringVar(value=str(layer.get("strength_percent", 45)))
            settings = layer.get("settings", {})
            variables = {
                "enabled": enabled_var,
                "type": type_var,
                "operation": operation_var,
                "strength": strength_var,
                **{
                    setting_key: tk.StringVar(
                        value=display_setting(
                            settings.get(setting_key, default)
                        )
                    )
                    for setting_key, default in MASK_LAYER_COMMON_DEFAULTS.items()
                },
            }
            self._custom_archetype_mask_layer_vars[index] = variables
            callback = lambda layer_index=index: self._custom_archetype_mask_layer_changed(
                layer_index
            )
            header = ttk.Frame(card)
            header.grid(row=0, column=0, sticky="w")
            ttk.Checkbutton(
                header,
                text=_lang_text(language, "Activer", "Enable", "Aktivieren", "Activar"),
                variable=enabled_var,
                state="normal" if editable else "disabled",
                command=callback,
            ).grid(row=0, column=0, sticky="w", padx=(0, 8))
            type_combo = ttk.Combobox(
                header,
                textvariable=type_var,
                values=list(mask_type_options.values()),
                state="readonly" if editable else "disabled",
                width=max(map(len, mask_type_options.values())) + 1,
            )
            type_combo.grid(row=0, column=1, sticky="w", padx=(0, 8))
            type_combo.bind("<<ComboboxSelected>>", lambda _event, action=callback: action())
            ttk.Label(
                header,
                text=custom_section_text("archetype_mask_operation", language),
            ).grid(row=0, column=2, sticky="w", padx=(0, 4))
            operation_combo = ttk.Combobox(
                header,
                textvariable=operation_var,
                values=list(mask_operation_options.values()),
                state="readonly" if editable else "disabled",
                width=max(map(len, mask_operation_options.values())) + 1,
            )
            operation_combo.grid(row=0, column=3, sticky="w", padx=(0, 8))
            operation_combo.bind(
                "<<ComboboxSelected>>",
                lambda _event, action=callback: action(),
            )
            ttk.Label(
                header,
                text=custom_section_text("archetype_mask_strength", language),
            ).grid(row=0, column=4, sticky="w", padx=(0, 4))
            strength_widget = ttk.Spinbox(
                header,
                from_=MASK_LAYER_STRENGTH_BOUNDS[0],
                to=MASK_LAYER_STRENGTH_BOUNDS[1],
                increment=5,
                textvariable=strength_var,
                width=7,
                state="normal" if editable else "disabled",
                command=callback,
            )
            _configure_integer_spinbox_steps(
                strength_widget,
                strength_var,
                MASK_LAYER_STRENGTH_BOUNDS[0],
                MASK_LAYER_STRENGTH_BOUNDS[1],
                callback,
            )
            strength_widget.grid(row=0, column=5, sticky="w")
            for event_name in ("<Return>", "<FocusOut>"):
                strength_widget.bind(
                    event_name,
                    lambda _event, action=callback: action(),
                )

            setting_frame = ttk.Frame(card)
            setting_frame.grid(row=1, column=0, sticky="w", pady=(4, 0))
            setting_widgets = {}
            for setting_key, row, column in mask_shape_layout:
                ttk.Label(
                    setting_frame,
                    text=mask_common_labels[setting_key],
                    style="Hint.TLabel",
                ).grid(
                    row=row,
                    column=column,
                    sticky="w",
                    padx=(0 if column == 0 else 12, 4),
                    pady=2,
                )
                low, high = MASK_LAYER_COMMON_BOUNDS[setting_key]
                widget = ttk.Spinbox(
                    setting_frame,
                    from_=low,
                    to=high,
                    increment=MASK_LAYER_COMMON_INCREMENTS[setting_key],
                    textvariable=variables[setting_key],
                    width=7,
                    state="normal" if editable else "disabled",
                    command=callback,
                )
                if MASK_LAYER_COMMON_INCREMENTS[setting_key] > 1:
                    _configure_integer_spinbox_steps(
                        widget,
                        variables[setting_key],
                        low,
                        high,
                        callback,
                    )
                widget.grid(row=row, column=column + 1, sticky="w", pady=2)
                setting_widgets[setting_key] = widget
                for event_name in ("<Return>", "<FocusOut>"):
                    widget.bind(
                        event_name,
                        lambda _event, action=callback: action(),
                    )
            self._custom_archetype_mask_layer_setting_widgets[index] = setting_widgets

            action_line = ttk.Frame(card)
            action_line.grid(row=2, column=0, sticky="w", pady=(4, 0))
            action_widgets = {
                "up": ttk.Button(
                    action_line,
                    text="↑",
                    width=3,
                    command=lambda layer_index=index: self._custom_archetype_mask_layer_reorder(
                        layer_index, -1
                    ),
                ),
                "down": ttk.Button(
                    action_line,
                    text="↓",
                    width=3,
                    command=lambda layer_index=index: self._custom_archetype_mask_layer_reorder(
                        layer_index, 1
                    ),
                ),
                "duplicate": ttk.Button(
                    action_line,
                    text=_lang_text(language, "Dupliquer", "Duplicate", "Duplizieren", "Duplicar"),
                    command=lambda layer_index=index: self._custom_archetype_mask_layer_duplicate(
                        layer_index
                    ),
                ),
                "delete": ttk.Button(
                    action_line,
                    text=_lang_text(language, "Supprimer", "Delete", "Löschen", "Eliminar"),
                    command=lambda layer_index=index: self._custom_archetype_mask_layer_remove(
                        layer_index
                    ),
                ),
                "edit": ttk.Button(
                    action_line,
                    text=_lang_text(language, "Éditer", "Edit", "Bearbeiten", "Editar"),
                    command=lambda layer_index=index: self._custom_archetype_mask_layer_edit(
                        layer_index
                    ),
                ),
            }
            for position, widget in enumerate(action_widgets.values()):
                widget.grid(row=0, column=position, sticky="w", padx=(0, 4))
            self._custom_archetype_mask_layer_action_widgets[index] = action_widgets
            preview_canvas = tk.Canvas(
                card,
                width=_ARCHETYPE_COMPONENT_PREVIEW_SIZE,
                height=_ARCHETYPE_COMPONENT_PREVIEW_SIZE,
                background="#202328",
                highlightthickness=1,
                highlightbackground="#5b6068",
                borderwidth=0,
            )
            preview_canvas.grid(
                row=0,
                column=1,
                rowspan=3,
                sticky="ne",
                padx=(12, 0),
            )
            self._custom_archetype_component_canvases[f"mask:{index}"] = preview_canvas
        self._custom_refresh_archetype_mask_layer_states()
        self._custom_refresh_archetype_mask_layer_action_states()

        preview_controls = ttk.Frame(root)
        preview_controls.grid(row=4, column=0, sticky="w", pady=(0, 6))
        projection_options = self._custom_archetype_preview_projection_options(language)
        size_options = self._custom_archetype_preview_size_options(language)
        self._custom_archetype_preview_projection_var.set(
            projection_options[self._custom_archetype_preview_projection_key]
        )
        self._custom_archetype_preview_size_var.set(
            size_options[self._custom_archetype_preview_size_key]
        )
        ttk.Label(
            preview_controls,
            text=custom_section_text("archetype_preview_projection", language),
        ).grid(row=0, column=0, sticky="w", padx=(0, 5))
        projection_combo = ttk.Combobox(
            preview_controls,
            textvariable=self._custom_archetype_preview_projection_var,
            values=list(projection_options.values()),
            state="readonly",
            width=max(map(len, projection_options.values())) + 2,
        )
        projection_combo.grid(row=0, column=1, sticky="w", padx=(0, 14))
        ttk.Label(
            preview_controls,
            text=custom_section_text("archetype_preview_size", language),
        ).grid(row=0, column=2, sticky="w", padx=(0, 5))
        size_combo = ttk.Combobox(
            preview_controls,
            textvariable=self._custom_archetype_preview_size_var,
            values=list(size_options.values()),
            state="readonly",
            width=max(map(len, size_options.values())) + 2,
        )
        size_combo.grid(row=0, column=3, sticky="w")
        relaxation_check = ttk.Checkbutton(
            preview_controls,
            text=custom_section_text("archetype_preview_macro_relaxation", language),
            variable=self._custom_archetype_preview_relaxation_var,
            state="normal" if editable else "disabled",
            command=self._custom_archetype_preview_relaxation_changed,
        )
        relaxation_check.grid(row=1, column=0, columnspan=2, sticky="w", pady=(5, 0))
        ttk.Label(
            preview_controls,
            text=custom_section_text("archetype_preview_macro_relaxation_hint", language),
            style="Hint.TLabel",
            wraplength=560,
            justify="left",
        ).grid(row=1, column=2, columnspan=2, sticky="w", padx=(14, 0), pady=(5, 0))

        preview_grid = ttk.Frame(root)
        preview_grid.grid(row=5, column=0, sticky="w", pady=(0, 8))
        preview_grid.columnconfigure(0, weight=0)
        preview_grid.columnconfigure(1, weight=0)
        preview_grid.columnconfigure(2, weight=0)
        self._custom_archetype_preview_canvases = {}
        self._custom_archetype_preview_image_items = {}
        canvas_width, canvas_height = self._custom_archetype_preview_dimensions()
        self._custom_archetype_preview_last_dimensions = (canvas_width, canvas_height)
        preview_specs = (
            (
                "noise",
                custom_section_text("archetype_preview_noise", language),
            ),
            (
                "macro",
                custom_section_text("archetype_preview_macro", language),
            ),
            (
                "contribution",
                custom_section_text("archetype_noise_contribution_short", language),
            ),
        )
        for column, (preview_key, title) in enumerate(preview_specs):
            panel = ttk.LabelFrame(preview_grid, text=title, padding=6)
            panel.grid(
                row=0,
                column=column,
                sticky="nw",
                padx=(0, 8 if column < 2 else 0),
            )
            canvas = tk.Canvas(
                panel,
                width=canvas_width,
                height=canvas_height,
                background="#202328",
                highlightthickness=0,
                borderwidth=0,
            )
            canvas.grid(row=0, column=0, sticky="nw")
            self._custom_archetype_preview_canvases[preview_key] = canvas
            if preview_key == "macro":
                legend = ttk.Frame(panel)
                legend.grid(row=1, column=0, sticky="w", pady=(6, 0))
                for legend_column, legend_key in enumerate(
                    ("water", "beach", "grass", "mountain", "snow")
                ):
                    colour = "#%02x%02x%02x" % MACRO_PALETTE[legend_column]
                    swatch = tk.Canvas(
                        legend,
                        width=12,
                        height=12,
                        background=colour,
                        highlightthickness=0,
                        borderwidth=0,
                    )
                    legend_row = legend_column // 3
                    legend_pair = legend_column % 3
                    swatch.grid(
                        row=legend_row,
                        column=legend_pair * 2,
                        sticky="w",
                        padx=(0, 2),
                    )
                    ttk.Label(
                        legend,
                        text=custom_section_text(
                            f"archetype_preview_{legend_key}",
                            language,
                        ),
                    ).grid(
                        row=legend_row,
                        column=legend_pair * 2 + 1,
                        sticky="w",
                        padx=(0, 6 if legend_column < 4 else 0),
                    )

        progress_row = ttk.Frame(root)
        progress_row.grid(row=6, column=0, sticky="w", pady=(0, 3))
        self._custom_archetype_preview_progress_bar = ttk.Progressbar(
            progress_row,
            orient="horizontal",
            mode="determinate",
            maximum=100,
            value=0,
            length=220,
        )
        self._custom_archetype_preview_progress_bar.grid(row=0, column=0, sticky="w")
        ttk.Label(
            root,
            textvariable=self._custom_archetype_preview_status_var,
            style="Hint.TLabel",
        ).grid(row=7, column=0, sticky="w", pady=(0, 8))
        ttk.Label(
            root,
            textvariable=self._custom_archetype_preview_stats_var,
            style="Hint.TLabel",
            wraplength=760,
            justify="left",
        ).grid(row=8, column=0, sticky="w", pady=(0, 8))

        contract = (
            _lang_text(
                language,
                "L’archétype construit une noisemap brute autonome. Le mode Générateur sélectionné reste inchangé et transforme ensuite ce champ en carte jouable.",
                "The archetype builds an autonomous raw noisemap. The selected Generator mode remains unchanged and then turns that field into a playable map.",
                "Der Archetyp erzeugt eine autonome rohe Noisemap. Der gewählte Generatormodus bleibt unverändert und wandelt dieses Feld anschließend in eine spielbare Karte um.",
                "El arquetipo construye un noisemap bruto autónomo. El modo Generador seleccionado no cambia y después transforma este campo en un mapa jugable.",
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
        ttk.Label(
            root,
            text=contract,
            style="Hint.TLabel",
            wraplength=680,
            justify="left",
        ).grid(row=12, column=0, sticky="w", pady=3)
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
        ).grid(row=13, column=0, sticky="w", pady=(12, 0))
        for variable in (self.size, self.seed, self.mirror):
            trace_id = variable.trace_add(
                "write",
                self._custom_schedule_archetype_preview_refresh,
            )
            self._custom_archetype_preview_trace_ids.append((variable, trace_id))
        for variable, callback in (
            (
                self._custom_archetype_preview_projection_var,
                self._custom_archetype_preview_projection_changed,
            ),
            (
                self._custom_archetype_preview_size_var,
                self._custom_archetype_preview_size_changed,
            ),
        ):
            trace_id = variable.trace_add("write", callback)
            self._custom_archetype_preview_trace_ids.append((variable, trace_id))
        self._custom_refresh_archetype_header()
        self._custom_refresh_archetype_section_reset_buttons()
        self._custom_schedule_archetype_preview_refresh()


__all__ = ("CustomGeneratorController",)
