# Settlers III MapGen — CURRENT SNAPSHOT

> **LIVING RECOVERY SNAPSHOT — v1.8 development.**
>
> Last refreshed: **2026-08-23 — v1.8 DEV_5_R3 validée sous Windows**

## État release / Git

- Repository : `JulienP36/settlers3-mapgen`.
- `main` = STABLE uniquement ; `dev` = développement ; `rc` reste en place pour le moment mais son utilité sera réévaluée si les futures RC restent courtes.
- v1.7 STABLE publiée sur GitHub, tag `v1.7`.
- Commit `main` de promotion v1.7 STABLE : `780bc5e` — `release: Settlers3 MapGen v1.7 STABLE`.
- ZIP final GitHub Release généré directement depuis le tag `v1.7` : `SETTLERS3_MAPGEN_V1_7_STABLE_20260821.zip`.
- SHA-256 ZIP final : `593A86CEE2926344D1C2675C23D5F99E2A5058C0DCC50A1A4A4D9EA077DC94E5`.
- Updater actuel détecte correctement v1.7 comme dernière STABLE.
- v1.7 = socle Stats/Graphs ; moteur de génération v1.5 validé/protégé inchangé.
- v1.8 DEV_2_R7 validée sous Windows et synchronisée sur `dev` au commit `85e7bfb`.
- Autorisation permanente du propriétaire : commits et pushs non destructifs autorisés sur `dev` sans confirmation ponctuelle, dans le périmètre et avec les exclusions définis par `PROJECT_WORKFLOW.md`.
- DEV_4_R4 validée et publiée sur `dev` au commit `e036582`.
- DEV_4_R5 validée et publiée sur `dev` au commit `7585042` : réglage persistant `Masqués / Petits / Normaux`, base raster sans marqueurs réutilisée et tooltip actualisé sans destruction.
- DEV_4_R6 validée et publiée sur `dev` au commit `0f3e5f6` : déplacement de l'aperçu Batch épinglé, remplacement à position constante et double tampon lors des changements de projection/miniature.
- DEV_4 PERF+ R1 validée sous Windows et intégrée à `dev` : cache raster en calques, invalidations ciblées et écritures de sliders différées. Aucune régression ni baisse de performances observable ; R6 reste le checkpoint historique de repli.
- DEV_5_R3 est validée sous Windows : centres d’export cartes et Graphiques multi-format, option Vue actuelle non redondante, bas de fenêtres et survols corrigés, modalité Windows stricte et formats indisponibles grisés/barrés. La hauteur initiale est calculée depuis le contenu ; toute extension future devra ajouter une contrainte écran et un scroll de secours si nécessaire.


## v1.8 DEV_2 — Responsive UI v1 + Status/Feedback v1

- DEV_1 validée et synchronisée exactement vers `dev` au commit `57d9569`.
- Responsive UI v1 : taille initiale adaptée à l’écran ; cible principale 1920×1080, reflow compact sous ~1500 px de largeur, minimum 900×650. Les groupes de contrôles supérieurs passent sur plusieurs lignes plutôt que de devenir minuscules ou hors écran. Les proportions carte/panneaux restent inchangées.
- La zone historique `status` reçoit enfin une mission formelle : communication courte, lisible et semi-persistante entre le programme et l’utilisateur.
- Les détails rapides du pipeline restent dans la barre/overlay de progression ; ils ne remplacent plus en rafale le message humain de statut.
- Pendant génération : le statut décrit map/mode/archétype/taille/joueurs/seed ; la progression affiche les étapes techniques ; fin de génération = confirmation lisible.
- Feedback branché notamment sur sélection/réservations, génération/cache, seed copié, historique, A/B, raccourcis, export et filtre Heatmap verrouillé.
- Feedback FR/EN et retraduisible lors du changement de langue.
- Status/Feedback v2 est explicitement futur : davantage de contexte, messages/temporisation/priorités raffinés, couleurs et jolies icônes ; ne pas transformer cette zone en log complet.

## v1.7 — état final fonctionnel

- Statistiques structurées orientées utilisateur + debug.
- Inventaires complets des Terrain IDs / Object IDs présents.
- Graphiques FR/EN, clair/sombre, A/B, tooltips interactifs persistants et segmentés.
- Tooltips contextuels avec IDs lorsqu'ils sont utiles.
- Densités normalisées `/1000` avec dénominateur pertinent.
- Herbe = Herbe verte ID16 + Herbe sèche ID24 ; Montagne = roche + neige ; Eau = mer + lacs.
- Boutons A/B avec LED verte et identification courte de la map.
- Export CSV/JSON/PNG opérationnel.
- RC_1 validée Windows ; export EDM, rechargement et View Map in-game validés sans régression.
- 70 tests PASS à la promotion STABLE ; hashes protégés inchangés.

