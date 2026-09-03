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

![Génération Legacy 768×768 et marqueurs de départ dans le Viewer](docs/screenshots/v1_8_generation_viewer.png)

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

## État actuel — v2.0 DEV_5 / finitions Upgraded

La génération `v2.0 DEV_1` a été validée puis publiée sur GitHub. `DEV_2` a été
le checkpoint validé du reset natif, et `DEV_3` est maintenant le checkpoint
validé et publié : l'ancien générateur Legacy
procédural et ses bibliothèques dérivées ont été retirés, puis remplacés par
un portage natif v1. Le moteur Upgraded est maintenant reconstruit dans une
copie indépendante de ce pipeline. DEV_4 ajoute la liaison temporaire
Graphiques → Vue, sans liaison dans A/B, corrige le dialogue d’export hors 768,
déverrouille les trois miroirs aussi en Upgraded et rend ce mode disponible sur
toutes les tailles natives du contrat ; 768
conserve les quotas calibrés et les autres tailles utilisent des quotas
proportionnels pour rester générables. Aucune taille du contrat n’est bloquée
par un statut « non testé » : les avertissements restent informatifs. Le
réglage **Marqueurs de départ** propose désormais Petits, Normaux et
Grands, en plus de Masqués, dans toutes les vues, Batch et Historique ; une
option indépendante permet aussi d’afficher les cercles de départ partout.
DEV_5 ajoute le contenu Upgraded autour des départs : objets statiques calqués
sur Legacy, mini-forêts, bonus arbres/pierres et mini-marais, tout en
conservant les récifs spécifiques Upgraded.

Le moteur **Legacy** implémente Continental v1 avec le relief, les terrains,
l'hydrologie, les objets, les ressources, les départs et les métadonnées de
partie observés dans S3.EXE. Le moteur **Upgraded** possède sa propre copie du
pipeline, calibrée sur Continental 768×768 mais générable sur toutes les tailles
du contrat. Il ajoute uniquement ses différences
explicites : minerais v7, poissons, arbres/décorations et pierres de
construction, sans boue. L'archétype Continental fournit le contexte macro-géographique ;
il ne sculpte pas une seconde forme par-dessus le noyau natif.
**DEV_5** conserve le pont provisoire de positionnement des starts,
mais rétablit les bonus arbres, pierres et mini-marais autour de ces
coordonnées. Les prochaines étapes prévues sont Dev 6 générateur Custom, Dev 7
archétype Custom et Dev 8 premiers modificateurs.

La comparaison des minerais a été faite avant la suppression : l'ancien
générateur avait un mix global proche des SAV natifs, mais des composants et
des tailles de gisements nettement trop fragmentés. Ces quotas et heuristiques
ne sont donc pas conservés comme règles. Le détail reproductible est dans
`references/SETTLERS3_LEGACY_MINERAL_COMPARISON_DEV2.md`.

Le portage natif de référence est présent dans DEV_2 pour les tailles `256, 320, 384, 448,
512, 576, 640, 704, 768, 832, 896, 960 et 1024`. Les modes miroir proposent
`Axe long`, `Axe court` ou `Les deux`. Les tailles sous 384 et au-dessus de 768
restent exportables et signalées dans le feedback lorsqu'elles sortent du
cadre de jeu habituel. Les audits de l'algorithme restent la source de vérité ;
une validation dans l'éditeur/jeu reste nécessaire pour les exportations
étendues.

DEV_3 poursuit cette base avec la forme validée des blobs miniers compensée pour
la projection parallélogramme, le nom court validé du terrain `34` (**Patch
d’herbe rocheuse**) et son affichage distinct dans la carte et les graphiques.

La GUI et l'outillage validés restent disponibles : import EDM / MAP / SAV en
lecture, export EDM/MAP de toutes les tailles natives via scaffold de test,
vues d'analyse et d'inspection,
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

> Le writer SAV n'est toujours pas implémenté : un SAV importé peut être lu et copié inchangé, jamais réinventé. Les exports EDM/MAP utilisent pour l'instant le scaffold 768 comme enveloppe de test, y compris pour les tailles étendues ; leur compatibilité avec l'éditeur/jeu doit encore être vérifiée. Le chemin Upgraded reste calibré sur 768×768, mais ses autres tailles sont désormais générables pour test. Limite connue : certains SAV peuvent afficher des récifs sur terre à cause d'un décodage d'ID probablement incorrect ; correction reportée.

La **v1.7 STABLE** clôt le socle Statistiques / Graphiques. La **v1.8** a construit la passe Workflow / accessibilité / production. La **v1.9** consolide maintenant l’architecture interne avant de terminer par l’archéologie/data mapping. Le retour profond au générateur reste prévu pour la v1.10.

## Modes de génération

### Legacy

Moteur natif v1 pour l'archétype Continental, disponible sur les tailles du
contrat natif et avec les quatre combinaisons de miroir. Il suit l'ordre
relief/terrain, objets et ressources globales, re-seed, puis préparation des
départs ; les objets/ressources propres aux joueurs, les colons et l'écriture
SAV restent reportés à la future gestion des `.sav`. Les données runtime type 9
qui ne tiennent pas dans l'Area sont reportées explicitement dans le rapport.

### Upgraded

Preset amélioré du projet, disponible sur les tailles natives du contrat. Il intègre les règles validées au fil des tests et du long-play : hydrologie corrigée, poissons et minerais rééquilibrés, SmallTree84, Building Stones avec footprint, décorations contrôlées, règles de transitions et validators spécifiques. Le placement des joueurs est actuellement un pont provisoire ; son comportement natif sera traité dans une passe dédiée.

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

Les deux modes n'ont pas le même ordre. Le Legacy natif porte d'abord le
terrain et le contenu global ; l'Upgraded utilise pour l'instant un pont de
positionnement isolé, qui sera recalibré séparément :

```text
Legacy : MapConfig
  ↓
Continental : contexte macro
  ↓
Relief / terrain / hydrologie native
  ↓
Objets et ressources globales
  ↓
Re-seed puis starts de transition MAP/EDM
  ↓
Finalisation / validators
```

```text
Upgraded : MapConfig
  ↓
Continental : macro-layout
  ↓
Copie indépendante du relief / biomes / hydrologie
  ↓
Pont de positionnement provisoire des starts
  ↓
Ressources / objets globaux / validators
  ↓
Export
```

Une passe tardive ne doit pas invalider un start réservé. Elle doit contourner la zone ou faire échouer explicitement la génération.

## Morphologie Upgraded

La première implémentation exécutable d'Upgraded 768 utilise une copie
indépendante de la séquence terrain native validée, puis applique ses passes de
contenu spécifiques. Le prochain chantier est la parité terrain mesurée et la
recalibration séparée du positionnement des joueurs.

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
