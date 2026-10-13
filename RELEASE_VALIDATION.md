# DEV10 — checkpoint validé, issu de R66

Le 13 octobre 2026, Julien valide Formule pour la 2.0, confirme avoir déjà testé
le parcours export EDM→éditeur→réexport MAP→jeu, et autorise explicitement le
push de R66 en tant que DEV10 complète. Aucun blocage fonctionnel restant.
Les fichiers/seeds exacts du parcours manuel ne sont pas précisés.

## Périmètre livré

- Finitions UI, masques et sprites utilisateur ; tooltips corrigés.
- Relief adaptatif insulaire, Îles individuelles et Îles par équipe au prorata
  des effectifs ; lacs intérieurs, montagnes réparties et espacement des alliés.
- Nouveau Continental issu de la grande île, calibration terre/océan et
  départage des directions de rivières Amélioré. Classique reste natif.
- Audit des placements et filtres jeu/éditeur (vert/jaune), terrain seul ou
  terrain+objets ; import/export cohérents, équipes indépendantes par défaut.
- Préparation native des exports EDM/MAP, maximum 768 ; import SAV contextuel
  et conversion SAV→nouvelle carte sans restaurer le setup de partie.
- Source Custom Formule V1 : expressions bornées, exemples, erreurs locales,
  source principale/fusions et sauvegarde du profil.

## Validation

Les étapes géographiques, filtres, tooltips/SAV et Formule ont été acceptées
par Julien ; jeu fonctionnel confirmé et parcours éditeur confirmé testé.
Qualification R66 : 1304 PASS distincts consolidés, 2 skips, aucun échec restant
sur les contrôles exécutés ; suite générale et finitions ciblées séparées.
Huit générations des exemples livrés et roundtrip EDM/MAP contrôlés.
Contrôle final : 16 tests de métadonnées/packaging/maintenance PASS ; auto-test
source PASS, 52 sprites présents et hashes protégés exacts.
Les preuves détaillées restent dans les références du ZIP source.

Seules la version du checkpoint, ses métadonnées Windows, le test correspondant
et la documentation changent depuis R66. Aucun algorithme, asset ou preset modifié.

## Reports

Éditeur Formule dédié avec visualiseur et explications : hors 2.0, sans échéance.
Stats 2 : après 2.1. Recherches binaires/runtime et seeds rares : surveillance ou
lots futurs. Tailles >768 et Petites îles abandonnées. Archipel hors 2.0.
Build portable, installation propre, updater et préparation de Release relèvent
de la qualification RC/STABLE ; ils ne sont pas annoncés validés par ce push.

Publication autorisée uniquement sur `dev`, sans suffixe R. Aucun tag ni Release.

---

## Validation utilisateur R66 — 13 octobre 2026

Julien valide l'implémentation Formule pour la 2.0 après essai : elle lui semble
fonctionner correctement. Aucun défaut signalé. Ce retour accepte cette V1 ;
il n'atteste pas individuellement chaque scénario du protocole automatique.

Une interface dédiée, inspirée de l'éditeur de masques, avec visualiseur et
meilleures explications, est reportée hors 2.0, bien plus tard, sans échéance.
Pas de nouvelle fonctionnalité Formule à ajouter à DEV10.

Suite : bilan de clôture DEV10 et consolidation des livrables. Le parcours
éditeur→réexport→jeu reste à documenter séparément ; les validations de R65 et
R66 ne sont pas une attestation de ce parcours exact. Aucun push, tag ni Release.

# 2.0 DEV_10_R66 — source Formule

V1 approuvée : équations bornées utilisant bruits existants et coordonnées, saisie/exemples/erreurs dans source principale et fusions, sauvegarde Custom schema23. Test hydrologique hérité recadré sur Amélioré, algorithmes natifs inchangés. Qualification DEV10_R66_QUALIFICATION ; V1 validée pour la 2.0 par Julien après essai le 13 octobre 2026.


## Bilan de livraison

Suite générale hors UI Custom :1239 PASS,2 skips,4 subtests PASS,4 échecs en823,19s.
Les4 échecs étaient des assertions figées sur la liste des sources et le schéma22 ;
actualisées pour Formule/schema23 puis retestées :4 PASS. Aucun autre échec,
y compris le test hydrologique maintenant explicitement Amélioré.

UI Custom isolée couverte dans les165 ciblés :57 PASS. Deux nouveaux cas de
contrôles conditionnels/catalogue complet ont été ajoutés après collecte générale
et passent dans les ciblés. Bilan consolidé distinct :1304 PASS,2 skips,
aucun échec restant dans les contrôles exécutés. Ne pas présenter les165/81/46
comme des tests supplémentaires sans déduire leurs recouvrements. La suite
générale et les finitions ciblées ont leurs logs séparés.

Auto-test source et archive extraite contrôlés avant livraison. Implémentation Formule
acceptée pour la 2.0 après essai utilisateur le 13 octobre 2026. Les exemples sont
une base de travail, pas une garantie de viabilité pour toute expression/seed.

## Hydrologie — décision et contrôle du 13 octobre 2026

Julien demande de conserver Classique strictement natif, sans correction de son
comportement. Seul Amélioré doit éviter le souci observé. Point clôturé sans
modifier les algorithmes ni les tests de l’application.

Profil `continental_landmass_profile()` via alias `continental_legacy_blocks_profile`,
256, seed20260921 : les deux moteurs natifs produisent19 composantes dont1 sans
contact eau ; Amélioré produit16 composantes, toutes reliées à l’eau, sans case
rivière en mer ouverte (au moins5 voisins eauHEX6). Trois autres seeds
20260920/42/2026101010 passent également dans les deux moteurs Amélioré :
8 générations Amélioré conformes au total. Les28 tests dédiés rivières Amélioré
et départage des ex æquo passent, ainsi que2 subtests. Hashes protégés exacts.

Preuves : `hydrology_comparison.json` et `hydrology_tests.txt` dans
`references/dev_notes/DEV10_R65_QUALIFICATION/`. Ces contrôles ciblés suffisent
à clôturer le cas signalé ; pas une preuve universelle pour tous seeds.
L’échec général historique applique une contrainte de connectivité au défaut
Classique ; son périmètre doit être recadré à la prochaine maintenance des tests,
sans altérer l’algorithme natif pour satisfaire cette assertion. Les logs des
anciennes suites restent inchangés, pas de suite générale annoncée verte ici.

## Validation utilisateur — 13 octobre 2026

Julien valide le point R65 et indique : « je suis actuellement sur une partie
générée par notre programme et tout fonctionne correctement ». Lot accepté.
Le retour confirme la partie en cours ; il ne précise pas lesquels des quatre
exports SAV de test ont été ouverts ni le parcours éditeur→réexport exact.
DEV10 reste ouverte. Aucun code fonctionnel changé après validation.
Prochain travail : vérifier le cas hydrologique hérité Classique/Continental
et son équivalent Amélioré, avant de décider si une correction est nécessaire.

# 2.0 DEV_10_R65 — SAV vers nouvelle carte (13 octobre 2026)

Conversion contextuelle, civilisations/alliances conservées et refus avant écriture des IDs incertains. R64 validée par Julien ; validation Windows R65 attendue. Preuves : references/dev_notes/DEV10_R65_QUALIFICATION/.

## Qualification R65

## Suite finale et empaquetage

Suite générale hors UI Custom :1207 PASS,2 skips,4 subtests PASS,2 échecs en810,50s.
L’échec documentaire (version complète absente des notes de validation) est
corrigé puis le module maintenance repasse :10 PASS. Aucun code fonctionnel
changé après la suite. Avec les57 tests UI isolés :1265 PASS distincts au bilan
consolidé,2 skips et1 échec hérité Classique/Continental256 seed20260921.
Les85 tests ciblés sont des recouvrements, pas ajoutés au total distinct.

L’échec restant est `test_custom_profile_rivers_do_not_start_in_open_water_and_reach_water` ;
algorithme implicite Classique, déjà présent R62/R63/R64. Aucun correctif spéculatif
dans R65 ; investigation hydrologique distincte. Les tests Amélioré de la suite
passent mais ne constituent pas une vérification dédiée du même seed/configuration.

Archive source contrôlée par le packager et auto-test après extraction avant livraison.
Validation Windows/éditeur/jeu R65 attendue.
## Validation utilisateur — 13 octobre 2026

Julien valide R64 : tooltips aux bons endroits et absence de faux récifs sur
terre dans les SAV chargés. Ces deux contrôles visuels sont confirmés sous
Windows. Aucun nouveau résultat éditeur/jeu, export ou hydrologique n'est déduit
de ce retour. DEV10 reste ouverte ; aucun code changé après cette validation.

## Qualification R64

- Tests ciblés initiaux : 22 PASS (SAV, tooltips, focus, territoire initial).
- Suite générale hors UI Custom : 1194 PASS, 2 skips, 1 échec hérité, 4 subtests PASS,
  794,97 s. UI Custom isolée : 57 PASS. Total consolidé : 1251 PASS, 2 skips, 1 échec.
- Échec : `test_custom_profile_rivers_do_not_start_in_open_water_and_reach_water`,
  Continental 256/seed 20260921 avec algorithme implicite Classique. Même échec
  documenté sur R62/R63 ; aucun moteur de rivières modifié dans R64.
  Ce résultat ne conclut rien sur le chemin Amélioré, à examiner au lot dédié.
- Dernier ajustement des IDs affichés dans les tooltips de graphiques SAV :
  rerun graphes/stats/focus/tooltips : 61 PASS. Pas de nouvelle suite monolithique
  après ce petit ajustement d'affichage ; logs et limites séparés explicitement.