## Registres d'archéologie IDs

Deux listes de travail ont été créées : Terrain IDs et Object IDs, actuellement présentées sur la plage technique 0–255.

IMPORTANT : `255` n'est PAS considéré comme la borne réelle des catégories. La plage 0–255 sert seulement de grille 8-bit pratique. Une future passe doit déterminer empiriquement :
- ID terrain maximum réellement utilisé/valide ;
- ID objet maximum réellement utilisé/valide ;
- trous/réservés ;
- différence entre plage théorique du champ et plage réellement exploitée.

Les IDs inconnus doivent rester explicitement inconnus ; ne jamais inventer leur sémantique.

## Roadmap versions désormais retenue

- **v1.8** : Workflow, accessibilité & production.
- **v1.9** : version de transition Archéologie / Data Mapping, avant modifications profondes du générateur.
- **v1.10** : retour au générateur, notamment Continental multi-tailles et éventuellement début d'autres archétypes.
- Ne pas figer les versions après v1.10 : décider selon l'évolution réelle du projet.
- Ne pas consommer `v2.0` pour le simple multi-size ou le début des archétypes. Réserver le saut 2.0 à une évolution structurelle réelle du programme/workbench.

## v1.8 — 13 axes validés

### 1. Batch Generation / Génération par lot

Feature principale envisagée pour v1.8.
- Fenêtre dédiée.
- 1 à 4 maps au départ ; architecture extensible éventuellement à 8 après mesures RAM/temps/cache.
- Paramètres indépendants par map : mode, archétype, taille, joueurs, seed et paramètres ordinaires de génération.
- États/pastilles : attente, génération, terminée, erreur.
- Réutiliser le pipeline de génération existant ; ne pas créer un second moteur batch parallèle.
- Résultats intégrés à l'historique.
- Affectation directe d'une map terminée en A ou B.

### 2. Export maps multi-format

Popup `Exporter…` avec :
- un seul nom de base partagé ;
- cases `.edm`, `.map`, copie `.sav` inchangée, PNG Global et PNG Vue actuelle ;
- disponibilité dépendant uniquement des capacités réellement validées ;
- noms exacts affichés avant export et écrasements confirmés en une fois.

Implémenté dans DEV_5_R1, validation Windows en attente.

### 3. Export Graphiques unifié

Les multiples boutons sont remplacés dans DEV_5_R1 par un bouton `Exporter…` ouvrant une popup JSON/CSV/PNG avec dossier, nom partagé, aperçu des sorties et confirmation groupée. Validation Windows en attente.

### 4. A/B — polish léger

- Reset A.
- Reset B.
- Reset A+B.
- À terme supprimer le texte redondant sous l'historique, les boutons LED A/B étant devenus la source visuelle principale.
- Bonne intégration avec Batch.
- Pas de refonte complète A/B dans ce bloc.

### 5. Titre de fenêtre entièrement i18n

Le titre complet doit passer par le système de traduction, pas seulement le mot `moteur`.

### 6. Nouvelles langues du programme

- Ajouter allemand (DE) et espagnol (ES) dans le programme.
- L'utilisateur peut relire partiellement l'espagnol ; allemand à soigner particulièrement vu la communauté Settlers III germanophone.
- Hors programme : communication GitHub surtout EN + FR ; allemand éventuellement ponctuel pour la visibilité communautaire ; espagnol externe non prioritaire.

### 7. Raccourcis clavier v2

- Sélecteur de combinaison plutôt que saisie libre si possible.
- Plus d'actions configurables.
- Gestion robuste AZERTY/QWERTY.
- Détection conflits, reset.
- Faire évoluer le JSON existant `%APPDATA%/Settlers3MapGen/settings.json`; ne pas créer un second système YAML/config parallèle.

### 8. Historique de session amélioré

- Imports EDM/MAP/SAV ajoutés à l'historique.
- Résultats Batch ajoutés.
- Taille de l'historique configurable.
- A/B assignables facilement depuis l'historique.

### 9. Premier vrai `.exe`

