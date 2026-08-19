# Settlers III MapGen — TODO programme

## État de validation
- [x] **v1.3.2 validée** sur 4 générations Continental 768×768 : Legacy 4P / 20P et Upgraded 4P / 20P.
- [x] Starts acceptés par l'éditeur sur ces 4 contrôles.
- [x] Aucun crash en View Map / vue in-game sur ces 4 contrôles.
- [x] Marais : correction visuelle confirmée.
- [x] Neige intérieure : non traversable comme prévu.
- [x] **v1.4 validée** : visualisation, thème sombre, combobox, sliders, projection parallélogramme, labels joueurs et territoire initial.
- [x] **Goods Default corrigé et validé** : `Legacy=Medium`, `Upgraded=High`.
- [x] **Première morphologie Upgraded indépendante validée** : seed `2026081908`, starts OK, aucun crash, relief natif conservé.
- [x] **v1.5 VALIDÉE / STABLE** pour le périmètre Continental 768 calibré : moteur Legacy/Upgraded audité, clusters de départ, Building Stones corrigées, géométrie minière v7 no-gap restaurée et contrôles éditeur/View Map/in-game PASS.

## Ordre de travail après v1.5
1. **Finir tous les TODO UI / outillage** avant de reprendre la génération.
2. **Grosse passe Statistiques** : enrichir fortement l'onglet avec beaucoup de métriques, ventilations et graphes utiles à l'analyse des maps.
3. **Calibration multi-tailles** : valider progressivement 384, 448, 512, 576, 640 et 704, puis confirmer les scalings généraux.
4. **Commencer l'archétype Large Islands / Grandes îles** une fois Continental multi-tailles suffisamment solide.
5. Ensuite : modificateurs, Terrain24 Upgraded, autres archétypes, Custom et reverse-engineering restant selon priorité.

