"""Loader for the active independent Upgraded generation profile."""

from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

from .profile_defaults import active_upgraded_profile

def load_profile(path: Path | str | None = None) -> dict:
    """Return active defaults, optionally loading an explicit override."""

    if path is None:
        profile = active_upgraded_profile()
    else:
        with Path(path).open(encoding="utf-8") as source:
            profile = deepcopy(json.load(source))
    if not isinstance(profile, dict) or profile.get("profile_kind") != "upgraded":
        raise ValueError("Le profil Upgraded est requis")
    return profile


__all__ = ("load_profile",)
