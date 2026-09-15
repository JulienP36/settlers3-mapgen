# Changelog

## v2.0 DEV_6_R61 — 2026-09-15 — alignement vertical du bonus lac/rivière

- Le libellé du rayon devient « Rayon de contrôle eau native », avec une aide
  qui précise la mesure depuis la bordure du territoire et le rôle de `0`.
- Tous les contrôles du panneau lac/rivière sont maintenant sur une seule
  colonne : forme, rayon min, rayon max, contrôle eau, rivières puis poissons.
- La génération, le placement, les rivières et les limites de R60 restent
  inchangés.

## v2.0 DEV_6_R60 — 2026-09-15 — compactage de l’interface des bonus

- Le panneau lac/rivière reprend la grille compacte du bonus minéral : quatre
  colonnes, deux commandes par ligne, unités et maxima conservés, aide réduite
  à une seule ligne logique.
- Le libellé « Seuil d’eau native depuis la bordure » devient « Eau native à
  éviter » (et ses traductions équivalentes), avec une aide courte rappelant
  que `0` désactive l’évitement.
- Les listes de forme du lac et du mini-marais sont explicitement regroupées
  avec leur libellé ; aucune logique de génération n’est modifiée.

## v2.0 DEV_6_R59 — 2026-09-14 — seuil et diagnostics du bonus lac/rivière

- Le seuil d’eau native depuis la bordure de territoire est désormais
  désactivé explicitement par `0` ; une valeur positive conserve le filtre de
  proximité. Aucun autre comportement de placement n’est modifié.
- Le bonus lac/rivière expose dans ses métadonnées des compteurs compacts par
  joueur et globaux : candidats essayés/acceptés et causes de refus (eau
  proche, centres, emprise, collisions, forme, embouchure, tracé ou
  transition). Cela permet d’expliquer un shortfall sans ajouter de bruit à
  l’interface.
- R59 ne modifie ni les formes validées, ni les profondeurs, ni le traceur
  natif local des rivières bonus.

## v2.0 DEV_6_R58 — 2026-09-14 — bornes du bonus lac/rivière

- Base exacte R57 ; les formes, profondeurs, deux anneaux de rive et le
  traceur natif local des rivières bonus restent inchangés.
- Le rayon maximal du lac bonus est maintenant `16 HEX6` (valeur par défaut
  conservée à `9`).
- La cible maximale de rivières par lac passe de `8` à `6`. Il s’agit toujours
  d’un plafond souple : les sorties légales disponibles peuvent produire moins.
- Les transitions d’épaisseur `River97–99` restent différées ; R58 ne modifie
  pas la morphologie validée de R57.

## v2.0 DEV_6_R57 — 2026-09-14 — construction native des rivières bonus

- Base exacte R56 ; les formes, profondeurs, poissons et contrôles du lac
  restent inchangés dans cette tranche.
- Suppression du routage vers un champ global `Water/River` : une rivière
  bonus démarre sur une embouchure locale et reprend le système natif
  (filtre 9×9, premier pas, fan HEX6, relief, marqueurs, backtracking et
  limite de longueur). Elle ne cherche plus la mer, un lac ou une rivière
  comme destination.
- Les contacts entre deux plans d’eau restent possibles lorsqu’ils résultent
  accidentellement de la géométrie, comme dans Legacy, mais aucune connexion
  n’est forcée.
- Les systèmes normaux écrivent désormais `River96` sur toute leur longueur ;
  l’alternance artificielle `96/97/98/99` case par case est supprimée.
- Ajout d’une régression ciblée sur la longueur, la connexion HEX6, l’absence
  de cible globale et l’ID natif unique. Validation Windows/éditeur/jeu reste
  à effectuer.

## v2.0 DEV_6_R56 — 2026-09-13 — rivières bonus natives et rives renforcées

- Base exacte R55 ; le code et l’archive R55 restent inchangés.
- Les lacs bonus conservent leurs formes et profondeurs actuelles, mais leur
  emprise de rive suit désormais le standard natif à deux anneaux HEX6.
- Les sorties de rivière sont entièrement retracées par une adaptation de la
  boucle native : éventail de directions, score de relief, virages contrôlés,
  retour arrière borné et arrêt au premier contact avec l’eau/une rivière
  existante. Les routes restent connectées au cœur du lac et ne remplacent
  jamais eau, rives, terrains incompatibles, objets ou ressources.
- La distance vers l’eau guide la recherche sans redevenir un chemin direct ;
  un repli local borné conserve un manque explicite si aucune route légale
  n’existe. Les poissons restent limités aux cellules d’eau du cœur.
- Ajout de régressions sur les deux anneaux de rive, la connexion HEX6, la
  courbure des routes et l’arrêt avant l’eau. Validation Windows/éditeur/jeu
  encore requise avant clôture de DEV6.

## v2.0 DEV_6_R55 — 2026-09-13 — bonus lac/rivière natifs

- Base exacte R54 ; les zones minérales, leur panneau persistant et les sprites
  restent inchangés.
- Le bonus lac propose désormais `Native` (forme arrondie et variable, bornée
  par le rayon) et `Hexagone` (compatibilité explicite). La rive est dérivée de
  l’emprise réelle et les niveaux Water0..Water7 progressent depuis son bord.
- Les rivières bonus recherchent toujours une sortie légale vers l’eau native,
  sans collision ni écrasement, avec une légère variation de direction inspirée
  de la boucle native. Les poissons restent limités au cœur en eau.
- La protection eau de la tour (`20 HEX6` par défaut) couvre désormais le lac,
  sa rive et ses rivières même quand le forçage de distance est désactivé.
- Ajout des tests de forme bornée/variable, de compatibilité hexagonale et de
  profondeur hydrologique. Validation utilisateur Windows/éditeur/jeu encore
  ouverte ; aucun push ni release.

## v2.0 DEV_6_R54 — 2026-09-13 — ordre du panneau et surfaces persistantes

- Base exacte R53 ; la compensation et la forme organique actuelles restent
  inchangées.
- Le panneau minéral suit maintenant l’ordre `Forme → Répartition → Rayon
  commun → Total`, sans créer une séparation supplémentaire avec la matrice.
- Un état partagé conserve les valeurs visibles lors d’un changement de
  répartition : le rayon égal recalcule les cœurs et le total, le total prorata
  recalcule les cœurs et affiche le rayon HEX6 équivalent le plus proche, et un
  passage en mode égal reprend ces valeurs plutôt qu’un ancien profil.
- Un total qui ne correspond pas exactement à trois disques HEX6 est conservé
  en prorata/personnalisé ; le mode égal le canonise ensuite sur le rayon
  équivalent le plus proche, de façon déterministe.

## v2.0 DEV_6_R53 — 2026-09-13 — variation organique et conservation UI

- La forme organique des zones minérales évalue désormais sa croissance dans
  l’espace de projection parallélogramme, afin d’éviter l’étirement visuel.
- Des variations douces supplémentaires différencient les contours sans bruit
  cellule par cellule, sans trou et sans modifier la surface demandée.
- Le contrôle « Répartition » passe sur la ligne suivante ; rayon, total et
  cœurs dérivés sont mémorisés par mode pour ne pas être perdus lors d’un
  changement de répartition.
- Base R52 exacte ; le bonus lac avec poissons/rivière reste inchangé.

## v2.0 DEV_6_R52 — 2026-09-13 — candidate de test

- Reprise fonctionnelle exacte de R51 avec l’identifiant de candidate et
  l’archive corrigés pour la validation Windows ; aucune règle de génération
  supplémentaire n’est introduite.

## v2.0 DEV_6_R51 — 2026-09-13 — géométrie organique et lisibilité

- Base exacte R50 ; le bonus lac/poissons/rivière reste inchangé.
- La forme `Organique` est maintenant construite par croissance HEX6 à priorité
  elliptique douce, comme les gisements Upgraded : contour arrondi, ondulations
  variables, surface exacte, connexion garantie et aucun trou.
- Les listes de sélection restent en lecture seule, les contrôles contextuels
  inutilisés restent désactivés et les unités `HEX6`/`cases` sont rapprochées
  des saisies du panneau minéral.
- Les sprites charbon/fer/or sont grisées dans les contrôles globaux ou bonus
  lorsque leur famille est inactive.
- Le rayon maximal des marais bonus passe à `16 HEX6`. Chaque cœur minéral est
  borné à `1–820` cases (`820` est le plafond arrondi couvrant le disque HEX6
  de rayon 16) ; le total prorata devient dynamique à `820/1 640/2 460` selon
  le nombre de familles actives.
- Validation utilisateur Windows/éditeur/jeu encore requise ; aucun push ni
  release.

## v2.0 DEV_6_R50 — 2026-09-12 — finitions des zones minérales

- Base exacte R49 ; le bonus lac/poissons/rivière n’est pas modifié dans cette
  tranche.
- Les trois lignes charbon, fer et or affichent les sprites 16×16 fournis dans
  `data/mineral_icons/`.
- La forme `Organique` perturbe maintenant réellement le contour par échanges
  de cellules de bord, tout en conservant une emprise connexe, sans trou et de
  surface exacte.
- Le mode égal expose un seul rayon commun (`1–16 HEX6`) ; les modes prorata et
  personnalisé gardent leurs surfaces dédiées. Les cœurs sont bornés à `1–1 000`
  cases par minerai et `1–3 000` au total.
- Validation technique et validation Windows/éditeur/jeu à produire ; aucun
  push ni release.

## v2.0 DEV_6_R49 — 2026-09-12 — panneau des zones minérales compacté

- Base exacte R48 ; aucune règle de génération ni valeur de sortie n’est
  modifiée.
- Le panneau des zones minérales regroupe forme et mode sur une ligne, puis
  présente les familles dans une grille compacte `Minerai / Cœur / Moyenne`.
- Les champs sont maintenant contextuels : rayons en mode égal, surface totale
  en mode prorata, surfaces par minerai en mode personnalisé ; les champs de
  quantité restent actifs uniquement pour les familles cochées.
- Un rappel indique que les parts du mode prorata viennent de la section
  globale des minerais. Validation Windows/éditeur/jeu encore à effectuer ;
  aucun push ni release.

## v2.0 DEV_6_R48 — 2026-09-12 — zones minérales configurables

- Base R47 conservée ; le mode Hexagone et les rayons historiques restent
  compatibles.
- Ajout d’une forme `Organique compacte`, de cœurs toujours 100 % minerai et
  de trois répartitions de surface : égale, prorata des parts globales actives
  et personnalisée par minerai.
- Chaque cœur peut hériter de la moyenne globale de son minerai ou recevoir une
  moyenne dédiée ; une emprise impossible est omise avec un shortfall explicite.
- TODO différé : nombre de zones indépendant et extension aux gemmes/soufre.
- Validation technique et validation utilisateur R48 à terminer ; aucun push ni
  release.

## v2.0 DEV_6_R47 — 2026-09-12 — forçage progressif des bonus

- Base exacte R46 ; validation utilisateur des forêts, pierres et marais enregistrée.
- Mode forcé : bande locale puis couronnes D+3 à D+34, première bande avec
  placement complet légal, hasard au sein d’une couronne uniquement.
- Forêts et pierres : plan avant écriture, espacements et empreintes respectés ;
  protection des tours sur toute l’emprise, y compris pour lac et rivière.
- Replis légaux avec manques explicites. Mode OFF inchangé.
- Validation : 414 tests vérifiés (411 suite complète + trois contrôles
  documentaires/version corrigés et repassés), 16 sorties OFF identiques à
  R46, self-test source/smoke PASS.
- Zones minérales et lac restent à valider ; DEV6 ouverte, aucun push/release.


## v2.0 DEV_6_R46 — 2026-09-11 — formes natives indépendantes des marais bonus

- Repart exclusivement de R45 et conserve le même plan natif
  brosse/extension/érosion pour la forme `Native`.
- Chaque start génère désormais sa propre empreinte native avec le PRNG de la
  génération ; les quatre marais bonus ne réutilisent donc plus la même forme.
  Les collisions, transitions, replis légaux et le rayon `1–20` restent
  inchangés ; la forme `Hexagone` n'est pas modifiée.
- Le chemin sans bonus reste inchangé. Validation R46 : `401 passed`, self-test
  source et smoke-test réussis ; les 16 comparaisons de sorties sans bonus
  R45/R46 sont identiques sur Legacy/Upgraded, deux tailles, deux seeds et
  deux miroirs. Les quatre configurations actives Legacy/Upgraded en
  `256×256` et `768×768` passent les validateurs durs. R46 reste une candidate
  locale ; aucun push, incrément DEV ou release n'est effectué.

## v2.0 DEV_6_R45 — 2026-09-11 — hitboxes globales et forme native des marais

- Repart exclusivement de R44. Le chemin sans bonus reste hors de la nouvelle
  collision active ; les routes natives Legacy/Upgraded sans bonus conservent
  donc leur sortie précédente.
- Quand un bonus est actif, le halo est maintenant alimenté par les objets
  effectivement écrits pour toutes les familles : arbres adultes, pousses,
  pierres et décorations, y compris la passe native globale Legacy. Les
  empreintes réelles des Building Stones restent protégées. Aucun emplacement
  vide n'est réservé et aucun objet n'est généré puis supprimé.
- La forme `Native` des marais bonus sélectionne désormais un composant issu
  du même plan natif brosse/extension/érosion que les marais globaux, en
  privilégiant un composant complet dans le rayon demandé ; le découpage par
  rayon ne devient qu'un repli légal. La forme `Hexagone` et la limite de test
  `1–20` sont conservées.
- Validation R45 : `400 passed`, compilation, self-test source et smoke-test
  réussis ; les 16 comparaisons de sorties sans bonus R44/R45 sont identiques
  sur Legacy/Upgraded, deux tailles, deux seeds et deux miroirs. Les cartes
  actives `256×256` et `768×768` passent les validateurs durs. R45 reste une
  candidate locale ; aucun push, incrément DEV ou release n’est effectué.

## v2.0 DEV_6_R44 — 2026-09-11 — placement des adultes et hitboxes des bonus

- Repart exclusivement de R43 et conserve le chemin sans bonus inchangé ; les
  marais bonus et leur algorithme ne sont pas modifiés dans cette tranche.
- Les forêts bonus calculent d’abord le noyau minimal des arbres adultes, posent
  les adultes en premier, puis limitent les pousses à la couronne extérieure.
  Les deux populations gardent le même espacement `3 HEX6` et les zones de
  recherche vides ne sont jamais réservées ni nettoyées après coup.
- Le halo de collision est maintenant dérivé des écritures réelles des bonus :
  ancres d’arbres, empreinte complète des Building Stones et objets déjà écrits.
  Les passes globales Legacy et Upgraded (arbres, pierres, décorations et
  familles natives) ne peuvent donc plus entrer dans les hitboxes bonus.
- Validation R44 : `400 passed`, compilations, self-test et smoke-test réussis ;
  16 sorties sans bonus R43/R44 restent identiques sur Legacy/Upgraded, deux
  tailles, deux seeds et deux miroirs. Les cartes actives `256×256` et `768×768`
  passent les validateurs durs.
- R44 reste une candidate locale ; aucun push, incrément DEV ou release n’est
  effectué.

## v2.0 DEV_6_R43 — 2026-09-10 — ordre prioritaire des bonus actifs

- Repart exclusivement de R42. Le chemin public Legacy/Upgraded sans bonus
  conserve le passage natif existant ; il ne demande aucune phase différée et
  ses couches de carte restent byte-identiques aux références R42.
- Lorsqu’au moins un bonus de départ est actif, le pipeline est découpé autour
  des écritures réelles : terrain de l’archétype → départs → bonus de terrain →
  terrains globaux non liés à l’archétype → objets bonus → objets globaux.
  Aucun objet bonus n’est posé puis supprimé ; les masques transmis aux passes
  globales ne couvrent que les cellules déjà écrites ou les emprises réelles.
- Le même ordre est raccordé aux routes Custom dérivées de Legacy et
  d’Upgraded. Les ressources bonus restent hors des cibles globales et les
  supports `18/19/24` restent compatibles lorsque le switch herbe est actif.
- R43 reste une candidate locale ; aucun push, incrément DEV ou release n’est
  effectué.
- Validation R43 : `399 passed`, self-test source et smoke-test réussis ; les
  sorties sans bonus restent byte-identiques à R42 sur les contrôles Legacy /
  Upgraded.

## v2.0 DEV_6_R42 — 2026-09-10 — correction des formes du bonus mini-marais

- Repart exclusivement de R41. Le rayon du mini-marais est maintenant borné à
  `1–20` pour les tests ; la forme `Hexagone` utilise réellement ce rayon.
- La forme `Native` réutilise le plan natif global des marais
  (brossage/expansion/érosion/transitions) dans une empreinte locale, au lieu
  d’ajouter un anneau géométrique artificiel.
- R42 reste une candidate locale ; aucun push, incrément DEV ou release n’est
  effectué.

## v2.0 DEV_6_R41 — 2026-09-10 — forme et rayon du bonus mini-marais

