"""Known display names used by the map-cell inspector."""

MINERAL_NAMES = {
    0x10: "Coal", 0x20: "Iron", 0x30: "Gold", 0x40: "Gemstones", 0x50: "Sulfur",
}

TERRAIN_NAMES = {
    16: "Grass", 18: "Grass detail 1", 19: "Grass detail 2",
    22: "Agricultural runtime", 24: "Yellow Grass",
    28: "Worked/Path runtime", 32: "Rocky", 34: "Rocky grass patch",
    35: "Rock/Snow transition", 48: "Shore", 128: "Snow",
    129: "Snow transition", 96: "River 1", 97: "River 2",
    98: "River 3", 99: "River 4",
}

OBJECT_NAMES = {
    **{i: f"Big Stone {i}" for i in range(1, 9)},
    **{i: f"Stone {i - 8}" for i in range(9, 13)},
    **{i: f"Border Stone {i - 12}" for i in range(13, 21)},
    **{i: f"Small Stone {i - 20}" for i in range(21, 29)},
    **{i: f"Wreck {i - 28}" for i in range(29, 34)},
    34: "Grave",
    **{i: f"Small Plant {i - 34}" for i in range(35, 38)},
    **{i: f"Toadstool {i - 37}" for i in range(38, 41)},
    **{i: f"Tree Stump {i - 40}" for i in range(41, 43)},
    **{i: f"Dead Tree {i - 42}" for i in range(43, 45)},
    **{i: f"Cactus {i - 44}" for i in range(45, 49)},
    49: "Skeleton",
    **{i: f"Small Flower {i - 49}" for i in range(50, 53)},
    **{i: f"Small Bush {i - 52}" for i in range(53, 57)},
    **{i: f"Bush {i - 56}" for i in range(57, 62)},
    **{i: f"Reed {i - 61}" for i in range(62, 68)},
    68: "Birch 1", 69: "Birch 2", 70: "Elm 1", 71: "Elm 2", 72: "Oak",
    78: "Palm 1", 79: "Palm 2", 84: "Small Tree",
    **{i: f"Wheat {i - 84}" for i in range(85, 94)},
    **{i: f"Vine {i - 93}" for i in range(94, 103)},
    **{i: f"Rice {i - 102}" for i in range(103, 111)},
    **{i: f"Reef {i - 110}" for i in range(111, 115)},
    **{i: f"Building Stone {i - 114}" for i in range(115, 128)},
}

# Data-mapping entries confirmed by the controlled 208–239 and 240–255
# calibrations.  The three crash-prone probes (215, 223 and 231) deliberately
# remain unresolved instead of being presented as valid gameplay objects.
OBJECT_NAMES.update({
    **{i: f"Tree stump — variant {i - 207}" for i in range(208, 215)},
    **{i: f"Tree sapling — stage 2 — variant {i - 215}" for i in range(216, 221)},
    221: "Palm sapling — stage 2",
    222: "Tree sapling — stage 2 — variant 7",
    **{i: f"Tree sapling — stage 1 — variant {i - 223}" for i in range(224, 229)},
    229: "Palm sapling — stage 1",
    230: "Tree sapling — stage 1 — variant 7",
    232: "Resource panel — none",
    233: "Resource panel — coal",
    234: "Resource panel — abundant coal",
    235: "Resource panel — iron",
    236: "Resource panel — abundant iron",
    237: "Resource panel — gold",
    238: "Resource panel — abundant gold",
    239: "Resource panel — gemstones",
    240: "Mineral discovery panel 1",
    241: "Mineral discovery panel 2",
    242: "Mineral discovery panel 3",
    243: "Burning tree — stage 1",
    244: "Burning tree — stage 2",
    245: "Burning tree — stage 3",
    246: "Burning tree — stage 4",
    247: "Bee nest — stage 1",
    248: "Bee nest — stage 2",
    249: "Bee nest — stage 3",
    250: "Bee nest — stage 4",
    251: "Bee nest — stage 5",
    252: "Bee nest — stage 6",
    253: "Bee nest — stage 7",
    254: "Red territory marker",
    255: "Red flag",
})

