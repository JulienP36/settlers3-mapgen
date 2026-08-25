# Settlers III MapGen — TODO programme

## État de validation

- [x] **v1.5 VALIDÉE / STABLE** pour Continental 768×768.
- [x] Référence finale : `S3_V1_5_V7NOGAP_CORRECTED_UPGRADED_4P_768x768_seed_2026082202`.
- [x] Starts / éditeur / View Map / in-game / aucun crash.
- [x] Minerais Upgraded géométrie **v7 no-gap** verrouillée.
- [x] Legacy / Upgraded séparés.
- [x] Building Stones 115..127 et ID127 constructible gérés.
- [x] Bonus de départ Upgraded validés.
- [x] **v1.6 STABLE UI/outillage** : validation utilisateur terminée.
- [x] **v1.7 STABLE Stats/Graphs** : publiée sur GitHub, tag `v1.7`, updater validé.

## Règle de release

**Ne pas modifier la génération v1.5 validée sans raison explicite.**

v1.6 est une surcouche UI/outillage ; `generator_v15.py` reste le moteur de référence.

## UX / outillage — v1.6

- [x] Import EDM / MAP / SAV ; export EDM+MAP 768.
- [x] Global / Heightmap / Ressources / Territoires.
- [x] Chemins / Terrain28 et Terrain22 runtime.
- [x] Cultures.
- [x] Heatmap ressources.
- [x] FR/EN persistant.
- [x] Inspecteur exact de cellule au survol.
- [x] Zoom / drag / projection / recentrage.
- [x] Thème sombre/clair ; combobox lisibles ; sliders click-to-position.
- [x] Cache transparent LRU mémoire de session, 8 générations.
- [x] Historique de session.
- [x] Comparaison A/B légère avec conservation du contexte visuel.
- [x] Raccourcis configurables/persistants + conflits + reset.
- [x] Aide F1 dynamique.
- [x] **Palette P1..P20** : validée visuellement en R4 ; P9 quasi blanc/ivoire et contours noirs validés.
- [x] **Contour de zone de départ d'origine sur import SAV** : bloc joueur SAV + masque natif exact 3500 cellules, validé visuellement. Évolution possible plus tard vers une vue dédiée.
- [ ] Comparaison A/B avancée côte-à-côte/diff uniquement si l'usage réel le justifie — non prioritaire.
- [ ] Étendre éventuellement les commandes rebindables après retour d'usage.

## Après validation v1.6 — GIGA passe Statistiques

Transformer l'onglet Statistiques en véritable outil d'analyse détaillé :

- [x] nombre exact de cellules par Terrain ID ;
- [x] quantité de chaque objet/ressource ;
- [x] stock total exploitable Building Stones ;
- [x] distribution des états 115..127 ;
- [x] graphes des ressources minières : stock réel (cases disponibles dans le modèle ; graphe dédié à enrichir) ;
- [x] densités normalisées par 1000 cellules avec dénominateur pertinent selon la donnée (terre/eau/montagne) — DEV_10 ;
- [x] ratios land/ocean, biomes, eau intérieure, forêts, ressources — socle ;
- [~] blobs / massifs / lacs / rivières / clusters : moteur de composantes avancé DEV_4, analyses/distributions à enrichir ;
- [x] distances inter-starts + voisin le plus proche ;
- [x] percentiles utiles — relief, quantités minières et distances ;
- [x] suivi Terrain24 / Terrain22 / Terrain28 via les comptes Terrain ID ;
- [ ] autres métriques et graphes pertinents tant que lisibles/exploitables.


## DEV_10 / DEV_11 — socle Stats / Graphiques avant RC