- Repart exclusivement de R40. Le bonus mini-marais remplace le nombre libre
  de cases par un rayon borné et dérive automatiquement son étendue.
- Ajoute une liste de formes extensible avec `Native` et `Hexagone`, sans
  modifier les bonus forêts, pierres, minerais ou lac.
- Conserve les profils Legacy/Upgraded comme presets Custom, les bonus par
  joueur hors quotas globaux et le repli légal en cas de terrain indisponible.
- R41 reste une candidate locale ; aucun push, incrément DEV ou release n’est
  effectué.

## v2.0 DEV_6_R40 — 2026-09-10 — placement direct des bonus et quotas à zéro

- Repart exclusivement de R39. Les familles d’objets globaux réellement
  modifiées par Custom sont désactivées dans le passage natif avant tout
  placement ; elles ne sont plus posées puis supprimées après les bonus.
- Supprime le nettoyage postérieur des zones de bonus et le masque partagé qui
  protégeait des cases vides. Chaque bonus vérifie désormais la couche d’objets
  et les emprises déjà écrites au moment de choisir une case légale.
- Corrige le cas Legacy « arbres globaux à `0 %` + bonus pierres seul » : aucun
  arbre ne peut survivre dans la zone des pierres, tandis que les ancres de
  départ restent additionnelles et hors quota global. Les mini-marais refusent
  également toute case portant déjà un objet ou une ressource.
- R40 est une candidate locale construite depuis R39 ; aucun push, incrément
  DEV ou release n’est effectué.

## v2.0 DEV_6_R39 — 2026-09-10 — correction des pierres à zéro et du stock bonus

- Repart exclusivement de R38. Lorsque les bonus de départ sont désactivés et
  que le taux global des pierres vaut `0 %`, Legacy comme Upgraded ne produisent
  plus aucun objet pierre, y compris dans l’empreinte technique d’un départ.
- Le stock moyen des rochers bonus utilise maintenant exactement la même loi
  `full_range_mean_tilt` que le stock global (`1–12`, moyenne réglable), pour
  Legacy comme pour Upgraded. Le rayon étendu n’est pas modifié dans R39.
- Validation ciblée : `6 passed`. R39 reste une candidate locale ; aucun push,
  incrément DEV ou release n’est effectué.

## v2.0 DEV_6_R38 — 2026-09-10 — route Custom commune et bonus protégés

- Repart de la candidate canonique R37 et corrige le switch « objets
  compatibles avec l’herbe » : les bonus déjà réservés ne sont plus effacés
  par le remplacement des objets globaux, et les cinq bonus peuvent utiliser
  les terrains `16`, `18`, `19` et `24` lorsque le switch est actif.
- Fait passer les sélections publiques Legacy et Upgraded par le même contrat
  de configuration Custom, sous forme de presets spécifiques ; les moteurs
  internes protégés restent séparés. Les bonus sont désactivés par défaut sur
  ces presets et une configuration explicite peut les activer sans changer de
  moteur de base. Le même principe est documenté pour les futurs archétypes.
- Ajoute l’option globale « Forcer le placement à une distance étendue si
  nécessaire » pour les cinq bonus. Sans cette option, chaque bonus reste dans
  sa couronne locale ; avec elle, il essaie des couronnes plus éloignées et
  signale l’extension réellement utilisée dans ses métadonnées.
- Corrige le pont Legacy vers les routines de bonus et sécurise les transitions
  lorsque un marais bonus utilise une variante d’herbe ou lorsqu’une rive de lac
  serait voisine d’une transition rocheuse ; les repliements légaux sont alors
  conservés sans invalider la carte.
- Validation finale locale de la candidate : `393 passed`.
- R38 reste une candidate locale : aucun push, incrément DEV ou release n’est
  effectué.

## v2.0 DEV_6_R37 — 2026-09-10 — forêt et pierres de départ

- Repart exclusivement de la candidate canonique R36 et conserve toutes ses
  fonctions, dont l’autorisation optionnelle des objets compatibles avec
  l’herbe sur les terrains `18`, `19` et `24` uniquement.
- Borne à `100` le nombre d’arbres par forêt globale ainsi que les quantités
  d’arbres adultes et de pousses du bonus par joueur. Le défaut reste `30`
  adultes puis `20` pousses, tous espacés d’au moins `3 HEX6` ; les plantations
  utilisent désormais la même couleur claire sur la carte et les graphiques.
- Porte les pierres de départ à `15` ancres par joueur par défaut, maximum `50`,
  avec une moyenne de `10` unités par pierre (`1–12`, pas `0,5`). Le stock est
  dérivé des deux valeurs visibles et le rayon est calculé depuis le nombre
  d’ancres, l’espacement et l’emprise native de sept cases ; les anciens rayons
  sérialisés sont ignorés.
- Place la catégorie Bonus en premier et garde l’interrupteur de chaque bonus
  au début de son propre panneau. Les cinq interrupteurs sont raccordés dans
  les Custom basés sur Legacy comme sur Upgraded, sans changer le moteur choisi.
- Le forçage à une distance plus grande reste volontairement reporté. R37 est
  une candidate locale sans push, promotion DEV ni release.

## v2.0 DEV_6_R36 — 2026-09-09 — correction du bonus forêt de départ

- Rend le bonus forêt utilisable dans un Custom basé sur Legacy comme dans un
  Custom basé sur Upgraded. Les presets Legacy/Upgraded exposés par l’éditeur
  commencent désormais avec tous les bonus de départ désactivés ; chaque bonus
  possède son interrupteur au début de son panneau.
- Remplace le défaut de forêt par `30` arbres adultes et `20` pousses par joueur.
  Les adultes sont placés en premier, puis les pousses, et tous respectent la
  distance commune de `3 HEX6`. Le rayon minimal est dérivé de ces quantités et
  de cet espacement ; les anciens champs `radius_min`/`radius_max` de forêt sont
  ignorés et aucune limite maximale arbitraire n’est ajoutée.
- Ajoute le switch d’objets compatibles avec l’herbe pour les terrains `18`,
  `19` et `24` uniquement ; le terrain rocheux `34` reste exclu. Les objets de
  départ restent additionnels et hors quotas globaux.
- R36 est une candidate locale : aucun push, incrément DEV ou release n’est
  effectué à cette étape.

## v2.0 DEV_6_R35 — 2026-09-09 — intégration complète des bonus de départ

- Branche réellement les cinq bonus Upgraded dans la section Custom : forêt,
  pierres, mini-marais, zones rocheuses séparées charbon/fer/or et lac bonus
  avec poissons/rivières. Les contrôles ne sont plus de simples cases : les
  quantités, tailles, distance commune et paramètres hydrologiques sont
  normalisés puis consommés par le moteur.
- Expose les valeurs convenues : `41` arbres adultes et `21` pousses par joueur,
  `5` pierres pour environ `53` unités, `19` cases de mini-marais, rayon
  réglable des zones rocheuses/lacs, seuil d’eau native `150 HEX6`, taux de
  poissons du lac et cible de rivières. Les pierres gardent le pas `0,5` et la
  plage `1–12`; les zones rocheuses sont pleines sur leur cœur et reprennent
  la moyenne globale des minerais.
- Conserve la distance `0` au bord du territoire, les formes natives pour les
  bonus compatibles et l’hexagone dessiné pour les zones rocheuses/lacustres.
  Les réservations empêchent les chevauchements entre bonus et les quotas
  globaux, les rivières/eaux natives ne sont jamais écrasées, et un lac sans
  sortie légale est omis. Une cible de plusieurs rivières peut légalement
  produire moins si le tracé disponible ne permet pas de faire mieux.
- Remplace l’ancien contrôle de stock total implicite par un stock dérivé de
  `ancres × moyenne par pierre`, arrondi à l’unité ; les paramètres de moyenne
  des minerais et poissons restent ceux des sections globales.
- R35 reste une candidate locale suffixée : aucun push ni promotion DEV6 n’est
  effectué automatiquement.

## v2.0 DEV_6_R34 — 2026-09-09 — bonus de départ Upgraded et section Rivières Custom

- Supprime l'ancien `config/upgraded_768_v1.json`, qui appartenait à une
  version obsolète et non fonctionnelle du moteur ; le profil Upgraded actif
  est désormais défini par le code R34 et le fichier JSON n'est plus une
  dépendance d'exécution.
- Intègre les cinq bonus de départ Upgraded : forêt, pierres, mini-marais,
  zones rocheuses indépendantes pour charbon/fer/or, et mini-lac avec poissons
  et rivière. Les bonus utilisent une distance paramétrable depuis la bordure
  du territoire (`150 HEX6` par défaut), des réservations séparées, des
  replis légaux et des quotas distincts des quotas globaux.
- Les zones rocheuses peignent uniquement le terrain et réutilisent les
  transitions natives ; les lacs bonus évitent l'eau existante lorsque celle-ci
  est suffisamment proche, protègent les rivières natives et ne sont conservés
  que lorsqu'une rivière légale peut être tracée.
- Ajoute la section Custom **Rivières** avec un taux global borné à `0–500 %`.
- À `100 %`, la boucle native reste inchangée : `4 × taille²` tentatives,
  seuil PRNG, marche HEX6, connexions à l’eau, longueurs et nettoyage.
- Les autres valeurs modifient seulement le seuil d’acceptation des tentatives
  natives ; `0 %` ne produit aucune rivière et ne désactive aucun validateur.
- Validation : **374 tests réussis**, autotest source/extrait et smoke-test PASS ;
  archive extraite et ré-emballée à l’identique.

## v2.0 DEV_6_R33 — 2026-09-09 — mise à l’échelle native directe des terrains

- Corrige R32 : les taux autres que `100 %` passent maintenant directement par
  les mêmes brosses, expansions et érosions que la génération existante ; le
  générateur ne construit plus de liste séparée de zones candidates.
- `100 %` conserve exactement le chemin natif ; les autres valeurs modifient
  seulement le nombre de sondes de brossage et d’expansions, ce qui conserve
  les grandes formes natives, leur variation de taille et les fusions légales.
- Le contrôle de l’épaisseur côtière depuis un Custom dérivé de Legacy reste
  corrigé.
- Validation : **369 tests réussis**, autotest source et smoke-test PASS ; archive
  extraite, contrôlée et ré-emballée à l’identique.

## v2.0 DEV_6_R32 — 2026-09-09 — mise à l’échelle des terrains par recettes natives

- Remplace la création de formes ad hoc par la réutilisation des recettes natives
  de brossage, d’expansion, d’érosion et de transitions pour la Boue, le Désert,
  l’Herbe sèche, les Détails décoratifs et le Marais.
- À `100 %`, le résultat natif est conservé ; sous `100 %`, seules des zones
  natives complètes sont retenues ; au-dessus, des zones natives supplémentaires
  sont réservées avant peinture pour que `500 %` ne puisse pas retirer une zone
  obtenue à `200 %`. Les capacités légales insuffisantes sont signalées dans les
  diagnostics au lieu de produire une transition illégale.
- Corrige l’état de l’input d’épaisseur côtière après dérivation d’un Custom
  depuis Legacy : l’option redevient utilisable dès que « Près des côtes » est
  activé.
- Validation : **369 tests réussis**, autotest source et smoke-test PASS ; archive
  extraite, contrôlée et ré-emballée à l’identique.

## v2.0 DEV_6_R31 — 2026-09-09 — zones de terrains légales et extensibles

- Remplace l’agrandissement brut des familles de terrains par une génération
  en zones HEX6 cohérentes : un taux supérieur à `100 %` ajoute prioritairement
  des zones distinctes, puis agrandit modérément les zones existantes.
- Autorise la fusion de zones d’une même famille, mais interdit tout nouveau
  contact avec une autre famille, l’eau, une rivière, un relief ou un détail.
- Recalcule les identifiants de transition depuis la profondeur HEX6 de chaque
  masque et ajoute un contrôle strict des transitions illégales ; les halos de
  départ et les mini-marais de secours restent protégés.
- Validation : **366 tests réussis** ; l’EDM R30 équivalent passe de 6 074
  contacts illégaux à zéro avec la même règle de contrôle.

## v2.0 DEV_6_R30 — 2026-09-09 — correction du créneau Boue Custom

- Réserve `0 %` aux terrains désactivés ; une famille activée commence à `1 %`.
- Conserve le profil Upgraded natif sans boue avec son paramètre nul, tout en
  permettant à Custom Upgraded d’activer le même plan de génération que Legacy.
- Ajoute les validations de non-régression correspondantes sans modifier les
  profils protégés ni la future refonte générale des taux de terrains.

## v2.0 DEV_6_R29 — 2026-09-09 — section Terrains et sprites Minerais

- Ajoute la section Custom **Terrains** : activation et taux `0–500 %` pour la
  Boue, le Désert, l’Herbe sèche, les Détails décoratifs et le Marais.
- Applique ces taux avant les objets, avec `100 %` comme comportement natif et
  la neutralisation effective des décorations dépendantes lorsqu’un terrain est
  désactivé. Les lacs, rivières, neige et relief rocheux restent hors de cette
  section ; les formes de terrain restent natives.
- Intègre les cinq sprites de minerais fournis en `16×16` dans les tableaux
  Répartition et Ressource moyenne, sans changer la hauteur des lignes ; la
  colonne vide de la ressource moyenne est supprimée.
- Porte la calibration des récifs à `20` pour 768×768, y compris pour la
  référence utilisée par un Custom basé sur Legacy.

## v2.0 DEV_6_R28 — 2026-09-08 — récifs Custom Legacy

- Corrige le taux de récifs dans un Custom basé sur Legacy : la valeur native
  0 ne bloque plus les taux supérieurs à 0.
- Utilise la calibration Upgraded de 11 récifs à 768×768 comme référence,
  avec mise à l’échelle selon la taille de carte.
- Le validateur autorise uniquement les récifs sur l’eau ; les autres objets
  restent interdits sur l’eau.

## v2.0 DEV_6_R27 — 2026-09-08 — sous-familles et mise en page Décorations

- Réserve un emplacement d’icône pixel art de `16×16` dans chaque ligne de
  Décorations, sans modifier la hauteur des champs.
- Affiche les sous-familles dans le graphique **Familles d’objets**.
- Aligne les récifs sur la sémantique des profils : `0 %` en Legacy et `100 %`
  en Upgraded.

## v2.0 DEV_6_R26 — 2026-09-08 — section Custom Décorations

- Ajoute la section **Décorations** avec un taux d’apparition indépendant de
  `0–500 %` pour chaque famille statique déjà reconnue par le générateur.
- Conserve `100 %` comme comportement du profil sélectionné ; les familles,
  terrains compatibles, identifiants et règles de collision restent internes.
- Raccorde les taux aux passes Legacy et Upgraded, avec les récifs traités
  séparément comme famille spécifique au profil Upgraded.
- Ajoute les traductions et les tests de génération, sans modifier les profils
  protégés ni les bonus de départ.

## v2.0 DEV_6_R25 — 2026-09-08 — mise en page Custom et molette ciblée

- Les sections de l’onglet Générateur utilisent leur largeur naturelle sans
  colonnes artificiellement étirées.
- La méthode de gisement est placée immédiatement à côté de son libellé.
- Les tableaux `Répartition` et `Ressource moyenne` alignent leurs champs,
  unités, noms de ressources et maxima dans le même ordre.
- La molette continue de modifier les Spinbox/Combobox sous le curseur et ne
  fait défiler l’onglet que sur les autres zones.

## v2.0 DEV_6_R24 — 2026-09-08 — resserrement de la section Minerais

- Les colonnes `Répartition` et `Ressource moyenne` utilisent désormais leur
  largeur naturelle afin de supprimer l’espace central inutile.

## v2.0 DEV_6_R23 — 2026-09-08 — hauteur du bouton de seed

- Le sprite de dé raffiné remplace R22.
- Le remplissage interne du bouton est supprimé afin de conserver la même
  hauteur que les boutons voisins.

## v2.0 DEV_6_R22 — 2026-09-08 — correction de démarrage du sprite

- Le sprite de dé est chargé au début de la construction de l’interface,
  avant la création des boutons qui l’utilisent.

## v2.0 DEV_6_R21 — 2026-09-08 — sprite du dé de seed

- Le sprite PNG 24×24 fourni remplace le caractère Unicode sur tous les boutons
  de randomisation des seeds, y compris dans la fenêtre de génération par lot.

## v2.0 DEV_6_R20 — 2026-09-08 — comportement des pierres épuisées

- Le nombre de piles épuisées est maintenant tiré aléatoirement à `1,125 %`
  des piles globales, avec les pierres bonus de départ exclues.

## v2.0 DEV_6_R19 — 2026-09-07 — moyenne du stock des pierres

- Le champ **Stock moyen par pierre** accepte maintenant les pas de `0,5`.
- Les piles personnalisées utilisent toute la plage active `1–12` : `6,5` donne
  une répartition uniforme, puis les valeurs intermédiaires déplacent
  progressivement le poids vers les petites ou grandes piles. Chaque état garde
  une probabilité non nulle, sans imposer une occurrence minimale ; `1` et `12`
  restent les deux extrêmes déterministes.