# The original tables above remain English-compatible public constants for
# existing callers.  The inspector needs a real localized lookup, however;
# displaying a tuple or silently falling back to ``?`` makes imported and
# generated maps unnecessarily hard to read.  These tables cover every known
# terrain/object entry and use an explicit language fallback for unresolved
# IDs.
MINERAL_NAMES_I18N = {
    'fr': {0x10: 'Charbon', 0x20: 'Fer', 0x30: 'Or', 0x40: 'Gemmes', 0x50: 'Soufre'},
    'en': {0x10: 'Coal', 0x20: 'Iron', 0x30: 'Gold', 0x40: 'Gemstones', 0x50: 'Sulfur'},
    'de': {0x10: 'Kohle', 0x20: 'Eisen', 0x30: 'Gold', 0x40: 'Edelsteine', 0x50: 'Schwefel'},
    'es': {0x10: 'Carbón', 0x20: 'Hierro', 0x30: 'Oro', 0x40: 'Gemas', 0x50: 'Azufre'},
}

TERRAIN_NAMES_I18N = {}


def _set_terrain_name(terrain, fr, en, de, es):
    TERRAIN_NAMES_I18N[int(terrain)] = {'fr': fr, 'en': en, 'de': de, 'es': es}


for _water_id in range(8):
    _set_terrain_name(
        _water_id,
        f'Eau {_water_id + 1}',
        f'Water {_water_id + 1}',
        f'Wasser {_water_id + 1}',
        f'Agua {_water_id + 1}',
    )

for _terrain_row in (
    (16, 'Herbe', 'Grass', 'Gras', 'Hierba'),
    (18, 'Détail herbe 1', 'Grass detail 1', 'Grasdetail 1', 'Detalle de hierba 1'),
    (19, 'Détail herbe 2', 'Grass detail 2', 'Grasdetail 2', 'Detalle de hierba 2'),
    (20, 'Transition herbe/désert', 'Grass/desert transition', 'Gras-Wüste-Übergang', 'Transición hierba/desierto'),
    (21, 'Transition herbe/marais', 'Grass/swamp transition', 'Gras-Sumpf-Übergang', 'Transición hierba/pantano'),
    (22, 'Agriculture runtime', 'Runtime agriculture', 'Laufzeit-Landwirtschaft', 'Agricultura de ejecución'),
    (23, 'Boue', 'Mud', 'Schlamm', 'Barro'),
    (24, 'Herbe sèche', 'Dry grass', 'Trockenes Gras', 'Hierba seca'),
    (28, 'Chemin runtime', 'Runtime path', 'Laufzeitweg', 'Camino de ejecución'),
    (32, 'Roche', 'Rocky', 'Fels', 'Roca'),
    (33, 'Transition roche 2', 'Rock transition 2', 'Felsübergang 2', 'Transición de roca 2'),
    (34, 'Patch d’herbe rocheuse', 'Rocky grass patch', 'Felsgrasfleck', 'Parche de hierba rocosa'),
    (35, 'Transition roche/neige', 'Rock/snow transition', 'Fels-Schnee-Übergang', 'Transición roca/nieve'),
    (48, 'Rivage', 'Shore', 'Küste', 'Costa'),
    (64, 'Désert', 'Desert', 'Wüste', 'Desierto'),
    (65, 'Transition désert', 'Desert transition', 'Wüstenübergang', 'Transición de desierto'),
    (80, 'Marais', 'Swamp', 'Sumpf', 'Pantano'),
    (81, 'Transition marais', 'Swamp transition', 'Sumpfübergang', 'Transición de pantano'),
    (96, 'Rivière 1', 'River 1', 'Fluss 1', 'Río 1'),
    (97, 'Rivière 2', 'River 2', 'Fluss 2', 'Río 2'),
    (98, 'Rivière 3', 'River 3', 'Fluss 3', 'Río 3'),
    (99, 'Rivière 4', 'River 4', 'Fluss 4', 'Río 4'),
    (128, 'Neige', 'Snow', 'Schnee', 'Nieve'),
    (129, 'Transition neige', 'Snow transition', 'Schneeübergang', 'Transición de nieve'),
    (144, 'Boue / transition 144', 'Mud / transition 144', 'Schlamm / Übergang 144', 'Barro / transición 144'),
    (145, 'Boue / transition 145', 'Mud / transition 145', 'Schlamm / Übergang 145', 'Barro / transición 145'),
):
    _set_terrain_name(*_terrain_row)


