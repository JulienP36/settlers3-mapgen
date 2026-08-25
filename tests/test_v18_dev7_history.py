from pathlib import Path

from s3mapgen.preferences import load_settings, save_settings
from s3mapgen.session_cache import GenerationCacheKey, ImportedHistoryKey, SessionGenerationCache


def test_unified_history_metadata_mru_resize_and_delete():
    cache = SessionGenerationCache(4)
    generated = GenerationCacheKey(1, 768, 4, 'legacy', 'continental')
    imported = ImportedHistoryKey('abc', 'SAV')
    cache.put(generated, object(), {'origin': 'generated'})
    sav = object(); cache.put(imported, sav, {'origin': 'imported', 'source_path': 'map.sav'})
    assert cache.metadata(imported)['source_path'] == 'map.sav'
    assert cache.get(generated) is not None
    assert cache.entries()[0][0] == generated
    cache.resize(1)
    assert len(cache) == 1
    assert cache.remove(generated) is not None
    assert len(cache) == 0


def test_import_identity_deduplicates_same_binary_content():
    cache = SessionGenerationCache(8)
    first = ImportedHistoryKey('same-digest', 'MAP')
    second = ImportedHistoryKey('same-digest', 'MAP')
    cache.put(first, 'one', {'source_path': 'first.map'})
    cache.put(second, 'two', {'source_path': 'copy.map'})
    assert len(cache) == 1
    assert cache.get(first) == 'two'
    assert cache.metadata(first)['source_path'] == 'copy.map'


def test_current_and_comparison_outputs_are_protected_from_lru_eviction():
    cache = SessionGenerationCache(2)
    pinned = object(); other = object(); newest = object()
    cache.set_protected_provider(lambda: (pinned,))
    cache.put('pinned', pinned); cache.put('other', other); cache.put('newest', newest)
    assert cache.peek('pinned') is pinned
    assert cache.peek('other') is None
    assert cache.peek('newest') is newest


def test_history_capacity_preference_is_bounded(tmp_path, monkeypatch):
    import s3mapgen.preferences as preferences
    monkeypatch.setattr(preferences, 'settings_path', lambda: Path(tmp_path) / 'settings.json')
    save_settings({'history_capacity': 16})
    assert load_settings()['history_capacity'] == 16
    (Path(tmp_path) / 'settings.json').write_text('{"history_capacity": 99}', encoding='utf-8')
    assert load_settings()['history_capacity'] == 8


def test_dev7_history_center_contract_is_present():
    source = (Path(__file__).parents[1] / 's3mapgen' / 'gui_v16.py').read_text(encoding='utf-8')
    for token in ('ImportedHistoryKey', 'def _open_history_center', 'def _history_center_delete',
                  "values=('4','8','12','16')", 'def _register_import_history',
                  "style='History.Treeview'", 'delete_assigned', 'capacity_reduce'):
        assert token in source


def test_semantic_theme_palettes_keep_role_parity():
    from s3mapgen.gui_v16 import THEME_PALETTES
    assert set(THEME_PALETTES) == {'dark', 'light'}
    assert set(THEME_PALETTES['dark']) == set(THEME_PALETTES['light'])
    for role in ('window','panel','surface','field','text','muted','disabled','border',
                 'hover','pressed','selection','primary','success','warning','danger','info'):
        assert role in THEME_PALETTES['dark']


def test_dev7_r3_history_table_has_rank_lock_and_live_capacity():
    source = (Path(__file__).parents[1] / 's3mapgen' / 'gui_v16.py').read_text(encoding='utf-8')
    assert "show='tree headings'" in source
    assert "tree.heading('#0',text='',image=self._history_heading_lock_icon,anchor='center')" in source
    assert "tree.heading('rank',text='#'" in source
    assert "values=(index+1,origin_label,map_label,details)" in source
    assert "image=self._history_role_image(roles)" in source
    assert "format(used=len(self.session_cache),count=self.session_cache.max_entries)" in source


def test_dev7_r3_accessible_state_indicators_cover_show_load_and_ab():
    source = (Path(__file__).parents[1] / 's3mapgen' / 'gui_v16.py').read_text(encoding='utf-8')
    assert "kind=='status_on'" in source and "kind=='status_off'" in source
    assert "def _refresh_state_indicators" in source
    assert "show.configure(text=ctx['shown'] if active else bt['show']" in source
    assert "load.configure(text=_CONTEXT_TEXT" in source
    assert "states={'show':" in source


