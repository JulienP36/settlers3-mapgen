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
        "fr": "Bonus de départ", "en": "Start bonuses", "de": "Startboni", "es": "Bonificaciones iniciales",
    },
    "start_bonus_common": {
        "fr": "Règles communes", "en": "Common rules", "de": "Gemeinsame Regeln", "es": "Reglas comunes",
    },
    "start_bonus_objects": {
        "fr": "Bonus d’objets", "en": "Object bonuses", "de": "Objektboni", "es": "Bonificaciones de objetos",
    },
    "start_bonus_terrain_resources": {
        "fr": "Bonus de terrains et ressources", "en": "Terrain and resource bonuses", "de": "Terrain- und Ressourcenboni", "es": "Bonificaciones de terrenos y recursos",
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
    "section_modified": {
        "fr": "· modifié", "en": "· modified", "de": "· geändert", "es": "· modificado",
    },
    "archetype_base_profile": {
        "fr": "Profil de base", "en": "Base profile", "de": "Basisprofil", "es": "Perfil base",
    },
    "archetype_profile_classic": {
        "fr": "Classique", "en": "Classic", "de": "Klassisch", "es": "Clásico",
    },
    "archetype_profile_continental": {
        "fr": "Continental", "en": "Continental", "de": "Kontinental", "es": "Continental",
    },
    "archetype_profile_edited": {
        "fr": "Profil personnalisé", "en": "Custom profile", "de": "Benutzerprofil", "es": "Perfil personalizado",
    },
    "archetype_profile_hint": {
        "fr": "Classique reprend le Legacy natif ; Continental reprend le relief Legacy dérivé validé. Modifier un réglage crée un Profil personnalisé.",
        "en": "Classic keeps native Legacy; Continental uses the validated Legacy-derived relief. Editing a setting creates a Custom profile.",
        "de": "Klassisch behält das native Legacy bei; Kontinental verwendet das validierte, vom Legacy abgeleitete Relief. Eine Änderung erstellt ein Benutzerprofil.",
        "es": "Clásico conserva Legacy nativo; Continental usa el relieve validado derivado de Legacy. Al cambiar un ajuste se crea un perfil personalizado.",
    },
    "archetype_macro_profile": {
        "fr": "Construction macro", "en": "Macro construction", "de": "Makroaufbau", "es": "Construcción macro",
    },
    "archetype_layout_engine": {
        "fr": "Moteur de forme", "en": "Shape engine", "de": "Formmotor", "es": "Motor de forma",
    },
    "archetype_noise_model": {
        "fr": "Modèle de bruit", "en": "Noise model", "de": "Rauschmodell", "es": "Modelo de ruido",
    },
    "archetype_relief_source": {
        "fr": "Source du relief", "en": "Relief source", "de": "Reliefquelle", "es": "Fuente del relieve",
    },
    "archetype_relief_source_hint": {
        "fr": "Legacy natif conserve son relief d’origine. Legacy par blocs construit un continent, des chaînes montagneuses et des bassins intérieurs, puis utilise le raffinement, la sculpture et la relaxation natifs. Les sources noise-map complètes restent des générateurs indépendants.",
        "en": "Native Legacy keeps its original relief. Legacy blocks builds a continent, mountain belts and inland basins, then uses native refinement, sculpture and relaxation. Complete noise-map sources remain independent generators.",
        "de": "Native Legacy behält sein ursprüngliches Relief. Legacy-Blöcke erzeugt einen Kontinent, Gebirgsketten und Binnenbecken und verwendet anschließend native Verfeinerung, Modellierung und Glättung. Vollständige Noise-Map-Quellen bleiben unabhängige Generatoren.",
        "es": "Legacy nativo conserva su relieve original. Legacy por bloques crea un continente, cordilleras y cuencas interiores y luego usa el refinamiento, modelado y suavizado nativos. Las fuentes de noise map completas siguen siendo generadores independientes.",
    },
    "archetype_relief_source_native": {
        "fr": "Legacy natif", "en": "Native Legacy", "de": "Native Legacy", "es": "Legacy nativo",
    },
    "archetype_relief_source_custom_legacy": {
        "fr": "Legacy par blocs", "en": "Legacy blocks", "de": "Legacy-Blöcke", "es": "Legacy por bloques",
    },
    "archetype_relief_source_fractal": {
        "fr": "fBm fractal", "en": "Fractal fBm", "de": "Fraktales fBm", "es": "fBm fractal",
    },
    "archetype_relief_source_warped": {
        "fr": "fBm déformé", "en": "Warped fBm", "de": "Verzerrtes fBm", "es": "fBm deformado",
    },
    "archetype_relief_source_ridged": {
        "fr": "fBm crêtes", "en": "Ridged fBm", "de": "Kamm-fBm", "es": "fBm de crestas",
    },
    "archetype_noise_range": {
        "fr": "Plage du bruit", "en": "Noise range", "de": "Rauschbereich", "es": "Rango del ruido",
    },
    "archetype_coast_model": {
        "fr": "Construction des plages", "en": "Shore construction", "de": "Uferaufbau", "es": "Construcción de costas",
    },
    "archetype_coast_derived": {
        "fr": "Dérivée de la relation eau/terrain", "en": "Derived from water/land relation", "de": "Aus Wasser-/Landbeziehung abgeleitet", "es": "Derivada de la relación agua/terreno",
    },
    "archetype_coast_custom": {
        "fr": "Construction dédiée", "en": "Dedicated construction", "de": "Eigene Konstruktion", "es": "Construcción propia",
    },
    "archetype_mass_model": {
        "fr": "Masse terrestre", "en": "Land-mass model", "de": "Landmassenmodell", "es": "Modelo de masa terrestre",
    },
    "archetype_micro_islands": {
        "fr": "Micro-îles", "en": "Micro-islands", "de": "Mikroinseln", "es": "Microislas",
    },
    "archetype_relief_group": {
        "fr": "Seuils du relief", "en": "Relief thresholds", "de": "Reliefschwellen", "es": "Umbrales del relieve",
    },
    "archetype_morphology_group": {
        "fr": "Morphologie du relief", "en": "Relief morphology", "de": "Reliefmorphologie", "es": "Morfología del relieve",
    },
    "archetype_legacy_blocks_group": {
        "fr": "Blocs natifs Legacy", "en": "Native Legacy blocks", "de": "Native Legacy-Blöcke", "es": "Bloques nativos Legacy",
    },
    "archetype_native_coarse_variation": {
        "fr": "Variation des points d’ancrage (%)", "en": "Anchor-point variation (%)", "de": "Variation der Ankerpunkte (%)", "es": "Variación de los puntos de anclaje (%)",
    },
    "archetype_native_coarse_variation_hint": {
        "fr": "Variation aléatoire des hauteurs posées sur la grille Legacy de 64 cases, avant les subdivisions. 100 % conserve exactement le Legacy ; 0 % fixe chaque bande à sa hauteur moyenne.",
        "en": "Random variation of heights on the Legacy 64-cell lattice, before subdivision. 100% exactly preserves Legacy; 0% fixes each band at its mean height.",
        "de": "Zufallsvariation der Höhen auf dem 64-Zellen-Legacy-Raster vor der Unterteilung. 100 % entspricht exakt Legacy; 0 % setzt jedes Band auf seine mittlere Höhe.",
        "es": "Variación aleatoria de las alturas en la cuadrícula Legacy de 64 celdas, antes de subdividir. 100 % conserva exactamente Legacy; 0 % fija cada franja en su altura media.",
    },
    "archetype_noise_layers_group": {
        "fr": "Composants de relief", "en": "Relief components", "de": "Reliefkomponenten", "es": "Componentes del relieve",
    },
    "archetype_noise_layer_count": {
        "fr": "Nombre de fusions",
        "en": "Fusion count",
        "de": "Anzahl Fusionen",
        "es": "Número de fusiones",
    },
    "archetype_noise_adaptive_frequency": {
        "fr": "Adapter les fréquences à la taille de carte",
        "en": "Scale frequencies with map size",
        "de": "Frequenzen an die Kartengröße anpassen",
        "es": "Adaptar frecuencias al tamaño del mapa",
    },
    "archetype_noise_adaptive_frequency_hint": {
        "fr": "Activé : les valeurs saisies servent de référence à 768 cases. La fréquence baisse sur les petites cartes et monte sur les grandes ; les octaves trop fines sont retirées des petits domaines. Désactivé : comportement actuel.",
        "en": "On: entered values are the 768-cell reference. Frequencies fall on smaller maps and rise on larger ones; octaves too fine for small domains are removed. Off: current behavior.",
        "de": "Ein: Die Eingaben gelten als Referenz für 768 Zellen. Auf kleineren Karten sinken die Frequenzen, auf größeren steigen sie; zu feine Oktaven entfallen auf kleinen Karten. Aus: aktuelles Verhalten.",
        "es": "Activado: los valores introducidos sirven de referencia para 768 celdas. Las frecuencias bajan en mapas pequeños y suben en los grandes; se eliminan las octavas demasiado finas para dominios pequeños. Desactivado: comportamiento actual.",
    },
    "archetype_noise_layer": {
        "fr": "Couche {index}", "en": "Layer {index}", "de": "Schicht {index}", "es": "Capa {index}",
    },
    "archetype_noise_family": {
        "fr": "Type", "en": "Type", "de": "Typ", "es": "Tipo",
    },
    "archetype_noise_scale": {
        "fr": "Échelle", "en": "Scale", "de": "Skala", "es": "Escala",
    },
    "archetype_noise_strength": {
        "fr": "Intensité", "en": "Strength", "de": "Stärke", "es": "Intensidad",
    },
    "archetype_noise_operation": {
        "fr": "Fusion", "en": "Blend", "de": "Mischung", "es": "Fusión",
    },
    "archetype_noise_add": {
        "fr": "Rehausser", "en": "Raise", "de": "Anheben", "es": "Elevar",
    },
    "archetype_noise_subtract": {
        "fr": "Abaisser", "en": "Lower", "de": "Absenken", "es": "Bajar",
    },
    "archetype_noise_smooth": {
        "fr": "Ondulations", "en": "Rolling", "de": "Wellen", "es": "Ondulaciones",
    },
    "archetype_noise_ridged": {
        "fr": "Crêtes", "en": "Ridged", "de": "Kamm", "es": "Crestas",
    },
    "archetype_noise_layers_hint": {
        "fr": "Les composants modulent le domaine terrestre de la source choisie avant la normalisation et la relaxation natives. Ils ne créent pas encore de lacs ; désactivés, ils ne changent rien à la source.",
        "en": "Components modulate the selected source's land domain before native normalization and relaxation. They do not create lakes yet; disabled components leave the source unchanged.",
        "de": "Komponenten verändern den Landbereich der gewählten Quelle vor der nativen Normalisierung und Glättung. Sie erzeugen noch keine Seen; deaktivierte Komponenten ändern die Quelle nicht.",
        "es": "Los componentes modifican el dominio terrestre de la fuente elegida antes de la normalización y relajación nativas. Todavía no crean lagos; desactivados no cambian la fuente.",
    },
    "archetype_noise_masks_hint": {
        "fr": "Un masque réduit ou inverse l’influence d’une source dans son rectangle fini : hauteur, bordure, bandes, direction, pente, courbure ou autre noise. Influence 0 % = neutre.",
        "en": "A mask reduces or inverts a source's influence inside its finite rectangle: height, edge, bands, direction, slope, curvature or another noise. Influence 0% = neutral.",
        "de": "Eine Maske verringert oder invertiert den Einfluss einer Quelle innerhalb ihres endlichen Rechtecks: Höhe, Rand, Bänder, Richtung, Neigung, Krümmung oder anderes Rauschen. Einfluss 0 % = neutral.",
        "es": "Una máscara reduce o invierte la influencia de una fuente dentro de su rectángulo finito: altura, borde, bandas, dirección, pendiente, curvatura u otro ruido. Influencia 0 % = neutra.",
    },
    "archetype_shape_group": {
        "fr": "Gabarit de forme", "en": "Shape template", "de": "Formgitter", "es": "Plantilla de forma",
    },
    "archetype_shape_subtitle": {
        "fr": "Structure spatiale de la macro-forme", "en": "Spatial structure of the macro shape", "de": "Räumliche Struktur der Makroform", "es": "Estructura espacial de la macroforma",
    },
    "archetype_shape_hint": {
        "fr": "Le gabarit définit une forme de carte dans laquelle les sources de bruit sont générées. Il ne crée pas un bruit secondaire et ne dépend d’aucune fusion.",
        "en": "The template defines a map shape in which noise sources are generated. It does not create a secondary noise and does not depend on any fusion.",
        "de": "Das Gitter definiert eine Kartenform, in der Rauschquellen erzeugt werden. Es erzeugt kein sekundäres Rauschen und hängt von keiner Fusion ab.",
        "es": "La plantilla define una forma de mapa dentro de la que se generan las fuentes de ruido. No crea un ruido secundario ni depende de ninguna fusión.",
    },
    "archetype_shape_type": {
        "fr": "Forme", "en": "Shape", "de": "Form", "es": "Forma",
    },
    "archetype_shape_width": {
        "fr": "Largeur %", "en": "Width %", "de": "Breite %", "es": "Anchura %",
    },
    "archetype_shape_height": {
        "fr": "Hauteur %", "en": "Height %", "de": "Höhe %", "es": "Altura %",
    },
    "archetype_shape_offset_x": {
        "fr": "Décalage X %", "en": "Offset X %", "de": "Versatz X %", "es": "Desfase X %",
    },
    "archetype_shape_offset_y": {
        "fr": "Décalage Y %", "en": "Offset Y %", "de": "Versatz Y %", "es": "Desfase Y %",
    },
    "archetype_shape_rotation": {
        "fr": "Rotation °", "en": "Rotation °", "de": "Drehung °", "es": "Rotación °",
    },
    "archetype_shape_softness": {
        "fr": "Douceur bord %", "en": "Edge softness %", "de": "Randweichheit %", "es": "Suavidad borde %",
    },
    "archetype_shape_points": {
        "fr": "Pointes", "en": "Points", "de": "Spitzen", "es": "Puntas",
    },
    "archetype_shape_inner_radius": {
        "fr": "Creux étoile %", "en": "Star inner radius %", "de": "Stern-Innenradius %", "es": "Radio interior estrella %",
    },
    "archetype_shape_thickness": {
        "fr": "Épaisseur %", "en": "Thickness %", "de": "Dicke %", "es": "Grosor %",
    },
    "archetype_shape_turns": {
        "fr": "Ondulations", "en": "Turns", "de": "Windungen", "es": "Ondulaciones",
    },
    "archetype_shape_amplitude": {
        "fr": "Amplitude %", "en": "Amplitude %", "de": "Amplitude %", "es": "Amplitud %",
    },
    "archetype_shape_taper": {
        "fr": "Pointe des extrémités %", "en": "End taper %", "de": "Endverjüngung %", "es": "Afinado extremos %",
    },
    "archetype_shape_crater": {
        "fr": "Cratère %", "en": "Crater %", "de": "Krater %", "es": "Cráter %",
    },
    "archetype_shape_relief": {
        "fr": "Relief du dôme %", "en": "Dome relief %", "de": "Kuppelrelief %", "es": "Relieve de cúpula %",
    },
    "archetype_shape_templates_hint": {
        "fr": "Les fusions restent des sources indépendantes. Le gabarit de forme agit au niveau de la macro-géographie et leur interdit de recréer du terrain hors de sa silhouette.",
        "en": "Fusions remain independent sources. The shape template acts at macro-geography level and prevents them from recreating terrain outside its silhouette.",
        "de": "Fusionen bleiben unabhängige Quellen. Das Formgitter wirkt auf Makrogeografie-Ebene und verhindert Terrain außerhalb seiner Silhouette.",
        "es": "Las fusiones siguen siendo fuentes independientes. La plantilla actúa a nivel de macrogeografía e impide recrear terreno fuera de su silueta.",
    },
    "archetype_mask_group": {
        "fr": "Masques spatiaux", "en": "Spatial masks", "de": "Räumliche Masken", "es": "Máscaras espaciales",
    },
    "archetype_mask_subtitle": {
        "fr": "Modulation douce du champ complet après les fusions", "en": "Soft modulation of the complete field after fusions", "de": "Sanfte Modulation des vollständigen Feldes nach Fusionen", "es": "Modulación suave del campo completo después de las fusiones",
    },
    "archetype_mask_hint": {
        "fr": "Un masque n’écrase pas le terrain hors de sa forme : il module toute la noisemap, avec une transition douce sur son bord et une variation conservée à l’extérieur. Le type Dessin libre permet de peindre ou d’importer une grille en niveaux de gris.",
        "en": "A mask does not erase terrain outside its shape: it modulates the whole noisemap, with a soft edge transition and variation preserved outside. Freehand lets you paint or import a grayscale grid.",
        "de": "Eine Maske löscht Terrain außerhalb ihrer Form nicht: Sie moduliert die gesamte Noisemap mit weichem Randübergang und erhaltener Variation außerhalb. Freihand ermöglicht das Malen oder Importieren eines Graustufenrasters.",
        "es": "Una máscara no borra el terreno fuera de su forma: modula todo el noisemap, con una transición suave en el borde y variación conservada fuera. Dibujo libre permite pintar o importar una cuadrícula en escala de grises.",
    },
    "archetype_mask_layer_count": {
        "fr": "Nombre de masques", "en": "Mask count", "de": "Anzahl Masken", "es": "Número de máscaras",
    },
    "archetype_mask_operation": {
        "fr": "Opération", "en": "Operation", "de": "Operation", "es": "Operación",
    },
    "archetype_mask_strength": {
        "fr": "Influence %", "en": "Strength %", "de": "Stärke %", "es": "Influencia %",
    },
    "archetype_mask_layer": {
        "fr": "Masque {index}", "en": "Mask {index}", "de": "Maske {index}", "es": "Máscara {index}",
    },
    "archetype_noise_lab_none": {
        "fr": "Laboratoire : aucun composant actif.",
        "en": "Lab: no active component.",
        "de": "Labor: keine aktive Komponente.",
        "es": "Laboratorio: ningún componente activo.",
    },
    "archetype_noise_lab_total": {
        "fr": "Laboratoire : {count} composant(s) actif(s), {percent} % des cellules modifiées.",
        "en": "Lab: {count} active component(s), {percent}% of cells modified.",
        "de": "Labor: {count} aktive Komponente(n), {percent}% der Zellen verändert.",
        "es": "Laboratorio: {count} componente(s) activo(s), {percent}% de celdas modificadas.",
    },
    "archetype_noise_lab_source": {
        "fr": "Source complète : {source}.",
        "en": "Complete source: {source}.",
        "de": "Vollständige Quelle: {source}.",
        "es": "Fuente completa: {source}.",
    },
    "archetype_noise_lab_source_metrics": {
        "fr": "Profil brut : terre {land} % · hauteurs P10/P50/P90 {p10}/{p50}/{p90}.",
        "en": "Raw profile: land {land}% · P10/P50/P90 heights {p10}/{p50}/{p90}.",
        "de": "Rohprofil: Land {land}% · Höhen P10/P50/P90 {p10}/{p50}/{p90}.",
        "es": "Perfil bruto: tierra {land}% · alturas P10/P50/P90 {p10}/{p50}/{p90}.",
    },
    "archetype_noise_lab_layer": {
        "fr": "Couche {index} : {source} · rôle {role} · masque {mask} · étape {stage} · {operation} · ordre {order} · {affected} % · delta {minimum}…{maximum}",
        "en": "Layer {index}: {source} · role {role} · mask {mask} · stage {stage} · {operation} · order {order} · {affected}% · delta {minimum}…{maximum}",
        "de": "Schicht {index}: {source} · Rolle {role} · Maske {mask} · Stufe {stage} · {operation} · Reihenfolge {order} · {affected}% · Delta {minimum}…{maximum}",
        "es": "Capa {index}: {source} · rol {role} · máscara {mask} · etapa {stage} · {operation} · orden {order} · {affected}% · delta {minimum}…{maximum}",
    },
    "archetype_noise_contribution": {
        "fr": "Contribution brute des fusions (rouge = rehausse, bleu = abaisse)",
        "en": "Raw fusion contribution (red = raise, blue = lower)",
        "de": "Roher Fusionsbeitrag (rot = höher, blau = niedriger)",
        "es": "Contribución bruta de las fusiones (rojo = subir, azul = bajar)",
    },
    "archetype_noise_contribution_short": {
        "fr": "Contribution brute",
        "en": "Raw contribution",
        "de": "Roher Beitrag",
        "es": "Contribución bruta",
    },
    "archetype_noise_role_land_relief": {
        "fr": "relief terrestre",
        "en": "land relief",
        "de": "Landrelief",
        "es": "relieve terrestre",
    },
    "archetype_noise_mask_native_land": {
        "fr": "terre native",
        "en": "native land",
        "de": "natives Land",
        "es": "tierra nativa",
    },
    "archetype_noise_mask_source_land": {
        "fr": "terre de la source",
        "en": "source land",
        "de": "Quellenland",
        "es": "tierra de la fuente",
    },
    "archetype_noise_stage_pre_normalize": {
        "fr": "avant normalisation",
        "en": "before normalization",
        "de": "vor Normalisierung",
        "es": "antes de normalizar",
    },
    "archetype_shape_scale": {
        "fr": "Échelle des formes", "en": "Shape scale", "de": "Formmaßstab", "es": "Escala de formas",
    },
    "archetype_relief_contrast": {
        "fr": "Contraste du relief", "en": "Relief contrast", "de": "Reliefkontrast", "es": "Contraste del relieve",
    },
    "archetype_native_large_scale_refinement": {
        "fr": "Variation grandes formes (32–8) (%)", "en": "Large-scale variation (32–8) (%)", "de": "Variation großer Formen (32–8) (%)", "es": "Variación de formas grandes (32–8) (%)",
    },
    "archetype_native_fine_scale_refinement": {
        "fr": "Variation détails fins (4–1) (%)", "en": "Fine-detail variation (4–1) (%)", "de": "Variation feiner Details (4–1) (%)", "es": "Variación de detalles finos (4–1) (%)",
    },
    "archetype_native_sculpture_attempts": {
        "fr": "Tentatives de sculpture (%)", "en": "Sculpture attempts (%)", "de": "Sculpturversuche (%)", "es": "Intentos de escultura (%)",
    },
    "archetype_native_relaxation_strength": {
        "fr": "Intensité de correction des pentes (%)", "en": "Slope-correction strength (%)", "de": "Stärke der Hangkorrektur (%)", "es": "Intensidad de corrección de pendientes (%)",
    },
    "archetype_native_refinement": {
        "fr": "Variation du raffinement natif (%)", "en": "Native refinement variation (%)", "de": "Variation der nativen Verfeinerung (%)", "es": "Variación del refinamiento nativo (%)",
    },
    "archetype_frame_margin": {
        "fr": "Marge du domaine (%)", "en": "Domain margin (%)", "de": "Bereichsrand (%)", "es": "Margen del dominio (%)",
    },
    "archetype_edge_falloff": {
        "fr": "Transition de bord", "en": "Edge transition", "de": "Randübergang", "es": "Transición de borde",
    },
    "archetype_shape_scale_hint": {
        "fr": "100 % conserve l’échelle native. Une valeur inférieure resserre l’échantillonnage et réduit l’échelle apparente des formes ; le pourtour reste aquatique.",
        "en": "100% keeps the native scale. Lower values tighten the sampling and reduce the apparent form scale; the perimeter remains water.",
        "de": "100 % behält den nativen Maßstab. Niedrigere Werte verkleinern den sichtbaren Formmaßstab; der Rand bleibt Wasser.",
        "es": "100 % conserva la escala nativa. Los valores inferiores reducen la escala aparente de las formas; el perímetro sigue siendo agua.",
    },
    "archetype_relief_contrast_hint": {
        "fr": "100 % conserve l’amplitude native. Une valeur supérieure accentue les écarts de hauteur ; une valeur inférieure adoucit le relief.",
        "en": "100% keeps the native amplitude. Higher values strengthen height differences; lower values soften the relief.",
        "de": "100 % behält die native Amplitude. Höhere Werte verstärken Höhenunterschiede; niedrigere Werte glätten das Relief.",
        "es": "100 % conserva la amplitud nativa. Los valores superiores acentúan las diferencias de altura; los inferiores suavizan el relieve.",
    },
    "archetype_native_large_scale_refinement_hint": {
        "fr": "Intensité aléatoire des subdivisions aux échelles 32, 16 et 8. Combinée au réglage général ; 100 % garde l’amplitude native de cette bande.",
        "en": "Random subdivision strength at scales 32, 16 and 8. Combined with the master setting; 100% keeps this band’s native amplitude.",
        "de": "Zufällige Unterteilungsstärke bei Maßstab 32, 16 und 8. Wird mit der Haupteinstellung kombiniert; 100 % behält die native Amplitude dieses Bereichs.",
        "es": "Intensidad aleatoria de subdivisión en escalas 32, 16 y 8. Se combina con el ajuste general; 100 % conserva la amplitud nativa de esta banda.",
    },
    "archetype_native_fine_scale_refinement_hint": {
        "fr": "Intensité aléatoire des subdivisions aux échelles 4, 2 et 1. Sur Legacy par blocs, la base est atténuée à 75 % pour limiter les petites cuvettes ; ce réglage la multiplie. Sur Legacy natif, 100 % garde l’amplitude native.",
        "en": "Random subdivision strength at scales 4, 2 and 1. Legacy Blocks starts from a 75% baseline to limit tiny basins; this control scales that baseline. Native Legacy keeps its 100% amplitude.",
        "de": "Zufällige Unterteilungsstärke bei Maßstab 4, 2 und 1. Legacy mit Blöcken beginnt mit 75 %, um kleine Senken zu begrenzen; diese Einstellung skaliert diesen Wert. Das native Legacy behält 100 %.",
        "es": "Intensidad aleatoria de subdivisión en escalas 4, 2 y 1. Legacy por bloques parte de un 75 % para limitar las pequeñas cuencas; este control multiplica esa base. Legacy nativo conserva el 100 %.",
    },
    "archetype_native_sculpture_attempts_hint": {
        "fr": "Nombre de tentatives du bloc de sculpture après le raffinement. 100 % correspond au nombre natif ; 0 % désactive les tentatives. Peut changer la consommation aléatoire de ce bloc.",
        "en": "Number of attempts in the sculpture block after refinement. 100% is the native count; 0% disables attempts. This can change random-number consumption in this block.",
        "de": "Anzahl der Versuche im Sculpturblock nach der Verfeinerung. 100 % entspricht der nativen Anzahl; 0 % deaktiviert die Versuche. Dadurch kann sich der Zufallszahlenverbrauch dieses Blocks ändern.",
        "es": "Número de intentos del bloque de escultura tras el refinamiento. 100 % equivale a la cantidad nativa; 0 % desactiva los intentos. Puede cambiar el consumo aleatorio de este bloque.",
    },
    "archetype_native_relaxation_strength_hint": {
        "fr": "Part de la correction locale appliquée après la relaxation native. 100 % conserve toute la correction Legacy ; 0 % garde les hauteurs issues de la sculpture avant relaxation. Les valeurs intermédiaires préservent davantage de ruptures et de pentes abruptes. Ce réglage est distinct du nombre de points examinés par la sculpture.",
        "en": "Share of the local correction applied after native relaxation. 100% keeps the full Legacy correction; 0% keeps the sculpted heights before relaxation. Intermediate values preserve more local breaks and steeper slopes. This setting is separate from how many points sculpture examines.",
        "de": "Anteil der lokalen Korrektur nach der nativen Relaxation. 100 % behält die vollständige Legacy-Korrektur bei; 0 % behält die vor der Relaxation skulptierten Höhen. Zwischenwerte erhalten mehr lokale Stufen und steilere Hänge. Diese Einstellung ist unabhängig von der Anzahl der von der Skulptur geprüften Punkte.",
        "es": "Parte de la corrección local aplicada tras la relajación nativa. 100 % conserva toda la corrección Legacy; 0 % mantiene las alturas esculpidas antes de relajar. Los valores intermedios preservan más rupturas locales y pendientes pronunciadas. Este ajuste es distinto de cuántos puntos examina la escultura.",
    },
    "archetype_native_refinement_hint": {
        "fr": "Intensité de variation aléatoire des subdivisions du bloc Legacy, de l’échelle 32 jusqu’à la case. 100 % conserve exactement le Legacy. Utilisé seulement avec la source « Legacy natif » ; les sources noisemaps complètes restent indépendantes.",
        "en": "Random variation strength in the Legacy subdivision block, from scale 32 down to individual cells. 100% exactly preserves Legacy. Used only with the Native Legacy source; complete noise-map sources remain independent.",
        "de": "Stärke der Zufallsvariation im Legacy-Unterteilungsblock von Maßstab 32 bis zur einzelnen Zelle. 100 % entspricht exakt Legacy. Nur mit der Quelle „Natives Legacy“ verwendet; vollständige Noise-Map-Quellen bleiben unabhängig.",
        "es": "Intensidad de variación aleatoria del bloque de subdivisión Legacy, desde escala 32 hasta cada celda. 100 % conserva exactamente Legacy. Solo se usa con la fuente Legacy nativa; las fuentes completas de mapas de ruido siguen siendo independientes.",
    },
    "archetype_frame_margin_hint": {
        "fr": "Sur le domaine Continental calibré, 0 % correspond à la petite marge testée en R66 ; 4 % rétablit l’ancienne marge de 18 cases sur 768. La transition de bord est réglée séparément.",
        "en": "On the calibrated Continental domain, 0% matches the small ocean margin tested in R66; 4% restores the former 18-cell margin on a 768 map. Edge transition is controlled separately.",
        "de": "Im kalibrierten Continental-Bereich entspricht 0 % dem kleinen, in R66 getesteten Ozeanrand; 4 % stellt den früheren Rand von 18 Zellen auf einer 768er Karte wieder her. Der Randübergang wird separat eingestellt.",
        "es": "0 % no añade un marco sin generación. En el preset Continental, 5 % restablece el marco anterior de 18 celdas; en otros perfiles, el valor escala con el dominio.",
    },
    "archetype_edge_falloff_hint": {
        "fr": "Largeur sur laquelle la source rejoint naturellement l’eau avant son cadre. La transition est carrée, pas un masque radial qui arrondit les continents.",
        "en": "Width over which the source naturally reaches water before its frame. The transition is rectangular, not a radial mask that rounds landmasses.",
        "de": "Breite, über die die Quelle vor ihrem Rahmen natürlich Wasser erreicht. Der Übergang ist rechteckig und keine radiale Maske, die Landmassen abrundet.",
        "es": "Anchura en la que la fuente llega naturalmente al agua antes del marco. La transición es rectangular, no una máscara radial que redondea las masas.",
    },
    "archetype_height_unit": {
        "fr": "hauteur", "en": "height", "de": "Höhe", "es": "altura",
    },
    "archetype_water_threshold": {
        "fr": "Seuil eau", "en": "Water threshold", "de": "Wasserschwelle", "es": "Umbral de agua",
    },
    "archetype_mountain_threshold": {
        "fr": "Seuil montagne", "en": "Mountain threshold", "de": "Bergschwelle", "es": "Umbral de montaña",
    },
    "archetype_snow_threshold": {
        "fr": "Seuil neige", "en": "Snow threshold", "de": "Schneeschwelle", "es": "Umbral de nieve",
    },
    "archetype_water_threshold_hint": {
        "fr": "Les hauteurs inférieures ou égales à cette valeur deviennent de l’eau. Le bruit natif descend jusqu’à -30 ; la hauteur de jeu reste toutefois bloquée à 0 sous l’eau.",
        "en": "Heights at or below this value become water. Native noise reaches -30; the game heightmap is still floored at 0 underwater.",
        "de": "Höhen bis einschließlich diesem Wert werden zu Wasser. Das native Rauschen reicht bis -30; die Spiel-Höhenkarte bleibt unter Wasser bei 0.",
        "es": "Las alturas menores o iguales a este valor se convierten en agua. El ruido nativo baja hasta -30, pero la altura del juego queda limitada a 0 bajo el agua.",
    },
    "archetype_mountain_threshold_hint": {
        "fr": "À partir de cette hauteur, le terrain devient rocheux/montagneux, jusqu’au seuil de neige. Il doit rester au-dessus du seuil eau.",
        "en": "From this height, terrain becomes rocky/mountainous until the snow threshold. It must stay above the water threshold.",
        "de": "Ab dieser Höhe wird das Terrain felsig/bergig bis zur Schneeschwelle. Der Wert muss über der Wasserschwelle bleiben.",
        "es": "A partir de esta altura, el terreno se vuelve rocoso/montañoso hasta el umbral de nieve. Debe quedar por encima del umbral de agua.",
    },
    "archetype_snow_threshold_hint": {
        "fr": "À partir de cette hauteur, le terrain est classé neige. Le seuil reste au moins 2 unités au-dessus de celui de la montagne pour préserver la transition minimale.",
        "en": "From this height, terrain is classified as snow. It stays at least 2 units above the mountain threshold to preserve the minimum transition.",
        "de": "Ab dieser Höhe wird das Terrain als Schnee klassifiziert. Der Wert bleibt mindestens 2 Einheiten über der Bergschwelle, um den Mindestübergang zu erhalten.",
        "es": "A partir de esta altura, el terreno se clasifica como nieve. Se mantiene al menos 2 unidades por encima del umbral de montaña para conservar la transición mínima.",
    },
    "archetype_unimplemented_hint": {
        "fr": "Cet archétype est encore réservé : ses paramètres seront activés avec son moteur macro.",
        "en": "This archetype is still reserved: its parameters will be enabled with its macro engine.",
        "de": "Dieser Archetyp ist noch reserviert: Seine Parameter werden mit dem Makromotor aktiviert.",
        "es": "Este arquetipo sigue reservado: sus parámetros se activarán con su motor macro.",
    },
    "archetype_preview_noise": {
        "fr": "Bruit / hauteur",
        "en": "Noise / height",
        "de": "Rauschen / Höhe",
        "es": "Ruido / altura",
    },
    "archetype_preview_macro": {
        "fr": "Carte macro",
        "en": "Macro map",
        "de": "Makrokarte",
        "es": "Mapa macro",
    },
    "archetype_preview_projection": {
        "fr": "Projection",
        "en": "Projection",
        "de": "Projektion",
        "es": "Proyección",
    },
    "archetype_preview_size": {
        "fr": "Taille",
        "en": "Size",
        "de": "Größe",
        "es": "Tamaño",
    },
    "archetype_preview_macro_relaxation": {
        "fr": "Lissage de la carte macro",
        "en": "Smooth macro map",
        "de": "Makrokarte glätten",
        "es": "Suavizado del mapa macro",
    },
    "archetype_preview_macro_relaxation_hint": {
        "fr": "Désactivez-le pour accélérer les essais : seule la relaxation finale disparaît. Le raffinement natif et les interpolations propres aux noises restent actifs.",
        "en": "Disable it for faster iteration: only final relaxation is removed. Native refinement and each noise provider's interpolation remain active.",
        "de": "Für schnellere Versuche deaktivieren: Nur die letzte Relaxation entfällt. Native Verfeinerung und die Interpolation der Noise-Quellen bleiben aktiv.",
        "es": "Desactívelo para iterar más rápido: solo se elimina la relajación final. El refinamiento nativo y la interpolación de cada ruido siguen activos.",
    },
    "archetype_noise_setting_applicability_hint": {
        "fr": "Les réglages grisés ne sont pas consommés par la famille sélectionnée ; points noir/blanc remappent l’amplitude, douceur à 0 % = seuil dur, plancher/plafond bornent la sortie, la courbe asymétrique favorise une moitié du relief, puis décalage, échelle, répétition et symétrie agissent dans le cadre fini.",
        "en": "Greyed-out settings are not consumed by the selected family; black/white points remap amplitude, 0% softness means a hard threshold, floor/ceiling bound the output, curve bias favors one relief half, then offset, scale, repeat and symmetry act inside the finite frame.",
        "de": "Ausgegraute Einstellungen werden von der gewählten Familie nicht verwendet; Schwarz-/Weißpunkt remappen die Amplitude, 0 % Weichheit bedeutet eine harte Schwelle, Unter-/Obergrenze beschränken die Ausgabe, der Kurvenbias bevorzugt eine Reliefhälfte, danach wirken Versatz, Skalierung, Wiederholung und Symmetrie im endlichen Rahmen.",
        "es": "Los ajustes atenuados no los usa la familia seleccionada; los puntos negro/blanco remapean la amplitud, 0 % de suavidad significa un umbral duro, suelo/techo limitan la salida, el sesgo de curva favorece una mitad del relieve, y después desplazamiento, escala, repetición y simetría actúan dentro del marco finito.",
    },
    "archetype_preview_progress": {
        "fr": "Génération de l’aperçu : {percent} %",
        "en": "Generating preview: {percent}%",
        "de": "Vorschau wird erzeugt: {percent} %",
        "es": "Generando vista previa: {percent} %",
    },
    "archetype_preview_noise_ready": {
        "fr": "Noise map prête · macro indicative · carte exacte en cours…",
        "en": "Noise map ready · indicative macro · exact map still calculating…",
        "de": "Noise-Map bereit · indikative Makrokarte · exakte Karte wird noch berechnet…",
        "es": "Mapa de ruido lista · macro indicativa · mapa exacto en curso…",
    },
    "archetype_preview_paused": {
        "fr": "Aperçu en pause hors de l’onglet Archétype.",
        "en": "Preview paused while the Archetype tab is inactive.",
        "de": "Vorschau pausiert, solange der Archetyp-Tab inaktiv ist.",
        "es": "Vista previa en pausa mientras la pestaña Arquetipo no está activa.",
    },
    "archetype_preview_meta": {
        "fr": "Aperçu : {side}×{side} · seed {seed}",
        "en": "Preview: {side}×{side} · seed {seed}",
        "de": "Vorschau: {side}×{side} · Seed {seed}",
        "es": "Vista previa: {side}×{side} · seed {seed}",
    },
    "archetype_preview_stats": {
        "fr": "Répartition macro : Eau {water} % · Plage {beach} % · Herbe {grass} % · Montagne {mountain} % · Neige {snow} %",
        "en": "Macro split: Water {water}% · Beach {beach}% · Grass {grass}% · Mountain {mountain}% · Snow {snow}%",
        "de": "Makroverteilung: Wasser {water} % · Strand {beach} % · Gras {grass} % · Berg {mountain} % · Schnee {snow} %",
        "es": "Reparto macro: Agua {water} % · Playa {beach} % · Hierba {grass} % · Montaña {mountain} % · Nieve {snow} %",
    },
    "archetype_preview_mass": {
        "fr": "Masse terrestre principale : {share} % des terres · {count} masse(s) macro.",
        "en": "Main landmass: {share}% of land · {count} macro mass(es).",
        "de": "Größte Landmasse: {share} % der Landfläche · {count} Makromasse(n).",
        "es": "Masa terrestre principal: {share} % de la tierra · {count} masa(s) macro.",
    },
    "archetype_preview_warning": {
        "fr": "Avertissement : aucune zone observée pour {classes} dans cet aperçu.",
        "en": "Warning: no area observed for {classes} in this preview.",
        "de": "Warnung: Für {classes} wurde in dieser Vorschau kein Bereich beobachtet.",
        "es": "Advertencia: no se ha observado ninguna zona de {classes} en esta vista previa.",
    },
    "archetype_preview_invalid": {
        "fr": "Aperçu en attente : taille ou seed invalide.",
        "en": "Preview waiting: invalid size or seed.",
        "de": "Vorschau wartet: ungültige Größe oder Seed.",
        "es": "Vista previa en espera: tamaño o seed no válidos.",
    },
    "archetype_preview_unimplemented": {
        "fr": "Aperçu réservé avec cet archétype.",
        "en": "Preview reserved for this archetype.",
        "de": "Vorschau für diesen Archetyp reserviert.",
        "es": "Vista previa reservada para este arquetipo.",
    },
    "archetype_preview_water": {
        "fr": "Eau", "en": "Water", "de": "Wasser", "es": "Agua",
    },
    "archetype_preview_beach": {
        "fr": "Plage", "en": "Beach", "de": "Strand", "es": "Playa",
    },
    "archetype_preview_grass": {
        "fr": "Herbe", "en": "Grass", "de": "Gras", "es": "Hierba",
    },
    "archetype_preview_mountain": {
        "fr": "Montagne", "en": "Mountain", "de": "Berg", "es": "Montaña",
    },
    "archetype_preview_snow": {
        "fr": "Neige", "en": "Snow", "de": "Schnee", "es": "Nieve",
    },
    "decoration_hint": {
        "fr": "0 % = absente · 100 % = profil sélectionné · 500 % = maximum.",
        "en": "0% = absent · 100% = selected profile · 500% = maximum.",
        "de": "0 % = aus · 100 % = gewähltes Profil · 500 % = Maximum.",
        "es": "0 % = ausente · 100 % = perfil seleccionado · 500 % = máximo.",
    },
    "objects_grass_compatible": {
        "fr": "Placement sur variantes d’herbe",
        "en": "Place on grass variants",
        "de": "Auf Grasvarianten platzieren",
        "es": "Colocar en variantes de hierba",
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
        "fr": "0 % = aucune rivière.\n100 % = profil sélectionné ; 500 % = maximum.",
        "en": "0% = no rivers.\n100% = selected profile; 500% = maximum.",
        "de": "0 % = keine Flüsse.\n100 % = gewähltes Profil; 500 % = Maximum.",
        "es": "0 % = ningún río.\n100 % = perfil seleccionado; 500 % = máximo.",
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
    "mineral_algorithm": {
        "fr": "Méthode de gisement", "en": "Deposit method", "de": "Lagerstättenmethode", "es": "Método de yacimiento",
    },
    "occupancy_percent": {
        "fr": "Occupation minérale", "en": "Mineral occupancy", "de": "Mineralbelegung", "es": "Ocupación mineral",
    },
    "mineral_shares": {
        "fr": "Répartition", "en": "Distribution", "de": "Verteilung", "es": "Reparto",
    },
    "size_variation": {
        "fr": "Variation de taille", "en": "Size variation", "de": "Größenvariation", "es": "Variación de tamaño",
    },
    "average_quantity": {
        "fr": "Quantité moyenne", "en": "Average quantity", "de": "Durchschnittliche Menge", "es": "Cantidad media",
    },
    "fill_percent": {
        "fr": "Remplissage", "en": "Fill", "de": "Füllung", "es": "Relleno",
    },
    "near_shore": {
        "fr": "Près des côtes", "en": "Near shore", "de": "Küstennah", "es": "Cerca de la costa",
    },
    "band_thickness": {
        "fr": "Épaisseur de la bande", "en": "Band thickness", "de": "Bandbreite", "es": "Grosor de la franja",
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
        "fr": "Quota de palmiers", "en": "Palm quota", "de": "Palmenkontingent", "es": "Cupo de palmeras",
    },
    "tree_hint": {
        "fr": "0 % = aucun arbre de base · 100 % = profil sélectionné · 500 % = maximum. Les bonus de départ sont séparés.",
        "en": "0% = no base trees · 100% = selected profile · 500% = maximum. Start bonuses are separate.",
        "de": "0 % = keine Grundbäume · 100 % = gewähltes Profil · 500 % = Maximum. Startboni bleiben getrennt.",
        "es": "0 % = ningún árbol base · 100 % = perfil seleccionado · 500 % = máximo. Las bonificaciones iniciales son independientes.",
    },
    "estimated_preview": {
        "fr": "Aperçu estimé",
        "en": "Estimated preview",
        "de": "Geschätzte Vorschau",
        "es": "Vista previa estimada",
    },
    "preview_map_size": {
        "fr": "Carte : {value}",
        "en": "Map: {value}",
        "de": "Karte: {value}",
        "es": "Mapa: {value}",
    },
    "preview_global_stones": {
        "fr": "Gisements totaux : ≈ {value}",
        "en": "Total deposits: ≈ {value}",
        "de": "Gesamte Vorkommen: ≈ {value}",
        "es": "Yacimientos totales: ≈ {value}",
    },
    "preview_active_stones": {
        "fr": "Gisements exploitables : ≈ {value}",
        "en": "Usable deposits: ≈ {value}",
        "de": "Nutzbare Vorkommen: ≈ {value}",
        "es": "Yacimientos utilizables: ≈ {value}",
    },
    "preview_stock_units": {
        "fr": "Stock estimé : ≈ {value} unités",
        "en": "Estimated stock: ≈ {value} units",
        "de": "Geschätzter Vorrat: ≈ {value} Einheiten",
        "es": "Reserva estimada: ≈ {value} unidades",
    },
    "preview_groups": {
        "fr": "Groupes : ≈ {value}",
        "en": "Groups: ≈ {value}",
        "de": "Gruppen: ≈ {value}",
        "es": "Grupos: ≈ {value}",
    },
    "preview_groups_disabled": {
        "fr": "Groupes : désactivés",
        "en": "Groups: disabled",
        "de": "Gruppen: deaktiviert",
        "es": "Grupos: desactivados",
    },
    "preview_placement_note": {
        "fr": "Valeurs indicatives selon le profil, la taille de carte et les réglages.\nLe placement réel peut être inférieur si le terrain manque.",
        "en": "Indicative values based on the profile, map size and settings.\nActual placement may be lower when terrain is scarce.",
        "de": "Richtwerte nach Profil, Kartengröße und Einstellungen.\nDie tatsächliche Platzierung kann bei knappem Gelände geringer ausfallen.",
        "es": "Valores indicativos según el perfil, el tamaño del mapa y los ajustes.\nLa colocación real puede ser menor si escasea el terreno.",
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
        "fr": "0 % = aucune pierre · 100 % = profil sélectionné · maximum 200 %. Les bonus de départ sont séparés.",
        "en": "0% = no stones · 100% = selected profile · maximum 200%. Start bonuses are separate.",
        "de": "0 % = keine Steine · 100 % = gewähltes Profil · Maximum 200 %. Startboni bleiben getrennt.",
        "es": "0 % = ninguna piedra · 100 % = perfil seleccionado · máximo 200 %. Las bonificaciones iniciales son independientes.",
    },
    "building_stone_average_hint": {
        "fr": "1–12 unités par pierre. Cette moyenne est indépendante des groupes.",
        "en": "1–12 units per stone. This average is independent of groups.",
        "de": "1–12 Einheiten je Stein. Dieser Mittelwert ist unabhängig von Gruppen.",
        "es": "1–12 unidades por piedra. Esta media es independiente de los grupos.",
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
        "fr": "1–15 unités par case minéralisée. Indépendant des zones minérales de départ.",
        "en": "1–15 units per mineral-bearing cell. Independent from start mineral zones.",
        "de": "1–15 Einheiten je mineralhaltiger Zelle. Unabhängig von Startmineralzonen.",
        "es": "1–15 unidades por casilla mineralizada. Independiente de las zonas minerales iniciales.",
    },
    "coast_hint": {
        "fr": "Limite le placement des ressources en poissons à une zone proche des côtes.\nLe remplissage y est uniforme ; « Épaisseur » règle la largeur de cette bande.",
        "en": "Restricts fish-resource placement to an area near the coast.\nFill is uniform inside it; “Thickness” sets the band width.",
        "de": "Begrenzt die Platzierung von Fischressourcen auf einen küstennahen Bereich.\nDie Füllung ist darin gleichmäßig; „Dicke“ legt die Bandbreite fest.",
        "es": "Limita la colocación de recursos de peces a una zona cercana a la costa.\nEl relleno es uniforme; «Grosor» define el ancho de la franja.",
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
        "fr": "Étendre la recherche si nécessaire",
        "en": "Extend the search if needed",
        "de": "Suche bei Bedarf erweitern",
        "es": "Ampliar la búsqueda si es necesario",
    },
    "start_bonus_forest": {
        "fr": "Forêts de départ",
        "en": "Start forests",
        "de": "Startwälder",
        "es": "Bosques iniciales",
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
        "fr": "Le rayon est calculé selon les nombres d’arbres et leur espacement ; il s’élargit seulement si le terrain l’exige.",
        "en": "The radius is derived from the tree counts and spacing; it expands only when terrain requires it.",
        "de": "Der Radius wird aus Baumanzahl und Abstand abgeleitet und nur bei Bedarf erweitert.",
        "es": "El radio se calcula según la cantidad de árboles y su separación; solo se amplía si el terreno lo exige.",
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
        "fr": "Pierres de construction de départ",
        "en": "Start building stones",
        "de": "Start-Bausteine",
        "es": "Piedras de construcción iniciales",
    },
    "start_bonus_anchors": {
        "fr": "Pierres par joueur",
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
        "fr": "Répartition de la surface",
        "en": "Surface allocation",
        "de": "Flächenverteilung",
        "es": "Reparto de superficie",
    },
    "start_bonus_rocky_surface_equal": {
        "fr": "Égale",
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
        "fr": "Surface totale des cœurs",
        "en": "Total core surface",
        "de": "Gesamte Kernfläche",
        "es": "Superficie total de núcleos",
    },
    "start_bonus_rocky_family_header": {
        "fr": "Minerai",
        "en": "Mineral",
        "de": "Mineral",
        "es": "Mineral",
    },
    "start_bonus_rocky_core_header": {
        "fr": "Surface du cœur",
        "en": "Core surface",
        "de": "Kernfläche",
        "es": "Superficie del núcleo",
    },
    "start_bonus_rocky_quantity_header": {
        "fr": "Quantité / case",
        "en": "Quantity / cell",
        "de": "Menge / Zelle",
        "es": "Cantidad / casilla",
    },
    "start_bonus_rocky_mode_hint_equal": {
        "fr": "Mode égal : le rayon commun détermine la surface ; la répartition globale n’est pas utilisée.",
        "en": "Equal mode: the common radius determines the surface; global shares are not used.",
        "de": "Gleich: Der gemeinsame Radius bestimmt die Fläche; globale Anteile werden nicht verwendet.",
        "es": "Modo igual: el radio común determina la superficie; el reparto global no se usa.",
    },
    "start_bonus_rocky_mode_hint_proportional": {
        "fr": "Mode prorata : la surface totale est répartie selon Minerais › Répartition. Les quantités moyennes restent propres au bonus.",
        "en": "Prorata mode: total surface follows Minerals › Shares. Average quantities remain specific to the bonus.",
        "de": "Nach Anteilen: Die Gesamtfläche folgt Mineralien › Anteile. Durchschnittsmengen bleiben bonusbezogen.",
        "es": "Modo prorrata: la superficie total sigue Minerales › Reparto. Las cantidades medias son propias del bono.",
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
        "fr": "Chaque zone possède sa propre quantité moyenne par case ; elle est indépendante de Minerais › Quantité moyenne.",
        "en": "Each zone has its own average quantity per cell; it is independent from Minerals › Average quantity.",
        "de": "Jede Zone hat ihre eigene Durchschnittsmenge je Zelle; sie ist unabhängig von Mineralien › Durchschnittliche Menge.",
        "es": "Cada zona tiene su propia cantidad media por casilla; es independiente de Minerales › Cantidad media.",
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
        "fr": "Lac, poissons et rivières",
        "en": "Lake, fish and rivers",
        "de": "See, Fische und Flüsse",
        "es": "Lago, peces y ríos",
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
        "fr": "Rayon de contrôle de l’eau",
        "en": "Water check radius",
        "de": "Radius der Wasserprüfung",
        "es": "Radio de control del agua",
    },
    "start_bonus_river_target": {
        "fr": "Rivières cibles par lac",
        "en": "Target rivers per lake",
        "de": "Zielflüsse je See",
        "es": "Ríos objetivo por lago",
    },
    "start_bonus_fish_fill": {
        "fr": "Remplissage en poissons",
        "en": "Fish fill",
        "de": "Fischfüllung",
        "es": "Relleno de peces",
    },
    "start_bonus_lake_settings": {
        "fr": "Lac", "en": "Lake", "de": "See", "es": "Lago",
    },
    "start_bonus_river_settings": {
        "fr": "Rivières", "en": "Rivers", "de": "Flüsse", "es": "Ríos",
    },
    "start_bonus_fish_settings": {
        "fr": "Poissons", "en": "Fish", "de": "Fische", "es": "Peces",
    },
    "start_bonus_fish_fill_hint": {
        "fr": "Pourcentage des cases d’eau du lac qui reçoivent des ressources en poissons.",
        "en": "Percentage of the lake’s water cells that receive fish resources.",
        "de": "Prozentsatz der Wasserzellen des Sees mit Fischressourcen.",
        "es": "Porcentaje de las casillas de agua del lago que reciben recursos de peces.",
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
