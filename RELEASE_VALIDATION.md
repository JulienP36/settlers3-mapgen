# Settlers III MapGen — journal de validation

## Checkpoint 2.0 DEV_9 — Grandes îles

Périmètre R25 validé et clôture/publication explicitement autorisées le 2026-10-04.
Renommage traduit de la source alternative, clés sauvegardées conservées.
R25 : 818 tests PASS, sept cartes/quatre exports, R21/Classique exactes ;
compilation, hashes protégés et auto-test extrait PASS.
Finalisation : 41 tests ciblés PASS (34,56 s), libellés FR/EN/DE/ES PASS ;
smoke Legacy/Upgraded et checksum PASS, compilation/hashes protégés PASS.
Code de génération identique à R25 ; suite complète R25 réutilisée (nom/docs seuls).
Auto-test du ZIP final à consigner lors de sa livraison.
Anciennes validations non consignées hors focus transférées au bilan DEV10 ;
aucune confirmation Windows/en jeu inventée. Bilan : docs/DEV_9_CHECKPOINT.md.

## Historique — candidate locale 2.0 DEV_9_R25

Finition du bruit montagneux ; côtes source R24 conservées.
818 tests PASS (540,98 s), 35 ciblés PASS ; sept cartes/quatre exports PASS.
Six côtes R24 exactes, deux cartes R21 et deux Classique exactes.
Compilation et hashes protégés PASS ; gain local ~32–35 %, total variable.
Archive contrôlée : CRC, parité source et auto-test extrait PASS.
Notes : `references/dev_notes/DEV9_R25_ROUNDED_MOUNTAINS.md`.
Grandes îles validée par l’utilisateur le 2026-10-04.
Clôture globale DEV9 à décider après revue des reports ; aucun push DEV9.

## Candidate précédente 2.0 DEV_9_R24

Essai Simplex multi-échelles local, sans warping du bruit côtier/intérieur.
Surface source et construction insulaire conservées ; résultats par seed
et proportions effectives différents. Qualification consignée avant livraison
avec rendus réels, contrats de terrain, exports, tests et mesures de temps.
810 tests PASS (538,32 s), 43 ciblés PASS ; sept cartes et quatre exports
PASS, deux cartes R21 exactes. Compilation PASS.
R21 conservée ; rivières R20 et contrôles R23 inchangés.
Temps sur trois paires : aperçus +0,2–0,8 s, complet variable selon cas ;
ZIP et auto-test extrait contrôlés avant livraison.
Rendu Windows à valider ; aucun push DEV9.
Notes : `references/dev_notes/DEV9_R24_MULTISCALE_SIMPLEX.md`.

## Candidate précédente 2.0 DEV_9_R23

Source R21 sélectionnable, détails du contour actuel légèrement arrondis,
molette verrouillée sur champs désactivés et resets individuels.
Six champs historiques exacts ; deux cartes R21 exactes (Area/départs),
sept cartes actuelles et quatre exports MAP/EDM contrôlés PASS. Deux Classique
restent exactes à R22.
810 cas vérifiés : suite 806 PASS / 4 écarts corrigés, puis 35 contrôles
sources/diagnostics et 16 contrôles maintenance/paquet PASS ; 106 ciblés PASS.
Compilation PASS ; ZIP/auto-test extrait contrôlés avant livraison.
Temps grand témoin 768/20 : complet ~13→18 s, aperçu ~3,4 s.
Rendu/ergonomie Windows à valider ; aucun push DEV9.
Notes : `references/dev_notes/DEV9_R23_SAVED_RELIEF_AND_LOCAL_RESETS.md`.

## Candidate précédente 2.0 DEV_9_R22

Alternative de bruit sans déformation des coordonnées, pointes légèrement
atténuées. Six champs, sept cartes et quatre exports PASS ; 92 ciblés PASS
(274,94 s). Deux Classique exactes à R21 ; 793 tests PASS (722,32 s), compilation PASS.
Rivières, profils de seuils et deux moteurs natifs exacts aux octets R21.
Temps isolés comparés sur cinq cas ; ZIP et auto-test extrait contrôlés.
Rendu Windows à valider ; aucun push DEV9.
Notes : `references/dev_notes/DEV9_R22_UNWARPED_MIDPOINT.md`.

## Candidate précédente 2.0 DEV_9_R21

Complément du détail côtier après réserve utilisateur sur R20 validée.
Six comparaisons source, sept cartes complètes et quatre exports contrôlés PASS ;
deux Classique exactes. 792 cas vérifiés : suite 791 PASS / ancienne attente R20
du numéro Windows corrigée, puis 16 contrôles paquet/maintenance PASS.
91 ciblés PASS, compilation PASS. Rendu Windows R21 requis.
Rivières et neige 200 exactes R20 ; aucun push DEV9.
Temps comparés sur cinq cas : 512/15 plus lent, recontrôlé ; rendu et durée
complète Windows à valider. Coût direct du détail ~0,01 s sur 512/15.
Notes : `references/dev_notes/DEV9_R21_UNIFORM_COAST_DETAIL.md`.

## Candidate précédente 2.0 DEV_9_R20

Détail des côtes contraintes et longueur Amélioré selon la terre connectée,
branches conservées. Neige 200. 789 tests PASS (578,96 s), 88 ciblés PASS,
7 cartes complètes et 4 exports MAP/EDM contrôlés ; deux Classique exactes.
Six comparaisons de masques et trois paires 768/42 avec 4/8/20 joueurs.
Cinq paires de temps sans validations concurrentes. R20 explicitement validée
par l’utilisateur le 2026-10-03 : Grandes îles, côtes et rivières retenues en l’état.
Aucun push DEV9. Notes : `references/dev_notes/DEV9_R20_COAST_DETAIL_AND_LOCAL_RIVERS.md`.

## Candidate précédente 2.0 DEV_9_R19

Raffinement hiérarchique des côtes et montagnes Grandes îles. Calibration R18
conservée. 785 tests PASS (692,12 s), 14 champs et 7 cartes qualifiées,
4 exports MAP/EDM PASS. Temps complets comparés sur cinq cas sans jobs
concurrents : quatre plus rapides, un +0,16 s ; aperçu 768/4 +0,58 s.
Retour visuel R19 très positif ; côtes contraintes et rivières nombreuses îles
à affiner ; neige 195 demandée pour la suite. R18 : proportions validées provisoirement, gain visuel insuffisant.
Aucun push DEV9 ; R17 et rivières R16 validées.
Notes : `references/dev_notes/DEV9_R19_MIDPOINT_ISLAND_SHAPES.md`.

## Candidate précédente 2.0 DEV_9_R18