- Les piles épuisées restent hors moyenne ; les bonus de départ restent hors du
  quota global et sont conservés comme population distincte dans les mesures.
- Les valeurs natives restent inchangées lorsque le réglage Custom n'est pas
  modifié ; validation complète à **353 tests**.

## v2.0 DEV_6_R18 — 2026-09-07 — pierres de construction Custom

- Remplace le « stock récoltable global » par un stock moyen par pierre,
  borné à `1–12` comme les quantités natives.
- Structure les groupes comme les forêts : activation, part du quota, nombre
  moyen de pierres par groupe et variation du nombre par groupe.
- Réduit l’aide de section à une ligne et conserve la migration des anciennes
  configurations R17 vers la nouvelle structure.

## v2.0 DEV_6_R17 — 2026-09-05 — pierres de construction Custom

- Quota global et stock récoltable explicités, groupes activables sans perdre
  leur pourcentage ; valeurs initiales dérivées du profil sélectionné.
- Distance arbre↔pierre minimale 3 HEX6 dans les deux placeurs, emprise active
  de sept cases ; les pierres épuisées ne laissent plus de blocage périphérique.
- Saturation du placement Legacy Custom rapportée sans pose illégale ni arrêt.
- Bonus de départ indépendants ; candidate locale à tester, aucun push.

## v2.0 DEV_6_R16 — 2026-09-05 — bandeau sombre au démarrage

- Réapplique la palette native du bandeau de titre lorsque la fenêtre
  principale est effectivement affichée, afin que le thème sombre chargé au
  démarrage ne laisse plus un bandeau blanc.
- Conserve le rafraîchissement événementiel des fenêtres secondaires et le
  comportement du changement de thème clair/sombre.
- Ne modifie aucune règle de génération, aucun quota ni aucune donnée native
  protégée.

## v2.0 DEV_6_R15 — 2026-09-05 — défilement et redimensionnement

- Corrige la voie de déplacement des barres de défilement des onglets : les
  positions intermédiaires sont regroupées à 16 ms et la dernière position est
  forcée à la libération, ce qui supprime les traînées dues aux reconstructions
  trop rapprochées des contrôles intégrés.
- Conserve le défilement à la molette immédiat et indépendant de cette cadence.
- Réduit à 24 ms l’attente de stabilisation des redimensionnements de la carte,
  des graphiques et de la mise en page des onglets.
- Ne modifie aucune règle de génération, aucun quota ni aucune donnée native
  protégée.

## v2.0 DEV_6_R14 — 2026-09-05 — fluidité de l’interface

- Diffère le redimensionnement coûteux de l’aperçu jusqu’à la stabilisation de
  la fenêtre et repositionne immédiatement l’image déjà affichée.
- Regroupe les recalculs des graphiques et des onglets défilants, en réutilisant
  les éléments de dessin existants.
- Évite de reconstruire l’éditeur Custom pour un changement de taille, de
  joueurs ou de graine sans modification de ses paramètres.
- Remplace `pool` par **quota** ou **réserve** dans les libellés français.

## v2.0 DEV_6_R13 — 2026-09-04 — sections Custom arbres et rochers

- Améliore l’ergonomie de l’éditeur Custom : la molette agit sur toute la
  surface des onglets, sans délai perceptible, et le scroll de Générateur est
  conservé lors d’un changement de mode. Les sections se répartissent mieux
  en colonnes ; unités et plafonds restent près des champs.
- Porte les quotas globaux des arbres de base et des palmiers à `500 %` dans
  l’éditeur, la normalisation et les deux moteurs Custom ; les autres plafonds
  restent inchangés.
- Ajoute la section sémantique **Arbres** dans l’éditeur Custom : quota global
  relatif des arbres de base, pousses acceptées avec réserve globale ou quota
  séparé et placement, forêts avec part/moyenne/variation, et quota maximal
  relatif des palmiers. Le preset Upgraded conserve exactement son défaut à
  `30 %` en forêts ; Legacy reste sans forêts ni pousses par défaut.
- Conserve la section **Pierres de construction** candidate déjà raccordée,
  sans modifier ses invariants d’emprise et de stock.
- Raccorde ces contrôles au contenu Upgraded sans modifier les profils protégés ;
  les quotas de départ restent séparés et les invariants d’IDs, d’espacement,
  d’emprise de sept cases et de quantités restent internes.
- Raccorde les mêmes réglages au Custom basé sur Legacy. Une famille Legacy
  inchangée conserve sa sortie native ; une famille modifiée est replacée par
  le même placeur légal avec diagnostics et états épuisés.
- Étend les tests, traductions, diagnostics et le contrôle d’intégrité de
  l’archive source.

## v2.0 DEV_6_R11 — 2026-09-04 — nettoyage des références et des tests

- Ajoute `references/REFERENCE_INDEX.md` et la matrice courante afin de
  distinguer sans ambiguïté l’état v2.0 actif des audits et essais historiques.
- Archive les anciens snapshots, la matrice Upgraded v1.2, la validation v1.7
  et les essais miniers remplacés ; les liens actifs pointent désormais vers
  les documents courants.
- Retire des tests actifs les trois sondes SAV dépendant de chemins locaux
  absents et supprime l’étape fantôme `hydrology.micro_water_cleanup`.
- Remplace les identifiants de cache par défaut hérités de v1.5 par des espaces
  de noms neutres ; les fichiers de compatibilité protégés restent inchangés.
- Ne modifie pas la génération Arbres/Rochers : les prochaines sections Custom
  restent prévues dans cet ordre.

## v2.0 DEV_6_R10 — 2026-09-04 — corrections Custom et liaison graphique

- Corrige **Pixels aléatoires** : la couche ressources de `MapState` est une
  vue entrelacée ; l’écriture passe désormais par son itérateur afin que les
  pixels choisis atteignent bien la carte et l’export.
- Empêche la reconstruction complète de l’onglet Custom à chaque changement
  de paramètre. La première modification entre toujours en Custom, puis les
  éditions suivantes conservent les contrôles et le focus.
- Active **Lier à la vue** par défaut dans les graphiques.

## v2.0 DEV_6_R9 — 2026-09-04 — pixels aléatoires et répartition Upgraded

- Ajoute la troisième méthode de gisement **Pixels aléatoires** dans Custom :
  les cases compatibles sont choisies uniformément en une seule passe, sans
  forme, rayon, regroupement ni recouvrement artificiel ; les quotas globaux et
  par minerai restent exacts.
- Met à jour la répartition minérale par défaut du générateur Upgraded en
  charbon 52,5 %, fer 22,5 %, or 15 %, gemmes 5 % et souffre 5 %. Le preset
  Custom Upgraded dérive ces mêmes valeurs afin de préserver la parité exacte.
- Sécurise l’allocation des pierres de construction : lorsque la distribution
  le permet, les états de quantité 1 à 12 restent tous représentés même après
  l’ajustement vers le stock total demandé.

## v2.0 DEV_6_R8 — 2026-09-04 — restauration exacte de R17 et quota final

- Confirme et récupère la dernière version procédurale Legacy avant le portage
  natif du jeu : `v2.0 DEV_1_R17`, commit `90175ee`.
- Remplace le placeur Custom Legacy intermédiaire par les zones HEX6 aléatoires
  de rayons 3/4/5, le remplissage uniforme propre à chaque zone, la
  compensation des recouvrements et l’ordre charbon → fer → or → gemmes →
  souffre de R17.
- Corrige le sens du taux d’occupation : le nombre final de cases minérales
  correspond désormais exactement à la cible calculée sur les terrains
  compatibles, y compris à 100 %, malgré les recouvrements historiques.
- Le moteur Legacy natif décompilé, le moteur Upgraded et les profils intégrés
  protégés restent inchangés.

## v2.0 DEV_6_R7 — 2026-09-04 — retour du placement Legacy historique

- Remplace l’approximation Custom Legacy par la mécanique historique
  pré-décompilation : zones HEX6 indépendantes de rayons 3/4/5, remplissage
  variable dépendant de la taille, sélection radiale bruitée et recouvrement
  séquentiel charbon → fer → or → gemmes → souffre.
- Réintroduit les multiplicateurs de peinture historiques pour compenser les
  recouvrements des familles précoces, tout en conservant le quota global et
  les quantités Legacy moyennes à 8.
- Le Legacy natif décompilé reste inchangé ; cette mécanique ne concerne que
  l’algorithme Legacy sélectionné dans Custom.

## v2.0 DEV_6_R6 — 2026-09-04 — parité minérale Legacy/Custom

- Préserve directement les octets minéraux produits par le cœur Legacy natif
  lorsque la section Minerais Custom correspond exactement au preset Legacy.
- Évite ainsi de rejouer une approximation postérieure avec un autre flux
  aléatoire ; les réglages minéraux réellement modifiés continuent d'utiliser
  le moteur Custom éditable.
- Ajoute une régression qui compare case par case présence, famille et quantité
  des minerais Legacy et Custom-Legacy à paramètres identiques.
- Validation locale : **329 tests** passés et self-test source conforme.

## v2.0 DEV_6_R5 — 2026-09-04 — parité exacte des ressources

- Supprime réellement l’ancien lissage Upgraded des poissons : la génération
  Upgraded et son équivalent Custom remplissent la même bande côtière uniforme
  avec le même pourcentage, la même épaisseur et la même moyenne.
- Préserve la précision interne des parts de minerais afin que les cibles par
  famille et les sorties complètes restent identiques entre Upgraded et Custom
  lorsque les paramètres sont identiques.
- Corrige le quota Legacy : le taux d’occupation est atteint sur les terrains
  compatibles, y compris aux bornes 0–100 %, et les replis sont répartis en
  patches connectés bornés plutôt qu’en un dépôt artificiellement gigantesque.
- Rend le validateur compatible avec le rayon côtier effectivement sélectionné
  ou avec le remplissage global Custom.
- Validation locale : **328 tests** passés ; égalité case par case vérifiée sur
  les couches terrain, hauteur, ressources, objets, accessibilité et les starts.

## v2.0 DEV_6_R4 — 2026-09-04 — calibration des ressources Custom

- Répare le placement Legacy Custom des minerais : les gisements restent
  irréguliers et connectés au lieu de produire une bouillie de pixels.
- Calibre les valeurs par défaut sur les comportements de référence : moyenne
  8 pour Legacy, moyenne 10 pour Upgraded, sans appliquer l'ancien
  multiplicateur `×1,3`.
- Remplace le modèle poissons près des côtes par un remplissage direct et
  uniforme d'une bande d'épaisseur réglable ; une bande impossible revient au
  remplissage global. Supprime l'ancienne extension progressive.
- Conserve les bornes de quantités du format du jeu (1–15), les profils
  intégrés protégés et la génération/export des tailles non testées.

## v2.0 DEV_6_R3 — 2026-09-04 — premières sections Custom raccordées

- Remplace l’exposition technique des paramètres Custom par deux sections
  courtes et sémantiques : **Minerais** et **Poissons**, avec traductions
  dynamiques et rechargement au changement de générateur.
- Raccorde les deux vrais algorithmes de gisements : motifs/placement Legacy
  et blobs connectés sans trous Upgraded ; ajoute occupation globale,
  répartition par minerai, variation de taille et ressource moyenne.
- Ajoute le remplissage global des poissons, la ressource moyenne, le mode près
  des côtes, le rayon minimal dynamique et l’extension côtière progressive,
  avec repli global lorsque la zone côtière ne peut pas contenir la demande.
- Borne les quantités de ressources à 1–15, versionne le payload Custom en
  schéma 2 et conserve les profils Legacy/Upgraded protégés inchangés.
- Validation de la tranche : **323 tests** ; self-test source, archive avec
  références et contrôle des hashes protégés à finaliser pour la candidate.

## v2.0 DEV_6_R2 — 2026-09-03 — nettoyage de l’éditeur Custom

- Recharge du catalogue et affichage automatique de l’onglet Générateur lors
  du changement de moteur sélectionné.
- Traductions dynamiques des groupes, paramètres, bonus de départ et contrats
  d’archétype.
- Suppression des interrupteurs Custom qui décrivent des invariants (`River
  stop at first water`, `River fish forbidden`, `Cleanup micro water`, `Border
  must have gradient`) ; les profils intégrés protégés restent inchangés.
- Les champs `name` des familles restent des métadonnées internes et ne sont
  plus proposés comme paramètres.

## v2.0 DEV_6_R1 — 2026-09-03 — socle du générateur Custom

- Ajoute une configuration Custom déclarative, sérialisable et immuable par
  valeur : dérivation depuis Legacy/Upgraded, modification par chemin, JSON
  complet et empreinte SHA-256 stable.
- Ajoute les onglets **Générateur** et **Archétype**, un catalogue automatique
  des paramètres scalaires, l’éditeur JSON complet et la sélection automatique
  de Custom dès qu’un preset est modifié.
- Ajoute le registre extensible des bonus de départ : forêt, pierres et
  mini-marais actifs ; zone rocheuse minérale et mini-lac/poissons/rivière
  réservés pour les futures implémentations.
- Rend les profils Custom Upgraded exécutables et inclut leur empreinte dans le
  cache et Batch. Le moteur Legacy Custom conserve sa sortie native validée et
  expose les sections encore non raccordées dans ses diagnostics.
- Les presets Legacy/Upgraded, les tailles, les miroirs et les exports ne sont
  pas verrouillés par cette passe.
- Candidate locale : validation complète et essai visuel Windows encore requis.

## v2.0 DEV_5 — 2026-09-03 — finitions Upgraded validées

- Clôt les finitions Upgraded : objets statiques calqués sur Legacy hors
  récifs, bonus de départ, mini-forêts d’arbres, pousses limitées aux forêts,
  pierres et clusters, sans compter les bonus dans les quotas globaux.
- Conserve l’espacement forestier minimal de 3 HEX, la teinte rocheuse des
  récifs carte/graphique et le pont provisoire de coordonnées des joueurs.
- Supprime la vue dédiée **Départs** au profit de marqueurs et cercles
  optionnels partagés entre toutes les vues, corrige le flash de **Générer un
  lot**, et route les graphes proches vers la vue globale.
- Titre le graphe **Familles d’objets** et fixe ses colonnes selon l’ordre exact
  des nombres rouges de la référence utilisateur : arbres adultes, pousses,
  plantes/champignons, fleurs/buissons, souches, roseaux, pierres de
  construction, pierres décoratives, récifs, décors désertiques, arbres morts,
  tombes, épaves.
- Validation : **309 tests** passés, tests de maintenance du paquet **9/9**,
  self-test runtime après extraction **PASS**, archive source finale de 298
  fichiers après retrait de la feuille candidate.
- Limite `.sav` connue conservée et documentée : des récifs peuvent apparaître
  sur terre à cause d’un décodage probablement incorrect.

## v2.0 DEV_5_R3 — 2026-09-03 — vues partagées des départs et familles d’objets

- Renomme le graphe des objets en **Familles d’objets** et fige l’ordre de ses
  colonnes sur la séquence native, avec les pierres de construction en dernier.
- Supprime la vue dédiée **Départs** : les marqueurs de départ peuvent être
  affichés dans toutes les vues, et l’option indépendante **Cercles de départ**
  affiche les contours dans le Viewer, les previews Batch et l’Historique.
- Décorrèle marqueurs et cercles de l’opacité de la couche sélectionnée.
- Route les graphes **distance au plus proche adversaire** et **X proche(s)**
  vers la vue globale, tout en conservant les flèches de bordure d’origine.
- Corrige le flash de la fenêtre **Générer un lot** en construisant sa fenêtre
  initiale hors écran avant de la rendre visible.
- Candidate locale : **309 tests automatisés passés** ; validation visuelle
  Windows encore requise avant publication de DEV_5.

## v2.0 DEV_5_R2 — 2026-09-03 — cohérence des forêts, récifs et graphes

- Confirme et teste la séparation des quotas globaux et des bonus de départ :
  les bonus arbres/pierres s’ajoutent aux quotas globaux sans les consommer.
- Aligne l’espacement minimal des arbres adultes en forêt sur 3 HEX, valeur
  observée dans les sorties Legacy, sans réduire les quotas ni les bonus ; les
  forêts sont agrandies localement seulement lorsque nécessaire pour conserver
  le nombre demandé.
- Remplace le bleu vif des récifs par une teinte rocheuse sombre commune au
  rendu de carte et au graphique, inspirée de la capture fournie.
- Rend explicite la cible `Départs` dans les payloads des graphes de distance
  au plus proche adversaire et de ressources « proches ».
- Candidate locale : 305 tests automatisés passés ; validation visuelle Windows
  encore requise avant publication de DEV_5.

## v2.0 DEV_5_R1 — 2026-09-03 — finitions du contenu Upgraded

