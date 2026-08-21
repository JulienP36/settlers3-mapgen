from __future__ import annotations

from .stats_analysis import analyze_map, format_stats_report, stats_json, stats_csv


def summarize(state):
    """Compatibility facade: return the new complete statistics model."""
    return analyze_map(state)


def format_stats(state, lang='fr'):
    return format_stats_report(analyze_map(state), lang=lang)

__all__=['analyze_map','format_stats_report','stats_json','stats_csv','summarize','format_stats']