Formes, proportions et coût Grandes îles. 783 cas vérifiés : suite 782 PASS (504.29 s), ancien témoin géométrique
actualisé puis six tests PASS. 14 paires de relief, 14 cartes/quatre exports PASS. Temps du relief réduit ; un cas complet +1,4 s (terrains
natifs). Proportions R18 validées provisoirement ; gain visuel insuffisant. Aucun push DEV9.
Contrôle Windows attendu. R17 validée par l’utilisateur le 2026-10-03.
Notes : `references/dev_notes/DEV9_R18_ISLAND_SHAPES_AND_BALANCE.md`.

## Candidate précédente 2.0 DEV_9_R17

Raccordement des défauts et mini-marais unique. 780 cas vérifiés : suite 775 PASS ; nommage et quatre anciennes attentes
de bonus actualisés puis 12 contrôles PASS. Sept cartes et huit exports PASS ; auto-test
source PASS. Contrôle Windows des raccordements R17 attendu. Aucun push DEV9. R16 rivières Amélioré validée
par l’utilisateur le 2026-10-03, algorithme inchangé. Aucun push DEV9.
Notes : `references/dev_notes/DEV9_R17_PROFILE_DEFAULTS.md`.

## Candidate précédente 2.0 DEV_9_R16

Amélioré : nombre et longueur adaptés à la taille et à la terre réelle.
772 tests PASS ; 22 cartes et six exports PASS. Rivières validées par l’utilisateur. Aucun push DEV9.
Notes : `references/dev_notes/DEV9_R16_RIVER_SIZE_SCALING.md`.

## Historique — candidate locale 2.0 DEV_9_R15

Quantité Amélioré générale et défaut Grandes îles.
22 cartes complètes et six exports PASS. Suite : 766 PASS / une assertion
de version R14 corrigée ; 123 contrôles ciblés finaux PASS. Windows requis. Aucun push DEV9.
Reprise : `references/dev_notes/DEV9_R15_RIVER_QUANTITY.md`.

## Historique — candidate locale 2.0 DEV_9_R14

Algorithme de rivières général dérivé du natif, sélectionnable dans Générateur.
Classique reste le défaut ; relief R13 inchangé. Suite complète : **761 PASS**
(499,02 s). Neuf paires complètes, six exports et six contrôles bruit/miroirs
PASS. Compilation et auto-test source PASS. Livraison après auto-test extrait.
Validation Windows requise ; aucun push DEV9.
Reprise : `references/dev_notes/DEV9_R14_SELECTABLE_IMPROVED_RIVERS.md`.

## Historique — candidate locale 2.0 DEV_9_R13

Profils de base chargés en place ; Profil personnalisé conditionnel.
Variation fine côtière sur Grandes îles, traceur natif inchangé.
Sept paires complètes qualifiées ; quatre exports MAP/EDM exacts à la relecture.
Suite : 745 PASS / une assertion de version R12 corrigée puis revalidée
parmi 16 contrôles version/maintenance PASS ; 746 cas contrôlés.
Contrôle Windows et rendu des rivières requis.
Aucun push DEV9. Reprise : `references/dev_notes/DEV9_R13_PROFILES_AND_COASTAL_RELIEF.md`.

## Historique — candidate locale 2.0 DEV_9_R12

R11 rejetée : ses restrictions contredisaient la fonction des onglets.
R12 fournit l’éditeur commun, trois profils de base, sources libres distinguées
entre compositions et bruits, fusions/masques/seuils réellement consommés.
Six cartes via Custom identiques aux presets R11/R10 ; 31 tests de composition
et 46 contrôles qualification/preview/packaging PASS. **739 tests PASS**
(474,46 s) en suite complète ; trois contrôles ciblés du dernier masque à force
zéro PASS. Quatre exports MAP/EDM relus exactement. Compilation et auto-test
source PASS ; ZIP livré après auto-test extrait. Validation Windows
requise. Aucun nouveau correctif de relief/traceur pour les longues rivières.
Détails : `references/dev_notes/DEV9_R12_COMMON_ARCHETYPE_EDITOR.md`.
Aucun push DEV9.

R11 : 703 tests PASS mais interface rejetée par l’utilisateur.
R10 : amélioration partielle ; petites cartes et côtes encore à corriger.

## Historique — candidate locale 2.0 DEV_9_R9

Corrections Classique et traceur natif, autorisées le 2026-10-01. Parité du
relief/rivières/transitions sur les cas vérifiés ; validation en jeu Windows
R9 à recevoir. Grandes îles reste indépendante, heightmaps témoins R8
inchangées ; longues rivières encore à affiner. Qualification et résultats :
`references/dev_notes/DEV9_R9_QUALIFICATION.json` et
`references/dev_notes/DEV9_R9_CLASSIC_CORRECTIONS.md`.
Suite complète finale : **676 tests PASS** (371,79 s), compilation et auto-test
source PASS. 14 comparaisons natives exactes et 18 exports contrôlés.
Aucun push DEV9. Les validations ci-dessous sont historiques.

## Historique — candidate locale 2.0 DEV_9_R8

Prototype de recherche intégré : pente côtière initiale non nulle, progression
adaptée à chaque île et bruit intérieur stabilisé. Géométrie R5, traceur/taux
natifs et relaxation conservés. Les 18 champs de hauteur et masques comparés
correspondent exactement au prototype autorisé. Export réel Amélioré 384/8,
seed42 : contrats bloquants, checksums, Area et départs EDM/MAP vérifiés.
25 tests ciblés et auto-test source PASS. La suite complète a donné 658 PASS
et un échec documentaire : ce journal mentionnait encore R7 comme candidate
courante. Cette entrée corrige le journal ; revalidation ciblée consignée
dans `references/dev_notes/DEV9_R8_QUALIFICATION.json`.

Validation Windows du relief et des rivières attendue. Les marches de 55/108
cases ne sont pas approuvées ; longueur/quantité et rares îles pauvres restent
à affiner après retour utilisateur. Candidate locale, aucun push DEV9.

## Candidate précédente 2.0 DEV_9_R7 — historique

Relief continu sans plancher 14 ni enveloppe séparée, formes R5 conservées,
masque retiré de Contribution brute. 51 tests ciblés preview/UI/packaging PASS.
Cinq comparaisons de relief et trois cartes Amélioré qualifiées : contrats
bloquants PASS, formes R6 conservées. Compilation, auto-test source, relecture
EDM/MAP et hashes protégés PASS. Suite complète : **658 PASS** en 580.72 s. Le ZIP de livraison conserve les 104
fichiers de références actualisés et est auto-testé après extraction.
Voir `references/dev_notes/DEV9_R7_QUALIFICATION.json`.
Aucun push ; validation visuelle de la heightmap attendue. Quantité de rivières
à revoir ensuite.

## Candidate précédente 2.0 DEV_9_R6 — historique

- Formes/processus R5 validés pour la 2.0 et un joueur par île confirmé par
  l’utilisateur. R6 conserve la géométrie et affine uniquement le relief.
- Terres basses côtières élargies et amplitude du relief aléatoire favorisée
  à l’intérieur réel par la distance HEX6 à la mer ; relaxation native active.