- Rétablit un mini-marais cohérent par départ sans recalculer les coordonnées
  des joueurs ; les transitions marécageuses sont reconstruites avec la
  profondeur HEX6 légale.
- Aligne les objets statiques Upgraded sur les 16 familles natives Legacy et
  conserve les récifs Upgraded sur les eaux profondes.
- Aligne les quotas d’arbres adultes sur Legacy, place 30 % du quota global en
  mini-forêts et conserve les pousses ID84 dans les forêts, avec les bonus de
  départ séparés.
- Restaure les bonus de pierres, les états actifs `115–126`, l’état épuisé
  `127`, les empreintes complètes, 30 % de clusters et environ 50 % de pierres
  récoltables supplémentaires au niveau global.
- Candidat local : suite automatisée et matrice multi-tailles passées ;
  validation visuelle Windows encore requise avant publication de DEV_5.

## v2.0 DEV_4 — 2026-09-03 — miroir et tailles de marqueurs

- Retire le verrou du miroir pour Upgraded dans le générateur principal et
  dans Batch : Axe long, Axe court et Les deux sont désormais transmissibles
  aux chemins natifs exposés, sans refus d’interface.
- Ajoute le niveau **Petits** et renomme les tailles affichées en
  **Petits**, **Normaux** et **Grands** ; les préférences historiques
  `small` et `normal` conservent leurs pixels et changent seulement de libellé
  pour suivre ce décalage.
- Propage ces quatre états aux vues Départs, aux aperçus Batch et à
  l’historique, avec une échelle 0,5× / 1× / 2×.

Les contrôles de viabilité et la limite de décodage `.sav` restent informatifs
et documentés ; les ajouts statistiques sont reportés à Stats V2.

## v2.0 DEV_4_R3 — 2026-09-03 — export multi-taille et ancrage des vues

- Corrige le crash du centre d’export hors 768 : le message de taille
  expérimentale est désormais traduit dans les quatre langues, donc le bouton,
  les informations et les fichiers prévus restent affichés pour 256–1024.
- Supprime le refus CLI fondé uniquement sur une validation de viabilité : les
  générations et exports restent disponibles pour tester les tailles signalées.
- Ancre les flèches de proximité entre les bordures des territoires de départ
  d’origine, en conservant la couleur du joueur sélectionné.
- Renomme le réglage en **Marqueurs de départ** et l’applique aussi à la vue
  Départs ; les graphes **X proche(s)** ouvrent désormais cette vue.
- Ignore `references/` pour GitHub tout en le réintégrant explicitement dans
  les ZIP sources remis avec les candidates.
- Conserve la limite `.sav` connue : des récifs peuvent apparaître sur des
  cases terrestres à cause d’un décodage probablement incorrect ; correction
  reportée.

## v2.0 DEV_4_R2 — 2026-09-02 — corrections Graphiques → Vue, tailles et exports

- Retire la liaison graphique → vue du graphique de comparaison A/B ; ce
  graphique reste réservé à la comparaison et aux tooltips.
- Route les graphes de pierres de construction vers la vue Globale, avec cache
  des masques / composites de surbrillance déjà visités.
- Corrige le graphe des distances adversaires : retrait des deux rayons de base,
  échelle couleur ancrée à zéro et flèche colorée du joueur vers l’adversaire
  le plus proche dans la vue Départs. Les distances nulles restent survolables.
- Rend la génération Upgraded disponible sur toutes les tailles natives du
  contrat ; les quotas calibrés 768 restent inchangés à 768, avec scaling
  proportionnel hors 768 pour garder la génération fonctionnelle.
- Maintient le bouton Exporter et les messages d’information lorsque des
  contrôles de viabilité échouent ; l’export reste disponible pour test.
- Note la limite `.sav` connue : des IDs de récifs peuvent actuellement être
  affichés sur terre, probablement à cause du décodage ; correction reportée.
- Candidate locale : **293 tests automatisés passés**, matrice Upgraded des
  13 tailles et limites joueurs passée, self-test source **PASS** ; validation
  visuelle Windows encore requise.

## v2.0 DEV_4_R1 — 2026-09-02 — candidate Graphiques → Vue et cadrage

- Ajoute le bouton **Lier à la vue** : le survol d’une région de graphique
  conserve le tooltip et cible les cellules exactes correspondantes dans la
  vue principale, avec changement de couche temporaire si nécessaire.
- Ajoute les payloads sémantiques pour terrains, neige, minerais, objets,
  arbres, agriculture, départs, rayons locaux et composantes de montagnes,
  lacs et rivières.
- Conserve le point d’ancrage, le zoom et le cadrage lors d’un changement de
  carte, d’une importation, d’un switch d’historique, d’une langue, d’une vue,
  d’une opacité ou d’une projection.
- Candidate locale : tests automatisés et self-test passés ; validation
  visuelle Windows encore requise.

## v2.0 DEV_3 — 2026-09-02 — calibration des formes et analyse des terrains

- Conserve le no-gap et les quotas des minerais, mais évalue désormais la
  forme des blobs dans l’espace de la projection parallélogramme afin de
  réduire l’étirement visuel dans l’aperçu standard.
- Renomme l’ID terrain `34` en **Patch d’herbe rocheuse** et l’expose
  explicitement dans le segment Montagne du graphique des familles de terrain.
- Aligne la couleur de l’ID `34` dans la carte et dans le graphique sur une
  teinte jaune/olive discrète inspirée de la référence native fournie.
- Le positionnement des bonus de départ et des objets de départ reste reporté
  à la passe `.sav` dédiée.

## v2.0 DEV_2 — 2026-09-02 — checkpoint Legacy natif validé

- Retire le pipeline procédural Continental Legacy DEV_1, ses profils et ses
  bibliothèques de silhouettes dérivées : ils étaient calibrés sur des
  résultats, mais ne reproduisaient pas l’algorithme natif.
- Retire également l’ancien chemin Legacy v1.5 qui ne constituait pas un
  générateur natif exploitable.
- Isole le chemin de compatibilité Upgraded et conserve ses profils, sa
  bibliothèque native de morphologie et ses règles validées.
- Compare les minerais avant suppression : volumes et mix proches des SAV,
  géométrie des amas trop fragmentée. Le relevé est conservé dans
  `references/history/minerals/SETTLERS3_LEGACY_MINERAL_COMPARISON_DEV2.md`.
- Ajoute la première passe de l'audit non-terrain de `S3.EXE` : ordre de
  matérialisation, séparation des couches Area/runtime, starts, bâtiments,
  colons, ressources de départ, métadonnées et transcription comportementale.
- Relie dans le noyau aléatoire les producteurs initiaux des ressources de sol
  (`0x51AD40`, poissons `0x518A08`) et des familles d'objets statiques
  (`0x51B010`, `0x51B1A0`). Approfondit ensuite l'audit avec le layout exact du
  registre type 9, les essais distincts des deux helpers, le catalogue de leurs
  paramètres et le writer natif `GameDataSave::Save` (`0x509995`) pour les
  records SAV principaux. Confirme aussi l'ordre des paramètres du noyau,
  le re-seed PRNG entre terrain et couches de partie, la banque exacte
  d'offsets hexagonaux, la frontière nouvelle carte/carte chargée et les
  sous-records SAV type 2. Le stock initial est relié à
  `0x506CF0 -> 0x5046B0 -> 0x504420`; seuls les noms métier, la source externe
  type 9 et le writer EDM/MAP restent à décoder.
- Met à jour le contrat de conception pour séparer `Continental v1` (archétype
  macro) de `Legacy v1` (moteur natif) et fixe l'ordre terrain/objets/ressources,
  re-seed, départs, ville/stock puis finalisation.
- Implémente le premier portage Legacy v1 séparé : relief, rivières,
  transitions, pinceaux de surfaces, objets statiques, minerais, poissons,
  reseed, sélection des départs et métadonnées runtime de ville/stock.
- Expose Continental v1 comme contexte d'archétype et garde le chemin Upgraded
  protégé séparé. Les tables runtime type 9 encore opaques sont conservées
  explicitement dans les métadonnées, sans règle inventée.
- Publie le générateur natif Legacy validé : tailles `256, 320, 384, 448, 512,
  576, 640, 704, 768, 832, 896, 960, 1024`, sélection des miroirs Axe long,
  Axe court ou Les deux, et avertissements de viabilité dans le feedback.
- Corrige le blocage observé sur le seed `297650040` en 256×256 et normalise
  la bordure extérieure en Water7. Les couches globales minerais, poissons,
  objets et décorations sont portées ; objets/ressources de départ, colons et
  écriture SAV restent différés.
- Rend les exports EDM/MAP disponibles sur toutes les tailles du contrat via
  le scaffold 768, explicitement comme candidates à tester dans l'éditeur
  communautaire/jeu. Le checkpoint est validé et poussé sur `dev` sans suffixe.

## v2.0 DEV_1 — 2026-08-31 — checkpoint Legacy validé

- Consolide les travaux R10 à R17 dans le premier checkpoint publiable de la
  reconstruction procédurale Continental Legacy v2.
- La génération des minerais et des poissons est validée : occupation et
  composition des familles minérales proches des SAV, quantités natives
  uniformes `1..15`, aucune modification des transitions, de la géométrie ou
  de la branche Upgraded.
- Relie enfin la façade utilisée par le GUI et `run_cli.py` au pipeline Legacy
  v2 ; le chemin historique Upgraded reste isolé et calibré séparément.
- Corrige le gate de hash Windows : les cinq fichiers de la baseline v1.5
  restent vérifiés, tandis que `validated.py`, devenue la façade du Legacy v2,
  n'est plus comparée à son ancien hash v1.5.
- Le checkpoint est désormais versionné sans suffixe `R`, conformément à la
  convention du projet ; les validations Windows/éditeur/jeu restent la
  prochaine étape d’homologation externe.

## v2.0 DEV_1_R17 — 2026-08-30 — quantités Legacy natives

- Conserve intégralement la géométrie minérale R16 : zones HEX6, rayons 3/4/5,
  remplissages, occupation montagneuse, ordre charbon → fer → or → gemmes →
  souffre et écrasements séquentiels.
- Corrige uniquement le low nibble des minerais et des poissons Legacy
  procéduraux : tirage uniforme des quantités `1..15`, avec plafond `15`.
- Remplace le multiplicateur `1,3` du profil `continental_legacy_v2` par
  `1,0`, conformément aux 16 SAV natifs audités ; les profils historiques
  protégés et la branche Upgraded restent inchangés.
- Confirme que la composition spatiale R16/R17 reste proche du natif : environ
  50 % charbon, 22 % fer, 14–15 % or, 5 % gemmes et 8 % soufre.
- Ajoute la mesure comparative dans
  `references/SETTLERS3_LEGACY_R17_QUANTITY_AND_FAMILY_MIX_REFERENCE_v1.md`.

## v2.0 DEV_1_R16 — 2026-08-30 — zones minérales aléatoires séquentielles

- Remplace la mécanique R15 de poches groupées, d'ancrage, de cohérence locale
  et de biais de compacité par des zones HEX6 indépendantes peintes directement.
- Applique explicitement l'ordre Legacy charbon → fer → or → gemmes → souffre ;
  chaque famille suivante peut recouvrir la précédente.
- Tire les rayons uniquement dans la palette mesurée 3/4/5 (diamètres 7/9/11)
  et le remplissage uniformément entre un minimum provisoire par famille et
  100 %. Les pixels retenus dans une zone sont aléatoires.
- Recalibre le support sur la montagne intérieure `32/33/34/35/128/129` et
  vise environ 53 % d'occupation, conforme à l'audit natif ; aucun halo autour
  des départs n'est ajouté.
- Ajoute des compteurs de couverture, d'écrasement, de remplissage,
  d'occupation Rocky32 et des limites d'essais pour diagnostiquer chaque seed.
- Ne modifie ni Upgraded v1.5/v7, ni les poissons, ni les règles de transition
  des terrains.

## v2.0 DEV_1_R15 — 2026-08-30 — amas minéraux localement cohérents

- Remplace la sélection quasi indépendante de R14 par un bruit aléatoire
  faiblement corrélé aux voisins HEX6 : les trous restent irréguliers, mais les
  cellules voisines forment de nouveau des amas lisibles comme dans les SAV.
- Fixe l'ancrage de chaque poche logique pendant la pose de ses HEX élémentaires
  afin d'éviter la dérive en chaînes longues et en traînées.
- Paramètres de cette candidate : cohérence locale `0,50` et biais de
  compacité `0,38`, sans revenir au noyau radial dominant de R13.
- Conserve les rayons 3/4/5, les taux de remplissage, les tailles de poches,
  les quotas, l'ordre charbon → fer → or → gemmes → soufre et les écrasements
  inter-familles. Aucun changement dans Upgraded, les transitions ou les poissons.

## v2.0 DEV_1_R14 — 2026-08-30 — remplissage interne quasi aléatoire

- Réduit fortement le biais radial introduit en R13 : les cellules manquantes
  sont maintenant réparties presque uniformément à l’intérieur de l’enveloppe
  HEX, avec seulement une cohérence locale très légère.
- Conserve les tailles de poches, la compacité générale, les rayons 3/4/5,
  l’ordre charbon → fer → or → gemmes → soufre et les quotas Legacy.
- Upgraded v1.5/v7 no-gap, les transitions terrain et les règles de poissons
  restent inchangés.

## v2.0 DEV_1_R13 — 2026-08-30 — remplissage compact et variable des minerais Legacy

- Remplace le tirage uniforme des cellules dans les enveloppes minérales par
  une sélection radiale bruitée autour d'un noyau : les gisements forment des
  masses compactes et irrégulières au lieu d'îlots dispersés.
- Rétablit une variation plus large des tailles de poches groupées (`0.65`),
  réduit la fenêtre de chaînage à `6` et conserve le bruit de sélection à
  `0.60`, valeurs calibrées sur les composantes de soufre des 16 SAV.
- Conserve les totaux, les rayons élémentaires 3/4/5, l'ordre
  charbon → fer → or → gemmes → soufre et les écrasements entre familles.
- Aucun changement dans le chemin Upgraded v7 no-gap ; les transitions terrain,
  les starts et les règles Legacy poissons restent séparés.
- Ajoute la mesure de remplissage et de fragmentation dans
  `references/history/minerals/SETTLERS3_LEGACY_MINERAL_FILL_RECHECK_v1.md`.

## v2.0 DEV_1_R12 — 2026-08-30 — géométrie minérale Legacy discrète

- Remplace la conversion directe des tailles groupées en rayons par une
  palette d’hexagones élémentaires de rayons 3, 4 et 5 (diamètres 7, 9 et 11).
  Le rayon 6, non démontré dans les SAV, n’est pas utilisé.
- Construit les grosses poches comme des chaînes de petits hexagones proches,
  avec des enveloppes susceptibles de se recouvrir ; un garde-centre évite
  seulement les doublons exacts d’une même famille.
- Rend le remplissage local plus variable et indépendant du rayon, sans
  modifier l’ordre Legacy charbon → fer → or → gemmes → soufre ni les
  écrasements entre familles.
- Ajoute des métadonnées et tests de contrôle des rayons, des shortfalls et de
  la conversion poche groupée → hexagones élémentaires. Le chemin Upgraded
  v7 no-gap reste inchangé.

## v2.0 DEV_1_R11 — 2026-08-30 — candidate rayons minéraux resserrés

- Amortit fortement la dispersion des tailles de patchs avant conversion en
  enveloppes HEX : les écarts visuels doivent venir surtout du remplissage et
  des recouvrements séquentiels, pas de rayons individuels gigantesques.
- Conserve l’ordre charbon → fer → or → gemmes → soufre, les écrasements entre
  familles et les quantités Legacy ; première validation 768×768 2P PASS.
- Restaure les fallbacks d’affichage : contour calculé et mini-balises dans
  Départs sans masque SAV direct, territoire de base calculé dans Territoires
  pour les cartes générées/EDM/MAP, claims SAV réels prioritaires.

## v2.0 DEV_1_R10 — 2026-08-30 — hexagones minéraux séquentiels

- Rejette le modèle R9 de champs minéraux exclusifs, qui fusionnait des zones
  et ne reproduisait pas le motif observé.
- Peint désormais les familles dans l’ordre charbon → fer → or → gemmes →
  soufre. Chaque famille pose des patchs HEX indépendants sur le support
  montagneux ; une famille suivante peut écraser les cellules précédentes.
- Calibre séparément le nombre de patchs, la distribution de cellules peintes
  et le remplissage. Les petits patchs sont plus creux ; le remplissage monte
  progressivement pour les grands patchs, conformément aux mesures des SAV.
- Sépare les patchs d’une même famille pour conserver des hexagones lisibles,
  tout en laissant les recouvrements entre familles. Les quotas finaux restent
  proches des médianes natives et les quantités conservent le multiplicateur
  Legacy R8.
- Mesures et limites consignées dans
  `references/history/minerals/SETTLERS3_LEGACY_MINERAL_HEX_REFERENCE_v1.md`.
