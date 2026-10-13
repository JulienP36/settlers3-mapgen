"""Exercise the real editor and Tcl variable traces without a display server."""
from types import SimpleNamespace
import tkinter as tk

import pytest

import s3mapgen.application.custom.controller as module
from s3mapgen.application.custom.controller import CustomGeneratorController
from s3mapgen.application.ui.i18n.shell import MODE_LABELS, ARCHETYPE_LABELS
from s3mapgen.generation.custom import build_custom_config, get_path, rocky_equal_core_cells, rocky_proportional_targets, rocky_equivalent_radius


class Widget:
    """Geometry/lifecycle probe; variables and their trace execution are real Tcl."""
    def __init__(self, parent=None, **options):
        self.parent, self.options = parent, options
        self.master = parent
        self.children, self.bindings, self.jobs = [], {}, {}
        self.binding_count = self.job_count = 0
        self.alive = True
        self.width = 1000
        self.placements = 0
        self.removed = False
        if parent is not None:
            parent.children.append(self)

    def cget(self, key):
        return self.options.get(key, "")

    def configure(self, **options):
        assert self.alive
        self.options.update(options)

    def grid(self, **options):
        assert self.alive
        self.placements += 1
        self.removed = False

    grid_configure = grid
    pack = grid

    def grid_remove(self):
        self.removed = True

    def lift(self, above=None):
        assert self.alive
        self.raised_above = above

    def columnconfigure(self, *args, **kwargs):
        pass

    def grid_propagate(self, *args):
        pass

    def instate(self, states):
        return self.options.get("state", "normal") in states

    def bind(self, sequence, callback, add=None):
        self.binding_count += 1
        key = str(self.binding_count)
        self.bindings[key] = (sequence, callback)
        return key

    def unbind(self, sequence, key):
        assert self.bindings[key][0] == sequence
        del self.bindings[key]

    def after_idle(self, callback):
        self.job_count += 1
        key = str(self.job_count)
        self.jobs[key] = callback
        return key

    def after_cancel(self, key):
        self.jobs.pop(key, None)

    def flush(self):
        jobs, self.jobs = self.jobs, {}
        for callback in jobs.values():
            callback()

    def resize(self, width):
        self.width = width
        for sequence, callback in list(self.bindings.values()):
            if sequence == "<Configure>":
                callback(SimpleNamespace(width=width))
        self.flush()

    def winfo_children(self):
        return list(self.children)

    def winfo_exists(self):
        return self.alive

    def winfo_width(self):
        return self.width

    def winfo_reqwidth(self):
        return 160

    def destroy(self):
        for child in list(self.children):
            child.destroy()
        self.alive = False
        if self.parent is not None:
            self.parent.children.remove(self)


@pytest.fixture(params=["fr", "en", "de", "es"])
def editor(monkeypatch, request):
    interp = tk.Tcl()
    monkeypatch.setattr(Widget, "tk", interp, raising=False)
    for name in ("Frame", "LabelFrame", "Label", "Button", "Combobox", "Spinbox", "Checkbutton", "Separator"):
        monkeypatch.setattr(module.ttk, name, type(name, (Widget,), {}))
    string_var, bool_var = tk.StringVar, tk.BooleanVar
    monkeypatch.setattr(module.tk, "StringVar", lambda **kw: string_var(master=interp, **kw))
    monkeypatch.setattr(module.tk, "BooleanVar", lambda **kw: bool_var(master=interp, **kw))
    monkeypatch.setattr(module, "mineral_icon", lambda *args, **kw: object())
    monkeypatch.setattr(module, "info_icons", lambda *args: {1: object(), 2: object()})
    c = CustomGeneratorController.__new__(CustomGeneratorController)
    language = request.param
    c.prefs = {"language": language}
    c.mode = string_var(master=interp, value=MODE_LABELS[language]["legacy"])
    c.arch = string_var(master=interp, value=ARCHETYPE_LABELS[language]["large_islands"])
    c.size = string_var(master=interp, value="512")
    c._mode_key = lambda: next(k for k,v in MODE_LABELS[c.prefs["language"]].items() if v == c.mode.get())
    c._arch_key = lambda: next(k for k,v in ARCHETYPE_LABELS[c.prefs["language"]].items() if v == c.arch.get())
    c._custom_config = build_custom_config("legacy", "large_islands")
    c._custom_last_concrete_mode = c._custom_last_ui_mode = "legacy"
    c._custom_last_concrete_archetype = c._custom_last_ui_archetype = "large_islands"
    c._custom_section_expanded = {key: True for key in c._custom_config.semantic_sections()}
    c._custom_status_var = string_var(master=interp)
    c._custom_provenance_var = string_var(master=interp)
    c._custom_generator_tab = Widget()
    c.preview_calls, c.archetype_renders = [], []
    c._render_custom_archetype_tab = lambda: c.archetype_renders.append(object())
    c._custom_schedule_archetype_preview_refresh = lambda **kw: c.preview_calls.append(kw)
    c._custom_sync_archetype_editor_values = lambda: None
    c._custom_refresh_archetype_ranges = lambda: None
    c._custom_refresh_archetype_section_reset_buttons = lambda: None
    c._selection_changed = c._custom_selection_changed
    c._render_custom_parameter_tabs()
    c._custom_generator_tab.flush()
    return c