- Deux SAV 768 réels : initial 4P et avancé 10P. 56 et 114 marqueurs de chantier ;
  162 animations d'abattage dans l'avancé. Aucun récif dans ces deux sources :
  contrôle positif des quatre IDs runtime récif couvert par fixtures synthétiques,
  pas présenté comme observation de récifs sur ces deux fichiers.
- 5 vues rendues par SAV, données actuelles/originales inchangées ; source originale
  avancée SHA256 0397cc782839a92ae7ef37b3bbd3bec3c4d5b520249c4e75610f9b6e3589ced9.
- Trois cartes statiques : scaffold768EDM, référence Upgraded768EDM, Wokkel640MAP ;
  rendu global bit-identique à R63 exacte.
- Auto-test source PASS ; hashes natifs protégés exacts. Sources moteurs,
  presets et assets identiques à R63 ; seule la copie diagnostic SAV change
  dans le package génération. Aucun réglage géographique ni PRNG changé.
- Validation visuelle Windows des tooltips/menu/SAV reste attendue. Pas de
  nouveau lancement éditeur/jeu ni push, pas de conversion SAV→EDM/MAP.

# 2.0 DEV_10_R64 — tooltips et objets SAV

Les tooltips communs utilisent le pointeur en coordonnées écran, avec repli
au-dessus/à gauche près des bords. Le menu de départs ne s'appuie plus sur
son origine native Windows. Positionnement à confirmer sur le poste utilisateur.

Lecture SAV : objets actuels byte7 conservés ; objet original byte14 stocké
séparément en tableau session-only en lecture seule. Ni restauration des objets
consommés, ni écriture SAV, ni conversion d'export implicite.

Interprétation commune au rendu/compteurs/focus : récifs13–16 sur eau0–7 ;
112/113 terrestres = chantier ; 111/114 runtime inconnus. Croissance224–230,
216–222 et souches208–214 visibles ; animations d'abattage128–207 des variantes
0..4/6 reconnues, variante5 et trous7 restent non confirmés. Couleurs schématiques,
pas sprites du jeu. Le catalogue statique des EDM/MAP conserve son comportement.

Les graphiques décoratifs utilisent une projection dérivée séparée ; leurs
IDs canoniques ne sont jamais réécrits dans la carte et les listes d'objets
conservent les IDs réels. Le filtre terrain+objets ignore les marqueurs de
chantier sur copie, conformément à l'exclusion des bâtiments.

La génération, les presets et rivières ne sont pas modifiés. Export SAV→EDM/MAP
reste un lot séparé. Les distances restent pour Stats2. Maximum768, aucun push
ou EXE modifié. Contrôles automatisés dans le dossier R64 ;
ils ne remplacent pas une validation visuelle Windows ou un lancement de jeu.

> Mise à jour du 13 octobre 2026 : Julien valide R63. Position des tooltips
> incorrecte (loin du curseur, en haut à gauche), à corriger. Cette passe est
> documentaire ; résultats ci-dessous conservés, aucun nouveau test en jeu revendiqué.

Qualification générale R63 consolidée après reruns : **1241 passent, 2 skips,
1 échec de rivières hérité de R62**. Voir GENERAL_SUITE.md pour les invocations
exactes ; pas de revendication de suite monolithique entièrement verte.

## 2.0 DEV_10_R63 — qualification des placements

58 générations complètes et 8 refus attendus sur la matrice de cinq choix,
quatre géographies, Legacy/Upgraded. Contrôles de taille 256/384/768 jusqu'à
20 joueurs. 36 fichiers EDM/MAP passent les roundtrips et checksums ; état
initial préservé. 77 tests ciblés passent. Contrôleurs UI testés sans affichage.
Auto-test et compilation passent ; hashes protégés inchangés. Les sources de
génération R62/R63 ne changent que trois chaînes de messages de refus.

La suite générale est exécutée en deux tranches pour isoler les interpréteurs
Tcl des tests UI Custom. Son résultat final, les reruns et les échecs hérités
sont décrits dans `references/dev_notes/DEV10_R63_QUALIFICATION/GENERAL_SUITE.md`.
Elle n'est pas déclarée entièrement verte si ces échecs subsistent.
Le nouveau Continental R62 est validé par Julien ; les tooltips/menu natif
R63 restent à vérifier sous Windows. Aucun essai Windows/éditeur/jeu nouveau
n'est revendiqué pour cette candidate. Aucun EXE ni push modifié.

## Historique des qualifications

## 2.0 DEV_10_R55 — lacs intérieurs liés à la taille des îles

Qualification locale de la correction R54 signalée par Julien : les bassins
près du rivage sont supprimés au profit de bassins intérieurs. Un bassin est
calculé par environ 125 000 cases de terre par île, maximum trois ; le nombre de
joueurs ne déclenche pas les lacs. Centre à au moins 50 % de la profondeur
maximale depuis la mer ; chaque cellule reste à au moins 35 %, marge ajustée au
rayon.

Générations Legacy :
- 384/8, équipe unique, seed 2026101021 : aucun bassin, 8 starts, zéro échec dur.
- 512/8, équipe unique, seed 2026101022 : un bassin, 8 starts, zéro échec dur.
- 768/8, équipe unique, seed 2026101015 : deux bassins, 8 starts, zéro échec dur ;
  composantes intérieures mesurées à 104 et 118 cases de l’océan.
- 768/8, équipes 4+4, seed 2026101023 : un bassin par île, 8 starts, zéro échec dur ;
  composantes intérieures à 62 et 61 cases de l’océan.
- 768/2, équipe unique, seed 2026101024 : deux bassins, 2 starts, zéro échec dur.
- Upgraded 768/8, équipe unique, seed 2026101025 : deux bassins, 8 starts, zéro échec dur.
- Masque synthétique rond : un bassin connecté, entièrement terrestre, minimum
  63 cases du rivage (minimum contractuel calculé : 54,6).

`python -m compileall -q s3mapgen tests tools` et `python run_gui.py --self-test`
PASS ; hashes protégés conformes. Pytest n’est pas installé dans cet
environnement. Validation visuelle Windows, éditeur et jeu attendue. Aucun EXE,
push ou modification des formats.

## Historique 2.0 DEV_10_R54 — relief continu d’équipe, qualification locale

R54 retire les régions de relief associées aux joueurs. Une île partagée combine
un champ continu à l’échelle de l’île et, pour une équipe d’au moins quatre, un signal de crêtes
irrégulières déformé. La fréquence et la progression s’arrêtent à l’échelle huit
joueurs. Les lacs sont dérivés séparément des zones basses et plafonnent à trois.
Le masque extérieur, les starts et les règles d’Îles individuelles sont conservés.

- Legacy 768/8, seed 2026101015 : 12,93 % de montagne sur terre, deux lacs,
  huit starts, aucune validation dure en échec.
- Legacy 768/8, seed 2026101027 : 12,47 %, deux lacs, huit starts, aucun échec dur.
- Legacy 768/20, seed 2026101023, équipes 19 + 1 indépendant : 13,48 %, trois
  bassins générés, vingt starts, aucune validation dure en échec. Quatre
  composantes d’eau intérieures dépassent 500 cellules après classification.
- Legacy 384/4, équipe unique, seed 2026101021 : 10,70 %, un lac, quatre starts.
- Upgraded 384/4, équipes 2/1/1, seed 2026101022 : quatre starts, aucun échec dur.
- Îles individuelles, 384/4, seed 2026101015 : R53 et R54 ont le même hash
  SHA-256 sur hauteurs, terrains, objets, ressources, flags et starts :
  ca92fb4d8b57a25627b96aa46567ce2f824d0e440c3fe2b30fa297d87756ab51.
  Les starts restent (132,339), (274,128), (305,267), (88,103).
- python -m compileall -q s3mapgen tests tools : PASS.
- python run_gui.py --self-test : PASS ; hashes Legacy et bibliothèque native PASS.
- La suite pytest n’a pas pu tourner car pytest n’est pas installé.
- Vérification visuelle Windows, ouverture éditeur et essai en jeu attendus.
  Aucun EXE ni push ; maximum 768 et format d’export inchangés.

## Historique R53 — méthode de relief rejetée

La première candidate R53 utilisait un champ indépendant par région de joueur,
fondu au raccord. Les validations de starts passaient, mais Julien a jugé le
découpage visuel incorrect. R54 remplace entièrement cette approche.

## 2.0 DEV_10_R51 — claims ignorés dans les deux filtres de départs

Les deux contextes ne prennent en compte que le terrain et les objets définis par
le contexte : « avant objets » retire les objets Area ; « carte actuelle » les
conserve avec leurs flags d’occupation. Les claims et anciennes métadonnées de
départs sont neutralisés sur une copie d’analyse, jamais dans la source. Wokkel.map
produit 44 718 zones vertes et 3 266 jaunes en « avant objets », puis 8 914
vertes et 5 812 jaunes en « carte actuelle ». SAV : la copie conserve ses objets
runtime et ne passe pas par la préparation d’export EDM/MAP. Génération, exports
et maximum 768 inchangés.

Vérifications effectuées : Wokkel.map conserve 44 718/3 266 zones avant objets et
8 914/5 812 avec les objets Area ; ses 4 starts ne sont plus bloqués par les
claims. Les trois EDM R49 gardent des zones dans les deux contextes. Une Area
synthétique taguée SAV confirme que les claims sont ignorés et que ses objets
restent présents ; aucun fichier SAV réel n’était disponible comme fixture.
Compilation Python et `run_gui.py --self-test` PASS, avec hashes protégés PASS.
La suite pytest complète n’a pas tourné : pytest est absent de cet environnement.
Validation visuelle Windows encore attendue.

## Historique 2.0 DEV_10_R50 — carte vide pour le filtre des départs

R50 vidait les objets Area en « avant objets » et neutralisait les claims des
EDM/MAP sur une copie. Wokkel.map y donnait 44 718 zones vertes et 3 266 jaunes.
Le mode « carte actuelle » gardait encore ses claims, d’où le correctif R51.

