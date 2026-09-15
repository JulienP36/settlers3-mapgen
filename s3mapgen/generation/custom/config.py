"""Serializable Custom-generator configuration and parameter catalogues."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from .start_packages import default_start_package_keys, normalize_start_package_keys
from .sections import default_sections, normalize_sections
from ..generators.upgraded.profile import load_profile as load_active_upgraded_profile


_STRUCTURAL_ROOTS = frozenset(
    {"profile_name", "profile_kind", "side", "max_players", "supported_players"}
)
_REMOVED_CUSTOM_PATHS = frozenset(
    {
        # These are engine invariants, not Custom controls.  The protected
        # Legacy/Upgraded source profiles keep their historical entries; only
        # the editable Custom derivative is sanitized.
        "river.stop_at_first_water",
        "river.fish_forbidden",
        "water.cleanup_micro_water",
        "water.border_must_have_gradient",
    }
)
_REMOVED_CUSTOM_LEAF_KEYS = frozenset()
_HIDDEN_PARAMETER_LEAF_KEYS = frozenset({"name"})
_PROJECT_ROOT = Path(__file__).resolve().parents[3]
_LEGACY_PROFILE = _PROJECT_ROOT / "config" / "legacy_768_v1.json"


def canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        default=str,
    )


def profile_digest(value: Any) -> str:
    """Return a stable SHA-256 identity for a profile or config payload."""

    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def deep_merge(base: Mapping[str, Any], overlay: Mapping[str, Any]) -> dict[str, Any]:
    """Deep-copy ``base`` and recursively apply a declarative overlay."""

    result = deepcopy(dict(base))
    for key, value in overlay.items():
        if isinstance(value, Mapping) and isinstance(result.get(key), Mapping):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = deepcopy(value)
    return result


def get_path(value: Mapping[str, Any], path: tuple[str, ...] | list[str] | str) -> Any:
    parts = tuple(path.split(".")) if isinstance(path, str) else tuple(path)
    current: Any = value
    for part in parts:
        if not isinstance(current, Mapping) or part not in current:
            raise KeyError(".".join(parts))
        current = current[part]
    return current


def set_path(value: Mapping[str, Any], path, new_value: Any) -> dict[str, Any]:
    """Return a copied mapping with one dotted path replaced."""

    parts = tuple(path.split(".")) if isinstance(path, str) else tuple(path)
    if not parts:
        raise ValueError("Un chemin de paramètre ne peut pas être vide")
    result = deepcopy(dict(value))
    current: dict[str, Any] = result
    for part in parts[:-1]:
        child = current.get(part)
        if not isinstance(child, Mapping):
            child = {}
            current[part] = child
        else:
            child = deepcopy(dict(child))
            current[part] = child
        current = child
    current[parts[-1]] = deepcopy(new_value)
    return result


def _humanize(part: str) -> str:
    return part.replace("_", " ").capitalize()


def sanitize_custom_profile(profile: Mapping[str, Any]) -> dict[str, Any]:
    """Return the editable profile without the removed invariant switches.

    The built-in JSON files are deliberately not rewritten: their hashes are
    part of the validated generator contract.  Custom receives a clean copy
    instead, so the removed switches cannot reappear through a serialized
    Custom configuration.  Family ``name`` values remain internal metadata
    because validators use them for readable rule IDs; they are simply not
    exposed as editable controls.
    """

    def walk(value: Any, path: tuple[str, ...] = ()) -> Any:
        if isinstance(value, Mapping):
            result: dict[str, Any] = {}
            for key, child in value.items():
                key_text = str(key)
                child_path = path + (key_text,)
                if key_text in _REMOVED_CUSTOM_LEAF_KEYS:
                    continue
                if ".".join(child_path) in _REMOVED_CUSTOM_PATHS:
                    continue
                result[key_text] = walk(child, child_path)
            return result
        if isinstance(value, list):
            return [walk(item, path) for item in value]
        return deepcopy(value)

    return walk(profile)


@dataclass(frozen=True, slots=True)
class ParameterDescriptor:
    """Metadata used by both the editor and future non-Tk frontends."""

    path: tuple[str, ...]
    value_type: str
    default: Any
    group: str
    label: str
    editable: bool = True

    @property
    def key(self) -> str:
        return ".".join(self.path)


def iter_parameter_descriptors(
    profile: Mapping[str, Any],
    *,
    include_structural: bool = False,
) -> tuple[ParameterDescriptor, ...]:
    """Enumerate scalar profile leaves without hardcoding a schema list.

    Arrays and objects remain editable through the raw JSON editor.  Scalar
    leaves get first-class controls, which makes a newly added profile field
    visible automatically without a code change in the UI.
    """

    result: list[ParameterDescriptor] = []

    def walk(value: Any, path: tuple[str, ...]) -> None:
        if isinstance(value, Mapping):
            for key, child in value.items():
                if str(key).startswith("_"):
                    continue
                walk(child, path + (str(key),))
            return
        if isinstance(value, list):
            return
        if value is None or not isinstance(value, (bool, int, float, str)):
            return
        if not path or path[-1] in _HIDDEN_PARAMETER_LEAF_KEYS:
            return
        if not include_structural and path[0] in _STRUCTURAL_ROOTS:
            return
        value_type = (
            "bool" if isinstance(value, bool)
            else "int" if isinstance(value, int)
            else "float" if isinstance(value, float)
            else "str"
        )
        group = _humanize(path[0])
        result.append(
            ParameterDescriptor(
                path=path,
                value_type=value_type,
                default=value,
                group=group,
                label=" / ".join(_humanize(part) for part in path),
            )
        )

    walk(profile, ())
    return tuple(result)


def load_preset_profile(
    mode: str,
    *,
    legacy_path: Path | str | None = None,
    upgraded_path: Path | str | None = None,
) -> dict[str, Any]:
    """Load the editable profile paired with a built-in generator."""

    key = str(mode)
    if key == "legacy":
        path = Path(legacy_path) if legacy_path is not None else _LEGACY_PROFILE
        expected = "legacy"
    elif key == "upgraded":
        if upgraded_path is None:
            return sanitize_custom_profile(load_active_upgraded_profile())
        path = Path(upgraded_path)
        expected = "upgraded"
    else:
        raise ValueError(f"Un preset de base Custom doit être Legacy ou Upgraded : {mode}")
    with path.open(encoding="utf-8") as source:
        profile = json.load(source)
    if not isinstance(profile, dict) or profile.get("profile_kind") != expected:
        raise ValueError(f"Le profil {key} est absent ou incompatible : {path}")
    return sanitize_custom_profile(profile)


@dataclass(frozen=True, slots=True)
class CustomGenerationConfig:
    """Immutable value object carried from UI/cache into a generator."""

    base_mode: str
    base_archetype: str
    profile: dict[str, Any]
    start_packages: tuple[str, ...] | None = None
    schema_version: int = 2
    sections: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.base_mode not in {"legacy", "upgraded"}:
            raise ValueError("Le mode de base Custom doit être Legacy ou Upgraded")
        if not self.base_archetype:
            raise ValueError("L’archétype de base Custom est requis")
        if not isinstance(self.profile, dict):
            raise TypeError("Le profil Custom doit être un objet JSON")
        if not isinstance(self.sections, Mapping):
            raise TypeError("Les sections Custom doivent être un objet JSON")
        packages = normalize_start_package_keys(self.start_packages)
        object.__setattr__(self, "profile", sanitize_custom_profile(self.profile))
        object.__setattr__(self, "start_packages", packages)
        object.__setattr__(self, "sections", deepcopy(dict(self.sections)))

    @property
    def digest(self) -> str:
        return profile_digest(self.to_dict())

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": int(self.schema_version),
            "base_mode": self.base_mode,
            "base_archetype": self.base_archetype,
            "profile": deepcopy(self.profile),
            "start_packages": list(self.start_packages),
            "sections": deepcopy(self.sections),
        }

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> "CustomGenerationConfig":
        if "profile" not in value:
            raise ValueError("Une configuration Custom doit contenir profile")
        return cls(
            base_mode=str(value.get("base_mode", "upgraded")),
            base_archetype=str(value.get("base_archetype", "continental")),
            profile=deepcopy(dict(value["profile"])),
            start_packages=(
                tuple(value["start_packages"])
                if "start_packages" in value
                else default_start_package_keys()
            ),
            schema_version=int(value.get("schema_version", 1)),
            sections=deepcopy(dict(value.get("sections", {})))
            if isinstance(value.get("sections", {}), Mapping)
            else {},
        )

    def with_value(self, path, value: Any) -> "CustomGenerationConfig":
        return CustomGenerationConfig(
            self.base_mode,
            self.base_archetype,
            set_path(self.profile, path, value),
            self.start_packages,
            self.schema_version,
            self.sections,
        )

    def with_start_packages(self, keys) -> "CustomGenerationConfig":
        return CustomGenerationConfig(
            self.base_mode,
            self.base_archetype,
            self.profile,
            tuple(keys),
            self.schema_version,
            self.sections,
        )

    def with_sections(self, sections: Mapping[str, Any]) -> "CustomGenerationConfig":
        """Return a copy with the curated user-facing sections replaced."""

        return CustomGenerationConfig(
            self.base_mode,
            self.base_archetype,
            self.profile,
            self.start_packages,
            self.schema_version,
            deepcopy(dict(sections)),
        )

    def semantic_sections(self) -> dict[str, Any]:
        """Return the complete bounded section model used by the engines."""

        fallback = default_sections(self.profile, self.base_mode)
        return normalize_sections(self.sections or fallback, fallback=fallback)

    def runtime_profile(self, *, execution_kind: str = "custom") -> dict[str, Any]:
        """Return a profile copy with the shared Custom-route metadata.

        Built-in Legacy and Upgraded selections are represented by the same
        runtime contract as editable Custom profiles.  ``preset`` keeps the
        public mode label and native output provenance while still travelling
        through that common route; ``custom`` means that the user changed the
        declarative profile or activated a start package.
        """

        if execution_kind not in {"custom", "preset"}:
            raise ValueError("execution_kind doit être 'custom' ou 'preset'")

        profile = deepcopy(self.profile)
        profile["_custom_runtime"] = {
            "execution_kind": execution_kind,
            "schema_version": int(self.schema_version),
            "base_mode": self.base_mode,
            "base_archetype": self.base_archetype,
            "configuration_digest": self.digest,
            "start_packages": list(self.start_packages),
            # A package toggle is itself a Custom change.  Materialize the
            # semantic sections even when no scalar field has been edited yet;
            # this is what lets a Legacy-derived Custom profile activate a
            # start bonus instead of silently falling back to the native path.
            "sections": (
                self.semantic_sections()
                if self.sections or self.start_packages
                else {}
            ),
        }
        return profile


def build_custom_config(
    base_mode: str = "upgraded",
    base_archetype: str = "continental",
    *,
    profile: Mapping[str, Any] | None = None,
    legacy_path: Path | str | None = None,
    upgraded_path: Path | str | None = None,
    start_packages=None,
    sections: Mapping[str, Any] | None = None,
) -> CustomGenerationConfig:
    selected = (
        deepcopy(dict(profile))
        if profile is not None
        else load_preset_profile(
            base_mode,
            legacy_path=legacy_path,
            upgraded_path=upgraded_path,
        )
    )
    return CustomGenerationConfig(
        str(base_mode),
        str(base_archetype),
        selected,
        tuple(start_packages) if start_packages is not None else default_start_package_keys(),
        2,
        deepcopy(dict(sections)) if isinstance(sections, Mapping) else {},
    )


__all__ = (
    "CustomGenerationConfig",
    "ParameterDescriptor",
    "build_custom_config",
    "canonical_json",
    "deep_merge",
    "get_path",
    "iter_parameter_descriptors",
    "load_preset_profile",
    "default_sections",
    "normalize_sections",
    "profile_digest",
    "sanitize_custom_profile",
    "set_path",
)