- Tests ciblés initiaux : 16 PASS ; contrôle côtier étendu et packaging après
  ajustement du plancher de relief : 7 PASS. Suite complète : **658 PASS** en
  606,47 s.
- Six cartes Amélioré (384/8, 512/15, 768/20, deux seeds par taille) : tous
  contrats bloquants PASS. Cinq comparaisons de relief : labels R5 identiques,
  p95 côtier 6–7 → 3–4 et montagnes plus loin de la mer. Mesures compactes dans
  `references/dev_notes/DEV9_R6_QUALIFICATION.json`.
- Compilation, auto-test source, hashes protégés et relecture des exports
  d’exemple PASS. ZIP contrôlé par l’auto-test après extraction avant livraison,
  avec les 102 références actualisées et les quatre fichiers de l’exemple R6.
  Aucun push ; validation visuelle du relief et des rivières encore attendue.

## Candidate précédente 2.0 DEV_9_R5 — historique

- Contours infléchis avant les contraintes d’espace et relief progressif
  près de la mer, avec lissage natif et masque visible dans Archétype.
- Suite Grandes îles : **16 passed**, dont vérification des hauteurs basses
  sur les trois premières couronnes côtières. Cartes Amélioré qualifiées
  384/8, 512/15 et 768/20 : tous les contrats bloquants PASS.
- Exemple exporté dans `examples/dev9_r5/` ; données compactes et comparaison
  avec R4 dans `references/dev_notes/DEV9_R5_QUALIFICATION.json`.
- Suite complète : **658 passed** en 367,75 s. Compilation et auto-tests
  source/paquet extrait PASS ; hashes protégés inchangés. L’archive conserve
  les **100 fichiers de références** et les quatre fichiers de l’exemple R5.
- Candidate locale, aucun push ; validation visuelle Windows attendue.

## Candidate précédente 2.0 DEV_9_R4 — historique

- Masques indépendants, surface proche de 50 % avant rivages et relief local
  continu, suivi du lissage natif. Preview en trois étapes avec masque visible.
- Générations Amélioré 384/8 (deux seeds), 512/15, 768/20 : tous les contrats
  bloquants PASS, 52,52–53,25 % de terre finale ; surfaces d’île min/max ≥0,971.
- Exemple exporté EDM/MAP/PNG/rapport dans `examples/dev9_r4/`.
- Compilation et auto-test source PASS. Suite complète : **657 passed**, une
  assertion de version Windows restée à R3 corrigée ; les **6 tests packaging
  PASS** ensuite, soit **658 cas vérifiés**. Le test de paquet extrait et son
  auto-test passent. Profil, bibliothèque et workflow protégés inchangés.
  Archive avec les **98 fichiers de références** actualisés.
- Validation visuelle Windows attendue. R4 est locale, aucun push.

## Candidate précédente 2.0 DEV_9_R3 — historique

- La relaxation native mode 0 est réappliquée à la hauteur finale des îles ;
  la preview macro suit ce comportement.
- Le relief est relevé doucement dans l’intérieur d’une île seulement quand la
  relaxation a fait disparaître son sommet montagneux. L’écart côtier reste
  protégé ; un chenal marin d’au moins 8 cellules ou 1,5 % de la carte est
  réservé entre les îles et au bord de carte.
- Générations qualifiées : Upgraded 384/4, 512/4, 768/4 ; Legacy 384/8 et
  Legacy 768/20 via la suite dédiée. Contrats de départ, séparation, montagne,
  marais et rivières PASS ; terre mesurée : 43,4 %, 49,1 %, 47,4 % et 24,5 %
  pour les quatre premières configurations.
- `python -m pytest tests/test_large_islands.py -q` : **10 passed**.
  Première suite complète : **649 passed**, deux tests de maintenance ont
  échoué uniquement parce que le snapshot et la matrice indiquaient encore R2 ;
  les deux tests ont passé après correction des références. `compileall` PASS.
- Auto-test source et auto-test après extraction du ZIP : PASS ; profil Legacy,
  bibliothèque native et références protégés par leurs hashes. Le ZIP contient
  366 fichiers, 96 références et les quatre fichiers de l’exemple R3.
  Candidate locale ; aucune publication ni push. Validation visuelle Windows à
  venir.

## Candidate précédente 2.0 DEV_9_R2 — historique

Les îles sont créées séparément, une par joueur ; chaque rivière manquante reçoit une relance du traceur natif limitée à son île. Contrôles dédiés, preview liée aux joueurs. Suite complète R2 : 651 tests réussis ; compilation et auto-test des ressources PASS, y compris après extraction du ZIP. L’archive contient 95 références et l’exemple R2. Validation visuelle Windows à venir. Aucun push.

## Checkpoint DEV publié — v2.0 DEV_8 (candidate R86)

- L’utilisateur confirme la validation visuelle Windows R85.
- R86 affiche « Personnalisé » dans le sélecteur Archétype quand le profil a
  été édité ; le statut revient à Classique/Continental quand un profil nommé
  est sélectionné.
- 641 tests, compilation, smoke-test et self-test du ZIP extrait PASS.
- Tests multi-tailles et correction des rivières Custom sont déclarés terminés
  par l’utilisateur. DEV8 est clôturée ; tous les travaux restants sont DEV9.

## Historique de validation — candidates R63 à R85


- Le défaut global de marge du domaine passe de 5 % à 0 % pour tous les
  nouveaux profils, y compris Legacy. Le relief Legacy reste identique, car sa
  source native ignore le domaine fini des providers de bruit.
- Le preset Continental Custom R53 hérite de 0 % : domaine source sur toute la
  carte, transition de bord conservée à 8 % (31 cases à la référence 768).
  L’ancien réglage explicite de 5 % garde son sens et résout toujours 18 cases.
- À 256², seed `20260920`, la preview R53 sans marge affiche 23,9 % d’eau et
  une distance médiane au premier terrain de 11 cases, contre 45,6 % et 30 cases
  avec l’ancien cadre.
- Qualification Custom (256/384/768, deux seeds, 4 joueurs, miroir 0) : départs
  6/6 et déterminisme PASS ; macro 4/6. Les deux cartes 768 dépassent le plafond
  de terre (86,2–86,8 % pour un maximum de 85 %). Il faudra juger cette couverture
  et, si nécessaire, recalibrer le profil tout en gardant la marge à 0 %.
- Vérifications ciblées de profils, providers, masques, déterminisme et
  invariance Legacy PASS ; `compileall` et self-test de l’application PASS.
  `pytest` absent, suite complète non exécutée. Validation Windows/en jeu
  restante ; R63 n’est pas un checkpoint DEV validé.


Date : 2026-09-25

> Ce document concerne la candidate locale actuelle. La validation historique
> de la v1.7 est conservée dans
> `references/history/RELEASE_VALIDATION_V1_7.md`.

## v2.0 DEV_8_R62 — candidate locale

