# Settlers III MapGen — TODO
> Roadmap orientée **travail restant**. Pour reprendre sans ambiguïté, lire
> `references/REFERENCE_INDEX.md`, puis le snapshot vivant et la matrice
> courante. Les étapes validées et les essais remplacés sont historiques.
## Historique clôturé — v1.9 (non prescriptif)
- Les jalons v1.5 à v1.9 sont terminés et conservés dans le `CHANGELOG.md`,
  les journaux `references/dev_notes/` et `references/history/`.
- La calibration 768 de l’Upgraded est portée par le profil actif du générateur
  indépendant ; la bibliothèque native reste une ressource de compatibilité.
  Il n'existe pas de moteur Upgraded v1.5 actif.
- Le générateur Legacy procédural de DEV_1 et ses heuristiques minières ont été
  retirés ; les essais associés restent archivés à titre explicatif.
- R19 a été rejetée pour le relief : elle conservait la côte et le masque
  Legacy. R20 a introduit les providers complets indépendants ; R21 a été
  rejetée pour son enveloppe post-génération ; R22 borne le domaine ; R23 est remplacée par R24, qui sépare la contribution des couches du delta de source ; R25 stabilise le rendu ; R26 conserve l’ancienne vue pendant les recalculs ; R27 fixe les premiers gates macro ; R28 est rejetée comme piste de presets trop ronds ; R29 installe l’éditeur multi-bruits et sépare l’état Archétype du mode Générateur ; R30 rend le lissage de la macro optionnel et corrige son ergonomie ; R31 aligne les panneaux indicatifs et exacts et rend l’applicabilité des réglages explicite ; R32 ajoute les fusions dynamiques, les miniatures brutes et remonte les previews principales ; R33 rend la pile réordonnable, duplicable, supprimable et isolable en Solo dans l’aperçu ; R34 recadre Solo et la source Legacy des miniatures ; R35 retire l’image indicative trompeuse, aligne la miniature source sur le raster exact et corrige le double positionnement des seuils ; R36 ajoute les transformations de sortie communes et place l’aide de l’éditeur de noisemaps dans son titre.
Lire `references/SETTLERS3_PREGEN_READ_FIRST.md` avant toute modification de génération ou de format. Le dernier checkpoint publié est v2.0 DEV8, issu de la candidate R86. **DEV8 est terminée** : le sélecteur Archétype affiche maintenant « Personnalisé » quand les paramètres sont édités, puis se recale sur le profil nommé sélectionné. L’utilisateur confirme la validation Windows R85 ; les rivières Custom et essais multi-tailles sont déclarés terminés. Toutes les tâches restantes sont transférées à **DEV9**, y compris Grandes îles. Voir `references/SETTLERS3_REFERENCE_AUDIT_20260930.md`.
## Future release — après DEV9
Les prochaines versions RC/STABLE restent distinctes du travail courant ; une release ne sera préparée qu'après validation des générations, des exports et de la diversité réellement obtenue.
- [ ] Geler les nouvelles fonctionnalités ; garder corrections, polish,
  optimisation et documentation autorisés.
- [ ] Produire un ZIP sources/Python et un ZIP Windows x64 portable `onedir`, sans
  installateur.
- [ ] Revalider ressources, exports, settings `%APPDATA%/Settlers3MapGen`, installation
  propre, mise à jour, absence réseau, checksum et rollback.
- [ ] Finaliser l'icône uniquement à partir du pixel art fourni manuellement ;
  aucune image IA.
- [ ] Finaliser l'updater v2 : version, téléchargement, SHA-256, settings,
  remplacement propre et rollback.
- [ ] Mettre à jour README, notes, manifests, validations et snapshot avant promotion.
## v2.1 — ouverture
- [ ] Au tout début de `v2.1 DEV1`, lire le todo personnel de Julien comme
  entrée obligatoire de priorisation avant toute planification ou
  implémentation ; s’il n’est pas accessible dans le contexte du projet, le
  demander avant de poursuivre.
