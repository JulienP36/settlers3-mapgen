import numpy as np
from PIL import Image

from s3mapgen.application.analysis.charts import render_stats_chart
from s3mapgen.application.analysis.core import analyze_map
from s3mapgen.application.rendering.focus import (
    apply_focus_overlay,
    focus_mask,
    focus_signature,
    focus_view,
)
from s3mapgen.map_data.model import MapState


def _state_with_content():
    state = MapState.empty(20)
    state.terrain[:] = 16
    state.terrain[0, :] = 0
    state.terrain[:, 0] = 0
    state.terrain[5:8, 5:8] = 32
    state.terrain[6, 6] = 128
    state.terrain[10:12, 10:12] = 0
    state.terrain[3, 3] = 96
    state.terrain[3, 4] = 97
    state.objects[2, 2] = 68
    state.objects[2, 3] = 84
    state.objects[8, 8] = 115
    state.resources[5, 5] = 0x1F
    state.resources[5, 6] = 0x25
    state.starts = [(2, 2), (15, 15)]
    return state


def test_chart_regions_expose_language_independent_focus_payloads():
    state = _state_with_content()
    stats = analyze_map(state)
    _image, regions = render_stats_chart(stats, 'terrain_families', return_regions=True)
    snow = next(region for region in regions if region['label'].endswith('Neige'))
    assert snow['focus'] == {'kind': 'terrain_ids', 'ids': (35, 128, 129)}
    assert focus_mask(state, snow['focus'])[6, 6]

    _image, regions = render_stats_chart(stats, 'lake_components', return_regions=True)
    assert regions
    lake = regions[0]
    assert lake['focus']['kind'] == 'component'
    assert focus_mask(state, lake['focus']).sum() == stats['hydrology']['inland_water_details'][0]['cells']


def test_focus_masks_match_chart_semantics_and_choose_relevant_views():
    state = _state_with_content()
    assert focus_mask(state, {'kind': 'object_ids', 'ids': (68,)})[2, 2]
    assert focus_mask(state, {'kind': 'resource_family', 'family': 'coal', 'scope': 'open'})[5, 5]
    assert focus_mask(state, {'kind': 'start_player', 'player': 1}).sum() == 1
    assert focus_mask(state, {'kind': 'player_local', 'player': 1, 'radius': 50, 'resource': 'trees'})[2, 2]
    assert focus_view({'kind': 'height_band', 'mode': 'ge', 'threshold': 10}) == 'heightmap'
    assert focus_view({'kind': 'resource_family', 'family': 'coal'}) == 'resources'
    assert focus_view({'kind': 'object_ids', 'ids': (115,)}) == 'global'
    for resource in ('trees', 'stone', 'fish', 'minerals'):
        assert focus_view({'kind': 'player_local', 'player': 1, 'radius': 50, 'resource': resource}) == 'starts'
    assert focus_signature({'kind': 'terrain_ids', 'ids': [16, 18]}) == focus_signature({'ids': (16, 18), 'kind': 'terrain_ids'})


def test_focus_overlay_preserves_base_and_emphasizes_only_selected_cells():
    state = _state_with_content()
    base = Image.fromarray(np.full((state.side, state.side, 3), 100, dtype=np.uint8), mode='RGB')
    focused = np.asarray(apply_focus_overlay(base, state, {'kind': 'terrain_ids', 'ids': (128,)}))
    assert focused[6, 6, 0] > focused[1, 1, 0]
    assert np.array_equal(np.asarray(base), np.full((state.side, state.side, 3), 100, dtype=np.uint8))


def test_comparison_regions_are_tooltip_only_and_zero_distance_stays_linkable():
    state = _state_with_content()
    stats = analyze_map(state)
    _image, regions = render_stats_chart(stats, 'nearest_starts', return_regions=True)
    assert len(regions) == len(state.starts)
    assert all(region['focus']['kind'] == 'start_player' for region in regions)
    assert all(region['focus']['nearest_player'] for region in regions)

    _image, regions = render_stats_chart(
        stats,
        'ab_summary',
        compare_stats=(stats, stats),
        return_regions=True,
    )
    assert regions
    assert all('focus' not in region for region in regions)