## Génération v1.5
- [x] Macro-géographie découplée du mode via `ArchetypeMorphologyLibrary`.
- [x] Terrain34 requalifié : variante Rocky rare, singleton entouré de Rocky32, minéralisable ; jamais anneau Snow.
- [x] Chaîne Snow commune validée : `Rocky32 -> 35 (1 cellule) -> 129 (1 cellule) -> Snow128`.
- [x] **Audit Legacy / Upgraded terminé conceptuellement**. Référence : `references/SETTLERS3_LEGACY_UPGRADED_AUDIT_20260819.md`.
- [x] **Séparation Legacy / Upgraded implémentée** dans `s3mapgen/generator.py` + profils 768 ; tests de verrouillage dans `tests/test_legacy_upgraded_audit.py`.
- [x] **Minerais Upgraded — géométrie v7 no-gap canonique revalidée visuellement** : nombreux petits blobs élémentaires pleins/compacts/légèrement ovoïdes, tailles lognormales ~18–105 cellules, légère variation d'aspect/orientation, pas de trous internes, pas de singleton, pas de moat forcé, blobs pouvant toucher/fusionner naturellement. Le moteur v1.5 utilise désormais explicitement cette géométrie canonique dans `generator_v15.py` ; l'ancienne croissance de frontière aléatoire est interdite pour Upgraded.
- [x] Minerais Upgraded : cible ~90 % du support minier, ratios natifs empiriques, +30 % quantité/case cap15, minerai sous Snow + Terrain34 valide.
- [x] Hydrologie : Legacy conserve étangs/rivières natifs ; Upgraded supprime/redistribue 1–4 cellules et applique un p99 river size-scaled `~0.0245*side + 34.7`.
- [x] Arbres : pool `68..77 + 80..81` dans les deux. Legacy volume natif ; Upgraded ~130 % + SmallTree84 séparé. Palms `78..79` comptés dans le bois.
- [x] Building Stones : footprint 7 cellules bloquant pour les états actifs `115..126`; Legacy stock/densité natifs, Upgraded stock amélioré + clusters/dispersé.
- [x] **États Building Stones variés** : Legacy distribution native-like ; Upgraded distribution variée mais biaisée vers les pierres plus pleines, avec ajustement fin pour atteindre exactement le stock cible. **Répartition visuelle `115..127` validée par l'utilisateur sur le contrôle v1.5.**
- [x] **Building Stone 13 / ID127 vide généré** : comportement natif confirmé. Référence 768 = 18/22/21 ancres vides, cible pratique **20 ancres globales sur 1683**. Elles comptent dans la densité/placement, apportent **0 unité**, sont exclues du stock exploitable et ne sont jamais utilisées dans les clusters bonus de start.
- [x] **ID127 constructible** : contrairement aux états actifs, le tas épuisé ne bloque plus la construction ; son ancien footprint 7 cellules est remis en `accessibility=0` avant validation/export.
- [x] Décorations : reefs Legacy=0 / Upgraded rares ; Reeds natifs communs ; pierres déco native Legacy / ~÷10 Upgraded ; petites végétations, Wrecks, Grave, Stumps communs natifs.
- [x] **Récifs Upgraded protégés des bords** : marge minimale de **2 cellules** par rapport aux quatre limites de map. Les récifs éventuellement placés trop près du bord sont relocalisés en eau profonde valide sans changer leur nombre/ID ; validator `REEF_EDGE_MARGIN`.
- [x] Désert : Dead Trees `43..44`, Cacti `45..48`, Skeleton `49`, Palms `78..79`, comportement commun natif.
- [x] Biomes : Mud natif Legacy / désactivé Upgraded ; Swamp natif Legacy / ~+30 % global Upgraded ; mini-marais start Upgraded uniquement. L'expansion Swamp Upgraded refuse tout nouveau contact HEX6 incompatible.
- [x] Terrain24 : conservé en Legacy ; retiré temporairement d'Upgraded pendant cette grosse passe. **Ajout Upgraded confirmé mais différé à une modification isolée.**
- [x] Starts : placement précoce commun et protection conservée ; bonus mini-marais/forêt/pierre Upgraded seulement.
- [x] **Bonus de départ Upgraded validés visuellement** : vrais clusters centrés sur la **bordure du territoire initial (~rayon HEX34)** afin que la bordure traverse le cluster. Forêt bonus ≈ cluster global moyen : **41 adultes + 21 SmallTree84/joueur**. Tas de Building Stones bonus ≈ cluster global moyen : **8 ancres/joueur**, bien remplies mais variées, **84 unités/joueur** au total (9..12 unités/ancre). Mini-marais inchangé.
- [x] GUI/CLI préparés en **v1.5** (`gui_v15.py`, runtime final `generator_v15.py`, exports `MapGenV1_5`).
- [x] Contrôle objets v1.5 : checksums EDM/MAP valides ; quotas arbres/SmallTree84/Stones exacts ; 20 ID127 ; 13 états 115..127 présents ; aucun footprint ID127 bloquant ; clusters bonus sur bordure validés.
- [x] **Contrôle ressources corrigé `S3_V1_5_V7NOGAP_CORRECTED_UPGRADED_4P_768x768_seed_2026082202` validé visuellement par l'utilisateur** : formes de minerais = exactement le style recherché/long-play v7. L'ancien candidat `seed_2026082201` à croissance BFS/aléatoire est invalidé et ne doit jamais servir de référence.
- [x] **Contrôle final v1.5** : ouverture éditeur OK, starts OK, View Map/in-game OK, aucun crash signalé.
- [ ] Micro-map de régression facultative : confirmer explicitement côté éditeur/in-game qu'un ID127 permet bien de construire sur l'ancien footprint. Non bloquant pour v1.5.
- [ ] Tester visuellement le nouveau volume d'arbres Upgraded sur plusieurs seeds ; si trop forestier, utiliser le futur modificateur de densité sans réduire le pool d'IDs.
- [ ] Ajouter Terrain24 à Upgraded dans une passe isolée/testable.
- [ ] Valider les scalings multi-tailles : arbres, stones, décorations, Swamp, reefs, désert, rivières.
- [ ] Reprendre ensuite le compositeur de formes natives / native stamps et produire plusieurs seeds 768 distinctes.