## 2.0 DEV_10_R49 — départs sur les anciens EDM avec marchandises

Le bloc natif 9 contient des piles de marchandises, pas des bâtiments ou unités.
Sa présence seule ne désactive plus le diagnostic des départs importés.
Les gardes des blocs 7/8 (entités privées) et des territoires occupés restent actifs.
Les trois EDM Echappee fournis sont conservés comme fixtures de régression,
avec PlayerInfo et marchandises : 200, 200 et 120 piles.
Les contextes « avant objets » et « carte actuelle » sont vérifiés sur chacun.
Les règles de placement, de génération et d’export restent celles de R48.
Les SAV avec état de partie ne sont pas requalifiés par cette correction.
Validation visuelle sous Windows attendue sur ces trois fichiers.

## 2.0 DEV_10_R48 — départs éditeur et parité export/import

R47 n’est pas validée sur ce sujet : le test utilisateur expose une catégorie
oubliée, « éditeur accepté / position exacte jeu refusée ». Vert = admis par
l’éditeur ; jaune = position exacte admise par le jeu, refusée par l’éditeur.
Le survol et les badges signalent la recherche voisine possible si l’éditeur
accepte mais le contrôle exact du jeu refuse. Ce contrôle ne prouve pas un
refus de chargement ; l’initialisation native peut chercher une position voisine.
Aucune garantie de destination voisine ni de lancement complet n’est donnée.

Le filtre propose chaque civilisation avec « avant objets » (défaut) ou
« carte actuelle ». Même contexte explicite sur génération et import, aucune
dépendance au snapshot pour la vue utilisateur. Avant objets enlève les objets
et leur bit d’occupation, conserve les autres flags et rétablit le blocage terrain.
Les badges utilisent toujours les objets finaux, la nation et l’espacement.
Grille préparée avec la fonction exacte du writer, sur copie, cache invalidé
par contenu. Génération, Area originale, snapshots et exports restent inchangés.

Cas réel 2026101011 / Legacy / Continental / 4P / 768 : les deux EDM ont une
Area identique. J5 (265,404), Romain, est accepté par les deux EXE éditeurs.
Le helper jeu exact le refuse pour le relief ; recherche native mode 0 retient
(265,398) sur le banc neutre, arrêté avant la création de ville. Les couleurs
R47 omettaient 12 368 cases éditeur ; la préparation export change 20 411 hauteurs
et 308 flags par rapport à la génération, expliquant les écarts de réimportation.
Preuves : references/dev_notes/DEV10_R48_DEPARTS_ET_EXPORT.md.
Maximum 768 ; équipes « − » ; aucun push ni EXE. Essai Windows/jeu attendu.

## Historique 2.0 DEV_10_R47 — départs valides sur terrain définitif

Le filtre utilise désormais le terrain et le relief finaux. Les objets et leur
occupation restent ceux présents au placement : les ajouts ultérieurs ne ferment
pas les zones possibles. Le survol indique cette distinction. Les départs posés
restent contrôlés sur la carte finale complète, avec civilisation et espacement.
Correction des faux verts sur herbe sèche et désert apparus après la sélection.
Classique après contenu et imports analysent leur état actuel complet.
Vert/jaune = admissibilité locale jeu/éditeur dans le contexte indiqué ; aucune
certification du lancement complet d’une partie. Génération et exports inchangés.

Requalification directe dans les trois EXE originaux : 10 188 comparaisons exactes
(terrains/flags sur 256 valeurs, civilisations, claims, relief, bords, emprises,
espacement et points du seed signalé). Aucun code natif intercepté dans le helper
jeu/nivellement ni les prédicats éditeur. 11 fixtures d’emprises reconfirmées.
Seed 2026101010, 6 joueurs, 768, Îles individuelles / Îles — seul : aucun faux
vert sur herbe sèche ni zone désert pour toutes les civilisations, dans les deux
modes. Area et starts identiques à R46. Détails : docs/PLAYER_STARTS.md et
references/dev_notes/DEV10_R47_DEPARTS_TERRAIN_FINAL.md.
Maximum 768, équipes « − » et garde-fous internes conservés. « ? » différé.
Aucun push ni EXE ; essai visuel Windows et lancement en jeu attendus.

## 2.0 DEV_10_R46 — départs jeu/éditeur et aucune équipe

« − » signifie aucune équipe ; chaque joueur concerné reste exporté dans un
groupe natif distinct. Alliances positives inchangées. « ? » est différé au
futur lot Îles par équipe. Le filtre conservateur disparaît de l’interface,
ses garde-fous internes de génération sont conservés.
Vert : admissible localement pour le jeu et l’éditeur ; jaune : admissible
localement pour le jeu, refusé par l’éditeur. Les motifs sont disponibles au
survol. Le raster utilise le snapshot de sélection ; les badges des départs
posés utilisent la carte finale, la civilisation réelle et l’écartement éditeur.
Ces diagnostics locaux ne garantissent pas le lancement complet d’un MAP.
Aucun export bloqué ; génération et maximum 768 inchangés.
Qualification native : 500 cas United et 500 cas éditeur standard concordants,
11 fixtures d’emprises d’objets. Voir docs/PLAYER_STARTS.md et
references/dev_notes/DEV10_R46_DEPARTS_JEU_EDITEUR.md.
Validation visuelle Windows et essai en jeu restent à effectuer. Aucun push ni EXE.

## 2.0 DEV_10_R45 — export natif, équipes et Îles individuelles

Préparation export United complète sur copie : contexte côtes/marais (0x10),
correction des hauteurs, finalisation (0x20). Objets, claims et ressources conservés.
Part 3 corrigée : (équipe, contrôle), et non l’inverse. Zéro est une vraie équipe
native ; « aucune » dans MapGen devient un groupe distinct par joueur. Les
alliances positives sont compactées en groupes natifs contigus à partir de zéro.
Grandes îles devient Îles individuelles, sans changer sa génération ni les clés
persistées. Petites îles retirée des choix proposés et abandonnée. Futur archétype
Îles par équipe : surface au prorata des joueurs, chaque joueur sans alliance
formant son propre groupe. Aucun algorithme par équipe ajouté dans cette candidate.
Maximum 768 conservé. Comparaison starts jeu/éditeur après essai MAP <=768 ;
aucune catégorie jaune sans preuve. Validation Windows/jeu attendue.
Preuves : references/dev_notes/DEV10_R45_QUALIFICATION/ et
references/dev_notes/DEV10_R45_EXPORT_ET_EQUIPES.md. Aucun push ni EXE.

# Settlers III MapGen — journal de validation

## 2.0 DEV_10_R44 — limite commune 768

Maximum 768×768 pour génération, batch, CLI, imports GUI et export MAP/EDM.
Extension 832–1024 retirée sur décision de Julien le 2026-10-10 ; recherches
côté jeu mises de côté. Relief, quotas, ressources et bonus <=768 conservés.
Prochains lots : préparation export côtes/marais complète, aucune équipe,
puis comparaison des départs jeu/éditeur. Aucun push ni EXE ; DEV10 ouverte.
Qualification : references/dev_notes/DEV10_R44_QUALIFICATION/.
Les mentions >768 des sections historiques ne décrivent plus le contrat actif.


Suite complète : 1084 tests PASS, 2 Tk ignorés (703.05 s).
Autotest source PASS ; générations/exports 1024 sur deux modes × deux
algorithmes, plus deux essais Équilibré 1024/20p PASS. Crash jeu non résolu.

## Historique 2.0 DEV_10_R43 — Classique étendu et identité Grandes îles

Classique accepte désormais les tailles 832, 896, 960 et 1024, avec les mêmes
règles de sélection et garde de carte neuve. Les filtres natifs couvrent aussi
ces tailles. Legacy + Équilibré conserve l’archétype final : l’aperçu de sélection
ne remplace plus Grandes îles par Continental dans les métadonnées/export.
Retour R42 : crash 1024 c0000005 à s3_united.exe+0xFD0B6. Cause non établie,
MAP exact requis ; ne pas annoncer ce crash corrigé. La capture est disponible.
Équipes toujours reportées. Aucun push ni EXE ; DEV10 reste ouverte.


Suite complète : 1079 tests PASS, 2 Tk ignorés (708.21 s).
Parité native sur douze tailles et cas réel 640 ; huit exports 832–1024,
chiffrement natif du bloc complet 1024 et autotest source PASS.
Validation jeu/éditeur des fichiers exacts R42 attendue.

## 2.0 DEV_10_R42 — export MAP/EDM conforme à United

Correction native des hauteurs appliquée à une copie au moment de l’export,
version 11 pour Amazones/marchandises étendues, padding natif et miniature
RGB555 actualisée. Dimensions 832–1024 conservées. Voir docs/MAP_EXPORT.md.
Les équipes restent inchangées et seront le prochain lot. Les sprites R41
sont confirmés impeccables par Julien. TEST_01 est jouable selon son retour ;
les exports exacts R42 restent à tester dans le jeu et l’éditeur United.
Aucun push ni EXE ; DEV10 reste ouverte.


## 2.0 DEV_10_R41 — 2026-10-09

- Diagnostic R40 : 11 cases bonus J8 sur une autre masse terrestre.
- R41 : même seed 512/15/4156456048, 15 départs et tous les contrôles durs PASS.
  J8 : marais de 10 cases sur sa masse, centre (142,89), distance inchangée.
- Règle Chinois/Choisir, slots partiels, garde des distances, validation sélective.
- Quatre PNG 16×16 RGBA originaux, hashes et packaging enregistrés.
- Tests ciblés : 52 profils/sprites/politique/limites PASS ; 31 politique/maintenance PASS.
- Qualification : 58 cartes, 712 départs, zéro échec dur et aucun centre bonus
  sur une autre masse terrestre ; quatre exports MAP/EDM relus avec Area exacte.
