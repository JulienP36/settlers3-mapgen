"""Runtime translations for the data-driven Custom parameter editor."""

from __future__ import annotations

from typing import Any


_WORDS = {
    "fr": {
        "river": "Rivière", "water": "Eau", "fish": "Poissons", "minerals": "Minerais",
        "snow": "Neige", "trees": "Arbres", "building_stones": "Pierres de construction",
        "decor": "Décorations", "starts": "Départs", "start_bonus": "Bonus de départ",
        "upgraded_rules": "Règles Upgraded", "families": "Familles", "shares": "Répartition",
        "practical": "Pratique", "max": "Max", "cells": "Cellules", "apply": "Appliquer",
        "trim": "Rogner", "scale": "Échelle", "slope": "Pente", "intercept": "Ordonnée",
        "rare": "Rare", "tail": "Queue", "straight": "Droit", "run": "Segment",
        "terrain": "Terrain", "ids": "Identifiants", "target": "Cible", "bands": "Bandes",
        "shore": "Rive", "hex": "Hexagones", "distance": "Distance", "quantity": "Quantité",
        "multiplier": "Multiplicateur", "cap": "Plafond", "edge": "Bord", "not": "Non",
        "rocky": "Rocheux", "accessible": "Accessible", "occupancy": "Occupation",
        "blob": "Zone", "size": "Taille", "shape": "Forme", "variant": "Variante",
        "space": "Espace", "aspect": "Proportions", "adult": "Adultes", "weights": "Poids",
        "global": "Global", "start": "Départ", "bonus": "Bonus", "small": "Petites pousses",
        "tree": "Arbre", "separate": "Séparé", "pool": "Réserve", "palm": "Palmiers",
        "forest": "Forêt", "centers": "Centres", "radius": "Rayon", "min": "Min",
        "cluster": "Groupe", "share": "Part", "center": "Centre", "requested": "Demandé",
        "placed": "Placé", "building": "Construction", "stone": "Pierre", "active": "Actifs",
        "exhausted": "Épuisée", "buildable": "Constructible", "anchor": "Point", "stock": "Stock",
        "fullness": "Remplissage", "footprint": "Emprise", "desert": "Désert", "swamp": "Marais",
        "reed": "Roseaux", "decorative": "Décoratives", "forbid": "Interdire", "objects": "Objets",
        "mountain": "Montagne", "initial": "Initial", "territory": "Territoire", "technical": "Technique",
        "clear": "Dégagement", "height": "Hauteur", "range": "Plage", "immediate": "Immédiat",
        "delta": "Écart", "sum": "Somme", "editor": "Éditeur", "outside": "Hors", "content": "Contenu",
        "restored": "Restauré", "first": "Premier", "after": "Après", "final": "Final",
        "hydrology": "Hydrologie", "deep": "Profond", "coast": "Côte", "straight": "Droit",
    },
    "en": {
        "river": "River", "water": "Water", "fish": "Fish", "minerals": "Minerals", "snow": "Snow",
        "trees": "Trees", "building_stones": "Building stones", "decor": "Decorations", "starts": "Starts",
        "start_bonus": "Start bonuses", "upgraded_rules": "Upgraded rules", "families": "Families",
        "shares": "Shares", "practical": "Practical", "max": "Max", "cells": "Cells", "apply": "Apply",
        "trim": "Trim", "scale": "Scale", "slope": "Slope", "intercept": "Intercept", "rare": "Rare",
        "tail": "Tail", "straight": "Straight", "run": "Run", "terrain": "Terrain", "ids": "IDs",
        "target": "Target", "bands": "Bands", "shore": "Shore", "hex": "Hex", "distance": "Distance",
        "quantity": "Quantity", "multiplier": "Multiplier", "cap": "Cap", "edge": "Edge", "not": "Not",
        "rocky": "Rocky", "accessible": "Accessible", "occupancy": "Occupancy", "blob": "Blob",
        "size": "Size", "shape": "Shape", "variant": "Variant", "space": "Space", "aspect": "Aspect",
        "adult": "Adult", "weights": "Weights", "global": "Global", "start": "Start", "bonus": "Bonus",
        "small": "Small", "tree": "Tree", "separate": "Separate", "pool": "Pool", "palm": "Palm",
        "forest": "Forest", "centers": "Centers", "radius": "Radius", "min": "Min", "cluster": "Cluster",
        "share": "Share", "center": "Center", "requested": "Requested", "placed": "Placed", "building": "Building",
        "stone": "Stone", "active": "Active", "exhausted": "Exhausted", "buildable": "Buildable", "anchor": "Anchor",
        "stock": "Stock", "fullness": "Fullness", "footprint": "Footprint", "desert": "Desert", "swamp": "Swamp",
        "reed": "Reed", "decorative": "Decorative", "forbid": "Forbid", "objects": "Objects", "mountain": "Mountain",
        "initial": "Initial", "territory": "Territory", "technical": "Technical", "clear": "Clearance", "height": "Height",
        "range": "Range", "immediate": "Immediate", "delta": "Delta", "sum": "Sum", "editor": "Editor",
        "outside": "Outside", "content": "Content", "restored": "Restored", "first": "First", "after": "After",
        "final": "Final", "hydrology": "Hydrology", "deep": "Deep", "coast": "Coast",
    },
    "de": {
        "river": "Fluss", "water": "Wasser", "fish": "Fische", "minerals": "Mineralien", "snow": "Schnee",
        "trees": "Bäume", "building_stones": "Bausteine", "decor": "Dekorationen", "starts": "Startpositionen",
        "start_bonus": "Startboni", "upgraded_rules": "Upgraded-Regeln", "families": "Familien", "shares": "Anteile",
        "practical": "Praktisch", "max": "Max", "cells": "Zellen", "apply": "Anwenden", "trim": "Kürzen",
        "scale": "Skalierung", "slope": "Steigung", "intercept": "Achsenabschnitt", "rare": "Selten", "tail": "Rand",
        "straight": "Gerade", "run": "Lauf", "terrain": "Terrain", "ids": "IDs", "target": "Ziel", "bands": "Bänder",
        "shore": "Ufer", "hex": "Hex", "distance": "Abstand", "quantity": "Menge", "multiplier": "Multiplikator",
        "cap": "Obergrenze", "edge": "Rand", "not": "Nicht", "rocky": "Felsig", "accessible": "Zugänglich",
        "occupancy": "Belegung", "blob": "Zone", "size": "Größe", "shape": "Form", "variant": "Variante",
        "space": "Raum", "aspect": "Seitenverhältnis", "adult": "Ausgewachsen", "weights": "Gewichte", "global": "Global",
        "start": "Start", "bonus": "Bonus", "small": "Klein", "tree": "Baum", "separate": "Getrennt", "pool": "Pool",
        "palm": "Palmen", "forest": "Wald", "centers": "Zentren", "radius": "Radius", "min": "Min", "cluster": "Gruppe",
        "share": "Anteil", "center": "Mitte", "requested": "Angefordert", "placed": "Platziert", "building": "Bau",
        "stone": "Stein", "active": "Aktiv", "exhausted": "Erschöpft", "buildable": "Baubar", "anchor": "Anker",
        "stock": "Bestand", "fullness": "Füllung", "footprint": "Grundfläche", "desert": "Wüste", "swamp": "Sumpf",
        "reed": "Schilf", "decorative": "Dekorativ", "forbid": "Verbieten", "objects": "Objekte", "mountain": "Berg",
        "initial": "Initial", "territory": "Gebiet", "technical": "Technisch", "clear": "Freiraum", "height": "Höhe",
        "range": "Bereich", "immediate": "Unmittelbar", "delta": "Differenz", "sum": "Summe", "editor": "Editor",
        "outside": "Außerhalb", "content": "Inhalt", "restored": "Wiederhergestellt", "first": "Zuerst", "after": "Nach",
        "final": "Final", "hydrology": "Hydrologie", "deep": "Tief", "coast": "Küste",
    },
    "es": {
        "river": "Río", "water": "Agua", "fish": "Peces", "minerals": "Minerales", "snow": "Nieve",
        "trees": "Árboles", "building_stones": "Piedras de construcción", "decor": "Decoración", "starts": "Inicios",
        "start_bonus": "Bonificaciones iniciales", "upgraded_rules": "Reglas Upgraded", "families": "Familias", "shares": "Reparto",
        "practical": "Práctico", "max": "Máx", "cells": "Celdas", "apply": "Aplicar", "trim": "Recortar", "scale": "Escala",
        "slope": "Pendiente", "intercept": "Intersección", "rare": "Rara", "tail": "Cola", "straight": "Recto", "run": "Tramo",
        "terrain": "Terreno", "ids": "IDs", "target": "Objetivo", "bands": "Bandas", "shore": "Orilla", "hex": "Hex",
        "distance": "Distancia", "quantity": "Cantidad", "multiplier": "Multiplicador", "cap": "Límite", "edge": "Borde",
        "not": "No", "rocky": "Rocoso", "accessible": "Accesible", "occupancy": "Ocupación", "blob": "Zona", "size": "Tamaño",
        "shape": "Forma", "variant": "Variante", "space": "Espacio", "aspect": "Proporción", "adult": "Adulto", "weights": "Pesos",
        "global": "Global", "start": "Inicio", "bonus": "Bono", "small": "Pequeño", "tree": "Árbol", "separate": "Separada",
        "pool": "Reserva", "palm": "Palmeras", "forest": "Bosque", "centers": "Centros", "radius": "Radio", "min": "Mín",
        "cluster": "Grupo", "share": "Parte", "center": "Centro", "requested": "Solicitado", "placed": "Colocado", "building": "Construcción",
        "stone": "Piedra", "active": "Activos", "exhausted": "Agotada", "buildable": "Construible", "anchor": "Punto", "stock": "Stock",
        "fullness": "Relleno", "footprint": "Huella", "stock": "Stock", "desert": "Desierto", "swamp": "Pantano", "reed": "Juncos", "decorative": "Decorativa",
        "forbid": "Prohibir", "objects": "Objetos", "mountain": "Montaña", "initial": "Inicial", "territory": "Territorio",
        "technical": "Técnico", "clear": "Despeje", "height": "Altura", "range": "Rango", "immediate": "Inmediato", "delta": "Diferencia",
        "sum": "Suma", "editor": "Editor", "outside": "Fuera", "content": "Contenido", "restored": "Restaurado", "first": "Primero",
        "after": "Después", "final": "Final", "hydrology": "Hidrología", "deep": "Profunda", "coast": "Costa",
    },
}