# Fill the English side from the compatibility table before applying the
# semantic translations below.  This also makes newly confirmed English-only
# names visible instead of losing them in the localized inspector.
OBJECT_NAMES_I18N = {
    int(_object_id): {'fr': str(_object_name), 'en': str(_object_name),
                      'de': str(_object_name), 'es': str(_object_name)}
    for _object_id, _object_name in OBJECT_NAMES.items()
}


def _set_object_name(object_id, fr, en, de, es):
    OBJECT_NAMES_I18N[int(object_id)] = {'fr': fr, 'en': en, 'de': de, 'es': es}
    # These entries were absent from the old English compatibility table even
    # though their semantic family is confirmed by the calibration notes.
    OBJECT_NAMES.setdefault(int(object_id), en)


def _set_numbered_object_family(start, stop, fr, en, de, es):
    for _object_id in range(start, stop + 1):
        number = _object_id - start + 1
        _set_object_name(
            _object_id,
            f'{fr} {number}', f'{en} {number}',
            f'{de} {number}', f'{es} {number}',
        )


_set_numbered_object_family(1, 8, 'Grosse pierre', 'Big Stone', 'Großer Stein', 'Piedra grande')
_set_numbered_object_family(9, 12, 'Pierre décorative', 'Stone', 'Stein', 'Piedra')
_set_numbered_object_family(13, 20, 'Pierre de bordure', 'Border Stone', 'Randstein', 'Piedra de borde')
_set_numbered_object_family(21, 28, 'Petite pierre', 'Small Stone', 'Kleiner Stein', 'Piedra pequeña')
_set_numbered_object_family(29, 33, 'Épave', 'Wreck', 'Wrack', 'Naufragio')
_set_object_name(34, 'Tombe', 'Grave', 'Grab', 'Tumba')
_set_numbered_object_family(35, 37, 'Petite plante', 'Small Plant', 'Kleine Pflanze', 'Planta pequeña')
_set_numbered_object_family(38, 40, 'Champignon', 'Toadstool', 'Pilz', 'Hongo')
_set_numbered_object_family(41, 42, 'Souche', 'Tree Stump', 'Baumstumpf', 'Tocón')
_set_numbered_object_family(43, 44, 'Arbre mort', 'Dead Tree', 'Toter Baum', 'Árbol muerto')
_set_numbered_object_family(45, 48, 'Cactus', 'Cactus', 'Kaktus', 'Cactus')
_set_object_name(49, 'Squelette', 'Skeleton', 'Skelett', 'Esqueleto')
_set_numbered_object_family(50, 52, 'Petite fleur', 'Small Flower', 'Kleine Blume', 'Flor pequeña')
_set_numbered_object_family(53, 56, 'Petit buisson', 'Small Bush', 'Kleiner Busch', 'Arbusto pequeño')
_set_numbered_object_family(57, 61, 'Buisson', 'Bush', 'Busch', 'Arbusto')
_set_numbered_object_family(62, 67, 'Roseau', 'Reed', 'Schilf', 'Junco')

_set_object_name(68, 'Bouleau 1', 'Birch 1', 'Birke 1', 'Abedul 1')
_set_object_name(69, 'Bouleau 2', 'Birch 2', 'Birke 2', 'Abedul 2')
_set_object_name(70, 'Orme 1', 'Elm 1', 'Ulme 1', 'Olmo 1')
_set_object_name(71, 'Orme 2', 'Elm 2', 'Ulme 2', 'Olmo 2')
_set_object_name(72, 'Chêne', 'Oak', 'Eiche', 'Roble')
for _object_id in (73, 74, 75, 76, 77, 80, 81):
    _set_object_name(
        _object_id,
        f'Arbre adulte {_object_id}', f'Adult tree {_object_id}',
        f'Erwachsener Baum {_object_id}', f'Árbol adulto {_object_id}',
    )