- Auto-test source et hashes protégés PASS. Suite complète : 1062 PASS,
  2 Tk ignorés faute d’affichage, zéro échec ; 695,80 s.
- Rapport : references/dev_notes/DEV10_R41_QUALIFICATION/.
- Validation Windows/éditeur/jeu attendue ; aucun push ni EXE.

## 2.0 DEV_10_R40 — 2026-10-09

- Retour Julien : ajouts appréciés, plusieurs générations testées.
- Campagne étendue : 240 cartes, 2780/2780 départs, 239/240 contrats durs,
  7040 contrôles durs dont un échec ISLAND_SWAMPS, zéro exception.
  Cinq configurations, 20 seeds, deux modes ; 200 Équilibré et 40 par île.
- Seul cas : Classique/par île 512/15/4156456048, huitième île sans marais.
  R39 et témoin R40 manuel100 : zéro départ et plusieurs îles sans marais.
  Adaptation qualifiée pour les départs ; réserve marais ouverte.
- Rapport exhaustif : references/dev_notes/DEV10_R40_CAMPAIGN_20261009/RAPPORT.md.

- Source insulaire adaptative et réglages manuels ; contrôles effectifs FR/EN/DE/ES.
- Nouveaux graphique et statistiques HEX6 des îles, survol, JSON et CSV.
- Cadenas/drapeau originaux fournis, PNG inchangés et hashes enregistrés.
- Comptage global des pierres préservé lors des bonus tardifs Équilibrés.
- 241 contrôles profils/UI/amplitude/stats PASS ; 31 compositions PASS ;
  43 reliefs/contours PASS ; 21 départs/pierres PASS.
- Sept cartes réelles : départs attendus et validations dures PASS ;
  six aperçus identiques au champ réellement classifié ; quatre exports MAP/EDM
  relus avec Area identique. Trois graines 384/8 Amélioré + un témoin Classique,
  512/4, 768/20, continent 512/4. Témoin continent exact R39 et
  snapshot Grandes îles 512/4 exact R39.
- Auto-test source et hashes protégés PASS ; 16 contrôles maintenance/packaging PASS.
- Suite complète : 1041 PASS, 6 échecs d’assertions anciennes, 2 Tk ignorés,
  638,21 s. Référence de version corrigée ; cinq témoins R21 testés explicitement
  en mode manuel à 100 % : hashes historiques exacts. Contrôles concernés repris :
  16 maintenance/packaging et 17 source archivée/réinitialisations PASS.
  Aucun changement fonctionnel après la suite, pas de second passage complet.
- Aucun Tk réel / Windows / éditeur / jeu ; aucun push ni EXE.
- Qualification : references/dev_notes/DEV10_R40_QUALIFICATION.json.

## 2.0 DEV_10_R39 — 2026-10-09

- Diagnostic sur une copie immuable à l’étape réelle du placement.
- Refus terrain/bord, occupation/accessibilité et nivellement séparés ;
  compteurs globaux et par île pour les filtres conservateur et natifs.
- Label Filtre commun, disponibilité et résumés traduits dans quatre langues.
- Six cartes témoins Legacy/Amélioré exactes R38 (Area et positions).
- 12 contrôles diagnostiques ciblés PASS ; 40 viewer/diagnostics PASS,
  puis 34 viewer/packaging PASS après les derniers ajustements UI.
- Auto-test source et hashes protégés PASS.
- Suite complète : 1029 PASS, 1 oubli de version dans ce journal, 2 Tk ignorés,
  617,63 s. Journal corrigé : 16 contrôles maintenance/packaging PASS en 7,54 s.
  Aucun échec fonctionnel ; pas de nouveau passage complet après correction documentaire.
- Pas de validation Tk réelle/Windows/éditeur/jeu ; aucun push ni EXE.
- Qualification : references/dev_notes/DEV10_R39_QUALIFICATION.json.

## 2.0 DEV_10_R38 — 2026-10-08

- Équilibré avant objets ; richesse minière seule ; 768/20/42 complet dans les deux moteurs.
- Carte incomplète conservée ; vue de validité et EDM de test partiel/vide.
- Trois nouveaux tests fonctionnels, anciens tests de rejet adaptés à la conservation.
- Auto-test PASS ; essais miroirs 1/2/3 PASS ; quatre EDM relus avec checksum/Area exacts.
- Suite complète : 1017 PASS, 3 anciennes assertions à adapter, 2 ignorés.
  Les assertions de rejet/ordre historique sont mises à jour : 26 contrôles
  concernés PASS en 12,19 s. Aucun nouveau passage complet annoncé.
  Résultats détaillés : references/dev_notes/DEV10_R38_QUALIFICATION.json.
- Ouverture Windows/éditeur/jeu à effectuer ; aucun push ni EXE.


## 2.0 DEV_10_R37 — 2026-10-08

- Équilibré : recherche complète à la distance souhaitée avant de comparer
  les ressources ; relâchement progressif quand les recherches ne placent pas tous les joueurs.
- Essai du pool admissible complet avant relâchement ; amélioration des
  ressources d’une solution de secours sans rapprocher les départs.
- Seed 2026100817, Continental 512/4p : minimum 65→141 en Legacy,
  68→148 en Amélioré ; quatre départs valides conservés.
- Un test ajouté pour cette seed dans les deux moteurs.
- Validité, terrain, bonus, autres algorithmes et interface inchangés.
- Qualification : references/dev_notes/DEV10_R37_QUALIFICATION.json.
- Validation Windows/éditeur/jeu à effectuer ; aucun push.


## 2.0 DEV_10_R36 — 2026-10-08

Validation technique : 1016 tests PASS, 2 ignorés sans écran ; 2 tests ajoutés.
Dix comparatifs R35/R36 et quatre générations bonus/îles PASS ; quatre exports
relus. Compilation et auto-test source PASS.

- Équilibré : pénalité souple de proximité adaptée à la terre accessible et
  au nombre de joueurs ; score de ressources inchangé.
- Cible souhaitée non obligatoire : préserver tous les joueurs si la place
  impose des départs plus proches. Minimum de validité et secours inchangés.
- Rapport : distance souhaitée et séparation minimale obtenue.
- Deux tests ciblés ajoutés ; qualification dev_notes/DEV10_R36_QUALIFICATION.json.
- Classique, Îles, Éloignement, terrain et interface inchangés.
- Validation Windows/éditeur/jeu à effectuer ; aucun push.


## 2.0 DEV_10_R35 — sprites et Équilibré

- Sprites PNG originaux et icône 16×16, pixels conservés.
- Équilibré après contenu global et avant bonus, sans quota par île.
- Quatre cas fonctionnels ajoutés ; contrôles de validité inchangés.
- Suite complète exécutée : deux assertions de documentation/inventaire
  actualisées ensuite et revalidées. Détail exact dans
  references/dev_notes/DEV10_R35_QUALIFICATION.json.
- Quatre contrôles Tk existants PASS avec écran ; menu quatre langues,
  sprites 16×16 et export désactivé si départs incomplets vérifiés.
- Cinq générations supplémentaires, dix exports MAP/EDM relus, dont 768/20p.
- Classique et module Grandes îles identiques à R34 ; hashes protégés PASS.
- Windows, éditeur et jeu non exécutés ; aucune publication Git.


## 2.0 DEV_10_R34 — civilisations communes et couleurs des joueurs

- Choix des quatre civilisations et Choisir disponible dans tous les algorithmes.
- Entrées transmises au cache, batch et CLI, puis exportées dans MAP et EDM.
- Carrés de couleur de 10 px devant les noms, palette existante J1–J20.
- Slots inactifs barrés/désactivés et configuration des vingt slots conservés.
- Algorithmes et reliefs inchangés ; contrôles conservateurs communs hors Classique.
- Choix des couleurs reporté à 2.1 ou après ; icône R33 conservée telle quelle.

Validation R34 : 1010 tests PASS, 2 tests Tk ignorés sans écran (556.97 s).
Les 4 contrôles existants de fenêtres passent avec un écran Tk Linux ; dialogue
vérifié dans 32 combinaisons langue/thème/algorithme. Deux cas fonctionnels
ajoutés (Legacy/Upgraded : nations, validité et deux exports) ; tests existants
batch/setup étendus. Îles 384/2p/seed 42 : nations [2,255] relues dans MAP/EDM,
pour les deux moteurs, contrôles de validité PASS.
Auto-test source, compilation et intégrité des ressources PASS.
Qualification : references/dev_notes/DEV10_R34_QUALIFICATION.json.
Aucun lancement Windows/éditeur/jeu ni push.

## 2.0 DEV_10_R33 — fenêtre joueurs compacte et icône

- Deux listes de dix joueurs, colonnes Joueur / Civilisation / Équipe.
- Équipe numérique courte sur la même ligne, rappel commun « 0 : aucune ».
- Noms des slots inutilisés barrés ; sélecteurs désactivés uniquement pour ces slots.
- Hors Classique, civilisation libre affichée comme texte normal pour les joueurs actifs.
- Icône fournie intégrée au runtime et à la configuration du build Windows.
- Aucune modification des algorithmes, paramètres d’équipes ou formats.

Validation R33 : 1008 tests PASS, 2 tests Tk ignorés sans écran (545.17 s).
Les 4 contrôles ciblés de fenêtres passent avec un écran Tk Linux ; dialogue
vérifié dans 16 combinaisons langue/thème/mode. Aucun nouveau test ajouté.
Auto-test source, intégrité des données et PNG original PASS.
Qualification : references/dev_notes/DEV10_R33_QUALIFICATION.json.
Aucun lancement Windows/éditeur/jeu ni push.

## 2.0 DEV_10_R32 — équipes et libellés