Remonter fortement la priorité du packaging `.exe` pour permettre à un utilisateur extérieur de lancer MapGen sans installer Python/pip/dépendances.
- Tester chemins, données embarquées, settings, dossiers utilisateur.
- L'exécutable doit devenir un élément important de la découvrabilité/accessibilité.

### 10. Icône application / exe

- Prévoir techniquement une icône/placeholder simple.
- L'icône finale sera dessinée manuellement par l'utilisateur en pixel art.
- Potentiellement réutilisée pour `.exe`, barre de fenêtre, barre des tâches, GitHub.
- RÈGLE PROJET : aucune génération d'image IA pour les visuels/assets du projet. Les rendus déterministes de maps issus des vraies données EDM/MAP/SAV restent autorisés ; la génération procédurale de terrain n'est évidemment pas concernée.

### 11. Updater v2 compatible exécutable

Faire évoluer l'updater GitHub Releases pour une application packagée :
- détecter version installée / dernière STABLE ;
- téléchargement/mise à jour ;
- préservation settings ;
- gestion du remplacement d'un exe lancé ;
- vérification SHA ;
- comportement propre en cas d'échec/rollback à étudier.

### 12. README — transparence sur l'assistance IA

Ajouter assez tôt dans le README une mention claire indiquant que le projet est conçu/dirigé par l'utilisateur mais construit avec un usage important de ChatGPT/OpenAI, particulièrement pour l'implémentation backend, l'analyse et les outils de reverse engineering. Le but est la transparence, pas de minimiser le travail humain ni de laisser croire que tout a été codé manuellement.

### 13. Découvrabilité GitHub

Petite passe post-v1.7 / v1.8 :
- About/description explicite ;
- Topics pertinents : `settlers3`, `settlers-iii`, `map-generator`, `procedural-generation`, `reverse-engineering`, etc. ;
- entrée anglaise claire du README tout en conservant le français ;
- termes naturels Settlers III / Settlers 3 / Siedler III / EDM / MAP / SAV ;
- vraies GitHub Releases pour STABLE ;
- pas de spam SEO ni de campagne marketing forcée.

## v1.9 — archéologie / data mapping

Version de transition fortement envisagée avant le retour profond au générateur :
- déterminer bornes réelles Terrain/Object IDs ;
- compléter nomenclature connue/inconnue ;
- clarifier familles/transitions ;
- commencer settlers/colons, marchandises, outils, ressources transformées (pierres taillées, planches, rondins, etc.) et autres catégories SAV si identifiables ;
- consolider les références utilisées par Stats/Tooltips ;
- tests contrôlés d'identification si nécessaire.

Ne pas lancer cette passe complète immédiatement pendant v1.8.

## v1.10 — retour générateur

Objectif général : revenir au cœur du programme après v1.8 + v1.9.
- Continental multi-tailles : 384 → 448 → 512 → 576 → 640 → 704 → 768.
- Utiliser Stats/Graphs comme outils de calibration/debug.
- Potentiellement commencer les autres archétypes selon l'état obtenu.
- Ne pas figer davantage la roadmap post-v1.10 pour le moment.

## Fonctionnalités futures importantes déjà retenues

- Comparaison multi-maps **3+** : fonctionnalité planifiée à très forte probabilité, pas simple idée. À faire plus tard comme vue d'analyse dédiée, plutôt que surcharger A/B.
- Modifiers / Modificateurs : feature volontairement fun mais sérieuse permettant des variations contrôlées et parfois drastiques du générateur. Toujours prévue.
- Synergie future importante : même seed + différents modifiers → génération batch → Stats → comparaison multi-map.
- ENDGAME non versionné : lorsque le générateur/workbench sera pratiquement finalisé, envisager un éditeur de cartes avancé intégré capable de générer, importer, inspecter, modifier, valider et exporter. Architecture UI à décider seulement alors : fenêtre dédiée ou espace/mode Édition complet. Ne pas anticiper ce chantier dans la roadmap proche ou moyenne.
- Rayons de ressources proches configurables : exactement 2 rayons, pas 3.
- Graphiques futurs possibles : histogrammes de tailles de composants, profil radial des ressources, variantes de type donut ; radar = idée incertaine ; boxplots surtout pour futures comparaisons au corpus natif.
- Massifs/Lacs/Rivières : garder le tooltip simple pour l'instant ; métriques géométriques plus poussées = TODO lointain/incertain.

## Règles moteur / génération toujours critiques

