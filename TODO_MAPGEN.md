# Settlers III MapGen — TODO

> Roadmap orientée **travail restant**. Reprise : PROJECT_WORKFLOW, index et
> snapshot courant. DEV10 complète validée le 13 octobre 2026 ; publication sur dev autorisée.

## Lot R64 — UI et imports SAV

- [x] Validation visuelle Windows R64 : tooltips bien placés et faux récifs
  terrestres absents des SAV chargés (Julien, 13 octobre).

- [x] R64 — corriger la position des tooltips : affichés loin de la souris, en haut
  à gauche de l'écran (retour Windows Julien). Revalider visuellement après fix.
- [x] R64 — rendre le catalogue d'objets contextuel format/terrain dans le rendu et
  les stats SAV : récifs carte 111–114→runtime 13–16 sur eau ; chantier 112/113
  sur terre. Préserver IDs bruts ; ne pas inventer la signification 111/114 terrestres.
- [x] R64 — conserver séparément objet courant byte 7 et original byte 14 ; cycles de
  croissance/abattage/cultures selon références et preuve, sans reconstruire
  le terrain initial depuis l'objet original.
- [x] R64 — vérifier le filtre terrain+objets SAV : marqueurs de chantier ignorés en
  tant que construction, sans réintroduire bâtiments/colons/piles/claims.
- [x] R65 — conversion SAV→nouvelle carte avec objets contextuels, starts, nations et alliances. Copie SAV inchangée.
- [x] R65 — lot validé par Julien ; partie générée en cours fonctionnelle. Fichiers SAV exacts et parcours éditeur non précisés.
- [x] Hydrologie : cas256/seed20260921 et trois autres seeds conformes avec Amélioré dans les deux moteurs ;28 tests dédiés PASS. Classique natif conservé, point clôturé.

## Historique clôturé — v1.9 (non prescriptif)

Historique dans CHANGELOG, history/ et bilan DEV9. R63 placements validée ;
Îles individuelles, Îles par équipeR 59 et ContinentalR 62 validés. Les anciennes
cases R35–R50 de validation de filtres/relief sont remplacées par ces retours,
sans inventer une validation en jeu de chaque ancien fichier exact.

## DEV10 — clôturée (bilan dans docs/DEV_10_CHECKPOINT.md)

- [x] R66 — test de connectivité hérité recadré sur Amélioré ; Classique natif inchangé.

- [x] Parcours éditeur→réexport→jeu confirmé déjà testé par Julien le 13 octobre.
  Fichiers/seeds exacts non précisés ; aucune attestation exhaustive inventée.
- [x] Évaluer bruit Custom par équations : faisable, essai numérique256/768 et intégration audités ; référence SETTLERS3_NOISE_FORMULA_REFERENCE.md.
- [x] V1 Formule autorisée par Julien et implémentée R66.
- [x] R66 — implémentation Formule validée pour la 2.0 par Julien après essai ;
  aucun défaut signalé, sans attestation individuelle de tous les scénarios.
- [x] Sprites reçus intégrés et contrôlés : quatre civilisations, cadenas et
  drapeau des départs. Auto-test du 13 octobre : 52 sprites présents, PASS.
- [x] Prochain lot cadré : bilan de clôture DEV10, contrôle du parcours éditeur,
  consolidation des livrables ; pas de nouvelle fonctionnalité Formule.
- [x] Bilan DEV10 consolidé ; checkpoint complet et push explicitement autorisés.

## Build Windows DEV10 — maintenance

- [x] Conditions du test desktop et cycle de vie Tcl corrigés ; CI isolée sans
  supprimer de tests. Contrôles locaux PASS, applications/natif inchangés.
- [x] Build Windows confirmé : 1306 tests et 4 subtests PASS, smokes PASS,
  portable construit et auto-test figé PASS. Run 38467559806 ; voir RELEASE_VALIDATION.

## DEV11 — clôturée et validée le 1er novembre 2026

Bilan : docs/DEV_11_CHECKPOINT.md. Push complet et publication 2.0 explicitement autorisés.

Checklist de clôture active : docs/RELEASE_2_0_CHECKLIST.md.
- [x] R15 : revue documentaire et ordre de qualification Windows clarifiés.

- [x] R12 : lots et sprites acceptés pour la passe 2.0 par Julien le 29 octobre ; ajustements éventuels en 2.1.
- [x] R13 : corriger le plantage de finalisation des lots et traduire les contraintes de départs insulaires.
- [x] R13 : intégrer les dessins soleil/lune 20px fournis par Julien sans retouche.
- [x] R13 acceptée par Julien le 31 octobre ; correction des lots et sprites validés pour cette passe.
- [x] R14 : dernière capture des lots avec A/B intégrée sans retouche ; README FR/EN actualisés.


