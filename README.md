# Settlers III MapGen

**Français** · [English](README_EN.md)

> Générateur procédural expérimental pour **The Settlers III**, construit à partir de reverse-engineering des formats `.EDM`, `.MAP` et `.SAV`, d'analyses du générateur natif et de nombreuses validations dans l'éditeur et en jeu.

> **Note de développement / transparence :** ce projet est conçu, dirigé, testé et validé humainement, avec un usage important de **ChatGPT / OpenAI comme assistance d’implémentation**, notamment pour le backend, l’analyse technique et les outils de reverse-engineering. Cette assistance fait partie explicitement du processus de développement du projet.

## Présentation du projet

**Settlers III MapGen** a pour objectif de créer, analyser et à terme éditer des cartes Settlers III avec une génération procédurale reproductible et contrôlable.

Le projet poursuit trois objectifs complémentaires :

- **préserver le comportement historique du jeu** grâce au mode **Legacy**, qui sert de référence native et de base de reverse-engineering ;
- **proposer une génération améliorée** grâce au mode **Upgraded**, qui applique les règles de gameplay, de morphologie, de ressources et de sécurité affinées au cours du projet ;
- **ouvrir progressivement la génération à l'utilisateur** avec un futur mode **Custom**, où les paramètres pourront être ajustés manuellement tout en conservant les garde-fous critiques.

La forme générale de la carte est volontairement séparée du mode de génération. Les **archétypes** définissent la macro-géographie (continent, grandes îles, petites îles, etc.), tandis que le **mode de génération** contrôle le relief, les zones de terrain, l'hydrologie détaillée, les ressources, les objets, les positions de départ, la balance et les validations.

Le projet repose sur une règle importante : les **positions de départ des joueurs sont placées très tôt** dans le pipeline. Le reste de la génération doit ensuite s'adapter à ces zones réservées afin de réduire les positions invalides et de permettre un meilleur équilibrage des ressources.

Les aperçus visuels sont toujours des rendus déterministes issus des vraies données de carte ; aucune image de carte fictive n'est utilisée.

## Aperçus de l’application

### Génération et Viewer

![Génération Legacy 768×768 et vue Départs dans le Viewer](docs/screenshots/v1_8_generation_viewer.png)

*Carte réellement générée, projection parallélogramme et zones de départ des quatre joueurs.*

### Statistiques

![Carte thermique et rapport Statistiques d’une carte générée](docs/screenshots/v1_8_statistics.png)

*Rapport détaillé : terrains, ressources, hydrologie, relief, départs et inventaires d’IDs.*

### Graphiques

![Vue Ressources et graphique du stock minier](docs/screenshots/v1_8_charts.png)

*Vue Ressources associée au graphique sémantique du stock minier, dont la part recouverte par la neige.*

### Génération par lot

![Génération par lot de quatre cartes avec miniatures et états de cache](docs/screenshots/v1_8_batch.png)

*Quatre tâches séquentielles avec miniatures réelles ; la barre bleue montre une réutilisation volontaire du cache pour une configuration identique.*

## État actuel — v2.0 DEV_2 / reconstruction native Legacy

La génération `v2.0 DEV_1` a été validée puis publiée sur GitHub. DEV_2 repart
sur une base propre : l'ancien générateur Legacy procédural, ses profils,
helpers et bibliothèques dérivées sont retirés, ainsi que l'ancien chemin
Legacy v1.5 qui ne produisait pas une génération exploitable. Le mode Legacy
reste réservé dans l'interface et l'API, mais sa génération est explicitement
désactivée pendant la reconstruction native.

Le seul moteur génératif conservé est le chemin **Upgraded** de compatibilité,
calibré sur Continental 768×768. Ses règles, son profil, ses validations et
ses références restent séparés et protégés. L'archétype Continental continue à
définir la macro-forme ; le futur générateur Legacy définira ensuite ses
propres couches de relief, terrains, hydrologie, ressources, objets, départs
et validations à partir de l'audit natif.

La comparaison des minerais a été faite avant la suppression : l'ancien
générateur avait un mix global proche des SAV natifs, mais des composants et
des tailles de gisements nettement trop fragmentés. Ces quotas et heuristiques
ne sont donc pas conservés comme règles. Le détail reproductible est dans
`references/SETTLERS3_LEGACY_MINERAL_COMPARISON_DEV2.md`.

Le chantier DEV_2 est maintenant la reconstruction du noyau Legacy natif,
puis de l'archétype Continental v1. Les audits de l'algorithme de génération
restent la source de vérité ; aucun résultat provisoire ne doit être présenté
comme une implémentation exacte avant validation sur les cartes du jeu.