- Moteur génération v1.5 validé/protégé ; ne pas le modifier sans raison explicite.
- Upgraded utilise les minerais v7 no-gap.
- Building Stones 115..127 ; ID127 = épuisé/0 stock.
- ID84 user-facing = `Pousse d’arbre` / `Tree sapling`, jamais `SmallTree84` dans l'UI.
- Adult tree validated IDs : 68–77, 80–81 ; exact species unresolved for 73–77/80–81, donc nom générique seulement.
- Rivières HEX6, connectées, aucun poisson en rivière.
- Petits étangs 1–4 cases interdits ; redistribution vers lacs existants.
- Snow uniquement via famille Rocky ; pas de snow↔grass direct.
- Ne rien remplacer dans la montagne hormis la neige selon les règles validées.
- Starts : géographie puis fair-play/protection selon architecture validée.
- Ne jamais générer d'illustrations imaginaires pour ce projet ; toute preview de map doit venir des vraies données EDM/MAP/SAV.

## Procédure de reprise

1. Lire `PROJECT_WORKFLOW.md`.
2. Lire `references/SETTLERS3_CURRENT_SNAPSHOT.md` si le repo courant est disponible.
3. Lire ce snapshot de reprise post-v1.7 si la conversation a été interrompue avant intégration des changements dans le repo.
4. Lire `TODO_MAPGEN.md`.
5. Avant toute modification générateur : lire `references/SETTLERS3_PREGEN_READ_FIRST.md`.
6. Vérifier tests + hashes protégés avant packaging.
7. DEV exact → `dev` via `sync_dev_from_zip.ps1` après validation utilisateur ; ne pas faire de synchronisation GitHub partielle.

## v1.8 DEV_3 — current work