- L’EXE joint porte le même SHA-256 que l’audit statique existant. Relecture
  directe du désassemblage `0x5176BD–0x51771F` : le premier index est le `0x600`
  conservé par le raffinement, puis `+0x97` avec une soustraction de la surface
  dès que l’index l’atteint. Le balayage fait `4 × surface` tentatives.
- Les comparaisons `coordonnée < 8` et `coordonnée > taille−8` précèdent
  l’appel PRNG ; celui-ci est ensuite comparé à `0x07D0`. À 256², R62 attend le
  premier point admissible `(row=92,col=8)`.
- R61 utilisait à tort `0xC000` ; ses assertions ne validaient que la constante
  R61. R62 corrige le test dans les deux moteurs. Les bonus gardent leur
  embouchure et le premier pas partagé.
- Neuf tests de `test_custom_river_sections.py`, deux tests de
  `test_native_river_scan.py`, deux contrôles de bonus et trois diagnostics de
  packaging ont passé en exécution directe (16 fonctions). `compileall` et les
  sept contrôles de `inspect_package()` passent. Les hashes protégés sont
  conformes : profil Legacy
  `bdd091afeafcce88aa558d656e6d2728d101440368642e0c50568821d3f25c85`,
  bibliothèque native
  `fbc43b2bba99f995c659753ef423656dfd3b61df8308cc186a7cae72b5db3d4d`.
  La suite complète `pytest` n’a pas démarré : `pytest` manque à l’interpréteur.
- Archive source de 258 fichiers et self-test exécuté après extraction : PASS,
  version `2.0 DEV_8_R62`, sept contrôles réussis et hashes protégés conformes.
  Écart Custom restant intentionnel : taux `0,4`, nettoyage post-transition
  et relief personnalisé. À comparer séparément une fois le Legacy natif
  vérifié dans le jeu. R62 n’est pas validée comme checkpoint DEV.

## v2.0 DEV_8_R61 — candidate locale supersédée

- R61 utilisait `0xC000`, contrairement au curseur `0x600` lu dans le
  désassemblage. Ses 13 tests ciblés passaient mais verrouillaient cette erreur
  interne ; l’auto-test de paquet ne contrôlait pas la parité native.
- Sa correction de l’ordre marge-avant-PRNG est conservée ; son premier-pas
  partagé pour les rivières bonus est également conservé en R62.

## v2.0 DEV_8_R60 — candidate locale

- Étend aux deux moteurs le recalage R59, limité aux profils de relief Custom
  avec source non native ou couche de noise active : taux effectif à `0,4 ×`
  la valeur demandée, suppression après transitions, copie miroir et reprise
  différée des composantes HEX6 sans contact Eau 0–7/Rive, et gate dur
  `CUSTOM_RIVER_WATER_CONNECTION`.
- Parité native vérifiée : fournir explicitement le profil continental Legacy
  natif donne, dans les deux moteurs, les mêmes champs `height`, `terrain`,
  `variant` et `marker` que le chemin natif implicite.
- R53 adaptatif, seeds `20260920–22` : les comptes Legacy et Upgraded sont
  égaux sur les neuf cartes : médianes `918` à 256², `1325` à 384² et `2238`
  à 512². Aucune sortie n’a de fragment orphelin. Les 24 intégrations
  moteur/seed/mode miroir (trois seeds, modes 0–3, Legacy et Upgraded) passent
  le gate strict et tous les contrôles durs à 384². Le cas Legacy seed
  `20260921`, miroir 1, élimine le fragment de 15 cases après la copie miroir.
- Les neuf fonctions de `test_custom_river_sections.py` passent en exécution
  directe ; `compileall` passe. `pytest` n’est pas installé dans
  l’interpréteur disponible. Les hashes protégés correspondent aux valeurs
  attendues : profil Legacy `bdd091afeafcce88aa558d656e6d2728d101440368642e0c50568821d3f25c85`,
  bibliothèque native `fbc43b2bba99f995c659753ef423656dfd3b61df8308c186a7cae72b5db3d4d`.
- ZIP source de 257 fichiers : extraction puis `run_gui.py --self-test` PASS,
  version `2.0 DEV_8_R60` et sept vérifications réussies.
- Le test visuel Windows reste à faire : comparer Legacy/Upgraded avec R53
  adaptatif, mêmes seeds, en particulier à 256². R60 n’est pas validée comme
  checkpoint DEV.

## v2.0 DEV_8_R59 — candidate locale

- Cause ciblée reproduite : à 384², seed `20260920`, le nettoyage natif en
  place effaçait 38 cases de rivière et laissait deux composantes déconnectées
  de 1 et 3 cases.
- Le taux demandé reste inchangé dans l’UI ; le chemin Upgraded avec source ou
  couche de relief bruitée applique un multiplicateur `0,4`. Le Legacy, les
  profils natifs et le chemin sans noise actif gardent leur comportement.
- Les composantes HEX6 isolées Eau/Rive sont retirées après les transitions et
  un gate dur `CUSTOM_RIVER_WATER_CONNECTION` vérifie toutes les composantes du
  Custom généré.
- R53 adaptatif, seeds `20260920–22` : médianes des cases de rivière Legacy →
  Custom `737 → 918` à 256², `1461 → 1325` à 384² et `2201 → 2238` à 512² ;
  seed `20260920` à 768² : `4234 → 4251`. Les neuf sorties 256²–512² et la
  sortie 768² ne contiennent aucune composante orpheline après correction.
- `compileall` PASS. Les six fonctions de test du fichier dédié ont été
  exécutées directement et passent. Le pipeline complet `MapGenerator`
  Custom R53 à 384² passe, avec la validation stricte ; les quatre modes
  miroir passent aussi la connectivité sur le noyau Upgraded. La parité
  explicite du profil natif Upgraded reste exacte. La commande pytest n’a pas
  pu s’exécuter : le module `pytest` est absent de cet environnement.
- Packaging source `257` fichiers et auto-test GUI depuis le ZIP extrait :
  PASS ; les ressources protégées conservent leurs hashes attendus. La
  validation visuelle Windows est requise, en particulier pour la densité à
  256². R59 n’est pas validée comme DEV.

## v2.0 DEV_8_R57 — candidate locale

- Option d’échelle adaptative ajoutée à l’onglet Archétype ; désactivée par
  défaut pour préserver le rendu des profils existants.
- R53 décoché retrouve bit à bit ses previews de référence sur 256/384/512/768 ;
  coché à 768, le résultat reste identique. Avec la seed `20260920` et le
  miroir 0, la part montagne/neige en mode adaptatif est `3,34/0,08 %` à 256,
  `7,24/0,87 %` à 384 et `9,95/1,68 %` à 512. À 256, la fréquence fBm passe
  de 4 à 3,55 ; la preview adaptative est déterministe.
- `compileall`, calcul direct du facteur, hashes protégés, validation de
  l’archive source et auto-test du ZIP extrait : PASS. La suite pytest n’a pas
  pu être lancée, car `pytest` manque dans l’interpréteur disponible.
