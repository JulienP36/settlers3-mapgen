# Settlers III MapGen — validation de l’état courant

Date : 2026-09-15

> Ce document concerne la candidate locale actuelle. La validation historique
> de la v1.7 est conservée dans
> `references/history/RELEASE_VALIDATION_V1_7.md`.

## v2.0 DEV_6_R61 — candidate locale active

- Base exacte R60 ; aucune logique de génération ou de placement n’est modifiée.
- Le libellé devient « Rayon de contrôle eau native » et son aide décrit le
  rayon mesuré depuis la bordure ainsi que la valeur `0`.
- Tous les contrôles du bonus lac/rivière sont alignés sur une seule colonne.
- Suite complète : `430 passed` ; compilation réussie.
- Self-test source (`2.0 DEV_6_R61`) et smoke-test PASS (33 validations
  Upgraded, 17 Legacy, checksum binaire). La validation Windows/éditeur/jeu
  de l’interface reste ouverte.

## v2.0 DEV_6_R60 — candidate locale historique immédiate

- Base exacte R59 ; la logique de placement et de génération des bonus reste
  inchangée.
- Le panneau lac/rivière est compacté sur quatre colonnes ; le label du filtre
  d’eau native est raccourci et les listes de forme sont accolées à leur label.
- Suite complète : `430 passed` ; compilation réussie.
- Self-test source (`2.0 DEV_6_R60`) et smoke-test PASS (33 validations
  Upgraded, 17 Legacy, checksum binaire). La validation Windows/éditeur/jeu
  de l’interface reste ouverte.

## v2.0 DEV_6_R59 — candidate locale historique immédiate

- Base exacte R58 ; les formes, profondeurs, deux anneaux de rive, bornes et
  traceur natif local des rivières bonus restent inchangés.
- `water_proximity_from_territory_border=0` désactive maintenant réellement
  le filtre d’eau native ; les valeurs positives conservent l’exclusion dans
  le rayon configuré.
- Les métadonnées du bonus ajoutent les tentatives/acceptations et les causes
  de refus par joueur et au total, sans écrire ni supprimer de terrain.
- Tests ciblés du bonus et de ses régressions : `31 passed` ; suite complète :
  `430 passed`.
- Self-test source (`2.0 DEV_6_R59`) et smoke-test PASS (33 validations
  Upgraded, 17 Legacy, checksum binaire). L’archive extraite reste à vérifier
  avant remise Windows.

## v2.0 DEV_6_R58 — candidate locale historique immédiate

- Base R57 exacte ; ses zones minérales, son panneau et la forme du lac restent
  inchangés.
- Le rayon maximal du lac/rivière est borné à `16 HEX6` et la cible maximale
  de rivières par lac à `6`; les valeurs par défaut restent `9` et `1`.
- Le bonus lac/poissons/rivière conserve `Native` ou `Hexagone`, dérive deux
  anneaux de rive et les niveaux Water0..Water7 depuis le cœur, mais construit
  désormais chaque rivière par le système natif local depuis une embouchure en
  eau. Aucun champ de distance vers l’eau existante n’est utilisé comme cible.
- Les jonctions accidentelles entre plans d’eau restent possibles si le
  relief les provoque ; elles ne sont pas recherchées. Une rivière normale
  bonus utilise `River96` sur tout son parcours, sans alternance artificielle
  des quatre IDs.
- La protection eau de la tour (`20 HEX6` par défaut) couvre toute l’emprise
  du lac/rivière même sans forçage ; l’eau/rivière existante n’est jamais
  écrasée et les poissons ne sont écrits que dans le cœur en eau.
- Suite complète R58 : `427 passed`, dont les tests
  ciblés bonus couvrent aussi l’absence de cible globale et l’ID natif unique.
  Self-test source (`2.0 DEV_6_R58`) et smoke-test PASS : 33 validations
  Upgraded, 17 validations Legacy et checksum binaire. Validation utilisateur
  Windows/éditeur/jeu encore requise.
- Validation utilisateur Windows/éditeur/jeu requise, notamment pour les deux
  formes, les routes, les états désactivés et l’aspect des sprites.
- Aucun push, tag ou release pendant cette candidate locale.

## v2.0 DEV_6_R48 — candidate locale historique immédiate

- Base R47 exacte ; R48 ajoute la forme organique compacte et les modes de
  surface égale, prorata des gisements et personnalisée pour les zones
  minérales, avec quantité moyenne par minerai.
