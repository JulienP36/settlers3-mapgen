"""Extensible catalogue for the active start-area content packages."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class StartPackageSpec:
    key: str
    label_fr: str
    label_en: str
    stage: str
    layers: tuple[str, ...]
    quota_scope: str
    status: str
    description: str
    label_de: str = ""
    label_es: str = ""
    description_en: str = ""
    description_de: str = ""
    description_es: str = ""

    @property
    def implemented(self) -> bool:
        return self.status == "active"

    def label(self, language: str = "fr") -> str:
        return {
            "fr": self.label_fr,
            "en": self.label_en,
            "de": self.label_de or self.label_en,
            "es": self.label_es or self.label_en,
        }.get(language, self.label_en)

    def localized_description(self, language: str = "fr") -> str:
        return {
            "fr": self.description,
            "en": self.description_en or self.description,
            "de": self.description_de or self.description_en or self.description,
            "es": self.description_es or self.description_en or self.description,
        }.get(language, self.description_en or self.description)


START_PACKAGE_CATALOG: tuple[StartPackageSpec, ...] = (
    StartPackageSpec(
        "start_forest",
        "Forêt de départ",
        "Start forest",
        "objects.start_forest",
        ("terrain", "objects", "accessibility"),
        "start",
        "active",
        "Arbres adultes et pousses regroupés autour de chaque départ.",
        "Startwald",
        "Bosque inicial",
        "Adult trees and saplings grouped around each start.",
        "Ausgewachsene Bäume und Setzlinge werden um jede Startposition gruppiert.",
        "Árboles adultos y brotes agrupados alrededor de cada inicio.",
    ),
    StartPackageSpec(
        "start_building_stones",
        "Pierres de départ",
        "Start building stones",
        "objects.start_building_stones",
        ("objects", "accessibility"),
        "start",
        "active",
        "Pierres de construction et stock séparés du quota global.",
        "Startbausteine",
        "Piedras de construcción iniciales",
        "Building stones and stock kept separate from the global quota.",
        "Bausteine und Bestand werden vom globalen Kontingent getrennt.",
        "Piedras de construcción y reserva separadas del cupo global.",
    ),
    StartPackageSpec(
        "start_mini_swamp",
        "Mini-marais de départ",
        "Start mini-swamp",
        "biomes.start_mini_swamp",
        ("terrain", "accessibility"),
        "start",
        "active",
        "Petite zone marécageuse cohérente près de chaque départ.",
        "Kleiner Start-Sumpf",
        "Mini-pantano inicial",
        "Small coherent swamp area near each start.",
        "Kleine zusammenhängende Sumpffläche nahe jeder Startposition.",
        "Pequeña zona pantanosa coherente cerca de cada inicio.",
    ),
    StartPackageSpec(
        "start_rocky_minerals",
        "Zone rocheuse minérale",
        "Rocky mineral zone",
        "resources.start_rocky_minerals",
        ("terrain", "resources", "accessibility"),
        "start",
        "active",
        "Mini-zone rocheuse indépendante avec minerais et taux global.",
        "Felsige Mineralzone",
        "Zona rocosa con minerales",
        "Independent small rocky mineral area with the global quantity mean.",
        "Unabhängige kleine felsige Mineralzone mit globaler Mengenmittelung.",
        "Zona rocosa mineral independiente con la media global de cantidad.",
    ),
    StartPackageSpec(
        "start_lake_fish_river",
        "Mini-lac, poissons et rivière",
        "Mini-lake, fish and river",
        "hydrology.start_lake",
        ("terrain", "resources", "accessibility"),
        "start",
        "active",
        "Mini-lac indépendant avec poissons et une rivière légale si possible.",
        "Minisee, Fische und Fluss",
        "Mini-lago, peces y río",
        "Independent mini-lake with fish and a legal river when possible.",
        "Unabhängiger Minisee mit Fischen und legalem Fluss, wenn möglich.",
        "Mini-lago independiente con peces y río legal cuando sea posible.",
    ),
)

_BY_KEY = {item.key: item for item in START_PACKAGE_CATALOG}


def get_start_package(key: str) -> StartPackageSpec:
    try:
        return _BY_KEY[str(key)]
    except KeyError as exc:
        raise ValueError(f"Paquet de bonus de départ inconnu : {key}") from exc


def default_start_package_keys() -> tuple[str, ...]:
    # Start bonuses are opt-in.  The catalogue describes what is available;
    # selecting Legacy or Upgraded must not silently add Custom-only starts.
    return ()


def normalize_start_package_keys(keys) -> tuple[str, ...]:
    """Validate and canonicalize active package IDs.

    Unknown or inactive catalogue entries are ignored so serialized Custom
    configurations remain forward-compatible.
    """

    if keys is None:
        return default_start_package_keys()
    if isinstance(keys, (str, bytes)):
        keys = (keys,)
    result: list[str] = []
    for value in keys:
        key = str(value)
        spec = get_start_package(key)
        if spec.implemented and key not in result:
            result.append(key)
    return tuple(result)


__all__ = (
    "START_PACKAGE_CATALOG",
    "StartPackageSpec",
    "default_start_package_keys",
    "get_start_package",
    "normalize_start_package_keys",
)