- Base : v1.8 DEV_2_R7 validée et synchronisée sur `dev` au commit `85e7bfb`.
- État courant : `v1.8 DEV_3_R7`, Batch Generation validée sous Windows et synchronisée sur `dev` ; DEV_3 terminée.
- Responsive UI v1 et Status/Feedback bar v1 sont implémentés ; aucun changement du moteur de génération.
- R6 remplace la grille globale widget-par-widget par trois régions indépendantes : Génération, Session/Comparaison et contrôles globaux.
- En mode large, Session/Comparaison occupe réellement le centre ; en compact, les blocs entiers se déplacent sans mélanger Langue/Aide/Thème aux paramètres de génération.
- Les rangées Générer/Batch, seed et Importer/Exporter/Aperçu PNG utilisent des layouts locaux ; leurs espacements ne dépendent plus des colonnes de sélecteurs et les boutons fichiers conservent leur largeur naturelle traduite.
- La zone de statut est désormais un feedback humain semi-persistant ; les étapes techniques rapides restent dans la progression.
- Status v1 est FR/EN et relié aux actions principales. Une v2 future doit ajouter couleurs, jolies icônes et une hiérarchie/temporisation plus raffinée sans devenir un log.
- R7 remet la zone Langue/Aide/Thème au véritable bord droit, déclenche le compact à 1750 px avant coupure et rend les boutons A/B naturels tant que Session dispose d'au moins 900 px.
- Les suppressions individuelles A/B affichent une croix rouge déterministe lorsque le slot est rempli ; vide, la croix reste discrète et désactivée.
- Validation automatisée R7 : 90 tests pytest PASS, 49 validations de génération PASS et checksum binaire PASS ; hashes protégés inchangés.
- Validation humaine R7 : header responsive validé sur Windows ; mode large, bascule compacte, ancrage global à droite, largeur adaptative des boutons A/B, croix rouges actives et taille minimale conformes.
- DEV_3_R1 remplace le placeholder `Générer lot…` par une fenêtre Batch FR/EN dédiée à 1–4 cartes.
- Chaque carte possède ses paramètres indépendants : mode, archétype, modificateurs réservés, taille, joueurs et seed ; seules les combinaisons actuellement implémentées/calibrées sont acceptées avant lancement.
- La file réutilise séquentiellement le pipeline v1.5 et le cache de session ; états et progression restent séparés par carte.
- Les résultats réussis rejoignent automatiquement l'historique et peuvent être affichés ou affectés à A/B après le lot.
- L'annulation marque uniquement les cartes encore en attente après la génération courante ; le moteur protégé n'est jamais interrompu.
- Validation automatisée DEV_3_R1 : 95 tests pytest PASS, 49 validations de génération PASS et checksum binaire PASS ; cinq hashes protégés inchangés et conformes au workflow.
- Validation humaine DEV_3_R1 : toutes les fonctions Batch testées sous Windows sont validées ; seuls des détails de présentation et de confort ont motivé R2.
- DEV_3_R2 ouvre les quatre lignes avec la même seed courante/par défaut et conserve les dés globaux et individuels ; une seed commune peut aussi être appliquée aux quatre lignes.
- Chaque réussite reçoit une miniature déterministe issue des données réelles ; clic immédiat et survol volontaire de 700 ms ouvrent une grande vue.
- La ligne résultat suit désormais Afficher / Affecter à A / Affecter à B / progression colorée contenant le feedback.
- Les assignations affichent les pastilles A/B, empêchent une même carte d'occuper simultanément les deux slots et signalent explicitement son déplacement.
- La fenêtre Batch ouverte se retraduit directement avec le changement de langue principal sans perdre les paramètres saisis.
- Validation automatisée DEV_3_R2 : 100 tests de régression PASS, 49 validations de génération PASS et checksum binaire PASS ; cinq hashes protégés inchangés et conformes au workflow.
- Retour Windows R2 : fonctionnement général de nouveau validé ; miniatures trop petites, dé manquant pour la seed commune et agrandissement demandé sous forme de tooltip sans chrome.
- DEV_3_R3 réserve 152×88 pixels par miniature et affiche le rendu réel jusqu'à 144×80, ajoute un dé dédié à la seed commune et remplace la fenêtre d'agrandissement par un tooltip contenant seulement la carte.
- Le clic épingle/désépingle le tooltip ; le survol de 700 ms reste temporaire. En projection parallélogramme, la couche transparente masque entièrement le rectangle autour de la carte sous Windows.
- Validation automatisée DEV_3_R3 : 103 tests de régression PASS, 49 validations de génération PASS et checksum binaire PASS ; cinq hashes protégés inchangés et conformes au workflow.
- Retour Windows R3 : fonctionnement jugé excellent ; miniatures encore légèrement petites/encadrées, projection non dynamique et placement du tooltip trop dépendant du pointeur.
- DEV_3_R4 agrandit la zone miniature à 210×116 et le rendu à 202×108, sans relief ni cadre clair.
- Les résultats Batch déjà générés, y compris le tooltip visible, se recalculent immédiatement lorsque la projection Carrée/Parallélogramme change dans les paramètres principaux.
- Le tooltip est désormais ancré à la miniature : côté offrant le plus d'espace, puis position verticale contrainte à l'écran ; aucune coordonnée du pointeur ne détermine plus son placement.
- TODO futur : importer/valider les sprites natifs exacts des positions de départ afin de produire des marqueurs plus petits et épurés dans les miniatures/aperçus, sans asset inventé.
- Validation automatisée DEV_3_R4 : 105 tests de régression PASS, 49 validations de génération PASS et checksum binaire PASS ; cinq hashes protégés inchangés et conformes au workflow.
- Validation humaine DEV_3_R4 : toutes les modifications fonctionnent parfaitement ; seuls un dernier resserrement des miniatures et une ouverture initiale non tronquée sont demandés.
- DEV_3_R5 resserre le conteneur à 204×110 sans réduire le rendu maximum 202×108, ainsi que les marges verticales secondaires.
- La fenêtre mesure désormais sa taille demandée après construction, utilise cette taille complète si l'écran le permet, se centre relativement à l'application principale et reste contrainte aux limites visibles.
- Validation automatisée DEV_3_R5 : 106 tests de régression PASS, 49 validations de génération PASS et checksum binaire PASS ; cinq hashes protégés inchangés et conformes au workflow.
- Validation humaine DEV_3_R5 : fonctionnement et géométrie initiale validés ; la demande de « resserrer » visait en réalité à agrandir carte et conteneur jusqu'au cadre extérieur.
- DEV_3_R6 agrandit la carte miniature à 222×120 et son conteneur à 224×122 : 1 px interne conservé et environ 1 px jusqu'au cadre blanc extérieur.
- Validation automatisée DEV_3_R6 : 107 tests de régression PASS, 49 validations de génération PASS et checksum binaire PASS ; cinq hashes protégés inchangés et conformes au workflow.
- Validation humaine DEV_3_R6 : taille/hauteur validées ; zone trop large pour le parallélogramme, barre collée et bouton Appliquer du nombre de cartes jugé redondant.
- DEV_3_R7 conserve le parallélogramme à 180×120 dans un conteneur 182×122, ajoute 8 px avant la miniature et centre naturellement la vue Carrée.
- Le nombre de cartes 1–4 s'applique directement par flèches ou saisie clavier ; le bouton Appliquer est supprimé.
- Validation automatisée DEV_3_R7 : 109 tests de régression PASS, 49 validations de génération PASS et checksum binaire PASS ; cinq hashes protégés inchangés et conformes au workflow.
- Validation humaine DEV_3_R7 : espace barre/miniature, conteneur parallélogramme, centrage Carrée et nombre de cartes dynamique validés ; l'ensemble de DEV_3 est accepté.
- Preuve v1.10 archivée : `references/SETTLERS3_V1_10_SEED_DIVERSITY_EVIDENCE_20260822.png`, seeds `69122063`, `958607757`, `1446058262`, `2085415098`. Le symptôme de macro-formes identiques/quasi identiques sous rotations ou symétries est confirmé visuellement, sans diagnostic de cause avant v1.10.