- Les cœurs restent intégralement minéralisés ; une zone sans emprise légale
  est omise et signalée.
- Suite complète : `417 passed`. 16 sorties R47/R48 identiques sur Legacy/
  Upgraded, 256/768, deux seeds et bonus OFF ou réglages historiques ; stress
  forcé maximal PASS. Self-test source/extrait et smoke-test PASS, hashes
  protégés conformes.
- Validation utilisateur Windows/éditeur/jeu des nouveaux réglages à terminer.
- Aucun push, tag ou release pendant cette candidate locale.

## v2.0 DEV_6_R47 — candidate locale active

- Base R46 exacte ; forêts, pierres et marais validés par l’utilisateur.
- Forçage progressif D+3..D+34, emprises complètes et protection des tours.
- 16 comparaisons R46/R47 OFF identiques : Legacy/Upgraded, 256/768,
  deux seeds, avec et sans les cinq bonus.
- Suite complète : `411 passed`, trois contrôles version/documentation
  corrigés et repassés en ciblé (`3 passed`) ; 414 tests vérifiés.
- Self-test source et smoke-test PASS, hashes protégés conformes.
- Validation Windows/éditeur/jeu de R47 attendue ; zones minérales et lac
  toujours à valider. DEV6 non clôturée, aucun push ni release.

## v2.0 DEV_6_R46 — candidate locale

- Base : R45, sans push ni release.
- Chaque marais bonus `Native` exécute indépendamment le même plan natif
  global ; les quatre starts ne partagent plus une empreinte unique. Les
  collisions, transitions, replis légaux et la forme `Hexagone` restent ceux
  de R45. Le chemin sans bonus reste hors de cette branche active.
- Suite complète : `401 passed`, compilation, self-test source et smoke-test
  réussis. Les 16 comparaisons de sorties sans bonus R45/R46 sont identiques
  sur Legacy/Upgraded, deux tailles, deux seeds et deux miroirs. Les quatre
  configurations actives Legacy/Upgraded en `256×256` et `768×768` passent les
  validateurs durs. La validation visuelle utilisateur reste ouverte et R46
  n’est ni poussée ni publiée.

## v2.0 DEV_6_R45 — candidate locale

- Base : R44, sans push ni release.
- R45 étend le halo de collision aux écritures réelles de toutes les familles
  d’objets actives, y compris la passe native globale Legacy ; les empreintes
  complètes des pierres sont prises en compte sans réserver de cases vides.
- La forme `Native` des marais bonus reprend le même plan natif global
  brosse/extension/érosion et privilégie un composant complet dans le rayon
  demandé ; l’hexagone reste paramétrique et le rayon de test reste `1–20`.
- Le chemin sans bonus reste strictement hors de cette branche active.
- Suite complète : `400 passed`, compilation, self-test source et smoke-test
  réussis ; les 16 comparaisons de sorties sans bonus R44/R45 sont identiques
  sur Legacy/Upgraded, deux tailles, deux seeds et deux miroirs. Les cartes
  actives `256×256` et `768×768` passent les validateurs durs. La validation
  visuelle utilisateur reste ouverte et R45 n’est ni poussée ni publiée.

## v2.0 DEV_6_R44 — candidate historique immédiate

- Base : R43, sans push ni release.
- R44 place les adultes des forêts bonus avant les pousses, en dérivant le
  noyau adulte de la quantité demandée et de l’espacement `3 HEX6`.
- Les passes globales arbres, pierres, décorations et objets natifs consultent
  les écritures bonus réelles, dont l’empreinte complète des rochers, avec un
  halo de collision commun. Aucun bonus n’est posé puis supprimé.
- Les marais bonus restent inchangés dans R44 ; le chemin sans bonus reste
  strictement inchangé.
- Suite complète : `400 passed`, compilation, self-test et smoke-test source
  réussis.
- Les cartes actives Legacy/Upgraded en `256×256` et `768×768` passent les
  validateurs durs ; les tests de hitbox couvrent les cinq bonus actifs.
- Seize comparaisons R43/R44 sans bonus sont identiques sur Legacy/Upgraded,
  deux tailles, deux seeds et les miroirs `0`/`3`.
- L’archive R44 extraite passe le self-test (`2.0 DEV_6_R44`) et le smoke-test
  (`33` validations Upgraded, `17` validations Legacy, checksum binaire).

## v2.0 DEV_6_R42 — candidate locale