## UX / outillage — priorité immédiate
- [x] Barre progression, seed aléatoire, import EDM/MAP/SAV, export EDM+MAP 768.
- [~] Export SAV non validé ; copie inchangée d'un SAV importé seulement.
- [x] Vues global / heightmap / ressources / territoires.
- [x] Vue **Chemins / zones creusées** Terrain28 ; Terrain28 runtime désormais préservé lors de l'import SAV au lieu d'être normalisé en Grass.
- [x] Vue **Cultures** blé/vigne/riz avec familles visuellement distinctes.
- [x] **Nouvelle vue Heatmap**, paramétrable par ressource, basée sur une densité locale déterministe et pondérée par stock réel lorsque disponible : arbres, Building Stones, poissons, Coal, Iron, Gold, Gemstones, Sulfur.
- [x] **Internationalisation UI Français / Anglais** : langue persistée dans les préférences ; principaux contrôles/vues/messages utilisateur traduits, contenus techniques autorisés à rester en anglais.
- [x] **Inspecteur de cellule au survol de la souris** : coordonnées réelles x/y, Terrain ID, Object ID, ressource + quantité, hauteur, accessibilité et claim/joueur. Fonctionne avec zoom/drag et projections Carrée/Parallélogramme ; enrichissement/design ajustables après usage réel.
- [ ] Palette exacte des couleurs joueurs.
- [ ] Contour de zone de départ d'origine sur import SAV.
- [x] Zoom/molette/drag/projection parallélogramme/labels/sliders/thème sombre.
- [x] Tailles natives visibles 384..768 et max joueurs adaptés.
- [~] Génération multi-tailles : UI prête, calibration moteur à compléter.
- [x] **Cache transparent des résultats de génération, mémoire de session uniquement** : objectif principal = relancer exactement les mêmes paramètres sans temps de génération. LRU limité initialement à 8 générations, jamais écrit sur disque, détruit à la fermeture.
  - [x] Clé : seed + taille + joueurs + mode + archétype + champ modificateurs + révision moteur.
  - [x] Un nouveau clic sur **Générer** avec une clé déjà présente produit un **cache hit immédiat** et réutilise le résultat complet sans recalcul.
  - [x] Conservation du `GenerationOutput` complet : map, validations, pipeline et métadonnées.
  - [x] Limite mémoire + bouton de vidage manuel.
  - [x] Le cache reste transparent : l'historique et la comparaison sont des outils optionnels ajoutés au-dessus, pas une étape obligatoire du workflow.
- [x] **Historique de session** : historique visible + recharge instantanée d'une génération déjà calculée.
- [x] **Comparaison A/B légère** : sélectionner deux entrées du cache comme A et B, puis basculer instantanément A↔B en conservant vue, zoom, cadrage, projection, overlay et Heatmap ; `Ctrl+B` par défaut pour basculer.
- [ ] **Comparaison A/B avancée éventuelle** : seulement si l'usage réel le justifie, ajouter côte-à-côte, diff visuelle par catégories (terrain/objets/ressources/hauteur/starts), synchronisation explicite des caméras et raccourcis de sélection A/B.
- [x] Bouton **Recentrer** : revient au zoom 100 % et recentre la carte.
- [x] Action rapide **Copier seed** de la génération courante.
- [x] **Raccourcis clavier configurables** : commandes Générer/Importer/Exporter/Recentrer/Copier seed/Basculer A-B/Aide, section dédiée, persistance dans les préférences, détection des doublons et restauration des valeurs par défaut.
- [x] **Aide dynamique** : F1/par commande affiche les raccourcis actuellement configurés, les commandes souris et le fonctionnement du cache.
- [ ] Étendre éventuellement les commandes rebindables après retour d'usage : changer de vue, sélectionner A/B, etc.

## Statistiques — grosse passe après l'UI
Objectif : faire de cet onglet un vrai outil d'analyse détaillée des cartes, pas seulement un résumé. Ajouter autant de statistiques utiles que nécessaire tant qu'elles restent lisibles et exploitables.