## v1.8 DEV_4_R4 — Visualisations joueurs v4 validée

- Base exacte : `dev` après le checkpoint documentaire `a43f2d1` ; aucun changement de génération.
- Global ne contient plus ni contour initial ni label/position de départ.
- Nouvelle Vue Départs FR/EN validée fonctionnellement en R1 : terrain global et masque initial natif exact, sans pollution de Global.
- Les vingt sprites 36×48 sont extraits automatiquement de `SETTLERS3_PLAYER_START_MARKERS_J1_J20_REFERENCE_20260822.png` ; le fond herbe uniforme devient transparent sans interpolation.
- R2 a centré géométriquement chaque sprite sur sa coordonnée dans Départs et Batch ; ce centrage est validé sous Windows.
- R3 est conservée comme repli visuel. R4 réduit ses 210 marqueurs frontaliers à la taille minimale sans chevauchement : 1×1 Carrée / 2×2 Parallélogramme. Le marqueur central conserve sa taille validée 18×24 / 36×48.
- L'opacité devient disponible dans Départs et affecte seulement la couche de sprites : 100 % complet, 0 % identique à Global. Global reste verrouillée à 100 %.
- Batch conserve uniquement ses marqueurs centraux compacts, sans frontière initiale. Un TODO séparé prévoit l'essai d'une taille réduite et d'un réglage/masquage dans Paramètres ou Batch.
- La liste place désormais Territoires immédiatement après Départs.
- Territoires SAV conserve strictement les claims runtime 0..19. Territoires EDM/MAP et états générés sans claims reconstruisent seulement à l'écran le masque initial exact de 3500 cellules autour de chaque start ; les chevauchements vont au départ HEX6 le plus proche, puis au joueur le plus petit en cas d'égalité.
- La retouche/modernisation manuelle éventuelle des marqueurs est reportée à la future refonte Pixel Art.
- Les labels ne sont pas réintroduits en R2 : une passe ultérieure devra concevoir leur forme, position, ancrage et gestion des collisions.
- La refonte future Vues ↔ Graphiques est consignée sous le nom de travail `Pilotage de la vue`, conjointement avec l'étude des vues composables.

## Prochaine action recommandée

Validation Windows obtenue : finesse de la frontière sans chevauchement, ordre des vues, opacité, Territoires synthétique EDM/MAP et claims réels SAV acceptés. Promouvoir exactement R4 sur `dev` sans toucher à `main`.

Conserver séparément : extraction éventuelle de la couleur effective des joueurs, interaction Graphiques→carte et étude contrôlée des Terrain IDs 18/19 pour v1.9 ; viewer scindable jusqu'à quatre cartes après la grosse passe générateur ; audit seed/diversité uniquement en v1.10 ; vues composables comme étude UX sans garantir toutes les combinaisons. Un moteur de formes alternatif réellement distinct de Legacy/Upgraded reste une piste non versionnée à n'ouvrir qu'après v1.10 et la consolidation des objectifs natifs.


## v1.8 DEV_2_R2 checkpoint
- Windows 1080p feedback caused a responsive R2: map-specific controls moved into a scalable viewer toolbar; 1080p explicitly selects compact layout.
- Obsolete header Progressbar removed from layout (it caused a persistent pale/white strip after resize).
- Status/Feedback v1 expanded with additional user actions; fast generator details remain in the map progress overlay.
- Future UI TODO includes magnifier/precision cursor + optional inspector-near-cursor toggle and a more compact zoom control.