- Réorganise le code en séparant le catalogue `generation/archetypes/` des
  moteurs `generation/generators/`. Le moteur actif est sous
  `generation/generators/legacy/`, sans copie des archétypes ni changement de
  comportement du pipeline Legacy ou du chemin de compatibilité v1.5.

## v2.0 DEV_1_R9 — 2026-08-30 — candidate minéraux rejetée

- Essai intermédiaire de champs minéraux larges, irréguliers et partiellement
  vides. Rejeté après comparaison visuelle : les zones fusionnaient et ne
  reproduisaient pas les hexagones superposables observés dans les SAV.
- La forme des champs est une aire HEX compacte découpée par le relief réel,
  ce qui autorise un même gisement à recouvrir des lobes de montagne proches
  sans créer les lignes denses produites par un simple flood-fill.
- Le paramétrage initial vient des SAV 768 : à une jonction de quatre
  hexagones, les quatre premières cartes Legacy 2P mesurées ont une médiane
  de 14 champs minéraux significatifs et un remplissage médian de 38 %.
  Cette mesure reste à étendre aux autres tailles.
- Ne modifie ni poissons, ni rivières, ni terrains, ni règle de proximité des
  départs. Les validations terrain restent toutes dures et inchangées.

## v2.0 DEV_1_R8 — 2026-08-30 — candidate intermédiaire

- Écarte les deux règles R7 qui ne décrivaient pas le Legacy : aucun rayon
  d’exclusion de ressources autour des starts et aucun filtre de poisson par
  distance à la Shore. Les poissons Legacy sont sélectionnés dans toute eau
  Water0..7 valide, toujours hors rivières.
- Remplace la distribution minérale générique par des profils par famille et
  densité de joueurs, construits depuis les quantiles de tailles de composantes
  mesurés dans les 16 SAV 768.
- Réoriente les rivières 768 vers une bande côtière de sources plus dense,
  des chemins courts et une préférence de virage ; la séparation entre tracés
  est protégée. La calibration reste ouverte : le volume et la forme locale
  des rivières ne sont pas encore simultanément assez fidèles.
- Aperçu déterministe produit : Continental Legacy 768×768, 2P,
  seed `2026083108`, validations dures PASS. Cette candidate ne valide pas
  encore la répartition globale des terrains, qui reste le prochain chantier.

## v2.0 DEV_1_R7 — 2026-08-30

- Commence le point 5 d’amélioration Legacy par la couche la mieux mesurée :
  ressources, sans modifier les terrains, la bathymétrie, les côtes ni les
  réservations visuelles des starts.
- Calibre les cibles 768 depuis les médianes des 16 SAV Legacy : environ
  39,9k cellules de minerais, avec profils séparés 2P/20P par famille, et
  46 071 / 43 737 cellules de poissons. Les composants de minerais utilisent
  désormais une distribution petites poches + longue traîne plutôt qu’un quota
  uniforme de blobs.
- Autorise les sept supports minéraux observés (`17,32,33,34,35,128,129`),
  dont `17/33/34` étaient exclus à tort.
- Réserve `r≤25` **uniquement pour les ressources** autour des starts : aucun
  nouveau halo de terrain ou de décor n’est créé. Ajoute le validateur dur
  `START_RESOURCE_CLEARANCE`.
- Préserve la règle historique de stock +30 % par cellule et les quantités
  plafonnées à 15 ; cette candidate affine l’occupation Legacy native, pas
  l’équilibrage long-play.
- Les poissons sont tirés sans remise avec un poids décroissant selon la
  distance à la rive (1–3, 4–6, 7–9, 10–12), toujours hors rivières et après
  l’hydrologie finale.
- Sondes déterministes 768 : 2P `39 859 minerais / 46 071 poissons`, 20P
  `40 061 minerais / 43 737 poissons`, 20/20 validations dures PASS ;
  génération 12,8–16,2 s selon la densité de joueurs.

## v2.0 DEV_1_R6 — 2026-08-29

- Conserve cumulativement le générateur Continental Legacy procédural de R5,
  ses sept tailles natives, ses silhouettes côtières calibrées par densité de
  joueurs, ses starts protégés, ses transitions, ses lacs et ses rivières.
- Ajoute une passe bathymétrique dédiée après la reconstruction des lacs : les
  résidus d'IDs Water0..7 des 16 SAV (8 cartes 2 joueurs et 8 cartes 20
  joueurs) reproduisent les variations locales d'épaisseur des bandes d'eau.
  La rive Shore48 est conservée intégralement ; aucune interruption visuelle
  n'est fabriquée en supprimant des cellules de plage.
- Fige le contrat de transition : toute terre en contact avec l'eau doit être
  Shore48, sauf les IDs River96..99 aux embouchures. Les validations dures
  `WATER_SHORE_TRANSITIONS` et `NO_WATER_GRASS_DIRECT` refusent toute sortie
  Eau→Herbe avant export.
- Ajoute un tampon autour des footprints de départ afin que la reconstruction
  des lacs ne puisse pas créer Eau→Herbe contre une zone de départ protégée.
- Corrige le ralentissement de génération 768 : le contrôle des composants qui
  entourent un départ est vectorisé sans changer sa décision, ce qui ramène le
  benchmark local 768×768 / 4 joueurs de ~38–40 s à ~19 s. Les tentatives de
  placement restent bornées.
- Rend la génération simple non bloquante pour Tk : le moteur travaille dans
  un worker dédié, les étapes sont relayées à l'interface par file d'événements
  et les paramètres sont verrouillés pendant la requête. Cela évite l'état
  Windows « Ne répond pas » pendant les étapes coûteuses.
- Optimise ensuite les champs de bruit des formes internes avec une
  interpolation quadratique très proche du champ cubique, et évite les champs
  génériques inutilisés quand la banque de silhouettes 768 est disponible :
  le benchmark 768 descend encore vers 13–16 s, sans modifier la règle de
  transitions ni le masque océanique principal.
- Consigne l'audit du point 4 dans
  `references/SETTLERS3_LEGACY_PIPELINE_AUDIT_v1.md` : les garde-fous
  Eau→Shore→terrain et les chaînes HEX6 sont confirmés, tandis que Shore48,
  les quotas/supports Legacy, les rivières, les décorations et la proximité
  économique des starts restent les écarts prioritaires. L'ordre start-first
  du projet est conservé ; l'ordre interne exact du jeu reste inconnu.
- Prépare le futur mode Custom comme laboratoire de réglage séparé ; aucun
  paramètre utilisateur n'est exposé tant que sa liste et ses garde-fous ne
  sont pas définis dans une discussion dédiée.
- Validation candidate : 267 tests, matrice des sept tailles natives jusqu'aux
  limites joueurs, autodiagnostic runtime, ZIP source déterministe et aperçus
  768 4P/20P avec validations dures PASS ; validation Windows/éditeur/jeu
  encore requise avant clôture de DEV_1.

## v2.0 DEV_1_R5 — 2026-08-29

- Réduit la réservation visible des starts à leur footprint exact : les
  massifs et autres familles ne sont plus découpés par un halo hexagonal, et
  chaque composant qui entourerait un start est rejeté puis resynthétisé.
- Renforce les contours côtiers avec un signal de détail indépendant pour
  éviter les longues sections droites contre la limite de la carte.
- Rend les rivières moins rectilignes grâce à une dérive latérale multi-échelle
  et à une préférence contrôlée pour les changements de direction, tout en
  conservant la connexion obligatoire à l'eau.
- Protège explicitement le footprint des starts pendant la reconstruction des
  berges et ajoute la validation dure `START_FOOTPRINT_GRASS`.
- Validation locale : 265 tests, matrice multi-tailles/joueurs et
  autodiagnostic du paquet PASS.

## v2.0 DEV_1_R4 — 2026-08-29

- Réordonne le vrai pipeline Legacy : océan/continent, starts, montagnes et
  neige, lacs/rivières, marais, autres terrains, objets de ressources,
  décorations, puis poissons/minerais.
- Reconstruit la macro-forme autour d’un continent principal unique : bord
  océanique irrégulier, baies côtières, îlots limités et absence de ré-ajout
  de cellules qui transformait la côte en archipel.
- Corrige l’ordre des transitions des familles Montagne, Désert et Marais ;
  les anneaux sont maintenant peints du bord vers le cœur.
- Isole l’hydrologie des massifs, limite les sources aux contreforts, borne les
  systèmes de rivières et reconstruit les profondeurs des lacs.
- Ajoute des validateurs durs pour toutes les chaînes de terrain, les trous de
  famille et les plages isolées. Les quotas objets/poissons/minerais restent
  inchangés pendant cette passe morphologique.

## v2.0 DEV_1_R3 — 2026-08-29

- Introduit le premier générateur **Continental — Héritage (Legacy)** réellement
  procédural : aucune génération Legacy ne lit de SAV, de PNG, de NPZ de
  références, de cache ou de silhouette stockée à l’exécution.
- Sépare les étapes dans `generation/generators/continental/legacy/` :
  macroforme, starts, biomes, lacs, relief/neige, rivières, ressources,
  objets et validations. Cette structure est le socle des futurs dérivés,
  notamment Upgraded, sans créer de générateur monolithique.
- Rend Continental Legacy disponible dans l’application pour les sept tailles
  natives `384…768` et leurs limites de joueurs ; les appels simple et batch
  passent explicitement la taille au même chemin de génération.
- Corrige le contrat de progression : le callback reçoit toujours
  `(étape, détail, index)`, ce qui empêche le crash de Génération simple tout
  en conservant la progression Batch.
- Calibre les premières formes sur le corpus hors runtime : continent irrégulier
  et baies, massifs rugueux, lacs internes non microscopiques, rivières
  herbe-only reliées à une berge réelle, chaînes de transitions et relief.
  Les quotas poissons/minerais sont conservés dans leur couche dédiée.
- Validation locale : génération déterministe 384 et 768, 4 et maximum joueurs,
  contrôles d’eau/accessibilité/transitions/rivières/objets ; affinage visuel
  Legacy à poursuivre avant tout modificateur ou archétype additionnel.

## v1.9 DEV_3 — 2026-08-28

- Consolide la candidate cumulative `DEV_3_R7` après validation Windows ;
  aucune fonctionnalité validée de `DEV_3_R1` à `R7` n'est retirée.
- Ajoute aux statistiques, exports et analyses locales les plantations `84`,
  les pousses d'arbre de stade 1/2 (`216–220`, `222`, `224–228`, `230`) et les
  pousses de palmier `221`/`229`.
- Rétablit le graphique **Arbres et pousses** dans l'ordre adultes, stade 2,
  stade 1, plantations, palmiers adultes, avec couleurs graduées et tooltips
  listant les IDs de chaque groupe.
- Conserve les nids `247–253` dans Agriculture/Cultures, les terrains `18/19`
  dans la famille Herbe et les éléments de joueurs/masque déjà validés.
- Validation locale et depuis le ZIP extrait : **258 tests réussis**, autodiagnostic
  du runtime PASS ; les six hashes protégés restent inchangés.
- Validation Windows utilisateur confirmée ; `DEV_3` est promue sur la branche
  `dev`. Les objets crash-prone `215/223/231`, les IDs `82/83` et la génération
  réelle restent explicitement hors de ce checkpoint.

## v1.9 DEV_3_R6 — 2026-08-28

- Consigne dans les catalogues les objets confirmés par les calibrations
  `208–214`, `216–222`, `224–230` et `232–255`.
- Valide les terrains `18/19` comme détails d’herbe singleton entourés d’herbe
  ID16 et les intègre à la famille Herbe, aux statistiques, au graphique et à
  l’inspecteur, avec un segment graphique dédié.
- Conserve `215`, `223` et `231` hors nomenclature sémantique après les crashes
  observés ; ne leur attribue aucun nom de gameplay.
- Laisse uniquement `82/83` à identifier, reportés à Datamining v2 ; les
  terrains `18/19` sont désormais validés comme détails d’herbe.
- Intègre les nids `247–253` à Agriculture et à la vue Cultures, avec une
  teinte miel distincte du blé, sans les remettre dans le graphique forestier.
- Validation locale après intégration : **257 tests réussis**.
- Le chantier de diversité/générateur est reporté à une reconstruction majeure,
  potentiellement v2.0, au lieu d'un audit v1.10 superficiel.

## v1.9 DEV_3_R5 — 2026-08-28

## v1.9 DEV_3_R5 — 2026-08-28

- Corrects native SAV type-6 player parsing to the observed `84 + 20×328`
  layout while retaining the old synthetic fixture for regression coverage.
- Exposes confirmed player activity/start fields and the repeated race/faction
  value as a clearly labelled candidate in statistics, JSON and CSV exports.
- Shows the validated slot-palette colour separately from the still-undecoded
  SAV effective colour; current/max mana and nominal tribe remain explicitly
  unknown rather than guessed.
- Adds the native player-block reference notes and real-SAV smoke coverage.
- Confirms the native initial-territory raster in the supplied immediate 4P SAV:
  type-3 byte 8 contains the exact cells (`3500/3500/4000/4000`), while the
  generated EDM and editor MAP carry no claim cells (`255` everywhere).
- Re-enables a **Masque initial** viewer based only on those explicit SAV
  coordinates; no canonical/radius reconstruction is used. Later SAVs retain
  their current runtime claims without being mislabelled as an initial mask.
- Treats native type-6 flags `1` and `2` as active human/computer slots so all
  four starts in the supplied SAV are recovered.
- Adds white diagonal hatching inside the direct initial-mask cells so this
  view is visually distinct from the solid-color runtime Territories view.
- Local candidate only: tests pass; Windows validation remains required before
  consolidating `DEV_3`.
- Validation Windows utilisateur : le fonctionnement de R5 est confirmé ; la
  cartographie R6 ci-dessus reste à compléter avant la clôture de DEV_3.

## v1.9 DEV_2 — 2026-08-27

- Consolidates the Windows-validated R2–R8 restructuring under the final
  unsuffixed checkpoint.
- Audits the post-restructuring test suite and removes seven duplicated or
  obsolete tests while keeping every represented behavior covered.
- Renames historical test functions by subsystem behavior and adds a contract
  preventing revision-number test names from returning.
- Replaces hard-coded old archive/title assertions with current version or
  neutral package contracts.
- Stops `ShellWindow` from constructing a disposable legacy header and hidden
  progress bar before `MainWindow` builds the active controls.
- Removes the obsolete task-dialog compatibility state and gives the remaining
  overlay lifecycle its real name.
- Leaves 243 passing cases with no historical test names or exact duplicate
  bodies; the remaining source-shaped GUI characterization tests are tracked
  for gradual behavioral replacement.
- Confirms after a closing import/caller audit that the remaining short modules
  own real package APIs, paths, profile loading, catalogues or subsystem
  boundaries; no line-count-driven merge is performed.
- Adds compact root `AGENTS.md` guidance, requires it in source archives and
  reduces the recommended ChatGPT Project instruction to a repository pointer.
- Keeps runtime behavior identical to the validated R8 candidate and changes
  only version metadata, tests, documentation and packaging requirements.
- Records that v1.8 remains DEV-only; the next RC/STABLE waits for the v1.10
  generator morphology and diversity correction.

## v1.9 DEV_2_R7 — 2026-08-26

- Replaces the implicit `base_window → settings_window → export_window →
  main_window` inheritance chain with one named `ShellWindow` foundation and
  explicit feature controllers.
- Removes the three obsolete window-layer files and the temporary generator
  construction that occurred before the runtime injected the real engine.
- Extracts import, task progress, application-level generation workflow,
  settings, language switching and theme rendering into responsibility
  packages; the strict engine remains exclusively under `generation/`.
- Renames the composed GUI class to `MainWindow`; `application.runtime.App` is
  now the sole public application composition root.
- Reduces `application/main_window.py` from about 860 to about 400 lines while
  preserving the complete behavioral suite and protected engine outputs.
- Windows validation completed: the application and exercised functionality
  remain operational; the final test-suite relevance audit now closes DEV_2.

## v1.9 DEV_2_R6 — 2026-08-26

- Extracts viewer interaction, statistics/graphs, map/statistics exports and
  shortcuts/help from `application/main_window.py` into dedicated subsystem
  controllers without changing their method bodies.
- Moves shortcut normalization from the generic settings family into its own
  `application/shortcuts/` package.
- Reorganizes historical `test_v18_dev*` files by functional subsystem and
  removes tests that required `main_window.py` to act as a compatibility
  catalogue for unrelated modules.
- Removes 48 obsolete imports and extraction gaps from the main window; its
  size falls from about 1560 to about 860 lines while the complete behavioral
  suite remains green.
- Keeps the protected generation engine and binary-format code unchanged.
  Windows behavior was validated by the project owner; this suffixed slice
  remains local because DEV_2 continues.

## v1.9 DEV_2_R5 — 2026-08-26

- Classifies every runtime module under `application/`, `generation/` or the
  deliberately shared `map_data/` lower layer; only package/version metadata
  remains at the Python root.
- Groups rendering, analysis, exports, settings, platform integration,
  diagnostics and session state into named application families.