### Historique récent — génération Legacy Custom dérivée du Legacy
R67–R72 ont extrait et rendu réglables les blocs natifs, tout en conservant la
sortie Legacy par défaut. R75 a introduit la grille d’ancres aléatoires 32 et
le raffinement midpoint natif, sans masque de silhouette ni lacs/montagnes
estampés. Après les essais R76–R78, R79 repart de R76 : une distribution
aléatoire intérieure homogène remplace les bandes d’altitude et une seule
couronne d’ancres côtières rejoint le bord marin natif. Les détails fins
gardent leur base Custom de 75 %. R77 et R78 sont rejetées.
R80 a réduit l’alignement des centres de raffinement. R81 a tenté
une déformation locale et un faible adoucissement, mais la noisemap Custom
restait trop saturée et les rivières grimpaient sur un relief trop haut.
R82 supprime le vide entre les plages des ancres et comprime réellement les
altitudes positives à 65 %. Les seuils montagne/neige visibles de cette
source sont recalés à 98/125 ; les anciens profils sont migrés.
Les lacs restent produits par le champ raffiné, sans placement explicite ni
quota. Le contrôle existant de détails fins multiplie la base Custom de 75 % ;
le Legacy natif garde son amplitude à 100 %. Une règle HEX6 retire les
fragments de terre détachés. Le chemin Legacy natif est inchangé ; les réglages natifs restent actifs sur `Legacy par blocs`,
les sources noise-map complètes restent indépendantes, les profils
`legacy_derived` sauvegardés continuent d’être migrés, et les previews exacte
et indicative partagent le relief Custom.

**Mise à jour 2026-09-30 :** l’utilisateur indique que les anomalies de rivières
Custom sont réglées par un bruit plus doux près des bords d’eau et que les
essais multi-tailles sont terminés. Les notes R82–R85 ci-dessus sont
l’historique des candidates ; ne pas réouvrir ces points sans nouvelle
reproduction.

### DEV8 publiée — candidate finale R86

R83 a été acceptée après essai utilisateur : les couches inactives affichent
leurs miniatures sans relancer la preview générale, le groupe Legacy natif est
replié et la taille initiale est 512.

R84 remplace les anciens presets d’essai par deux profils utilisables :
« Classique » conserve le Legacy natif ; « Continental » choisit le relief
Legacy par blocs R82. Toute modification d’un profil nommé affiche son état
personnalisé. Le seed d’ouverture redevient daté à l’heure locale. Dans
l’éditeur Archétype, les flèches numériques avancent de 1 et la molette de 5.
Les masques Cœur et Serpent sont retirés, Volcan devient Dôme, et deux formes
simples sont disponibles : Ellipse et Anneau.

Les « Modificateurs » restent des emplacements réservés visibles dans l’en-tête
et les lots, mais sont désactivés et sans effet sur la génération. Le champ vide
est conservé dans le contrat de requête et dans la clé du cache ; aucune
implémentation fonctionnelle n’est engagée pour la sortie 2.0.

R85 expose les profils « Classique » (relief natif) et « Continental » (relief
Legacy par blocs R82) dans le sélecteur principal Archétype. R86 ajoute l’état
« Personnalisé » à ce sélecteur après édition, retiré automatiquement quand un
profil nommé est resélectionné. L’onglet et le feedback conservent « Profil
personnalisé ». Les deux profils gardent la géographie interne `continental`
et ne changent pas le Mode. Les libellés du Mode sont « Classique »,
« Amélioré » et « Personnalisé », sans modifier les clés des moteurs.

R86 passe les **641 tests de non-régression**, le smoke-test et l’auto-test
applicatif extrait. La validation visuelle de l’UI R85 est confirmée par
l’utilisateur. Les références compactées restent incluses dans les ZIP
sources et exclues des commits/push GitHub.

La correction hydrologique Custom est déclarée terminée par le dernier retour
utilisateur : champ plus doux près des bords d’eau. Le Legacy natif reste
inchangé. Ne reprendre l’investigation qu’en cas de nouvelle reproduction.
L’utilisateur confirme aussi la validation Windows de l’interface R85 et les
tests multi-tailles. DEV8 est clôturée et publiée sans suffixe ; tout chantier ouvert passe à
DEV9.

### DEV9 — Grandes îles et suites

- [ ] Ne pas débloquer l’archétype en changeant uniquement son drapeau : le
  registre le garde explicitement non implémenté, et certaines passes Custom
  suppriment les composantes de terre détachées.
- [ ] Préserver la silhouette du prototype utilisateur 384×384 / 4 joueurs,
  déjà jugée prometteuse. Vérifier si cette piste est encore facilement
  finalisable ; les points connus sont l’équilibre terrain par île et la
  validité des départs P1/P4 (proximité des objets statiques à vérifier).
- [ ] Traiter Grandes îles comme un chantier dédié : conservation des masses,
  équilibre local par île et sécurité des départs ; la dépendance DEV9/10 sur
  les règles supplémentaires des départs sont en DEV9.

### DEV9 — tout le travail restant

- [ ] Appliquer au sélecteur Mode le comportement dynamique validé pour
  Archétype : n’afficher « Personnalisé » qu’après une modification effective,
  puis revenir au profil nommé lorsqu’il est resélectionné.