- Choisir en français ; labels joueurs simples, sélecteurs inutilisés grisés.
- Îles — seul ; futur Îles — par équipe noté au TODO.
- Départs → Joueurs… : équipe 0 à 20 par joueur, pour tous les algorithmes.
- Équipes conservées au cache/batch/CLI et exportées dans MAP et EDM.
- Setup corrigé : type Choisir et équipes configurées, plus de valeurs cycliques.
- Aucun changement des positions, règles de validité ou relief insulaire.

Validation R32 : 1008 tests PASS, 2 tests Tk ignorés faute d’écran (560.47 s).
Compilation, hashes protégés et auto-test source PASS.
Qualification : references/dev_notes/DEV10_R32_QUALIFICATION.json.
Aucun lancement Windows/éditeur/jeu ni push.

## 2.0 DEV_10_R31 — Choose et slots inactifs

- Option Choose (255) vérifiée dans les deux éditeurs et conservée à l’export.
- Slots inutilisés grisés et identifiés ; configuration conservée pour leur réactivation.
- Validité pour les quatre civilisations sur Choose, filtre supplémentaire documenté.
- Nations fixes R30 et génération insulaire R28 conservées.
- Correction documentaire : les Asiatiques acceptent la boue, pas les marais.
- Trois cas fonctionnels ajoutés ; outils de recherche exclus du programme.

Validation R31 : 1006 tests PASS, 2 tests Tk ignorés faute d’écran (564.65 s).
Compilation, hashes protégés et auto-test source PASS.
Qualification : references/dev_notes/DEV10_R31_QUALIFICATION.json.
Aucun essai Windows/éditeur/jeu ni push.

## 2.0 DEV_10_R30 — départs Classique

- Retrait complet du repli de relief R29 ; Grandes îles restauré à R28.
- Classique actif dans le menu principal, batch et CLI ; nations explicites
  exportées, placement après contenu global et bonus MapGen de départ désactivés.
- Sélection native et effets successifs de ville : mêmes positions et PRNG
  que le .exe sur neuf scénarios de référence, dont l’échec à un million d’essais.
- Carte conservée si le Classique désactive un slot ; export incomplet explicite.
- 13 cas de régression fonctionnels, aucun outil de recherche ajouté au programme.
- Validation Windows/éditeur/jeu ouverte ; souci des starts insulaires reporté.

Validation : 1003 tests PASS, 2 tests Tk ignorés faute d’écran (562.49 s).
Compilation, hashes et self-test source PASS. Contrôles ciblés finaux : 15 PASS.
Qualification : references/dev_notes/DEV10_R30_QUALIFICATION.json.
Aucun lancement Windows, éditeur ou session en jeu.

## 2.0 DEV_10_R28 — recherche des départs insulaires

Validation : 990 tests PASS, 2 tests Tk ignorés faute d’écran (736,38 s).
Compilation et hashes protégés PASS ; aucun essai Windows/éditeur/jeu.
Qualification : references/dev_notes/DEV10_R28_QUALIFICATION.json.

- Suppression de l’échantillonnage ; toutes les positions admissibles conservées.
- Marge de carte et dégagement devenus préférences ; contrôles obligatoires inchangés.
- Recherche avec retour sur les choix précédents en cas de conflit de séparation.
- Erreurs précises : terrain/occupation, relief ou combinaison de séparation impossible.
- Quatre tests fonctionnels ajoutés ; aucun port de recherche inactif.
- Le cas Grandes îles 384/8p/seed 42 reste refusé par le relief ; aucune parité Classique revendiquée.
- Rejet global encore présent, aucune validation Windows/éditeur/jeu ni push.


## Candidate locale 2.0 DEV_10_R27 — messages

Parcours réels Tk : import d’un fichier invalide, paramètres invalides,
copie intégrale/persistance après fermeture, regroupement, détails, restauration
du modal précédent et thèmes/langues. Aucune validation Windows revendiquée.
Le correctif d’affichage R26 reste présent ; règles de génération inchangées.
988 tests PASS (564,84 s) ; qualification DEV10_R27_QUALIFICATION.json.

## Candidate locale 2.0 DEV_10_R26 — interface

Générateur vide reproduit : cadres de lignes couvrant les contrôles frères.
Correction de l’ordre d’affichage ; aucun changement du moteur.
Test réel Tk PASS : quatre langues, deux thèmes, trois tailles et menu Départs.
Contrôle négatif R25 : FAIL attendu, bouton recouvert par un cadre.
Suite complète : 928 PASS, 56 erreurs du double Tk et un échec de métadonnées.
Double adapté : 57 contrôles UI PASS ; métadonnées de référence actualisées : 10 maintenance PASS.
Qualification détaillée : references/dev_notes/DEV10_R26_QUALIFICATION.json.
Aucune validation Windows/éditeur/jeu revendiquée. Classique exact ouvert.

## Candidate locale 2.0 DEV_10_R25

Menu Départs raccordé ; filtre de nivellement natif limité aux cartes neuves.
144 contrôles natifs des 36 nouveaux starts PASS, avant création des villes.
984 tests PASS (550,74 s), compilation et auto-test source PASS.
Classique exact reste ouvert ; aucun essai Windows/éditeur/jeu revendiqué.
Détails et limites : docs/PLAYER_STARTS.md et DEV_CANDIDATE_NOTES.md.

## Candidate locale 2.0 DEV_10_R24 — départs visibles

Qualification : 983 cas couverts en plusieurs lots (298 + 1 + 684).
Exécution monolithique interrompue après absence de progression ; cas suivant
PASS isolément. 193 ciblés UI/cache/architecture/sécurité, 27 baselines de
comportement, cinq cartes et quatre exports réouverts contrôlés.
Cela ne constitue pas une validation Windows/éditeur/jeu.

Menu Départs principal/batch/CLI raccordé, stratégies et sécurité R20 conservées.
Quatre modules de recherche non raccordés, outils/fixtures et 171 tests retirés.
Trois nouveaux tests fonctionnels ; bilan détaillé dans docs/PLAYER_STARTS.md.
Classique exact et garantie de validité native restent ouverts. Essai provisoire
MAP→runtime retiré : pas assez qualifié pour devenir un filtre obligatoire.
Validation Windows, deux éditeurs et jeu attendue ; aucun push.


## Historique : 2.0 DEV_10_R22 — sélection des départs natifs

Poursuite autorisée par Julien après R21. Sélection 0x5074B0 portée, isolée :
62 scénarios exacts (appels, slots, PRNG), 1 000 distances et 1 536 tirages exacts ;
quatre épuisements réels d’un million de tentatives exacts.
19 999 offsets ordonnés exacts contre l’initialiseur du jeu. Validité/ville
remplacées par callbacks contrôlés dans ces essais ; pas de parité complète.
Placeur actif R20 conservé. Raccordement runtime/ville, Classique et îles à suivre.
Suite : 1 095 réussis ; un attendu de version R21 corrigé, puis 130 tests PASS.
Référence : references/history/DEPARTS_NATIFS_SELECTION_R22_20261006.md.
DEV10 ouverte, aucun push ; aucun nouvel essai visuel demandé pour ce lot.

## Historique : 2.0 DEV_10_R21 — noyau des départs natifs

Retour Julien : rien de visible signalé dans R20, essais difficiles ; poursuite
explicitement autorisée. Pas de validation complète Windows/jeu déduite.
Noyau isolé : nivellement normal 0x4DA440, filtre 0x4D99E0 et richesse 0x5081A0.
1 000 comparaisons directes EXE : valeur et buffers 31×31 exacts ; 359 essais
sur les seuils de richesse exacts. Objets/flags/claim runtime fournis explicitement,
sans conversion supposée depuis Area. Le placeur actif reste celui de R20.
Tests : 1 027 réussis (574,50 s), dont 45 du noyau ; 16 contrôles maintenance réussis.
Aucune nouvelle commande UI, aucun changement de carte ou bonus dans ce lot.
Classique complet à raccorder après port sélection/PRNG/contexte/initialisation ;
variante îles obligatoire avec un départ par île. DEV10 ouverte, aucun push.
Référence : references/history/DEPARTS_NATIFS_NOYAU_R21_20261006.md ; qualification :
references/dev_notes/DEV10_R21_QUALIFICATION.json.


## Candidate locale 2.0 DEV_10_R20 — départs

Filtre conservateur terrain/occupation, protection des départs et contrôle final.
Resets individuels préservent la source choisie. Audit original/Settlers United
inclus. Classique natif exact et nivellement restent à porter ; validation
Windows/éditeur/jeu en attente. DEV10 ouverte, aucun push.
Qualification : references/dev_notes/DEV10_R20_QUALIFICATION.json.

## Candidate locale 2.0 DEV_10_R19 — catalogue allégé

R18 appréciée par Julien : « excellentes modifications ». Ajustements du catalogue
et du gap Copier seed/Importer autorisés le 2026-10-06, repris dans R19.
Catalogue : ligne unique Nom · Taille (Variable pour les modèles), sans retour
à la ligne ; noms longs tronqués selon la police, nom complet en infobulle.
Charger une copie et poubelle 24 × 24 sur la même rangée pour les fichiers custom,
avec 4 px d’écart. Suppression toujours confirmée, infobulle traduite et thémée.
Les messages des fichiers invalides restent visibles sur une ligne séparée.
Sprites originaux et reflow mesuré R18 conservés ; aucune relecture au resize.
Copier seed/Importer : gap de 7 à 4 px, identique aux autres boutons voisins.
Qualification : references/dev_notes/DEV10_R19_QUALIFICATION.json.
DEV10 ouverte ; aucun push ni EXE, génération/données natives inchangées.
R19 validée par Julien le 2026-10-06 ; étape 4 limitée à l’éditeur/catalogue clôturée. Aucun nouveau test ajouté.
974 tests PASS (856.51 s) ; Tk quatre langues/deux thèmes, compilation et packaging PASS.
Molette validée ; resets valides mais doivent conserver le bruit sélectionné (DEV10).
Exports/EDM/MAP et erreurs avec bouton Copier : chantier dédié DEV11 ou DEV12.
Ouverture 832–1024 validée globalement dans l’éditeur modifié Settlers United ; réexport vers le jeu non fonctionnel.
Future MAJ pixel art distincte du lot éditeur/catalogue et des dessins récents.