- Moves modes, archetypes, profiles, rules and morphology into the strict
  generation package without changing the validated pipeline.
- Adds dependency-direction contracts and removes the obsolete statistics
  compatibility facade.
- Preserves exact R4 Legacy/Upgraded output identity. The owner validated the
  application under Windows; the slice stays local because DEV_2 continues.

## v1.9 DEV_2_R4 — 2026-08-26

- Removes every active `gui_v*` and `generator_v*` filename in favor of stable
  `application/` and `generation/` package boundaries.
- Gives Batch and History/comparison their own subsystem packages and
  behavior-preserving controller mixins.
- Moves GUI/runtime, CLI, self-test, packaging and test imports to the new
  canonical paths without a numbered compatibility facade.
- Confirms identical generated map bytes, starts, validations and stage logs
  against R3 for fixed Legacy 4P and Upgraded 20P references.
- Windows behavior was validated by the project owner; further DEV_2 slices
  will split viewer, analysis, exports, shortcuts/help and the remaining shell.

## v1.9 DEV_2_R3 — 2026-08-26

- Moves the complete UI translation/catalogue block out of `gui_v16.py` into
  feature-scoped `ui/i18n` modules for shell, viewer, Batch, History, exports
  and shortcuts.
- Moves stable viewer option order and selector colors to
  `ui/viewer/options.py` while preserving the temporary legacy `VIEWS` bridge.
- Preserves all 22 compared catalogues exactly and adds module-ownership,
  language-key, placeholder and option-order contracts.
- Reduces `gui_v16.py` from 2982 to 2697 lines; Windows startup was validated
  and DEV_2 continued without publishing the suffixed candidate.

## v1.9 DEV_2_R2 — 2026-08-26

- Starts the behavior-preserving GUI restructuring with stable `ui/theme`,
  `ui/viewer` and `ui/widgets` package families.
- Moves theme palettes, inspector labels, deterministic icons and
  `ColorMenuSelect` out of `gui_v16.py` while keeping temporary compatibility
  imports.
- Adds mirrored UI tests and deterministic pixel-equivalence coverage; the
  local candidate awaits Windows validation and is not publishable on `dev`.
- Replaces rejected R1 after its Windows startup exposed a missing `ImageDraw`
  import in the remaining theme-toggle drawing.
- Restores the import, adds direct headless coverage of that path and introduces
  a reproducible Ruff `F821` undefined-name gate for structural moves.
- Uses a distinct `DEV_2_R2` version and archive root so cached R1 files cannot
  be mistaken for the corrected candidate.
- Windows functionality tested by the project owner is operational; the slice
  is accepted locally and DEV_2 continues without publishing this suffix.

## v1.9 DEV_1 — 2026-08-26

- Consolidates the Windows-validated EDM terminal-padding fix from R1 into the publishable DEV_1 checkpoint without a revision suffix.
- Confirms both supplied sources load in the Windows GUI: 256×256/20 starts and 768×768/10 starts.
- Requalifies v1.9 around behavior-preserving internal restructuring first, with Data Mapping moved toward the end of the version.
- Adds an explicit context/quota budget to the project workflow: targeted reads and tests, bounded tool output, one candidate archive per validation and fresh chats after validated DEV checkpoints.
- Records the initial structural hotspots without pre-approving deletions: the 3168-line GUI monolith, historical GUI inheritance chain and three-layer engine/generator lineage.
- Keeps the v1.5 engine and all protected assets unchanged.

## v1.9 DEV_1_R1 — 2026-08-26

- Fixes partial `.EDM` import failures tracked by Issue #4 without changing the protected generation engine v1.5.
- Recognizes the confirmed file-level DWORD alignment used by two real editor-written EDM files: one to three opaque bytes may follow the terminal `type 0 / total size 8` part.
- Keeps scaffold parsing strict so an export reconstruction can never silently discard an unknown source tail.
- Adds regressions for all three valid padding lengths and rejects tails without the confirmed terminal part.
- Records both source files, SHA-256 values, exact part boundaries, valid checksums and the original traceback in a dedicated diagnostic reference.
- Repairs the mandatory PREGEN index after an obsolete SAV v2 reference had survived the documentation consolidation.
- Candidate remains local pending Windows validation on the two supplied EDM files.

## v1.8 DEV_11 — 2026-08-26

- Adds a reviewed English project entry point linked bidirectionally with the historical French README.
- Documents the real runtime architecture, protected-engine boundary, data flows, cache/protection semantics and safe-change rules without adding runtime work.
- Adds a reproducible debugging guide covering source/package failures, layered validation and the first-priority partial `.EDM` import investigation for v1.9 DEV_1.
- Prepares an explicit GitHub About description, restrained topic list, real-screenshot requirements and release checklist without changing repository settings.
- Applies the approved About description and nine Topics to the public GitHub repository.
- Integrates four real Windows screenshots of Generation/Viewer, Statistics, Charts and Batch into both READMEs, with recorded provenance and an explicit cache-reuse caption.
- Documents the known three-base-morphology seed limit instead of presenting rotations or mirrors as independent generated forms.
- Makes the deterministic source-package contract require the English README and all three maintenance/publication guides.
- Clarifies that `V` protects its attached Viewer map against eviction; simple generation is the exception because it necessarily moves the Viewer and `V` to the new result.
- Surfaces that `V` exception in the localized Help window and protection tooltip, and makes the mandatory snapshot refresh/checkpoint boundary explicit in project/versioning workflow.
- Keeps the v1.5 engine, binary formats, rendering and user-facing behavior unchanged.
- The first R2 archive was withdrawn before validation because it covered only part of the agreed scope; the rebuilt R2 then passed its targeted Windows checks.
- Consolidates the validated R1/R2 work into the only publishable checkpoint, `DEV_11` without a revision suffix, and closes development before the v1.8 RC phase.

## v1.8 DEV_11_R1 — 2026-08-25

- Adds a deterministic source-ZIP builder with one-root, required-file, excluded-path, corruption, SHA-256 and extracted-runtime validation.
- Runs the packaged source self-test from the extracted candidate directory so incomplete archives fail before delivery.
- Extracts stable history ordering and identity-based protection selection into pure helpers covered by behavioral tests instead of source-text coupling.
- Rewrites the session cache core for readable control flow and explicit hard-cap/LRU contracts without changing its public behavior.
- Centralizes application and engine version metadata in the localized window titles to prevent release-label drift.
- Makes the explicit engine/checksum smoke script directly runnable from the project root without relying on pytest path setup.
- Keeps the validated v1.5 generation engine, binary formats, profiles, native library and rendering behavior unchanged.
- Windows maintenance validation passed for the main controls, History Center, hard capacity, simple/Batch generation, `.MAP`/`.SAV` loading, languages and themes; the revision remains local because the broader DEV_11 publication/maintainability scope is not complete.
- Records partial `.EDM` loading failures as a potentially older defect promoted to the first priority of v1.9 DEV_1, and clarifies that `V` protects against eviction except when simple generation necessarily moves the Viewer to its new result.

## v1.8 DEV_10 — 2026-08-25

- Makes cache capacity a strict invariant: a simple generation/import can no longer create a hidden overflow slot when every retained map is protected.
- Keeps a rejected new result displayed outside history and reports the situation through localized dynamic feedback.
- Adds regressions for normal eviction, all-protected rejection and repeated insertion attempts that previously allowed unbounded growth.
- Separates the history rank from the V/A/B/M protection strip so combined locks no longer collide with the row number.
- Moves the larger outside-history warning from cache controls to the Viewer toolbar, where its meaning is unambiguous.
- Aligns Batch capacity forecasting with the same hard-limit insertion rule.
- Centers the protection lock in its dedicated History Center heading and closes DEV_10 without a revision suffix.

## v1.8 DEV_10_R1 — 2026-08-25

- Added session-only manual `M` locks to protect selected history maps from real cache eviction.
- Added explicit Lock/Unlock and Move up/Move down controls to the History Center in FR/EN/DE/ES.
- Separated the user-visible history order from true LRU recency; Viewer/A/B actions and cache hits no longer reorder the visual list.
- New/imported maps enter at the top while preserving the relative manual order of surviving entries.
- Extended delete, clear, capacity reduction and Batch forecasting to the shared V/A/B/M protection model.
- Deferred the standalone Windows package and packaged updater to the v1.8 RC phase; ordinary DEV work returns to source ZIPs and `run_gui.bat` / `run_gui.py`.

## v1.8 DEV_9_R2 — 2026-08-25

- Fixes the R1 startup failure caused by manually excluding Python standard-library modules reached indirectly by the normal SciPy/NumPy/Tk GUI import chain; R2 no longer uses hand-maintained module exclusions.
- Extends the packaged `--self-test` to import the real GUI runtime before checking resources, so missing frozen dependencies now fail the Windows build instead of appearing only on the user's machine.
- Makes the PowerShell builder explicitly wait for the windowed executable to finish before reading its self-test report.
- Keeps the R1 `onedir` layout, protected-byte checks, APPDATA preferences and executable-adjacent output folder unchanged.
- Generation engine v1.5, binary formats and protected assets remain unchanged.

## v1.8 DEV_9_R1 — 2026-08-25

- Introduces the first autonomous Windows x64 package in PyInstaller `onedir` form: users no longer need Python, pip or a source checkout.
- Separates bundled read-only resources from the application directory, keeping default exports beside the executable and preferences under `%APPDATA%/Settlers3MapGen`.
- Bundles the required profiles, native library, EDM/MAP scaffolds, upgraded reference and J1–J20 marker sheet.
- Adds an executable `--self-test` that opens every required runtime resource and emits a machine-readable report before the candidate is archived.
- Adds a reproducible Windows build, SHA-256 output and GitHub Actions artifact while deliberately avoiding a GitHub Release before Windows validation.
- Prepares optional `.ico` adoption without generating or inventing a final visual asset; the handmade pixel-art icon remains deferred.
- Keeps generation engine v1.5, binary formats and protected assets unchanged.

## v1.8 DEV_8_R4 — 2026-08-25

- Removes the unreliable Windows global-key-state query introduced in R3 after real validation showed both phantom Alt and missed Shift results.
- Builds captured combinations exclusively from modifier key press/release events observed by the focused capture control.
- Ignores every Tk state mask when the GUI supplies that explicit modifier set, eliminating both extended-state false positives.
- Keeps all validated R3 badges, reminders, scrolling, persistence, migration and Help behavior unchanged.
- Windows validation passed for plain keys and genuine Ctrl, Shift and Alt combinations, with no phantom modifier remaining.

## v1.8 DEV_8_R3 — 2026-08-25

- Stops inferring Alt from platform-dependent extended Tk state bits during capture.
- Tracks real modifier key presses and queries the physical Ctrl/Shift/Alt state on Windows at the primary key event, eliminating the remaining phantom Alt path without disabling genuine Alt shortcuts.
- Replaces the small pixelated conflict triangle with a larger circular exclamation badge and gives pending changes a distinct clock badge.
- Makes the bottom pending/conflict reminder bold, color-coded and icon-assisted in both themes.
- Adds automatic vertical scrolling to Settings and Shortcuts while preserving the useful R2 horizontal scrolling; each bar appears only when needed.
- Keeps persistence and schema migration unchanged; candidate awaits Windows validation.

## v1.8 DEV_8_R2 — 2026-08-25

- Fixes phantom `Alt` capture on Windows by excluding the unrelated `0x0080` keyboard-state bit while retaining both validated Alt indicators.
- Replaces modal shortcut-conflict errors with per-row warning icons, localized tooltips and an Apply button disabled until conflicts are resolved.
- Marks every changed-but-unapplied shortcut with a distinct inline icon and a compact localized reminder below the list.
- Makes individual and global resets participate in the same explicit Apply workflow.
- Adds automatic horizontal scrolling to Settings and Shortcuts only when their content no longer fits the available compact width.
- Keeps the R1 migration, expanded commands and dynamic themed Help unchanged; candidate awaits Windows validation.

## v1.8 DEV_8_R1 — 2026-08-25

- Replaces free-text shortcut editing with direct key capture, per-action Disable and Reset controls, conflict detection and canonical Tk/Windows binding conversion.
- Expands configurable shortcuts to Batch generation, PNG preview, History Center and A+B clearing while keeping existing actions and allowing any shortcut to be disabled.
- Migrates the existing `%APPDATA%/Settlers3MapGen/settings.json` shortcut map entry by entry to schema 2; malformed entries fall back independently and user-disabled entries remain disabled.
- Replaces the native Help message box with a reusable themed FR/EN/DE/ES window listing the live configured shortcuts and navigation controls.
- Preserves the validated semantic native title bars and their event-driven behavior; generation engine, binary formats and protected assets remain unchanged.
- Candidate awaits Windows validation before synchronization on `dev`.

## v1.8 TITLEBAR_TEST_R4 — 2026-08-25

- Keeps the Windows-validated dark caption and separator unchanged.
- Gives the light theme its own light-gray native caption, dark text and visible separator instead of inheriting the dark caption.
- Preserves event-driven updates only: window mapping and explicit theme changes, with no polling or background work.
- Keeps the one-pixel separator static after placement and preserves the native Windows frame.
- Remains an isolated experiment based on the Windows-validated DEV_7_R10 state.

## v1.8 TITLEBAR_TEST_R3 — 2026-08-25

- Gives the native caption a darker color that remains distinct from the dark client area.
- Separates caption color, outer Windows border and the client-edge separator into independent semantic roles.
- Adds a one-pixel internal separator below the native caption because DWM border color alone does not guarantee that boundary.
- Preserves native Windows chrome, event-driven refresh and the documented Help-dialog exception.
- Remains an isolated experiment based on the Windows-validated DEV_7_R10 state.

## v1.8 TITLEBAR_TEST_R2 — 2026-08-25

- Keeps the native Windows caption dark in both built-in application themes.
- Adds dedicated semantic roles for native caption, caption text and border instead of coupling them to client-area colors.
- Requests a fixed medium-gray DWM border as the first non-invasive separator test while preserving the standard Windows frame.
- Records the native Help message box as an explicit theming exception for a later dialog-design pass.
- Remains an isolated experiment based on the Windows-validated DEV_7_R10 state.

## v1.8 TITLEBAR_TEST_R1 — 2026-08-25

- Adds best-effort native DWM theming for decorated Tk title bars.
- Reuses the active semantic theme palette for caption, text and border colors on supported Windows versions.
- Refreshes only on theme changes and top-level window mapping; no polling is introduced.
- Keeps native Windows chrome and ignores borderless preview overlays.
- Remains an isolated experiment based on the Windows-validated DEV_7_R10 state.

## v1.8 DEV_7_R10 — 2026-08-24
- Keeps the source thumbnail accessible whenever a large preview is opened by delayed hover.
- Selects the best available area around the source and temporarily reduces only the rendered preview when required.
- Preserves the stored zoom value and leaves pinned previews fully movable and unconstrained by thumbnail avoidance.
- Adds Escape as a fallback way to close a visible large preview.
- Applies the same behavior to Batch and History; DEV_7_R10 is validated under Windows.

## v1.8 DEV_7_R9 — 2026-08-24
- Fixes the reproducible Tk error triggered by generating after closing the History Center.
- Cancels pending History callbacks, clears destroyed widget references and guards late preview refreshes.
- Adds a fifth magnifier state for temporary hover-opened previews without showing a misleading close cross.
- Keeps the orange close cross exclusively for pinned previews that a click will actually close.
- Gives the Batch large preview the same screen-wide zoom geometry as History while preserving the 35–125% range.
- Preserves drag, remembered position and atomic replacement behavior; candidate awaits Windows validation.

## v1.8 DEV_7_R8 — 2026-08-24
1. Restores a neutral style for the history-capacity confirmation action.
2. Makes the idle magnifier more translucent and adds an explicit active-hover close state.
3. Separates the active preview source from the currently hovered thumbnail so both cues can coexist.
4. Binds hover lifetime to the full thumbnail container to prevent stuck visual states.
5. Adds mouse-wheel zoom to the Batch large preview with the same 35–125% range as History.
6. Preserves click, delayed hover, drag, position retention and atomic replacement behavior.
7. Candidate awaits Windows validation; generation engine and protected assets remain unchanged.

## v1.8 DEV_7_R7 — 2026-08-24
- Replaces the history-capacity reduction prompt with a fully modal, themed FR/EN/DE/ES dialog that prevents background wheel/click changes and duplicate confirmations.
- Restores large translucent magnifiers as deterministic RGBA thumbnail layers without opaque backing rectangles.
- Introduces exclusive inactive, awake and active magnifier states shared across Batch and History previews.
- Preserves delayed hover, click pinning, drag/zoom and atomic preview replacement behavior.
- Locks the Batch forecast to the shared protection list so future manual locks scale without capacity-specific rules.
- Candidate awaits Windows validation; generation engine and protected assets remain unchanged.