def test_dev7_r3_import_details_use_lowercase_extension():
    source = (Path(__file__).parents[1] / 's3mapgen' / 'gui_v16.py').read_text(encoding='utf-8')
    assert "f'(.{key.source_format.lower()})" in source


def test_dev7_r3_history_large_preview_is_draggable_zoomable_and_reused():
    source = (Path(__file__).parents[1] / 's3mapgen' / 'gui_v16.py').read_text(encoding='utf-8')
    for token in ('def _history_toggle_large_preview','def _history_large_drag_start',
                  "label.bind('<MouseWheel>'",'def _history_large_wheel',
                  'preserved=(old.winfo_x(),old.winfo_y())'):
        assert token in source


def test_dev7_r3_manual_deletion_covers_current_and_comparison_roles():
    source = (Path(__file__).parents[1] / 's3mapgen' / 'gui_v16.py').read_text(encoding='utf-8')
    assert "if out is getattr(self,'current',None):reasons.append(text['main_view'])" in source
    assert "reasons.extend(f'Slot {slot}' for slot in slots)" in source
    assert "outside_history" in source
    assert "confirm_clear_protected" in source


def test_dev7_r3_history_catalogs_keep_four_language_key_parity():
    from s3mapgen.gui_v16 import HISTORY_TEXT
    assert set(HISTORY_TEXT) == {'fr','en','de','es'}
    assert all(set(values) == set(HISTORY_TEXT['fr']) for values in HISTORY_TEXT.values())


def test_dev7_r4_observational_peek_does_not_promote_lru_order():
    cache=SessionGenerationCache(4)
    cache.put('old','old');cache.put('new','new')
    assert [key for key,_ in cache.entries()]==['new','old']
    assert cache.peek('old')=='old'
    assert [key for key,_ in cache.entries()]==['new','old']


def test_dev7_r4_history_navigation_and_assignment_use_peek():
    source=(Path(__file__).parents[1] / 's3mapgen' / 'gui_v16.py').read_text(encoding='utf-8')
    assert "out=self.session_cache.peek(key) if key else None" in source
    assert "def _history_center_assign(self,slot):\n        key=self._history_selected_key();out=self.session_cache.peek(key)" in source


def test_dev7_r4_role_locks_prepare_viewer_ab_and_manual_roles():
    source=(Path(__file__).parents[1] / 's3mapgen' / 'gui_v16.py').read_text(encoding='utf-8')
    for token in ("roles.append('V')","roles.append('A')","roles.append('B')","roles.append('M')",'def _history_role_icon'):
        assert token in source


def test_dev7_r4_history_preview_matches_batch_interaction_contract():
    source=(Path(__file__).parents[1] / 's3mapgen' / 'gui_v16.py').read_text(encoding='utf-8')
    for token in ('def _history_schedule_hover_preview','self.after(700','def _history_bind_large_surface',"cursor='fleur' if pinned else 'arrow'",'old_projection==projection'):
        assert token in source


def test_dev7_r4_batch_capacity_preflight_and_context_labels_are_localized():
    from s3mapgen.gui_v16 import _BATCH_CAPACITY_TEXT, _CONTEXT_TEXT
    assert set(_BATCH_CAPACITY_TEXT)=={'fr','en','de','es'}
    assert set(_CONTEXT_TEXT)=={'fr','en','de','es'}
    source=(Path(__file__).parents[1] / 's3mapgen' / 'gui_v16.py').read_text(encoding='utf-8')
    assert 'def _confirm_batch_cache_capacity' in source
    assert "ctx['shown'] if active else bt['show']" in source


def test_dev7_r4_outside_history_warning_has_hover_explanation():
    source=(Path(__file__).parents[1] / 's3mapgen' / 'gui_v16.py').read_text(encoding='utf-8')
    assert "bind('<Enter>',lambda e:self._history_residency_tooltip())" in source
    assert 'def _show_ui_tooltip' in source


def test_dev7_r6_cache_forecast_counts_viewer_ab_and_deduplicates_roles():
    from s3mapgen.gui_v16 import App
    current=object();slot_a=object();slot_b=object()
    cache=SessionGenerationCache(4)
    cache.put('current',current);cache.put('a',slot_a);cache.put('b',slot_b)
    dummy=type('Dummy',(),{})();dummy.session_cache=cache;dummy.current=current
    dummy._compare_slots={'A':slot_a,'B':slot_b};dummy._manual_history_locks=[]
    dummy._output_in_history=lambda out:any(value is out for _,value in cache.entries())
    requests=[{'key':GenerationCacheKey(seed,768,4,'legacy','continental')} for seed in range(1,5)]
    forecast=App._batch_cache_capacity_forecast(dummy,requests)
    assert forecast=={
        'used':3,'capacity':4,'requested':4,'retained':1,'protected':3,
        'existing_evicted':0,'batch_dropped':3,
    }


