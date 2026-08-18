# Settlers III MapGen

> Générateur procédural expérimental pour **The Settlers III**, construit à partir de reverse-engineering des formats `.EDM`, `.MAP` et `.SAV`, d'analyses du générateur natif et de nombreuses validations dans l'éditeur et en jeu.

## Présentation du projet

**Settlers III MapGen** a pour objectif de créer, analyser et à terme éditer des cartes Settlers III avec une génération procédurale reproductible et contrôlable.

Le projet poursuit trois objectifs complémentaires :

- **préserver le comportement historique du jeu** grâce au mode **Legacy**, qui sert de référence native et de base de reverse-engineering ;
- **proposer une génération améliorée** grâce au mode **Upgraded**, qui applique les règles de gameplay, de morphologie, de ressources et de sécurité affinées au cours du projet ;
- **ouvrir progressivement la génération à l'utilisateur** avec un futur mode **Custom**, où les paramètres pourront être ajustés manuellement tout en conservant les garde-fous critiques.

La forme générale de la carte est volontairement séparée du mode de génération. Les **archétypes** définissent la macro-géographie (continent, grandes îles, petites îles, etc.), tandis que le **mode de génération** contrôle le relief, les zones de terrain, l'hydrologie détaillée, les ressources, les objets, les positions de départ, la balance et les validations.

Le projet repose sur une règle importante : les **positions de départ des joueurs sont placées très tôt** dans le pipeline. Le reste de la génération doit ensuite s'adapter à ces zones réservées afin de réduire les positions invalides et de permettre un meilleur équilibrage des ressources.

Les aperçus visuels sont toujours des rendus déterministes issus des vraies données de carte ; aucune image de carte fictive n'est utilisée.

## État actuel — v1.3.2

La GUI est fonctionnelle sous Windows et permet actuellement :

- génération **Legacy** et **Upgraded** sur l'archétype **Continental 768×768** ;
- choix du nombre de joueurs et du seed ;
- seed aléatoire ;
- barre de progression ;
- import `.EDM`, `.MAP` et `.SAV` ;
- export `.EDM` / `.MAP` pour les configurations actuellement sérialisables ;
- aperçu Global / Heightmap / Ressources / Territoires ;
- zoom de l'aperçu ;
- validations automatiques ;
- métadonnées, pipeline et premières statistiques ;
- tailles natives visibles avec adaptation automatique du nombre maximal de joueurs.
- starts avec halo conservateur destiné à réduire les positions refusées par l'éditeur ;
- neige intérieure non marchable (`129/128`) ;
- transitions de marais reconstruites et validées automatiquement.

> Les tailles autres que 768 sont visibles dans l'interface mais leur génération reste volontairement bloquée tant que leur calibration n'est pas validée. Le writer `.SAV` n'est pas encore implémenté : un SAV importé peut être analysé et copié, mais le programme n'invente pas un nouveau SAV.

## Modes de génération

### Legacy

Mode orienté fidélité au générateur original de Settlers III et au corpus natif analysé. Il sert aussi de baseline de comparaison pour le reverse-engineering.

### Upgraded

Preset amélioré du projet. Il intègre les règles validées au fil des tests et du long-play : starts précoces, hydrologie corrigée, poissons et minerais rééquilibrés, SmallTree84, Building Stones avec footprint, décorations contrôlées, règles de transitions et validators spécifiques.

La matrice détaillée est disponible dans `references/SETTLERS3_UPGRADED_RULE_MATRIX_v1.md`.

### Custom

Mode futur permettant d'exposer les paramètres de génération à l'utilisateur. Il est actuellement réservé et non implémenté.

## Archétypes

- **Continental** — implémenté ;
- **Large Islands** — prévu ;
- **Small Islands** — prévu ;
- d'autres macro-formes pourront être ajoutées sans dupliquer le moteur de génération.

L'archétype décrit principalement la **forme globale terre/eau**. Les objets, ressources, formes locales des zones, balance et logique de starts appartiennent au mode de génération.

## Architecture des starts

Ordre conceptuel actuel :

```text
MapConfig
  ↓
Archetype : macro-layout
  ↓
Placement précoce des starts
  ↓
Réservation des zones techniques
  ↓
Relief / biomes / hydrologie détaillée
  ↓
Ressources et balance locale
  ↓
Objets / décorations
  ↓
Hydrologie finale / poissons
  ↓
Validators
  ↓
Export
```

Une passe tardive ne doit pas invalider un start réservé. Elle doit contourner la zone ou faire échouer explicitement la génération.

## Morphologie Upgraded

La première implémentation exécutable d'Upgraded 768 utilise encore le checkpoint terrain/height validé comme référence de morphologie locale. Cela évite de réinventer des formes déjà validées.

La prochaine grosse étape de génération est de **généraliser cette morphologie Upgraded** afin de produire de nouvelles formes fraîches et compatibles avec plusieurs tailles et archétypes sans dépendre d'un unique checkpoint 768.

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

Les validators du programme sont des **garde-fous de non-régression**. Un PASS signifie que les règles encodées sont respectées ; il ne remplace pas une validation dans l'éditeur officiel ou en jeu.

La hiérarchie de validation du projet reste : parser/checksum → éditeur → View Map/smoke test → SAV runtime → long-play.

## Documentation technique

Les références principales sont dans `references/`. En particulier :

- `SETTLERS3_PREGEN_READ_FIRST.md` — point d'entrée obligatoire avant toute modification/génération ;
- `SETTLERS3_MAPGEN_REFERENCE_v15_LONGPLAY_RULES.md` — règles canoniques ;
- `SETTLERS3_UPGRADED_RULE_MATRIX_v1.md` — correspondance règles Upgraded / implémentation / validators ;
- `SETTLERS3_EDM_MAP_FORMAT_REFERENCE_v3.md` — format EDM/MAP ;
- `SETTLERS3_SAV_FORMAT_REFERENCE_v1.md` — lecture SAV ;
- `TODO_MAPGEN.md` — feuille de route courante.

## Versioning

L'historique Git rétroactif est conservé depuis la v1.0 avec des tags de version. Les nouvelles releases doivent mettre à jour le code, le changelog, les tests et la documentation avant création du tag.
