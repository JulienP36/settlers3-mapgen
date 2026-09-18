# Settlers III MapGen

**Français** · [English](README_EN.md)

> Générateur procédural expérimental pour **The Settlers III**, construit à partir de reverse-engineering des formats `.EDM`, `.MAP` et `.SAV`, d'analyses du générateur natif et de nombreuses validations dans l'éditeur et en jeu.

> **Note de développement / transparence :** ce projet est conçu, dirigé, testé et validé humainement, avec un usage important de **ChatGPT / OpenAI comme assistance d’implémentation**, notamment pour le backend, l’analyse technique et les outils de reverse-engineering. Cette assistance fait partie explicitement du processus de développement du projet.

## Présentation du projet

**Settlers III MapGen** a pour objectif de créer, analyser et à terme éditer des cartes Settlers III avec une génération procédurale reproductible et contrôlable.

Le projet poursuit trois objectifs complémentaires :

- **préserver le comportement historique du jeu** grâce au mode **Legacy**, qui sert de référence native et de base de reverse-engineering ;
- **proposer une génération améliorée** grâce au mode **Upgraded**, qui applique les règles de gameplay, de morphologie, de ressources et de sécurité affinées au cours du projet ;
- **ouvrir progressivement la génération à l'utilisateur** avec le mode **Custom**, où les paramètres pourront être ajustés manuellement tout en conservant les garde-fous critiques.

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

## État actuel — v2.0 DEV_7 / finition du Générateur Custom

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
conservant les récifs spécifiques Upgraded. Le socle applicatif DEV_6_R61
reprend R57, conserve les formes et la profondeur des lacs, renforce la rive
à deux anneaux et reconstruit les rivières bonus avec le système natif local
(filtre 9×9, relief, éventail HEX6, marqueurs et retour arrière), sans
rechercher une destination vers l’eau existante. Une jonction accidentelle
reste possible si la géométrie la provoque, mais aucun trajet lac→mer n’est
recherché ; les rivières normales bonus utilisent River96 sans alternance des
quatre IDs. R58 borne le rayon maximal à `16 HEX6` et la cible maximale à `6`
rivières par lac, sans modifier le traceur validé. À `0`, le seuil d’eau native
depuis la bordure désactive le filtre ; les valeurs positives conservent ce
rayon d’exclusion. Les métadonnées enregistrent les tentatives, acceptations et
causes de refus par joueur et au total. La protection eau de la tour reste à 20 HEX sur toute l’emprise,
même hors forçage. Elle place
« Répartition » entre « Forme » et « Rayon commun » et conserve les valeurs
dérivées lors d’un changement de répartition ; R60 compacte maintenant le
panneau lac/rivière sur quatre colonnes, raccourcit le libellé de l’évitement
d’eau native et rapproche explicitement les listes de formes de leur libellé.
R61 remplace ce libellé par « Rayon de contrôle eau native », puis aligne tous
les contrôles du panneau lac/rivière sur une seule colonne verticale. La logique
de génération reste celle de R59 ;
elle conserve. La finition ergonomique de l’onglet Générateur est publiée dans
DEV_7 ; la prochaine tranche porte sur les archétypes Custom. Les sections
sémantiques utilisables du générateur restent : Minerais, Poissons,
Arbres, Pierres de construction, Décorations et réglages détaillés des bonus de départ,
traductions dynamiques, profils dérivés des presets,
empreinte de configuration intégrée au cache, onglets Générateur/Archétype et
registre extensible des bonus de départ. Les minerais proposent les trois
algorithmes Legacy/Upgraded/Pixels aléatoires, avec occupation, répartition, tailles et ressource
moyenne ; les poissons proposent remplissage global ou dans une bande côtière
d'épaisseur réglable, avec repli global si cette bande dépasse les côtes. Les
détails techniques des profils ne sont pas exposés dans l'interface. Les réglages sélectionnés
sont appliqués au contenu Upgraded et au contenu ressources du pont Legacy,
sans modifier un profil via l’édition Custom. Le profil Upgraded de base porte
désormais la répartition 52,5 / 22,5 / 15 / 5 / 5 demandée ; son équivalent
Custom la reprend automatiquement. La méthode **Pixels aléatoires** pose
uniformément les cases compatibles sans former de gisements, y compris dans la
vue de ressources entrelacée réellement exportée. Le chemin
Upgraded et son Custom équivalent partagent désormais exactement les routines
de minerais et de poissons lorsque les paramètres sont identiques. Les éditions
Custom successives conservent les contrôles et leur focus, et la liaison
Graphiques → Vue est active par défaut.