def _token_label(token: str, language: str) -> str:
    if token.isdigit():
        return token
    words = _WORDS.get(language, _WORDS["en"])
    if token in words:
        return words[token]
    return " ".join(words.get(part, part) for part in token.split("_"))


def parameter_group(path: tuple[str, ...], language: str) -> str:
    return _token_label(path[0], language) if path else ""


def parameter_label(path: tuple[str, ...], language: str) -> str:
    return " / ".join(_token_label(part, language) for part in path)


_ARCHETYPE_DESCRIPTIONS = {
    "continental": {
        "fr": "Macro-topologie : une masse terrestre principale avec océan périphérique.",
        "en": "Macro-topology: one main landmass with a surrounding ocean.",
        "de": "Makrotopologie: eine Hauptlandmasse mit umgebendem Ozean.",
        "es": "Macrotopología: una masa terrestre principal con océano periférico.",
    },
    "large_islands": {
        "fr": "Macro-topologie : plusieurs grandes masses insulaires.",
        "en": "Macro-topology: several large island landmasses.",
        "de": "Makrotopologie: mehrere große Inselmassen.",
        "es": "Macrotopología: varias grandes masas insulares.",
    },
    "small_islands": {
        "fr": "Macro-topologie : nombreuses petites masses insulaires.",
        "en": "Macro-topology: many small island landmasses.",
        "de": "Makrotopologie: viele kleine Inselmassen.",
        "es": "Macrotopología: numerosas pequeñas masas insulares.",
    },
}


