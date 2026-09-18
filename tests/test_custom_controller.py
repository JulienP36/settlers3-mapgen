import ast
from pathlib import Path

from s3mapgen.application.custom.controller import (
    CustomGeneratorController,
    _read_preview_number,
)
from s3mapgen.application.custom.i18n import _CUSTOM_SECTION_TEXT
from s3mapgen.application.ui.i18n.shell import MODE_LABELS
from s3mapgen.generation.custom import build_custom_config, default_sections


CUSTOM_CONTROLLER_SOURCE = Path(
    "s3mapgen/application/custom/controller.py"
).read_text(encoding="utf-8")
SETTINGS_CONTROLLER_SOURCE = Path(
    "s3mapgen/application/settings/controller.py"
).read_text(encoding="utf-8")


class _FakeVar:
    def __init__(self, value):
        self.value = value
        self.set_calls = 0

    def get(self):
        return self.value

    def set(self, value):
        self.value = value
        self.set_calls += 1


class _ProbeController(CustomGeneratorController):
    def __init__(self):
        self.mode = _FakeVar("Custom")
        self.prefs = {"language": "fr"}
        self._custom_status_var = _FakeVar("")
        self._custom_provenance_var = _FakeVar("")
        self.selection_calls = 0
        self.provenance_refreshes = 0
        self.render_calls = 0

    def _mode_key(self):
        return "custom" if self.mode.get() == "Custom" else "upgraded"

    def _custom_render_custom_mode(self, config):
        self.provenance_refreshes += 1

    def _render_custom_parameter_tabs(self):
        self.render_calls += 1

    def _selection_changed(self):
        self.selection_calls += 1


def test_custom_parameter_edits_do_not_rebuild_the_selection_ui():
    controller = _ProbeController()
    base = build_custom_config("upgraded")

    controller._custom_activate(base.with_value("minerals.occupancy_percent", 42))

    assert controller.selection_calls == 0
    assert controller.provenance_refreshes == 1
    assert controller.mode.set_calls == 0


def test_first_custom_parameter_edit_enters_custom_mode_without_rebuilding():
    controller = _ProbeController()
    controller.mode.set("Upgraded")
    base = build_custom_config("upgraded")

    controller._custom_activate(base.with_value("minerals.occupancy_percent", 42))

    assert controller.selection_calls == 0
    assert controller.render_calls == 0
    assert controller.mode.get() == MODE_LABELS["fr"]["custom"]
    assert controller.mode.set_calls == 2
    assert controller._custom_last_ui_mode == "custom"
    assert controller._custom_last_ui_archetype == "continental"
    assert controller._custom_last_render_digest == controller._custom_config.digest


def test_global_mineral_mean_does_not_mark_start_bonus_modified():
    controller = _ProbeController()
    config = build_custom_config("upgraded")
    controller._custom_config = config
    controller._custom_section_baseline = default_sections(config.profile, config.base_mode)

    sections = config.semantic_sections()
    sections["minerals"]["average_quantity"]["coal"] = 5
    controller._custom_config = config.with_sections(sections)

    assert controller._custom_section_is_modified("minerals")
    assert not controller._custom_section_is_modified("start_bonus")


def test_custom_previews_read_profile_scalars_and_tk_variables():
    assert _read_preview_number(2736) == 2736.0
    assert _read_preview_number(_FakeVar("1683")) == 1683.0
    assert _read_preview_number("not-a-number", 7) == 7.0


