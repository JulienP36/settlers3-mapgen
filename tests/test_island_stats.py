import numpy as np
import pytest

from s3mapgen.application.analysis.core import analyze_map, format_stats_report, stats_csv
from s3mapgen.application.analysis.charts import render_stats_chart
from s3mapgen.application.rendering.focus import _component_mask
from s3mapgen.map_data.model import MapState


def test_island_components_include_shores_rivers_and_lake_holes():
    state = MapState.empty(16)
    state.terrain[2:8, 2:8] = 16
    state.terrain[4:6, 4:6] = 0  # An inland lake does not become another island.
    state.terrain[8, 7] = 48
    state.terrain[9, 7] = 96  # A river is part of the same land mass.
    state.terrain[11:13, 11:13] = 32
    before = state.area.copy()
    stats = analyze_map(state)
    islands = stats['spatial']['islands']
    assert islands['summary']['count'] == 2
    assert [r['cells'] for r in islands['components']] == [34, 4]
    assert sum(r['cells'] for r in islands['components']) == stats['general']['land_cells']
    row = islands['components'][0]
    assert int(_component_mask(state.terrain, 'island', row['id']).sum()) == row['cells']
    assert np.array_equal(state.area, before)
    assert 'island,cells' in stats_csv(stats)


@pytest.mark.parametrize('land', [False, True])
@pytest.mark.parametrize('language', ['fr', 'en', 'de', 'es'])
def test_single_continent_and_empty_sea_have_valid_reports_and_charts(land, language):
    state = MapState.empty(16)
    if land:
        state.terrain[:] = 16
    stats = analyze_map(state)
    summary = stats['spatial']['islands']['summary']
    assert summary['count'] == int(land)
    assert summary['size_distribution']['max'] == (256 if land else 0)
    report = format_stats_report(stats, language)
    title = {'fr': 'ÎLES / CONTINENTS', 'en': 'ISLANDS / CONTINENTS', 'de': 'INSELN / KONTINENTE', 'es': 'ISLAS / CONTINENTES'}[language]
    assert title in report
    image, regions = render_stats_chart(stats, 'island_components', lang=language, return_regions=True)
    assert image.size == (900, 520)
