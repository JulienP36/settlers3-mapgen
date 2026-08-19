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

## UX / outillage
- [x] Barre progression, seed aléatoire, import EDM/MAP/SAV, export EDM+MAP 768.
- [~] Export SAV non validé ; copie inchangée d'un SAV importé seulement.
- [x] Vues global / heightmap / ressources / territoires.
- [ ] Vue **Chemins / zones creusées** Terrain28.
- [ ] Vue **Cultures** blé/vigne/riz.
- [ ] **Nouvelle vue Heatmap**, paramétrable par ressource, pour visualiser les zones de meilleure concentration :
  - [ ] arbres ;
  - [ ] Building Stones ;
  - [ ] poissons ;
  - [ ] Coal ;
  - [ ] Iron ;
  - [ ] Gold ;
  - [ ] Gemstones ;
  - [ ] Sulfur.
- [ ] **Internationalisation UI Français / Anglais** : permettre de changer la langue. Traduire les titres/labels utilisateur ; les contenus techniques des sections Debug/Validations/Pipeline/Métadonnées peuvent rester en anglais.
- [ ] Palette exacte des couleurs joueurs.
- [ ] Contour de zone de départ d'origine sur import SAV.
- [x] Zoom/molette/drag/projection parallélogramme/labels/sliders/thème sombre.
- [x] Tailles natives visibles 384..768 et max joueurs adaptés.
- [~] Génération multi-tailles : UI prête, calibration moteur à compléter.

### Statistiques
- [ ] **Détail exact du nombre de cellules pour chaque tile/ID de terrain.**
- [ ] **Quantité de chaque objet-ressource.**
- [ ] **Building Stones : afficher aussi la quantité totale de pierre attendue/exploitable.**
- [ ] **Graphe de distribution des différents états/types de Building Stones.**
- [ ] **Graphe des ressources de montagne**, par famille, affichant :
  - [ ] quantité de cases ;
  - [ ] pourcentage du stock réel total de ressources.
- [ ] Garder les IDs terrain non résolus séparés.
- [ ] Suivre Terrain24 et terrains runtime 22/28.
- [ ] Graphiques utiles supplémentaires plus tard.
- [ ] Édition directe de map — pas maintenant.

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