_set_object_name(78, 'Palmier 1', 'Palm 1', 'Palme 1', 'Palmera 1')
_set_object_name(79, 'Palmier 2', 'Palm 2', 'Palme 2', 'Palmera 2')
_set_object_name(84, 'Pousse d’arbre', 'Small Tree', 'Kleiner Baum', 'Árbol pequeño')

for _object_id in range(85, 94):
    _set_object_name(_object_id, f'Blé {_object_id - 84}', f'Wheat {_object_id - 84}', f'Weizen {_object_id - 84}', f'Trigo {_object_id - 84}')
for _object_id in range(94, 103):
    _set_object_name(_object_id, f'Vigne {_object_id - 93}', f'Vine {_object_id - 93}', f'Weinrebe {_object_id - 93}', f'Vid {_object_id - 93}')
for _object_id in range(103, 111):
    _set_object_name(_object_id, f'Riz {_object_id - 102}', f'Rice {_object_id - 102}', f'Reis {_object_id - 102}', f'Arroz {_object_id - 102}')
for _object_id in range(111, 115):
    _set_object_name(_object_id, f'Récif {_object_id - 110}', f'Reef {_object_id - 110}', f'Riff {_object_id - 110}', f'Arrecife {_object_id - 110}')
for _object_id in range(115, 128):
    _set_object_name(_object_id, f'Pierre de construction {_object_id - 114}', f'Building Stone {_object_id - 114}', f'Baustein {_object_id - 114}', f'Piedra de construcción {_object_id - 114}')

for _object_id in range(208, 215):
    _set_object_name(_object_id, f'Souche d’arbre — variante {_object_id - 207}', f'Tree stump — variant {_object_id - 207}', f'Baumstumpf — Variante {_object_id - 207}', f'Tocón de árbol — variante {_object_id - 207}')
for _object_id in range(216, 221):
    _set_object_name(_object_id, f'Pousse d’arbre — stade 2 — variante {_object_id - 215}', f'Tree sapling — stage 2 — variant {_object_id - 215}', f'Baumsetzling — Stufe 2 — Variante {_object_id - 215}', f'Retoño — etapa 2 — variante {_object_id - 215}')
_set_object_name(221, 'Pousse de palmier — stade 2', 'Palm sapling — stage 2', 'Palmensetzling — Stufe 2', 'Retoño de palmera — etapa 2')
_set_object_name(222, 'Pousse d’arbre — stade 2 — variante 7', 'Tree sapling — stage 2 — variant 7', 'Baumsetzling — Stufe 2 — Variante 7', 'Retoño — etapa 2 — variante 7')
for _object_id in range(224, 229):
    _set_object_name(_object_id, f'Pousse d’arbre — stade 1 — variante {_object_id - 223}', f'Tree sapling — stage 1 — variant {_object_id - 223}', f'Baumsetzling — Stufe 1 — Variante {_object_id - 223}', f'Retoño — etapa 1 — variante {_object_id - 223}')
_set_object_name(229, 'Pousse de palmier — stade 1', 'Palm sapling — stage 1', 'Palmensetzling — Stufe 1', 'Retoño de palmera — etapa 1')
_set_object_name(230, 'Pousse d’arbre — stade 1 — variante 7', 'Tree sapling — stage 1 — variant 7', 'Baumsetzling — Stufe 1 — Variante 7', 'Retoño — etapa 1 — variante 7')