- Validation visuelle Windows sur les petites et grandes tailles : requise ;
  R57 n’est pas encore un checkpoint DEV validé.

## v2.0 DEV_8_R56 — candidate locale

- Profilage ciblé de l’onglet Archétype : six miniatures de fusion variées
  passent de ~32 ms par demande sans cache à ~2 ms à chaud avec cache ; le
  premier calcul reste proche de ~30 ms.
- Comparaison bit-à-bit R55/R56 PASS sur noise, macro, fusions et masques pour
  les profils natif, Continental R53 et manuel six fusions en 384²/768².
- Cache par source et masque borné à 48 entrées ; tests d’invalidation,
  isolation des tableaux et changement de référence de taille ajoutés.
- La macro native reste le coût majoritaire ; aucune modification de son
  pipeline Legacy/Upgraded. Suite pytest indisponible ici (dépendance absente).

## v2.0 DEV_8_R55 — candidate locale

- Correction ciblée PASS : les miniatures de fusion 128² utilisent le côté
  natif demandé par la preview comme référence pour l’enveloppe absolue R53.
- Correction ciblée PASS : les previews de masques et le chemin d’application
  partagent l’enveloppe `native_calibrated`, donc un masque ne peut plus
  réintroduire de relief dans le cadre océanique.
- Contrat local PASS pour les 16 providers : déterminisme, plage signée
  `[-1, 1]`, sortie finie et intégration en fusion.
- Les nouveaux providers sont `heterogeneous_fbm` et
  `ridged_multifractal`. Le preset R53 et ses forces restent inchangés.
- Compilation et smoke-tests ciblés PASS ; la suite pytest n’est pas
  disponible dans cet interpréteur (`pytest` absent).

## v2.0 DEV_8_R54 — candidate locale

- Ajoute la première tranche de providers génériques prévue par la roadmap :
  `hybrid_fbm`, `turbulence`, `worley_f1`, `worley_f2` et
  `worley_f2_minus_f1`.
- Le preset Continental Custom R53 et sa composition `fbm` + `domain_warp` +
  `ridged` restent inchangés ; la candidate ouvre seulement de nouvelles
  briques dans l’onglet Archétype pour l’exploration suivante.
- Contrat local PASS pour les 14 providers : déterminisme, plage signée
  `[-1, 1]`, normalisation des profils et génération aux tailles `384/512/768`.
  Les cinq nouveaux providers fonctionnent aussi en fusion ; la qualification
  macro isolée reste diagnostique (`3/5` PASS sur la seed de référence, les
  écarts étant la fragmentation attendue de `F2−F1` et le faible relief de
  `turbulence`).
- Smoke-test ciblé du preset R53 PASS sur `384²`, seed `20260920`, miroir `0`.
- Compilation PASS ; la suite pytest n’est pas disponible dans cet interpréteur
  (`pytest` absent).

## v2.0 DEV_8_R53 — candidate locale

- Conserve la composition `fbm` + `domain_warp blend 15 %` + `ridged add
  12 %` de R52.
- Corrige la marge océanique du profil Custom avec une enveloppe absolue
  native-calibrée : cadre 18 cellules, transition 31 cellules.
- Les mesures de relief sur les trois tailles représentatives donnent environ
  `65 %` de terre à 384², `72 %` à 512² et `79 %` à 768², avec une transition
  de bord stable autour de 29–30 cellules.
- Compilation PASS ; la suite pytest n’est pas disponible dans cet interpréteur
  (`pytest` absent). Les qualifications macro et le gate de départs restent à
  rejouer après la mise à jour documentaire et l’archive.

## v2.0 DEV_8_R52 — candidate locale

- Ajoute le preset `Continental Custom R52 — fBm + domain warp + crêtes` :
  source autonome `fbm`, fusion `domain_warp` en `blend 15 %`, puis fusion
  `ridged` en `add 12 %`. Le sélecteur de l’onglet Archétype remplit les
  mêmes champs visibles et éditables ; aucun masque dessiné ou gabarit n’est
  utilisé.
- Compilation PASS. Smoke-test PASS : `34` validations Upgraded, `18`
  validations Legacy et checksum binaire.
- Profil déterministe et qualification macro PASS : `18/18` gates sans
  nouvelle violation sur `384/512/768`, trois seeds et miroirs `0/3`.
  Les résultats bruts sont `17/18` ; l’unique ligne sous le seuil de relief
  est l’avertissement déjà présent dans le Continental natif (`384²`, seed
  `20260920`, miroir `3`).
- Gate de départs Legacy ciblé PASS : `18/18` cas sur `384²`, `18/18` sur
  `512²`, et `6/6` sur `768²` pour le seed représentatif `20260920` ; chaque
  cas valide les validations dures, le nombre exact, l’unicité et les bornes.
  Le rapport réduit extrait passe également avec `2/2` cas.
- La suite pytest n’est pas disponible dans cet interpréteur (`pytest` absent).
- Archive source validée après extraction : `256` fichiers et environ `7,39 MB` ;
  son SHA-256 est communiqué à côté de l’archive pour éviter une
  auto-référence dans cette note.
- Limite restante : validation visuelle sous Windows, dans l’éditeur et en
  jeu, sur plusieurs tailles/seeds avant de retoucher éventuellement les
  forces des deux fusions.

## v2.0 DEV_8_R51 — candidate locale

- Ajoute une calibration Continental provisoire dérivée du contrat natif et
  tools/qualify_continental.py, avec comparaison à la baseline et gate dur
  des départs sur le chemin Custom basé sur Legacy.
- Le profil conserve la topologie, le bruit et la côte natifs ; seuls
  shape_scale_percent=96 et relief_contrast_percent=105 changent. Aucun
  preset actif ni génération Legacy n’est modifié.
- Compilation PASS. Smoke-test PASS : 34 validations Upgraded,
  18 validations Legacy et checksum binaire.
- Rapport R51 complet PASS : 18/18 macro-gates, 54/54 cas de départs,
  3/3 gates. Les qualifications macro brutes sont 16/18, avec deux
  avertissements mountain_snow_share déjà présents dans la baseline native ;
  aucune nouvelle violation n’est introduite. 9 warnings startable_mass
  restent souples.
- Non-régression R50 PASS : 36/36 cas et 4/4 gates.
- La validation de l’archive extraite et son SHA-256 sont consignés à côté de
  l’archive candidate pour éviter une auto-référence dans cette note. La
  validation visuelle Windows/éditeur/jeu reste ouverte.

## v2.0 DEV_8_R50 — candidate locale

- Ajoute `tools/qualify_manual_masks.py`, avec fixture numérique asymétrique et
  option `--mask` utilisant le resampling grayscale 64×64 de l’éditeur.
- Matrice complète par défaut : 36 cas (`384/512/768` × trois seeds × quatre
  miroirs), 36/36 cas PASS et 4/4 gates PASS. La couverture reste stable avec
  une amplitude maximale de `0,212012` point de pourcentage ; la variation
  hors masque et l’effet sur la preview complète sont mesurés.