def archetype_description(key: str, language: str) -> str:
    descriptions = _ARCHETYPE_DESCRIPTIONS.get(key, {})
    return descriptions.get(language, descriptions.get("en", key))


_CUSTOM_SECTION_TEXT = {
    "start_bonus": {
        "fr": "Réglages détaillés des bonus de départ", "en": "Detailed start-bonus settings", "de": "Detaillierte Startbonus-Einstellungen", "es": "Ajustes detallados de las bonificaciones iniciales",
    },
    "trees": {
        "fr": "Arbres", "en": "Trees", "de": "Bäume", "es": "Árboles",
    },
    "building_stones": {
        "fr": "Pierres de construction", "en": "Building stones", "de": "Bausteine", "es": "Piedras de construcción",
    },
    "decorations": {
        "fr": "Décorations", "en": "Decorations", "de": "Dekorationen", "es": "Decoraciones",
    },
    "decoration_hint": {
        "fr": "100 % = profil sélectionné.", "en": "100% = selected profile.", "de": "100 % = gewähltes Profil.", "es": "100 % = perfil seleccionado.",
    },
    "objects_grass_compatible": {
        "fr": "Autoriser les objets compatibles avec l’herbe sur Herbe sèche et Détails herbe 1 & 2",
        "en": "Allow grass-compatible objects on Dry grass and Grass details 1 & 2",
        "de": "Graskompatible Objekte auf trockenem Gras und Grasdetails 1 & 2 erlauben",
        "es": "Permitir objetos compatibles con hierba sobre Hierba seca y Detalles de hierba 1 y 2",
    },
    "decoration_big_stones": {
        "fr": "Gros rochers", "en": "Large rocks", "de": "Große Felsen", "es": "Rocas grandes",
    },
    "decoration_decorative_stones": {
        "fr": "Pierres décoratives", "en": "Decorative stones", "de": "Dekorative Steine", "es": "Piedras decorativas",
    },
    "decoration_border_stones": {
        "fr": "Pierres de bordure", "en": "Border stones", "de": "Randsteine", "es": "Piedras de borde",
    },
    "decoration_small_stones": {
        "fr": "Petites pierres", "en": "Small stones", "de": "Kleine Steine", "es": "Piedras pequeñas",
    },
    "decoration_bushes": {
        "fr": "Buissons", "en": "Bushes", "de": "Büsche", "es": "Arbustos",
    },
    "decoration_cacti": {
        "fr": "Cactus", "en": "Cacti", "de": "Kakteen", "es": "Cactus",
    },
    "decoration_dead_trees": {
        "fr": "Arbres morts", "en": "Dead trees", "de": "Tote Bäume", "es": "Árboles muertos",
    },
    "decoration_graves": {
        "fr": "Tombes", "en": "Graves", "de": "Gräber", "es": "Tumbas",
    },
    "decoration_skeletons": {
        "fr": "Squelettes", "en": "Skeletons", "de": "Skelette", "es": "Esqueletos",
    },
    "decoration_small_bushes": {
        "fr": "Petits buissons", "en": "Small bushes", "de": "Kleine Büsche", "es": "Arbustos pequeños",
    },
    "decoration_small_flowers": {
        "fr": "Petites fleurs", "en": "Small flowers", "de": "Kleine Blumen", "es": "Flores pequeñas",
    },
    "decoration_small_plants": {
        "fr": "Petites plantes", "en": "Small plants", "de": "Kleine Pflanzen", "es": "Plantas pequeñas",
    },
    "decoration_stumps": {
        "fr": "Souches", "en": "Stumps", "de": "Baumstümpfe", "es": "Tocones",
    },
    "decoration_toadstools": {
        "fr": "Champignons", "en": "Toadstools", "de": "Pilze", "es": "Hongos",
    },
    "decoration_wrecks": {
        "fr": "Épaves", "en": "Wrecks", "de": "Wracks", "es": "Naufragios",
    },
    "decoration_reeds": {
        "fr": "Roseaux", "en": "Reeds", "de": "Schilf", "es": "Juncos",
    },
    "decoration_reefs": {
        "fr": "Récifs", "en": "Reefs", "de": "Riffe", "es": "Arrecifes",
    },
    "minerals": {
        "fr": "Minerais", "en": "Minerals", "de": "Mineralien", "es": "Minerales",
    },
    "fish": {
        "fr": "Poissons", "en": "Fish", "de": "Fische", "es": "Peces",
    },
    "rivers": {
        "fr": "Rivières", "en": "Rivers", "de": "Flüsse", "es": "Ríos",
    },
    "river_rate": {
        "fr": "Taux global de rivières", "en": "Global river rate", "de": "Globale Flussrate", "es": "Tasa global de ríos",
    },
    "river_hint": {
        "fr": "0 % = aucune rivière ; 100 % = profil sélectionné. Tracé et connexions natifs.",
        "en": "0% = no rivers; 100% = selected profile. Native paths and connections.",
        "de": "0 % = keine Flüsse; 100 % = gewähltes Profil. Native Wege und Verbindungen.",
        "es": "0 % = ningún río; 100 % = perfil seleccionado. Trazado y conexiones nativos.",
    },
    "terrains": {
        "fr": "Terrains", "en": "Terrain", "de": "Terrain", "es": "Terrenos",
    },
    "terrain_mud": {
        "fr": "Boue", "en": "Mud", "de": "Schlamm", "es": "Barro",
    },
    "terrain_desert": {
        "fr": "Désert", "en": "Desert", "de": "Wüste", "es": "Desierto",
    },
    "terrain_dry_grass": {
        "fr": "Herbe sèche", "en": "Dry grass", "de": "Trockenes Gras", "es": "Hierba seca",
    },
    "terrain_details": {
        "fr": "Détails décoratifs", "en": "Decorative details", "de": "Dekorative Details", "es": "Detalles decorativos",
    },
    "terrain_swamp": {
        "fr": "Marais", "en": "Swamp", "de": "Sumpf", "es": "Pantano",
    },
    "terrain_hint": {
        "fr": "Les lacs, la neige et le relief rocheux restent liés au moteur sélectionné.",
        "en": "Lakes, snow and rocky relief remain tied to the selected engine.",
        "de": "Seen, Schnee und felsiges Relief bleiben an die gewählte Engine gebunden.",
        "es": "Los lagos, la nieve y el relieve rocoso siguen ligados al motor seleccionado.",
    },
    "mineral_algorithm": {
        "fr": "Méthode de gisement", "en": "Deposit method", "de": "Lagerstättenmethode", "es": "Método de yacimiento",
    },
    "occupancy_percent": {
        "fr": "Occupation", "en": "Occupancy", "de": "Belegung", "es": "Ocupación",
    },
    "mineral_shares": {
        "fr": "Répartition", "en": "Distribution", "de": "Verteilung", "es": "Reparto",
    },
    "size_variation": {
        "fr": "Variation de taille", "en": "Size variation", "de": "Größenvariation", "es": "Variación de tamaño",
    },
    "average_quantity": {
        "fr": "Ressource moyenne", "en": "Average resource", "de": "Durchschnittliche Ressource", "es": "Recurso medio",
    },
    "fill_percent": {
        "fr": "Remplissage", "en": "Fill", "de": "Füllung", "es": "Relleno",
    },
    "near_shore": {
        "fr": "Près des côtes", "en": "Near shore", "de": "Küstennah", "es": "Cerca de la costa",
    },
    "band_thickness": {
        "fr": "Épaisseur", "en": "Thickness", "de": "Dicke", "es": "Grosor",
    },
    "tree_base_quota": {
        "fr": "Quota global d’arbres de base", "en": "Global base-tree quota", "de": "Globales Grundbaumkontingent", "es": "Cupo global de árboles base",
    },
    "tree_saplings": {
        "fr": "Pousses", "en": "Saplings", "de": "Setzlinge", "es": "Retoños",
    },
    "tree_saplings_enabled": {
        "fr": "Pousses acceptées", "en": "Saplings enabled", "de": "Setzlinge aktiv", "es": "Retoños activados",
    },
    "tree_saplings_global_pool": {
        "fr": "Font partie du quota global", "en": "Part of the global pool", "de": "Teil des globalen Pools", "es": "Parte del cupo global",
    },
    "tree_saplings_global_share": {
        "fr": "Part du quota global réservée aux pousses", "en": "Global-pool share reserved for saplings", "de": "Globaler Poolanteil für Setzlinge", "es": "Parte del cupo global reservada a retoños",
    },
    "tree_saplings_separate_quota": {
        "fr": "Quota séparé des pousses", "en": "Separate sapling quota", "de": "Separates Setzlingskontingent", "es": "Cupo separado de retoños",
    },
    "tree_saplings_placement": {
        "fr": "Répartition des pousses", "en": "Sapling placement", "de": "Setzlingsverteilung", "es": "Distribución de retoños",
    },
    "tree_placement_everywhere": {
        "fr": "Partout", "en": "Everywhere", "de": "Überall", "es": "En todas partes",
    },
    "tree_placement_forests_only": {
        "fr": "Forêts seulement", "en": "Forests only", "de": "Nur in Wäldern", "es": "Solo en bosques",
    },
    "tree_placement_outside_forests": {
        "fr": "Hors des forêts", "en": "Outside forests", "de": "Außerhalb der Wälder", "es": "Fuera de los bosques",
    },
    "tree_forests": {
        "fr": "Forêts", "en": "Forests", "de": "Wälder", "es": "Bosques",
    },
    "tree_forests_enabled": {
        "fr": "Forêts activées", "en": "Forests enabled", "de": "Wälder aktiviert", "es": "Bosques activados",
    },
    "tree_forest_share": {
        "fr": "Part en forêts", "en": "Forest share", "de": "Waldanteil", "es": "Parte en bosques",
    },
    "tree_forest_average": {
        "fr": "Nombre moyen d’arbres par forêt", "en": "Average trees per forest", "de": "Durchschnittliche Bäume je Wald", "es": "Promedio de árboles por bosque",
    },
    "tree_forest_variation": {
        "fr": "Variation du nombre d’arbres", "en": "Tree-count variation", "de": "Variation der Baumanzahl", "es": "Variación del número de árboles",
    },
    "tree_palm_quota": {
        "fr": "Quota maximal de palmiers", "en": "Maximum palm quota", "de": "Maximales Palmenkontingent", "es": "Cupo máximo de palmeras",
    },
    "tree_hint": {
        "fr": "Les quotas sont relatifs au profil sélectionné. Les bonus de départ seront traités séparément.",
        "en": "Quotas are relative to the selected profile. Start bonuses will be handled separately.",
        "de": "Kontingente beziehen sich auf das gewählte Profil. Startboni werden getrennt behandelt.",
        "es": "Los cupos son relativos al perfil seleccionado. Las bonificaciones iniciales se tratarán aparte.",
    },
    "building_stone_anchor_density": {
        "fr": "Quota global de pierres", "en": "Global stone quota", "de": "Globales Steinkontingent", "es": "Cupo global de piedras",
    },
    "building_stone_groups_enabled": {
        "fr": "Groupes activés", "en": "Enable groups", "de": "Gruppen aktivieren", "es": "Activar grupos",
    },
    "building_stone_average": {
        "fr": "Stock moyen par pierre", "en": "Average stock per stone", "de": "Durchschnittlicher Vorrat je Stein", "es": "Reserva media por piedra",
    },
    "building_stone_groups": {
        "fr": "Groupes", "en": "Groups", "de": "Gruppen", "es": "Grupos",
    },
    "building_stone_group_share": {
        "fr": "Part du quota en groupes", "en": "Share of quota in groups", "de": "Anteil des Kontingents in Gruppen", "es": "Parte del cupo en grupos",
    },
    "building_stone_group_average": {
        "fr": "Nombre moyen de pierres par groupe", "en": "Average stones per group", "de": "Durchschnittliche Steine je Gruppe", "es": "Promedio de piedras por grupo",
    },
    "building_stone_group_variation": {
        "fr": "Variation du nombre de pierres", "en": "Stone-count variation", "de": "Variation der Steinanzahl", "es": "Variación del número de piedras",
    },
    "stone_unit": {
        "fr": "unités", "en": "units", "de": "Einheiten", "es": "unidades",
    },
    "stones_unit": {
        "fr": "pierres", "en": "stones", "de": "Steine", "es": "piedras",
    },
    "building_stone_hint": {
        "fr": "100 % = profil sélectionné ; bonus de départ séparés.",
        "en": "100% = selected profile; start bonuses are separate.",
        "de": "100 % = gewähltes Profil; Startboni bleiben getrennt.",
        "es": "100 % = perfil seleccionado; las bonificaciones iniciales son independientes.",
    },
    "low": {"fr": "Faible", "en": "Low", "de": "Gering", "es": "Baja"},
    "normal": {"fr": "Normale", "en": "Normal", "de": "Normal", "es": "Normal"},
    "high": {"fr": "Forte", "en": "High", "de": "Hoch", "es": "Alta"},
    "legacy_algorithm": {"fr": "Legacy", "en": "Legacy", "de": "Legacy", "es": "Legacy"},
    "upgraded_algorithm": {"fr": "Upgraded", "en": "Upgraded", "de": "Upgraded", "es": "Upgraded"},
    "random_algorithm": {"fr": "Pixels aléatoires", "en": "Random pixels", "de": "Zufällige Pixel", "es": "Píxeles aleatorios"},
    "percent_unit": {"fr": "%", "en": "%", "de": "%", "es": "%"},
    "trees_unit": {"fr": "arbres", "en": "trees", "de": "Bäume", "es": "árboles"},
    "cells_unit": {"fr": "cases", "en": "cells", "de": "Zellen", "es": "casillas"},
    "resource_unit": {"fr": "unités", "en": "units", "de": "Einheiten", "es": "unidades"},
    "max_value": {
        "fr": "max. {value}",
        "en": "max {value}",
        "de": "max. {value}",
        "es": "máx. {value}",
    },
    "shares_total": {
        "fr": "Total : {value} % (normalisé à la génération)",
        "en": "Total: {value} % (normalized during generation)",
        "de": "Summe: {value} % (bei der Generierung normalisiert)",
        "es": "Total: {value} % (normalizado durante la generación)",
    },
    "resource_hint": {
        "fr": "Les valeurs restent dans les limites du jeu.",
        "en": "Values stay within the game limits.",
        "de": "Werte bleiben innerhalb der Spiellimits.",
        "es": "Los valores se mantienen dentro de los límites del juego.",
    },
    "coast_hint": {
        "fr": "Si l’option est active, le remplissage s’applique uniformément dans cette bande côtière.",
        "en": "When enabled, the fill percentage is applied uniformly inside this coastal band.",
        "de": "Wenn aktiviert, wird der Füllanteil gleichmäßig innerhalb dieses Küstenbands angewendet.",
        "es": "Si está activado, el porcentaje de relleno se aplica uniformemente dentro de esta banda costera.",
    },
    "start_bonus_hint": {
        "fr": "Chaque bonus est par joueur et hors quota global. La distance mesure le centre du bonus depuis la bordure du territoire ; 0 conserve le placement natif.",
        "en": "Each bonus is per player and outside global quotas. Distance measures the bonus centre from the territory border; 0 keeps native placement.",
        "de": "Jeder Bonus gilt je Spieler und außerhalb globaler Kontingente. Der Abstand misst die Bonusmitte ab der Gebietsgrenze; 0 behält die native Platzierung.",
        "es": "Cada bonificación es por jugador y queda fuera de los cupos globales. La distancia mide el centro desde el borde del territorio; 0 conserva la colocación nativa.",
    },
    "start_bonus_enabled": {
        "fr": "Activer ce bonus",
        "en": "Enable this bonus",
        "de": "Diesen Bonus aktivieren",
        "es": "Activar esta bonificación",
    },
    "start_bonus_distance": {
        "fr": "Distance du centre depuis la bordure",
        "en": "Centre distance from border",
        "de": "Abstand der Mitte von der Grenze",
        "es": "Distancia del centro desde el borde",
    },
    "start_bonus_force_extended": {
        "fr": "Forcer le placement à une distance étendue si nécessaire",
        "en": "Force placement at an extended distance if necessary",
        "de": "Platzierung bei Bedarf in erweiterter Entfernung erzwingen",
        "es": "Forzar la colocación a una distancia ampliada si es necesario",
    },
    "start_bonus_forest": {
        "fr": "Forêt de départ — forme native du profil",
        "en": "Start forest — profile-native shape",
        "de": "Startwald — native Profilform",
        "es": "Bosque inicial — forma nativa del perfil",
    },
    "start_bonus_adult_trees": {
        "fr": "Arbres adultes par joueur",
        "en": "Adult trees per player",
        "de": "Ausgewachsene Bäume je Spieler",
        "es": "Árboles adultos por jugador",
    },
    "start_bonus_saplings": {
        "fr": "Pousses par joueur",
        "en": "Saplings per player",
        "de": "Setzlinge je Spieler",
        "es": "Retoños por jugador",
    },
    "start_bonus_forest_radius_derived": {
        "fr": "Le rayon est calculé automatiquement selon les 30/20 arbres et leur espacement ; il s’élargit seulement si le terrain l’exige.",
        "en": "Radius is derived automatically from the 30/20 trees and their spacing; it expands only when terrain requires it.",
        "de": "Der Radius wird automatisch aus den 30/20 Bäumen und ihrem Abstand abgeleitet und nur bei Bedarf erweitert.",
        "es": "El radio se calcula automáticamente según los 30/20 árboles y su separación; solo se amplía si el terreno lo exige.",
    },
    "start_bonus_radius_min": {
        "fr": "Rayon minimal",
        "en": "Minimum radius",
        "de": "Minimaler Radius",
        "es": "Radio mínimo",
    },
    "start_bonus_radius_max": {
        "fr": "Rayon maximal",
        "en": "Maximum radius",
        "de": "Maximaler Radius",
        "es": "Radio máximo",
    },
    "start_bonus_rocky_radius": {
        "fr": "Rayon commun",
        "en": "Common radius",
        "de": "Gemeinsamer Radius",
        "es": "Radio común",
    },
    "start_bonus_native_shape": {
        "fr": "Forme : native du profil",
        "en": "Shape: profile-native",
        "de": "Form: nativ zum Profil",
        "es": "Forma: nativa del perfil",
    },
    "start_bonus_stones": {
        "fr": "Pierres de départ",
        "en": "Start building stones",
        "de": "Startbausteine",
        "es": "Piedras de construcción iniciales",
    },
    "start_bonus_anchors": {
        "fr": "Nombre de pierres par joueur",
        "en": "Stones per player",
        "de": "Steine je Spieler",
        "es": "Piedras por jugador",
    },
    "start_bonus_average_quantity": {
        "fr": "Stock moyen par pierre",
        "en": "Average stock per stone",
        "de": "Durchschnittlicher Vorrat je Stein",
        "es": "Reserva media por piedra",
    },
    "start_bonus_stock_preview": {
        "fr": "Stock demandé par joueur : environ {value} unités (arrondi à l’unité)",
        "en": "Requested stock per player: about {value} units (rounded to whole units)",
        "de": "Angeforderter Vorrat je Spieler: etwa {value} Einheiten (auf ganze Einheiten gerundet)",
        "es": "Reserva solicitada por jugador: aproximadamente {value} unidades (redondeada a unidades enteras)",
    },
    "start_bonus_swamp": {
        "fr": "Mini-marais de départ",
        "en": "Start mini-swamp",
        "de": "Kleiner Start-Sumpf",
        "es": "Mini-pantano inicial",
    },
    "start_bonus_swamp_shape": {
        "fr": "Forme",
        "en": "Shape",
        "de": "Form",
        "es": "Forma",
    },
    "start_bonus_swamp_shape_native": {
        "fr": "Native du générateur",
        "en": "Generator-native",
        "de": "Generator-nativ",
        "es": "Nativa del generador",
    },
    "start_bonus_swamp_shape_hexagon": {
        "fr": "Hexagone",
        "en": "Hexagon",
        "de": "Hexagon",
        "es": "Hexágono",
    },
    "start_bonus_swamp_radius": {
        "fr": "Rayon de la zone",
        "en": "Zone radius",
        "de": "Zonenradius",
        "es": "Radio de la zona",
    },
    "start_bonus_swamp_derived": {
        "fr": "Le rayon détermine automatiquement l’étendue de la zone ; le nombre de cases n’est pas réglé séparément.",
        "en": "The radius determines the zone extent automatically; cell count is not edited separately.",
        "de": "Der Radius bestimmt die Zonengröße automatisch; die Zellzahl wird nicht separat eingestellt.",
        "es": "El radio determina automáticamente el tamaño de la zona; las casillas no se ajustan por separado.",
    },
    "start_bonus_rocky": {
        "fr": "Zones minérales rocheuses",
        "en": "Rocky mineral zones",
        "de": "Felsige Mineralzonen",
        "es": "Zonas minerales rocosas",
    },
    "start_bonus_rocky_shape": {
        "fr": "Forme",
        "en": "Shape",
        "de": "Form",
        "es": "Forma",
    },
    "start_bonus_rocky_shape_hexagon": {
        "fr": "Hexagone",
        "en": "Hexagon",
        "de": "Hexagon",
        "es": "Hexágono",
    },
    "start_bonus_rocky_shape_organic": {
        "fr": "Organique",
        "en": "Organic",
        "de": "Organisch",
        "es": "Orgánica",
    },
    "start_bonus_rocky_surface": {
        "fr": "Répartition",
        "en": "Allocation",
        "de": "Verteilung",
        "es": "Reparto",
    },
    "start_bonus_rocky_surface_equal": {
        "fr": "Égal",
        "en": "Equal",
        "de": "Gleich",
        "es": "Igual",
    },
    "start_bonus_rocky_surface_proportional": {
        "fr": "Prorata",
        "en": "Prorata",
        "de": "Anteile",
        "es": "Prorrata",
    },
    "start_bonus_rocky_surface_custom": {
        "fr": "Par minerai",
        "en": "Per mineral",
        "de": "Je Mineral",
        "es": "Por mineral",
    },
    "start_bonus_rocky_total_surface": {
        "fr": "Total",
        "en": "Total",
        "de": "Gesamt",
        "es": "Total",
    },
    "start_bonus_rocky_family_header": {
        "fr": "Minerai",
        "en": "Mineral",
        "de": "Mineral",
        "es": "Mineral",
    },
    "start_bonus_rocky_core_header": {
        "fr": "Cœur",
        "en": "Core",
        "de": "Kern",
        "es": "Núcleo",
    },
    "start_bonus_rocky_quantity_header": {
        "fr": "Moyenne / case",
        "en": "Average / cell",
        "de": "Mittel / Zelle",
        "es": "Media / casilla",
    },
    "start_bonus_rocky_mode_hint_equal": {
        "fr": "Mode égal : le rayon commun détermine la surface ; les champs de surface sont inactifs.",
        "en": "Equal mode: the common radius determines the surface; surface fields are disabled.",
        "de": "Gleich: Der gemeinsame Radius bestimmt die Fläche; die Flächenfelder sind deaktiviert.",
        "es": "Modo igual: el radio común determina la superficie; los campos de superficie están desactivados.",
    },
    "start_bonus_rocky_mode_hint_proportional": {
        "fr": "Mode prorata : la surface totale est active ; les parts viennent de Minerais › Répartition.",
        "en": "Prorata mode: total surface is active; shares come from Minerals › Shares.",
        "de": "Nach Anteilen: Die Gesamtfläche ist aktiv; die Anteile kommen aus Mineralien › Anteile.",
        "es": "Modo prorrata: la superficie total está activa; las partes vienen de Minerales › Reparto.",
    },
    "start_bonus_rocky_mode_hint_custom": {
        "fr": "Mode personnalisé : la surface de chaque minerai est active ; surface totale et rayons sont inactifs.",
        "en": "Custom mode: each mineral surface is active; total surface and radii are disabled.",
        "de": "Benutzerdefiniert: Die Fläche je Mineral ist aktiv; Gesamtfläche und Radien sind deaktiviert.",
        "es": "Modo personalizado: la superficie de cada mineral está activa; superficie total y radios están desactivados.",
    },
    "start_bonus_rocky_limits": {
        "fr": "Rayon 1–16 HEX6 · cœur 1–820 cases · total dynamique jusqu’à 2 460 · moyenne 1–15.",
        "en": "Radius 1–16 HEX6 · core 1–820 cells · dynamic total up to 2,460 · average 1–15.",
        "de": "Radius 1–16 HEX6 · Kern 1–820 Zellen · dynamische Summe bis 2.460 · Mittel 1–15.",
        "es": "Radio 1–16 HEX6 · núcleo 1–820 casillas · total dinámico hasta 2.460 · media 1–15.",
    },
    "start_bonus_rocky_surface_family": {
        "fr": "Surface cœur — {value}",
        "en": "Core surface — {value}",
        "de": "Kernfläche — {value}",
        "es": "Superficie del núcleo — {value}",
    },
    "start_bonus_rocky_quantity_family": {
        "fr": "Quantité moyenne — {value}",
        "en": "Average quantity — {value}",
        "de": "Durchschnittsmenge — {value}",
        "es": "Cantidad media — {value}",
    },
    "start_bonus_rocky_occupancy": {
        "fr": "Le cœur de chaque zone est occupé à 100 % par le minerai choisi ; aucun taux d’occupation séparé.",
        "en": "Each zone core is 100% occupied by its selected mineral; there is no separate occupancy rate.",
        "de": "Der Kern jeder Zone ist zu 100 % mit dem gewählten Mineral belegt; keine separate Belegungsrate.",
        "es": "El núcleo de cada zona está ocupado al 100 % por el mineral elegido; no hay tasa de ocupación separada.",
    },
    "start_bonus_global_mean": {
        "fr": "Chaque quantité moyenne est initialisée depuis le réglage global des minerais ; elle peut être surchargée ici.",
        "en": "Each average quantity starts from the global mineral setting and can be overridden here.",
        "de": "Jede Durchschnittsmenge übernimmt zunächst die globale Mineraleinstellung und kann hier überschrieben werden.",
        "es": "Cada cantidad media parte del ajuste global de minerales y puede sobrescribirse aquí.",
    },
    "start_bonus_hexagon_shape": {
        "fr": "Les deux formes produisent un cœur intégralement minéralisé et deux transitions légales ; une zone impossible est omise.",
        "en": "Both shapes produce a fully mineralized core and two legal transitions; an impossible zone is skipped.",
        "de": "Beide Formen erzeugen einen vollständig mineralisierten Kern und zwei legale Übergänge; eine unmögliche Zone wird ausgelassen.",
        "es": "Ambas formas producen un núcleo completamente mineralizado y dos transiciones legales; una zona imposible se omite.",
    },
    "start_bonus_coal": {
        "fr": "Charbon",
        "en": "Coal",
        "de": "Kohle",
        "es": "Carbón",
    },
    "start_bonus_iron": {
        "fr": "Fer",
        "en": "Iron",
        "de": "Eisen",
        "es": "Hierro",
    },
    "start_bonus_gold": {
        "fr": "Or",
        "en": "Gold",
        "de": "Gold",
        "es": "Oro",
    },
    "start_bonus_lake": {
        "fr": "Lac bonus",
        "en": "Bonus lake",
        "de": "Bonussee",
        "es": "Lago adicional",
    },
    "start_bonus_lake_shape": {
        "fr": "Forme",
        "en": "Shape",
        "de": "Form",
        "es": "Forma",
    },
    "start_bonus_lake_shape_native": {
        "fr": "Native",
        "en": "Native",
        "de": "Nativ",
        "es": "Nativa",
    },
    "start_bonus_lake_shape_hexagon": {
        "fr": "Hexagone",
        "en": "Hexagon",
        "de": "Hexagon",
        "es": "Hexágono",
    },
    "start_bonus_lake_proximity": {
        "fr": "Rayon de contrôle eau native",
        "en": "Native-water check radius",
        "de": "Radius für natives Wasser",
        "es": "Radio de control de agua nativa",
    },
    "start_bonus_river_target": {
        "fr": "Rivières cibles par lac",
        "en": "Target rivers per lake",
        "de": "Zielflüsse je See",
        "es": "Ríos objetivo por lago",
    },
    "start_bonus_fish_fill": {
        "fr": "Cases du lac contenant des poissons",
        "en": "Lake cells containing fish",
        "de": "Seezellen mit Fischen",
        "es": "Casillas del lago con peces",
    },
    "start_bonus_lake_hint": {
        "fr": "Rayon mesuré depuis la bordure du territoire pour contrôler l’eau native ; 0 désactive ce contrôle. Deux rives et une rivière légale sont requises ; l’eau existante reste protégée.",
        "en": "Radius from the territory border used to check native water; 0 disables this check. Two shores and a legal river are required; existing water stays protected.",
        "de": "Radius ab der Gebietsgrenze zur Prüfung von nativem Wasser; 0 deaktiviert die Prüfung. Zwei Ufer und ein legaler Fluss sind nötig; vorhandenes Wasser bleibt geschützt.",
        "es": "Radio desde el borde del territorio para comprobar agua nativa; 0 desactiva este control. Se requieren dos orillas y un río legal; el agua existente queda protegida.",
    },
}


def custom_section_text(key: str, language: str, **values: Any) -> str:
    """Return a translated label for the curated Custom sections."""

    entry = _CUSTOM_SECTION_TEXT.get(key, {})
    text = entry.get(language, entry.get("en", key))
    return text.format(**values)


def mineral_label(key: str, language: str) -> str:
    labels = {
        "coal": {"fr": "Charbon", "en": "Coal", "de": "Kohle", "es": "Carbón"},
        "iron": {"fr": "Fer", "en": "Iron", "de": "Eisen", "es": "Hierro"},
        "gold": {"fr": "Or", "en": "Gold", "de": "Gold", "es": "Oro"},
        "gems": {"fr": "Gemmes", "en": "Gems", "de": "Edelsteine", "es": "Gemas"},
        "sulfur": {"fr": "Soufre", "en": "Sulfur", "de": "Schwefel", "es": "Azufre"},
    }
    entry = labels.get(key, {})
    return entry.get(language, entry.get("en", key))


__all__ = (
    "archetype_description",
    "custom_section_text",
    "mineral_label",
    "parameter_group",
    "parameter_label",
)
