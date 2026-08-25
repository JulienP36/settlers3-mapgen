# Settlers III MapGen — TODO

> Roadmap orientée **travail restant**. Les étapes validées et les essais remplacés appartiennent à `references/dev_notes/V1_8_DEVELOPMENT_LOG.md` et au `CHANGELOG.md`.

## Socle validé

- [x] **v1.5 STABLE** : moteur Continental 768×768 validé dans l’éditeur, View Map et en jeu ; référence `S3_V1_5_V7NOGAP_CORRECTED_UPGRADED_4P_768x768_seed_2026082202`.
- [x] **v1.6 STABLE** : UI/outillage, import EDM/MAP/SAV, vues, inspecteur, thèmes, préférences et A/B.
- [x] **v1.7 STABLE** : Statistiques/Graphiques et exports d’analyse.
- [x] **v1.8 DEV_1 à DEV_11** : workflow, responsive, Batch, vues joueurs, exports, quatre langues, historique, raccourcis v2, preuve `.exe`, verrou `M`, capacité dure, publication et maintenabilité.

Règle absolue : ne pas modifier le moteur v1.5 ni ses fichiers protégés sans raison explicite. Lire `references/SETTLERS3_PREGEN_READ_FIRST.md` avant toute modification génération/format.

## v1.8 DEV_11 — validée

- [x] Maintenance, packaging source déterministe, documentation canonique et architecture/diagnostic finalisés.
- [x] README anglais, quatre captures Windows réelles, provenance, About et neuf Topics GitHub intégrés.
- [x] Clarification de `V`, workflow de snapshot obligatoire et frontière candidates locales/checkpoints publiables verrouillés.
- [x] 231 tests, 49 validations moteur, checksum, autodiagnostic extrait et hashes protégés PASS ; contrôles Windows R1 puis R2 validés.
- [x] Snapshot final, journal et changelog consolidés ; feuille de candidate retirée.
- [x] Checkpoint **DEV_11** sans suffixe prêt pour publication sur `dev` ; aucune candidate `R` publiée.

## v1.8 RC

- [ ] Geler les nouvelles fonctionnalités ; corrections, polish, optimisation et documentation restent autorisés.
- [ ] Produire deux artefacts séparés : ZIP sources/Python et ZIP Windows x64 portable `onedir`, sans installateur.
- [ ] Revalider chemins de ressources, exports près de l’exécutable et settings sous `%APPDATA%/Settlers3MapGen`.
- [ ] Finaliser l’icône seulement à partir du pixel art fourni manuellement par le propriétaire ; aucune image IA.
- [ ] Updater v2 : version locale/dernière STABLE, téléchargement, SHA-256, préservation des settings, remplacement propre et rollback.
- [ ] Tester installation propre, mise à jour, absence réseau, téléchargement interrompu, mauvais checksum, rollback et conservation des préférences.
- [ ] Mettre à jour README, notes, manifests, validation et snapshot avant promotion.

## v1.9 — Archéologie / Data Mapping

### DEV_1 — priorité urgente

- [ ] **Corriger les imports `.EDM` partiellement défaillants** : certains fichiers s’ouvrent, d’autres non ; `.MAP` et `.SAV` testés fonctionnent.
- [ ] Conserver le screenshot utilisateur, les vrais fichiers concernés, leurs SHA-256, provenance et tracebacks complets.
- [ ] Comparer au moins un EDM fonctionnel structurellement proche ; diagnostic d’abord en lecture seule.
- [ ] Identifier la régression ou l’hypothèse de format fautive, puis ajouter une régression minimale fondée uniquement sur des octets confirmés.
- [ ] Terminer ce correctif avant les expériences contrôlées d’IDs.

### Mapping

- [ ] Déterminer les bornes réellement valides des Terrain IDs et Object IDs ; `0–255` reste une grille technique, pas une borne démontrée.
- [ ] Compléter `SETTLERS3_TERRAIN_IDS_REFERENCE.md` et `SETTLERS3_OBJECT_IDS_REFERENCE.md` sans inventer les inconnus.
- [ ] Clarifier trous/réservés, transitions et catégories SAV : settlers, marchandises, outils, ressources transformées, bâtiments, armes, etc.
- [ ] Consolider les tables utilisées par Statistiques, Graphiques, tooltips et inspecteur.
- [ ] Vérifier si EDM/MAP/SAV expose l’identité ou la couleur effective des joueurs ; utiliser l’information seulement si elle est démontrée.
- [ ] Tester les Terrain IDs 18/19, provisoirement `Détail herbe 1/2`, isolés puis en groupes, dans l’éditeur et en jeu.
- [ ] Identifier les nids d’abeilles amazones dans des SAV joués avant tout support Agriculture.

## v1.10 — retour au générateur

### Audit seed et diversité morphologique — priorité majeure

- [ ] Vérifier que la seed complète pilote toutes les étapes stochastiques et qu’aucune réduction, collision ou réinitialisation involontaire ne limite les résultats.
- [ ] Distinguer explicitement génération recalculée et résultat de cache.
- [ ] Construire un corpus multi-seeds et comparer les masques macro-géographiques par signatures exactes et mesures de similarité.
- [ ] Canoniser séparément rotations/orientations et symétries pour détecter les mêmes formes transformées.
- [ ] Conserver comme preuve `references/SETTLERS3_V1_10_SEED_DIVERSITY_EVIDENCE_20260822.png` et ses seeds `69122063`, `958607757`, `1446058262`, `2085415098`.
- [ ] Si la diversité est réellement insuffisante, élargir fortement silhouettes, masses, orientations et organisations sans casser les règles validées.