- Contrôles locaux : compilation PASS, smoke-test (`34` validations Upgraded,
  `18` Legacy et checksum binaire) PASS, qualification importée réduite PASS.
  La suite pytest complète n’est pas disponible dans cet interpréteur
  (`pytest` absent).
- Archive source : 254 fichiers, `7 380 713` octets ; l’archive extraite
  repasse compilation, smoke-test et assertions de présence R50.
- Le SHA-256 de la copie livrée est communiqué à côté de l’archive afin
  d’éviter une auto-référence dans cette note.
- Limite connue : la validation Windows d’un masque réellement dessiné ou
  importé reste à faire ; aucun checkpoint DEV complet ni push n’est effectué.

## v2.0 DEV_8_R49 — candidate locale

- Corrige la palette de la fenêtre d’édition des masques : son fond, le fond
  du canevas et sa bordure utilisent maintenant le thème actif, en particulier
  le thème sombre. Aucun pipeline de génération ni format de masque n’est
  modifié.
- Ajoute au TODO le chantier post-DEV8 consacré aux rivières hors Legacy, dont
  le comportement actuel est distinct de la génération native et indésirable.
- Validation complète et archive candidate à consigner après compilation,
  self-test, smoke-test et vérification de l’archive extraite.

## v2.0 DEV_8_R48 — candidate locale

- Ajoute le provider `Dessin libre` à la pile indépendante : grille 64×64,
  peinture/effacement, import d’image en niveaux de gris, export PNG et
  preview du signal réellement appliqué. Les paramètres spatiaux communs et
  la variation hors masque restent inchangés ; le schéma passe à 16.
- Validation locale : compilation, self-test source, smoke-test (`34`
  validations Upgraded + `18` Legacy et checksum binaire), contrôles directs
  de grille, resampling, effet hors masque et migration R47 PASS. La suite
  pytest complète n’est pas disponible dans l’interpréteur de cet
  environnement (`pytest` absent).
- Archive source finale : 253 fichiers. L’archive extraite repasse
  compilation, self-test et smoke-test ; le SHA-256 de la copie livrée est
  communiqué avec le fichier afin d’éviter une auto-référence dans cette note.

## v2.0 DEV_8_R47 — candidate locale

- Rend le contrat des masques générique : la carte expose uniquement les
  réglages spatiaux communs et conserve les paramètres de provider séparément.
  Les profils R46 sont normalisés vers le schéma 15 sans perdre leurs formes.
- Le profil neuf utilise `0` fusion active ; les profils qui enregistrent un
  compteur explicite gardent leur composition.
- Validation locale : compilation, self-test source, smoke-test (`34`
  validations Upgraded + `18` Legacy et checksum binaire), contrôles directs
  des quatre providers et migrations R44/R46 PASS. La suite pytest complète
  n’est pas disponible dans l’interpréteur de cet environnement (`pytest`
  absent).
- Archive source finale : 253 fichiers. L’archive extraite repasse
  compilation, self-test et smoke-test ; le SHA-256 de la copie livrée est
  communiqué avec le fichier afin d’éviter une auto-référence dans cette note.

## v2.0 DEV_8_R46 — candidate locale

- Refonte de R44 en pile autonome de masques paramétriques, appliquée après la
  source et les fusions sans découpe dure de l’extérieur ; migration R44 et
  previews par masque couvertes par des contrôles directs.
- Validation locale : compilation, self-test source, smoke-test (`34`
  validations Upgraded + `18` Legacy et checksum binaire), contrôles directs
  des quatre formes et migration R44 PASS. La suite pytest complète n’est pas
  disponible dans l’interpréteur de cet environnement (`pytest` absent).
- Archive source finale : 253 fichiers, `7 366 719` octets ; SHA-256
  `ddcd5e87d0a12b83fa2e32394267b1dca44db941c502808ede7d182397f9b3c9`.
  L’archive extraite repasse compilation, self-test et smoke-test.

## v2.0 DEV_8_R45 — candidate locale

- Base exacte : candidate R44 ; correction ciblée du crash de démarrage dans
  l’onglet Archétype. `display_setting` est maintenant défini avant la
  construction des variables du gabarit de forme ; aucun comportement de
  génération ni paramètre de R44 ne change.
- Une régression source vérifie explicitement l’ordre définition/utilisation.
- Validation locale : compilation, self-test source, smoke-test (`34`
  validations Upgraded + `18` Legacy et checksum binaire) et régression ciblée
  de l’ordre de définition PASS. La suite pytest complète n’est pas disponible
  dans l’interpréteur de cet environnement (`pytest` absent).
- Archive source finale : 253 fichiers, `7 361 017` octets ; SHA-256
  `2ebbd2a1b7e74063bbd5f0a5ee9dc2c2322abd7947b181152630224131d68d7d`.

## v2.0 DEV_8_R44 — candidate locale historique

- Base exacte : candidate R43 prototype ; refonte du concept de masque en
  gabarit spatial global de l’archétype. Les sources de relief et les fusions
  restent indépendantes puis remplissent ce gabarit ; elles ne s’imbriquent
  plus comme des « fusions de fusion ».
- Quatre gabarits paramétriques sont disponibles : étoile, cœur, serpent et
  volcan, avec dimensions, position, rotation, douceur et paramètres propres
  à chaque forme. L’aperçu dédié suit le miroir natif et est rafraîchi sans
  effacer l’image précédente. Les champs R43 restent lisibles uniquement pour
  compatibilité/migration.
- Validation locale : compilation, self-test source, smoke-test (`34`
  validations Upgraded + `18` Legacy et checksum binaire) et contrôles directs
  des quatre gabarits/fusions PASS. La suite pytest complète n’est pas
  disponible dans l’interpréteur de cet environnement (`pytest` absent).
- Archive source finale : 253 fichiers, `7 360 441` octets ; SHA-256
  `6584a378df5a0e65f64b9571a7e93c60d0ebbfc514d55f1a908830cda35d8d21`.

## v2.0 DEV_8_R43 — candidate locale historique

- Base exacte : candidate R42 ; masques indépendants pour la source principale
  et les fusions, avec types hauteur, bordure, bandes, direction, pente,
  courbure et noise secondaire, neutres par défaut.
- Validation locale : `575 passed`, compilation et self-test source PASS ;
  smoke-test `34` validations Upgraded + `18` Legacy et checksum binaire PASS.
  L’archive extraite repasse compilation, self-test et smoke-test.
- Archive source finale : 253 fichiers, `7 353 487` octets ; SHA-256
  `37d6b5da7ffa7d3338c356bded8a0354990f7f0f361c183dc2c1f6f9dfa28903`.

## v2.0 DEV_8_R42 — candidate locale

- Base exacte : candidate R41 ; contrôles de l’en-tête ancrés en haut, reflow
  historique de Session / Comparaison conservé, groupes repliables resserrés
  et mini-previews revenues à 128² fixe.