Décision du 14 octobre 2026 : aucune étape RC. Développement, corrections,
qualification du portable et essais utilisateur restent sur `dev` avant STABLE.
Le lot équipes/audit est autorisé le 14 octobre. Les autres sujets restent
des propositions ; Stats 2 conserve son échéance après 2.1.

- [x] R1 — équipes « ? » : nombre réglable (2 par défaut), tirage déterministe,
  effectifs équilibrés, équipes manuelles et joueurs « − » conservés ; GUI,
  lots, aperçus et exports reliés. Étape validée par Julien le14 octobre.
- [x] R1 — audit des surfaces sur 12 cartes : minerais/poissons adaptés au support ;
  quotas arbres/pierres/décors à la surface totale. Pas de saturation arbres/pierres
  mesurée ; aucun recalibrage automatique dans ce lot. Voir docs/DEV11_SURFACE_AUDIT.md.
- [x] DEV11 R3 — case globale de prorata des quotas, cochée par défaut ; OFF
  reprend la surface totale de carte. Pas de révision dédiée à cette seule case.
- [x] DEV11 R4 — retour Julien : case sans effet sur base Classique à100%. OFF
  active les remplacements globaux Custom ; ON garde les familles natives
  inchangées. Essai GUI ON/OFF réel reproduit et corrigé ; validation utilisateur
  R4 validée par Julien le 18 octobre : case fonctionnelle, quotas meilleurs.
- [x] DEV11 R4 — îles par équipe : même référence terre/océan corrigée que le
  Continental, gain atténué par nombre d’îles. Budgets solo/Continental conservés.
- [x] R3 — départs par équipes validés par Julien sur plusieurs essais le 18 octobre.
- [x] R5 — calibration indépendante sur la surface réelle de chaque contour
  insulaire avant les lacs, îles individuelles et par équipes ; aperçu et
  classification des deux moteurs utilisent les seuils locaux.
- [x] R5 — Continental sans adaptation insulaire automatique ; amplitude manuelle conservée.
- [x] R5 — défauts Amélioré, section Générateur : désert 50 %, boue 50 %.
  Réglages des profils enregistrés conservés ; validation utilisateur R5 à venir.
- [x] R6 — résolution des valeurs insulaires hors Tk, aperçu différé hors onglet,
  résultats obsolètes invalidés dès changement ; fluidité validée par Julien
  le18 octobre : lag disparu et paramétrage possible pendant l’aperçu.
- [x] Mini-audit Équilibré : 14 cartes / 92 départs, validité et espacement
  conformes sur cet échantillon ; aucune correction urgente proposée.
  Limites rivières/expansion et absence de quota par île documentées dans
  docs/RELEASE_2_0_SCOPE.md. Prochaine étape : brainstorm réorganisation UI.
- [x] Placement manuel et futur onglet Départs reportés après 2.0 ; inclure
  l’affectation de la même équipe à plusieurs joueurs. Périmètre à cadrer ensuite.
- [x] Aucun nouvel archétype avant l’après-2.0. Conserver les idées : deux
  continents, péninsules, détroits, mers intérieures, quasi-atoll.
- [ ] Préparer directement STABLE sur `dev` : portable, préférences et données utilisateur,
  intégrité et documentation/captures réelles, sans branche RC.
- [x] Reports bonus/minerais vérifiés contre le code : extension du forçage
  configurable (`center_extension_limit`, défaut 34), bonus gemmes/soufre et
  tooltips minéraux/bonus déjà présents ; ne pas les réimplémenter depuis un vieux TODO.

- [x] R12 — lots : archétype Classique disponible ; copies contextuelles du générateur/archétype
  personnalisés présentes uniquement si actives à l’ouverture, allers-retours conservés.
  Réglages communs visibles, équipes/civilisations copiées, requêtes figées pour cache/génération.
- [x] R12 — quatre drapeaux et nouvelle pipette fournis par Julien intégrés sans retouche.
- [x] R12 — README FR/EN recentrés sur la 2.0 ; captures Windows R11 récentes intégrées.
- [x] Passe lots/sprites acceptée en R13 ; capture finale Windows fournie le 31 octobre et intégrée en R14.

## Fonctionnalités à planifier — sans échéance attribuée