## Candidate locale 2.0 DEV_10_R18 — sprites et agencement adaptatif

R17 appréciée avec corrections demandées : réduction des sprites refusée et
agencement/repositionnement encore trop espacés. R18 reprend ces points.
Sprites originaux 24 × 24 conservés, y compris avec texte ; aucun redimensionnement.
Éditeur : annuler/rétablir, transformations et importer/exporter/catalogue
partagent padx 2/pady 1 ; boutons à padding (5,0,5,1), hauteur Tk mesurée 31 px.
Catalogue : libellés/actions regroupés à côté de la vignette, fiches compactes ;
colonnes calculées avec la largeur requise des fiches, sans seuil fixe ni plafond.
En français : fiche + marges 259 px, deux colonnes à 560 px, trois à 800 px.
En-tête, Session et barre Vue : demandes Tk et marges réelles remplacent les
seuils fixes ; en-tête recalculé après sa propre allocation, langues prises en compte.
À largeur minimale, les commandes globales passent sur une rangée supplémentaire.
Générateur/bonus : rangées indépendantes pour éviter les colonnes partagées qui
créaient des espaces ; réserve supplémentaire de 32 px supprimée, viewport mesuré.
Disposition automatique des previews et ses seuils de lisibilité conservés.
F11 55/45, infobulles et disponibilité PNG de R17 conservés.
DEV10 ouverte ; aucun push ni EXE. Génération et données natives inchangées.
Qualification : references/dev_notes/DEV10_R18_QUALIFICATION.json.
Validation visuelle Windows R18 attendue. Aucun nouveau test ajouté.
974 tests vérifiés : 918 PASS en suite complète ; 56 erreurs de simulateur corrigées, 57 tests concernés PASS en relance.
Compilation et contrôles de packaging PASS ; aucun changement applicatif après lancement de la suite.

## Candidate locale 2.0 DEV_10_R17 — calibration et catalogue compact

R16 jugée « pas trop mal » par Julien ; ajustements demandés repris dans R17.
Boutons à icône seule : enveloppe commune 30 × 31 px mesurée (dé +1 px),
sprite 24 × 24 et marges minimales ; soleil/lune 20 × 20 avec compensation.
Images accompagnées de texte : affichage 16 × 16, cache par taille, PNG originaux
inchangés ; hauteur identique aux boutons textuels (33 px dans le banc Tk).
Les dimensions finales des boutons textuels suivent la police et l’échelle Tk/OS.
Infobulles traduites pour dé (principal/lot), thème (action suivante/raccourci)
et suppression des slots A/B ; autres actions compactes conservées.
Annuler/rétablir : mêmes colonnes, padx 2/pady 1 que les transformations.
Catalogue : modèles « Variable », fichiers utilisateur avec taille réelle ;
actions à 8 px des libellés, sans colonne centrale extensible, grille conservée.
F11 : vue 55 % / onglets 45 %, maximisation et ancrage supérieur conservés.
Enregistrer l’aperçu PNG désactivé au démarrage, activé au chargement comme Exporter.
DEV10 ouverte ; aucun push ni EXE. Génération et données natives inchangées.
Qualification : references/dev_notes/DEV10_R17_QUALIFICATION.json.
Suite complète : 974 tests PASS (1016.70 s), aucun nouveau test.
Tk réel quatre langues/deux thèmes, mesures et actions du lot PASS.
Compilation, intégrité et self-test après extraction PASS.
Validation visuelle Windows R17 attendue.


## Candidate locale 2.0 DEV_10_R16 — agencement et sprites partagés

R15 acceptée par Julien avec ajustements d’agencement demandés, repris dans R16.
Annuler/rétablir espacés ; importer/exporter côte à côte, catalogue en dessous.
Catalogue : actions alignées et séparées, grille adaptative de 1 à 4 colonnes.
Le redimensionnement réutilise les fiches et images ; aucun PNG relu à cette occasion.
Éditeur/catalogue : fenêtres redimensionnables avec agrandissement natif disponible.
Sprites réutilisés dans les actions compactes (infobulles localisées), l’historique
et les dialogues d’export ; cinq dessins de minerais dans le filtre thermique.
Nouveau dessin original Recentrer la carte intégré : 33 PNG, 54 sprites/frames.
F11 configurable : maximise le programme et rétablit les deux séparateurs
(position naturelle sous les contrôles, proportion vue/onglets 3:2).
F11 ne modifie ni le zoom ni la position de la carte ; Ctrl+R recentre la carte.
Un déplacement manuel reprend la main sur le séparateur horizontal.
DEV10 reste ouverte ; aucun push ni EXE. Génération et données natives inchangées.
Qualification : references/dev_notes/DEV10_R16_QUALIFICATION.json.
Suite complète : 974 tests PASS (557.10 s), un nouveau scénario F11.
Tk réel : quatre langues/deux thèmes, catalogue peuplé, historique/exports PASS.
Compilation, intégrité des sprites/génération et self-test après extraction PASS.
Validation visuelle Windows R16 attendue.


## Candidate locale 2.0 DEV_10_R15 — lot complet de sprites

R14 validée par Julien le 2026-10-05, avec inversion des deux miroirs signalée.
R15 corrige leur action selon les dessins : miroir horizontal inverse haut/bas,
miroir vertical inverse gauche/droite. Les actions restent annulables.
Les deux lots du 2026-10-06 couvrent les 24 sprites de l’éditeur/catalogue.
Les 13 existants sont remplacés par les dernières copies : seule la gomme change ;
les 12 autres sont identiques. Onze nouveaux dessins, PNG originaux conservés.
Icône + libellé sur les actions restantes, catalogue et dialogues thémés.
Fermer est également accessible dans le catalogue ; comportements conservés.
32 PNG au registre commun (53 sprites/frames). Aucun sprite du lot ne manque.
Suite complète : 973 tests PASS (545.88 s), aucun nouveau test.
Tk réel : boutons/catalogue/dialogues/sauvegarde, miroirs/undo, quatre langues
et deux thèmes PASS. Éditeur 686 px de haut sur écran 1366×768.
32 ressources, PNG originaux, génération inchangée, compilation et self-test PASS.
R15 acceptée avec remarques UI, traitées dans R16.
DEV10 reste ouverte, aucun push ni EXE ; génération et données natives inchangées.


## Candidate locale 2.0 DEV_10_R14 — deuxième lot d’icônes

R13 validée explicitement par Julien le 2026-10-05.
R14 intègre huit nouveaux PNG originaux 24×24 : annuler/rétablir, inverser les
gris, miroirs horizontal/vertical, rotations gauche/droite et remplissage.
Icônes + texte, cache partagé et thèmes/langues conservés. Remplissage par clic
de la zone contiguë de gris identique (4 voisins), avec le gris choisi.
Un clic = une action annulable ; cliquer sur le même gris ne crée pas d’historique.
Le clic droit reste la gomme ; rayon/bord doux ne changent pas le remplissage.
Rotations ±90° sans interpolation, annulables. Vingt-et-un PNG au registre.
Deux nouveaux scénarios automatisés pour frontières/historique et taille 512.
Génération et données natives inchangées ; DEV10 ouverte, aucun push ni EXE.
Suite complète : 973 tests PASS (564.66 s), deux nouveaux scénarios.
Tk réel : remplissage/historique/rotations, quatre langues/deux thèmes PASS.
Écran 1366×768 : éditeur 665 px de haut ; 21 sprites et self-test PASS.
55 fichiers de génération et 13 PNG précédents identiques à R13.
Compilation, maintenance documentaire et hashes protégés PASS.
R14 validée par Julien ; miroirs inversés signalés, corrigés dans R15. Suite des dessins par petits lots.


## Candidate locale 2.0 DEV_10_R13 — premier lot d’icônes et rangement

R12 : vignettes jugées très bien par Julien ; calcul hors ligne confirmé.
R13 intègre le premier lot dessiné par Julien : pinceau, gomme, pipette, rond,
carré. Les cinq PNG RGBA 24×24 sont copiés à l’identique, sans redessin.
Icône et libellé dans les menus et la sélection ; comportements de dessin,
événements, langues et thèmes conservés. Images réutilisées entre éditeurs.
Les sprites fournis sont regroupés sous assets/sprites par usage : éditeur,
minerais, marqueurs de joueurs et interface. Treize PNG (34 sprites/frames),
chargeur commun, registre, provenance/hashes et packaging source/Windows adaptés.
Les huit PNG précédents sont déplacés byte pour byte. Le self-test contrôle
les treize ressources. Vignettes procédurales et captures restent distinctes.
Suite complète : 971 tests PASS (578.37 s), deux nouveaux scénarios.
Tk réel : outils/formes, quatre langues/deux thèmes et photos partagées PASS.
Treize ressources, huit anciens PNG exacts et génération inchangée : PASS.
Compilation/self-test/protected hashes PASS.
Guide : docs/SPRITES.md ; qualification : references/dev_notes/DEV10_R13_QUALIFICATION.json.
R13 validée explicitement par Julien le 2026-10-05 ; DEV10 ouverte, aucun push ni EXE.


## Candidate locale 2.0 DEV_10_R12 — vignettes des sources

