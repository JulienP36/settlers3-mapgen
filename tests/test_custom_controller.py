import ast
from pathlib import Path

from s3mapgen.application.custom.controller import CustomGeneratorController
from s3mapgen.application.ui.i18n.shell import MODE_LABELS
from s3mapgen.generation.custom import build_custom_config


CUSTOM_CONTROLLER_SOURCE = Path(
    "s3mapgen/application/custom/controller.py"
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

    def _mode_key(self):
        return "custom" if self.mode.get() == "Custom" else "upgraded"

    def _custom_render_custom_mode(self, config):
        self.provenance_refreshes += 1

    def _selection_changed(self):
        self.selection_calls += 1


def test_custom_parameter_edits_do_not_rebuild_the_selection_ui():
    controller = _ProbeController()
    base = build_custom_config("upgraded")

    controller._custom_activate(base.with_value("minerals.occupancy_percent", 42))

    assert controller.selection_calls == 0
    assert controller.provenance_refreshes == 1
    assert controller.mode.set_calls == 0


def test_first_custom_parameter_edit_still_enters_custom_mode_once():
    controller = _ProbeController()
    controller.mode.set("Upgraded")
    base = build_custom_config("upgraded")

    controller._custom_activate(base.with_value("minerals.occupancy_percent", 42))

    assert controller.selection_calls == 1
    assert controller.mode.get() == MODE_LABELS["fr"]["custom"]
    assert controller.mode.set_calls == 2


def test_custom_generator_uses_natural_width_and_aligned_mineral_rows():
    assert 'algorithm_line.grid(row=0, column=0, columnspan=2, sticky="w"' in CUSTOM_CONTROLLER_SOURCE
    assert 'def add_aligned_spin(' in CUSTOM_CONTROLLER_SOURCE
    assert 'widget.grid(row=row, column=column, sticky="w", pady=2)' in CUSTOM_CONTROLLER_SOURCE
    assert 'row=row, column=column, sticky="w", padx=(5, 10), pady=2' in CUSTOM_CONTROLLER_SOURCE
    assert 'row=row, column=column, sticky="w", padx=(0, 8), pady=2' in CUSTOM_CONTROLLER_SOURCE
    assert 'row=row, column=column, sticky="w", pady=2' in CUSTOM_CONTROLLER_SOURCE
    assert 'quantity_frame.columnconfigure(1, minsize=24)' not in CUSTOM_CONTROLLER_SOURCE
    assert 'fish_grid.grid(row=0, column=0, columnspan=2, sticky="nw")' in CUSTOM_CONTROLLER_SOURCE
    assert 'tree_quota_grid.grid(row=0, column=0, columnspan=2, sticky="nw")' in CUSTOM_CONTROLLER_SOURCE
    assert 'stone_grid.grid(row=0, column=0, columnspan=2, sticky="nw")' in CUSTOM_CONTROLLER_SOURCE
    assert 'text=custom_section_text("decorations", language)' in CUSTOM_CONTROLLER_SOURCE
    assert 'text=custom_section_text("terrains", language)' in CUSTOM_CONTROLLER_SOURCE
    assert 'text=custom_section_text("start_bonus", language)' in CUSTOM_CONTROLLER_SOURCE
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
    assert 'mode_combo.grid(row=2, column=1' in CUSTOM_CONTROLLER_SOURCE
    assert 'rocky_state = {}' in CUSTOM_CONTROLLER_SOURCE
    assert 'rocky_equivalent_radius(' in CUSTOM_CONTROLLER_SOURCE
    assert 'self._custom_materialize_rocky_state = materialize_rocky_state' in CUSTOM_CONTROLLER_SOURCE
    assert '("start_bonus", "lake_fish_river", "river_target_per_lake")' in CUSTOM_CONTROLLER_SOURCE
    assert 'START_BONUS_DISTANCE_MAX' in CUSTOM_CONTROLLER_SOURCE
    assert 'start_bonus_force_extended' in CUSTOM_CONTROLLER_SOURCE
    assert 'force_extended_radius' in CUSTOM_CONTROLLER_SOURCE
    assert 'DECORATION_RATE_MAX' in CUSTOM_CONTROLLER_SOURCE
    assert CUSTOM_CONTROLLER_SOURCE.index('start_bonus.grid(row=0') > CUSTOM_CONTROLLER_SOURCE.index('minerals.grid(row=1')
    assert 'def _custom_refresh_fish_controls(' in CUSTOM_CONTROLLER_SOURCE
    assert 'self._custom_fish_band_thickness_widget = band_thickness' in CUSTOM_CONTROLLER_SOURCE
    assert 'swamp_shape_line = ttk.Frame(swamp_bonus)' in CUSTOM_CONTROLLER_SOURCE
    assert 'lake_shape_line = ttk.Frame(lake_bonus)' in CUSTOM_CONTROLLER_SOURCE
    assert 'for column in range(2):\n            lake_bonus.columnconfigure(column, weight=0)' in CUSTOM_CONTROLLER_SOURCE
    assert 'column=0,\n        )\n        add_start_spin(\n            lake_bonus,\n            3,' in CUSTOM_CONTROLLER_SOURCE
    assert 'custom_section_text("start_bonus_lake_proximity", language)' in CUSTOM_CONTROLLER_SOURCE


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
