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
- [ ] Futur proche traduction : ajouter **allemand (DE)** et **espagnol (ES)** à l'interface ; inclure explicitement l'onglet Statistiques dans toutes les langues utilisateur.
- [x] v1.8 DEV_1 : traduire intégralement le **titre de la fenêtre**, y compris le libellé du moteur.
- [ ] v1.8 : refondre l'export map avec un popup unique : nom de base commun + cases `.EDM`, `.MAP`, `.SAV`, et option PNG de la vue de base ; conserver l'export PNG de la vue courante avec overlays séparément.
- [ ] v1.8/futur Graphiques : étudier un bouton **Exporter…** unique ouvrant un popup multi-format, pouvant remplacer les boutons d'export séparés si l'UX est meilleure.
- [ ] Futur proche : rendre configurables les **2 rayons** utilisés par Arbres/Pierres/Poissons/Stock minier proches (rester à deux intervalles ; pas de troisième rayon dans l'UI actuelle).
- [ ] Futur Graphiques : proposer éventuellement plusieurs représentations d'une même métrique (ex. barres / donut) via un sélecteur, plutôt lors d'une grosse évolution Stats/Graphs.
- [ ] Futur Graphiques : histogrammes de distribution des tailles de massifs/lacs/rivières.
- [ ] Futur Graphiques : profil radial/cumulatif des ressources autour d'un start.
- [ ] Idée expérimentale/non garantie : radar léger de richesse par joueur uniquement si une représentation non trompeuse apporte une vraie valeur.
- [ ] Futur comparaison corpus : boxplots / bandes de référence pour situer MapGen dans les distributions natives lorsque ce chantier de calibration sera ouvert.
- [ ] Très lointain/incertain : détails géométriques supplémentaires dans les tooltips massifs/lacs/rivières (périmètre, bbox, compacité, allongement) seulement si l'usage le justifie.

## v1.8 — Workflow, accessibilité & production (13 axes validés)

- [ ] **Batch Generation** : 1 à 4 maps, paramètres indépendants, états visuels, historique + assignation A/B ; réutiliser le pipeline existant.
- [ ] **Export maps multi-format** : popup, nom de base unique, cases EDM/MAP/SAV + option PNG de base ; conserver PNG vue courante séparé.
- [ ] **Export Graphiques unifié** : étudier un bouton `Exporter…` multi-format (PNG/CSV/JSON selon contexte).
- [x] **A/B polish léger — DEV_1** : reset A/B/A+B, suppression du résumé texte redondant, boutons LED conservés.
- [x] **Titre de fenêtre entièrement i18n — DEV_1** : FR/EN.
- [ ] **Langues programme** : allemand (DE) + espagnol (ES) ; communication externe reste surtout EN/FR, DE ponctuel possible.
- [ ] **Raccourcis v2** : capture/sélecteur de touches, plus d’actions, AZERTY/QWERTY, conflits/reset, JSON existant.
- [ ] **Historique session amélioré** : imports + batch dans l’historique, taille configurable, assignation A/B facile.
- [ ] **Premier vrai `.exe`** : packaging autonome sans Python/pip à installer.
- [ ] **Icône application/exe** : infrastructure + placeholder simple ; icône finale dessinée manuellement en pixel art par l’utilisateur. Aucune image IA.
- [ ] **Updater v2 pour executable** : version installée/dernière STABLE, SHA, settings préservés, remplacement/rollback propre.
- [ ] **README transparence IA** : indiquer clairement conception/direction humaine + usage important de ChatGPT/OpenAI, notamment backend/analyse/reverse-engineering.
- [ ] **Découvrabilité GitHub** : About/Topics, entrée anglaise claire, FR conservé, termes Settlers III/Settlers 3/Siedler III + EDM/MAP/SAV naturels, sans spam SEO.

## v1.9 — Archéologie / Data Mapping (transition planifiée)

- [ ] Déterminer les bornes réelles des Terrain IDs et Object IDs ; `0–255` n’est qu’une grille technique 8-bit, pas une borne validée.
- [ ] Compléter progressivement les registres `references/SETTLERS3_TERRAIN_IDS_REFERENCE.md` et `references/SETTLERS3_OBJECT_IDS_REFERENCE.md`.
- [ ] Clarifier trous/réservés, familles/transitions et autres catégories SAV : settlers/colons, marchandises, outils, ressources transformées, bâtiments, etc., sans inventer.
- [ ] Consolider les tables utilisées par Stats/Tooltips avant les modifications profondes du générateur.

## v1.10 — Retour générateur

- [ ] Continental multi-tailles : 384 → 448 → 512 → 576 → 640 → 704 → 768.
- [ ] Utiliser le socle Stats/Graphs pour calibration et debug.
- [ ] Évaluer ensuite le début d’autres archétypes selon les résultats ; ne pas figer la roadmap post-v1.10 à l’avance.
- [ ] Ne pas réserver `v2.0` au simple multi-size : garder ce saut pour une évolution structurelle réellement majeure.

## v1.8 / workflow de génération — planifié après v1.7

- [ ] **Génération par lot / Batch Generation** : fenêtre dédiée pour préparer et lancer plusieurs maps avec les mêmes paramètres disponibles qu’une génération unitaire (mode, archétype, taille, joueurs, seed, etc.).
- [ ] Première version limitée à **4 maps simultanées** ; architecture extensible jusqu’à 8 seulement après mesure du coût réel RAM/temps/cache.
- [ ] Chaque map du lot possède un état visuel compact (attente / génération / terminée / erreur) et ses propres paramètres.
- [ ] Permettre d’affecter directement un résultat du batch au slot **Comparaison A** ou **Comparaison B**.
- [ ] Réutiliser le pipeline de génération existant ; ne pas créer un second moteur divergent.
- [ ] **Comparaison multi-maps 3+ : fonctionnalité planifiée à très forte probabilité**, distincte de l’A/B actuelle. La repousser après une grosse passe sur le générateur afin qu’elle serve ensuite de banc d’analyse rapide pour les évolutions profondes.
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
- [ ] Later: move original SAV initial-territory outlines to a dedicated view if desired.
- [ ] Later: Amazon beehives only after IDs/runtime semantics are identified.
- [ ] Later: broader exact ID naming pass.

## UI — après validation v1.6 / refonte majeure
- Repenser complètement l'organisation générale de l'interface.
- Étudier une section **Outils Map** sous la zone Validations / Pipeline / Métadonnées / Statistiques afin d'y regrouper les outils d'analyse de carte.
- Ajouter une **loupe flottante près du curseur**, activable/désactivable par bouton et raccourci : zoom local de la zone survolée pour viser précisément les cellules/objets avec l'inspecteur.
- Faire une passe dédiée sur la police des labels joueurs P 1..P 20 avec propositions visuelles comparatives avant choix définitif.
- Faire une passe complète de consolidation/nomenclature des tables d'IDs connues et les exposer proprement dans l'inspecteur.
- À terme, envisager de sortir starts/territoires initiaux de la vue Global vers une vue dédiée afin d'épurer la carte globale.
- Envisager une vue dédiée Forêts / Carrières pour l'analyse des arbres et Building Stones.


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
- [ ] Synchronisation **optionnelle/désactivable** graphe ↔ vue map ; exemple Agriculture→Cultures, distances→vue relationnelle avec flèches.
- [ ] Ajouter les maps importées à l'historique session et rendre la taille de l'historique configurable (base actuelle 8).
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
- [ ] Passe dédiée Raccourcis plus tard : sélecteur/capture de touches, davantage de commandes, defaults repensés et config utilisateur étendue (JSON privilégié).
- [ ] Étendre progressivement la config utilisateur persistante aux autres réglages utiles (historique, options UI, etc.) sans complexifier le format inutilement.

## DEV_9 — mini-polish retours DEV_8

- [x] Labels extérieurs des petits segments toujours placés à gauche.
- [x] Stock minier proche : minerai sous famille Neige exclu des métriques locales.
- [x] Distance adversaire : ordre `→ couleur adversaire label adversaire`.
- [x] Podiums massifs/lacs/rivières : `# + médaille` pour les rangs 1–3.
- [x] Stats schema v5 pour refléter la nouvelle sémantique du minage local.

## Post-v1.7 — découvrabilité / publication GitHub
- [ ] Renseigner/revoir la description **About** GitHub avec une formulation courte et explicite sur Settlers III MapGen.
- [ ] Ajouter des topics GitHub pertinents : `settlers-iii`, `settlers3`, `map-generator`, `procedural-generation`, `reverse-engineering`, `python`, puis uniquement les tags formats réellement utiles.
- [ ] Garder le README français comme base, mais ajouter une entrée anglaise claire (résumé haut de README ou `README_EN.md` lié explicitement).
- [ ] Faire apparaître naturellement les termes utiles à la recherche : `Settlers III map generator`, `Settlers 3 procedural map generator`, `Siedler III Kartengenerator`, `.EDM`, `.MAP`, `.SAV` — sans bourrage de mots-clés.
- [ ] Continuer les versions **STABLE** sous forme de vraies GitHub Releases avec tag + ZIP + release notes ; DEV/RC restent hors Releases.
- [ ] Éventuel partage communauté Settlers III (Discord/wiki/sites de maps) uniquement plus tard et volontairement ; ce n'est pas une obligation du workflow.