- Base publiée : `v2.0 DEV_5`, validée sur `dev`.
- État : candidate locale construite exclusivement depuis R41, non publiée et non promue comme DEV6
- R42 : le mini-marais utilise une liste déroulante de formes (`Native` ou
  `Hexagone`) et un rayon borné `1–20` pour les tests ; l’hexagone scale avec
  ce rayon et `Native` réutilise le plan natif global des marais. Les anciens
  profils contenant `cells_per_player` sont normalisés vers ce modèle.
  Validation ciblée et suite complète à consigner.

## v2.0 DEV_6_R41 — candidate historique immédiate
- R41 : première liste de formes du mini-marais, remplacée par R42 après
  correction du rayon hexagonal et de la forme native.

## v2.0 DEV_6_R40 — candidate historique
- R40 : les familles d’objets Custom modifiées sont désactivées avant le
  passage natif, puis posées une seule fois par leur couche propriétaire. Les
  bonus ne réservent plus de zones vides et aucun objet n’est supprimé après
  leur placement. Le cas Legacy `arbres=0 %`, `pierres globales=0 %`, bonus
  pierres seul est couvert par une régression : zéro arbre et 30 ancres de
  départ. Validation ciblée : `56 passed`; suite complète à consigner.
  complet.
- R36 : corrige la forêt de départ dans Custom Legacy et Custom Upgraded :
  presets de bonus désactivés par défaut, interrupteur en tête de chaque
  panneau, défaut `30` adultes + `20` pousses par joueur, adultes placés avant
  les pousses et espacement commun de `3 HEX6`. Le rayon minimal est dérivé de
  la population totale et de l’espacement ; les anciens champs de rayon de
  forêt sont ignorés et l’enveloppe peut s’étendre si nécessaire.
- R36 : ajoute le switch d’objets compatibles avec l’herbe sur les terrains
  `18`, `19` et `24` uniquement ; le terrain rocheux `34` reste exclu. Les
  bonus sont additionnels et hors quotas globaux.
- R37 : plafonne forêts, adultes et pousses à `100`, conserve le défaut
  `30 + 20` et partage la couleur des pousses entre carte et graphiques.
- R37 : pierres de départ à `15` ancres par joueur par défaut, maximum `50`,
  moyenne `10`, stock et rayon dérivés sans contrôles de rayon. La catégorie
  Bonus passe en premier et les cinq activations atteignent les deux bases
  Custom sans changer de moteur.
- R38 : le switch herbe protège les réservations et rend les supports herbe,
  herbe sèche et détails herbe 1/2 utilisables par les bonus lorsqu’il est
  actif. Legacy et Upgraded publics utilisent le contrat Custom via des
  presets, avec les bonus désactivés par défaut ; leurs moteurs internes
  restent séparés. La case globale de forçage à distance étendue est active
  pour les cinq bonus, désactivée par défaut, avec indication de son usage.
- R38 : le pont Legacy utilise le bon flux aléatoire pour les cinq bonus ; les
  transitions de mini-marais et les rives de lacs restent légales même avec
  les variantes d’herbe. Suite complète : `393 passed`.
- R39 : le cas `bonus de départ désactivés + pierres globales à 0 %` ne laisse
  aucun objet pierre, y compris dans l’empreinte technique d’un départ. Le
  stock moyen des rochers bonus utilise `full_range_mean_tilt`, comme le stock
  global. Le forçage étendu n’a pas été modifié. Validation ciblée : `6 passed`.
- R34 : la section Rivières expose un taux global `0–500 %` ; à `100 %`, la
  boucle native, le seuil PRNG, les connexions, les longueurs et le nettoyage
  sont conservés ; les autres valeurs ne créent pas de routeur séparé.
- R33 : les taux de terrains passent directement dans les recettes natives de
  brossage, d’expansion et d’érosion ; à `100 %`, la sortie reste identique et
  les autres valeurs ne créent pas de système séparé de zones candidates.
  Les grandes formes natives, les variations de taille et les transitions
  légales sont conservées.
- Périmètre : sections Custom **Terrains**, **Arbres**, **Pierres de
  construction** et **Décorations** raccordées aux deux moteurs, avec
  contrôles bornés et invariants conservés, plus les corrections ciblées du
  défilement, du redimensionnement et du bandeau sombre.
- R24 : stock moyen par pierre au pas de `0,5`, loi complète `1–12` avec
  probabilité non nulle pour chaque état, uniforme à `6,5` et biais progressif
  ailleurs ; groupes structurés comme les forêts, distance mixte 3 HEX6 et
  libération des emprises épuisées. Les bonus de départ et les piles épuisées
  sont mesurés séparément du quota global.