La section Décorations expose un taux d’apparition indépendant de `0–500 %`
pour chaque famille statique déjà reconnue par le générateur ; `100 %` reprend
le comportement du profil sélectionné, sans exposer les identifiants ni les
règles de terrain et de collision. Le moteur **Legacy** implémente Continental v1 avec le relief, les terrains,
l'hydrologie, les objets, les ressources, les départs et les métadonnées de
partie observés dans S3.EXE. Le moteur **Upgraded** possède sa propre copie du
pipeline, calibrée sur Continental 768×768 mais générable sur toutes les tailles
du contrat. Il ajoute uniquement ses différences
explicites : minerais v7, poissons, arbres/décorations et pierres de
construction, sans boue. L'archétype Continental fournit le contexte macro-géographique ;
il ne sculpte pas une seconde forme par-dessus le noyau natif.
**DEV_5** conserve le pont provisoire de positionnement des starts. **R36**
corrige le bonus forêt dans les deux variantes Custom, **R37** consolide les
forêts et les pierres de départ, et **R40** supprime les réservations de cases vides
et unifie la route Custom : Legacy et Upgraded sont des presets spécifiques de
cette route et commencent avec les bonus désactivés, chaque panneau possède son
interrupteur, et la forêt demande par défaut `30` adultes et `20` pousses par
joueur. Les adultes sont posés avant les pousses, tous avec au moins `3 HEX6`
entre eux ; le rayon minimal est dérivé de ces quantités et peut s’étendre
automatiquement si le terrain l’exige. Les anciens champs de rayon de forêt ne
sont plus pris en compte. R37 plafonne les adultes et pousses à `100`, ainsi
que les forêts globales à `100` arbres, et affiche les pousses avec la même
couleur sur la carte et les graphiques. Les pierres demandent par défaut `15`
ancres par joueur, maximum `50`, avec une moyenne de `10` unités ; leur rayon
est dérivé automatiquement. R46 conserve le mini-marais de R42, génère une
forme `Native` indépendante pour chaque start avec le même plan
brosse/extension/érosion que les marais globaux, et ajoute un découpage strict
uniquement lorsque des bonus sont actifs : le chemin sans bonus
reste byte-identique à R42. Les bonus de terrain sont placés après les terrains
liés à l’archétype et avant les familles globales, puis les objets bonus sont
écrits avant tous les objets globaux ; aucune écriture bonus n’est supprimée
ensuite. R46 conserve le halo des écritures réelles de R45 pour toutes les familles
d’objets actives, y compris la passe native globale Legacy ; l’empreinte complète
des rochers reste protégée. Les adultes des forêts sont posés avant les pousses.
R54 conserve le mini-marais R42 avec une borne de rayon `1–16` ; R42 avait
remplacé les cases libres du bonus mini-marais par une liste de formes
extensible (`Native`, `Hexagone`) ; l’hexagone scale réellement avec le rayon et `Native`
réutilise le plan natif global des marais. Le nombre de cases est dérivé. Le switch d’objets compatibles avec l’herbe
autorise les terrains `18`, `19` et `24`, mais pas le terrain rocheux `34`, sans
effacer des objets déjà posés ; les bonus peuvent donc aussi utiliser ces
cases lorsqu’elles sont compatibles. Les sélections publiques Legacy et
Upgraded sont des presets de la même route Custom, avec les bonus désactivés
par défaut. R39 supprime aussi les pierres natives résiduelles lorsque le
taux global est à `0 %` et que le bonus local est désactivé ; le stock des
rochers bonus suit la même loi que le stock global. Les cinq bonus restent
hors quotas globaux, et le forçage à
distance élargie est maintenant disponible pour tous via une case commune,
désactivée par défaut, avec repli local lorsque la case est décochée. R13
raccorde la section Arbres aux deux moteurs Custom : quota de
base relatif, pousses (quota global ou quota séparé et placement), forêts (part,
moyenne et variation) et quota maximal relatif des palmiers. Le défaut Upgraded
est celui du profil actif, notamment `30 %` du quota adulte en forêts ; le défaut
Legacy n’active ni forêts ni pousses. Le socle DEV6 attend encore la validation
utilisateur, avant Dev 7 (archétypes Custom) et Dev 8 (premiers modificateurs).

La comparaison des minerais a été faite avant la suppression : l'ancien
générateur avait un mix global proche des SAV natifs, mais des composants et
des tailles de gisements nettement trop fragmentés. Ces quotas et heuristiques
ne sont donc pas conservés comme règles. Le détail reproductible est dans
`references/history/minerals/SETTLERS3_LEGACY_MINERAL_COMPARISON_DEV2.md`.

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

