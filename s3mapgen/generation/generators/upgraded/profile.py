"""Loader for the independent Upgraded generation profile."""

from __future__ import annotations

import json
from pathlib import Path


PROFILE_PATH = Path(__file__).resolve().parents[4] / "config" / "upgraded_768_v1.json"


def load_profile(path: Path | str = PROFILE_PATH) -> dict:
    with Path(path).open(encoding="utf-8") as source:
        profile = json.load(source)
    if profile.get("profile_kind") != "upgraded":
        raise ValueError("Le profil Upgraded est requis")
    return profile


__all__ = ("PROFILE_PATH", "load_profile")