- R25 : largeur naturelle appliquée aux groupes de l’onglet Générateur ; les
  tableaux `Répartition` et `Ressource moyenne` partagent l’ordre champ,
  unité, ressource et maximum ; les champs Spinbox/Combobox gardent leur
  molette native.
- R26 : chaque famille de décoration possède un taux d’apparition `0–500 %` ;
  `100 %` conserve la population du profil sélectionné. Les paramètres de
  terrain, d’identifiants et de collision restent internes.
- R27 : les lignes de Décorations réservent un emplacement d’icône `16×16`
  sans modifier la hauteur des champs ; le graphique Familles d’objets détaille
  les sous-familles ; les récifs suivent `0 %` en Legacy et `100 %` en Upgraded.
- R28 : un taux de récifs supérieur à 0 fonctionne désormais aussi dans un
  Custom basé sur Legacy.
- R29 : la calibration Upgraded/Custom des récifs est fixée à `20` pour
  768×768 ; les sprites minerais `16×16` sont intégrés et les lignes de
  ressource moyenne n’ont plus de colonne vide.
- R29 : les taux de Boue, Désert, Herbe sèche, Détails décoratifs et Marais
  sont appliqués avant les objets ; les lacs, rivières, neige et relief rocheux
  restent natifs, et les décorations dépendantes sont grisées effectivement.
- R30 : `0 %` est réservé aux familles désactivées ; une famille activée est
  bornée à `1–500 %`. Le paramètre Boue Upgraded reste à zéro dans le profil
  natif, mais Custom peut désormais activer le même plan de génération.
- R33 : le contrôle strict des transitions HEX6 reste nul sur les cartes Custom
  contrôlées. L’épaisseur côtière est utilisable après dérivation d’un profil
  Legacy.
- R35 (historique) : les cinq bonus de départ sont actifs dans Upgraded : forêt, pierres,
  mini-marais, zones rocheuses charbon/fer/or et mini-lac hexagonal avec
  poissons/rivière. Ils sont placés après les starts, réservés sans
  chevauchement et exclus des quotas globaux ; l’eau native proche (`150 HEX`
  depuis la bordure de territoire) supprime le lac redondant. Les zones
  rocheuses ont un cœur plein sans modification d’altitude ; les formes
  compatibles restent natives et les valeurs de minerai/poisson reprennent
  les moyennes globales.

Il n’existe aucun moteur Upgraded v1.5 actif. La calibration 768 appartient au
profil actif de l’Upgraded indépendant ; la bibliothèque native 768 reste la
seule ressource de compatibilité/calibration conservée à ce titre. Toutes les
tailles du contrat restent générables et exportables.

## Contrôles de remise

R37 : compilation, tests directs Custom Legacy/Upgraded, self-test source et
smoke-test PASS ; archive de `330` fichiers revalidée après extraction et
ré-emballage déterministe identique. La suite pytest n’est pas disponible dans
cet environnement.
R36 : **385 tests réussis**, compilation, self-test source et smoke-test PASS ;
la candidate reste locale et n’est ni poussée ni publiée comme release.
R35 : **381 tests réussis**, compilation, autotest source et smoke-test PASS ;
archive extraite et ré-emballée à l’identique, **328 fichiers**, SHA-256
`62231b1cf644dc7aed1b5b2e15955e5cdbf1634a6743407c6aee29e687b0634e`.
R34 : **374 tests réussis**, autotest source/extrait et smoke-test PASS ; archive
extraite et ré-emballée à l’identique, 327 fichiers.
R33 : **369 tests réussis**, autotest source et smoke-test PASS ; archive extraite,
auto-test/smoke-test, suite complète et ré-emballage déterministe PASS.
R29 : **361 tests réussis**, autotest source et smoke-test PASS ; archive extraite,
autotest/smoke-test, tests ciblés et ré-emballage déterministe PASS.

- suite complète de tests Python au vert ;
- self-test source et self-test après extraction ;
- archive source complète avec `references/` inclus ;
- hashes protégés inchangés ;
- smoke-test Legacy/Upgraded et validation Windows lorsque le candidat est
  transmis à l’utilisateur.

Ne pousser qu’un checkpoint DEV complet après validation explicite de l’ensemble
de son périmètre. Cette candidate R37 ne constitue pas cette autorisation et ne
constitue pas une release.