- [x] R7 — presets complets dans l’onglet Configurations : générateur/archétype,
  taille, joueurs, civilisations, équipes, départs, miroir et seed facultatif.
  Collection locale auto-enregistrée ; import/export JSON unique avec masques.
  Validé par Julien le 19 octobre 2026 après essai : fonctionnement satisfaisant.
- [ ] Revoir une liste de configurations dans l’en-tête seulement lors d’un
  futur remaniement global ; aucun emplacement réservé pour le moment.

- [x] R8 — regroupe Validations, Pipeline et Métadonnées sous Diagnostic.
  Trois sous-onglets ; Statistiques reste directement accessible.
  Nom validé par Julien ; organisation provisoire acceptée par Julien le 22 octobre 2026.
- [ ] Après 2.0 : améliorer la lisibilité des trois vues Diagnostic : résultats
  structurés, libellés compréhensibles, problèmes/avertissements/informations
  distingués, causes et conséquences expliquées ; conserver le détail technique
  accessible pour approfondir, au lieu de restituer les processus internes bruts.

## Surveillance conditionnelle — ne bloque pas DEV10

- Reprendre les rares îles pauvres en montagne seulement avec un nouveau seed
  reproductible ; les archétypes déjà validés restent conservés.
- Surveiller les îles longues et fines : une surface importante peut masquer
  une faible largeur ; pas de règle supplémentaire sans cas reproductible.
- Intégrer de nouveaux sprites seulement à réception de nouveaux assets.

## Formats et recherches restantes — hors clôture DEV10

- [ ] Tokens d'empreinte non couverts et champs inconnus : audit non-terrain EXE.
- [ ] Bloc 9 live/SAV : registre de piles probable, records 14 octets vs 8 en MAP/EDM ;
  valider types/quantités/index en capturant création/mouvement/consommation.
- [ ] Valider la taille directe candidate contre la taille en jeu avant de
  remplacer l'heuristique ; flags byte 10 et lien registry bytes 2–3 restent partiels.
- [ ] Ne pas généraliser aux builds EXE non identifiés par hash ni aux capacités
  des tables à partir d'un simple compteur observé.
- [x] Équipes aléatoires « ? » implémentées R1 ; « − » = groupes natifs distincts.
- [ ] Terrains d’expansion et placements manuels : cadrage ultérieur.
  Algorithme de départs par équipes inscrit explicitement dans la 2.0 ci-dessous.

## v2.0 — reconstruction native Legacy, puis Custom

La **reconstruction complète des pipelines** est le périmètrev 2.0. Les moteurs
Legacy/Upgraded indépendants et les presets Custom sont implémentés ; histoire
dans CHANGELOG. Natif protégé, mineraisv 7 no-gap, géographie d'abord et bonus
hors quotas sont conservés. Maximum 768 ; Petites îles abandonné ; Archipel hors 2.0.

- [x] DEV11 R3 — choix **Par équipes** : chaque équipe de son côté, alliés
  espacés, sans attraction vers un centre commun ; effectifs pris en compte,
  sans imposer une superficie par joueur. Contrats insulaires conservés. Qualification/essai utilisateur R3
  distincts ; tirage des équipes « ? » reste le lot R1.

## v2.1 — ouverture

- [x] Audit issu de DEV8 (20 septembre, R29/R30), repris en DEV11 R1 : docs/DEV11_SURFACE_AUDIT.md.
- [x] DEV11 R2 — quotas par supports implémentés ; référence médiane de cinq
  Continental768/12P, arrondi fractionnaire par seed et estimations explicites.
  Validation utilisateur R2 en attente. Passes natives conservées.
- [x] DEV11 R2 — décors Custom/Legacy : remplacement à la granularité des
  sous-familles modifiées, familles inchangées conservées. Essai utilisateur attendu.


- [ ] Lire le todo personnel de Julien au débutDEV 1 ; le demander s'il manque.
- [ ] Fiabiliser pose minérale Amélioré sur montagnes morcelées, quotas/supports
  légaux conservés ; repli insulaire n'est pas correction générale.
- [ ] Réglage boutons sprite+texte / sprite+tooltip / texte.
- [ ] Tester personnalisation des couleurs joueurs ; aucune mise en œuvre actuelle.
- [ ] UI responsive/rafraîchissements/clignotements : passe avec mesures si requis.

## Mise à jour dédiée Statistiques (Stats 2) — après v2.1

- [ ] Distances centres/bordures, alliés/adversaires ; valeurs actuelles conservées.
- [ ] Contenu, organisation, visuels interactifs : inventories, familles runtime,
  distributions et références corpus ; cadrage au démarrage, pas chantier immédiat.