La GUI et l'outillage validés restent disponibles : import EDM / MAP / SAV en
lecture, export EDM/MAP 768 avec scaffold, vues d'analyse et d'inspection,
statistiques, graphiques, historique, comparaison A/B, génération par lot,
thèmes et langues FR/EN/DE/ES. Les aperçus restent des rendus déterministes de
données réelles ou de sorties identifiées du moteur conservé.

### Qualité des traductions

Les interfaces **française et anglaise** sont les versions linguistiques de référence, relues et considérées comme correctes. Les traductions **allemande et espagnole** ont été produites automatiquement puis seulement partiellement revues ; elles peuvent donc contenir des formulations imparfaites ou un vocabulaire à affiner. Cette règle s’appliquera également aux futures langues tant qu’une relecture humaine compétente ne les aura pas validées. Les corrections proposées par des locuteurs sont les bienvenues.

Les coordonnées de départ sont lues dans le bloc joueur du SAV. L'ancienne
forme canonique de 145 régions et 3 500 cellules est conservée uniquement comme
trace d'analyse historique ; elle ne sert jamais à remplir un masque. La vue
Masque initial affiche exclusivement les coordonnées directes du byte 8 d'un
SAV immédiat reconnu, tandis que Territoires affiche les claims runtime
réellement lus dans le SAV.

> Le writer SAV n'est toujours pas implémenté : un SAV importé peut être lu et copié inchangé, jamais réinventé. Les exports EDM/MAP restent dépendants d’un scaffold de la taille concernée ; la génération active conservée est calibrée sur Upgraded 768×768.

La **v1.7 STABLE** clôt le socle Statistiques / Graphiques. La **v1.8** a construit la passe Workflow / accessibilité / production. La **v1.9** consolide maintenant l’architecture interne avant de terminer par l’archéologie/data mapping. Le retour profond au générateur reste prévu pour la v1.10.

## Modes de génération

### Legacy

Mode réservé à la fidélité au générateur original de Settlers III et au corpus natif analysé. Il sert de cible du reverse-engineering, mais sa génération est désactivée pendant la reconstruction DEV_2.

### Upgraded

Preset amélioré du projet. Il intègre les règles validées au fil des tests et du long-play : starts précoces, hydrologie corrigée, poissons et minerais rééquilibrés, SmallTree84, Building Stones avec footprint, décorations contrôlées, règles de transitions et validators spécifiques.

La matrice détaillée est disponible dans `references/SETTLERS3_UPGRADED_RULE_MATRIX_v1.md`.

### Custom

Mode futur permettant d'exposer les paramètres de génération à l'utilisateur. Il
reste réservé pour l'instant : son premier objectif sera un laboratoire de
réglage séparé, avec presets exportables, génération par lot et garde-fous
critiques conservés. La liste complète des paramètres sera définie avant son
implémentation afin de ne pas mélanger ses essais avec le preset Upgraded.

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

Limite connue avant cette refonte : les seeds actuelles ne produisent que trois morphologies de base, ensuite présentées avec des rotations et parfois un miroir. L’audit seed/RNG et la diversification objective sont planifiés pour la v1.10.

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

- `AGENTS.md` — consignes courtes auto-découvertes pour reprendre le travail ;
- `SETTLERS3_PREGEN_READ_FIRST.md` — point d'entrée obligatoire avant toute modification/génération ;
- `SETTLERS3_MAPGEN_REFERENCE_v15_LONGPLAY_RULES.md` — règles canoniques ;
- `SETTLERS3_UPGRADED_RULE_MATRIX_v1.md` — correspondance règles Upgraded / implémentation / validators ;
- `SETTLERS3_EDM_MAP_FORMAT_REFERENCE_v3.md` — format EDM/MAP ;
- `SETTLERS3_SAV_FORMAT_REFERENCE_v1.md` — lecture SAV ;
- `docs/ARCHITECTURE.md` — couches runtime, flux de données, invariants et zones protégées ;
- `docs/DEBUGGING.md` — diagnostic reproductible, commandes de validation et informations à conserver ;
- `docs/GITHUB_PUBLICATION.md` — métadonnées proposées et checklist de publication, sans modifier les réglages du dépôt ;
- `TODO_MAPGEN.md` — feuille de route courante.

## Versioning

L'historique Git rétroactif est conservé depuis la v1.0 avec des tags de version. Les nouvelles releases doivent mettre à jour le code, le changelog, les tests et la documentation avant création du tag.

## Récupérer la dernière release STABLE

Sous Windows, `update_latest_release.bat` interroge uniquement la dernière GitHub Release publiée et télécharge son archive officielle dans `updates/`. Il ne suit ni `main`, ni les builds DEV/RC et n'écrase jamais l'installation courante.
