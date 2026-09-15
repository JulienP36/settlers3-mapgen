# Settlers III MapGen — TODO
> Roadmap orientée **travail restant**. Pour reprendre sans ambiguïté, lire
> `references/REFERENCE_INDEX.md`, puis le snapshot vivant et la matrice
> courante. Les étapes validées et les essais remplacés sont historiques.
## Historique clôturé — non prescriptif
- Les jalons v1.5 à v1.9 sont terminés et conservés dans le `CHANGELOG.md`,
  les journaux `references/dev_notes/` et `references/history/`.
- La calibration 768 de l'Upgraded est portée par le profil actif du générateur
  indépendant et la bibliothèque native reste une ressource de compatibilité.
  Il n'existe pas de moteur Upgraded v1.5 actif.
- Le générateur Legacy procédural de DEV_1 et ses heuristiques minières ont
  été retirés ; les essais associés restent archivés à titre explicatif.
Lire `references/SETTLERS3_PREGEN_READ_FIRST.md` avant toute modification de génération ou de format. La ligne active est v2.0 DEV6 : Legacy natif et Upgraded indépendant sont séparés, et le Custom avance par sections sémantiques testées.
## Future release — après DEV6–DEV8
Les prochaines versions RC/STABLE restent distinctes du travail courant. Une release ne sera préparée qu'après validation des générations, des exports et de la diversité réellement obtenue.
- [ ] Geler les nouvelles fonctionnalités ; garder les corrections, le polish,
  l'optimisation et la documentation autorisés.
- [ ] Produire un ZIP sources/Python et un ZIP Windows x64 portable `onedir`,
  sans installateur.
- [ ] Revalider ressources, exports, settings `%APPDATA%/Settlers3MapGen`,
  installation propre, mise à jour, absence réseau, checksum et rollback.
- [ ] Finaliser l'icône uniquement à partir du pixel art fourni manuellement ;
  aucune image IA.
- [ ] Finaliser l'updater v2 : version, téléchargement, SHA-256, settings,
  remplacement propre et rollback.
- [ ] Mettre à jour README, notes, manifests, validations et snapshot avant
  promotion.
## Historique clôturé — v1.9, restructuration et Data Mapping

Les fondations UI, imports, séparation des couches, validations et premiers
résultats de Data Mapping sont terminés. Le détail des décisions et des pistes
non retenues reste dans `references/dev_notes/` et le `CHANGELOG.md`; aucun
ancien sous-TODO ne doit être repris comme tâche active.
Les bornes encore inconnues, les objets `82/83`, les champs SAV non décodés et
les résidus de format sont suivis dans la section v2.0 « Résidus d’audit » ou
dans les références spécialisées, jamais dans une ancienne liste v1.x.

## v2.0 — reconstruction native Legacy, puis Custom

La **reconstruction complète des pipelines** est le périmètre v2.0. Le
générateur procédural Continental DEV_1 a été retiré ; le Legacy natif est
validé dans DEV_2 et l’Upgraded indépendant dans DEV_3/DEV_5.

### v2.0 — Upgraded indépendant

- [x] Dupliquer le pipeline terrain Legacy dans `generators/upgraded/` sans
  dépendance d’exécution vers `generators/legacy/`.
- [x] Réintégrer la génération calibrée des minerais de montagnes.
- [x] Réintégrer poissons, arbres, décorations et pierres de construction.
- [x] Dev 5 validé : calquer les objets statiques sur les familles Legacy, conserver
  les récifs Upgraded, restaurer les bonus arbres/pierres/mini-marais, placer
  30 % des adultes en mini-forêts, réserver les pousses aux forêts et créer
  les clusters de pierres.
- [x] Désactiver toute génération de boue dans Upgraded.
- [x] Garder le positionnement des joueurs isolé pour une passe dédiée ; le
  pont actuel reste provisoire et ne crée ni ressources ni colons de départ.
- [x] Calibrer les blobs miniers avec compensation de la projection
  parallélogramme, sans changer la topologie HEX6, les quotas, les quantités ou
  la règle no-gap.
- [x] Documenter le terrain `34` comme **Patch d’herbe rocheuse**, l’ajouter au
  graphique Montagne avec une couleur dédiée et harmoniser sa couleur de carte.
- [x] Ajouter les tests de parité terrain et les validations spécifiques
  Upgraded du checkpoint DEV_3 ; la parité externe complète reste à rejouer
  dans l’éditeur/jeu lors de la prochaine validation dédiée.