def assert_display(c):
    sections = c._custom_config.semantic_sections()
    rocky = sections["start_bonus"]["rocky_minerals"]
    active = [key for key in ("coal", "iron", "gold", "gems", "sulfur") if rocky[key]["enabled"]]
    if rocky["surface_mode"] == "equal":
        cores = {key: rocky_equal_core_cells(rocky["radius_min"]) for key in active}
    elif rocky["surface_mode"] == "proportional":
        cores = rocky_proportional_targets(rocky["total_core_cells"], active, sections["minerals"]["shares"])
    else:
        cores = {key: rocky[key]["core_cells"] for key in active}
    total = sum(cores.values())
    for path, variable in c._custom_section_vars.items():
        value = get_path(sections, tuple(path.split(".")))
        if path == "start_bonus.rocky_minerals.total_core_cells":
            value = total
        elif path == "start_bonus.rocky_minerals.radius_min" and rocky["surface_mode"] != "equal":
            value = rocky_equivalent_radius(total, len(active), rocky["radius_min"])
        elif path.startswith("start_bonus.rocky_minerals.") and path.endswith(".core_cells"):
            value = cores.get(path.split(".")[-2], value)
        formatter = c._custom_generator_value_formatters.get(path)
        if formatter:
            value = formatter(value)
        elif isinstance(value, (int, float)) and not isinstance(value, bool):
            value = c._custom_archetype_display_number(value)
        # Disabled decoration/terrain inputs intentionally display zero.
        if variable.get() != value:
            assert variable.get() == "0" and path.startswith(("decorations.", "terrains."))


def test_mode_switch_keeps_controls_archetype_and_live_dependencies(editor):
    c = editor
    identities = dict(c._custom_section_vars)
    generation = c._custom_layout_generation
    root_children = c._custom_generator_tab.winfo_children()
    for mode in ("upgraded", "legacy", "upgraded"):
        c.mode.set(MODE_LABELS[c.prefs["language"]][mode])
        c._custom_selection_changed()
        assert c._custom_config == build_custom_config(mode, "large_islands")
        assert c._custom_section_vars == identities
        assert c._custom_generator_tab.winfo_children() == root_children
        assert c._custom_layout_generation == generation
        assert_display(c)
        assert c._custom_fish_band_thickness_widget.options["state"] == ("normal" if c._custom_config.semantic_sections()["fish"]["near_shore"] else "disabled")
    assert len(c.archetype_renders) == 1
    assert not c.preview_calls


