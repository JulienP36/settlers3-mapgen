from pathlib import Path

import pytest

from s3mapgen.application.main_window import MainWindow
from s3mapgen.application.ui.i18n.batch import BATCH_TEXT


ROOT = Path(__file__).resolve().parents[3] / "s3mapgen" / "application"
SRC = "\n".join(
    (ROOT / relative).read_text(encoding="utf-8")
    for relative in (
        "main_window.py", "viewer/controller.py", "batch/controller.py",
        "history/controller.py", "workflows/generation.py",
        "ui/i18n/controller.py",
    )
)


class Var:
    def __init__(self, value):
        self.value = value

    def get(self):
        return self.value

    def set(self, value):
        self.value = value


def row(index, *, mode="Héritage (Legacy)", archetype="Continental", mirror="Aucun", side="768", players="4", seed="100"):
    return {
        "index": index,
        "mode_var": Var(mode),
        "arch_var": Var(archetype),
        "mirror_var": Var(mirror),
        "size_var": Var(side),
        "players_var": Var(players),
        "seed_var": Var(seed),
    }


def batch_dummy(rows, count=None, language="fr"):
    class Dummy:
        pass

    dummy = Dummy()
    dummy.prefs = {"language": language}
    dummy._batch_rows = rows
    dummy._batch_count_var = Var(count if count is not None else len(rows))
    dummy._batch_label_key = MainWindow._batch_label_key
    return dummy


def test_batch_is_bilingual_and_replaces_the_reserved_placeholder():
    assert BATCH_TEXT["fr"]["start"] == "Générer le lot"
    assert BATCH_TEXT["en"]["start"] == "Generate batch"
    assert "command=self._open_batch_window" in SRC
    assert "batch_reserved" not in SRC


def test_batch_collects_one_to_four_independent_generation_keys():
    dummy = batch_dummy([
        row(1, mode="Héritage (Legacy)", players="4", seed="101"),
        row(2, mode="Amélioré (Upgraded)", players="8", seed="202"),
    ])
    requests = MainWindow._batch_collect_requests(dummy)
    assert [request["key"].seed for request in requests] == [101, 202]
    assert [request["key"].players for request in requests] == [4, 8]
    assert [request["key"].mode for request in requests] == ["legacy", "upgraded"]
    assert requests[0]["key"].engine_revision == "continental_legacy_native_content"
    assert requests[1]["key"].engine_revision == "continental_upgraded-native-v1"


def test_batch_collects_native_size_and_mirror_parameters():
    dummy = batch_dummy([row(1, side="320", players="6", mirror="Axe long")])
    request = MainWindow._batch_collect_requests(dummy)[0]["key"]
    assert request.side == 320
    assert request.players == 6
    assert request.mirror_mode == 1


def test_batch_accepts_mirror_for_upgraded_maps():
    dummy = batch_dummy([row(1, mode="Amélioré (Upgraded)", side="256", players="2", mirror="Les deux")])
    request = MainWindow._batch_collect_requests(dummy)[0]["key"]
    assert request.mode == "upgraded"
    assert request.mirror_mode == 3


def test_batch_rejects_unknown_sizes_before_starting():
    dummy = batch_dummy([row(1, side="192")])
    with pytest.raises(ValueError, match="native"):
        MainWindow._batch_collect_requests(dummy)


def test_batch_queue_is_sequential_and_populates_history_and_ab_actions():
    assert "request=self._batch_queue.pop(0)" in SRC
    assert "self.generator.generate(key.players,key.seed,mode=key.mode,archetype=key.archetype,side=key.side,mirror_mode=key.mirror_mode)" in SRC
    assert "self.session_cache.put(key,out)" in SRC
    assert "self.after(30,self._batch_run_next)" in SRC
    assert "self._set_compare_output(slot,out)" in SRC


def test_cancel_only_marks_queued_maps_and_never_interrupts_the_engine():
    assert "self._batch_cancel_requested=True" in SRC
    assert "Cancellation deliberately affects" in SRC
    assert "the protected engine is never interrupted" in SRC


def test_rows_share_the_default_seed_and_keep_row_and_global_randomizers():
    assert "row['seed_var']=tk.StringVar(value=str(first_seed))" in SRC
    assert "command=lambda r=row:self._batch_randomize_row(r)" in SRC
    assert "command=self._batch_randomize_seeds" in SRC
    assert "command=self._batch_apply_seed_all" in SRC


def test_map_previews_use_real_renders_with_click_and_delayed_hover():
    assert "render_square_base(out.state,view='global'" in SRC
    assert "'<Button-1>'" in SRC
    assert "self.after(700" in SRC
    assert "Image.Resampling.NEAREST" in SRC


def test_open_batch_window_is_retranslated_live():
    assert "self._apply_language();self._retranslate_batch_window()" in SRC
    assert "def _retranslate_batch_window" in SRC