R11 validée et fonctionnelle selon Julien le 2026-10-05.
R12 ajoute vingt vignettes fixes pour les bruits et compositions dans le choix
de source principale et les six fusions. PNG 64×64 affichés en 24×24 ;
échantillons réels, seed/réglages constants, sans fusions ni masques.
Ce sont des repères de sélection ; les aperçus de travail restent dynamiques.
Images partagées entre sélecteurs, réutilisées après changement de langue ;
aucune génération au démarrage ou à l’ouverture des menus. Menus thémés,
état désactivé et navigation clavier conservés ; sélection inchangée sans action.
Provenance et hashes : data/source_thumbnails/manifest.json ; reconstruction
hors interface : tools/generate_source_thumbnails.py. Aucune règle native modifiée.
Suite complète : 969 tests PASS (599.00 s), deux nouveaux scénarios.
Tk réel : sept sélecteurs, quatre langues, deux thèmes, menus sans recalcul PASS.
55 fichiers de génération identiques à R11 ; compilation/self-test/hashes PASS.
Qualification : references/dev_notes/DEV10_R12_QUALIFICATION.json.
Validation Windows R12 attendue ; DEV10 ouverte, aucun push ni EXE.


## Candidate locale 2.0 DEV_10_R11 — masquage exact et vues persistantes

R10 validée par Julien le 2026-10-05. R11 ajoute le lot autorisé :
Masquer, permissions exactes noir=0/blanc=100%, gris proportionnel, force
0–100% initialisée à 100% lors du choix et inversion conservée dans le profil.
Les permissions se cumulent ; sur une fusion elles bornent sa contribution,
et ne remplacent pas le champ par zéro avant Mélanger/Minimum/etc.
Les modulations existantes gardent leur ordre ; aucune ne réactive une zone
bloquée par une permission sur la même cible. Une fusion suivante peut agir
sur une source masquée ; cible Résultat pour masquer la composition entière.
Vues libres, fixées en haut (défaut), à droite ou automatiques ; préférence
persistante. Zone de réglages indépendante du panneau fixe ; auto selon la
largeur/hauteur réelle de l’onglet, avec hystérésis. Changer le placement ou
la taille redessine les champs en cache sans relancer la génération ni
reconstruire les réglages. Clic sur une vue : agrandissement thémé du dernier
champ calculé, statistiques et légende macro accessibles.
Vignettes 24×24 dans le menu de masques et sur la sélection ; formes calculées
une fois, dessins copiés dans le profil, PNG invalides exclus, caches bornés.
Vignettes fixes des bruits/compositions : lot suivant distinct, pas implémentées.
Six nouveaux scénarios ; suite complète : 967 tests PASS (588.60 s).
Tk réel PASS : défilement fixe, placements sans régénération, masques et caches.
Parité exacte R10/R11 sur quatre previews 384 ; deux cartes complètes masquées
Legacy/Amélioré et exports EDM/MAP (checksums) PASS. Compilation/self-test PASS.
Détails : references/dev_notes/DEV10_R11_QUALIFICATION.json.
R11 validée et fonctionnelle selon Julien le 2026-10-05.
DEV10 reste ouverte ; aucune publication Git ni construction EXE.


## Candidate locale 2.0 DEV_10_R10 — cibles des masques et dialogues centrés

R9 validée par Julien le 2026-10-05. R10 implémente l’étape 3 autorisée :
chaque masque cible Défaut (résultat), Source principale ou Fusion 1–6.
Source : avant les fusions ; fusion : sur son propre bruit avant mélange ;
résultat : après toutes les fusions. Les profils anciens gardent Défaut.
Plusieurs masques sur une cible suivent l’ordre de la liste. Les miniatures
source/fusion affichent leur masque ; une cible absente/désactivée est signalée
et sans effet, sans redirection. Le masque suit sa fusion réordonnée ; sa
suppression conserve une cible supprimée à réaffecter explicitement.
Les dialogues thémés sont centrés sur leur parent, après calcul de leur taille,
et bornés à l’écran. Aucun changement de générateur/format binaire demandé.
Cinq nouveaux scénarios fonctionnels. Suite complète : 961 tests PASS (557,36 s).
Tk réel PASS : cibles, édition, déplacement/suppression et dialogues centrés.
Parité exacte R9/R10 : quatre previews 384 avec/sans masques résultat ; deux
cartes complètes ciblées passent leurs contrôles obligatoires. Compilation,
hashes protégés, auto-test extrait, CRC/parité archive PASS. Qualification :
references/dev_notes/DEV10_R10_QUALIFICATION.json. Fonctionnement R10 confirmé par Julien le 2026-10-05.
DEV10 reste ouverte ; candidate source locale, aucun push ni build EXE.
Suite du lot masques : bilan des sprites existants et des dessins/taille à fournir
avec Julien, après validation de l’étape 3 ; réorganisation non faite ici.
Les menus « suite » restent centrés sur la branche actuelle.


## Candidate locale 2.0 DEV_10_R9 — éditeur et sélection directe des masques

R8 : fonctionnement confirmé par Julien, avec remarques UI reprises dans R9.
R9 : fenêtres et confirmations de masques sous une infrastructure commune de
thèmes sémantiques, y compris changement de thème sur les fenêtres ouvertes.
Les sélecteurs de fichiers natifs restent régis par le système. Nouveau masque
est déplacé dans le catalogue : nouveau document vide, confirmation des dessins
modifiés, nom et historique remis à zéro ; Effacer tout reste une édition annulable.
Fermer / Enregistrer dans mes masques / Appliquer au profil sur une ligne.
Éditeur redimensionnable, dessin carré centré, coordonnées adaptées sans changer
la résolution, rafraîchissements regroupés au prochain idle. Contour du pinceau
rond/carré et nom/états PNG et profil visibles séparément.
Mes masques est directement accessible dans le sélecteur de la couche : PNG
carrés valides, vérifiés progressivement ; invalides/rectangles restent au
catalogue avec diagnostic/cadrage. Actualisation à chaque ouverture du menu et
relecture du fichier choisi ; cache partagé borné. Grille, résolution et nom sont
copiés dans le profil, sans dépendance au fichier après sélection.
Étape 3 différée. Réorganisation des sprites lors du prochain ajout fourni par
Julien, avec inventaire des fichiers et dessins effectués par le code ; pas maintenant.
Préférence de collaboration : proposer spontanément des améliorations pertinentes,
en distinguant le lot actuel des idées pour plus tard.
18 tests ciblés PASS (1,44 s), deux nouveaux scénarios seulement ; compilation PASS.
Essais Tk réels sous Linux PASS : redimensionnement/dessin, boîte de nom et sauvegarde,
restauration du focus/grab, catalogue, exclusion PNG invalide et rectangle,
démarrage MainWindow et propagation clair/sombre sur l’éditeur ouvert.
956 scénarios vérifiés : suite complète (946 PASS), puis reprise des dix contrôles
UI/docs corrigés (10 PASS). Aucun échec restant. Auto-test de ressources PASS.
R9 validée par Julien le 2026-10-05 : tout fonctionne bien. Réserve mineure :
le dialogue de confirmation de sortie apparaît en haut à gauche de l’écran.
À corriger dans la prochaine révision : centrer les dialogues de l’éditeur sur
leur fenêtre parente, après calcul de leur taille, en restant dans l’écran utile.
Aucun code modifié pour cette prise de notes ; aucun push.


## Candidate locale 2.0 DEV_10_R8 — commandes de dessin et sauvegarde visible

R7 validée par Julien le 2026-10-04 : « c’est parfait, tout semble bien fonctionner ».
Retour complémentaire : l’étape 2 doit être enrichie avec un curseur de sélection
et des commandes de dessin ; ne pas passer à l’étape 3 dans cette candidate.
R8 ajoute un curseur de gris, un dégradé cliquable et une pastille de la valeur
choisie ; curseurs rayon/bord doux synchronisés aux champs, y compris la pipette.
Choix rond/carré, chacun dur ou doux. Nouveau masque remet une copie à zéro et
vide son nom, avec undo possible ; aucune application automatique au profil.
La sauvegarde existait en R7 : son bouton est désormais visible en bas près
 d’Appliquer au profil. Un nouveau nom enregistre un nouveau PNG utilisateur.
Boutons groupés sur deux colonnes pour limiter la hauteur de la fenêtre.
22 ciblés PASS (1,66 s), dont deux nouveaux tests, traces Tcl réelles et fichiers PNG.
Compilation PASS. Suite complète : 954 tests PASS (546.00 s). Archive : CRC, parité source et auto-test extrait PASS. Fonctionnement R8 confirmé par Julien ; remarques UI traitées dans R9.
Toute la génération et les données exactes R7. Aucun push, DEV10 reste ouverte.
Étape 3 ciblage/source dessinée différée. Étape 4 éventuelle : icônes dessinées
et fournies par Julien pour apporter de la couleur, sans asset généré par IA.
Qualification : references/dev_notes/DEV10_R8_QUALIFICATION.json.

## Candidate locale 2.0 DEV_10_R7 — catalogue et éditeur de masques

R6 validée et fonctionnelle selon Julien le 2026-10-04. R7 implémente les étapes
1 et 2 du brainstorm approuvé : dossier masks dans les données utilisateur,
catalogue avec miniatures, ouverture du dossier/actualisation, ajout/suppression
et protection des modèles fournis. PNG externe reconnu sur son contenu réel ;
fichier illisible, animé ou excessif écarté individuellement avec un motif.
Couleur convertie en gris, transparence sur noir, masque uniforme utilisable.
Rectangle : choix explicite entre marges noires, recadrage central et étirement.
Éditeur : gris 0–255, rayon, bord dur/doux, gomme, pipette, undo/redo par trait,
inversion, miroirs et rotation. Résolutions 64/128/256/512, profil portable à sa
résolution ; cache du catalogue borné, miniatures ajoutées au prochain cycle idle.
Appliquer au profil, enregistrer dans mes masques et exporter sont distincts.
Six comparaisons de calcul 64 × 64 exactes R6 ; moteurs/données natives inchangés.
159 ciblés profils/masques PASS (90,98 s) ; 21 ciblés UI/architecture PASS (1,48 s).
Huit nouveaux tests au total. Compilation PASS. Suite complète : 952 tests PASS (544.24 s). Archive : CRC, parité source et auto-test extrait PASS.
R7 validée par Julien le 2026-10-04 ; aucun push, DEV10 reste ouverte.
Étape 3 proposée par Julien : cibler source principale/fusion ou utiliser le dessin
comme source de relief autonome. À cadrer après validation R7, non implémentée.
Qualification : references/dev_notes/DEV10_R7_QUALIFICATION.json.