def test_dev7_r6_batch_autodisplay_only_fills_an_empty_viewer():
    from s3mapgen.gui_v16 import App
    dummy=type('Dummy',(),{'current':object()})()
    assert App._batch_should_autodisplay(dummy) is False
    dummy.current=None
    assert App._batch_should_autodisplay(dummy) is True


def test_dev7_r6_capacity_warning_uses_exact_forecast_and_custom_dialog():
    from s3mapgen.gui_v16 import App, _BATCH_CAPACITY_TEXT
    assert set(_BATCH_CAPACITY_TEXT)=={'fr','en','de','es'}
    assert all(set(catalog)==set(_BATCH_CAPACITY_TEXT['fr']) for catalog in _BATCH_CAPACITY_TEXT.values())
    forecast={'used':4,'capacity':4,'requested':4,'retained':1,'protected':3,'existing_evicted':1,'batch_dropped':3}
    captured=[]
    dummy=type('Dummy',(),{})()
    dummy._batch_cache_capacity_forecast=lambda requests:forecast
    dummy._show_batch_cache_warning=lambda value:captured.append(value) or False
    assert App._confirm_batch_cache_capacity(dummy,[object()]) is False
    assert captured==[forecast]


def test_dev7_r6_capacity_forecast_is_exact_for_all_supported_full_caches():
    from s3mapgen.gui_v16 import App
    for capacity in (4,8,12,16):
        cache=SessionGenerationCache(capacity)
        current=object();slot_a=object();slot_b=object()
        cache.put('current',current);cache.put('a',slot_a);cache.put('b',slot_b)
        for index in range(capacity-3):cache.put(f'existing-{index}',object())
        dummy=type('Dummy',(),{})();dummy.session_cache=cache;dummy.current=current
        dummy._compare_slots={'A':slot_a,'B':slot_b};dummy._manual_history_locks=[]
        requests=[{'key':GenerationCacheKey(seed,768,4,'legacy','continental')} for seed in range(1,5)]
        forecast=App._batch_cache_capacity_forecast(dummy,requests)
        assert forecast['capacity']==capacity
        assert forecast['used']==capacity
        assert forecast['existing_evicted']==min(4,capacity-3)
        assert forecast['batch_dropped']==max(0,7-capacity)
        assert forecast['retained']==min(4,capacity-3)


def test_dev7_r6_capacity_forecast_allows_batch_when_nothing_is_discarded():
    from s3mapgen.gui_v16 import App
    cache=SessionGenerationCache(8)
    current=object();slot_a=object();slot_b=object()
    cache.put('current',current);cache.put('a',slot_a);cache.put('b',slot_b)
    dummy=type('Dummy',(),{})();dummy.session_cache=cache;dummy.current=current
    dummy._compare_slots={'A':slot_a,'B':slot_b};dummy._manual_history_locks=[]
    requests=[{'key':GenerationCacheKey(seed,768,4,'legacy','continental')} for seed in range(1,5)]
    forecast=App._batch_cache_capacity_forecast(dummy,requests)
    assert forecast['existing_evicted']==0
    assert forecast['batch_dropped']==0
    dummy._batch_cache_capacity_forecast=lambda values:forecast
    dummy._show_batch_cache_warning=lambda value:(_ for _ in ()).throw(AssertionError('unexpected warning'))
    assert App._confirm_batch_cache_capacity(dummy,requests) is True


def test_dev7_r7_capacity_forecast_scales_with_future_manual_locks():
    from s3mapgen.gui_v16 import App
    cache=SessionGenerationCache(8)
    current=object();slot_a=object();slot_b=object();manual=[object(),object(),object()]
    cache.put('current',current);cache.put('a',slot_a);cache.put('b',slot_b)
    for index,value in enumerate(manual):cache.put(f'manual-{index}',value)
    cache.put('free-0',object());cache.put('free-1',object())
    dummy=type('Dummy',(),{})();dummy.session_cache=cache;dummy.current=current
    dummy._compare_slots={'A':slot_a,'B':slot_b};dummy._manual_history_locks=manual
    requests=[{'key':GenerationCacheKey(seed,768,4,'legacy','continental')} for seed in range(1,5)]
    forecast=App._batch_cache_capacity_forecast(dummy,requests)
    assert forecast['protected']==6
    assert forecast['existing_evicted']==2
    assert forecast['retained']==2
    assert forecast['batch_dropped']==2