## v1.8 DEV_7_R6 — 2026-08-24
- Simulates the final Batch cache exactly for every supported capacity: 4, 8, 12 and 16 maps.
- Separates existing history entries that will be evicted from newly generated Batch results that will not remain cached.
- Replaces the native capacity prompt with a themed modal dialog localized in FR/EN/DE/ES.
- Marks successfully generated but non-retained Batch rows with a localized warning state and includes their count in the final summary.
- Preserves the validated R5 cancellation and viewer behavior; generation engine and protected assets remain unchanged.
- Candidate awaits Windows validation.

## v1.8 DEV_7_R5 — 2026-08-24
- Removes the white outer pixels from the validated checked-circle size.
- Removes the unstable R4 magnifier overlays while preserving direct thumbnail hover/click interactions and the validated History preview.
- Fixes Batch capacity forecasting by counting distinct cached Viewer/A/B/manual protections and testing the exact capacity-4/three-protection case.
- Keeps an existing viewer map after Batch completion; automatic display now only fills an empty viewer.
- Records the rare, non-reproducible long Statistics calculation for monitoring rather than applying a speculative fix.
- Generation engine, binary formats and protected assets remain unchanged; candidate awaits Windows validation.

## v1.8 DEV_7_R4 — 2026-08-24
- Keeps History order stable while maps are displayed or assigned; only real generation-cache hits promote LRU entries.
- Replaces the ambiguous protection glyph with compact combinable `V/A/B` padlocks and prepares the reserved `M` manual-lock role.
- Enlarges the checked state inside its existing button footprint and adds contextual Loaded/Shown/Assigned labels in FR/EN/DE/ES.
- Adds three-state magnifier overlays to History and Batch thumbnails.
- Aligns the History large preview with Batch: delayed hover, pinning, drag, wheel zoom, same-source close and position-preserving replacement.
- Atomically replaces preview surfaces during projection changes and updates marker/selection changes in place to avoid flicker.
- Adds a hover explanation to the outside-history warning and a preflight warning when protected entries leave insufficient room for a Batch.
- Records the post-DEV_7 GitHub Issues/Wiki design pass without creating repository Issues yet.
- Generation engine, binary formats and the five protected assets remain unchanged; candidate awaits Windows validation.

## v1.8 DEV_7_R3 — 2026-08-24
- Adds a compact MRU rank column and live used/capacity count to the History Center; protected entries carry a lock without consuming another data column.
- Replaces color-only dots with larger hollow/checked state icons on History, Batch and header Show/Load/A/B actions.
- Displays imported formats as lowercase parenthesized extensions in Details.
- Keeps the selected preview vertically stable and adds a deterministic frameless large preview with drag, wheel zoom, preserved position and live replacement.
- Renames Comparison to Comparison slot in the selected information panel and refreshes all current/A/B/protection information immediately.
- Extends manual-delete and Clear All warnings to the currently displayed map; a manually removed current map remains visible and is explicitly marked outside history until replaced.
- Keeps automatic LRU protection, exact source preservation, generation engine, binary formats and protected assets unchanged.
- Candidate awaits Windows validation.

## v1.8 DEV_7_R2 — 2026-08-24
- Introduces shared semantic light/dark palettes and explicit normal, hover, pressed, selected, focused and disabled state maps for recurring ttk widget families.
- Fixes History Treeview rows and headings in dark mode with dedicated styles and explicit alternating row colors.
- Adds a selected-map panel with deterministic preview, A/B presence, current-map state, MRU position and full imported source path without duplicating table columns.
- Protects the currently displayed output and A/B outputs from automatic LRU eviction; completed four-map batches remain complete at the minimum capacity of four.
- Warns before manually deleting an A/B map, then clears the affected slots only after confirmation; Clear All follows the same rule.
- Keeps selection at the same row after deletion, falling back to the previous row at the end.
- Renames the setting to “Capacité de l’historique” and warns before a reduction removes older unprotected entries.
- Keeps all History Center content live in FR/EN/DE/ES and both themes; generation engine and protected assets remain unchanged.
- Candidate awaits Windows validation.

## v1.8 DEV_7_R1 — 2026-08-23
- Unifies simple generations, Batch results and imported EDM/MAP/SAV maps in one session-only MRU history.
- Adds explicit origin and map metadata, content-based import deduplication and configurable 4/8/12/16 capacity (default 8).
- Keeps the compact header selector and adds a resizable History Center with Show, Assign A, Assign B, delete-one and clear-all actions.
- Restores the original import source when loading a history item, preserving exact unchanged SAV copy behavior after history and A/B navigation.
- Keeps history content in memory only; deleting or evicting an entry does not invalidate maps already held by the current viewer or A/B slots.
- Supports live FR/EN/DE/ES retranslation and light/dark theme changes in the open History Center.
- Generation engine, binary formats, map rendering and protected assets remain unchanged; candidate awaits Windows validation.

## v1.8 DEV_6_R1 — 2026-08-23
- Extends the persistent dynamic UI language selector from FR/EN to FR/EN/DE/ES with deterministic German and Spanish raster flags.
- Localizes the main window, Batch generation, both Export Centers, settings, feedback, help, disabled states and fully localized window titles.
- Localizes Statistics reports plus all chart titles, labels, legends, units and contextual tooltips in German and Spanish.
- Keeps English as the explicit missing-entry safety fallback while preserving the selected language across restarts.
- Documents French and English as reviewed reference languages; German and Spanish are automatic translations with only partial review and remain open to native-speaker corrections.
- Records a non-blocking limitation: the existing Statistics text report is translated after a map reload rather than immediately when switching language.
- Adds catalog parity, language persistence, report and complete chart-render regression coverage.
- Generation engine, binary formats, map rendering and protected assets remain unchanged.
- Windows validation completed; delayed Statistics text-report retranslation is accepted as a documented non-blocking limitation.

## v1.8 DEV_5_R3 — 2026-08-23
- Keeps both Export Centers modal and disables the Windows parent at the native window level while either center is open, blocking external clicks, wheel input, keyboard input and shortcuts.
- Restores and focuses the main window when the modal center closes.
- Gives unavailable export formats a dedicated muted, struck-through style in both themes while keeping the existing bilingual explanation below the choices.
- Keeps all R1/R2 export behavior, geometry and theme fixes unchanged; generation engine and protected assets remain untouched.
- Windows validation completed: strict modality, parent restoration, unavailable-state styling, explanations, bottom geometry and dark-theme hover behavior accepted.

## v1.8 DEV_5_R2 — 2026-08-23
- Disables the Current View PNG option when Global is selected because it would be pixel-identical to the dedicated Global PNG; Global PNG becomes the default preview export in that case.
- Adds a bilingual explanation beside the disabled option.
- Gives both export windows a small theme-independent bottom safety margin and lets their content frame fill the complete client area.
- Colors the native Toplevel surface with the active theme to prevent any exposed system-color strip.
- Explicitly themes normal, disabled, hovered and pressed Checkbutton states, preventing light system-color flashes in the dark theme.
- Keeps every R1 export rule and output unchanged; generation engine and protected assets remain untouched.

## v1.8 DEV_5_R1 — 2026-08-23
- Replaces the direct all-at-once map export with a bilingual Map Export Center using one folder and one Windows-safe shared basename.
- Offers independent EDM, MAP, unchanged source SAV, Global PNG and current-view PNG selections with an exact live filename summary.
- Enables EDM/MAP only for the validated 768 scaffold and SAV only when the current output retains a real imported SAV source; no SAV writer is introduced.
- Distinguishes a marker-free Global PNG in the active projection from the current rendered View PNG with its selected overlay and start layer.
- Detects every existing destination before writing and asks for one grouped overwrite confirmation.
- Replaces the three Chart export buttons with one bilingual multi-format Export Center for JSON, CSV and the currently displayed PNG chart.
- Persists imported SAV source identity in map metadata so an SAV kept in A/B still exports the correct unchanged source after later navigation.
- Adds pure export planning/sanitization helpers and an integration check that writes real EDM/MAP/PNG outputs.
- Generation engine, protected profiles and native library unchanged; candidate awaits Windows validation.

## v1.8 DEV_4 PERF+ R1 — 2026-08-23
- Builds a separate, reversible performance candidate from the Windows-validated DEV_4_R6 checkpoint.
- Splits deterministic map rendering into a reusable marker-free square raster followed by lightweight projection and start-marker composition.
- Reuses the same Global square raster when switching between Global and Starts; Starts opacity now invalidates only its sprite composite.
- Keeps at most the current main-view square layer and its projection composites, plus one square and one parallelogram base per completed Batch result.
- Stops invalidating deterministic map pixels for language, theme and projection changes; the visible result still refreshes immediately.
- Debounces rapid opacity and wheel-zoom preference writes by 200 ms and flushes the latest values on application close.
- Preserves exact rendering: split and direct render paths are pixel-identical for Global, Starts and Territories in Square and Parallelogram.
- Reference 768 benchmark: cached projection about 7.6× faster and cached Starts-opacity composition about 24× faster than full rerendering on this environment.
- No threads, engine changes, rendering approximation or interaction changes.
- Windows validation completed: no regression or performance loss observed, with a possible responsiveness improvement; PERF+ R1 is accepted and retained.

## v1.8 DEV_4_R6 — 2026-08-23
- Makes pinned Batch previews draggable directly from the rendered map while keeping temporary hover previews non-interactive.
- Removes click-to-close from the large preview itself; clicking the same source mini-map again remains the primary close action, with Escape as fallback.
- Replaces an already pinned preview with another mini-map at the exact same top-left position instead of re-anchoring it.
- Preserves the current tooltip position during live marker/projection refreshes and clamps all manual movement inside the visible screen.
- Double-buffers projection changes and pinned row replacements: the complete new transparent surface is shown above the old one before the old surface is destroyed.
- Keeps same-projection marker changes on the lighter in-place image swap path.
- Keeps the validated R5 marker-layer cache and atomic image replacement unchanged.
- Generation engine, protected profiles and native library unchanged.
- Windows validation completed: dragging, closing, same-position replacement, screen clamping and projection double-buffering accepted by the user.

## v1.8 DEV_4_R5 — 2026-08-23
- Adds a persistent `Hidden / Small / Normal` display setting for start markers in Batch thumbnails and their enlarged previews.
- Defaults to Small; Normal preserves the R4 compact-marker scale and Hidden removes only preview markers.
- Keeps one marker-free base raster per completed Batch result/projection and composes only the lightweight start layer when the setting changes.
- Refreshes every completed Batch thumbnail immediately and swaps the image of an already visible hover/click preview without destroying its tooltip.
- Confirms pixel-for-pixel equivalence between direct and layered marker rendering in Square and Parallelogram.
- Keeps the validated Starts view, its central marker, 210-marker boundary, opacity behavior and Territories rendering unchanged.
- Layer composition benchmark on the 768 reference: about 0.08–0.09 ms Square and 0.57–0.64 ms Parallelogram, excluding Tk display resizing; generation engine, protected profiles and native library unchanged.
- Windows validation completed: all three marker modes, immediate thumbnails and non-blinking pinned preview accepted by the user.

## v1.8 DEV_4_R4 — 2026-08-23
- Adds a dedicated localized Starts view and removes all start labels/initial-territory overlays from the Global view.
- Keeps the exact native 3500-cell initial-territory mask and 210-cell HEX6 boundary in the Starts view only.
- Extracts J1–J20 start sprites deterministically from the user-provided editor reference, removes only its flat grass background and preserves nearest-neighbour pixel rendering.
- Refines the exact 210-marker Starts outline to the smallest non-overlapping raster sizes: 1×1 in Square and 2×2 in Parallelogram; R3 remains the visual fallback.
- Anchors central, boundary and compact Batch markers on their geometric center instead of their lower edge.
- Enables the opacity slider in Starts and applies it only to its central/boundary sprite layer, from fully visible at 100% to absent at 0%; the terrain remains unchanged.
- Uses compact center sprites in Batch mini-maps and their enlarged previews without adding the initial-territory boundary there.
- Makes Territories claims use the centralized validated J1–J20 palette with strict claim IDs 0..19; unknown values no longer wrap to another player color.
- Moves Territories immediately after Starts in the localized View list.
- Keeps SAV Territories tied to real runtime claims, while EDM/MAP and claim-less generated states reconstruct display-only initial territories from the exact confirmed 3500-cell native mask around each real start.
- Resolves synthetic initial-territory overlaps by nearest HEX6 distance, then lower player slot on ties; source map data remains untouched.
- Records the later label-design pass and the broader composable Views / chart-driven View Control interaction as separate UX work.
- Records a later Batch setting study for smaller, adjustable or disabled compact start markers.
- Postpones any manual modernization of the marker sprites to the future hand-made Pixel Art redesign.
- Windows validation completed: non-overlapping Starts borders, View ordering, opacity and EDM/MAP/SAV Territories behavior accepted by the user.
- Generation engine, protected profiles and native library unchanged.

## v1.8 DEV_3_R7 — 2026-08-22
- Removes the redundant Batch map-count Apply button.
- Applies valid 1–4 map counts immediately from spin arrows or keyboard input; focus/Enter clamps invalid committed values back into range.
- Adds an 8-pixel gap between each progress-feedback bar and its mini-map region.
- Narrows the mini-map container from 224×122 to 182×122 and the render constraint from 222×120 to 180×120, matching the validated parallelogram aspect without reducing the displayed parallelogram.
- Square projection remains naturally centered and less width-constrained.
- Windows validation completed: DEV_3 Batch Generation and all R1–R7 polish accepted by the user, then promoted to `dev`.
- Archives a user-provided four-seed Batch screenshot as evidence for the v1.10 seed/RNG and morphological-diversity audit; no root-cause analysis or generator change is performed here.
- Generation engine, protected profiles and native library unchanged.

## v1.8 DEV_3_R6 — 2026-08-22
- Enlarges the real Batch mini-map from 202×108 to 222×120 and its frameless container from 204×110 to 224×122.
- Preserves the validated one-pixel internal gap between map and container.
- Reduces the Batch row frame padding to one pixel around the mini-map container, letting the preview use the space up to the outer row border.
- Keeps independent left padding on parameter controls and result actions so only the preview region reaches the edge.
- Generation engine, protected profiles and native library unchanged.

## v1.8 DEV_3_R5 — 2026-08-22
- Tightens Batch mini-map containers from 210×116 to 204×110 while preserving the 202×108 rendered map maximum.
- Reduces header, row, frame and footer spacing so the four result blocks remain compact without shrinking their readable controls.
- Measures the completed Batch window's requested width and height before final placement instead of relying only on the historical 1120×650 default.
- Opens at the full requested content size whenever the current screen permits, centers relative to the main application and clamps the window inside visible screen bounds.
- Generation engine, protected profiles and native library unchanged.

## v1.8 DEV_3_R4 — 2026-08-22
- Enlarges each Batch mini-map area from 152×88 to 210×116 pixels and its rendered map from 144×80 to 202×108.
- Removes the relief/highlight frame around mini-maps; transparent projected corners now reveal the current panel color directly.
- Makes existing Batch mini-maps react immediately to Square/Parallelogram projection changes in the main Settings tab.
- Rebuilds an already visible hover/click preview immediately when projection changes.
- Replaces cursor-relative preview placement with deterministic mini-map anchoring: preferred adjacent side with screen-aware fallback and vertical clamping.
- Records a future deterministic start-marker pass using validated native game sprites; no sprite is guessed or bundled in this candidate.
- Generation engine, protected profiles and native library unchanged.

## v1.8 DEV_3_R3 — 2026-08-22
- Fixes Batch thumbnails that collapsed to 12×4 pixels when Tk switched Label dimensions from text units to image pixels; each result now has a fixed 152×88 preview area with a map up to 144×80.
- Adds a dedicated common-seed dice button between the shared seed field and “Apply to all”; global and per-row dice actions remain unchanged.
- Replaces the decorated large-preview window with a borderless map-only tooltip.
- Click toggles a pinned tooltip; deliberate 700 ms hover shows a temporary tooltip.
- Parallelogram preview alpha is preserved through a Windows transparent-color surface so only the projected map remains visible around its transparent corners.
- Generation engine, protected profiles and native library unchanged.

## v1.8 DEV_3_R2 — 2026-08-22
- Polishes the Windows-validated Batch v1 workflow without changing the protected generation engine.
- Every row now opens with the same current/default seed; global and per-row dice actions are both preserved, with an additional common-seed “Apply to all” action.
- Adds deterministic mini previews rendered from each real generated map; click opens the large preview immediately and a 700 ms deliberate hover opens it without reacting to quick passes.
- Reorders each result line to Show / Assign A / Assign B / colored progress-feedback bar.
- Adds semantic Batch bar colors for running/success, cache, error and cancellation states.
- Shows A/B occupancy LEDs on result actions and centrally prevents the same output from occupying both slots; reassignment moves the map and reports it explicitly.
- The open Batch window is retranslated live when the main language changes, while keeping the entered configuration.
- Adds a future focused deterministic/manual iconography pass to the roadmap.