- [x] R86 ajoute « Personnalisé » au sélecteur principal Archétype quand un
  profil est édité ; le statut se met à jour au retour vers Classique ou
  Continental, et reste synchronisé avec l’onglet Archétype.
- [x] L’utilisateur confirme la validation visuelle Windows R85 (seed, pas
  numériques, profils, formes, emplacements Modificateurs et comportements R83).
- [ ] DEV9 — évaluer Grandes îles à partir du prototype utilisateur 384×384 /
  4 joueurs, l’équilibre terrain par île et la validité des départs P1/P4.
- [x] Tests multi-tailles : déclarés terminés par l’utilisateur le 2026-09-30.
- [x] Anomalies de rivières Custom : déclarées réglées avec un bruit plus doux
  autour des bords d’eau le 2026-09-30.
- Les tests multi-tailles et rivières n’ont pas de tableau de résultats joint
  à la candidate ; consigner les valeurs si elles sont nécessaires à un futur
  audit. Les validations des tailles 832–1024 et l’équilibrage des départs
  restent des sujets de viabilité distincts, pas des échecs des essais DEV8.

R32 est validée, R33 à R49 fiabilisent la pile, le cycle de preview, les
transformations et le provider de masque dessinable/importable. R50 ajoute le
rapport déterministe multi-tailles, multi-seeds et multi-miroirs. R51 reste une
calibration Continental diagnostique ; R52 ajoute le premier preset Custom
construit par composition de noises et son gate conjoint macro-forme/placement
des joueurs, sans toucher au Legacy. R53 conserve cette composition et recale
son cadre océanique sur l’enveloppe native en cellules absolues. La roadmap
détaillée, les profils cibles et les seuils sont dans
`docs/ARCHETYPE_ROADMAP.md`. Les noises restent autonomes ; les masques sont
des modulations spatiales séparées des fusions. R54 ajoute les providers
`hybrid_fbm`, `turbulence`, `worley_f1`, `worley_f2` et
`worley_f2_minus_f1` ; R55 ajoute `heterogeneous_fbm` et `ridged_multifractal`,
corrige le cadrage des previews et réapplique l’enveloppe native-calibrée aux
masques. R56 réduit les recalculs des miniatures de fusion/masque sans changer
la macro. R57 ajoute une option de fréquence adaptative par taille ; R58
atténue progressivement les octaves fines. Le test de parallélisme montre un
gain à deux workers seulement pour six sources actives, mais pas de gain stable
sur le preset R53 courant : ne pas ajouter de réglage global à ce stade.
## v2.0 — reconstruction native Legacy, puis Custom
La **reconstruction complète des pipelines** est le périmètre v2.0. Le
générateur procédural Continental DEV_1 a été retiré ; le Legacy natif est
validé dans DEV_2 et l’Upgraded indépendant dans DEV_3/DEV_5.
### v2.0 — Upgraded indépendant

- [x] Dupliquer le pipeline terrain Legacy dans `generators/upgraded/` sans
  dépendance d’exécution vers `generators/legacy/`.
- [x] Réintégrer la génération calibrée des minerais de montagnes.
- [x] Réintégrer poissons, arbres, décorations et pierres de construction.
- [x] Dev 5 validé : calquer les objets statiques sur les familles Legacy, conserver les récifs Upgraded, restaurer les bonus arbres/pierres/mini-marais, placer 30 % des adultes en mini-forêts, réserver les pousses aux forêts et créer les clusters de pierres.
- [x] Désactiver toute génération de boue dans Upgraded.
- [x] Garder le positionnement des joueurs isolé pour une passe dédiée ; le pont actuel reste provisoire et ne crée ni ressources ni colons de départ.
- [x] Calibrer les blobs miniers avec compensation de la projection parallélogramme, sans changer la topologie HEX6, les quotas, les quantités ou la règle no-gap.
- [x] Documenter le terrain `34` comme **Patch d’herbe rocheuse**, l’ajouter au graphique Montagne avec une couleur dédiée et harmoniser sa couleur de carte.
- [x] Ajouter les tests de parité terrain et les validations spécifiques Upgraded du checkpoint DEV_3 ; la parité externe complète reste à rejouer dans l’éditeur/jeu lors de la prochaine validation dédiée.

- [x] Ancien pipeline Legacy DEV_1 retiré ; chemin Upgraded isolé avec ses
  règles, profils et validations. La comparaison minière DEV_1/natif est
  archivée et ses formes fragmentées ne sont pas reconduites.