@pytest.mark.parametrize("section", ["start_bonus", "minerals", "fish", "trees", "building_stones", "decorations", "terrains", "rivers"])
def test_section_reset_keeps_widgets_and_other_committed_values(editor, section):
    c = editor
    base = build_custom_config("upgraded", "large_islands")
    sections = base.semantic_sections()
    sections["rivers"]["rate_percent"] = 42
    sections["minerals"]["occupancy_percent"] = 31
    sections["fish"]["fill_percent"] = 21
    sections["trees"]["saplings"]["enabled"] = False
    sections["building_stones"]["average_quantity"] = 3
    sections["decorations"]["cacti"] = 42
    sections["terrains"]["desert"]["enabled"] = False
    sections["start_bonus"]["rocky_minerals"]["gems"]["enabled"] = True
    sections["start_bonus"]["rocky_minerals"]["surface_mode"] = "custom"
    c._custom_config = base.with_sections(sections).with_start_packages(("start_rocky_minerals",))
    c._custom_last_concrete_mode = "upgraded"
    c.mode.set(MODE_LABELS[c.prefs["language"]]["custom"])
    c._custom_selection_changed()
    before = c._custom_config.semantic_sections()
    widgets = dict(c._custom_section_vars)
    assert c._custom_section_is_modified(section)
    c._custom_reset_section(section)
    expected = dict(before)
    expected[section] = base.semantic_sections()[section]
    if section == "decorations":
        expected["objects"] = base.semantic_sections()["objects"]
    assert c._custom_config.semantic_sections() == expected
    assert not c._custom_section_is_modified(section)
    assert c._custom_section_vars == widgets
    assert_display(c)
    assert len(c.archetype_renders) == 1
    assert not c.preview_calls


def test_language_rebuild_retires_only_owned_bindings_and_pending_jobs(editor):
    c = editor
    root = c._custom_generator_tab
    external = root.bind("<Configure>", lambda event: None, add="+")
    for _ in range(3):
        root.resize(640)
        for _, callback in list(root.bindings.values()):
            callback(SimpleNamespace())
        old_jobs = set(root.jobs)
        c._custom_refresh_after_language()
        assert external in root.bindings
        assert len(root.bindings) == 3
        assert len(root.jobs) == 2
        assert not old_jobs.intersection(root.jobs)
        # New callbacks own live children; stale callbacks have been canceled.
        root.flush()
        assert not root.jobs
    assert len(c.archetype_renders) == 4


def test_same_responsive_layout_does_not_reposition_controls(editor):
    c = editor
    root = c._custom_generator_tab
    def total(widget):
        return widget.placements + sum(total(child) for child in widget.children)
    old = total(root)
    for width in (1001, 1002, 1000):
        root.resize(width)
    assert total(root) == old
    root.resize(250)
    changed = total(root)
    assert changed > old
    root.resize(251)
    assert total(root) == changed


def test_plain_generator_edits_and_unchanged_focusout_do_not_refresh_relief(editor):
    c = editor
    c._custom_section_changed(("minerals", "occupancy_percent"), "31")
    digest = c._custom_config.digest
    c._custom_section_changed(("minerals", "occupancy_percent"), "31")
    assert c._custom_config.digest == digest
    assert not c.preview_calls
    assert len(c.archetype_renders) == 1


def test_full_custom_reset_uses_current_base_and_keeps_controls(editor):
    c = editor
    c._custom_section_changed(("fish", "fill_percent"), "31")
    widgets = dict(c._custom_section_vars)
    c._custom_reset()
    assert c._custom_config == build_custom_config("legacy", "large_islands")
    assert c._custom_section_vars == widgets
    assert_display(c)
    assert not c.preview_calls


def test_mode_switch_preserves_a_custom_archetype_and_preview(editor):
    c = editor
    edited = c._custom_config.with_archetype_value(("relief", "snow_threshold"), 210)
    c._custom_activate_archetype(edited)
    c.preview_calls.clear()
    c.mode.set(MODE_LABELS[c.prefs["language"]]["upgraded"])
    c._custom_selection_changed()
    assert c._custom_config.archetype_profile == edited.archetype_profile
    assert c._custom_config.base_mode == "upgraded"
    assert not c.preview_calls
    assert len(c.archetype_renders) == 1


def test_language_refresh_restores_the_last_computed_preview_on_new_canvases():
    c = CustomGeneratorController.__new__(CustomGeneratorController)
    c._custom_generator_tab = object()
    computed = object()
    c._custom_archetype_preview_last_result = computed
    actions = []
    def rebuild():
        c._custom_archetype_preview_last_result = None
        actions.append("rebuild")
    def restore(preview):
        assert preview is computed
        c._custom_archetype_preview_last_result = preview
        actions.append("restore")
    c._render_custom_parameter_tabs = rebuild
    c._custom_apply_archetype_preview = restore
    c._custom_refresh_after_language()
    assert actions == ["rebuild", "restore"]
    assert c._custom_archetype_preview_last_result is computed