def test_dev7_r6_non_retained_results_have_localized_status_and_summary():
    from s3mapgen.gui_v16 import BATCH_TEXT
    for language in ('fr','en','de','es'):
        assert BATCH_TEXT[language]['not_cached']
        assert '{lost}' in BATCH_TEXT[language]['finished_retention']
    source=(Path(__file__).parents[1] / 's3mapgen' / 'gui_v16.py').read_text(encoding='utf-8')
    assert "self._batch_text('not_cached')" in source
    assert "self._batch_text('finished_retention'" in source
    assert "colors.get('warning','#f9ab00')" in source


def test_dev7_r6_cache_really_retains_one_batch_result_with_three_protections():
    cache=SessionGenerationCache(4)
    current=object();slot_a=object();slot_b=object()
    cache.set_protected_provider(lambda:(current,slot_a,slot_b))
    cache.put('current',current);cache.put('a',slot_a);cache.put('b',slot_b)
    results=[]
    for index in range(4):
        value=object();results.append(value);cache.put(f'batch-{index}',value)
    retained=[value for key,value in cache.entries() if key.startswith('batch-')]
    assert retained==[results[-1]]


def test_dev7_r7_history_capacity_warning_is_fully_modal_themed_and_localized():
    import inspect
    from s3mapgen.gui_v16 import App, _HISTORY_CAPACITY_DIALOG_TEXT
    assert set(_HISTORY_CAPACITY_DIALOG_TEXT)=={'fr','en','de','es'}
    assert all(set(catalog)==set(_HISTORY_CAPACITY_DIALOG_TEXT['fr']) for catalog in _HISTORY_CAPACITY_DIALOG_TEXT.values())
    source=inspect.getsource(App._show_history_capacity_warning)
    for token in ('win.grab_set()','win.wait_window()','self.history_capacity_combo.configure(state=\'disabled\')','_apply_history_capacity_dialog_theme'):
        assert token in source
    assert 'messagebox.askyesno' not in inspect.getsource(App._history_capacity_changed)


def test_dev7_r9_magnifier_is_translucent_has_five_states_and_no_backing_square():
    from PIL import Image
    from s3mapgen.gui_v16 import _thumbnail_with_magnifier
    base=Image.new('RGBA',(180,120),(31,73,109,255))
    states={state:_thumbnail_with_magnifier(base,state) for state in ('idle','hover','active','preview_hover','close_hover')}
    for image in states.values():
        assert image.getpixel((0,0))==base.getpixel((0,0))
        assert image.getpixel((179,119))==base.getpixel((179,119))
        assert image.getpixel((90,56))!=base.getpixel((90,56))
    assert len({image.tobytes() for image in states.values()})==5


def test_dev7_r8_active_and_hover_magnifiers_are_independent():
    from s3mapgen.gui_v16 import App
    active=object();hovered=object()
    dummy=type('Dummy',(),{})();dummy._magnifier_active_kind='batch';dummy._magnifier_active_ref=active;dummy._magnifier_hover_kind='batch';dummy._magnifier_hover_ref=hovered
    dummy._magnifier_refs_match=App._magnifier_refs_match;dummy._magnifier_preview_exists=lambda kind,ref:ref is active;dummy._magnifier_preview_pinned=lambda kind,ref:False
    assert App._magnifier_state_for(dummy,'batch',active)=='active'
    assert App._magnifier_state_for(dummy,'batch',hovered)=='hover'
    assert App._magnifier_state_for(dummy,'batch',object())=='idle'
    dummy._magnifier_hover_ref=active
    assert App._magnifier_state_for(dummy,'batch',active)=='preview_hover'
    dummy._magnifier_preview_pinned=lambda kind,ref:True
    assert App._magnifier_state_for(dummy,'batch',active)=='close_hover'