- Validation locale : `565 passed`, compilation et self-test source PASS ;
  smoke-test `34` validations Upgraded + `18` Legacy et checksum binaire PASS.
  L’archive extraite repasse compilation, self-test et smoke-test.
- Archive source finale : 253 fichiers, `7 348 000` octets ; SHA-256
  `848ba8429fc7619a9f8406d466a0f3ceaba68640d8d5cbec50f0861e585f3a73`.

## v2.0 DEV_8_R41 — candidate locale

- Base exacte : candidate R40 ; groupe « Fondamentaux » repliable et ouvert par
  défaut, mini-previews adaptatives repeintes depuis les tableaux en cache, et
  second séparateur vertical mémorisant le ratio de l’en-tête.
- Validation locale : `564 passed`, compilation et self-test source PASS ;
  smoke-test `34` validations Upgraded + `18` Legacy et checksum binaire PASS.
  L’archive extraite repasse compilation, self-test et smoke-test.
- Archive source : 253 fichiers, `7 347 700` octets ; SHA-256
  `4e0c10a76be5fadfcb1ee12ef5404777023f8e0616e7dd8e6be1c38273affd64`.

## v2.0 DEV_8_R40 — archive précédente

- Base exacte : candidate R39 ; regroupement ergonomique des réglages de chaque
  source en quatre familles, dont trois groupes avancés repliables par source.
  Aucun paramètre ni comportement de génération n’est retiré.
- Validation locale : `563 passed`, compilation et self-test source PASS ;
  smoke-test `34` validations Upgraded + `18` Legacy et checksum binaire PASS.
  L’archive extraite repasse compilation, self-test et smoke-test.
- Archive source : 253 fichiers, `7 344 761` octets ; SHA-256
  `4887161d7a13191deda22a8974abc7d8b66393c003b0daeb4637cfa0bdd54d56`.

## v2.0 DEV_8_R39 — archive précédente

- Base exacte : candidate R38 ; ajout de deux resets locaux ciblés dans
  l’onglet Archétype et séparation des grilles internes des cartes de fusion.
  Aucun paramètre n’est retiré, le reset global reste présent et les previews
  sont synchronisées en place.
- Validation locale : `563 passed`, compilation et self-test source PASS ;
  smoke-test `34` validations Upgraded + `18` Legacy et checksum binaire PASS.
  L’archive extraite repasse compilation, self-test et smoke-test.
- Archive source : 253 fichiers, `7 342 771` octets ; SHA-256
  `324feaeb768312caea24ac82eacddc185424b9e0f39f802dfbf71a178e4e4489`.

## v2.0 DEV_8_R38 — archive précédente

- Base exacte : candidate R37 ; ajout du remappage avancé par source : points
  noir/blanc, seuils durs ou adoucis, plancher/plafond et courbe asymétrique.
  Les valeurs identitaires migrent les profils antérieurs sans modifier leur
  bruit.
- Les réglages sont disponibles séparément pour la source principale et les
  fusions ; ils restent dans le pipeline autonome borné par le cadre fini.
- Validation locale : `563 passed`, compilation et self-test source PASS ;
  smoke-test `34` validations Upgraded + `18` Legacy et checksum binaire PASS.
  L’archive extraite repasse compilation, self-test et smoke-test.
- Archive source : 253 fichiers, `7 340 561` octets ; SHA-256
  `7fe2a31fadce4cd82d98c80f8c449fcf3e239d1f53ebcf18aad291747237b46f`.

## v2.0 DEV_8_R37 — archive précédente

- Base exacte : candidate R36 ; ajout de transformations de coordonnées
  indépendantes par source : décalage X/Y, échelle X/Y, répétition X/Y et
  symétrie X/Y. Les valeurs identitaires migrent les profils existants sans
  modifier leur bruit.
- Les transformations restent dans le pipeline autonome des providers et le
  cadre rectangulaire fini continue de limiter la génération aux bords utiles.
- Validation locale : `554 passed`, compilation et self-test source PASS ;
  smoke-test `34` validations Upgraded + `18` Legacy et checksum binaire PASS.
  L’archive extraite repasse compilation, self-test et smoke-test.
- Archive source : 253 fichiers, `7 337 357` octets ; SHA-256
  `f869a26d799df564a30fffda17cbddd77028bbf65e63412bb84312cdb385f11a`.

- Base exacte : candidate R35 ; ajout des transformations de sortie communes
  (inversion, absolu, gamma et terrasses) et déplacement du tooltip de
  l’éditeur de noisemaps dans son titre.
- Validation locale : `541 passed`, compilation et self-test source PASS ;
  smoke-test `34` validations Upgraded + `18` Legacy et checksum binaire PASS.
  L’archive extraite repasse self-test, smoke-test et compilation ; sa taille
  et son SHA-256 sont fournis avec l’artefact, sans auto-référence dans le ZIP.

## v2.0 DEV_8_R35 — candidate locale

- Base exacte : candidate R34 ; corrections limitées au cycle d’affichage des
  previews, à la miniature source et au placement de la section des seuils.
- La passe indicative n’est plus commitée dans l’interface. L’ancienne image
  reste visible jusqu’au résultat exact ; au premier rendu ou après reset, seul
  le rendu exact peut apparaître.
- Validation locale : `535 passed`, compilation et self-test source PASS ;
  smoke-test `34` validations Upgraded + `18` Legacy et checksum binaire PASS.
  Le contrôle de l’archive extraite et son empreinte SHA-256 sont consignés
  dans le relevé de livraison à côté de l’artefact.

## v2.0 DEV_8_R34 — candidate locale

- Base exacte : candidate R33 ; corrections limitées au cycle de preview, aux
  miniatures de source, au comportement Solo et au compactage de l’éditeur.
- Sans lissage, la phase indicative n’est plus exécutée ; avec lissage, le
  calcul rapide reste disponible avant le résultat exact.
- Solo ne peut plus activer implicitement une fusion désactivée ; la source
  principale Legacy est reconstruite depuis le champ brut pré-sculpture.
- Validation locale : `534 passed`, compilation et self-test source PASS ;
  smoke-test `34` validations Upgraded + `18` Legacy et checksum binaire PASS.
  L’archive extraite repasse self-test, smoke-test et les 107 tests ciblés.
- Archive source : 253 fichiers ; sa taille et son SHA-256 sont consignés dans
  le relevé de livraison à côté de l’artefact (sans auto-référence dans le ZIP).

- Base exacte : candidate R32 validée par l’utilisateur ; aucun changement des
  générateurs réels, des formats ou des données protégées.
- Chaque carte active de fusion propose déplacement haut/bas, duplication,
  suppression et aperçu Solo ; Solo n’est appliqué qu’à une copie de profil
  destinée à la preview.
- Le plafond de six slots, les réglages masqués et les miniatures brutes 96²
  sont conservés.
