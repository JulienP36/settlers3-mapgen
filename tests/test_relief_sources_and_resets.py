"""Archived source parity and isolated editor actions."""

from copy import deepcopy
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest

from s3mapgen.application.custom.controller import CustomGeneratorController, _configure_integer_spinbox_steps
from s3mapgen.application.ui.widgets.selectors import ColorMenuSelect
from s3mapgen.generation.archetypes import (
    default_archetype_profile, generate_archetype_preview,
    generate_noise_component_previews, normalize_archetype_profile,
    NOISE_LAYER_DEFAULTS, MASK_LAYER_DEFAULTS,
    RELIEF_SOURCE_LARGE_ISLANDS_R21,
)
from s3mapgen.generation.custom import build_custom_config


WITNESSES = json.loads(Path("tests/fixtures/islands_r21_source.json").read_text())


@pytest.mark.parametrize("case", WITNESSES, ids=lambda c: f"{c['side']}-{c['players']}")
def test_archived_island_source_retains_exact_original_height_and_mask(case):
    profile = default_archetype_profile("large_islands")
    profile["morphology"]["relief_source"] = RELIEF_SOURCE_LARGE_ISLANDS_R21
    preview = generate_archetype_preview(profile, case["side"], case["seed"], players=case["players"])
    assert hashlib.sha256(preview.noise.tobytes()).hexdigest() == case["height_sha256"]
    assert hashlib.sha256(preview.island_mask.tobytes()).hexdigest() == case["labels_sha256"]


def test_archived_island_source_is_selectable_and_composable_from_continental():
    profile = default_archetype_profile("continental")
    morphology = profile["morphology"]
    morphology["relief_source"] = RELIEF_SOURCE_LARGE_ISLANDS_R21
    assert normalize_archetype_profile(profile)["morphology"]["relief_source"] == RELIEF_SOURCE_LARGE_ISLANDS_R21
    original = generate_archetype_preview(profile, 384, 42, players=4)
    morphology["noise_layer_count"] = 1
    morphology["noise_layers"][0].update(enabled=True, strength_percent=20)
    morphology["mask_layer_count"] = 1
    morphology["mask_layers"][0].update(enabled=True, strength_percent=15)
    composed = generate_archetype_preview(profile, 384, 42, players=4)
    assert np.array_equal(original.source_noise, composed.source_noise)
    assert not np.array_equal(original.noise, composed.noise)
    source, layers = generate_noise_component_previews(profile, 64, 42, domain_side=384, players=4)
    assert source.shape == (64, 64) and len(layers) == 1 and np.ptp(source) > 100


@pytest.mark.parametrize("state", ["disabled", "readonly"])
@pytest.mark.parametrize("event_name,event", [
    ("<MouseWheel>", SimpleNamespace(delta=240)),
    ("<Button-4>", SimpleNamespace(num=4)),
    ("<Button-5>", SimpleNamespace(num=5)),
])
def test_disabled_numeric_controls_ignore_every_wheel_event(state, event_name, event):
    from tests.test_custom_controller import _FakeSpinbox, _FakeVar
    widget, variable = _FakeSpinbox(), _FakeVar("100")
    calls = []
    _configure_integer_spinbox_steps(widget, variable, 0, 200, lambda: calls.append(True))
    widget.configure(state=state)
    assert widget.bindings[event_name](event) == "break"
    assert variable.get() == "100" and not calls and variable.set_calls == 0
    widget.configure(state="normal")
    widget.bindings[event_name](event)
    assert variable.get() != "100" and calls == [True]


def test_selector_respects_actual_disabled_state_even_when_enabled_flag_is_stale():
    selector = SimpleNamespace(_enabled=True, _items=[("a", "A", None, None)], instate=lambda states: True)
    assert ColorMenuSelect._wheel_step(selector, 1) == "break"
    assert ColorMenuSelect._choose(selector, "a", "A") is None


@pytest.mark.parametrize("kind,defaults", [("noise", NOISE_LAYER_DEFAULTS), ("mask", MASK_LAYER_DEFAULTS)])
def test_component_reset_preserves_other_slots_and_generator_settings(kind, defaults):
    controller = CustomGeneratorController.__new__(CustomGeneratorController)
    profile = default_archetype_profile("large_islands")
    morphology = profile["morphology"]
    morphology[f"{kind}_layer_count"] = 3
    for layer in morphology[f"{kind}_layers"][:3]:
        layer.update(enabled=True, strength_percent=85)
    config = build_custom_config("upgraded", "large_islands").with_archetype_profile(profile)
    controller._custom_config = config
    controller._custom_archetype_editor_editable = True
    controller._custom_archetype_noise_layer_solo = 1
    controller._custom_activate_archetype = lambda updated: setattr(controller, "_custom_config", updated)
    controller._custom_sync_archetype_editor_values = lambda: None
    before = deepcopy(config.archetype_profile)
    controller._custom_reset_archetype_component(kind, 1)
    after = controller._custom_config.archetype_profile
    expected = deepcopy(before)
    expected["morphology"][f"{kind}_layers"][1] = deepcopy(defaults[1])
    assert after == expected
    assert controller._custom_config.semantic_sections() == config.semantic_sections()
    assert controller._custom_archetype_noise_layer_solo == (None if kind == "noise" else 1)
    controller._custom_archetype_editor_editable = False
    controller._custom_reset_archetype_component(kind, 0)
    assert controller._custom_config.archetype_profile == after


def test_primary_reset_keeps_fusions_masks_and_manual_thresholds():
    controller = CustomGeneratorController.__new__(CustomGeneratorController)
    profile = default_archetype_profile("large_islands")
    morphology = profile["morphology"]
    morphology["relief_source"] = RELIEF_SOURCE_LARGE_ISLANDS_R21
    morphology["relief_source_settings"]["frequency"] = 7
    morphology["relief_source_mask"]["type"] = "noise"
    morphology["noise_layer_count"] = 2
    morphology["noise_layers"][0]["enabled"] = True
    morphology["mask_layer_count"] = 1
    profile["relief"]["snow_threshold"] = 205
    controller._custom_config = build_custom_config("upgraded", "large_islands").with_archetype_profile(profile)
    controller._custom_activate_archetype = lambda updated: setattr(controller, "_custom_config", updated)
    controller._custom_sync_archetype_editor_values = lambda: None
    before = deepcopy(controller._custom_config.archetype_profile)
    controller._custom_reset_archetype_section("primary_source")
    expected = deepcopy(before)
    baseline = default_archetype_profile("large_islands")
    for key in ("relief_source", "relief_source_settings", "relief_source_mask"):
        expected["morphology"][key] = baseline["morphology"][key]
    assert controller._custom_config.archetype_profile == expected