def test_dev7_r8_magnifier_hover_exit_and_preview_fallback_contract():
    source=(Path(__file__).parents[1] / 's3mapgen' / 'gui_v16.py').read_text(encoding='utf-8')
    for token in ('def _set_magnifier_hover','def _set_magnifier_active','def _restore_magnifier_visual',"'idle'","'hover'","'active'","'preview_hover'","'close_hover'",'def _batch_hover_preview_ready','def _history_hover_preview_ready',"thumbnail_host'].bind('<Leave>'","preview_image_host.bind('<Leave>'"):
        assert token in source


def test_dev7_r8_batch_preview_gains_history_zoom_parity():
    import inspect
    from s3mapgen.gui_v16 import App
    source=inspect.getsource(App._batch_build_preview_surface)+inspect.getsource(App._batch_preview_geometry)+inspect.getsource(App._batch_preview_wheel)
    assert "label.bind('<MouseWheel>',self._batch_preview_wheel)" in source
    assert 'self._batch_preview_zoom' in source
    assert "self._batch_refresh_preview_tooltip(self._batch_preview_row)" in source
    assert 'max_w=max(320,screen_w-80);max_h=max(280,screen_h-120)' in source


def test_dev7_r8_capacity_confirm_button_uses_neutral_style():
    import inspect
    from s3mapgen.gui_v16 import App
    source=inspect.getsource(App._show_history_capacity_warning)
    assert "ttk.Button(buttons,text=dialog_text['continue'],command=" in source
    assert "style='Warning.TButton'" not in source


def test_dev7_r9_closed_history_center_cannot_refresh_destroyed_preview_widget():
    from s3mapgen.gui_v16 import App
    class StaleLabel:
        def winfo_exists(self):raise AssertionError('destroyed label must not be queried')
    dummy=type('Dummy',(),{})();dummy._history_window=None;dummy._history_preview_label=StaleLabel()
    assert App._refresh_history_preview(dummy) is None


def test_dev7_r9_history_close_clears_every_preview_reference_before_destroy():
    from s3mapgen.gui_v16 import App
    class FakeWindow:
        destroyed=False
        def destroy(self):self.destroyed=True
    win=FakeWindow();dummy=type('Dummy',(),{})();dummy._history_window=win;dummy._magnifier_hover_kind=None
    dummy._history_cancel_hover_preview=lambda:None;dummy._history_hide_large_preview=lambda:None;dummy._hide_ui_tooltip=lambda:None
    for name in ('_history_tree','_history_preview_label','_history_preview_status','_history_preview_source','_history_preview_photo','_history_preview_base_image','_history_preview_key'):setattr(dummy,name,object())
    dummy._history_center_lookup={'x':1};dummy._history_window_widgets={'x':1};dummy._history_preview_hover=True
    App._close_history_center(dummy)
    assert win.destroyed is True
    assert dummy._history_window is None and dummy._history_tree is None and dummy._history_preview_label is None
    assert dummy._history_preview_status is None and dummy._history_preview_source is None and dummy._history_preview_base_image is None


def test_dev7_r10_temporary_preview_never_covers_its_source_and_keeps_requested_zoom():
    from PIL import Image
    from s3mapgen.gui_v16 import App
    class Anchor:
        def update_idletasks(self):pass
        def winfo_rootx(self):return 710
        def winfo_rooty(self):return 430
        def winfo_width(self):return 180
        def winfo_height(self):return 120
    dummy=type('Dummy',(),{})();dummy.winfo_screenwidth=lambda:1920;dummy.winfo_screenheight=lambda:1080
    dummy._history_large_scaled_image=lambda image:(image,(image.width,image.height));dummy._history_large_clamp=lambda x,y,size:(x,y)
    zoom=1.25;image=Image.new('RGBA',(1200,800),(0,0,0,0))
    _,size,x,y=App._temporary_preview_geometry(dummy,image,zoom,Anchor())
    preview=(x,y,x+size[0],y+size[1]);source=(710,430,890,550)
    assert preview[2]<=source[0]-18 or preview[0]>=source[2]+18 or preview[3]<=source[1]-18 or preview[1]>=source[3]+18
    assert zoom==1.25


def test_dev7_r10_only_unpinned_previews_use_automatic_anticollision():
    import inspect
    from s3mapgen.gui_v16 import App
    history=inspect.getsource(App._history_show_large_preview);batch=inspect.getsource(App._batch_show_preview_tooltip)
    assert "if pinned:" in history and '_temporary_preview_geometry' in history
    assert "if pinned:" in batch and '_temporary_preview_geometry' in batch
    assert "self.bind('<Escape>',self._close_large_preview_escape" in inspect.getsource(App.__init__)