### Continental multi-tailles

- [ ] 384×384
- [ ] 448×448
- [ ] 512×512
- [ ] 576×576
- [ ] 640×640
- [ ] 704×704
- [ ] Reconfirmation 768×768

Pour chaque taille : starts, morphologie, relief, montagnes/neige, minerais, arbres, Building Stones, poissons, marais, désert, décorations, récifs, rivières/lacs, quotas et stabilité éditeur/View Map/in-game.

## Analyse et UI futures

- [ ] Rafraîchir immédiatement le rapport texte Statistiques lors d’un changement de langue.
- [ ] Ajouter un tri d’inventaire debug par quantité / ID / nom et l’affichage optionnel des IDs connus absents.
- [ ] Étendre les inventaires aux nouvelles familles runtime seulement après mapping confirmé.
- [ ] Enrichir les distributions de composants : massifs, lacs, rivières et clusters.
- [ ] Étudier histogrammes, profils radiaux/cumulatifs, variantes donut et références corpus ; radar seulement s’il reste non trompeur.
- [ ] Garder exactement **deux rayons** configurables pour les ressources proches, jamais trois dans l’UI actuelle.
- [ ] Revoir netteté/résolution des exports PNG de carte et de graphiques.
- [ ] Repenser éventuellement la Vue Hauteurs en carte topographique/classes d’altitude.
- [ ] Concevoir les vues composables : compatibilités, ordre de rendu, légendes et conflits avant implémentation.
- [ ] Concevoir le **Pilotage de la vue** depuis les Graphiques, optionnel et désactivable, avec restauration de l’état précédent.
- [ ] Repenser légèrement Comparaison et la signalétique Chargée/Affichée/Affectée sans dépendre uniquement de la couleur.
- [ ] Comparaison A/B avancée côte-à-côte/diff seulement si l’usage le justifie.
- [ ] Comparaison multi-cartes 3+ planifiée après une grosse passe générateur : viewer scindable en 2/3/4 zones.
- [ ] Label J1–J20 de la Vue Départs : conception dédiée pour ancrage, position et collisions.
- [ ] Loupe locale et informations d’inspecteur près du curseur, avec toggles indépendants.
- [ ] Responsive UI v2, Status/Feedback v2 et audit global des états interactifs lors d’une future refonte.
- [ ] Centres d’export : si le contenu grandit, ajouter contrainte écran et scroll de secours.
- [ ] Surveiller l’incident Statistiques exceptionnellement long ; profiler uniquement avec reproduction complète.
- [ ] Diagnostic mémoire possible v1.11 : mesures NumPy/Pillow factuelles, estimations Python/Tk explicites et déduplication par identité.
- [ ] Tester le calcul raster en arrière-plan uniquement si les optimisations simples deviennent insuffisantes ; Tk reste sur le thread principal.

## Personnalisation et communauté — plus tard

- [ ] Relecture humaine DE/ES ; FR/EN restent les langues de référence jusqu’à validation compétente.
- [ ] Packs de langue déclaratifs versionnés, sans code exécutable, héritage/repli et validation stricte des variables `{...}`.
- [ ] Écosystème de thèmes déclaratifs fondé sur des rôles sémantiques et sans duplication widget par widget.
- [ ] Étendre éventuellement les commandes rebindables après retour d’usage.
- [ ] Passe d’iconographie UI déterministe et validée manuellement.
- [ ] Pixel art fait main pour l’application/exécutable et éventuelle modernisation des marqueurs J1–J20.
- [ ] Maintenir `SETTLERS3_VISUAL_ASSET_PROVENANCE.md` avant chaque intégration visuelle externe.
- [ ] Couleurs A/B personnalisables seulement dans une passe UI dédiée.

## Après Continental

- [ ] **Large Islands / Grandes îles** : constituer et analyser les références natives nécessaires.
- [ ] **Small Islands / Petites îles** ensuite.
- [ ] Conserver l’idée d’un moteur expérimental réellement différent de Legacy/Upgraded, mais seulement après l’audit v1.10.
- [ ] Ne pas confondre Mode, Archetype et Modifier.
- [ ] **Modifiers** : variations contrôlées et parfois fortes, particulièrement utiles avec Batch et comparaison multi-cartes.
- [ ] Ne pas réserver `v2.0` au simple multi-size ; attendre une évolution structurelle réelle.

## ENDGAME — éditeur intégré

- [ ] Attendre que le générateur/workbench soit pratiquement finalisé.
- [ ] Permettre à terme de générer, importer, inspecter, modifier, valider et exporter.
- [ ] Dépasser l’éditeur officiel seulement pour les données EDM/MAP/SAV réellement comprises et validées.
- [ ] Décider tardivement entre fenêtre dédiée et mode/ espace Édition complet.
- [ ] Ne créer maintenant ni placeholder, ni refonte anticipée, ni numéro de version artificiel.

## Invariants à préserver

- Archetype = macro-géographie ; Legacy/Upgraded = contenu, règles, balance, ressources et objets.
- Starts placés tôt et protégés.
- Minerais Upgraded v7 no-gap.
- Aucun aperçu ou asset imaginaire ; toute carte montrée provient de données réelles générées/importées.
- SAV jamais réinventé : lecture ciblée et copie source inchangée seulement.
- IDs inconnus explicitement inconnus.
- Ne jamais repartir d’une version invalidée du générateur.
