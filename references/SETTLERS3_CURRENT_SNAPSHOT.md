# Settlers III MapGen — CURRENT SNAPSHOT

> **LIVING RECOVERY SNAPSHOT — v1.8 development.**
>
> Last refreshed: **2026-08-22 — v1.8 DEV_2_R7**

## État release / Git

- Repository : `JulienP36/settlers3-mapgen`.
- `main` = STABLE uniquement ; `dev` = développement ; `rc` reste en place pour le moment mais son utilité sera réévaluée si les futures RC restent courtes.
- v1.7 STABLE publiée sur GitHub, tag `v1.7`.
- Commit `main` de promotion v1.7 STABLE : `780bc5e` — `release: Settlers3 MapGen v1.7 STABLE`.
- ZIP final GitHub Release généré directement depuis le tag `v1.7` : `SETTLERS3_MAPGEN_V1_7_STABLE_20260821.zip`.
- SHA-256 ZIP final : `593A86CEE2926344D1C2675C23D5F99E2A5058C0DCC50A1A4A4D9EA077DC94E5`.
- Updater actuel détecte correctement v1.7 comme dernière STABLE.
- v1.7 = socle Stats/Graphs ; moteur de génération v1.5 validé/protégé inchangé.


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
- cases `.edm`, `.map`, `.sav` ;
- option potentielle PNG de la vue de base ;
- conserver séparément l'export PNG de la vue courante (overlays/zoom/vue active).

### 3. Export Graphiques unifié

Étudier/remplacer les multiples boutons d'export par un bouton `Exporter…` ouvrant une popup avec formats applicables (PNG/CSV/JSON selon contexte). Garder une architecture extensible.

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

## v1.8 DEV_2 — current work

- Base : v1.8 DEV_1 validée et synchronisée exactement sur `dev` au commit `57d9569`.
- Candidate courante : `v1.8 DEV_2_R7`, validée sous Windows après contrôle du GIF de redimensionnement avec et sans slots A/B définis.
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

## Prochaine action recommandée

Synchroniser le ZIP exact de **v1.8 DEV_2_R7 validée** vers `dev` via `sync_dev_from_zip.ps1`, puis vérifier l'état Git conformément au workflow. Ne pas ouvrir la fonctionnalité suivante avant cette synchronisation propre.


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