def test_custom_sections_use_responsive_natural_width_layout():
    assert 'for column in range(3):\n            sections_frame.columnconfigure(column, weight=0)' in CUSTOM_CONTROLLER_SOURCE
    assert 'section_order = (' in CUSTOM_CONTROLLER_SOURCE
    assert '"start_bonus",\n            "minerals",\n            "fish",\n            "rivers",\n            "trees",\n            "building_stones",\n            "decorations",\n            "terrains",' in CUSTOM_CONTROLLER_SOURCE
    assert 'section_preferred_rows = (' in CUSTOM_CONTROLLER_SOURCE
    assert '("decorations", "terrains"),' in CUSTOM_CONTROLLER_SOURCE
    assert 'return {"start_bonus", "minerals"}' in CUSTOM_CONTROLLER_SOURCE
    assert 'return max(shell.winfo_reqwidth(), body.winfo_reqwidth())' in CUSTOM_CONTROLLER_SOURCE
    assert 'section_layout_gap = 16' in CUSTOM_CONTROLLER_SOURCE
    assert 'section_layout_safety_margin = 32' in CUSTOM_CONTROLLER_SOURCE
    assert 'section_pair_required_width(keys) + section_layout_safety_margin' in CUSTOM_CONTROLLER_SOURCE
    assert 'for candidate in (2,):' in CUSTOM_CONTROLLER_SOURCE
    assert 'available_width = max(0, root.winfo_width() - 28)' in CUSTOM_CONTROLLER_SOURCE
    assert 'self._custom_generator_tab._scroll_fit_width = True' in CUSTOM_CONTROLLER_SOURCE
    assert "fit_width=bool(getattr(inner,'_scroll_fit_width',False))" in SETTINGS_CONTROLLER_SOURCE
    assert 'target_width=available_w if fit_width else max(required_w,available_w)' in SETTINGS_CONTROLLER_SOURCE
    assert 'sections_frame.bind("<Configure>", schedule_section_relayout, add="+")' in CUSTOM_CONTROLLER_SOURCE
    assert 'root.bind("<Configure>", schedule_section_relayout, add="+")' in CUSTOM_CONTROLLER_SOURCE
    assert 'shell.grid_configure(' in CUSTOM_CONTROLLER_SOURCE
    assert 'columnspan=column_count' in CUSTOM_CONTROLLER_SOURCE
    assert 'section_layout_gap if column < len(row) - 1 else 0' in CUSTOM_CONTROLLER_SOURCE
    assert 'body.grid(\n                        row=1,\n                        column=0,\n                        columnspan=2,' in CUSTOM_CONTROLLER_SOURCE
    assert 'header.grid(row=0, column=0, sticky="w")' in CUSTOM_CONTROLLER_SOURCE
    assert 'sticky="nw"' in CUSTOM_CONTROLLER_SOURCE


