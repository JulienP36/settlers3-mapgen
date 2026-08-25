from pathlib import Path

from s3mapgen.gui_v16 import App, HISTORY_TEXT
from s3mapgen.session_cache import SessionGenerationCache


class _HistoryDummy:
    _ordered_history_entries = App._ordered_history_entries
    _history_move_key = App._history_move_key
    _cached_protected_outputs = App._cached_protected_outputs


def test_visual_order_is_independent_from_real_lru_recency():
    dummy = _HistoryDummy()
    dummy.session_cache = SessionGenerationCache(max_entries=8)
    dummy._history_visual_order = []
    for key in ('a', 'b', 'c'):
        dummy.session_cache.put(key, object())

    assert [key for key, _ in dummy._ordered_history_entries()] == ['c', 'b', 'a']
    dummy.session_cache.get('a')
    assert [key for key, _ in dummy._ordered_history_entries()] == ['c', 'b', 'a']

    assert dummy._history_move_key('a', -1)
    assert [key for key, _ in dummy._ordered_history_entries()] == ['c', 'a', 'b']

    dummy.session_cache.put('d', object())
    assert [key for key, _ in dummy._ordered_history_entries()] == ['d', 'c', 'a', 'b']


def test_visual_order_drops_evicted_keys_without_reordering_survivors():
    dummy = _HistoryDummy()
    dummy.session_cache = SessionGenerationCache(max_entries=3)
    dummy._history_visual_order = []
    for key in ('a', 'b', 'c'):
        dummy.session_cache.put(key, object())
    dummy._ordered_history_entries()
    dummy._history_move_key('a', -1)

    dummy.session_cache.put('d', object())
    assert [key for key, _ in dummy._ordered_history_entries()] == ['d', 'c', 'b']


def test_unique_cached_protections_merge_viewer_slots_and_manual_lock():
    dummy = _HistoryDummy()
    dummy.session_cache = SessionGenerationCache(max_entries=8)
    shared = object()
    manual = object()
    outside = object()
    dummy.session_cache.put('shared', shared)
    dummy.session_cache.put('manual', manual)
    dummy.current = shared
    dummy._compare_slots = {'A': shared, 'B': outside}
    dummy._manual_history_locks = [shared, manual, outside]

    protected = dummy._cached_protected_outputs()
    assert len(protected) == 2
    assert any(value is shared for value in protected)
    assert any(value is manual for value in protected)


def test_dev10_manual_history_controls_are_translated_in_every_language():
    required = {
        'lock', 'unlock', 'move_up', 'move_down', 'display_position',
        'manual_lock', 'locked', 'unlocked', 'capacity_protected',
    }
    for language in ('fr', 'en', 'de', 'es'):
        assert required <= HISTORY_TEXT[language].keys()


def test_dev10_history_center_wires_manual_lock_reorder_and_cleanup():
    for method_name in (
        '_history_center_toggle_manual_lock',
        '_history_center_move',
        '_history_center_delete',
        '_clear_history',
    ):
        assert callable(getattr(App, method_name))


def test_capacity_cannot_be_reduced_below_unique_protected_maps():
    source = Path('s3mapgen/gui_v16.py').read_text(encoding='utf-8')
    assert "protected=len(self._cached_protected_outputs())" in source
    assert "if value<protected:" in source
    assert "blocked=True,protected=protected" in source


def test_full_cache_rejects_new_viewer_result_when_every_old_entry_is_protected():
    cache = SessionGenerationCache(max_entries=3)
    old = [object() for _ in range(3)]
    for index, value in enumerate(old):
        cache.put(f'old-{index}', value)
    incoming = object()
    cache.set_protected_provider(lambda: (*old, incoming))

    assert cache.put('incoming', incoming) is False
    assert len(cache) == 3
    assert cache.peek('incoming') is None
    assert all(cache.peek(f'old-{index}') is value for index, value in enumerate(old))


def test_full_cache_evicts_old_unprotected_entry_and_retains_new_result():
    cache = SessionGenerationCache(max_entries=3)
    old = [object() for _ in range(3)]
    for index, value in enumerate(old):
        cache.put(f'old-{index}', value)
    incoming = object()
    cache.set_protected_provider(lambda: (old[1], old[2], incoming))

    assert cache.put('incoming', incoming) is True
    assert len(cache) == 3
    assert cache.peek('old-0') is None
    assert cache.peek('incoming') is incoming


def test_repeated_protected_insertions_can_never_grow_past_capacity():
    cache = SessionGenerationCache(max_entries=2)
    protected = [object(), object()]
    cache.put('a', protected[0]);cache.put('b', protected[1])
    cache.set_protected_provider(lambda: tuple(protected))

    for index in range(20):
        incoming = object();protected.append(incoming)
        assert cache.put(f'overflow-{index}', incoming) is False
        assert len(cache) == cache.max_entries


def test_history_center_separates_protection_icons_from_rank_column():
    source = Path('s3mapgen/gui_v16.py').read_text(encoding='utf-8')
    assert "columns=('rank','origin','map','details')" in source
    assert "values=(index+1,origin_label,map_label,details)" in source
    assert "_selector_icon(self.viewer_toolbar,'#f2b84b','warning',20)" in source
    assert "def _history_heading_lock_icon(master,width=62,size=18):" in source
