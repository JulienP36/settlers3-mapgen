import ast
import threading
import pytest
from copy import deepcopy
from pathlib import Path
from types import SimpleNamespace

from s3mapgen.application.custom.controller import (
    CustomGeneratorController,
    _archetype_effective_preview_profile,
    _archetype_ui_parameter_descriptors,
    _configure_integer_spinbox_steps,
    _read_preview_number,
)
from s3mapgen.application.custom.i18n import _CUSTOM_SECTION_TEXT
from s3mapgen.application.ui.i18n.shell import ARCHETYPE_INPUT_LABELS, MODE_LABELS
from s3mapgen.generation.custom import build_custom_config, default_sections
from s3mapgen.generation.archetypes import (
    CONTINENTAL_CUSTOM_PROFILE_KEY,
    continental_legacy_blocks_profile,
    RELIEF_SOURCE_CUSTOM_LEGACY,
    default_archetype_profile,
)


CUSTOM_CONTROLLER_SOURCE = Path(
    "s3mapgen/application/custom/controller.py"
).read_text(encoding="utf-8")
SETTINGS_CONTROLLER_SOURCE = Path(
    "s3mapgen/application/settings/controller.py"
).read_text(encoding="utf-8")
SHELL_FOUNDATION_SOURCE = Path(
    "s3mapgen/application/shell/foundation.py"
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


class _FakeSpinbox:
    def __init__(self):
        self.options = {}
        self.bindings = {}

    def configure(self, **kwargs):
        self.options.update(kwargs)

    def instate(self, states):
        return self.options.get("state", "normal") in states

    def bind(self, sequence, callback, add=None):
        self.bindings[sequence] = callback


def test_integer_spinboxes_use_one_for_arrows_and_five_for_each_wheel_notch():
    widget = _FakeSpinbox()
    value = _FakeVar("100")
    callbacks = []
    _configure_integer_spinbox_steps(
        widget, value, 0, 200, lambda: callbacks.append(value.get())
    )

    assert widget.options["increment"] == 1
    assert widget.bindings["<MouseWheel>"](SimpleNamespace(delta=120)) == "break"
    assert value.get() == "105"
    assert widget.bindings["<MouseWheel>"](SimpleNamespace(delta=-240)) == "break"
    assert value.get() == "95"
    widget.bindings["<Button-4>"](SimpleNamespace(num=4))
    assert value.get() == "100"
    assert callbacks == ["105", "95", "100"]


class _FakeProgressBar:
    def __init__(self):
        self.values = []

    def configure(self, *, value):
        self.values.append(value)


class _FakeStateWidget:
    def __init__(self):
        self.states = []

    def configure(self, *, state):
        self.states.append(state)


def test_archetype_parameter_tooltip_icon_uses_hover_visual_state():
    start = CUSTOM_CONTROLLER_SOURCE.index("        def add_archetype_spin(")
    block = CUSTOM_CONTROLLER_SOURCE[
        start:
        CUSTOM_CONTROLLER_SOURCE.index("        for descriptor in descriptors:", start)
    ]
    assert '\"<Enter>\"' in block
    assert '\"<Leave>\"' in block
    assert "image=icons[2]" in block
    assert "image=icons[1]" in block


def test_default_map_size_starts_at_512():
    assert "self.size=tk.StringVar(value='512')" in SHELL_FOUNDATION_SOURCE


def test_inactive_fusion_and_mask_slots_do_not_change_preview_profile():
    profile = default_archetype_profile()
    with_disabled_slots = deepcopy(profile)
    with_disabled_slots["morphology"]["noise_layer_count"] = 1
    with_disabled_slots["morphology"]["mask_layer_count"] = 1

    assert _archetype_effective_preview_profile(profile) == (
        _archetype_effective_preview_profile(with_disabled_slots)
    )

    with_disabled_slots["morphology"]["noise_layers"][0]["enabled"] = True
    assert _archetype_effective_preview_profile(profile) != (
        _archetype_effective_preview_profile(with_disabled_slots)
    )


def test_adding_disabled_layer_activates_profile_without_full_preview():
    controller = CustomGeneratorController.__new__(CustomGeneratorController)
    config = build_custom_config("legacy", "continental")
    controller._custom_config = config
    controller._custom_current_mode = lambda: "legacy"
    controller._custom_language = lambda: "fr"
    controller._custom_status_var = _FakeVar("")
    scheduled = []
    controller._custom_schedule_archetype_preview_refresh = lambda **kwargs: scheduled.append(kwargs)
    controller._custom_refresh_archetype_header = lambda: None
    controller._custom_refresh_archetype_ranges = lambda: None
    controller._custom_refresh_archetype_section_reset_buttons = lambda: None

    profile = deepcopy(config.archetype_profile)
    profile["morphology"]["noise_layer_count"] = 1
    controller._custom_activate_archetype(config.with_archetype_profile(profile))

    assert scheduled == [{"refresh_main": False}]


def test_legacy_block_controls_are_excluded_from_visible_descriptors():
    keys = {
        descriptor.key
        for descriptor in _archetype_ui_parameter_descriptors(
            default_archetype_profile()
        )
    }
    assert "morphology.native_sculpture_attempts_percent" not in keys
    assert "morphology.native_relaxation_strength_percent" not in keys


def test_continental_profile_selector_offers_classic_and_current_relief():
    controller = CustomGeneratorController.__new__(CustomGeneratorController)
    controller._custom_current_archetype = lambda: "continental"

    options = controller._custom_archetype_profile_options("fr")
    presets = controller._custom_archetype_profile_presets()

    assert options == {
        "native": "Classique",
        CONTINENTAL_CUSTOM_PROFILE_KEY: "Continental",
        "large_islands": "Grandes îles",
    }
    assert set(presets) == {"native", CONTINENTAL_CUSTOM_PROFILE_KEY, "large_islands"}
    assert presets[CONTINENTAL_CUSTOM_PROFILE_KEY] == continental_legacy_blocks_profile()


def test_archetype_edits_change_the_profile_selector_to_custom():
    controller = CustomGeneratorController.__new__(CustomGeneratorController)
    controller._custom_current_archetype = lambda: "continental"
    controller._custom_language = lambda: "fr"
    profile = continental_legacy_blocks_profile()
    profile["relief"]["mountain_threshold"] += 1
    controller._custom_config = build_custom_config("legacy").with_archetype_profile(profile)
    controller._custom_archetype_profile_var = _FakeVar("Continental")
    controller._custom_archetype_modified_label = None
    controller._custom_archetype_reset_button = None

    controller._custom_refresh_archetype_header()

    assert controller._custom_archetype_profile_var.get() == "Profil personnalisé"


def test_main_archetype_selector_applies_the_named_continental_profile():
    controller = CustomGeneratorController.__new__(CustomGeneratorController)
    controller._custom_current_archetype = lambda: "continental"
    controller._custom_current_mode = lambda: "legacy"
    controller._custom_language = lambda: "fr"
    controller.arch = _FakeVar("Continental")
    controller.arch_input = _FakeVar("Continental")
    controller._custom_main_archetype_input_options = lambda _language: {
        "classic": "Classique",
        "continental": "Continental",
        "large_islands": "Grandes îles",
        "small_islands": "Petites îles",
    }
    controller._custom_ensure_config = lambda mode, archetype: build_custom_config(
        mode or "legacy", archetype
    )
    controller._selection_changed = lambda: None
    controller._custom_activate_archetype = lambda config: setattr(controller, "_custom_config", config)
    controller._custom_sync_archetype_editor_values = lambda: None
    controller._custom_status_var = _FakeVar("")
    controller.arch_input.set(ARCHETYPE_INPUT_LABELS["fr"]["continental"])

    controller._custom_main_archetype_input_changed()

    assert controller.arch.get() == "Continental"
    assert controller._custom_config.archetype_profile == continental_legacy_blocks_profile()
    assert controller._custom_config.base_mode == "legacy"


def test_main_archetype_selector_classic_choice_restores_native_profile():
    controller = CustomGeneratorController.__new__(CustomGeneratorController)
    controller._custom_current_archetype = lambda: "continental"
    controller._custom_current_mode = lambda: "legacy"
    controller._custom_language = lambda: "fr"
    controller.arch = _FakeVar("Continental")
    controller.arch_input = _FakeVar("Classique")
    controller._custom_main_archetype_input_options = lambda _language: {
        "classic": "Classique",
        "continental": "Continental",
        "large_islands": "Grandes îles",
        "small_islands": "Petites îles",
    }
    controller._custom_ensure_config = lambda mode, archetype: build_custom_config(
        mode or "legacy", archetype
    ).with_archetype_profile(continental_legacy_blocks_profile())
    controller._selection_changed = lambda: None
    controller._custom_activate_archetype = lambda config: setattr(controller, "_custom_config", config)
    controller._custom_sync_archetype_editor_values = lambda: None
    controller._custom_status_var = _FakeVar("")

    controller._custom_main_archetype_input_changed()

    assert controller._custom_config.archetype_profile == default_archetype_profile("continental")
    assert controller._custom_config.base_mode == "legacy"


def test_archetype_edit_marks_both_profile_selectors_as_custom():
    controller = CustomGeneratorController.__new__(CustomGeneratorController)
    controller._custom_current_archetype = lambda: "continental"
    controller._custom_language = lambda: "fr"
    profile = continental_legacy_blocks_profile()
    profile["relief"]["mountain_threshold"] += 1
    controller._custom_config = build_custom_config("legacy").with_archetype_profile(profile)
    controller._custom_profile_for_display = lambda: controller._custom_config
    controller._custom_archetype_profile_var = _FakeVar("Continental")
    controller._custom_archetype_profile_combo = _FakeSpinbox()
    controller.arch_input = _FakeVar("Continental")
    controller.arch_combo = _FakeSpinbox()
    controller._custom_archetype_modified_label = None
    controller._custom_archetype_reset_button = None

    controller._custom_refresh_archetype_header()

    assert controller._custom_archetype_profile_var.get() == "Profil personnalisé"
    assert controller.arch_input.get() == "Personnalisé"
    assert "Personnalisé" in controller.arch_combo.options["values"]


@pytest.mark.parametrize("origin,target", [
    ("continental", "large_islands"), ("large_islands", "native"),
    ("large_islands", "continental_custom_r82"),
])
def test_profile_of_base_changes_the_archetype_and_preserves_generator_settings(origin, target):
    controller = CustomGeneratorController.__new__(CustomGeneratorController)
    controller._custom_config = build_custom_config("upgraded", origin).with_value(
        "minerals.mountain_occupancy_target", 0.61,
    )
    controller._custom_current_archetype = lambda: origin
    controller._custom_current_mode = lambda: "custom"
    controller._custom_language = lambda: "fr"
    controller._custom_ensure_config = lambda *args: controller._custom_config
    controller.arch = _FakeVar(origin)
    controller._custom_archetype_profile_var = _FakeVar(
        controller._custom_archetype_profile_options("fr")[target],
    )
    changed = []
    controller._selection_changed = lambda: pytest.fail("A profile choice must not rebuild the tabs")
    controller._custom_sync_archetype_editor_values = lambda: changed.append(True)
    controller._custom_status_var = _FakeVar("")
    controller._custom_schedule_archetype_preview_refresh = lambda **kwargs: None
    before = deepcopy(controller._custom_config.profile)
    sections_before = controller._custom_config.semantic_sections()
    controller._custom_river_algorithm_var = _FakeVar("Classique")
    controller._custom_package_vars = {"start_mini_swamp": _FakeVar(False)}
    controller._custom_archetype_profile_changed()
    expected = controller._custom_archetype_profile_presets()[target]
    assert controller._custom_config.archetype_profile == expected
    assert controller._custom_config.base_archetype == expected["archetype_key"]
    assert controller._custom_config.profile == before
    expected_sections = deepcopy(sections_before)
    expected_sections["rivers"]["algorithm"] = "native" if target == "native" else "improved"
    assert controller._custom_river_algorithm_var.get() == ("Classique" if target == "native" else "Amélioré")
    assert controller._custom_config.semantic_sections() == expected_sections
    assert controller._custom_package_vars["start_mini_swamp"].get() == (target == "large_islands")
    assert ("start_mini_swamp" in controller._custom_config.start_packages) == (target == "large_islands")
    assert controller._custom_config.base_mode == "upgraded"
    assert changed == [True]


@pytest.mark.parametrize("origin,source", [("large_islands", "perlin"), ("continental", "large_islands")])
def test_source_selector_really_switches_both_directions_without_forcing_a_preset(origin, source):
    import s3mapgen.application.custom.controller as module
    controller = CustomGeneratorController.__new__(CustomGeneratorController)
    config = build_custom_config("upgraded", origin)
    controller._custom_config = config
    controller._custom_current_archetype = lambda: origin
    controller._custom_current_mode = lambda: "upgraded"
    controller._custom_language = lambda: "fr"
    controller._custom_ensure_config = lambda *args: config
    controller._custom_archetype_relief_source_var = _FakeVar(
        controller._custom_archetype_relief_source_options("fr")[source],
    )
    controller._custom_archetype_relief_source_vars = {
        key: _FakeVar(value) for key, value in module.NOISE_SOURCE_SETTING_DEFAULTS.items()
    }
    mask = module.NOISE_MASK_DEFAULTS.copy()
    mask["type"] = controller._custom_archetype_noise_mask_options("fr")[mask["type"]]
    mask["source"] = controller._custom_archetype_noise_family_options("fr")[mask["source"]]
    controller._custom_archetype_relief_mask_vars = {key: _FakeVar(value) for key, value in mask.items()}
    controller._custom_refresh_archetype_noise_setting_states = lambda *args: None
    controller._custom_status_var = _FakeVar("")
    controller._custom_activate_archetype = lambda cfg: setattr(controller, "_custom_config", cfg)
    controller._custom_archetype_relief_source_changed()
    assert controller._custom_status_var.get() == ""
    assert controller._custom_config.base_archetype == origin
    assert controller._custom_config.archetype_profile["morphology"]["relief_source"] == source
    assert controller._custom_archetype_profile_selection_key(controller._custom_config.archetype_profile) == "edited"


def test_relief_source_selector_includes_custom_legacy_blocks():
    controller = CustomGeneratorController.__new__(CustomGeneratorController)
    options = controller._custom_archetype_relief_source_options("fr")

    assert RELIEF_SOURCE_CUSTOM_LEGACY in options
    assert options[RELIEF_SOURCE_CUSTOM_LEGACY] == "Composition · Legacy par blocs"


def test_native_block_controls_only_apply_to_native_or_custom_legacy_sources():
    control_keys = (
        "native_coarse_variation_percent",
        "native_refinement_percent",
        "native_large_scale_refinement_percent",
        "native_fine_scale_refinement_percent",
        "native_sculpture_attempts_percent",
        "native_relaxation_strength_percent",
    )
    for source, expected in (
        ("native_legacy", "normal"),
        ("legacy_blocks", "normal"),
        ("perlin", "disabled"),
    ):
        controller = CustomGeneratorController.__new__(CustomGeneratorController)
        controller._custom_archetype_editor_editable = True
        controller._custom_language = lambda: "fr"
        controller._custom_archetype_relief_setting_widget_map = {}
        controller._custom_archetype_relief_mask_vars = {}
        controller._custom_archetype_noise_layer_setting_widgets = {}
        controller._custom_archetype_noise_layer_vars = {}
        controller._custom_archetype_spinboxes = {
            f"morphology.{key}": _FakeStateWidget() for key in control_keys
        }
        controller._custom_archetype_spinboxes["morphology.shape_scale_percent"] = _FakeStateWidget()

        controller._custom_refresh_archetype_noise_setting_states(source)

        assert all(
            widget.states[-1] == expected
            for widget in controller._custom_archetype_spinboxes.values()
            if widget is not controller._custom_archetype_spinboxes["morphology.shape_scale_percent"]
        )
        assert controller._custom_archetype_spinboxes[
            "morphology.shape_scale_percent"
        ].states[-1] == ("disabled" if source == "legacy_blocks" else "normal")


class _FakeImageCanvas:
    def __init__(self):
        self.next_id = 1
        self.created = []
        self.configured = []
        self.positioned = []

    def create_image(self, x, y, *, image, anchor):
        item_id = self.next_id
        self.next_id += 1
        self.created.append((item_id, x, y, image, anchor))
        return item_id

    def itemconfigure(self, item_id, *, image):
        self.configured.append((item_id, image))

    def coords(self, item_id, x, y):
        self.positioned.append((item_id, x, y))


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


class _FakeNotebook:
    def __init__(self, selected):
        self.selected = selected

    def select(self):
        return self.selected


class _FakeArchetypeHost:
    def __str__(self):
        return ".archetype_host"


class _FakeArchetypeTab:
    def __init__(self):
        self._scroll_host = _FakeArchetypeHost()
        self.after_calls = 0

    def after(self, _delay, _callback):
        self.after_calls += 1
        return "preview-after"

    def after_cancel(self, _after_id):
        return None


def _preview_gate_probe(selected):
    controller = _ProbeController()
    controller.nb = _FakeNotebook(selected)
    controller._custom_archetype_tab = _FakeArchetypeTab()
    controller._custom_archetype_preview_canvases = {"noise": object()}
    controller._custom_archetype_preview_after = None
    controller._custom_archetype_preview_poll_after = None
    controller._custom_archetype_preview_refresh_pending = False
    controller._custom_archetype_preview_request_id = 0
    controller._custom_archetype_preview_request = None
    controller._custom_archetype_preview_completed = None
    controller._custom_archetype_preview_progress = None
    controller._custom_archetype_preview_lock = threading.Lock()
    return controller


def test_archetype_preview_is_deferred_until_its_tab_is_active():
    controller = _preview_gate_probe(".generator_host")

    controller._custom_schedule_archetype_preview_refresh()

    assert controller._custom_archetype_preview_refresh_pending is True
    assert controller._custom_archetype_preview_after is None
    assert controller._custom_archetype_tab.after_calls == 0


def test_archetype_preview_is_scheduled_when_its_tab_is_active():
    controller = _preview_gate_probe(".archetype_host")

    controller._custom_schedule_archetype_preview_refresh()

    assert controller._custom_archetype_preview_refresh_pending is False
    assert controller._custom_archetype_preview_after == "preview-after"
    assert controller._custom_archetype_tab.after_calls == 1


def test_archetype_relaxation_toggle_invalidates_old_preview_state():
    controller = _preview_gate_probe(".archetype_host")
    controller._custom_archetype_preview_noise_cache = {"old": object()}
    controller._custom_archetype_preview_raw_noise_cache = {"old": object()}
    old_request_id = controller._custom_archetype_preview_request_id

    controller._custom_archetype_preview_relaxation_changed()

    assert controller._custom_archetype_preview_request_id == old_request_id + 1
    assert controller._custom_archetype_preview_noise_cache == {}
    assert controller._custom_archetype_preview_raw_noise_cache == {}
    assert controller._custom_archetype_tab.after_calls == 1


def test_archetype_preview_queue_rechecks_tab_before_starting_work():
    controller = _preview_gate_probe(".generator_host")

    controller._custom_queue_archetype_preview()

    assert controller._custom_archetype_preview_refresh_pending is True
    assert controller._custom_archetype_preview_request is None


def test_archetype_solo_isolated_to_preview_copy():
    controller = CustomGeneratorController.__new__(CustomGeneratorController)
    controller._custom_archetype_noise_layer_solo = 1
    profile = default_archetype_profile()
    profile["morphology"]["noise_layer_count"] = 2
    profile["morphology"]["noise_layers"][0]["enabled"] = True
    profile["morphology"]["noise_layers"][1]["enabled"] = True

    preview_profile = controller._custom_archetype_preview_profile(deepcopy(profile))

    assert preview_profile["morphology"]["noise_layers"][0]["enabled"] is False
    assert preview_profile["morphology"]["noise_layers"][1]["enabled"] is True
    assert profile["morphology"]["noise_layers"][0]["enabled"] is True
    assert profile["morphology"]["noise_layers"][1]["enabled"] is True


def test_archetype_solo_does_not_bypass_disabled_layer():
    controller = CustomGeneratorController.__new__(CustomGeneratorController)
    controller._custom_archetype_noise_layer_solo = 1
    profile = default_archetype_profile()
    profile["morphology"]["noise_layer_count"] = 2
    profile["morphology"]["noise_layers"][0]["enabled"] = True
    profile["morphology"]["noise_layers"][1]["enabled"] = False

    preview_profile = controller._custom_archetype_preview_profile(deepcopy(profile))

    assert preview_profile["morphology"]["noise_layers"][0]["enabled"] is False
    assert preview_profile["morphology"]["noise_layers"][1]["enabled"] is False


def test_archetype_preview_progress_is_monotone_until_explicit_reset():
    controller = CustomGeneratorController.__new__(CustomGeneratorController)
    progress_bar = _FakeProgressBar()
    controller._custom_archetype_preview_progress_bar = progress_bar

    controller._custom_set_archetype_preview_progress(0.15, reset=True)
    controller._custom_set_archetype_preview_progress(0.35)
    controller._custom_set_archetype_preview_progress(0.20)
    controller._custom_set_archetype_preview_progress(1.0)
    controller._custom_set_archetype_preview_progress(0.10, reset=True)

    assert progress_bar.values == [15.0, 35.0, 35.0, 100.0, 10.0]


def test_archetype_preview_worker_commits_only_the_exact_result(monkeypatch):
    import s3mapgen.application.custom.controller as controller_module

    controller = CustomGeneratorController.__new__(CustomGeneratorController)
    controller._custom_archetype_preview_lock = threading.Lock()
    controller._custom_archetype_preview_request_id = 1
    controller._custom_archetype_preview_request = (
        1,
        {"morphology": {}},
        64,
        17,
        0,
        False,
    )
    controller._custom_archetype_preview_worker = object()
    controller._custom_archetype_preview_completed = None
    controller._custom_archetype_preview_noise_completed = None
    controller._custom_archetype_preview_raw_noise_cache = {}
    controller._custom_archetype_preview_noise_cache = {}
    exact = SimpleNamespace(
        noise="exact-noise",
        noise_lab=None,
    )
    preview_calls = []

    def preview(*args, **kwargs):
        assert controller._custom_archetype_components_completed[0] == 1
        preview_calls.append((args, kwargs))
        return exact

    monkeypatch.setattr(
        controller_module,
        "generate_archetype_preview",
        preview,
    )
    monkeypatch.setattr(
        controller_module,
        "generate_noise_component_previews",
        lambda *_args, **_kwargs: ("source", ("layer",)),
    )
    monkeypatch.setattr(
        controller_module,
        "generate_mask_component_previews",
        lambda *_args, **_kwargs: ("mask",),
    )

    controller._custom_archetype_preview_worker_loop()

    assert len(preview_calls) == 1
    assert preview_calls[0][1]["relax_macro"] is False
    assert controller._custom_archetype_preview_noise_completed is None
    completed = controller._custom_archetype_preview_completed
    assert completed[:3] == (1, exact, None)
    assert completed[3] == "source"
    assert completed[4] == ("layer",)
    assert completed[5] is not None


def test_component_only_preview_skips_full_map_calculation(monkeypatch):
    import s3mapgen.application.custom.controller as controller_module

    controller = CustomGeneratorController.__new__(CustomGeneratorController)
    controller._custom_archetype_preview_lock = threading.Lock()
    controller._custom_archetype_preview_request_id = 4
    controller._custom_archetype_preview_request = (
        4,
        {"morphology": {}},
        64,
        17,
        0,
        False,
        False,
    )
    controller._custom_archetype_preview_worker = object()
    controller._custom_archetype_preview_completed = None
    controller._custom_archetype_preview_noise_cache = {}
    controller._custom_archetype_component_cache = {}

    def fail_full_preview(*_args, **_kwargs):
        raise AssertionError("a disabled slot must not trigger a full map preview")

    monkeypatch.setattr(
        controller_module,
        "generate_archetype_preview",
        fail_full_preview,
    )
    monkeypatch.setattr(
        controller_module,
        "generate_noise_component_previews",
        lambda *_args, **_kwargs: ("source", ("layer",)),
    )
    monkeypatch.setattr(
        controller_module,
        "generate_mask_component_previews",
        lambda *_args, **_kwargs: ("mask",),
    )

    controller._custom_archetype_preview_worker_loop()

    assert controller._custom_archetype_preview_completed is None
    assert controller._custom_archetype_components_completed == (
        4,
        "source",
        ("layer",),
        ("mask",),
        None,
    )


def test_archetype_preview_replaces_image_items_without_clearing_canvas():
    controller = CustomGeneratorController.__new__(CustomGeneratorController)
    controller._custom_archetype_preview_image_items = {}
    canvas = _FakeImageCanvas()
    first_photo = object()
    second_photo = object()

    controller._custom_update_archetype_preview_image_item(
        "noise", canvas, first_photo, 50, 60
    )
    controller._custom_update_archetype_preview_image_item(
        "noise", canvas, second_photo, 55, 65
    )

    assert len(canvas.created) == 1
    assert canvas.created[0][1:3] == (50, 60)
    assert canvas.configured == [(1, second_photo)]
    assert canvas.positioned == [(1, 55, 65)]


def test_archetype_preview_fast_phase_updates_panels_without_blank_frame():
    controller = CustomGeneratorController.__new__(CustomGeneratorController)
    old_snapshot = ("old-noise", "old-macro", 256, 41)
    old_lab = object()
    controller._custom_archetype_preview_last_snapshot = old_snapshot
    controller._custom_archetype_preview_last_lab = old_lab
    controller._custom_archetype_preview_status_var = _FakeVar("calcul")
    controller._custom_archetype_preview_stats_var = _FakeVar("old stats")
    controller._custom_archetype_preview_progress_bar = _FakeProgressBar()
    controller.prefs = {"language": "fr"}
    render_calls = []

    def record_render(*args, **kwargs):
        render_calls.append((args, kwargs))
        return True

    controller._custom_render_archetype_preview_rasters = record_render
    new_lab = object()

    controller._custom_apply_archetype_noise_preview(
        "new-noise",
        "new-macro",
        512,
        99,
        new_lab,
    )

    assert len(render_calls) == 2
    assert render_calls[0][0][:2] == ("new-noise", None)
    assert render_calls[1][0][:2] == (None, "new-macro")
    assert controller._custom_archetype_preview_last_snapshot == (
        "new-noise", "new-macro", 512, 99
    )
    assert controller._custom_archetype_preview_last_lab is new_lab
    assert controller._custom_archetype_preview_stats_var.value == "old stats"
    assert controller._custom_archetype_preview_progress_bar.values == [15.0]


def test_archetype_preview_error_keeps_the_last_committed_triptych():
    controller = CustomGeneratorController.__new__(CustomGeneratorController)
    old_snapshot = ("old-noise", "old-macro", 256, 41)
    old_lab = object()
    canvas = _FakeImageCanvas()
    controller._custom_archetype_preview_last_snapshot = old_snapshot
    controller._custom_archetype_preview_last_lab = old_lab
    controller._custom_archetype_preview_status_var = _FakeVar("old status")
    controller._custom_archetype_preview_stats_var = _FakeVar("old stats")
    controller._custom_archetype_preview_progress_bar = _FakeProgressBar()
    controller._custom_archetype_preview_canvases = {"noise": canvas}
    controller._custom_archetype_preview_image_items = {"noise": 7}

    controller._custom_set_archetype_preview_placeholder("new request invalid")

    assert controller._custom_archetype_preview_status_var.value == "new request invalid"
    assert controller._custom_archetype_preview_stats_var.value == "old stats"
    assert controller._custom_archetype_preview_last_snapshot == old_snapshot
    assert controller._custom_archetype_preview_last_lab is old_lab
    assert controller._custom_archetype_preview_image_items == {"noise": 7}
    assert canvas.created == []


def test_archetype_preview_failed_commit_does_not_advance_bookkeeping():
    controller = CustomGeneratorController.__new__(CustomGeneratorController)
    old_snapshot = ("old-noise", "old-macro", 256, 41)
    old_result = object()
    old_lab = object()
    controller._custom_archetype_preview_last_snapshot = old_snapshot
    controller._custom_archetype_preview_last_result = old_result
    controller._custom_archetype_preview_last_lab = old_lab
    controller._custom_render_archetype_preview_rasters = lambda *_args, **_kwargs: False
    preview = SimpleNamespace(
        noise="new-noise",
        macro="new-macro",
        side=512,
        seed=99,
        noise_lab=object(),
    )

    controller._custom_apply_archetype_preview(preview)

    assert controller._custom_archetype_preview_last_snapshot == old_snapshot
    assert controller._custom_archetype_preview_last_result is old_result
    assert controller._custom_archetype_preview_last_lab is old_lab


@pytest.mark.parametrize("island_mask", [None, "actual-island-mask"])
def test_archetype_preview_exact_commit_replaces_fast_noise_with_exact_triptych(island_mask):
    controller = CustomGeneratorController.__new__(CustomGeneratorController)
    controller._custom_archetype_component_canvases = {}
    controller._custom_archetype_preview_last_snapshot = (
        "fast-noise",
        "fast-macro",
        192,
        41,
    )
    controller._custom_archetype_preview_last_result = None
    controller._custom_archetype_preview_last_lab = None
    controller._custom_archetype_preview_status_var = _FakeVar("calcul")
    controller._custom_archetype_preview_stats_var = _FakeVar("")
    controller._custom_archetype_preview_progress_bar = _FakeProgressBar()
    controller.prefs = {"language": "fr"}
    controller._custom_archetype_preview_summary = lambda _preview: "exact stats"
    render_calls = []

    def record_render(*args, **kwargs):
        render_calls.append((args, kwargs))
        return True

    controller._custom_render_archetype_preview_rasters = record_render
    exact_lab = object()
    preview = SimpleNamespace(
        noise="exact-noise",
        macro="exact-macro",
        side=512,
        seed=99,
        noise_lab=exact_lab,
        island_mask=island_mask,
    )

    controller._custom_apply_archetype_preview(preview)

    assert len(render_calls) == 1
    assert render_calls[0][0][:4] == (
        "exact-noise",
        "exact-macro",
        512,
        99,
    )
    assert "island_mask" not in render_calls[0][1]
    assert render_calls[0][1]["noise_lab"] is exact_lab
    assert render_calls[0][1]["include_neutral_contribution"] is False
    assert controller._custom_archetype_preview_last_snapshot == (
        "exact-noise",
        "exact-macro",
        512,
        99,
    )
    assert controller._custom_archetype_preview_last_lab is exact_lab


def test_archetype_preview_exact_commit_reuses_exact_noise_for_primary_thumbnail():
    controller = CustomGeneratorController.__new__(CustomGeneratorController)
    controller._custom_archetype_preview_last_snapshot = None
    controller._custom_archetype_preview_last_result = None
    controller._custom_archetype_preview_last_lab = None
    controller._custom_archetype_preview_status_var = _FakeVar("calcul")
    controller._custom_archetype_preview_stats_var = _FakeVar("")
    controller._custom_archetype_preview_progress_bar = _FakeProgressBar()
    controller.prefs = {"language": "fr"}
    controller._custom_archetype_preview_summary = lambda _preview: "exact stats"
    controller._custom_render_archetype_preview_rasters = lambda *_args, **_kwargs: True
    component_calls = []

    def record_components(principal, layers, **kwargs):
        component_calls.append((principal, layers, kwargs))

    controller._custom_render_archetype_component_previews = record_components
    exact_noise = object()
    preview = SimpleNamespace(
        noise=exact_noise,
        macro="exact-macro",
        side=768,
        seed=99,
        noise_lab=None,
    )

    controller._custom_apply_archetype_preview(
        preview,
        component_source="legacy-source",
        component_layers=("layer",),
    )

    assert component_calls == [
        (
            "legacy-source",
            ("layer",),
            {"primary_noise": exact_noise, "mask_layers": ()},
        )
    ]


def test_archetype_preview_exact_commit_uses_source_noise_for_primary_thumbnail():
    controller = CustomGeneratorController.__new__(CustomGeneratorController)
    controller._custom_archetype_preview_last_snapshot = None
    controller._custom_archetype_preview_last_result = None
    controller._custom_archetype_preview_last_lab = None
    controller._custom_archetype_preview_status_var = _FakeVar("calcul")
    controller._custom_archetype_preview_stats_var = _FakeVar("")
    controller._custom_archetype_preview_progress_bar = _FakeProgressBar()
    controller.prefs = {"language": "fr"}
    controller._custom_archetype_preview_summary = lambda _preview: "exact stats"
    controller._custom_render_archetype_preview_rasters = lambda *_args, **_kwargs: True
    component_calls = []

    def record_components(principal, layers, **kwargs):
        component_calls.append((principal, layers, kwargs))

    controller._custom_render_archetype_component_previews = record_components
    preview = SimpleNamespace(
        noise="composed-noise",
        source_noise="source-only-noise",
        macro="exact-macro",
        side=768,
        seed=99,
        noise_lab=object(),
    )

    controller._custom_apply_archetype_preview(
        preview,
        component_source="raw-source",
        component_layers=("layer",),
    )

    assert component_calls == [
        (
            "raw-source",
            ("layer",),
            {"primary_noise": "source-only-noise", "mask_layers": ()},
        )
    ]


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


def test_archetype_edit_keeps_generator_mode_and_gets_its_own_runtime_config():
    controller = _ProbeController()
    controller.mode.set("Upgraded")
    controller._custom_current_archetype = lambda: "continental"
    controller._custom_refresh_archetype_header = lambda: None
    controller._custom_refresh_archetype_ranges = lambda: None
    controller._custom_schedule_archetype_preview_refresh = lambda **_kwargs: None
    base = build_custom_config("upgraded")
    edited = base.with_archetype_value(("morphology", "frame_margin_percent"), 9)

    controller._custom_activate_archetype(edited)

    assert controller.mode.get() == "Upgraded"
    assert controller.mode.set_calls == 1
    assert controller._custom_config_for_generation("upgraded", "continental") is edited
    assert controller._custom_config_for_generation("legacy", "continental") is None


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


def test_archetype_shape_display_formatter_is_defined_before_use():
    formatter_definition = CUSTOM_CONTROLLER_SOURCE.index(
        "        def display_setting(value):"
    )
    shape_formatter_use = CUSTOM_CONTROLLER_SOURCE.index(
        "display_setting(base_settings[setting_key])", formatter_definition
    )

    assert formatter_definition < shape_formatter_use


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

            def literal_states(expression):
                if isinstance(expression, ast.Constant):
                    return {expression.value}
                if isinstance(expression, ast.IfExp):
                    return literal_states(expression.body) | literal_states(expression.orelse)
                return set()

            states = literal_states(state)
            assert states and states <= {"readonly", "disabled"}, (
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
        "archetype_preview_mass",
        "archetype_preview_noise_ready",
        "archetype_preview_macro_relaxation",
        "archetype_preview_macro_relaxation_hint",
    ):
        assert set(_CUSTOM_SECTION_TEXT[key]) == languages


def test_archetype_contract_labels_cover_every_language():
    languages = {"fr", "en", "de", "es"}
    for key in (
        "archetype_coast_custom",
        "archetype_mass_model",
        "archetype_micro_islands",
        "archetype_relief_source",
        "archetype_relief_source_hint",
        "archetype_relief_source_native",
        "archetype_relief_source_custom_legacy",
        "archetype_relief_source_fractal",
        "archetype_relief_source_warped",
        "archetype_relief_source_ridged",
        "archetype_morphology_group",
        "archetype_legacy_blocks_group",
        "archetype_shape_scale",
        "archetype_relief_contrast",
        "archetype_native_coarse_variation",
        "archetype_native_coarse_variation_hint",
        "archetype_native_refinement",
        "archetype_native_refinement_hint",
        "archetype_native_large_scale_refinement",
        "archetype_native_large_scale_refinement_hint",
        "archetype_native_fine_scale_refinement",
        "archetype_native_fine_scale_refinement_hint",
        "archetype_native_sculpture_attempts",
        "archetype_native_sculpture_attempts_hint",
        "archetype_native_relaxation_strength",
        "archetype_native_relaxation_strength_hint",
        "archetype_shape_scale_hint",
        "archetype_relief_contrast_hint",
        "archetype_frame_margin",
        "archetype_frame_margin_hint",
        "archetype_edge_falloff",
        "archetype_edge_falloff_hint",
        "archetype_noise_layers_group",
        "archetype_noise_layer_count",
        "archetype_noise_adaptive_frequency",
        "archetype_noise_adaptive_frequency_hint",
        "archetype_noise_layer",
        "archetype_noise_family",
        "archetype_noise_scale",
        "archetype_noise_strength",
        "archetype_noise_operation",
        "archetype_noise_add",
        "archetype_noise_subtract",
        "archetype_noise_smooth",
        "archetype_noise_ridged",
        "archetype_noise_layers_hint",
        "archetype_noise_lab_none",
        "archetype_noise_lab_total",
        "archetype_noise_lab_layer",
        "archetype_noise_lab_source_metrics",
        "archetype_noise_contribution",
        "archetype_noise_contribution_short",
        "archetype_noise_role_land_relief",
        "archetype_noise_mask_source_land",
        "archetype_noise_stage_pre_normalize",
        "archetype_noise_lab_source",
    ):
        assert set(_CUSTOM_SECTION_TEXT[key]) == languages
    assert "archetype_contract_values" not in CUSTOM_CONTROLLER_SOURCE
    assert "text=custom_section_text(\"archetype_mass_model\"" not in CUSTOM_CONTROLLER_SOURCE
    assert "noise_delta_rgb(noise_lab.layer_delta)" in CUSTOM_CONTROLLER_SOURCE
    assert "raw_height_rgb(noise_lab.composed_height)" not in CUSTOM_CONTROLLER_SOURCE
    assert "noise_delta_rgb(noise_lab.total_delta)" not in CUSTOM_CONTROLLER_SOURCE
    assert "generate_noise_component_previews" in CUSTOM_CONTROLLER_SOURCE
    assert 'row=4, column=0' in CUSTOM_CONTROLLER_SOURCE
    assert 'row=9,\n            column=0,\n            columnspan=2' in CUSTOM_CONTROLLER_SOURCE
    assert 'column=1,\n            sticky="nw",\n            padx=(14, 0)' in CUSTOM_CONTROLLER_SOURCE
    assert 'morphology_controls.grid(row=0, column=0, sticky="nw")' in CUSTOM_CONTROLLER_SOURCE
    assert 'noise_title = ttk.Frame(noise_box)' in CUSTOM_CONTROLLER_SOURCE
    assert 'noise_box.configure(labelwidget=noise_title)' in CUSTOM_CONTROLLER_SOURCE
    assert 'add_compact_info(noise_title, 0, 1, noise_hint' in CUSTOM_CONTROLLER_SOURCE
    assert 'add_info(noise_title, 0, noise_hint' not in CUSTOM_CONTROLLER_SOURCE
    assert 'add_compact_info(\n            noise_box,' not in CUSTOM_CONTROLLER_SOURCE
    assert '_ARCHETYPE_COMPONENT_PREVIEW_SIZE = 128' in CUSTOM_CONTROLLER_SOURCE
    assert 'def _custom_reset_archetype_section(self, key: str)' in CUSTOM_CONTROLLER_SOURCE
    assert 'self._custom_archetype_morphology_reset_button' in CUSTOM_CONTROLLER_SOURCE
    assert 'self._custom_archetype_noise_reset_button' in CUSTOM_CONTROLLER_SOURCE
    assert 'fusion_header = ttk.Frame(card)' in CUSTOM_CONTROLLER_SOURCE
    assert 'fusion_settings = ttk.Frame(card)' in CUSTOM_CONTROLLER_SOURCE
    assert 'noise_setting_groups = (' in CUSTOM_CONTROLLER_SOURCE
    assert 'toggle_noise_group(source_key, group_key)' in CUSTOM_CONTROLLER_SOURCE
    assert 'group_shell = ttk.Frame(parent)' in CUSTOM_CONTROLLER_SOURCE
    assert 'content = ttk.LabelFrame(group_shell, padding=(4, 2))' in CUSTOM_CONTROLLER_SOURCE
    assert 'f"layer:{index}"' in CUSTOM_CONTROLLER_SOURCE
    assert 'add_source_settings(\n            base_settings_frame,' in CUSTOM_CONTROLLER_SOURCE
    assert 'row=action_row,' in CUSTOM_CONTROLLER_SOURCE
    assert 'rowspan=action_row + 1' in CUSTOM_CONTROLLER_SOURCE
    assert 'state="normal" if editable else "disabled"' in CUSTOM_CONTROLLER_SOURCE
    assert 'width=_ARCHETYPE_COMPONENT_PREVIEW_SIZE' in CUSTOM_CONTROLLER_SOURCE
    assert 'height=_ARCHETYPE_COMPONENT_PREVIEW_SIZE' in CUSTOM_CONTROLLER_SOURCE
    assert 'padding=(4, 0)' in CUSTOM_CONTROLLER_SOURCE
    assert 'def _custom_archetype_component_preview_dimensions' not in CUSTOM_CONTROLLER_SOURCE
    assert 'def _custom_resize_archetype_component_canvases' not in CUSTOM_CONTROLLER_SOURCE
    assert 'self._custom_archetype_component_last_data' not in CUSTOM_CONTROLLER_SOURCE


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


@pytest.mark.parametrize("language", ["fr", "en", "de", "es"])
def test_source_selector_offers_the_same_complete_and_simple_sources_for_all_presets(language):
    controller = CustomGeneratorController.__new__(CustomGeneratorController)
    controller._custom_current_archetype = lambda: "large_islands"
    options = controller._custom_archetype_relief_source_options(language)
    assert {"large_islands", "native_legacy", "legacy_blocks", "perlin", "fbm"} <= options.keys()
    controller._custom_current_archetype = lambda: "continental"
    assert options == controller._custom_archetype_relief_source_options(language)
    assert options["large_islands"].split(" · ")[0] != options["perlin"].split(" · ")[0]


def test_island_editor_has_the_same_parameter_catalogue_as_continental():
    islands = _archetype_ui_parameter_descriptors(default_archetype_profile("large_islands"))
    continental = _archetype_ui_parameter_descriptors(default_archetype_profile("continental"))
    identity = lambda row: (row.path, row.value_type, row.group, row.label_key)
    assert tuple(map(identity, islands)) == tuple(map(identity, continental))
    # Defaults and dynamic threshold bounds may differ between named profiles.
    matching = default_archetype_profile("large_islands")
    matching["relief"] = dict(default_archetype_profile("continental")["relief"])
    assert _archetype_ui_parameter_descriptors(matching) == continental


def test_island_preview_worker_uses_actual_domain_players_and_generic_components(monkeypatch):
    import s3mapgen.application.custom.controller as module
    controller = CustomGeneratorController.__new__(CustomGeneratorController)
    controller._custom_archetype_preview_lock = threading.Lock()
    controller._custom_archetype_preview_request_id = 7
    profile = default_archetype_profile("large_islands")
    controller._custom_archetype_preview_request = (7, profile, 384, 42, 0, True, True, 8)
    controller._custom_archetype_preview_noise_cache = {}
    exact = object()
    calls = []

    def generate(*args, **kwargs):
        calls.append((args, kwargs))
        return exact

    monkeypatch.setattr(module, "generate_noise_component_previews", lambda *args, **kwargs: ("source", ("fusion",)))
    monkeypatch.setattr(module, "generate_mask_component_previews", lambda *args, **kwargs: ("mask",))
    monkeypatch.setattr(module, "generate_archetype_preview", generate)
    controller._custom_archetype_preview_worker_loop()
    assert len(calls) == 1
    assert calls[0][0] == (profile, 384, 42, 0)
    assert calls[0][1]["players"] == 8
    assert calls[0][1]["relax_macro"] is True
    assert controller._custom_archetype_preview_completed == (7, exact, None, "source", ("fusion",), ("mask",))


def test_island_source_thumbnail_commits_without_a_generic_component_preview():
    controller = CustomGeneratorController.__new__(CustomGeneratorController)
    controller._custom_archetype_preview_status_var = _FakeVar("")
    controller._custom_archetype_preview_stats_var = _FakeVar("")
    controller.prefs = {"language": "fr"}
    controller._custom_archetype_preview_summary = lambda preview: "island stats"
    controller._custom_render_archetype_preview_rasters = lambda *args, **kwargs: True
    calls = []
    controller._custom_render_archetype_component_previews = lambda *args, **kwargs: calls.append((args, kwargs))
    height = object()
    preview = SimpleNamespace(noise=height, source_noise=height, island_mask=object(),
                              macro=object(), side=384, seed=42, noise_lab=None)
    controller._custom_apply_archetype_preview(preview)
    assert calls == [((height, ()), {"primary_noise": height, "mask_layers": ()})]
    assert controller._custom_archetype_preview_last_result is preview


@pytest.mark.parametrize("archetype", ["continental", "large_islands"])
@pytest.mark.parametrize("language", ["fr", "en", "de", "es"])
def test_archetype_tab_build_uses_the_same_customizable_editor_for_both_presets(
    monkeypatch, archetype, language,
):
    import s3mapgen.application.custom.controller as module

    class Variable(_FakeVar):
        def __init__(self, value=""):
            super().__init__(value)

        def trace_add(self, *args):
            return "trace"

    class Widget:
        def __init__(self, parent=None, **options):
            self.parent, self.options = parent, options
            self.children = []
            self.removed = parent is not None
            if parent is not None:
                parent.children.append(self)

        def configure(self, **options):
            self.options.update(options)

        def grid(self, **options):
            self.removed = False

        grid_configure = grid

        def grid_remove(self):
            self.removed = True

        def visible(self):
            return not self.removed and (self.parent is None or self.parent.visible())

        def winfo_children(self):
            return self.children

        def bind(self, *args, **kwargs):
            pass

        def columnconfigure(self, *args, **kwargs):
            pass

    for name in ("Frame", "LabelFrame", "Label", "Button", "Combobox", "Spinbox",
                 "Checkbutton", "Progressbar", "Separator"):
        monkeypatch.setattr(module.ttk, name, Widget)
    monkeypatch.setattr(module.tk, "Canvas", Widget)
    monkeypatch.setattr(module.tk, "StringVar", Variable)
    monkeypatch.setattr(module.tk, "BooleanVar", Variable)
    controller = CustomGeneratorController.__new__(CustomGeneratorController)
    controller.prefs = {"language": language}
    controller._custom_current_archetype = lambda: archetype
    controller._custom_profile_for_display = lambda: build_custom_config("upgraded", archetype)
    controller._custom_archetype_profile_selection_key = lambda profile: "native"
    controller._custom_info_icons = {1: object(), 2: object()}
    controller._custom_archetype_legacy_blocks_expanded = False
    controller._custom_archetype_noise_group_expanded = {}
    controller._custom_archetype_preview_trace_ids = []
    controller._custom_archetype_preview_projection_key = "square"
    controller._custom_archetype_preview_size_key = "compact"
    controller._custom_archetype_preview_dimensions = lambda: (280, 280)
    controller._custom_archetype_tab = Widget()
    for name in ("profile", "noise_layer_count", "mask_layer_count", "preview_projection",
                 "preview_size", "preview_status", "preview_stats", "preview_relaxation"):
        setattr(controller, f"_custom_archetype_{name}_var", Variable())
    for name in ("size", "seed", "mirror", "players"):
        setattr(controller, name, Variable("4"))
    for name in ("_custom_clear_archetype_preview_traces", "_custom_refresh_archetype_header",
                 "_custom_refresh_archetype_mask_layer_action_states",
                 "_custom_refresh_archetype_noise_layer_action_states",
                 "_custom_refresh_archetype_noise_setting_states",
                 "_custom_refresh_archetype_section_reset_buttons",
                 "_custom_schedule_archetype_preview_refresh"):
        setattr(controller, name, lambda *args, **kwargs: None)

    # Add visible slots so the test exercises the actual common UI tree.
    config = build_custom_config("upgraded", archetype)
    profile = config.archetype_profile
    profile["morphology"]["noise_layer_count"] = 1
    profile["morphology"]["mask_layer_count"] = 1
    controller._custom_config = config.with_archetype_profile(profile)
    controller._custom_profile_for_display = lambda: controller._custom_config
    controller._render_custom_archetype_tab()
    source = controller._custom_archetype_component_canvases["source"]
    assert source.visible()
    assert controller._custom_archetype_noise_layer_cards[0].visible()
    assert controller._custom_archetype_mask_layer_cards[0].visible()
    assert "morphology.shape_scale_percent" in controller._custom_archetype_vars
    assert "relief.water_threshold" in controller._custom_archetype_vars
    assert controller._custom_archetype_relief_mask_vars["type"].get()
    assert "large_islands" in controller._custom_archetype_profile_options(language)

    del controller._custom_archetype_profile_selection_key
    del controller._custom_refresh_archetype_header
    del controller._custom_refresh_archetype_noise_setting_states
    controller._custom_current_mode = lambda: "custom"
    controller._custom_ensure_config = lambda *args: controller._custom_config
    controller.arch = Variable(archetype)
    controller._custom_status_var = Variable()
    controller._selection_changed = lambda: pytest.fail("Whole-tab reload during profile change")
    initial_widgets = tuple(controller._custom_archetype_tab.winfo_children())
    vars_before = dict(controller._custom_archetype_vars)
    for preset_key in ("native", "large_islands", CONTINENTAL_CUSTOM_PROFILE_KEY):
        controller._custom_apply_archetype_preset(preset_key)
        expected = controller._custom_archetype_profile_presets()[preset_key]
        assert tuple(controller._custom_archetype_tab.winfo_children()) == initial_widgets
        assert controller._custom_archetype_vars == vars_before
        assert controller._custom_archetype_vars["relief.mountain_threshold"].get() == str(expected["relief"]["mountain_threshold"])
        assert controller._custom_archetype_noise_layer_count_var.get() == "0"
        assert not controller._custom_archetype_noise_layer_cards[0].visible()
        assert not controller._custom_archetype_mask_layer_cards[0].visible()
        assert "edited" not in controller._custom_archetype_profile_options(language)
        assert "edited" not in controller._custom_archetype_profile_combo.options["values"]
    controller._custom_selection_changed = lambda: None


@pytest.mark.parametrize("language", ["fr", "en", "de", "es"])
def test_base_profile_custom_entry_appears_only_after_edit_and_disappears_on_preset(language):
    controller = CustomGeneratorController.__new__(CustomGeneratorController)
    controller._custom_config = build_custom_config("upgraded", "large_islands")
    assert "edited" not in controller._custom_archetype_profile_options(language)
    profile = controller._custom_config.archetype_profile
    profile["relief"]["mountain_threshold"] += 1
    controller._custom_config = controller._custom_config.with_archetype_profile(profile)
    assert "edited" in controller._custom_archetype_profile_options(language)
    controller._custom_config = controller._custom_config.with_archetype_profile(continental_legacy_blocks_profile(), base_archetype="continental")
    assert "edited" not in controller._custom_archetype_profile_options(language)


def test_spinbox_wheel_uses_bounds_updated_by_the_current_profile():
    widget = _FakeSpinbox()
    widget.configure(from_=0, to=200)
    widget.cget = lambda key: widget.options[{"from": "from_", "to": "to"}[key]]
    value = _FakeVar("120")
    _configure_integer_spinbox_steps(widget, value, 0, 200, lambda: None)
    widget.configure(from_=0, to=122)
    widget.bindings["<MouseWheel>"](SimpleNamespace(delta=120))
    assert value.get() == "122"
    widget.configure(from_=121, to=130)
    widget.bindings["<MouseWheel>"](SimpleNamespace(delta=-120))
    assert value.get() == "121"


def test_river_algorithm_changes_only_generator_without_rebuilding_tabs():
    controller = _ProbeController()
    controller._custom_last_concrete_mode = "upgraded"
    controller._custom_config = build_custom_config("upgraded", "large_islands")
    controller._custom_current_archetype = lambda: "large_islands"
    controller._custom_refresh_section_headers = lambda: None
    initial_profile = controller._custom_config.archetype_profile
    controller._custom_section_changed(("rivers", "algorithm"), "improved")
    assert controller._custom_config.semantic_sections()["rivers"]["algorithm"] == "improved"
    assert controller._custom_config.archetype_profile == initial_profile
    assert controller.selection_calls == controller.render_calls == 0
    controller._custom_section_changed(("rivers", "algorithm"), "native")
    assert controller._custom_config.semantic_sections()["rivers"]["algorithm"] == "native"
    assert controller.selection_calls == controller.render_calls == 0


def test_leaving_large_islands_restores_classic_default_without_rebuilding():
    controller = CustomGeneratorController.__new__(CustomGeneratorController)
    controller._custom_config = build_custom_config("upgraded", "large_islands")
    controller._custom_current_archetype = lambda: "large_islands"
    controller._custom_current_mode = lambda: "upgraded"
    controller._custom_language = lambda: "fr"
    controller._custom_ensure_config = lambda *args: controller._custom_config
    controller.arch = _FakeVar("Grandes îles")
    controller._custom_river_algorithm_var = _FakeVar("Amélioré")
    controller._custom_sync_archetype_editor_values = lambda: None
    controller._custom_activate_archetype = lambda c: setattr(controller, "_custom_config", c)
    controller._custom_status_var = _FakeVar("")
    controller._selection_changed = lambda: pytest.fail("Profile switch rebuilt tabs")
    entered = []
    controller._custom_enter_custom_mode_without_render = lambda c: entered.append(c)
    controller._custom_apply_archetype_preset("native")
    assert entered == []
    assert controller._custom_config.semantic_sections()["rivers"]["algorithm"] == "native"
    controller._custom_current_mode = lambda: "custom"
    controller._custom_current_archetype = lambda: "continental"
    assert controller._custom_config_for_generation() is controller._custom_config
    assert controller._custom_river_algorithm_var.get() == "Classique"
    # Returning to Large islands restores its default even after Classic was
    # chosen manually; the rate and unrelated settings are retained.
    sections = controller._custom_config.semantic_sections()
    sections["rivers"].update(algorithm="native", rate_percent=50)
    controller._custom_config = controller._custom_config.with_sections(sections)
    controller._custom_apply_archetype_preset("large_islands")
    assert controller._custom_config.semantic_sections()["rivers"] == {"algorithm": "improved", "rate_percent": 50.0}
    assert controller._custom_river_algorithm_var.get() == "Amélioré"



def test_large_islands_river_reset_uses_its_improved_default():
    controller = CustomGeneratorController.__new__(CustomGeneratorController)
    controller._custom_config = build_custom_config("upgraded", "large_islands")
    assert not controller._custom_section_is_modified("rivers")
    sections = controller._custom_config.semantic_sections()
    sections["rivers"]["algorithm"] = "native"
    controller._custom_config = controller._custom_config.with_sections(sections)
    assert controller._custom_section_is_modified("rivers")
    controller._custom_current_mode = lambda: "custom"
    controller._custom_language = lambda: "fr"
    controller._selection_changed = lambda: None
    controller._custom_reset_section("rivers")
    assert controller._custom_config.semantic_sections()["rivers"]["algorithm"] == "improved"
    assert not controller._custom_section_is_modified("rivers")