- [ ] Joueurs/stocks, entités filtrées (slots 255 libres/recyclés), bâtiments et
  progression : champs observés vs hypothèses explicités. Ne pas déduire chantier
  définitivement bloqué depuis un seul instantané ; santé de siège reste inconnue.
- [ ] Graphiques→Vue, légendes/clic persistant, multi-cartes 3+ si utile.
- [ ] Réévaluer Comparaison/A-B, labelsJ 1–J 20, loupe/inspecteur près du curseur.
- [ ] RésolutionPNG et carte topographique/classes d'altitude éventuelles.
- [ ] Garder deux rayons configurables pour ressources proches.

## ENDGAME et idées sans échéance

- [ ] Hors 2.0, bien plus tard : éditeur de formules dédié, inspiré de l'éditeur
  de masques, avec visualiseur et explications améliorées. V1 R66 acceptée.

- [ ] Mode éditeur après générateur : modifier uniquement données comprises,
  placement des unités/bâtiments/piles avec validité distincte de terrain+objets.
- [ ] Replay par instantanés : tick du jeu, pause/vitesse, réutilisation d'indices,
  événements courts manqués ; aucune resimulation exacte promise sans ordres/RNG.
- [ ] Formes/espacement de forêts et groupes de pierres, poissons/lacs bonus
  plus paramétrables seulement si besoin établi.
- [ ] RelireDE/ES, packs langues/thèmes et commandes rebindables.
- Nombre de zones par minerai : déprogrammé indéfiniment ; reprendre seulement
  sur demande explicite. Pixel art manuel dédié à planifier.

## Publication 2.0 autorisée — sans étape RC

- [x] Fonctionnalités gelées ; ressources/exports/settings et données utilisateur de recette qualifiés,
  intégrité et lancement sans dépendances à télécharger ; ZIP source et Windows portable.
- [x] Présentation courante des README français/anglais actualisée en R14/R15 ;
  historique détaillé conservé dans CHANGELOG et les références du ZIP.
- [x] Captures réelles et icônes acceptées ; About/Topics vérifiés le 1er novembre.
- [x] Notes et snapshot synchronisés avant promotion DEV10 ; nom sans suffixe R.
  Publication sur dev autorisée ; main/tags/releases exigent instruction explicite.

## Décisions de clôture — 20 octobre 2026

- [x] R9 — ancien lanceur/script de mise à jour retirés, documentation actualisée.
  Aucun check automatique, notification, téléchargement ou remplacement en un clic.
  Téléchargement manuel GitHub ; futur bouton manuel dans À propos sans échéance.
- [x] Portable Windows R15 construit, rapports PASS et essai accepté le 1er novembre : lancement direct .exe avec icône, sans installation
  de Python ni téléchargement de dépendances ; pas de lanceur .bat inutile.
- [x] R10 — quatre BAT source/build examinés et conservés : lancement, dépendances,
  installation de Python et compilation. Code retour du lanceur de build corrigé ;
  aucun BAT dans le portable. Détails : docs/WINDOWS_LAUNCHERS.md.
- [x] R9 — dessins 16×16 et 64×64 retrouvés et intégrés, ICO multi-tailles.
- [x] Répartition acceptée le 27 octobre : petite pour 16/20/24, grande pour 32 et plus.
- [ ] Plus tard : Julien dessinera une version intermédiaire de l’icône ;
  non bloquant pour la 2.0, aucune modification artistique à produire ici.
- [x] Passe d’essai Windows R15 acceptée globalement : petite/grande version selon
  l’affichage réel ; vérifier Explorer, raccourcis, fenêtres, Alt+Tab, barre des
  tâches et Gestionnaire des tâches là où Windows permet cette présentation.
- Suppression de rc : étape automatique du workflow 2.0 après publication réussie ;
  autorisation reçue, pointe protégée contre un changement concurrent.
- [x] R11 — audit source entre versions : chemins communs, préférences, configurations
  et masques ; corrige l’oubli du filtre de départs dans la sauvegarde GUI.
- [x] Passe de conservation des données du portable R15 acceptée globalement par Julien le 1er novembre ; détails des cas individuels non précisés.

## Invariants

HEX 6, transitions et profils Legacy/Upgraded séparés ; inconnus restent inconnus.
Aucune image inventée. SAV copié inchangé. La documentation n'est pas une
implémentation ; validations automatiques, Windows et en jeu restent distinctes.