- Validation locale : `531 passed`, compilation et self-test source PASS. La
  source ZIP contient 253 fichiers ; validation de l’archive extraite PASS.
  L’empreinte SHA-256 est fournie avec l’archive livrée.

## v2.0 DEV_8_R32 — candidate locale validée

- Base exacte : candidate R31 ; aucun changement des générateurs réels, des
  formats ou des données protégées.
- Le triptyque principal est placé en tête sur trois colonnes compactes ; la
  pile de fusions accepte `0..6` slots persistants et les cartes de source
  affichent des miniatures brutes 96² mises à jour en place.
- La relaxation facultative reste limitée à l’aperçu macro. Le raffinement
  natif et les interpolations des providers sont conservés et explicités.
- Validation locale : `528 passed`, compilation et self-test source PASS. La
  validation utilisateur est reçue. Une finition visuelle post-validation
  place les seuils du relief en colonne 2 à côté de la source du relief ; la
  validation Windows/1080p de cette retouche reste incluse dans le prochain
  test pratique.

## v2.0 DEV_7 — checkpoint validé et publié

- Base exacte : candidate `DEV_7_R26`, issue du socle applicatif `DEV_6_R61`.
- La validation utilisateur est reçue ; la finition ergonomique du Générateur
  est clôturée. Le moteur, les données, les exports et les règles de génération
  restent inchangés.
- R26 retire l’aide redondante de Terrains, place Décorations avant Terrains,
  applique le reflow anticipé des sections et ajoute le troisième panneau du
  Bonus quand la largeur le permet.
- Validation finale : `437 passed`, compilation, self-test source,
  smoke-test (`33` validations Upgraded + `17` Legacy), hashes protégés,
  contrôle après extraction et archive fraîche PASS.
- Le checkpoint est publié sur `dev` sans le suffixe R ; `references/` reste
  réservé à l’archive de reprise et n’entre pas dans le dépôt GitHub.
- Prochaine tranche : archétypes Custom.

## v2.0 DEV_7_R19 — candidate locale historique

- Base exacte : candidate DEV7 R17 ; rollback de l’essai de staging R18 après
  validation visuelle, le gain étant insuffisant et potentiellement moins
  fluide.
- Le rendu de l’onglet Générateur revient à R17 ; la solution robuste à
  widgets persistants reste au TODO sans version cible, avec la v2.1 comme
  horizon possible.
- 10 tests ciblés Custom/controller, compilation, self-test source,
  smoke-test (`33` validations Upgraded + `17` Legacy), checksum binaire,
  intégrité/extraction ZIP et ré-emballage PASS ; l’archive contient 338
  fichiers. La suite complète R17 reste à `433 passed` ; le rerun complet R19
  attend un interpréteur disposant de `pytest`. Aucun push ni release.

## v2.0 DEV_7_R18 — candidate locale historique abandonnée

- Essai de staging temporaire lors des changements explicites de mode ou
  d’archétype ; gain jugé insuffisant après validation visuelle.
- La candidate R19 revient au code R17 éprouvé. La solution robuste reste
  suivie dans le TODO sans version cible.

## v2.0 DEV_7_R17 — candidate locale historique

- Base exacte : candidate DEV7 R16 ; correction limitée à la transition
  automatique preset → Custom lors de la première édition d’un contrôle.
- Le mode, la provenance, le statut et les indicateurs sont synchronisés sans
  reconstruire l’onglet Générateur ; le focus et les widgets sont conservés.
- Un chantier UI sans version cible est ajouté au TODO pour les clignotements
  lors des changements d’options et les artefacts de redimensionnement.
- 10 tests ciblés Custom/controller, compilation, self-test source,
  smoke-test, checksum binaire, extraction et ré-emballage ZIP PASS. Le paquet
  contient 338 fichiers. La suite complète R16 reste à `433 passed` ; le
  rerun complet R17 attend un interpréteur disposant de `pytest`.

## v2.0 DEV_7_R16 — candidate locale

- Base exacte : candidate DEV7 R15 ; finition limitée à la section Poissons.
- Le tooltip de « Près des côtes » explique la limitation du placement des
  ressources en poissons. Les contrôles sont ordonnés Quantité moyenne → Près
  des côtes → Épaisseur de la bande, sans texte d’état redondant visible.
- 10 tests ciblés Custom/controller, compilation, self-test, smoke-test et
  extraction ZIP passent. La suite complète R15 reste à `433 passed` ; le
  rerun complet R16 attend un interpréteur disposant de `pytest`. Aucun push ni
  release.

## v2.0 DEV_7_R15 — candidate locale historique

- Base exacte : candidate DEV7 R14 ; finition limitée aux aperçus estimés.
- L’avertissement de placement est dans le tooltip du titre « Aperçu estimé ».
  Forêts et Groupes de pierres signalent de façon identique leur état
  désactivé ; les pierres utilisent les libellés « Gisements totaux » et
  « Gisements exploitables ».
- Le point 2 de la mini-roadmap de finition de l’onglet Générateur est clos.
  Le Bonus de départ reste reporté. Les 9 tests ciblés Custom/controller,
  compilation, self-test source, smoke-test et extraction ZIP passent. La
  suite complète R14 reste à `433 passed` ; le rerun complet R15 attend un
  interpréteur disposant de `pytest`. Aucun push ni release.

## v2.0 DEV_7_R14 — candidate locale historique

- Base exacte : candidate DEV7 R13 ; correction ciblée de la lecture des
  valeurs de référence des aperçus Custom, sans modification des moteurs
  Legacy/Upgraded ni des sections validées.
- Les aperçus Arbres et Pierres affichent désormais les valeurs profilées au
  lieu de zéros et restent réactifs à la taille de carte.
- Test de régression ajouté ; les 8 tests ciblés Custom/controller, le
  self-test source, le smoke-test et l’intégrité de l’archive fraîche passent.
  La suite complète R13 reste à `433 passed` ; le rerun complet R14 attend un
  interpréteur disposant de `pytest`. Aucun push ni release.

## v2.0 DEV_7_R13 — candidate locale historique

## v2.0 DEV_7_R12 — candidate locale historique

## v2.0 DEV_7_R11 — candidate locale historique

## v2.0 DEV_7_R10 — candidate locale

- Base exacte : candidate DEV7 R9 ; aucune logique de génération, donnée,
  bonus ou export n’est modifiée.
- Repères `?` rapprochés de leur texte ; Poissons, Arbres et Pierres passent
  sur une colonne par défaut ; la matrice dense des Minerais/Décorations est
  conservée. Le stock moyen des pierres et les champs de Groupes sont alignés.
- Rivières, Terrains et Minerais validés visuellement restent inchangés ; la
  refonte du Bonus de départ est reportée.
- Suite complète : `430 passed`, compilation réussie.
- Self-test source, smoke-test, checksum binaire et hashes protégés PASS ; la
  validation visuelle Windows reste ouverte.

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