- [x] Page Statistiques assumée comme outil de **debug technique** : inventaire exhaustif de tous les Terrain IDs et Object IDs présents, sans limite Top 12.
- [x] Densités normalisées `/1000` avec support pertinent : terre pour arbres/pierres/agriculture, eau pour poissons, montagne pour minerais.
- [x] Export CSV enrichi avec les densités normalisées ; JSON schema v7 après correction Herbe sèche.
- [x] Tooltips interactifs génériques sur les segments/barres des graphes, y compris A/B.
- [x] Tooltips : fenêtre persistante pendant le mouvement + sémantique par segment (libre/sous neige, mer/lacs, roche/neige, rayons, minerais, A/B) — DEV_10_R2.
- [x] Slots de comparaison A/B : état visible directement sur les boutons avec LED verte + identification courte de la map définie.
- [x] DEV_11 : famille **Herbe** corrigée et segmentée en Herbe verte (Terrain 16) + Herbe sèche (Terrain 24), avec légende et tooltips dédiés.
- [x] DEV_11 : tooltips enrichis avec les IDs contextuels utiles (terrain, objet ou ressource) sans ajouter systématiquement le terrain support quand il n'apporte rien.
- [x] DEV_11 : onglet **Statistiques** confirmé comme surface utilisateur bilingue FR/EN (rapport structuré + inventaires debug).
- [x] v1.8 DEV_1 : permettre de vider/réinitialiser séparément A, B, ou les deux ; les boutons LED/labels remplacent le texte redondant sous l’historique.
- [ ] Futur inventaires debug : tri commutable par quantité / ID / nom et option pour afficher les IDs connus mais absents de la map.
- [ ] Futur : étendre le debug à d’autres familles runtime quand identifiées (settlers/colons, marchandises, planches, rondins, pierres taillées, outils, armes, bâtiments, etc.) sans inventer les IDs.
- [ ] Futur : refonte UI légère de la section Comparaison, sans changer son fonctionnement de base.
- [ ] Futur : synchronisation optionnelle/désactivable Graphiques ↔ vue Map, hors périmètre du socle v1.7 initial.
- [x] **v1.8 DEV_6_R1 validée sous Windows** : allemand (DE) et espagnol (ES) ajoutés à l’interface dynamique complète, y compris Statistiques, Graphiques, Batch, exports, aide, états et persistance.
- [ ] **Rafraîchissement i18n de l’onglet Statistiques** : lorsqu’une carte est déjà chargée, le rapport texte ne se retraduit actuellement qu’après rechargement de la carte. Corriger ce rafraîchissement lors de la future amélioration de l’onglet Statistiques ; non bloquant pour DEV_6.
- [ ] **Relecture linguistique communautaire** : FR/EN sont les références relues. DE/ES sont des traductions automatiques seulement partiellement revues ; conserver cet avertissement public et intégrer les corrections de locuteurs avant de les qualifier de validées. Appliquer la même règle à toute future langue.
- [x] v1.8 DEV_1 : traduire intégralement le **titre de la fenêtre**, y compris le libellé du moteur.
- [x] v1.8 DEV_5_R3 : centre d’export map multi-format validé sous Windows ; géométrie/thème corrigés, modalité Windows stricte et formats indisponibles grisés/barrés.
- [x] v1.8 DEV_5_R3 : bouton Graphiques **Exporter…** unique et popup JSON/CSV/PNG validés sous Windows ; mêmes corrections de géométrie, thème et modalité.
- [ ] Futur proche : rendre configurables les **2 rayons** utilisés par Arbres/Pierres/Poissons/Stock minier proches (rester à deux intervalles ; pas de troisième rayon dans l'UI actuelle).
- [ ] Futur Graphiques : proposer éventuellement plusieurs représentations d'une même métrique (ex. barres / donut) via un sélecteur, plutôt lors d'une grosse évolution Stats/Graphs.
- [ ] Futur Graphiques : histogrammes de distribution des tailles de massifs/lacs/rivières.
- [ ] Futur Graphiques : profil radial/cumulatif des ressources autour d'un start.
- [ ] Idée expérimentale/non garantie : radar léger de richesse par joueur uniquement si une représentation non trompeuse apporte une vraie valeur.
- [ ] Futur comparaison corpus : boxplots / bandes de référence pour situer MapGen dans les distributions natives lorsque ce chantier de calibration sera ouvert.
- [ ] Très lointain/incertain : détails géométriques supplémentaires dans les tooltips massifs/lacs/rivières (périmètre, bbox, compacité, allongement) seulement si l'usage le justifie.


### Responsive / Status feedback

- [x] **v1.8 DEV_2_R2 — Responsive UI v1** : première passe compacte testée sur petite surface ; outils Vue/Carte thermique/Recentrer/Zoom déplacés dans une barre contextuelle du viewer avec reflow indépendant ; ancienne Progressbar de header supprimée du layout ; préserver le splitter carte/panneaux.
- [x] **v1.8 DEV_2_R2 — Status/Feedback v1** : formaliser la zone d’état comme feedback utilisateur lisible ; réserver les étapes rapides à la progression ; relier les principales interactions ; FR/EN. R2 ajoute notamment bascule A/B explicite, cache vide, bouton thème, recentrage, seed aléatoire, exports Stats/Graphiques, opacité indisponible et synchronisation du nombre de joueurs.
- [x] **v1.8 DEV_2_R3 — Header fonctionnel** : réorganiser le haut par fonction (Génération à gauche, Session/Comparaison au centre quand la largeur le permet, Langue/Aide/Thème à droite), garder Copier seed près du Seed, Inspecteur visible en haut et Feedback comme messager principal ; réserver le mode compact aux fenêtres réellement étroites.
- [x] **v1.8 DEV_2_R4 — Densité du header + emplacement Modificateurs** : réserver après Archétype un menu à cases cochables compatible multi-modificateurs (Aucun seul pour l’instant), intégrer ce paramètre au cache/historique/feedback ; réduire la largeur par défaut de l’historique, faire descendre Charger/Vider cache quand Session est contrainte, et empiler Aide/Thème sous Langue en mode étroit.
- [x] **v1.8 DEV_2_R5_R5 — Paint 3, test Windows effectué** : structure stable et minimum 900 px obtenus, mais retour utilisateur non validant pour le header final : Session restait en bande inférieure au lieu d'occuper le centre en mode large, contrôles globaux mélangés aux paramètres en compact et boutons Importer/Exporter/Aperçu tronqués par des largeurs fixes.
- [x] **v1.8 DEV_2_R6 — test Windows + GIF effectué** : trois régions et minimum jugés très proches du résultat final ; GIF de redimensionnement validant la structure générale, mais révélant le bouton Thème coupé juste avant le passage compact, la zone globale pas complètement ancrée à droite et les identités A/B encore tronquées par largeur fixe.
- [x] **v1.8 DEV_2_R7 — validée sous Windows** : GIF de redimensionnement contrôlé avec et sans A/B définis ; ancrage réel à droite, passage compact à 1750 px sans coupure, boutons A/B adaptatifs, croix rouge active et taille minimale validés.
- [ ] **Status/Feedback v2 — grosse révision UI future** : couleurs sémantiques, jolies icônes dessinées/validées sans génération d’image IA, meilleure hiérarchie/priorité/temporisation, davantage d’actions liées et explications de contrôles indisponibles. Garder la zone concise : ce n’est pas un journal/log.
- [ ] **Audit global des états interactifs — refonte UI future** : retrouver et harmoniser dans toute l’application les contrôles désactivés, verrouillés ou temporairement indisponibles ; vérifier normal/survol/pression/focus en clair et sombre. R3 expérimente dans les centres d’export le couple texte grisé + barré avant toute généralisation.
- [ ] **Responsive UI v2 / refonte UI future** : revoir plus profondément l’organisation, breakpoints, densité, éventuels panneaux repliables/scroll de secours après retour d’usage sur v1.

## v1.8 — Workflow, accessibilité & production (13 axes validés)

- [x] **Batch Generation — DEV_3_R7 validée sous Windows** : fenêtre 1–4 cartes, paramètres indépendants, seeds communes/individuelles, exécution séquentielle, cache, annulation en attente, historique, miniatures/tooltip dynamiques, assignation A/B exclusive, progression/feedback et nombre de cartes dynamique. DEV_3 terminée et synchronisée sur `dev`.
- [x] **Vue Territoires — palette joueurs exacte — DEV_4_R1 validée sous Windows** : claims 0..19 reliés strictement à la palette J1–J20 centralisée et validée dans [`SETTLERS3_PLAYER_COLORS_20_REFERENCE_20260820.png`](references/SETTLERS3_PLAYER_COLORS_20_REFERENCE_20260820.png) ; les valeurs inconnues ne sont plus recyclées par modulo.
- [x] **Vue Départs dédiée — DEV_4_R4 validée sous Windows** : Global épurée, Carrée/Parallélogramme, centrage et opacité validés. La frontière conserve exactement 210 marqueurs à la taille minimale sans chevauchement, 1×1 Carrée / 2×2 Parallélogramme. Cet aspect devient la référence ; R3 reste seulement un repli historique.
- [ ] **Label joueur de la Vue Départs — passe de conception dédiée** : réintroduire plus tard une identification J1–J20 après brainstorming de sa forme, de son ancrage, de sa position et de ses collisions, afin d'aboutir à un rendu fini plutôt qu'à un simple retour de l'ancien texte.
- [x] **Export maps multi-format — DEV_5_R3 validée sous Windows** : popup bilingue, dossier et nom de base commun, sélection EDM/MAP/copie SAV inchangée/PNG Global/PNG vue actuelle, disponibilité explicite, résumé des noms et confirmation groupée. R2 désactive Vue actuelle lorsque Global la rendrait identique et corrige bas de fenêtre/survols ; R3 bloque toute interaction extérieure et rend les choix indisponibles grisés/barrés.
- [x] **Export Graphiques unifié — DEV_5_R3 validée sous Windows** : bouton unique `Exporter…`, dossier et nom commun, sélection JSON/CSV/PNG du graphique affiché, résumé et confirmation groupée ; géométrie et états de thème corrigés en R2, modalité stricte en R3.
- [ ] **Évolutivité future des centres d’export** : leur hauteur initiale est déjà calculée depuis le contenu réel. Si des formats supplémentaires sont ajoutés, préserver ce calcul puis contraindre la fenêtre à la hauteur visible de l’écran avec une zone défilable de secours lorsque le contenu ne peut plus tenir entièrement.
- [x] **A/B polish léger — DEV_1** : reset A/B/A+B, suppression du résumé texte redondant, boutons LED conservés.
- [x] **Titre de fenêtre entièrement i18n — DEV_1** : FR/EN.
- [x] **Langues programme — DEV_6_R1 validée** : allemand (DE) + espagnol (ES) implémentés avec FR/EN, sélection par drapeaux, application dynamique et persistance. FR/EN sont les références relues ; DE/ES restent explicitement automatiques et partiellement revues. Communication externe surtout EN/FR, DE ponctuel possible.
- [ ] **Packs de langue communautaires — version non fixée** : extraire à terme les textes du code vers des catalogues externes à identifiants sémantiques stables, puis charger les langues intégrées et personnalisées depuis un dossier utilisateur sans surveillance permanente.
  - format de données uniquement, sans code exécutable : JSON versionné ou paquet `.s3lang` ; métadonnées `code`, nom natif, auteur, version, compatibilité et langue parente ;
  - héritage par `extends` afin qu’une traduction, une variante régionale ou une langue fantaisie (LOLCAT, Shakespeare, etc.) puisse ne remplacer que les textes souhaités ; repli vers la langue parente puis l’anglais ;
  - commandes utilisateur : ouvrir le dossier des langues, créer/exporter un modèle, vérifier un pack et recharger les langues ; apparition automatique des packs valides dans le sélecteur ;
  - éditeur intégré envisageable : identifiant, références FR/EN, traduction, recherche, entrées manquantes, aperçu dynamique et export ;
  - validation stricte : syntaxe, version, clés inconnues/manquantes, textes vides, Unicode, compatibilité programme et conservation exacte des variables `{seed}`, `{players}`, `{error}`, etc. ; un pack invalide ne doit jamais empêcher le démarrage ;
  - icône facultative ; sinon badge neutre fondé sur le code de langue, plus adapté aux variantes et langues fictives qu’un drapeau obligatoire ;
  - avant ce chantier, centraliser tous les événements de changement de langue et éliminer les derniers textes dispersés, notamment le rafraîchissement tardif du rapport Statistiques.
- [ ] **Écosystème de thèmes complet — version lointaine non fixée / mise à jour dédiée probable** : centraliser les couleurs de l’interface dans une palette sémantique globale afin que chaque famille de widgets et chaque état (`normal`, survol, pressé, sélectionné, désactivé, focus) produisent un résultat prévisible. Le programme peut rester coloré : définir des rôles cohérents pour actions principales, information, succès, avertissement, erreur, sélection, progression, joueurs, graphiques, icônes et images, sans couleurs ponctuelles arbitraires difficiles à maintenir. Prévoir ensuite un format de thème déclaratif complet, validé et sans code exécutable, avec héritage/repli vers un thème intégré, aperçu, rechargement explicite, outils de création et possibilité de thèmes communautaires sans dupliquer les styles widget par widget. Le chantier peut être plus court qu’une langue complète sans devoir être volontairement minimal.
- [x] **Fenêtre d’aide et thèmes — DEV_8_R4 validée sous Windows** : le `messagebox` natif est remplacé par une vraie fenêtre d’aide FR/EN/DE/ES, pilotée par la palette sémantique et la barre de titre native. Elle reste consultable pendant l’utilisation, se retraduit en direct et affiche les raccourcis réellement configurés.
- [x] **Barres de titre natives thémables — TITLEBAR_TEST_R4 validée sous Windows** : rôles distincts pour barre, texte, contour Windows, séparateur interne et mode clair/sombre des contrôles natifs. Palettes claire et sombre validées, cadre/Snap Windows conservés, actualisation événementielle sans polling ni coût CPU permanent observable. Les futurs thèmes pourront fournir ces cinq rôles sans modifier le mécanisme.
- [x] **Raccourcis v2 — DEV_8_R4 validée sous Windows** : capture fondée exclusivement sur les événements d’appui/relâchement des modificateurs, sans état global Windows ni bits Tk ambigus ; actions supplémentaires, AZERTY/QWERTY, conflits non modaux, modifications en attente, désactivation/reset et migration du JSON existant.
- [x] **Historique session amélioré — DEV_7_R10 validée sous Windows** : imports + Batch dans l’historique, capacité configurable, Centre dédié, rang stable lors des actions UI, aperçu sélectionné et grand aperçu aligné sur Batch, protections `V/A/B` explicites et indicateurs accessibles avec libellés contextuels. R9 a sécurisé le cycle de vie du Centre et finalisé les cinq états de loupe ; R10 empêche les aperçus temporaires de masquer leur miniature source sans contraindre les aperçus épinglés.
- [ ] **Signalétique set/unset — future passe UI** : revoir le design des états Chargée/Affichée/Affectée afin que la différence set/unset se lise encore plus vite, au-delà du cercle coché et du seul changement de libellé ; conserver une information non fondée uniquement sur la couleur et vérifier clair/sombre ainsi que daltonisme.
- [x] **Preuve de faisabilité `.exe` — DEV_9_R2** : packaging Windows x64 autonome `onedir`, ressources embarquées, chemins robustes, import complet du runtime GUI par l’autodiagnostic, ZIP et SHA-256 automatisés ; démarrage Windows réel validé après correction R2.
- [ ] **Paquet `.exe` final — phase RC v1.8** : ne plus reconstruire PyInstaller pendant les DEV ordinaires. À partir des RC, publier séparément un ZIP sources/Python et un ZIP Windows x64 portable sans installation, puis reprendre les derniers ajustements de packaging.
- [~] **Icône application/exe — infrastructure DEV_9_R2** : build prêt à adopter automatiquement `assets/Settlers3MapGen.ico`. L’icône finale sera dessinée manuellement en pixel art par l’utilisateur et intégrée pendant une future passe visuelle ou les RC. Aucune image IA.
- [ ] **Passe d’iconographie UI dédiée** : petites icônes déterministes, dessinées ou validées manuellement, pour faciliter le repérage dans toute l’application ; à traiter comme focus d’une version ultérieure, sans urgence.
- [~] **Registre de provenance des éléments visuels** : registre initial créé dans `references/SETTLERS3_VISUAL_ASSET_PROVENANCE.md` pour les références et assets actuellement utilisés ; le compléter avant chaque future intégration graphique externe.
- [ ] **Passe Pixel Art faite main — option lointaine** : l'utilisateur pourra finalement choisir de créer ou retoucher lui-même une partie ou la totalité des icônes ; l'assistant peut aider à définir les idées, contraintes, tailles, états et cohérence visuelle, sans produire d'image non demandée. La modernisation manuelle éventuelle des marqueurs J1–J20 est explicitement reportée à cette passe.
- [x] **Sprites J1–J20 dans Départs et Batch — DEV_4_R4 validée sous Windows** : extraction, transparence, netteté, correspondance joueurs, centrage et opacité validés. Départs emploie 210 marqueurs minimaux 1×1 / 2×2 sur la frontière, plus le marqueur central validé. Batch conserve seulement le marqueur central compact.
- [x] **Territoires EDM/MAP — DEV_4_R4 validée sous Windows** : Territoires est placé juste après Départs. Pour SAV, conserver les claims runtime réels. Pour EDM/MAP et états générés sans claims, reconstruire une couche initiale depuis le masque natif exact de 3500 cellules autour de chaque start ; ne jamais présenter cette couche comme une information lue dans le fichier. Chevauchements : départ HEX6 le plus proche, puis plus petit numéro de joueur en cas d'égalité.
- [x] **Réglage des marqueurs Batch — DEV_4_R5 validée sous Windows** : réglage global persistant dans Paramètres, choix `Masqués / Petits / Normaux`, valeur par défaut `Petits`, actualisation immédiate des miniatures et du grand aperçu. Pilote de rendu par couches validé : base sans marqueurs conservée par résultat/projection, recomposition limitée aux sprites et remplacement atomique du tooltip sans clignotement.
- [x] **Interaction grand aperçu Batch — DEV_4_R6 validée sous Windows** : un aperçu épinglé se déplace par glisser-déposer, un clic sur son image ne le ferme plus, cliquer une autre miniature remplace la carte à la même position, et recliquer la miniature source ferme l'aperçu. `Échap`, placement initial automatique, limites d'écran et survol temporaire sont conservés. Changements de projection et de miniature utilisent un double tampon validé pour afficher la nouvelle surface avant de retirer l'ancienne.
- [ ] **Updater v2 pour exécutable — phase RC v1.8** : version locale/dernière STABLE, SHA, settings préservés, remplacement/rollback propre ; aucun chantier updater pendant les DEV ordinaires.
- [x] **README transparence IA** : conception/direction humaine et usage important de ChatGPT/OpenAI explicitement indiqués, notamment pour le backend, l’analyse et le reverse-engineering.
- [ ] **Découvrabilité GitHub** : About/Topics, entrée anglaise claire, FR conservé, termes Settlers III/Settlers 3/Siedler III + EDM/MAP/SAV naturels, sans spam SEO.

### Rappel de checkpoint DEV_3

- [x] DEV_3 validée sous Windows et synchronisée sur `dev` ; dernières notes du TODO local reçues et consolidées le 2026-08-22.

## v1.9 — Archéologie / Data Mapping (transition planifiée)

- [ ] Déterminer les bornes réelles des Terrain IDs et Object IDs ; `0–255` n’est qu’une grille technique 8-bit, pas une borne validée.
- [ ] Compléter progressivement les registres `references/SETTLERS3_TERRAIN_IDS_REFERENCE.md` et `references/SETTLERS3_OBJECT_IDS_REFERENCE.md`.
- [ ] Clarifier trous/réservés, familles/transitions et autres catégories SAV : settlers/colons, marchandises, outils, ressources transformées, bâtiments, etc., sans inventer.
- [ ] Consolider les tables utilisées par Stats/Tooltips avant les modifications profondes du générateur.
- [ ] **Couleur effective des joueurs dans les fichiers** : vérifier si EDM/MAP/SAV expose réellement l'identité ou la couleur affectée à chaque joueur ; si l'information est démontrée, l'utiliser dans les vues Territoires, Départs, Stats et autres visualisations pertinentes au lieu de déduire aveuglément la palette par numéro de slot.
- [ ] **Interaction Graphiques → carte** : dans `Graphiques > Familles de terrain`, permettre au survol d'un biome/de sa série de mettre temporairement en surbrillance les cellules correspondantes dans la carte. Définir précisément le comportement lorsque plusieurs familles ou couches sont actives.
- [ ] **Terrain IDs 18 et 19 — détails d'herbe provisoires** : observations actuelles consignées comme `Détail herbe 1` / `Grass detail 1` et `Détail herbe 2` / `Grass detail 2`. Ils semblent apparaître isolément et uniquement entourés d'herbe. En v1.9, tester leur placement contrôlé, notamment en groupes, vérifier les transitions/artefacts ou incompatibilités graphiques, observer leur comportement dans l'éditeur et en jeu, puis affiner leur nom et leur sémantique sans extrapolation.

## v1.10 — Retour générateur

- [ ] **PRIORITÉ MAJEURE — audit seed et diversité morphologique Continental** : les miniatures Batch ont révélé que des seeds différentes peuvent produire des formes de carte visuellement identiques, parfois seulement réorientées. Ne pas conclure avant mesure.
- [ ] **Preuve visuelle R7 à conserver pour l'audit** : [`SETTLERS3_V1_10_SEED_DIVERSITY_EVIDENCE_20260822.png`](references/SETTLERS3_V1_10_SEED_DIVERSITY_EVIDENCE_20260822.png), lot Legacy Continental 768×768 4P avec les seeds `69122063`, `958607757`, `1446058262` et `2085415098`. Le symptôme visuel est confirmé : silhouettes côtières et grandes structures de terrain paraissent identiques ou quasi identiques après rotations/symétries. La cause reste volontairement indéterminée avant v1.10.
- [ ] **Étape 1 — intégrité des seeds/RNG** : vérifier que la seed complète pilote réellement toutes les étapes stochastiques pertinentes, qu'aucune réinitialisation, collision, réduction ou réutilisation involontaire ne limite l'espace des résultats, et distinguer clairement un résultat recalculé d'un résultat issu du cache.
- [ ] **Étape 2 — détection objective des doublons** : générer un corpus multi-seeds puis comparer les masques macro-géographiques avec des signatures exactes et des mesures de similarité, en canonisant séparément rotations/orientations et symétries afin de repérer les mêmes formes transformées.
- [ ] **Étape 3 — diversité réelle du générateur** : si les seeds fonctionnent correctement, mesurer combien de familles de formes réellement distinctes sont produites et déterminer si la calibration sur les cartes de référence a excessivement contraint la macro-morphologie.
- [ ] **Objectif central v1.10 si diversité insuffisante** : élargir fortement la variété des silhouettes, masses continentales, orientations et organisations macro-géographiques tout en conservant les règles validées, la jouabilité et les proportions natives. Éviter une simple collection de gabarits tournés ou symétrisés.
- [ ] Continental multi-tailles : 384 → 448 → 512 → 576 → 640 → 704 → 768.
- [ ] Utiliser le socle Stats/Graphs pour calibration et debug.
- [ ] Évaluer ensuite le début d’autres archétypes selon les résultats ; ne pas figer la roadmap post-v1.10 à l’avance.
- [ ] Ne pas réserver `v2.0` au simple multi-size : garder ce saut pour une évolution structurelle réellement majeure.

## Optimisations diverses — expérimentation après DEV_4 / cible possible v1.11

- [x] **DEV_4 PERF+ R1 validée sous Windows** : candidate séparée construite depuis DEV_4_R6, conservée après validation sans régression ni baisse de performances observable. Parité pixel, validations internes et interactions dynamiques confirmées ; R6 reste le checkpoint historique de repli.
- [x] **Pilote local dans DEV_4_R5** : Batch conserve une base raster sans marqueurs et compose uniquement les sprites `Masqués / Petits / Normaux`; l'égalité pixel par pixel avec le rendu direct est couverte en Carrée et Parallélogramme. Ne pas considérer ce succès local comme validation automatique de la généralisation PERF+.
- [x] Invalidations raster inutiles supprimées pour langue, thème et projection dans PERF+ R1, validée sous Windows.
- [x] Cache de rendu borné et sélectif validé : calque carré de la vue courante et ses composites, plus une base carrée et une projetée par résultat Batch. Mesure brute maximale pour quatre résultats Batch : environ 60,7 Mio hors copies Tk et miniatures.
- [x] Carrée/Parallélogramme : projection dérivée de la carte carrée déjà colorisée et deux variantes réutilisées une fois créées.
- [x] Écritures rapides : sauvegardes JSON des sliders Opacité et Zoom molette différées de 200 ms, avec flush à la fermeture ; autres réglages discrets immédiats.
- [ ] Ne tester le calcul raster en arrière-plan que si les optimisations simples restent insuffisantes ; Tkinter et la création des images d'interface doivent rester sur le thread principal.
- [x] Mesures PERF+ R1 sur la référence 768×768 : projection mise en cache ~7,6× plus rapide ; recomposition d'opacité Départs ~24× plus rapide ; parité pixel exacte dans les deux projections. Test Windows validé sans régression ni croissance problématique observée.
- [ ] Si un fine tuning important est nécessaire, reporter l'ensemble vers une passe dédiée autour de v1.11, notamment avant ou avec les Vues cumulables et interactions Graphiques → carte.
- [ ] **Diagnostic mémoire — cible possible v1.11** : proposer un panneau de debug avec total estimé et barre empilée par familles (données de carte, statistiques, rendus/projections, miniatures Batch, objets d’interface). Afficher séparément les mesures factuelles — notamment buffers NumPy/Pillow — et les estimations Python/Tk, avec libellés explicites, méthode documentée et déduplication par identité pour ne pas compter plusieurs fois une même carte référencée par l’historique, la vue courante et A/B.

## v1.8 / workflow de génération — plan Batch historique désormais réalisé

- [x] **Génération par lot / Batch Generation** : fenêtre dédiée avec les paramètres ordinaires de génération, validée en DEV_3.
- [x] Première version limitée à **4 maps simultanées** ; architecture extensible jusqu’à 8 seulement après mesure du coût réel RAM/temps/cache.
- [x] Chaque map du lot possède un état visuel compact et ses propres paramètres.
- [x] Affectation directe d’un résultat du Batch au slot **Comparaison A** ou **Comparaison B**.
- [x] Pipeline de génération existant réutilisé sans moteur Batch divergent.
- [ ] **Comparaison multi-maps 3+ : fonctionnalité planifiée à très forte probabilité**, distincte de l’A/B actuelle. Permettre de scinder le viewer en 2, 3 ou 4 zones, chacune compatible avec le système de Vues existant. La repousser après une grosse passe sur le générateur afin qu’elle serve ensuite de banc d’analyse rapide pour les évolutions profondes.
- [ ] Prévoir la multi-comparaison comme outil particulièrement utile pour comparer plusieurs variantes d’un même seed, plusieurs tailles/configurations, et plus tard plusieurs combinaisons de **Modifiers**.
- [ ] **Modifiers / Modificateurs** : fonctionnalité future conservée explicitement dans la roadmap. Objectif : appliquer volontairement des modifications fortes/amusement aux règles ou proportions de génération (ex. eau, montagnes, ressources, végétation, etc.) sans transformer chaque variante en nouvel archétype. Les paramètres exacts et garde-fous seront définis lors du chantier dédié.

## Calibration multi-tailles — après UI + Stats

Continental, une taille à la fois :

- [ ] 384×384
- [ ] 448×448
- [ ] 512×512
- [ ] 576×576
- [ ] 640×640
- [ ] 704×704
- [ ] reconfirmation 768×768

Pour chaque taille : starts, morphologie, montagnes/neige, minerais, arbres, Building Stones, poissons, marais, désert, décorations, récifs, rivières/lacs, quotas et stabilité éditeur/View Map/in-game.

Le premier exécutable Windows est remonté dans v1.8. Le numéro `v2.0` reste réservé à une future évolution structurelle majeure et n’est pas automatiquement lié à la fin du multi-size Continental.

## Après Continental

- [ ] **Large Islands / Grandes îles**.
- [ ] Constituer/analyser les références natives nécessaires.
- [ ] **Small Islands / Petites îles** ensuite.

## Futur génération — moteur alternatif expérimental (non versionné)

- [ ] Conserver l'idée d'une famille de génération réellement différente de Legacy et Upgraded, pouvant explorer des algorithmes de formes plus variés ou s'inspirer de principes rencontrés dans d'autres jeux, sans copier leurs assets ni compromettre les modes validés.
- [ ] Ne pas confondre ce chantier avec un simple **Archetype** (macro-géographie comme Continental/Large Islands/Small Islands), ni avec un **Modifier**. Décider seulement lors de la conception s'il mérite un nouveau Mode, un moteur expérimental isolé ou une autre architecture.
- [ ] N'ouvrir cette piste qu'après l'audit/diversification v1.10 et la consolidation des objectifs natifs : Legacy et Upgraded doivent rester reproductibles, protégés et indépendants.

## ENDGAME — Éditeur de cartes avancé intégré (long terme, non versionné)

- [ ] Ne commencer ce chantier que lorsque le générateur/workbench actuel sera pratiquement finalisé, hors modifications mineures et éditeur intégré.
- [ ] Faire évoluer MapGen vers une chaîne complète permettant de générer, importer, inspecter, modifier, valider et exporter des cartes Settlers III.
- [ ] Dépasser progressivement les limites de l'éditeur officiel uniquement pour les données EDM/MAP/SAV réellement comprises, écrites correctement et validées dans l'éditeur ou en jeu.
- [ ] Décider tardivement l'architecture UI selon l'application alors mature : fenêtre d'édition dédiée ou espace/mode Édition remplaçant la vue principale.
- [ ] Ne pas préparer maintenant de placeholder, de refonte anticipée ou de numéro v2/v3/v4 ; ce but terminal ne doit pas ralentir la roadmap proche ou moyenne.

## À préserver

- Archetype = macro-géographie.
- Legacy/Upgraded = contenu, règles, balance, ressources et objets.
- Starts placés tôt et protégés.
- Upgraded conserve impérativement les minerais v7 no-gap.
- Aucun aperçu imaginaire.
- Toute image/preview = rendu déterministe réellement issu des données EDM/MAP/SAV.
- Ne jamais repartir d'une version invalidée du générateur.

### Agriculture / Amazones — futur
- [ ] Identifier dans des SAV joués les IDs et le fonctionnement des nids d'abeilles amazones avant tout support dans la vue Cultures/Agriculture. Ne rien supposer tant que le mapping runtime n'est pas confirmé.

## v1.6 — finalisation validée

- [x] Palette P1..P20 + contours noirs validés.
- [x] Palette Ressources minières validée.
- [x] Traductions FR/EN et thème clair/sombre validés pour le checkpoint v1.6.
- [x] Icônes raster Vue / Carte thermique et drapeaux langue validés.
- [x] Filtre Carte thermique : verrouillage, libellé, molette et hover validés.
- [x] Overlay de chargement centré dans la zone carte, responsive, détail technique dans la barre, validé en clair/sombre.
- [x] Nettoyage de release effectué avant figement STABLE.
- [ ] Later: dedicated Forests / Quarries view.
- [x] DEV_4_R4 validated on Windows: dedicated Starts view uses 210 non-overlapping minimal markers and adjustable opacity; Territories follows Starts and reconstructs exact initial regions for EDM/MAP while preserving real SAV runtime claims.
- [ ] Later: Amazon beehives only after IDs/runtime semantics are identified.
- [ ] Later: broader exact ID naming pass.

## UI — après validation v1.6 / refonte majeure
- Repenser complètement l'organisation générale de l'interface.
- Étudier une section **Outils Map** sous la zone Validations / Pipeline / Métadonnées / Statistiques afin d'y regrouper les outils d'analyse de carte.
- Ajouter une **loupe flottante près du curseur**, activable/désactivable par bouton discret et raccourci : zoom local carré de la zone survolée pour viser précisément les cellules/objets ; prévoir un curseur d’inspection plus fin que le curseur de drag.
- Ajouter un second toggle indépendant pour afficher les **informations de l’inspecteur près du curseur** (ou dans une petite zone contextuelle proche de la map après essai UX), sans imposer la loupe.
- Repenser à terme le contrôle de zoom : barre plus compacte ou autre forme de contrôle ; DEV_2_R2 le rapproche déjà du viewer pour cohérence.
- Le label texte d'un joueur peut sortir de la carte lorsqu'un départ est très proche de la côte droite. Ne pas investir dans un correctif isolé avant l'essai de la Vue Départs et des marqueurs natifs J1–J20, qui devraient remplacer ou rendre optionnels ces labels.
- Faire une passe complète de consolidation/nomenclature des tables d'IDs connues et les exposer proprement dans l'inspecteur.
- Envisager une vue dédiée Forêts / Carrières pour l'analyse des arbres et Building Stones.
- Étudier des **Vues composables** : permettre d'activer plusieurs couches compatibles au lieu d'une seule vue exclusive. `Global` / `Aucune` remettrait les autres couches à zéro. Définir avant implémentation les compatibilités, l'ordre de rendu, la légende et les conflits ; ne pas promettre que toutes les vues pourront être cumulées.
- Repenser complètement la liste Vue avec les Graphiques. Chaque graphique pertinent pourra proposer un bouton-poussoir **Pilotage de la vue** : activé, il impose/verrouille sa couche cartographique associée et remplace temporairement la sélection manuelle ; désactivé, il restitue l'état précédent. Brainstorm requis sur le nom final, la visibilité du mode piloté, le comportement lors d'un changement de graphique et son interaction avec les vues composables.


## Après DEV_5 — Stats / UI à poursuivre

- [x] Recalibrer les distances de ressources autour des starts : lecture gameplay 0–50 HEX + 50–100 HEX implémentée et validée.
- [x] Permettre d'ajouter aux slots A/B des cartes importées `.SAV`, `.EDM` et `.MAP` ; DEV_6 conserve explicitement leur sémantique d'import lors des bascules.
- [ ] Couleurs A/B personnalisables.
- [ ] Vue Hauteurs : remplacer à terme le simple dégradé blanc/gris par un rendu de type carte topographique / courbes ou classes d'altitude.
- [ ] Explorer très tard l'utilisation de vrais sprites du jeu dans certains labels, uniquement si extraction propre et légitime des ressources graphiques possible ; ne jamais inventer de pseudo-sprites.
- [ ] Agriculture : ajouter les nids d'abeilles uniquement après identification/calibration exacte.
- [ ] Continuer la nomenclature des IDs sans inventer les espèces/objets inconnus.


## DEV_7 — consolidation retours DEV_5 + DEV_6

- [x] Gradients quantitatifs rouge → jaune → vert pour pierres, distances et richesses locales.
- [x] Building Stones : 12 pierres vert, milieu jaune, épuisé rouge.
- [x] Ne jamais masquer silencieusement une valeur de segment > 0 : fallback de label extérieur relié au segment.
- [x] Ressources forestières : ordre Adultes → Palmiers → Pousses.
- [x] Hauteurs : labels courts plus descriptifs.
- [x] Raccourci configurable de bascule thème clair/sombre (`Ctrl+Shift+T`).
- [x] Distances adversaires : gradient 3 couleurs, adversaire le plus proche identifié, couleurs P joueur + P adversaire.
- [x] Arbres/Pierres/Poissons proches : 0–50 HEX + 50–100 HEX.
- [x] Stock minier proche : deux barres/joueur (≤50 ; 50–100), couleurs minerai conservées.
- [x] Massifs/lacs/rivières : plus grand = plus foncé.
- [x] A/B : couleurs sémantiques pour Terre, Stock pierre, Stock poisson.
- [x] Tooltips interactifs génériques sur les barres/segments des Graphiques — DEV_10.
- [ ] **Pilotage de la vue** optionnel/désactivable depuis un graphique ; exemples Agriculture→Cultures, familles de terrain→surbrillance du biome survolé, distances→vue relationnelle avec flèches. Concevoir avec la future composition des vues avant de coder.
- [x] **DEV_7_R1 → R3** : fondations successives de l’historique unifié, du thème sémantique, des protections et de l’aperçu ; candidates remplacées par R4 après retours Windows.
- [x] **DEV_7_R4 → R10 validée sous Windows** : ordre LRU stable lors des actions UI ; cadenas explicites `V/A/B` avec rôle `M` préparé ; états cercle/coche et libellés contextuels ; aperçu Historique aligné sur Batch avec remplacement atomique ; infobulle hors historique ; prévision exacte 4/8/12/16 ; confirmation de réduction protégée ; loupes translucides à cinq états ; cycle de vie Tk sécurisé ; parité réelle de zoom et anticollision des aperçus temporaires.
- [~] **DEV_10_R1 — verrouillage manuel de l’historique** : cadenas `M` réel et ordre visuel réorganisable, sans modifier automatiquement cet ordre lors des affectations Viewer/A/B ni lors d’un hit LRU. La liste commune V/A/B/M protège le vrai cache et alimente la prévision Batch ; verrous et ordre restent limités à la session. Validation Windows requise.
- [x] **DEV_7_R9 — crash après fermeture du Centre d’historique corrigé dans la candidate** : reproduction minimale couverte par régression. Les callbacks sont annulés avant destruction, toutes les références de preview sont invalidées, et les rafraîchissements vérifient fenêtre et widget avant configuration. Validation Windows requise.
- [x] **Loupes de miniatures — candidate R9** : cinq états déterministes couvrent repos, survol, source active, aperçu temporaire et fermeture. La croix n’apparaît que lorsqu’un clic ferme réellement un aperçu épinglé ; l’aperçu ouvert par pause souris possède un état distinct. Validation Windows requise.
- [ ] **Surveillance calcul Statistiques potentiellement bloqué** : incident unique non reproductible observé pendant la revue R4. Si récidive, relever fichier/carte, action précédente, vue/onglet actif, slots A/B et durée ; profiler seulement avec un cas reproductible.
- [x] Après DEV_7 : modèles GitHub Issues anglais, labels/conventions et milestones stables v1.8/v1.9/v1.10 mis en place. Le Wiki est volontairement reporté car prématuré.
- [ ] Historique futur : distinguer clairement ordre d’éviction LRU, ordre visuel manuel et verrouillage manuel. Étudier déplacement de lignes et cadenas `M` uniquement après définition des règles de persistance et d’éviction.
- [ ] Revoir netteté/résolution des exports PNG graphes et vue map.

## DEV_8 — polish retours DEV_7

- [x] Corriger les raccourcis clavier avec `Shift` (`Ctrl+Shift+T`, `Ctrl+Shift+C`) sous Tk/Windows, y compris AZERTY.
- [x] Ajouter un bouton raster soleil/lune pour basculer le thème.
- [x] Placer Graphiques à côté de Statistiques, puis Paramètres à côté de Raccourcis.
- [x] Valeurs de graphes en blanc avec contour noir fin, hors libellés d’échelle.
- [x] Fallback des petits segments non nuls avec lignes de liaison + anti-chevauchement vertical.
- [x] Stock minier : note concise pour la partie sous neige + légende minerais propre.
- [x] Pierres : gradient explicite rouge → jaune → vert.
- [x] Distances adversaires : joueur compact en axe, adversaire + flèche dans le graphe.
- [x] Arbres/Pierres/Poissons proches : carré joueur + note 0–50 / 50–100.
- [x] Minage proche : deux barres regroupées sous un seul joueur + carré joueur.
- [x] Massifs/Lacs/Rivières : médailles légères top 3 sans recoloration du podium.
- [x] **DEV_8_R1 → R4 validée — Raccourcis v2** : capture directe fondée sur les événements réellement observés, désactivation/réinitialisation par action, conflits inline, changements non appliqués visibles, AZERTY/QWERTY, commandes supplémentaires, aide dynamique et défilement compact horizontal/vertical. Migration entrée par entrée du JSON existant vers le schéma 2, sans second format de configuration.
- [x] **DEV_8 clôturée sur R4 après validation Windows** : aucune dernière correction fonctionnelle nécessaire ; touches simples et vrais modificateurs Ctrl/Shift/Alt validés sans Alt fantôme.
- [x] **Nettoyage des notes DEV après DEV_8** : les 39 notes dispersées sont consolidées dans `references/dev_notes/V1_8_DEVELOPMENT_LOG.md`. Les futures candidates réutiliseront un unique `DEV_CANDIDATE_NOTES.md`, retiré après consolidation à la clôture de chaque DEV.
- [ ] Étendre progressivement la config utilisateur persistante aux autres réglages utiles sans complexifier le format inutilement. Le verrouillage/réordonnancement manuel de l’historique reste le candidat prioritaire à ne pas trop repousser, mais ne doit pas être greffé à R1 sans besoin observé.

## Pré-DEV_9 — mini-polish retours DEV_8 terminé

- [x] Labels extérieurs des petits segments toujours placés à gauche.
- [x] Stock minier proche : minerai sous famille Neige exclu des métriques locales.
- [x] Distance adversaire : ordre `→ couleur adversaire label adversaire`.
- [x] Podiums massifs/lacs/rivières : `# + médaille` pour les rangs 1–3.
- [x] Stats schema v5 pour refléter la nouvelle sémantique du minage local.

## DEV_9 — preuve d’exécutable Windows autonome clôturée

- [x] **DEV_9_R2** : distribution Windows x64 en dossier autonome avec `Settlers3MapGen.exe`, sans Python/pip chez l’utilisateur. R1 rejetée après échec au démarrage : `unittest` avait été exclu alors que SciPy l’importe via `numpy.testing` ; R2 démarre réellement sous Windows.
- [x] Résoudre les ressources par rapport au bundle PyInstaller, indépendamment du répertoire courant de lancement.
- [x] Conserver les préférences dans `%APPDATA%/Settlers3MapGen/settings.json` et placer le dossier d’export par défaut à côté de l’exécutable.
- [x] Embarquer profils, bibliothèque native, scaffolds EDM/MAP, référence Upgraded et sprites J1–J20 nécessaires au runtime.
- [x] Ajouter un autodiagnostic du véritable exécutable packagé avant création du ZIP, plus un rapport JSON et un SHA-256.
- [x] **R2** : faire importer à l’autodiagnostic toute la chaîne GUI normale, afin qu’une dépendance gelée manquante bloque automatiquement le build.
- [x] Automatiser le build Windows via GitHub Actions sans créer prématurément de tag ou de Release.
- [x] Préparer l’adoption facultative d’un `.ico` fourni manuellement ; conserver une icône neutre en son absence.
- [x] Valider la faisabilité sous Windows : extraction complète et premier lancement réel après autodiagnostic du runtime GUI.
- [x] Décision post-DEV_9 : développement quotidien via `launch_gui`; paquet Windows et updater entièrement reportés aux RC v1.8, sans installateur.

## DEV_10 — verrouillage et ordre manuel de l’historique

- [~] **R1 candidate source** : bouton contextuel Verrouiller/Déverrouiller, cadenas `M` explicite et protection réelle contre l’éviction.
- [~] Réorganisation par Monter/Descendre ; le rang `#` et le sélecteur principal suivent cet ordre visuel, indépendant de l’ordre LRU interne.
- [~] Nouvelles cartes en tête ; actions Afficher/A/B et hits cache ne réordonnent pas la liste manuelle.
- [~] Suppression/vidage libèrent aussi `M` après avertissement ; réduction de capacité refusée si elle devient inférieure aux protections uniques V/A/B/M.
- [~] FR/EN/DE/ES, thèmes et prévision Batch réutilisent les infrastructures existantes ; validation Windows requise.

## Post-v1.7 — découvrabilité / publication GitHub
- [ ] Renseigner/revoir la description **About** GitHub avec une formulation courte et explicite sur Settlers III MapGen.
- [ ] Ajouter des topics GitHub pertinents : `settlers-iii`, `settlers3`, `map-generator`, `procedural-generation`, `reverse-engineering`, `python`, puis uniquement les tags formats réellement utiles.
- [ ] Garder le README français comme base, mais ajouter une entrée anglaise claire (résumé haut de README ou `README_EN.md` lié explicitement).
- [ ] Faire apparaître naturellement les termes utiles à la recherche : `Settlers III map generator`, `Settlers 3 procedural map generator`, `Siedler III Kartengenerator`, `.EDM`, `.MAP`, `.SAV` — sans bourrage de mots-clés.
- [ ] Ajouter au README plusieurs captures réelles et récentes du programme (génération, analyse/Stats, Graphiques et Batch), en évitant les builds périmées et toute image illustrative inventée.
- [ ] Continuer les versions **STABLE** sous forme de vraies GitHub Releases avec tag + ZIP + release notes ; DEV/RC restent hors Releases.
- [ ] Éventuel partage communauté Settlers III (Discord/wiki/sites de maps) uniquement plus tard et volontairement ; ce n'est pas une obligation du workflow.