## v1.8 DEV_3_R1 — 2026-08-22
- Replaces the reserved Batch button with a dedicated bilingual Batch Generation window.
- Configures 1 to 4 maps independently: mode, archetype, modifiers placeholder, size, player count and seed.
- Runs the existing protected v1.5 pipeline sequentially and reuses matching session-cache results.
- Displays per-map waiting/running/success/error/cancelled states and progress without interrupting the active engine call.
- Adds every successful result to session history; after completion, each result can be displayed or assigned directly to comparison slot A or B.
- Pending maps can be cancelled after the current synchronous generation finishes; successful and failed maps remain available in the window.
- Adds `.pytest_cache/` to Git exclusions; generation engine, protected profiles and native library unchanged.

## v1.8 DEV_2_R7 — 2026-08-22
- Resets the inherited elastic header column left behind by the pre-R6 layout, allowing Language/Help/Theme to reach the actual right edge.
- Raises the wide-to-compact breakpoint from 1600 to 1750 px after GIF review showed the theme button clipping immediately before reflow.
- A/B identity buttons now use natural translated text width whenever Session has room and compact only near the real minimum.
- Active individual A/B delete actions use a deterministic red cross icon; empty slots keep a disabled muted cross.
- R6 three-region structure and minimum layout preserved; generation engine v1.5 unchanged.
- Windows resize validation completed from the user-provided R7 GIF, both with empty and populated A/B slots: wide/compact transition, right anchoring, adaptive A/B widths, active red crosses and minimum layout validated.

## v1.8 DEV_2_R6 — 2026-08-22
- Replaces the widget-by-widget header grid with three independent functional regions: Generation, Session/Comparison and global controls.
- Wide mode keeps Session/Comparison genuinely centered between Generation and Language/Help/Theme.
- Compact mode moves whole regions only; global controls no longer mix with generation parameters.
- Generation selectors and action rows use independent local layouts, so button spacing no longer depends on unrelated columns above.
- Import/Export/PNG Preview buttons use their natural translated text width and are no longer clipped.
- Viewer Zoom minimum behavior intentionally unchanged; generation engine v1.5 and protected assets unchanged.

## v1.8 DEV_2_R5_R5 — 2026-08-22
- Header/layout aligned to the Paint 3 reference; stable shared structure across widths.
- Reserved `Générer lot…` / `Generate batch…` action slot for v1.8 Batch.
- Session/Comparison compact A/B layout; compact mode fits the 900 px minimum runtime width.

## v1.8 DEV_2_R4 — 2026-08-22

- Reserved a future multi-select **Modifiers** control after Archetype; current value is None only.
- Wired modifiers into generation cache/history/status semantics without touching generator v1.5.
- Reduced Session history field width and reflowed Load/Clear cache actions on constrained widths.
- Stacked Help/Theme below Language in compact mode.
- Progress overlay unchanged and validated.

## v1.8 DEV_2_R3 — 2026-08-22

- Reorganizes the application header by function instead of historical grid position.
- On normal 1080p-width windows, Generation stays left, Session/Comparison uses the center, and Language/Help/Theme stay right.
- `Copier seed` / `Copy seed` stays next to the Seed controls.
- Inspector remains visible in the upper application area rather than being hidden under the map viewer.
- Feedback/status remains a prominent thin messenger strip immediately above the main map/data area.
- Compact mode is now reserved for genuinely narrow windows instead of being forced solely by 1080p screen height.
- Viewer toolbar/progress/feedback behavior from R2 is preserved.

## v1.8 DEV_2_R2 — 2026-08-22

- 1080p explicit compact target.
- Viewer-specific toolbar for View / Heatmap filter / Recenter / Zoom, with its own reflow.
- Removed the obsolete header Progressbar from layout to prevent the persistent pale strip after resize.
- Expanded Status/Feedback v1 for A/B toggle, empty cache, theme button, recenter, random seed, graph/stat exports, opacity lock and player-count changes.
- No generation-engine changes.

## v1.8 DEV_2
- Responsive header/layout v1 for 1080p and smaller windows.
- Formal Status/Feedback bar v1 with FR/EN user-facing messages.
- Fast generator stages remain in progress UI instead of replacing readable status text.

# v1.8 DEV_1 — 2026-08-21

- Start of the v1.8 Workflow / Accessibility / Production line.
- Full FR/EN window-title localization.
- A/B comparison reset controls (A, B, A+B) and removal of redundant summary text.
- Post-v1.7 recovery/archaeology references integrated.
- Release-note archive cleanup for v1.5/v1.6.
- No generator-engine changes.

## v1.7 STABLE — 2026-08-21
- Promoted RC_1 after user validation on Windows.
- User smoke validation: GUI operational, exports operational, exported EDM reloads correctly, and in-game View Map works without regression.
- No feature changes from RC_1; release promotion and documentation/archive hygiene only.
- Archived v1.7 DEV/RC notes under `references/release_notes/v1_7_history/`.

## v1.7 RC_1 — 2026-08-21
- Feature freeze after user validation of DEV_11_R2.
- Global release review completed; no functional blocker found.
- Fixed stale GUI window title (`DEV_9` → `v1.7 RC_1`).
- Refreshed README, release validation and current snapshot for the real v1.7 RC phase.
- No generation-engine change.

## v1.7 DEV_11 — 2026-08-21
- Final planned feature DEV before v1.7 RC.
- Corrected Terrain ID24 classification: Grass now includes and visually segments Green Grass ID16 + Dry Grass ID24.
- Added contextual terrain/object/resource IDs to graph tooltips; global mining tooltips identify both mineral ID and open-rock/Snow-family terrain IDs.
- Confirmed Statistics as a structured FR/EN user-facing surface; Stats schema v7.
- Updated forward TODOs without adding Graph↔Map coupling or extra proximity radii.
- Generation engine v1.5 unchanged.

## v1.7 DEV_10 — 2026-08-21

- Stats/debug: exhaustive Terrain/Object ID inventories.
- Stats schema v6 with normalized `/1000` densities using relevant support denominators.
- Generic interactive chart tooltips, including A/B.
- A/B slot buttons expose a visible set-state with green LED and short map identity.
- Documentation/TODO cleanup before RC preparation.

## v1.7 DEV_9 — 2026-08-21
- Mini-polish DEV_8 review: external chart values always use the left annotation lane.
- Nearby mining excludes Snow-family-covered ore; Stats schema v5.
- Nearest-opponent cue reordered to `→ [color] Pn`.
- Top-3 component labels replaced by compact `# + medal` badges.
- Generation engine v1.5 unchanged.

## v1.7 DEV_5 — 2026-08-20
- Stats chart redesign: vertical normal charts, semantic colors and segmented bars.
- Water split Ocean/Lakes; Mountain split non-snow/Snow; mining stock split outside/under Snow family.
- Building Stone states renamed by remaining stock; Forestry Resources category; Agriculture colors aligned with map view.
- Compact same-row A/B comparison.
- Land-height distribution used for height chart; global min removed from chart.
- Read-only selectable report panes and progress feedback for uncached Stats during history/comparison.
- Stats schema v3; 49 tests PASS.
- Cache LRU dédié aux statistiques dérivées pour accélérer historique et bascule A/B.
- Correction du comptage des arbres adultes : IDs 68–77 et 80–81 pris en compte ; 73–77/80–81 libellés comme arbres adultes sans inventer d’espèce.
- ID84 conservé comme « Pousse d’arbre » / « Tree sapling ».
- Graphes explicitement horizontaux (catégories Y, valeurs X) avec grille de lecture.
- Police système Unicode pour accents français (Segoe UI/Arial/DejaVu selon plateforme).
- Familles terrain ordonnées : Herbe, Montagne, Désert, Marais, Boue, Rivage, Rivière, Eau.
- Ajout de la famille Boue (23/144/145), visible même à 0 dans le graphe.
- Transitions agrégées dans leurs familles analytiques (Désert, Marais, Montagne).
- Palette graphique centralisée pour permettre une refonte couleur ultérieure sans toucher aux calculs.
- 42 tests automatisés PASS ; hashes du moteur v1.5 inchangés.

## v1.7 DEV_1 — 2026-08-20

- Première passe GIGA Stats sans modification du moteur de génération v1.5.
- Nouveau modèle d’analyse structuré : terrain, objets, minerais, poissons, végétation, Building Stones, agriculture, relief, hydrologie et starts.
- `Object ID 84` exposé comme **Pousse d’arbre / Tree sapling**, jamais comme identifiant technique utilisateur.
- Stock minier réel (quantité basse du byte ressource), distributions et occupation du support montagne.
- Building Stones 115..127 : anchors, états, stock exploitable exact et ID127 à stock nul.
- Premiers graphes intégrés : terrains, stock minier, états de pierres, végétation, hauteurs, agriculture et distances de starts.
- Exports Stats JSON, CSV et graphe PNG.
- 38 tests automatisés PASS ; hashes moteur/profils/librairie v1.5 inchangés.

## v1.6 STABLE — 2026-08-20

- RC_9 validée comme checkpoint final v1.6.
- UI/outillage post-v1.5 consolidé : Heatmap, vues Chemins/Cultures, FR/EN, inspecteur, cache/historique/A-B, raccourcis, thèmes, palettes, import SAV runtime et territoire initial exact.
- Overlay de chargement centré dans la zone carte validé en thèmes clair et sombre.
- Nettoyage des checklists, notes et manifests temporaires de RC avant packaging STABLE.
- Moteur de génération v1.5 et profils Legacy/Upgraded conservés inchangés.
- Prochaine étape : grosse passe Statistiques.

## v1.6 RC_9 — 2026-08-20

- Ajustement ultra ciblé de l’overlay de progression : en thème clair, suppression du halo/contour noir autour du texte dans la barre.
- Couleur du texte inchangée ; rendu thème sombre inchangé.
- Moteur v1.5, profils et données natives inchangés.

## v1.6 RC_8 — 2026-08-20

- remplace la popup de progression par un overlay responsive centré dans la vue carte ;
- conserve une seule barre de progression ;
- affiche le détail technique directement dans la barre ;
- adapte automatiquement la largeur et le centrage au viewport carte ;
- aucune modification du moteur de génération v1.5.

## v1.6 RC_7 — popup robuste / molette / hover menus raster

- Popup de chargement : abandon du placement absolu interne ; le contenu remplit maintenant réellement le `Toplevel` fixe 420×108, avec barre 384 px et marges symétriques de 18 px.
- Le changement de texte de progression ne modifie plus la géométrie du dialogue ni de la barre.
- Molette restaurée sur les sélecteurs raster Vue, Filtre carte thermique et Langue.
- Hover/pressed des sélecteurs raster explicitement thémé : sombre lisible en thème sombre, clair lisible en thème clair.
- Nommage de release normalisé : `DEV`, `RC`, `STABLE`; dossier de cette build `mapgen_v1_6_RC_7`.
- Moteur de génération v1.5 inchangé.

## v1.6 RC_6 — popup fixe / filtre thermique / drapeaux

- Fenêtre de chargement à géométrie fixe 420×108 : les changements de libellé ne redimensionnent plus la popup et la barre reste centrée avec marges symétriques.
- `Ressource carte thermique` renommé **Filtre carte thermique** / **Heatmap filter**, pour ne pas limiter le sélecteur aux seules ressources à terme.
- Sélecteur de langue remplacé par le même système raster coloré que Vue/Carte thermique, avec drapeaux France et Royaume-Uni dessinés par Pillow (aucun emoji dépendant du rendu Windows).
- Icônes Vue/Carte thermique, cadenas, palettes joueurs/minerais, traductions et thème clair conservés tels que validés en R5/R4.
- Moteur de génération v1.5 inchangé.

## v1.6 RC_5 — sélecteurs raster / verrouillage / finition popup

- Remplacement des emoji de couleur des listes Vue et Carte thermique par de vraies icônes raster dessinées par Pillow : rendu coloré indépendant du support emoji Windows/Tk.
- Vue : pictogrammes distincts (global, élévation, ressources, territoires, chemins, cultures, carte thermique) au lieu de simples pastilles.
- Carte thermique : pastilles raster par ressource, avec les couleurs métier centralisées.
- Verrou Carte thermique : icône raster rouge fermée / verte ouverte, sans disque Unicode gris.
- Listes Mode/Archétype élargies pour limiter les débordements des traductions.
- Fenêtre de chargement : marge horizontale symétrique autour de la barre Canvas.
- Palette joueurs, palette ressources minières, traductions, thème clair et moteur v1.5 conservés tels que validés en R4.
- Moteur de génération v1.5 inchangé.

## v1.6 RC_4 — corrections visuelles/localisation

- Palette joueurs : P9 quasi blanc/ivoire ; halo noir autour des contours initiaux colorés.
- Vue Ressources recalée sur la capture éditeur : charbon noir, fer orange, or jaune, gemmes rouge, soufre beige/ocre mieux séparé.
- Icônes colorées renforcées dans Vue et Carte thermique.
- Cadenas jaune fermé / vert ouvert pour le sélecteur de Carte thermique.
- Traductions FR/EN renforcées, y compris modes, archétypes, Élévation et Carte thermique.
- Correction robuste des listes déroulantes en thème clair.
- Fenêtre de chargement : barre Canvas unique pour supprimer le glitch de fragment ttk.
- TODO enrichi pour la future refonte UI, Outils Map et loupe flottante d’inspection.
- Moteur de génération v1.5 inchangé.

## v1.6 RC_1 — UI/outillage post-v1.5

- Moteur de génération v1.5 stable conservé sans changement de règle.
- Regroupement des ajouts post-v1.5 : Heatmap, Chemins/Terrain28, Cultures, FR/EN, inspecteur, cache LRU, historique, A/B léger, raccourcis configurables et aide F1.
- Palette joueurs P1..P20 remplacée par une candidate plus fidèle au jeu, centralisée pour validation/calibration.
- SAV v11 : extraction des coordonnées de départ d'origine depuis le bloc joueur type 6.
- Territoire initial : remplacement de l'ellipse approximative par le masque natif exact 3500 cellules / 71×71 / bord HEX6 210 cellules.
- Terrain22/28 runtime préservé à l'import SAV.
- Export nommé `MapGenV1_6`; SAV toujours copié inchangé uniquement.
- Tests modernisés sur le moteur final v1.5 et nouveaux tests SAV/territoire/cache/préférences/preview.

## v1.4 candidate — dark mode / visualization comfort
- Thème sombre/clair, préférences persistantes, overlays, drag/zoom et progression étendue.
- Projection parallélogramme à décalage de 0,5 cellule par ligne.
- P1..P20 bitmap nets, couleur joueur, non déformés.
- Contour territoire initial SAV : 3500 cellules, étendue ±35.
- Combobox corrigées en sombre et sliders click-to-position.
- Bug connu : fournitures `Défaut` à investiguer.


## v1.3.2 — editor-safe starts / snow blocking / swamp transitions
- Starts : ajout d'une marge de sécurité éditeur autour des 33 cellules natives, sans nettoyage artificiel du terrain.
- Starts : distance conservatrice accrue vis-à-vis de l'eau et exclusion stricte des objets statiques dans le halo éditeur.
- Building Stones : le footprint complet doit désormais rester hors du halo protégé du start, pas seulement l'ancre.
- Neige : `Snow129` et `Snow128` deviennent non marchables via l'accessibility statique, sur le même principe que le correctif Water.
- Marais : reconstruction systématique `Grass16 -> 21 -> 81 -> 80` depuis le masque complet ; les mini-marais de départ utilisent désormais une famille cohérente.
- Validators : ajout de contrôles d'accessibilité Snow et de chaînes de transitions Desert/Swamp/Snow.
- TODO Markdown enrichi avec les prochaines améliorations UI/statistiques demandées.
- Suppression de `docs/user_todo_20260818.txt`, désormais entièrement absorbé dans `TODO_MAPGEN.md`.
- Développé avec l'assistance de ChatGPT.

## v1.3.1 — preview crash fix / README presentation
- Correction du crash `NameError: Image is not defined` lors de la génération/rafraîchissement de l'aperçu.
- Import explicite de `PIL.Image` utilisé par le redimensionnement/zoom.
- Ajout d'un test de non-régression dédié au rendu GUI.
- README entièrement remis à jour avec une présentation du projet, les modes, archétypes, architecture des starts et état réel de la v1.3.1.
- Aucun changement dans les règles de génération Legacy/Upgraded.

## v1.3 — tooling / UX
- Ajout barre de progression par étapes de pipeline.
- Bouton seed aléatoire.
- Import EDM/MAP/SAV (SAV en lecture seule).
- Vues Global / Heightmap / Ressources / Territoires.
- Zoom par slider et molette.
- Sélecteur de toutes les tailles natives + max joueurs dynamique.
- Génération reste volontairement limitée à 768 tant que les autres tailles ne sont pas calibrées.
- Onglet Statistiques basique.
- Scrollbars sur les onglets texte.
- Export SAV non inventé : copie inchangée seulement si la source importée est déjà un SAV.
- TODO actualisé avec la généralisation future de la morphologie Upgraded.
