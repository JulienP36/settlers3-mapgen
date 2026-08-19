# Settlers III MapGen

> Générateur procédural expérimental pour **The Settlers III**, construit à partir de reverse-engineering des formats `.EDM`, `.MAP` et `.SAV`, d'analyses du générateur natif et de nombreuses validations dans l'éditeur et en jeu.

## Présentation du projet

**Settlers III MapGen** a pour objectif de créer, analyser et à terme éditer des cartes Settlers III avec une génération procédurale reproductible et contrôlable.

Le projet poursuit trois objectifs complémentaires :

- **préserver le comportement historique du jeu** grâce au mode **Legacy**, qui sert de référence native et de base de reverse-engineering ;
- **proposer une génération améliorée** grâce au mode **Upgraded**, construit sur la même base mais avec des améliorations volontaires de gameplay/équilibrage ;
- **ouvrir progressivement la génération à l'utilisateur** avec un futur mode **Custom** et des **modificateurs orthogonaux** combinables avec Legacy/Upgraded.

La forme générale de la carte est séparée du mode de génération. Les **archétypes** définissent la macro-géographie ; le **mode** contrôle les règles de contenu, hydrologie, ressources, objets, balance et validations.

Les **positions de départ sont placées très tôt**. Toutes les passes suivantes doivent respecter les zones réservées afin d'éviter les anciennes positions invalides/crashs.

Les aperçus visuels sont toujours des rendus déterministes issus des vraies données EDM/MAP/SAV ; aucune image fictive de carte n'est utilisée.

## État actuel — v1.5 CANDIDATE

- **v1.3.2** : moteur de stabilité validé extérieurement sur Continental 768×768 Legacy/Upgraded 4P/20P (starts acceptés, aucun crash View Map/in-game).
- **v1.4** : interface/visualisation validée (thème sombre, projection parallélogramme, overlays, zoom/drag, territoires initiaux, labels joueurs).
- **v1.5** : nouvelle candidate moteur intégrant l'audit complet Legacy/Upgraded, les nouveaux clusters de départ et les corrections Building Stones. Elle doit encore être validée dans l'éditeur/View Map avant promotion/tag stable.

Le correctif **Goods Default** est déjà validé et conservé : `Legacy=Medium/2`, `Upgraded=High/3`, fallback sûr Medium.

### Principaux changements v1.5

- séparation explicite **Legacy / Upgraded** ;
- macro-morphologie commune par archétype ;
- neige commune `Rocky32 -> 35 -> 129 -> Snow128`, Terrain34 conservé comme variante Rocky minéralisable ;
- hydrologie Upgraded : suppression/redistribution des plans d'eau 1–4 cellules + trimming de rivière size-scaled ;
- minerais Upgraded : ~90 % du support montagneux accessible, ratios natifs empiriques, v7 no-gap, stock/case augmenté ;
- arbres `68..77 + 80..81` dans les deux modes ; Palms `78..79` comptées comme bois ; Upgraded ~130 % volume natif + SmallTree84 séparé ;
- Mud natif en Legacy, désactivé en Upgraded ; Swamp Upgraded ~+30 % ;
- petites plantes/fleurs/buissons/champignons identiques dans les deux modes ;
- Decorative Stones natives en Legacy, réduites en Upgraded ; reefs uniquement Upgraded ;
- **clusters de départ Upgraded sur la bordure du territoire initial (~HEX34)** : forêt `41 adultes + 21 SmallTree84`, pierres `8 ancres / 84 unités`, hors quotas globaux ;
- Building Stones `115..126` variées au lieu d'un état uniforme ;
- environ **20 Building Stone 13 / ID127** vides générées globalement sur 768 ; elles comptent dans la densité d'ancres mais jamais dans le stock exploitable ;
- **ID127 est constructible** : son ancien footprint 7 cellules est libéré, contrairement aux états actifs ;
- nouveaux validators dédiés au stock réel, à la variété `115..127` et à la constructibilité d'ID127.

> Les tailles autres que 768 sont visibles dans l'interface mais leur génération reste volontairement bloquée tant que leur calibration n'est pas validée. Le writer `.SAV` n'est pas encore implémenté : un SAV importé peut être analysé et copié, mais le programme n'invente pas un nouveau SAV.