def test_batch_window_is_hidden_during_initial_widget_and_geometry_build():
    open_window=SRC[SRC.index('def _open_batch_window'):SRC.index('def _fit_batch_window_initial')]
    assert "win=tk.Toplevel(self);self._batch_window=win;win.withdraw()" in open_window
    assert "self._batch_update_row_visibility();self._fit_batch_window_initial();win.deiconify()" in open_window


def test_assignment_is_unique_and_batch_buttons_show_active_state():
    assert "moved=self._compare_slots.get(other) is out" in SRC
    assert "if moved:self._compare_slots[other]=None" in SRC
    assert "def _refresh_batch_assignment_buttons" in SRC
    assert "active=out is not None and self._compare_slots.get(slot) is out" in SRC
    assert "ctx['assigned_a' if slot=='A' else 'assigned_b']" in SRC


def test_action_order_and_feedback_colors_are_explicit():
    show=SRC.index("row['show'].grid(row=0,column=0")
    set_a=SRC.index("row['set_a'].grid(row=0,column=1")
    set_b=SRC.index("row['set_b'].grid(row=0,column=2")
    progress=SRC.index("row['progress'].grid(row=0,column=3")
    assert show < set_a < set_b < progress
    assert "'cached':'#2879d0'" in SRC
    assert "'failed':'#d84a3a'" in SRC


def test_thumbnail_container_matches_parallelogram_ratio():
    assert "width=182,height=122" in SRC
    assert "grid_propagate(False)" in SRC
    assert "thumb.thumbnail((180,120)" in SRC
    assert "bg=mini_bg,bd=0,highlightthickness=0" in SRC
    assert "text=str(index),width=12,height=4" not in SRC


def test_minimap_container_reaches_the_outer_row_border():
    assert "padding=(1,1)" in SRC
    host=SRC[SRC.index("row['thumbnail_host']=tk.Frame"):SRC.index("row['thumbnail']=tk.Label")]
    assert "padx=" not in host and "pady=" not in host
    assert "controls.grid(row=0,column=0,sticky='ew',padx=(7,0)" in SRC


def test_progress_bar_keeps_space_before_minimap():
    assert "result_line.grid(row=1,column=0,sticky='ew',padx=(7,8)" in SRC


def test_map_count_applies_live_without_redundant_button():
    assert "_batch_apply_count_button" not in SRC
    assert "command=self._batch_update_row_visibility" in SRC
    assert "bind('<KeyRelease>',self._batch_count_typed)" in SRC
    assert "bind('<FocusOut>',self._batch_commit_count)" in SRC
    assert "def _batch_count_typed" in SRC and "def _batch_commit_count" in SRC


def test_common_seed_keeps_its_own_randomizer_button():
    assert "self._batch_common_seed_random=ttk.Button" in SRC
    assert "command=self._batch_randomize_common_seed" in SRC
    assert "self._batch_common_seed_random.pack" in SRC
    assert SRC.index("self._batch_common_seed_entry.pack") < SRC.index("self._batch_common_seed_random.pack") < SRC.index("self._batch_apply_seed_button.pack")


def test_large_preview_is_a_borderless_transparent_tooltip():
    assert "win.overrideredirect(True)" in SRC
    assert "win.wm_attributes('-transparentcolor',chroma)" in SRC
    assert "chroma='#ff00ff'" in SRC
    tooltip=SRC[SRC.index("def _batch_show_preview_tooltip"):SRC.index("def _batch_hide_preview_tooltip")]
    assert "win.title(" not in tooltip
    assert "def _batch_toggle_large_preview" in SRC


def test_projection_change_refreshes_batch_thumbnails_and_open_tooltip():
    projection=SRC[SRC.index("def _projection_changed"):SRC.index("def _update_view_controls")]
    assert "self._refresh_batch_previews()" in projection
    refresh=SRC[SRC.index("def _refresh_batch_previews"):SRC.index("def _batch_schedule_hover_preview")]
    assert "self._batch_render_thumbnail(row)" in refresh
    assert "self._batch_refresh_preview_tooltip(visible_row)" in refresh


def test_tooltip_position_is_anchored_to_the_minimap_not_the_pointer():
    tooltip=SRC[SRC.index("def _batch_show_preview_tooltip"):SRC.index("def _batch_hide_preview_tooltip")]
    assert "anchor=row['thumbnail_host']" in tooltip
    assert "left_space=" in tooltip and "right_space=" in tooltip
    assert "self.winfo_pointerx()" not in tooltip


def test_initial_batch_geometry_fits_requested_content_when_screen_allows():
    assert "self._batch_update_row_visibility();self._fit_batch_window_initial()" in SRC
    fit=SRC[SRC.index("def _fit_batch_window_initial"):SRC.index("def _default_batch_seed")]
    assert "win.winfo_reqwidth()" in fit and "win.winfo_reqheight()" in fit
    assert "screen_w-64" in fit and "screen_h-96" in fit
    assert "win.geometry(f'{width}x{height}+{x}+{y}')" in fit