## Candidate locale 2.0 DEV_10_R6 — langue du rapport Statistiques

R5 acceptable pour le moment selon Julien le 2026-10-04 : « on va dire qu’on est bon
pour le moment ». Aucun détail de scénarios Windows fourni ; DEV10 reste ouverte.
R6 corrige le rapport resté dans l’ancienne langue sans régénération. Le callback
existait mais Tk ignorait ses écritures dans le champ Text désactivé. L’écriture
est maintenant temporairement autorisée, puis l’état lecture seule et le défilement
sont restaurés. Carte, widget et statistiques en cache conservés.
L’audit statique précédent avait conclu à tort que cette traduction fonctionnait.
Un seul nouveau test reproduit ce défaut avant correction, puis vérifie EN/DE/ES/FR.
75 ciblés PASS (1,56 s). Suite complète : 944 tests PASS (684.70 s). Archive : CRC, parité source et auto-test extrait PASS.
R6 validée et fonctionnelle selon Julien le 2026-10-04 ; aucun push de candidate.
Refonte complète Statistiques : mise à jour dédiée après 2.1, contenu enrichi,
organisation et visuels plus jolis et interactifs ; version précise non décidée.
Qualification : references/dev_notes/DEV10_R6_QUALIFICATION.json.

## Candidate locale 2.0 DEV_10_R5 — blocage au démarrage R4

Julien signale le 2026-10-04 : run_gui.bat tourne sans fenêtre ni erreur.
Cause reproduite dans le constructeur des onglets : winfo_ismapped est faux
sur une page masquée même si ses barres sont déjà placées dans grid. R4 les
replaçait donc à chaque callback idle, puis reprogrammait le même callback.
La boucle pouvait empêcher update_idletasks de rendre la main au démarrage.
R5 compare le gestionnaire grid, indépendant de la visibilité de l’onglet.
Les mises à jour regroupées et correctifs des séparateurs R4 sont conservés.
Le lanceur BAT est inchangé ; aucun délai visuel fixe réintroduit.
Deux scénarios reproduisent la boucle avant correctif (échecs attendus), puis
se stabilisent après : onglet masqué et retrait/retour de ses barres.
193 ciblés PASS (8,64 s), deux nouveaux scénarios ; compilation PASS.
Suite complète : 943 tests PASS (729.71 s). Archive : CRC, parité source et auto-test extrait PASS. Démarrage/rendu Windows à confirmer.
R4 n’est pas validée ; ses tests/auto-test de ressources ne testaient pas ce cycle.
Génération et données natives exactes R4 ; hashes protégés PASS. Aucun push.
Qualification : references/dev_notes/DEV10_R5_QUALIFICATION.json.

## Candidate locale 2.0 DEV_10_R4 — séparateurs internes

Retour Julien sur R3 : peu de différence visible ; les redimensionnements
visés sont les séparateurs vue/onglets et contenu/inputs, pas seulement la fenêtre.
R3 n’est pas validée visuellement ; ses changements internes sont conservés.
R4 supprime les limites 160 px/20–65 % du séparateur supérieur. Par défaut,
il suit la hauteur réelle des inputs ; le haut ne reçoit plus l’espace gagné
par agrandissement. Une position manuelle reste en pixels, y compris zéro ou
un panneau partiellement masqué. Position proche des inputs = ancrage automatique.
Préférence vertical_split_height ; anciens ratios ignorés pour ce comportement.

Délais visuels fixes retirés : vue/graphique/onglets 24 ms, miniature adaptative
100 ms. Une seule mise à jour par lot au prochain cycle idle, sans temporisateur
relancé pendant le glissement. La carte n’est plus déplacée à son ancienne taille
avant son redessin. Ancienne PhotoImage conservée jusqu’au remplacement attaché
au canvas, pour la vue et le graphique. Délais calcul de relief et molette inchangés.
220 ciblés PASS (7,55 s), dont cinq nouveaux scénarios ; compilation PASS.
Suite complète : 941 tests PASS (684.16 s). Archive : CRC, parité source et auto-test extrait PASS. Validation visuelle Windows à venir.
Génération/formats/données natives identiques R3 ; hashes protégés PASS.
Bruit Custom via une ou plusieurs équations manuelles non implémenté : bilan
fin DEV10 pour faisabilité/intérêt, puis décision de programmation éventuelle.
Aucun push ; DEV10 ouverte. Qualification : references/dev_notes/DEV10_R4_QUALIFICATION.json.

## Candidate locale — 2.0 DEV_10_R3 — mises à jour UI

Base R2 validée ; candidat source local, validation visuelle Windows à venir.
Les modes Classique/Amélioré et les resets Générateur chargent désormais les
valeurs dans les contrôles existants. Les dépendances sont rafraîchies après
le chargement complet, sans états intermédiaires propagés par les traces Tcl.
Une sortie de champ sans modification ne crée plus de profil Personnalisé.
Une modification Générateur seule ne recalcule plus le relief Archétype.
Les reconstructions de langue restent autorisées ; leurs anciens callbacks
de redimensionnement et travaux différés sont retirés. Les dispositions
inchangées ne sont plus réappliquées et le dernier aperçu calculé est redessiné
sur les nouveaux canvas pendant la reconstruction.

179 tests ciblés PASS (9,41 s), dont 57 cas de cycle UI avec traces Tcl réelles,
modes/resets dans les quatre langues, identité des contrôles, dépendances,
callbacks et aperçus. Géométrie testée avec des widgets de simulation : aucun
contrôle visuel Windows revendiqué. Suite complète : 936 tests PASS (745.40 s). Archive : CRC, parité source et auto-test extrait PASS.
Génération, formats et données natifs identiques aux octets R2 ; hashes protégés PASS.
R1/R2 restent validées ; DEV10 ouverte, aucun push de candidate.
Détail : references/dev_notes/DEV10_R3_QUALIFICATION.json.

## Candidate locale 2.0 DEV_10_R2 — gemmes/soufre bonus

191 tests ciblés PASS (8,25 s), cinq minerais/deux formes/trois modes qualifiés.
Douze poses et quatre cartes exactes R1 avec nouveautés OFF. Quatre cartes
avec dix zones chacune (deux joueurs), huit exports MAP/EDM : checksums et
relecture Area PASS. Profils/digest/reset et hashes protégés PASS.
Suite complète : 879 tests PASS (545.70 s) ; archive contrôlée PASS.
R1 et R2 validées par Julien. R2 : « ok c’est validé ça fonctionne », le 2026-10-04.
Détail des manipulations non fourni ; aucun push de candidate.

Archive R2 : CRC, parité avec la copie source et auto-test extrait PASS.


## Candidate locale 2.0 DEV_10_R1 — premier lot court

Extension commune aux cinq bonus, 34 par défaut ; tooltips courts complétés.
851 tests PASS (539.10 s) ; 150 ciblés PASS (11,34 s).
Quatre cartes Area/départs exactes DEV9, validations dures et hashes protégés PASS.
Détail : `docs/DEV_10_PROGRESS.md`. R1 validée par Julien le 2026-10-04 ; manipulations détaillées non fournies.
Aucun push : checkpoint Git DEV9 et sa CI réussie conservés.


Archive : CRC, parité avec la copie source et auto-test extrait PASS.

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

R20 : 982 cas exécutés (977 PASS initiaux ; cinq écarts de références/version/fixture
corrigés et requalifiés par les suites ciblées). Aucun changement du code de
génération après lancement de la suite. Maintenance 10 PASS, resets 17 PASS,
packaging 6 PASS ; quatre générations désert/bonus, hashes et auto-test extrait PASS.

Qualification finale R46 : 1147 passed, 2 skipped in 754.45s (0:12:34).
1 000 comparaisons natives, 500 comparaisons point/fixture et 11 emprises PASS.
Autotest source et hashes protégés PASS. Essai Windows/jeu attendu.

Qualification finale R47 : 1173 passed, 2 skipped in 718.66s (0:11:58).
10 188 comparaisons avec les fonctions natives PASS (jeu, éditeur standard et United).
Autotest source, hashes protégés et rendu des deux projections PASS. Essai Windows/jeu attendu.

Qualification finale R48 : 1193 passed, 2 skipped in 740.86s (0:12:20).
Parité des filtres export/import, cas J5 et autotest source PASS. Essai Windows/jeu attendu.

Qualification finale R49 : 1 failed, 1202 passed, 2 skipped in 737.92s (0:12:17); corrected documentation: 10 passed (targeted rerun).
Trois EDM et deux contextes PASS ; gardes privés et hashes protégés PASS.
Autotest source PASS ; confirmation visuelle Windows attendue.

Qualification R50 : Wokkel.map relu sans modification ; 888 colons, 6 bâtiments,
303 piles. Le contexte « avant objets » réinitialise sur copie objets et claims :
44 718 vertes et 3 266 jaunes. Les trois EDM R49 gardent des zones dans les deux
contextes ; le garde explicite d’un contexte natif inconnu reste actif.
Autotest source PASS, hashes protégés PASS. Suite pytest indisponible dans
l’environnement de cette reprise (module pytest absent) ; validation visuelle Windows
attendue.