## Interface actuelle

La GUI v1.5 reprend toute l'UX validée de v1.4 :

- génération **Legacy** / **Upgraded**, Continental 768×768 ;
- seed + nombre de joueurs ;
- import `.EDM`, `.MAP`, `.SAV` ;
- export `.EDM` / `.MAP` ;
- vues Global / Heightmap / Ressources / Territoires ;
- thème Sombre / Clair ;
- overlays avec opacité ;
- projection Carrée / Parallélogramme ;
- zoom, molette et drag ;
- contour des territoires initiaux et labels joueurs ;
- validations, métadonnées, pipeline et statistiques ;
- exports nommés `MapGenV1_5`.

## Modes de génération

### Legacy

Mode orienté fidélité au générateur original. Les différences volontaires sont limitées aux correctifs de stabilité, sérialisation, validité des starts et exceptions pratiques explicitement validées.

### Upgraded

Part du socle Legacy puis ajoute les améliorations assumées : hydrologie pratique, minerais plus exploitables, contenu/balance augmentés, clusters de départ, réduction des obstacles décoratifs et reefs rares contrôlés.

La référence canonique actuelle est :

`references/SETTLERS3_LEGACY_UPGRADED_AUDIT_20260819.md`

### Custom

Mode futur permettant d'exposer les paramètres de génération à l'utilisateur. Il reste réservé/non défini proprement.

## Modificateurs futurs

Les options transversales ne doivent pas créer de nouveaux modes. Elles seront combinables avec Legacy/Upgraded.

Idées actuelles :

- **Barebone** — retire seulement le cosmétique sans fonction gameplay ;
- **Densité de forêt** ;
- **Starting Crops** expérimental ;
- **Montagnes plus réalistes** ;
- **Réaliste** — distributions écologiques : arbres/plantes favorisés près de l'eau, champignons près des marais/sols humides, végétation modulée par biome/relief/humidité, sans sacrifier constructibilité ni gameplay.

## Archétypes

- **Continental** — implémenté ;
- **Large Islands** — prévu ;
- **Small Islands** — prévu.

L'archétype décrit la macro-forme. Les objets, ressources, balance et règles de starts appartiennent au mode/modificateurs.

## Architecture des starts

```text
MapConfig
  ↓
Archetype : macro-layout
  ↓
Placement précoce des starts
  ↓
Réservation des zones techniques
  ↓
Biomes / hydrologie / ressources
  ↓
Objets + bonus locaux
  ↓
Accessibility finale
  ↓
Validators
  ↓
Export
```

Une passe tardive ne doit jamais invalider silencieusement un start réservé.

## Installation Windows

Premier lancement :

```bat
install_and_run.bat
```

Si Python n'est pas encore installé :

```bat
install_python_and_run.bat
```

Lancements suivants :

```bat
run_gui.bat
```

Dépendances Python principales : NumPy, SciPy et Pillow.

## Validation

Les validators sont des garde-fous de non-régression ; ils ne remplacent pas le jeu.

Hiérarchie de validation :

`parser/checksum → éditeur → View Map/smoke → SAV runtime → long-play`

La v1.5 reste **candidate** jusqu'au prochain contrôle officiel d'une génération fraîche, notamment sur les clusters de start, la variété Building Stones et la constructibilité des ID127.

## Documentation technique

Références principales :

- `references/SETTLERS3_PREGEN_READ_FIRST.md` ;
- `references/SETTLERS3_LEGACY_UPGRADED_AUDIT_20260819.md` ;
- `references/SETTLERS3_MAPGEN_REFERENCE_v15_LONGPLAY_RULES.md` ;
- `references/SETTLERS3_EDM_MAP_FORMAT_REFERENCE_v3.md` ;
- `TODO_MAPGEN.md` ;
- `RELEASE_VALIDATION.md`.

## Versioning

Les releases doivent mettre à jour code, tests, changelog et documentation avant création du tag. **v1.4 est stable ; v1.5 est candidate tant que sa validation externe n'est pas terminée.**
