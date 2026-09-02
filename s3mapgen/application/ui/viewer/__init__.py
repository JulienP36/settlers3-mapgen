"""Viewer-specific presentation data and controls."""

from .labels import (
    MINERAL_NAMES,
    OBJECT_NAMES,
    TERRAIN_NAMES,
    localized_object_name,
    localized_resource_text,
    localized_terrain_name,
)
from .options import HEATMAP_ICON_COLORS, VIEW_CHOICES, VIEW_ICON_COLORS

__all__ = [
    "HEATMAP_ICON_COLORS",
    "MINERAL_NAMES",
    "OBJECT_NAMES",
    "TERRAIN_NAMES",
    "localized_object_name",
    "localized_resource_text",
    "localized_terrain_name",
    "VIEW_CHOICES",
    "VIEW_ICON_COLORS",
]