## v1.8 DEV_2_R3 checkpoint
- Header réorganisé par fonction, selon le retour visuel Windows de DEV_2_R2.
- 1080p n'est plus forcé en mode compact uniquement à cause de sa hauteur : le layout large est conçu pour y tenir proprement.
- Génération à gauche ; Session/Comparaison au centre lorsque la largeur le permet ; Langue/Aide/Thème à droite.
- Copier seed reste rattaché visuellement à Seed.
- Inspecteur reste visible dans la zone supérieure (placement encore temporaire à long terme).
- Feedback reste une barre fine mais majeure, visible juste avant la zone Map/Data.
- Viewer toolbar et progression validés en R2 restent inchangés.


## v1.8 DEV_2_R4 checkpoint

- Modificateurs réservé dans le header via menu à cases cochables ; `Aucun` seul actuellement.
- Modificateurs intégré à la clé de cache, à l’historique et aux messages de génération/état.
- Historique Session compacté ; Charger/Vider cache passent en seconde ligne quand le bloc est contraint.
- Aide/Thème passent sous Langue en mode étroit.
- Progression validée++ et gelée pour cette passe.

## v1.8 DEV_2_R5_R5 checkpoint

- Paint 3 utilisé comme référence du header ; minimum 900 px atteint sans chevauchement destructeur.
- Test Windows utilisateur effectué sur 2560×1392, 1920×1020 et 902×682.
- R5_R5 non retenue comme layout final : Session/Comparaison ne revenait pas au centre en mode large, Langue/Aide/Thème se mélangeait à la grille Génération au minimum et les boutons fichiers étaient tronqués.

## v1.8 DEV_2_R6 checkpoint

- Trois régions structurelles indépendantes au lieu d'une grille globale de widgets.
- Mode large : Génération à gauche, Session/Comparaison réellement au centre, contrôles globaux à droite.
- Mode compact : Génération et contrôles globaux restent séparés ; Session descend comme un bloc complet.
- Les boutons d'action sont organisés dans des barres locales équidistantes et gardent leur largeur textuelle naturelle.
- 86 tests pytest PASS ; 49 validations de génération PASS ; checksum binaire PASS ; hashes protégés inchangés.
- Test visuel Windows/GIF effectué ; R6 non retenue comme version finale à cause du clipping pré-compact et de l'ancrage incomplet à droite.

## v1.8 DEV_2_R7 checkpoint

- Retour R6 : taille minimum jugée très bonne et structure générale presque finale.
- Analyse frame par frame du GIF : thème coupé pendant les dernières frames du mode large ; ancien poids élastique de la colonne 11 empêchant la région globale d'atteindre le bord réel.
- Ancien poids supprimé ; breakpoint compact relevé de 1600 à 1750 px.
- Boutons A/B à largeur naturelle lorsque Session a la place, largeur bornée seulement sous 900 px en mode compact.
- Suppression A/B : croix rouge raster active, croix grise désactivée lorsque le slot est vide.
- 90 tests pytest PASS ; 49 validations de génération PASS ; checksum binaire PASS ; hashes protégés inchangés.
- Validation Windows utilisateur terminée sur GIF de redimensionnement avec et sans A/B définis : aucun chevauchement ni contrôle coupé ; passage large/compact, ancrage à droite, boutons A/B et croix rouges validés.

## v1.8 DEV_3_R1 checkpoint

- Première implémentation fonctionnelle de Batch Generation derrière le bouton réservé depuis DEV_2.
- Fenêtre externe pour préserver le header validé et garder quatre configurations lisibles.
- 1–4 cartes, paramètres indépendants, seeds aléatoires individuelles, exécution séquentielle.
- États attente/génération/succès/cache/erreur/annulation et progression individuelle.
- Résultats réussis ajoutés au cache/historique ; affichage et assignation A/B disponibles après le lot.
- Annulation limitée aux éléments en attente afin de ne jamais interrompre le moteur v1.5.
- 95 tests pytest PASS ; 49 validations moteur PASS ; checksum binaire PASS ; cinq hashes protégés inchangés.
- Validation fonctionnelle Windows utilisateur terminée ; R2 porte uniquement le polish final demandé.
- Rappel effectué après validation et synchronisation `dev` ; notes locales reçues et consolidées le 2026-08-22.

## v1.8 DEV_3_R2 checkpoint