- [x] Ancien pipeline Legacy DEV_1 retiré ; chemin Upgraded isolé avec ses
  règles, profils et validations. La comparaison minière DEV_1/natif est
  archivée et ses formes fragmentées ne sont pas reconduites.
- [x] Audits non-terrain complétés : ordre Area/bâtiments/colons/départs,
  cellules runtime, registre type 9, catalogue `0x51B010/0x51B1A0`, chemin
  `GameDataSave::Save`, offsets hexagonaux, filtre des départs et stock initial
  (`0x506CF0 -> 0x5046B0 -> 0x504420`).
- [ ] Poursuivre séparément les résidus de format : couverture complète des
  tokens d'empreinte, nomenclature des IDs/champs, source externe type 9 et
  writer EDM/MAP ; voir `references/S3_EXE_STATIC_NON_TERRAIN_AUDIT_20260901.md`.
- [x] Documenter l'ordre natif complet observable : noyau terrain, objets et
  ressources de sol, re-seed, départs, ville/stock et finalisation.
- [x] Implémenter le noyau Legacy natif séparé : seed, relief, familles de
  terrains, transitions, hydrologie et ordre d’écriture démontrés.
- [x] Définir l’archétype Continental v1 au-dessus de ce noyau sans lui
  appliquer une seconde macro-forme.
- [x] Reproduire le terrain, les ressources globales (minerais/poissons), les
  objets/décorations et les validations Legacy avec les mesures natives ; les
  objets/ressources de départ, colons et writer SAV restent hors périmètre.
- [x] Exposer les tailles natives 256–1024, les miroirs Axe long/Axe court/Les
  deux pour Legacy et Upgraded, les avertissements de viabilité et l'export
  MAP/EDM multi-tailles via scaffold de test.
- [x] Laisser toutes les tailles du contrat générables et exportables pour
  test, sans refus lié au statut « non testé » ; conserver les avertissements
  uniquement comme information.
- [ ] **Dev 6 — générateur Custom** : socle déclaratif décrit dans
  `references/SETTLERS3_CUSTOM_GENERATOR_ARCHITECTURE_DEV6.md` ; tranche
  DEV_6_R61 : Minerais/Poissons/Rivières, Arbres, Pierres, Décorations et bonus raccordés, trois algorithmes de gisements, moyennes natives Legacy 8 / Upgraded 10, bande côtière directe, quotas relatifs, invariants d’emprise et diagnostics de placement du lac/rivière ; rivières bonus reconstruites sur le système natif local ; interface des bonus compacte et verticale.
  La forêt demande `30` adultes + `20` pousses par joueur, adultes avant
  pousses, espacement `3 HEX6` et rayon minimal dérivé. Legacy/Upgraded sont
  des presets de la route Custom, bonus désactivés par défaut ; le switch herbe
  accepte `18`, `19`, `24`, jamais `34`, pour objets et bonus. Le forçage global
  étendu est disponible pour les cinq bonus, désactivé par défaut, avec
  indicateur de repli effectif. R45 étend le halo à toutes les écritures d’objets,
  passe native Legacy comprise, et corrige la forme `Native` des
  marais avec le plan global. Forêts, pierres et marais sont validés ;
  R48 ajoute les formes et surfaces des bonus minéraux ; R50 ajoute leurs sprites et le rayon commun ; R51 varie la forme organique, verrouille les listes, rapproche les unités, grise les sprites inactifs, porte le marais à 16 et rend les bornes minérales dynamiques `820/1 640/2 460` ; R55 ajoute la forme Native/Hexagone et la profondeur des lacs ; R56 renforce les deux anneaux de rive ; R57 refait les rivières par le système natif local sans cible globale ; R58 borne le lac à `16 HEX6` et les rivières cibles par lac à `6` ; validation utilisateur des zones minérales et du lac/rivière encore à effectuer.
- [x] R34–R36 — moteur des cinq bonus et réglages Custom raccordés ;
  forêt Legacy/Upgraded `30 + 20`, maximum `100` chacun, espacement `3 HEX6`.
- [x] R37 — forêts et pierres validées par l’utilisateur : maximum `100`, pierres
  `15` par défaut (maximum `50`, moyenne `10`), rayon dérivé, couleur des pousses harmonisée ; base intégrée dans R38 avec switch herbe protégé et preset Custom commun.