_set_object_name(232, 'Panneau de ressource — aucune', 'Resource panel — none', 'Ressourcenpanel — keine', 'Panel de recursos — ninguno')
_set_object_name(233, 'Panneau de ressource — charbon', 'Resource panel — coal', 'Ressourcenpanel — Kohle', 'Panel de recursos — carbón')
_set_object_name(234, 'Panneau de ressource — charbon abondant', 'Resource panel — abundant coal', 'Ressourcenpanel — reichlich Kohle', 'Panel de recursos — carbón abundante')
_set_object_name(235, 'Panneau de ressource — fer', 'Resource panel — iron', 'Ressourcenpanel — Eisen', 'Panel de recursos — hierro')
_set_object_name(236, 'Panneau de ressource — fer abondant', 'Resource panel — abundant iron', 'Ressourcenpanel — reichlich Eisen', 'Panel de recursos — hierro abundante')
_set_object_name(237, 'Panneau de ressource — or', 'Resource panel — gold', 'Ressourcenpanel — Gold', 'Panel de recursos — oro')
_set_object_name(238, 'Panneau de ressource — or abondant', 'Resource panel — abundant gold', 'Ressourcenpanel — reichlich Gold', 'Panel de recursos — oro abundante')
_set_object_name(239, 'Panneau de ressource — gemmes', 'Resource panel — gemstones', 'Ressourcenpanel — Edelsteine', 'Panel de recursos — gemas')
for _object_id in range(240, 243):
    _set_object_name(_object_id, f'Panneau de découverte de minerai {_object_id - 239}', f'Mineral discovery panel {_object_id - 239}', f'Mineral-Entdeckungspanel {_object_id - 239}', f'Panel de descubrimiento de mineral {_object_id - 239}')
for _object_id in range(243, 247):
    _set_object_name(_object_id, f'Arbre en feu — stade {_object_id - 242}', f'Burning tree — stage {_object_id - 242}', f'Brennender Baum — Stufe {_object_id - 242}', f'Árbol en llamas — etapa {_object_id - 242}')
for _object_id in range(247, 254):
    _set_object_name(_object_id, f'Nid d’abeilles — stade {_object_id - 246}', f'Bee nest — stage {_object_id - 246}', f'Bienennest — Stufe {_object_id - 246}', f'Nido de abejas — etapa {_object_id - 246}')
_set_object_name(254, 'Borne de territoire rouge', 'Red territory marker', 'Rote Gebietsmarkierung', 'Marcador de territorio rojo')
_set_object_name(255, 'Drapeau rouge', 'Red flag', 'Rote Flagge', 'Bandera roja')


def _language_or_default(lang):
    return lang if lang in ('fr', 'en', 'de', 'es') else 'en'


def localized_terrain_name(terrain, lang='fr'):
    lang = _language_or_default(lang)
    terrain = int(terrain)
    entry = TERRAIN_NAMES_I18N.get(terrain)
    if entry:
        return entry.get(lang, entry['en'])
    prefix = {'fr': 'Terrain', 'en': 'Terrain', 'de': 'Gelände', 'es': 'Terreno'}[lang]
    return f'{prefix} {terrain}'


def localized_object_name(object_id, lang='fr'):
    lang = _language_or_default(lang)
    object_id = int(object_id)
    if object_id == 0:
        return {'fr': 'Aucun objet', 'en': 'No object', 'de': 'Kein Objekt', 'es': 'Ningún objeto'}[lang]
    entry = OBJECT_NAMES_I18N.get(object_id)
    if entry:
        return entry.get(lang, entry['en'])
    unknown = {'fr': 'Objet inconnu', 'en': 'Unknown object', 'de': 'Unbekanntes Objekt', 'es': 'Objeto desconocido'}[lang]
    return f'{unknown} {object_id}'


def localized_resource_text(terrain, raw, lang='fr'):
    lang = _language_or_default(lang)
    terrain = int(terrain)
    raw = int(raw)
    family = raw & 0xF0
    quantity = raw & 0x0F
    if quantity <= 0:
        return '—'
    if family == 0 and terrain in range(8):
        fish = {'fr': 'Poisson', 'en': 'Fish', 'de': 'Fisch', 'es': 'Pez'}[lang]
        return f'{fish} {quantity}'
    mineral = MINERAL_NAMES_I18N.get(lang, MINERAL_NAMES_I18N['en']).get(family)
    if mineral:
        return f'{mineral} {quantity}'
    resource = {'fr': 'Ressource inconnue', 'en': 'Unknown resource', 'de': 'Unbekannte Ressource', 'es': 'Recurso desconocido'}[lang]
    return f'{resource} 0x{family:02X} {quantity}'