> Le writer SAV n'est toujours pas implémenté : un SAV importé peut être lu et copié inchangé, jamais réinventé. Les exports EDM/MAP utilisent pour l'instant le scaffold 768 comme enveloppe de test, y compris pour les tailles étendues ; leur compatibilité avec l'éditeur/jeu doit encore être vérifiée. Le moteur Upgraded actif est indépendant ; 768 reste une référence de calibration, pas une version ou un profil séparé, et toutes les tailles du contrat restent générables pour test. Il n'existe plus de moteur Upgraded v1.5 actif. Limite connue : certains SAV peuvent afficher des récifs sur terre à cause d'un décodage d'ID probablement incorrect ; correction reportée.

Les étapes v1.x sont historiques et leurs documents sont archivés. La ligne
active est désormais la v2.0 : finir le socle Custom, puis implémenter les
archétypes Custom et les modificateurs selon le TODO courant.

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

La matrice détaillée est disponible dans
`references/SETTLERS3_UPGRADED_RULE_MATRIX_CURRENT.md`. L'index
`references/REFERENCE_INDEX.md` indique les documents actifs et les archives.

### Custom

Mode laboratoire permettant d'exposer les paramètres de génération à
l'utilisateur. Une modification d'un preset crée une configuration Custom
séparée, identifiée par une empreinte et réutilisable dans le cache et Batch.
Les presets intégrés restent immuables. Les cinq bonus de départ actifs (forêt,
pierres, mini-marais, zone rocheuse minérale et mini-lac avec poissons/rivière)
sont décrits dans un registre extensible et restent hors quotas globaux.

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

L'implémentation actuelle d'Upgraded possède une copie indépendante de la
séquence terrain native validée, puis applique ses passes de contenu
spécifiques. Le 768×768 est une calibration protégée, pas une version séparée
du moteur ; le positionnement exact des joueurs reste une passe future.

La diversification des seeds et l'extension aux autres archétypes restent des
sujets futurs de la roadmap v2.0.

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
- `REFERENCE_INDEX.md` — routage des références actives, historiques et de reprise ;
- `SETTLERS3_MAPGEN_REFERENCE_v15_LONGPLAY_RULES.md` — mesures long-play historiques, avec surcharge v2.0 ;
- `SETTLERS3_UPGRADED_RULE_MATRIX_CURRENT.md` — correspondance courante des règles Upgraded / Custom / validators ;
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

R58 reprend le moteur R48 et le forçage R47 (recherche par couronnes successives jusqu’à D+34)
et ajoute aux zones minérales charbon/fer/or une forme organique arrondie de
type gisement Upgraded,
des surfaces égales, au prorata des parts de gisements ou personnalisées par
minerai, ainsi qu’une moyenne de quantité globale ou dédiée. Le cœur reste
toujours entièrement minéralisé et une zone impossible est omise avec un
shortfall explicite. Le mode Hexagone et les rayons historiques restent
compatibles. Le panneau regroupe les familles dans une grille
`Minerai / Cœur / Moyenne` et désactive les rayons, la surface totale ou les
surfaces par minerai selon le mode sélectionné ; le prorata rappelle ses parts
globales. R50 ajoute les sprites 16×16 des trois familles et un seul rayon
commun en mode égal (`1–16 HEX6`). R54 reprend les finitions R51 : listes verrouillées, unités rapprochées,
unités `HEX6`/`cases`, grise les sprites quand leur famille est inactive, porte
le rayon maximal des marais à `16 HEX6`, borne chaque cœur à `1–820` cases et
adapte le total prorata à `820/1 640/2 460` selon les minerais actifs. Les plans objets sont
préparés avant écriture et les abords des tours restent protégés. Le mode OFF
conserve R46 pour les bonus existants. Forêts, pierres et marais validés ;
zones minérales et lac/rivière restent à valider séparément. DEV6 reste une
candidate locale.
R57 conserve les formes et profondeurs de R55, renforce les lacs à deux
anneaux de rive et construit chaque rivière bonus par un système natif local,
sans cible globale ni pont lac→mer recherché. Les jonctions accidentelles
restent possibles comme dans Legacy ; les systèmes normaux utilisent River96
sur toute leur longueur. R58 borne le rayon maximal à `16 HEX6` et la cible
maximale à `6` rivières par lac, sans modifier le traceur validé.
