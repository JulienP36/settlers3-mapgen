"""Chargement du profil autonome Continental Legacy."""

from __future__ import annotations

import json
from pathlib import Path


PROFILE_PATH=Path(__file__).resolve().parents[4]/"config"/"generation_profiles"/"continental_legacy_v2.json"


def load_profile(path:Path|str=PROFILE_PATH)->dict:
    """Load parameters only; reject a runtime native-map dependency."""

    with Path(path).open(encoding="utf-8") as source:
        profile=json.load(source)
    contract=profile.get("runtime_contract",{})
    if contract.get("reads_native_corpus") or contract.get("reads_template_library"):
        raise ValueError("Un profil runtime ne peut pas dépendre du corpus ou de templates")
    return profile
