"""Chargement du profil autonome Continental Legacy."""

from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path


PROFILE_PATH=Path(__file__).resolve().parents[4]/"config"/"generation_profiles"/"continental_legacy_v2.json"
EXTENDED_NATIVE_SIDES=(832,896,960,1024)


def _extend_side_tables(value):
    """Carry the last calibrated side tables into editor-only extensions.

    The active native terrain path does not consume the old procedural tables,
    but the comparison entry point remains public.  Keeping its side-indexed
    maps total prevents a new editor size from failing with a raw KeyError.
    These copied values are deliberately a provisional 768 baseline until the
    larger-size corpus is measured.
    """
    if isinstance(value,dict):
        if '768' in value:
            for side in EXTENDED_NATIVE_SIDES:
                value.setdefault(str(side),deepcopy(value['768']))
        for child in value.values():
            _extend_side_tables(child)
    elif isinstance(value,list):
        for child in value:
            _extend_side_tables(child)
    return value


def load_profile(path:Path|str=PROFILE_PATH)->dict:
    """Load parameters only; reject a runtime native-map dependency."""

    with Path(path).open(encoding="utf-8") as source:
        profile=json.load(source)
    contract=profile.get("runtime_contract",{})
    if contract.get("reads_native_corpus") or contract.get("reads_template_library"):
        raise ValueError("Un profil runtime ne peut pas dépendre du corpus ou de templates")
    return _extend_side_tables(profile)
