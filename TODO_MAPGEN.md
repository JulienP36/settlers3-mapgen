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

## Prochaine RC/STABLE — après v1.10

La v1.8 reste une série de checkpoints DEV : aucune Release ne sera publiée
tant que la génération réelle et la diversité morphologique ne sont pas
corrigées en v1.10. Les tâches ci-dessous sont conservées pour la prochaine
RC, quel que soit son numéro final.

- [ ] Geler les nouvelles fonctionnalités ; corrections, polish, optimisation et documentation restent autorisés.
- [ ] Produire deux artefacts séparés : ZIP sources/Python et ZIP Windows x64 portable `onedir`, sans installateur.
- [ ] Revalider chemins de ressources, exports près de l’exécutable et settings sous `%APPDATA%/Settlers3MapGen`.
- [ ] Finaliser l’icône seulement à partir du pixel art fourni manuellement par le propriétaire ; aucune image IA.
- [ ] Updater v2 : version locale/dernière STABLE, téléchargement, SHA-256, préservation des settings, remplacement propre et rollback.
- [ ] Tester installation propre, mise à jour, absence réseau, téléchargement interrompu, mauvais checksum, rollback et conservation des préférences.
- [ ] Mettre à jour README, notes, manifests, validation et snapshot avant promotion.

## v1.9 — Restructuration interne, puis Data Mapping

### DEV_1 — priorité urgente

- [x] **Corriger les imports `.EDM` partiellement défaillants** : certains fichiers s’ouvraient, d’autres non ; `.MAP` et `.SAV` restent fonctionnels.
- [x] Conserver le screenshot utilisateur, les vrais fichiers concernés, leurs SHA-256, provenance et tracebacks complets dans l’Issue #4 et la référence diagnostique.
- [x] Comparer les deux EDM fautifs aux EDM fonctionnels du dépôt ; diagnostic effectué en lecture seule.
- [x] Cause identifiée : 1–3 octets opaques après la partie terminale `type 0 / taille 8`, pour alignement DWORD du fichier ; checksums sources valides.
- [x] Ajouter une régression minimale couvrant les trois longueurs de remplissage et le refus des queues non terminales.
- [x] Validation Windows des deux fichiers réels dans `v1.9 DEV_1_R1` ; Issue #4 prête à fermer.
- [x] Correctif terminé avant les expériences contrôlées d’IDs.

### Restructuration — priorité principale

- [x] Cartographier les responsabilités, dépendances, imports, tailles, points d’entrée et tests avant tout déplacement.
- [x] Ajouter des tests de caractérisation autour des comportements GUI déplacés hors de l’héritage historique.
- [x] Décomposer `application/main_window.py` par responsabilités cohérentes : Viewer, Analyse, Exports, Imports, Raccourcis/Aide, Batch, Historique, Settings, Theme, Langue, Tâches et workflow applicatif de génération sont isolés ; le fichier restant porte le shell cohérent.
- [x] Supprimer les noms et entrypoints GUI versionnés sans créer une nouvelle couche : la chaîne historique vit désormais sous des noms de responsabilité dans `application/`.
- [x] Déplacer les trois couches moteur dans `generation/` sous des noms stables et prouver l’équivalence déterministe Legacy/Upgraded ; la suppression progressive de l’héritage interne reste à faire.
- [x] Auditer les petits modules et entrypoints : aucun fragment artificiel à
  fusionner ; les modules courts restants portent une frontière, une API de
  paquet, un catalogue ou une responsabilité indépendante.
- [x] Nettoyer les noms de fichiers de tests figés sur d’anciennes DEV et organiser les tests applicatifs par sous-système sans perdre la couverture comportementale utile.
- [x] Auditer la pertinence de la suite après R7 : supprimer sept doublons ou
  gardes obsolètes, neutraliser les versions historiques et interdire leur
  retour dans les noms de tests.
- [ ] Remplacer progressivement les assertions GUI fondées sur le texte source
  par des contrats comportementaux ou de widgets ; commencer par Batch et
  Historique, qui concentrent la majorité de ces caractérisations.
- [x] Simplifier la chaîne des fenêtres et le runtime : une fondation Tk nommée, un `MainWindow` composé et un seul point de construction du générateur dans `runtime.App`.
- [x] À la clôture de la restructuration, auditer le coût de contexte : raccourcir
  les instructions projet, supprimer les doublons/états obsolètes et router
  chaque tâche vers les seules références nécessaires.
- [ ] Procéder par extractions mécaniques courtes, avec comportement inchangé, tests ciblés puis validation complète à chaque DEV terminée.
- [ ] Intégrer les apports d’autres LLM comme hypothèses traçables et non comme vérité de référence.
- [x] Auditer toutes les références après publication de DEV_2 : conserver les
  références spécialisées importantes, compacter les répétitions, puis
  fusionner/renommer/supprimer uniquement avec preuve d’obsolescence et liens
  entrants migrés.

### Data Mapping — fin de v1.9

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