- [x] Audits non-terrain complétés : ordre Area/bâtiments/colons/départs,
  cellules runtime, registre type 9, catalogue `0x51B010/0x51B1A0`, chemin
  `GameDataSave::Save`, offsets hexagonaux, filtre des départs et stock initial
  (`0x506CF0 -> 0x5046B0 -> 0x504420`).
- [ ] Poursuivre séparément les résidus de format : couverture complète des tokens
  d’empreinte, nomenclature des IDs/champs, source externe type 9 et writer EDM/MAP ;
  voir `references/S3_EXE_STATIC_NON_TERRAIN_AUDIT_20260901.md`.
- [x] Documenter l'ordre natif complet observable : noyau terrain, objets et ressources
  de sol, re-seed, départs, ville/stock et finalisation.
- [x] Implémenter le noyau Legacy natif séparé : seed, relief, familles de
  terrains, transitions, hydrologie et ordre d’écriture démontrés.
- [x] Définir l’archétype Continental v1 au-dessus de ce noyau sans lui
  appliquer une seconde macro-forme.
- [x] Reproduire le terrain, les ressources globales (minerais/poissons), les objets/décorations et les validations Legacy avec les mesures natives ; les objets/ressources de départ, colons et writer SAV restent hors périmètre.
- [x] Exposer les tailles natives 256–1024, les miroirs Axe long/Axe court/Les deux pour Legacy et Upgraded, les avertissements de viabilité et l'export MAP/EDM multi-tailles via scaffold de test.
- [x] Laisser toutes les tailles du contrat générables et exportables pour
  test, sans refus lié au statut « non testé » ; conserver les avertissements
  uniquement comme information.
- [x] **Dev 6 — générateur Custom** : socle déclaratif décrit dans
  `references/SETTLERS3_CUSTOM_GENERATOR_ARCHITECTURE_DEV6.md`. Les sections
  Custom et les cinq bonus sont raccordés aux deux moteurs ; les validations de
  génération restantes sont suivies par R61 et les tests spécialisés.
- [x] R17–R19 — transition Custom sans reconstruction au premier changement,
  rollback de l’essai R18 et clôture des points 1 à 6 de la mini-roadmap UI par
  validation utilisateur.
- [x] R34–R58 — moteur des cinq bonus, forçage par couronnes, hitboxes,
  formes minérales et lac/rivière documentés dans les notes de candidate.
- [x] R20–R26 — refonte ergonomique du panneau Bonus : règles communes, groupes
  lisibles, panneaux verticaux, microcopy/tooltips ; R21 conserve uniquement
  l’aperçu calculé des Pierres de construction et R22 isole la matrice rocheuse
  et resserre tous les cadres internes ; R23 ajoute une grille responsive des
  sections, R24 l’applique aussi aux panneaux internes du Bonus et rapproche
  « Réinitialiser » de « modifié » ; R25 corrige le reflow par largeur de
  fenêtre, équilibre les couples Terrains/Décorations et aligne les sections
  en haut de leurs lignes ; R26 retire l’aide redondante de Terrains, place le
  bloc dense à gauche, ajoute la troisième colonne du Bonus et avance le seuil
  de séparation, sans reconstruction lors des edits. Aucun changement de
  génération.
  Validation utilisateur reçue ; le checkpoint DEV7 est publié.
- [x] **DEV_6_R61** — bonus lac/rivière et fignolages visuels. Cette candidate
  est antérieure à DEV7 ; ses contrôles de panneau sont historiques et ne
  constituent plus une tâche active.
- [x] **Rivières Custom hors Legacy** — dernier retour utilisateur du
  2026-09-30 : les anomalies sont réglées par un champ de bruit plus doux près
  des bords d’eau. Le tracé Legacy natif reste inchangé ; ne rouvrir qu’en cas
  de nouvelle reproduction.
- [x] **R50 — qualification des masques manuels** : l’outil déterministe couvre
  les tailles `384/512/768`, trois seeds et les quatre miroirs ; il mesure
  reproductibilité, effet, couverture, variation hors masque et bordure d’eau.
  La validation visuelle Windows d’une silhouette dessinée/importée reste à
  faire avant de fermer ce gate.
- [x] **R51 — calibration Continental provisoire** : le profil dérivé
  `relief compact` est comparé au Continental natif sur la matrice ; le gate
  dur des départs passe sur `54/54` cas et le diagnostic `startable_mass`
  reste souple. Il reste un diagnostic et n’est pas installé comme preset.
- [x] **R52 — composition Continental Custom** : le preset nommé
  `fBm + domain warp + crêtes` remplit une source et deux fusions inspectables
  dans l’onglet Archétype ; le Continental natif et les moteurs Legacy/Upgraded
  restent inchangés. Le rapport de qualification rejoue aussi le gate dur des
  départs sur le chemin Custom basé sur Legacy.