- Quatre seeds initiales identiques, dérivées de la seed courante/par défaut ; dés globaux et individuels conservés ; application commune ajoutée.
- Miniatures et agrandissements calculés uniquement depuis les vraies cartes générées.
- Clic immédiat et survol temporisé 700 ms disponibles simultanément pour test Windows.
- Ligne résultat réordonnée et progression/feedback fusionnés dans une barre sémantique colorée.
- A/B exclusifs, pastilles d'occupation synchronisées et feedback de déplacement.
- Retraduction directe de la fenêtre Batch ouverte.
- 100 tests de régression PASS ; 49 validations moteur PASS ; checksum binaire PASS ; cinq hashes protégés inchangés.
- Validation fonctionnelle Windows R2 obtenue ; trois détails visuels/confort reportés dans R3.

## v1.8 DEV_3_R3 checkpoint

- Miniature réelle corrigée : conteneur fixe 152×88, rendu maximum 144×80.
- Dé de seed commune ajouté sans retirer aucun dé existant.
- Agrandissement devenu un tooltip map-only, sans barre de titre ni bordure.
- Clic épinglé/désépinglé et survol volontaire 700 ms temporaire.
- Transparence du rendu parallélogramme conservée sur la surface Windows.
- 103 tests de régression PASS ; 49 validations moteur PASS ; checksum binaire PASS ; cinq hashes protégés inchangés.
- Validation fonctionnelle Windows R3 obtenue ; ajustements finaux de taille, projection et position reportés dans R4.

## v1.8 DEV_3_R4 checkpoint

- Miniatures sans cadre : zone 210×116, carte jusqu'à 202×108.
- Projection Carrée/Parallélogramme synchronisée immédiatement avec les miniatures et le tooltip Batch ouvert.
- Placement du tooltip adjacent à la miniature et indépendant du pointeur.
- Futurs sprites natifs de départ consignés au TODO, sans ajout d'asset dans R4.
- Audit seed/diversité morphologique consigné comme priorité majeure de v1.10.
- 105 tests de régression PASS ; 49 validations moteur PASS ; checksum binaire PASS ; cinq hashes protégés inchangés.
- Validation Windows R4 terminée ; derniers réglages de densité et taille initiale reportés dans R5.

## v1.8 DEV_3_R5 checkpoint

- Conteneur miniature 204×110, rendu maximum toujours 202×108.
- Espacements verticaux légèrement resserrés.
- Taille initiale calculée depuis le contenu réellement demandé.
- Centrage relatif à la fenêtre principale et contrainte aux limites écran.
- 106 tests de régression PASS ; 49 validations moteur PASS ; checksum binaire PASS ; cinq hashes protégés inchangés.
- Validation Windows R5 terminée hors interprétation finale de la taille des miniatures.

## v1.8 DEV_3_R6 checkpoint

- Carte miniature 222×120 maximum dans un conteneur 224×122.
- Environ 1 px entre carte/conteneur et conteneur/cadre extérieur.
- Tous les comportements R5 préservés.
- 107 tests de régression PASS ; 49 validations moteur PASS ; checksum binaire PASS ; cinq hashes protégés inchangés.
- Validation Windows R6 terminée hors trois derniers détails d'espacement/commande.

## v1.8 DEV_3_R7 checkpoint

- Parallélogramme 180×120 dans un conteneur 182×122.
- Marge de 8 px entre progression et miniature.
- Nombre de cartes appliqué dynamiquement ; bouton Appliquer supprimé.
- 109 tests de régression PASS ; 49 validations moteur PASS ; checksum binaire PASS ; cinq hashes protégés inchangés.
- Validation Windows finale terminée ; DEV_3 synchronisée sur `dev`.
- Notes locales utilisateur récupérées et consolidées dans `TODO_MAPGEN.md` ; prochain checkpoint à choisir dans la fin de v1.8.

## v1.8 DEV_4_R4 checkpoint

- R1 validée fonctionnellement sous Windows : Global épurée, Départs dédiée, Territoires J1–J20, sprites nets/transparents, FR/EN, thèmes et zoom.
- R2 validée : centrage géométrique dans Départs et Batch.
- R3 : 210 marqueurs 3×4 / 6×8 et opacité Départs fonctionnelle ; conserver comme repli.
- R4 validée sous Windows : 210 marqueurs sans chevauchement 1×1 / 2×2 ; Territoires placé après Départs et synthétisé depuis le masque natif exact pour EDM/MAP.
- Labels reportés à une passe de conception ; retouche manuelle reportée à la refonte Pixel Art.
- Validation automatisée R4 : 121 tests PASS ; vrais rendus EDM Départs/Territoires contrôlés en Parallélogramme ; 49 validations moteur et checksum binaire PASS ; cinq hashes protégés inchangés.