- [ ] **Détail exact du nombre de cellules pour chaque tile/ID de terrain.**
- [ ] **Quantité de chaque objet-ressource.**
- [ ] **Building Stones : afficher aussi la quantité totale de pierre attendue/exploitable.**
- [ ] **Graphe de distribution des différents états/types de Building Stones.**
- [ ] **Graphe des ressources de montagne**, par famille, affichant quantité de cases et pourcentage du stock réel total de ressources.
- [ ] Ajouter progressivement d'autres métriques utiles : densités par 1000 cellules de land, ratios land/ocean, biomes, eau intérieure, forêts, ressources, objets décoratifs, starts et distances pertinentes.
- [ ] Ajouter des répartitions / percentiles utiles quand cela apporte une information réelle (tailles de blobs, tailles de massifs, lacs, rivières, clusters, distances aux starts, etc.).
- [ ] Prévoir des graphes complémentaires lorsque la donnée est réellement mieux comprise visuellement qu'en tableau.
- [ ] Garder les IDs terrain non résolus séparés.
- [ ] Suivre Terrain24 et terrains runtime 22/28.
- [ ] Édition directe de map — pas maintenant.

## Calibration multi-tailles — après UI + Stats
- [ ] Valider Continental 384×384.
- [ ] Valider Continental 448×448.
- [ ] Valider Continental 512×512.
- [ ] Valider Continental 576×576.
- [ ] Valider Continental 640×640.
- [ ] Valider Continental 704×704.
- [ ] Reconfirmer 768×768 après généralisation des scalings.
- [ ] Pour chaque taille : starts, morphologie, montagnes/neige, minerais, arbres, Building Stones, poissons, marais, désert, décorations, récifs, rivières, lacs, quotas et stabilité éditeur/View Map/in-game.

## Archétypes — après Continental multi-tailles
- [ ] **Large Islands / Grandes îles** : commencer le développement comme prochain archétype majeur.
- [ ] Définir le contrat macro-géographique Large Islands sans dupliquer les règles Legacy/Upgraded downstream.
- [ ] Constituer/analyser les références natives nécessaires avant calibration.
- [ ] **Small Islands / Petites îles** : après stabilisation Large Islands.

## Modificateurs futurs — orthogonaux aux modes
- [ ] Système de modificateurs combinables avec Legacy/Upgraded, pas de quatrième générateur Barebone.
- [ ] **Barebone** : retire seulement le cosmétique sans fonction gameplay.
- [ ] **Densité de forêt** configurable.
- [ ] Idée : **cultures présentes au démarrage** (blé/vigne/riz), à étudier avec le decay runtime.
- [ ] Variante possible : **montagnes plus réalistes** comme modificateur explicite.
- [ ] **Réaliste** : distribution écologique plus crédible sans changer la macro-géographie. Pistes : arbres/plantes favorisés près de l'eau, champignons favorisés près des marais/sols humides, végétation modulée par biome/relief/humidité, avec priorité à la constructibilité, aux ressources et au gameplay. À développer comme modificateur orthogonal.

## Reverse engineering terrain/runtime
- [x] Terrain24 = herbe jaune/sèche, blend uniquement Grass16, native.
- [x] Terrain22 = terrain agricole runtime.
- [x] Terrain28 = sol runtime travaillé/usé, bâtiments + chemins.
- [~] Terrain18/19/23 encore non résolus.
- [x] Terrain34 = détail Rocky rare/minéralisable, entièrement entouré de 32 dans les références contrôlées.
- [x] `85..93` blé (`92` récoltable, `93` chaume).
- [x] `94..102` vigne/raisin.
- [x] `103..110` riz.
- [~] `82/83` techniques/invisibles, différés.

## Idées volontairement non actives / à clarifier plus tard
- Génération Upgraded : aucune nouvelle idée supplémentaire pour le moment.
- Engine de formes totalement différentes de Legacy/Upgraded : idée encore trop floue, ne pas engager de travail dessus pour l'instant.

## À préserver
- [x] Archetype = macro-forme uniquement.
- [x] Mode = contenu/règles/balance/objets/ressources.
- [x] Starts générés très tôt et protégés.
- [x] Legacy / Upgraded séparés selon l'audit canonique.
- [ ] Custom reste à définir proprement.
- [x] Aucun aperçu imaginaire ; seulement rendu déterministe depuis EDM/MAP/SAV.