- [x] R38 — corriger le switch herbe/réservations, les presets Custom publics et le forçage étendu des cinq bonus.
- [x] R39 — supprimer les pierres résiduelles à taux global `0 %` quand le bonus local est désactivé ; aligner le stock bonus sur `full_range_mean_tilt`. Forçage étendu inchangé.
- [x] R40 — désactiver les familles globales remplacées avant le passage natif, supprimer les réservations de cases vides et empêcher les arbres natifs de survivre dans un bonus pierres à `0 %`.
- [x] R41 — première liste de formes du mini-marais ; [x] R42 — corriger le scaling de l’hexagone, remplacer la fausse forme Native par le plan natif global des marais et porter temporairement le rayon maximal à `20` pour les tests ; [x] R43 — différer les seules familles nécessaires lorsqu’un bonus est actif : terrains bonus avant les terrains non liés à l’archétype, objets bonus avant les objets globaux ; conserver le chemin sans bonus strictement inchangé ; [x] R44 — placer les adultes des forêts bonus avant les pousses et appliquer le halo des hitboxes réellement écrites aux bonus ; [x] R45 — étendre ce halo à toutes les écritures d’objets, y compris la passe native Legacy, et rendre la forme `Native` des marais réellement non hexagonale tout en conservant son plan global ; [x] R46 — générer une empreinte `Native` indépendante pour chaque start tout en conservant le plan natif global, les replis légaux et le chemin sans bonus inchangé ; validation utilisateur reçue pour les marais R46.
- [x] R47 — recherche forcée par couronnes D+3 à D+34 après la bande locale,
  plans objets avant écriture, emprise entière protégée autour des tours ; forçage
  OFF inchangé. Validation visuelle R47 attendue.
- [x] R48 — forme organique compacte, surfaces égale/prorata/personnalisée,
  cœurs 100 % minerai, moyenne globale/par minerai et shortfall légal.
- [x] R49/R50 — panneau minéral compacté puis finition des zones : contrôles contextuels, sprites charbon/fer/or et rayon unique `1–16 HEX6`.
- [x] R51–R54 — forme organique arrondie/variable type Upgraded, compensation de
  projection, listes non éditables, unités accolées, sprites grisées, marais
  `1–16 HEX6`, bornes `820/1 640/2 460`, ordre compact du panneau
  et conservation partagée des valeurs dérivées lors d’un changement de répartition ; validation utilisateur à effectuer.
- [ ] R61 — bonus lac/rivière et fignolages visuels : tester Native/Hexagone,
  les deux anneaux de rive, les sorties natives locales, l’absence de recherche
  de cible globale, le seuil d’eau `0`, les diagnostics, les poissons, la
  protection de tour et les états UI sous Windows ; compacter puis polir les
  panneaux et labels DEV6 ; rayon maximal `16 HEX6`, cible maximale `6`.
- [ ] **Dev 7 — archétypes Custom** : contrats de masses jouables et solveur de
  répartition des départs, notamment pour les archipels et les joueurs.
- [ ] **Dev 8 — modificateurs** : pile orthogonale avec ordre, activation, dépendances et diagnostics.
- [ ] **DEV8/9 — validité des starts** : certaines positions de départ restent parfois invalides malgré les contrôles actuels ; décoder la règle native supplémentaire et corriger la sélection.
- [ ] Revalider progressivement terrains, transitions, joueurs, ressources,
  macro-forme, côtes et exports 832–1024 dans l'éditeur communautaire/jeu.
## Raffinements différés — après stabilisation du socle v2.0
- [ ] Rendre configurable l’**extension maximale du forçage des bonus de
  départ**. Le réglage devra être exprimé en hexagones au-delà de `D`, avec
  `34` conservé comme valeur par défaut actuelle ; il ne devra pas modifier le
  comportement du forçage désactivé ni l’ordre de recherche par couronnes.
  Ne pas ouvrir ce chantier avant d’avoir terminé les validations restantes de
  DEV6 et stabilisé la suite DEV7/DEV8.
- [ ] Ajouter éventuellement un **nombre de zones par minerai** indépendant
  du mode de surface, puis recalculer les surfaces en conséquence.
- [ ] Étendre ultérieurement le bonus rocheux aux familles **gemmes** et
  **soufre**, avec validation de leurs transitions et de leurs quotas.
- [ ] Dev 8/9 : ajouter des tooltips courts aux contrôles minéraux et bonus.

### Garde-fous

- [ ] Préserver la chaîne eau → plage/rive → terrain, la topologie HEX6 et les
  règles hydrologiques mesurées.
- [ ] Ne jamais mélanger les calibrations internes Legacy et Upgraded : chaque
  moteur garde profils, références et tests séparés ; les sélections publiques
  et futurs archétypes suivent néanmoins la route Custom commune par presets.
