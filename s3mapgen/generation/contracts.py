"""Neutral application contract returned by concrete map generators."""

from __future__ import annotations

from dataclasses import dataclass

from ..map_data.model import MapState
from .rules import ValidationResult


@dataclass
class GenerationOutput:
    """Generated/imported state plus validation and progress information."""

    state: MapState
    validations: list[ValidationResult]
    stage_log: list[str]