def test_custom_generator_uses_natural_width_and_aligned_mineral_rows():
    assert 'algorithm_line.grid(row=0, column=0, columnspan=2, sticky="w"' in CUSTOM_CONTROLLER_SOURCE
    assert 'def add_aligned_spin(' in CUSTOM_CONTROLLER_SOURCE
    assert 'widget.grid(row=row, column=column, sticky="w", pady=2)' in CUSTOM_CONTROLLER_SOURCE
    assert 'row=row, column=column, sticky="w", padx=(5, 10), pady=2' in CUSTOM_CONTROLLER_SOURCE
    assert 'row=row, column=column, sticky="w", padx=(0, 8), pady=2' in CUSTOM_CONTROLLER_SOURCE
    assert 'row=row, column=column, sticky="w", pady=2' in CUSTOM_CONTROLLER_SOURCE
    assert 'quantity_frame.columnconfigure(1, minsize=24)' not in CUSTOM_CONTROLLER_SOURCE
    assert 'fish_grid.grid(row=0, column=0, sticky="nw")' in CUSTOM_CONTROLLER_SOURCE
    assert 'near_shore_line.grid(row=2, column=0, sticky="w", pady=(5, 2))' in CUSTOM_CONTROLLER_SOURCE
    assert 'band_thickness = add_spin(\n            fish_grid,\n            3,' in CUSTOM_CONTROLLER_SOURCE
    assert 'self._custom_fish_band_reason_var' not in CUSTOM_CONTROLLER_SOURCE
    assert 'tree_quota_grid.grid(row=0, column=0, sticky="nw")' in CUSTOM_CONTROLLER_SOURCE
    assert 'stone_grid.grid(row=0, column=0, sticky="nw")' in CUSTOM_CONTROLLER_SOURCE
    assert 'placement_line.grid(row=4, column=0, sticky="w", pady=1)' in CUSTOM_CONTROLLER_SOURCE
    assert 'tooltip_after_label=True' in CUSTOM_CONTROLLER_SOURCE
    assert 'custom_section_text("building_stone_group_average", language)' in CUSTOM_CONTROLLER_SOURCE
    assert 'custom_section_text("building_stone_group_variation", language)' in CUSTOM_CONTROLLER_SOURCE
    assert 'custom_section_text("terrain_hint", language)' not in CUSTOM_CONTROLLER_SOURCE
    assert 'objects_line.grid(row=0, column=0, sticky="w", pady=(0, 4))' in CUSTOM_CONTROLLER_SOURCE
    assert 'add_collapsible_section(' in CUSTOM_CONTROLLER_SOURCE
    assert '"decorations", 7, custom_section_text("decorations", language)' in CUSTOM_CONTROLLER_SOURCE
    assert '"terrains", 4, custom_section_text("terrains", language)' in CUSTOM_CONTROLLER_SOURCE
    assert '"start_bonus", 0, custom_section_text("start_bonus", language)' in CUSTOM_CONTROLLER_SOURCE
    assert '("start_bonus", "forest", "adult_trees_per_player")' in CUSTOM_CONTROLLER_SOURCE
    assert '("start_bonus", "building_stones", "anchors_per_player")' in CUSTOM_CONTROLLER_SOURCE
    assert '("start_bonus", "building_stones", "radius_min")' not in CUSTOM_CONTROLLER_SOURCE
    assert '("start_bonus", "building_stones", "radius_max")' not in CUSTOM_CONTROLLER_SOURCE
    assert 'ttk.Combobox(' in CUSTOM_CONTROLLER_SOURCE
    assert '("start_bonus", "mini_swamp", "shape")' in CUSTOM_CONTROLLER_SOURCE
    assert '("start_bonus", "mini_swamp", "radius")' in CUSTOM_CONTROLLER_SOURCE
    assert '("start_bonus", "rocky_minerals", f, "enabled")' in CUSTOM_CONTROLLER_SOURCE
    assert 'def add_rocky_spin(' in CUSTOM_CONTROLLER_SOURCE
    assert 'rocky_total_cells_max(active_count)' in CUSTOM_CONTROLLER_SOURCE
    assert 'rocky_proportional_targets(' in CUSTOM_CONTROLLER_SOURCE
    assert 'start_bonus_rocky_radius' in CUSTOM_CONTROLLER_SOURCE
    assert 'START_ROCKY_RADIUS_MAX' in CUSTOM_CONTROLLER_SOURCE
    assert 'image=self._custom_mineral_icons[family]' in CUSTOM_CONTROLLER_SOURCE
    assert '("start_bonus", "rocky_minerals", "radius_max")' in CUSTOM_CONTROLLER_SOURCE
    assert 'radius_state = "normal" if package_enabled and mode == "equal"' in CUSTOM_CONTROLLER_SOURCE
    assert 'total_state = "normal" if package_enabled and mode == "proportional"' in CUSTOM_CONTROLLER_SOURCE
    assert 'custom_state = "normal" if package_enabled and mode == "custom"' in CUSTOM_CONTROLLER_SOURCE
    assert 'start_bonus_rocky_core_header' in CUSTOM_CONTROLLER_SOURCE
    assert 'start_bonus_rocky_quantity_header' in CUSTOM_CONTROLLER_SOURCE
    assert 'icon_key=key' in CUSTOM_CONTROLLER_SOURCE
    assert 'disabled=True' in CUSTOM_CONTROLLER_SOURCE
    assert 'metric_x, metric_y = 2 * x - y, 2 * y' in Path(
        "s3mapgen/generation/custom/bonus_minerals.py"
    ).read_text(encoding="utf-8")
    assert 'shape_line = ttk.Frame(rocky_bonus)' in CUSTOM_CONTROLLER_SOURCE
    assert 'mode_line = ttk.Frame(rocky_bonus)' in CUSTOM_CONTROLLER_SOURCE
    assert 'radius_widget = add_start_spin(' in CUSTOM_CONTROLLER_SOURCE
    assert 'total_widget = add_start_spin(' in CUSTOM_CONTROLLER_SOURCE
    assert 'rocky_state = {}' in CUSTOM_CONTROLLER_SOURCE
    assert 'rocky_equivalent_radius(' in CUSTOM_CONTROLLER_SOURCE
    assert 'self._custom_materialize_rocky_state = materialize_rocky_state' in CUSTOM_CONTROLLER_SOURCE
    assert '("start_bonus", "lake_fish_river", "river_target_per_lake")' in CUSTOM_CONTROLLER_SOURCE
    assert 'START_BONUS_DISTANCE_MAX' in CUSTOM_CONTROLLER_SOURCE
    assert 'start_bonus_force_extended' in CUSTOM_CONTROLLER_SOURCE
    assert 'force_extended_radius' in CUSTOM_CONTROLLER_SOURCE
    assert 'force_extended_line = ttk.Frame(common_bonus)' in CUSTOM_CONTROLLER_SOURCE
    assert 'DECORATION_RATE_MAX' in CUSTOM_CONTROLLER_SOURCE
    assert '"start_bonus", 0, custom_section_text("start_bonus", language)' in CUSTOM_CONTROLLER_SOURCE
    assert '"minerals", 1, custom_section_text("minerals", language)' in CUSTOM_CONTROLLER_SOURCE
    assert 'def _custom_refresh_fish_controls(' in CUSTOM_CONTROLLER_SOURCE
    assert 'self._custom_fish_band_thickness_widget = band_thickness' in CUSTOM_CONTROLLER_SOURCE
    assert 'swamp_shape_line = ttk.Frame(swamp_bonus)' in CUSTOM_CONTROLLER_SOURCE
    assert 'lake_shape_line = ttk.Frame(lake_bonus)' in CUSTOM_CONTROLLER_SOURCE
    assert 'start_bonus_common' in CUSTOM_CONTROLLER_SOURCE
    assert 'start_bonus_objects' in CUSTOM_CONTROLLER_SOURCE
    assert 'start_bonus_terrain_resources' in CUSTOM_CONTROLLER_SOURCE
    assert 'common_bonus.grid(row=0, column=0, sticky="w"' in CUSTOM_CONTROLLER_SOURCE
    assert 'bonus_objects_grid = ttk.Frame(start_bonus)' in CUSTOM_CONTROLLER_SOURCE
    assert 'bonus_resources_grid = ttk.Frame(start_bonus)' in CUSTOM_CONTROLLER_SOURCE
    assert 'forest_bonus.grid(row=0, column=0, sticky="nw"' in CUSTOM_CONTROLLER_SOURCE
    assert 'stone_bonus.grid(row=0, column=1, sticky="nw"' in CUSTOM_CONTROLLER_SOURCE
    assert 'for column in range(3):\n            bonus_resources_grid.columnconfigure(column, weight=0)' in CUSTOM_CONTROLLER_SOURCE
    assert 'swamp_bonus.grid(row=0, column=2, sticky="nw"' in CUSTOM_CONTROLLER_SOURCE
    assert 'rocky_bonus.grid(row=0, column=1, sticky="nw"' in CUSTOM_CONTROLLER_SOURCE
    assert 'lake_bonus.grid(row=0, column=0, sticky="nw"' in CUSTOM_CONTROLLER_SOURCE
    assert 'def relayout_bonus_panels()' in CUSTOM_CONTROLLER_SOURCE
    assert 'bonus_group_fits(("forest", "stones"), available_width)' in CUSTOM_CONTROLLER_SOURCE
    assert 'bonus_group_fits(("lake", "rocky", "swamp"), available_width)' in CUSTOM_CONTROLLER_SOURCE
    assert 'layout_bonus_group(("lake", "rocky", "swamp"), 3)' in CUSTOM_CONTROLLER_SOURCE
    assert 'layout_bonus_group(("lake", "rocky"), 2)' in CUSTOM_CONTROLLER_SOURCE
    assert 'layout_bonus_group(("swamp",), 1, start_row=1)' in CUSTOM_CONTROLLER_SOURCE
    assert 'sections_frame.bind("<Configure>", schedule_bonus_panel_relayout, add="+")' in CUSTOM_CONTROLLER_SOURCE
    assert 'root.bind("<Configure>", schedule_bonus_panel_relayout, add="+")' in CUSTOM_CONTROLLER_SOURCE
    assert 'rocky_matrix = ttk.Frame(rocky_bonus' in CUSTOM_CONTROLLER_SOURCE
    assert 'line = ttk.Frame(rocky_matrix)' in CUSTOM_CONTROLLER_SOURCE
    assert 'add_start_preview(parent, row, variable' not in CUSTOM_CONTROLLER_SOURCE
    assert 'start_bonus_lake_settings' in CUSTOM_CONTROLLER_SOURCE
    assert 'start_bonus_river_settings' in CUSTOM_CONTROLLER_SOURCE
    assert 'start_bonus_fish_settings' in CUSTOM_CONTROLLER_SOURCE
    assert 'lake_bonus,\n            3,\n            custom_section_text("start_bonus_radius_min", language)' in CUSTOM_CONTROLLER_SOURCE
    assert 'lake_bonus,\n            8,\n            custom_section_text("start_bonus_river_target", language)' in CUSTOM_CONTROLLER_SOURCE
    assert 'custom_section_text("start_bonus_lake_proximity", language)' in CUSTOM_CONTROLLER_SOURCE
    assert 'self._custom_info_icons' in CUSTOM_CONTROLLER_SOURCE
    assert 'style="SectionToggle.TButton"' in CUSTOM_CONTROLLER_SOURCE
    assert 'custom_sections_expanded' in CUSTOM_CONTROLLER_SOURCE
    assert 'def _custom_reset_section(' in CUSTOM_CONTROLLER_SOURCE
    assert 'custom_section_text("section_modified", language)' in CUSTOM_CONTROLLER_SOURCE
    assert 'modified_label = ttk.Label(header_line, style="Modified.TLabel")' in CUSTOM_CONTROLLER_SOURCE
    assert "s.configure('Modified.TLabel'" in SETTINGS_CONTROLLER_SOURCE
    assert 'header_line = ttk.Frame(shell)' in CUSTOM_CONTROLLER_SOURCE
    assert 'header.configure(text=f"{arrow}  {title}")' in CUSTOM_CONTROLLER_SOURCE
    assert 'modified_label.grid(row=0, column=1, sticky="w", padx=(6, 0))' in CUSTOM_CONTROLLER_SOURCE
    assert 'reset_button.grid(row=0, column=2, sticky="w", padx=(6, 0))' in CUSTOM_CONTROLLER_SOURCE
    assert 'header.configure(text=f"{arrow}  {title}{suffix}")' not in CUSTOM_CONTROLLER_SOURCE
    assert 'stone_preview_var' in CUSTOM_CONTROLLER_SOURCE
    assert 'stone_preview_frame = ttk.LabelFrame(' in CUSTOM_CONTROLLER_SOURCE
    assert 'stone_preview_frame.grid(row=2, column=0, sticky="w"' in CUSTOM_CONTROLLER_SOURCE
    assert 'tree_preview_frame' not in CUSTOM_CONTROLLER_SOURCE
    assert 'self._custom_preview_size_trace = self.size.trace_add(' in CUSTOM_CONTROLLER_SOURCE
    assert 'refresh_custom_previews_for_size' in CUSTOM_CONTROLLER_SOURCE
    assert 'Activez « Pousses acceptées » pour régler' not in CUSTOM_CONTROLLER_SOURCE
    assert 'Activez « Forêts activées » pour régler' not in CUSTOM_CONTROLLER_SOURCE
    assert 'Activez « Groupes activés » pour régler' not in CUSTOM_CONTROLLER_SOURCE
    assert 'custom_section_text("objects_grass_compatible", language)' in CUSTOM_CONTROLLER_SOURCE
    assert 'Étend les supports des arbres' in CUSTOM_CONTROLLER_SOURCE
    assert 'Legacy : motifs historiques.\\nUpgraded' in CUSTOM_CONTROLLER_SOURCE


