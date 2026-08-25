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
    source = Path('s3mapgen/gui_v16.py').read_text(encoding='utf-8')
    for token in (
        "self._manual_history_locks=[];self._history_visual_order=[]",
        "command=self._history_center_toggle_manual_lock",
        "command=lambda:self._history_center_move(-1)",
        "command=lambda:self._history_center_move(1)",
        "self._manual_history_locks=[value for value in self._manual_history_locks if value is not out]",
        "self._manual_history_locks=[];self._history_visual_order=[]",
    ):
        assert token in source


def test_capacity_cannot_be_reduced_below_unique_protected_maps():
    source = Path('s3mapgen/gui_v16.py').read_text(encoding='utf-8')
    assert "protected=len(self._cached_protected_outputs())" in source
    assert "if value<protected:" in source
    assert "blocked=True,protected=protected" in source