- [x] **DEV8 — archétypes Custom, publiée sur `dev` (base R86)** : providers, fusions,
  masques, previews et relief dérivé Legacy ; profils Classique/Continental,
  état dynamique Personnalisé et synchronisation des sélecteurs. L’utilisateur
  confirme la validation UI Windows, les tests multi-tailles et la résolution
  des anomalies de rivières Custom. Tout le travail ouvert passe en DEV9 ; la
  chronologie détaillée est dans `CHANGELOG.md`.
- [ ] DEV9 — reprendre tous les autres points ouverts du TODO selon leur
  priorité : validité résiduelle des starts, viabilité au-delà des tailles
  testées, polissage et vérifications de release.
- [ ] DEV9 — revalider progressivement terrains, transitions, joueurs,
  ressources, macro-forme, côtes et exports 832–1024 dans l’éditeur/jeu.
## Raffinements différés — DEV9
- [ ] Rendre configurable l’**extension maximale du forçage des bonus de
  départ**. Le réglage devra être exprimé en hexagones au-delà de `D`, avec
  `34` conservé comme valeur par défaut actuelle ; il ne devra pas modifier le
  comportement du forçage désactivé ni l’ordre de recherche par couronnes.
  Ne pas ouvrir ce chantier avant la stabilisation des chantiers DEV9.
- [ ] Ajouter éventuellement un **nombre de zones par minerai** indépendant
  du mode de surface, puis recalculer les surfaces en conséquence.
- [ ] Étendre ultérieurement le bonus rocheux aux familles **gemmes** et
  **soufre**, avec validation de leurs transitions et de leurs quotas.
- [ ] DEV9 : ajouter des tooltips courts aux contrôles minéraux et bonus.

### Reports supplémentaires — DEV9
- [ ] Refaire l’éditeur de masques : plusieurs types de pinceaux ; dessin en
  niveaux de gris au lieu d’un choix noir/blanc ; ajout et suppression
  persistants des masques utilisateur, avec protections pour les masques par
  défaut et un repère visuel distinct pour les masques modifiables.
- [ ] Revoir le placement des terrains/objets hors macro-forme selon le terrain réellement disponible, non selon Continental Legacy ; DEV ultérieure ou au plus tard v2.1.
- [ ] Repenser à terme le rendu des onglets avec des widgets persistants et des
  mises à jour en place (mode, langue, redimensionnement), afin de supprimer
  durablement les reconstructions et les artefacts visuels ; chantier
  compatible avec la consolidation, l’amélioration et le débogage poussés de
  la v2.1, sans lui assigner une version cible. L’essai R18 de staging n’est
  pas la solution de référence.
- [ ] Étudier un réglage indépendant du rayon et de l’espacement des forêts
  globales, seulement si les quotas actuels ne suffisent pas.
- [ ] Étudier des variantes de forme et de répartition des groupes de pierres
  de construction.
- [ ] Étudier une granularité supplémentaire pour le remplissage des poissons
  et les paramètres des lacs bonus, sans modifier les règles natives validées.
- [x] Accélérer exactement la preview macro autour de `_relax_relief` sans changer la génération native ; l’étape indicative de R13 reste séparée et explicitement signalée, sans version cible supplémentaire.

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

- [ ] Auditer et réduire les clignotements visuels lors des changements
  d’options (notamment la langue), ainsi que les artefacts provoqués par les
  redimensionnements d’onglets ou de fenêtres ; privilégier les mises à jour
  en place et les rafraîchissements regroupés.
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
  puis **Small Islands**.
- [ ] Garder ENDGAME pour la fin : générer, importer, inspecter, modifier,
  valider et exporter seulement les données EDM/MAP/SAV comprises.
## Invariants

- Archétype = contexte macro-géographique et futur contrat des masses jouables ;
  Legacy/Upgraded = exécution du relief, hydrologie, contenu, règles, balance,
  ressources et objets. Les montagnes et lacs natifs sont dérivés de ces passes ;
  les bonus rocheux/lacustres sont des zones locales explicites, jamais des objets.
- Legacy : terrain/objets/ressources avant re-seed, puis starts/ville/stock ; Upgraded :
  terrain copié indépendant, contenu global spécifique, minerais v7 no-gap préservés et
  bonus de contenu autour des coordonnées de départ provisoires.
- Aucun aperçu ou asset imaginaire ; SAV lu sans réinvention et copié inchangé.
- IDs inconnus explicitement inconnus ; ne jamais repartir d'une version
  invalidée du générateur.