def test_application_comboboxes_are_read_only_selectors():
    """A list selector must never turn into an editable text field."""

    root = Path("s3mapgen/application")
    for source_path in root.rglob("*.py"):
        tree = ast.parse(source_path.read_text(encoding="utf-8"), filename=str(source_path))
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Attribute):
                continue
            owner = node.func.value
            if not (
                node.func.attr == "Combobox"
                and isinstance(owner, ast.Name)
                and owner.id == "ttk"
            ):
                continue
            state = next((keyword.value for keyword in node.keywords if keyword.arg == "state"), None)
            assert isinstance(state, ast.Constant) and state.value == "readonly", (
                f"{source_path}:{node.lineno} creates an editable Combobox"
            )


def test_custom_preview_and_object_labels_cover_every_language():
    languages = {"fr", "en", "de", "es"}
    for key in (
        "objects_grass_compatible",
        "start_bonus_common",
        "start_bonus_objects",
        "start_bonus_terrain_resources",
        "start_bonus_lake_settings",
        "start_bonus_river_settings",
        "start_bonus_fish_settings",
        "start_bonus_fish_fill_hint",
        "estimated_preview",
        "preview_map_size",
        "preview_global_stones",
        "preview_active_stones",
        "preview_stock_units",
        "preview_groups",
        "preview_groups_disabled",
        "preview_placement_note",
    ):
        assert set(_CUSTOM_SECTION_TEXT[key]) == languages


def test_grass_variant_label_is_short_and_leaves_detail_to_the_tooltip():
    label = _CUSTOM_SECTION_TEXT["objects_grass_compatible"]["fr"]
    assert len(label) < 40
    assert "Herbe sèche" not in label
    assert "Détails" not in label


def test_fish_coastal_tooltip_explains_what_is_limited():
    hint = _CUSTOM_SECTION_TEXT["coast_hint"]["fr"]
    assert "ressources en poissons" in hint
    assert "proche des côtes" in hint
    assert "Active une bande côtière" not in hint


def test_only_building_stone_preview_remains_and_stays_compact():
    assert '"preview_forests" if forests_enabled else "preview_forests_disabled"' not in CUSTOM_CONTROLLER_SOURCE
    assert '"preview_groups" if groups_enabled else "preview_groups_disabled"' in CUSTOM_CONTROLLER_SOURCE
    assert 'labelwidget=tree_preview_title' not in CUSTOM_CONTROLLER_SOURCE
    assert 'labelwidget=stone_preview_title' in CUSTOM_CONTROLLER_SOURCE
    assert CUSTOM_CONTROLLER_SOURCE.count(
        'custom_section_text("preview_placement_note", language),'
    ) == 1