- [x] Maintenir l'ordre natif démontré : terrain/objets/ressources, re-seed,
  départs, ville/stock puis finalisation ; conserver le footprint natif et la
  protection sans halo.
- [x] Séparer décor initial byte 14, objet runtime byte 7 et byte 9 SAV encore
  inconnu.
- [ ] Toute comparaison visuelle doit venir d'un EDM/MAP/SAV réel ou d'une génération déterministe identifiée.

## Analyse et UI futures

- [ ] Rafraîchir le rapport Statistiques après changement de langue ; améliorer inventaires, IDs absents, familles runtime et distributions.
- [ ] Étudier histogrammes, profils radiaux/cumulatifs et références corpus sans
  produire de visualisation trompeuse.
- [ ] Garder exactement deux rayons configurables pour les ressources proches.
- [ ] Revoir résolution des exports PNG et éventuellement transformer Hauteurs
  en carte topographique/classes d'altitude.
- [x] Première liaison Graphiques → Vue avec payloads sémantiques, cache de
  surbrillance et conservation du cadrage ; A/B reste volontairement
  informatif (tooltip uniquement).
- [x] Router tous les graphes **X proche(s)** vers la vue globale, ancrer leur
  flèche aux bordures des territoires de départ d’origine et conserver le
  contexte des départs via les marqueurs/cercle partagés.
- [x] Ajouter les tailles de marqueurs Petits / Normaux / Grands (plus
  Masqués), conserver la compatibilité des préférences historiques et propager
  le réglage à toutes les vues, Batch et Historique.
- [x] Supprimer la vue dédiée Départs et ajouter l’option indépendante
  **Cercles de départ**, propagée à toutes les vues et previews sans lien avec
  l’opacité couche.
- [x] Renommer le graphique des objets en **Familles d’objets** et figer son
  ordre de colonnes sur les nombres rouges de la référence utilisateur.
- [x] Corriger le flash initial de la fenêtre **Générer un lot** en la gardant
  masquée pendant la construction de ses contrôles et de sa géométrie.
- [x] Corriger le centre d’export multi-taille et conserver `references/` dans
  les ZIP sources tout en l’excluant des commits/push GitHub.
- [ ] Étendre le pilotage de la vue depuis les Graphiques : légendes, conflits,
  clic persistant et multi-cartes 3+.
- [ ] Repenser Comparaison, signalétique Chargée/Affichée/Affectée et A/B avancé
  seulement si l'usage le justifie ; multi-cartes 3+ après le générateur.
- [ ] Concevoir labels J1–J20, loupe locale, inspecteur près du curseur et
  indépendance des toggles.
- [ ] Reporter responsive UI v2, Status/Feedback v2, centres d'export et
  diagnostic mémoire à une passe dédiée avec mesures factuelles.
- [ ] Implémenter dans Upgraded la passe séparée du positionnement des starts et
  des données natives `.sav` ; Dev 5 utilise le pont de coordonnées existant
  sans le recalculer.

## Personnalisation, après Continental et ENDGAME

- [ ] Relire DE/ES, versionner les packs de langue et thèmes déclaratifs, puis
  étendre éventuellement les commandes rebindables.
- [ ] Créer l'iconographie UI et le pixel art manuellement ; maintenir la
  provenance des assets et ne rien importer sans validation.
- [ ] Après Continental, analyser les références natives de **Large Islands**,
  puis **Small Islands**, avant les Modifiers.
- [ ] Garder ENDGAME pour la fin : générer, importer, inspecter, modifier,
  valider et exporter seulement les données EDM/MAP/SAV comprises.
## Invariants

- Archétype = contexte macro-géographique et futur contrat des masses jouables ;
  Legacy/Upgraded = exécution du relief, hydrologie, contenu, règles, balance,
  ressources et objets. Les montagnes et lacs natifs sont dérivés de ces passes ;
  les bonus rocheux/lacustres sont des zones locales explicites, jamais des objets.
- Legacy : terrain/objets/ressources avant re-seed, puis starts/ville/stock ;
  Upgraded : terrain copié indépendant, contenu global spécifique, minerais v7
  no-gap préservés et bonus de contenu autour des coordonnées de départ
  provisoires.
- Aucun aperçu ou asset imaginaire ; SAV lu sans réinvention et copié inchangé.
- IDs inconnus explicitement inconnus ; ne jamais repartir d'une version
  invalidée du générateur.
