# Settlers III MapGen — TODO programme

## État de validation

- [x] **v1.5 VALIDÉE / STABLE** pour Continental 768×768.
- [x] Référence finale : `S3_V1_5_V7NOGAP_CORRECTED_UPGRADED_4P_768x768_seed_2026082202`.
- [x] Starts / éditeur / View Map / in-game / aucun crash.
- [x] Minerais Upgraded géométrie **v7 no-gap** verrouillée.
- [x] Legacy / Upgraded séparés.
- [x] Building Stones 115..127 et ID127 constructible gérés.
- [x] Bonus de départ Upgraded validés.
- [x] **v1.6 STABLE UI/outillage** : validation utilisateur terminée (RC_9 validée).

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
- [ ] densités par 1000 cellules de land ;
- [x] ratios land/ocean, biomes, eau intérieure, forêts, ressources — socle ;
- [~] blobs / massifs / lacs / rivières / clusters : moteur de composantes avancé DEV_4, analyses/distributions à enrichir ;
- [x] distances inter-starts + voisin le plus proche ;
- [x] percentiles utiles — relief, quantités minières et distances ;
- [x] suivi Terrain24 / Terrain22 / Terrain28 via les comptes Terrain ID ;
- [ ] autres métriques et graphes pertinents tant que lisibles/exploitables.

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

Après validation du cycle Continental : préparer **v2.0** avec premier exécutable Windows portable et build reproductible, avant de démarrer les nouveaux archétypes.

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

- [ ] Recalibrer les distances de ressources autour des starts : conserver les rayons DEV_4 comme exploration mais étudier une lecture gameplay autour de ~50/60 HEX (claim rapide probable) et ~100 HEX (sécurité stratégique, notamment minerais).
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
- [ ] Tooltips interactifs détaillés sur les barres/segments (architecture généralisable à tous les graphes).
- [ ] Synchronisation **optionnelle/désactivable** graphe ↔ vue map ; exemple Agriculture→Cultures, distances→vue relationnelle avec flèches.
- [ ] Ajouter les maps importées à l'historique session et rendre la taille de l'historique configurable (base actuelle 8).
- [ ] Revoir netteté/résolution des exports PNG graphes et vue map.
