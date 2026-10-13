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
- [ ] Confirmer le build Windows après cette correction ; premier run bloqué
  pendant les tests, avant le packaging. Voir RELEASE_VALIDATION.

## Surveillance conditionnelle — ne bloque pas DEV10

- Reprendre les rares îles pauvres en montagne seulement avec un nouveau seed
  reproductible ; les archétypes déjà validés restent conservés.
- Intégrer de nouveaux sprites seulement à réception de nouveaux assets.

## Formats et recherches restantes — hors clôture DEV10

- [ ] Tokens d'empreinte non couverts et champs inconnus : audit non-terrain EXE.
- [ ] Bloc 9 live/SAV : registre de piles probable, records 14 octets vs 8 en MAP/EDM ;
  valider types/quantités/index en capturant création/mouvement/consommation.
- [ ] Valider la taille directe candidate contre la taille en jeu avant de
  remplacer l'heuristique ; flags byte 10 et lien registry bytes 2–3 restent partiels.
- [ ] Ne pas généraliser aux builds EXE non identifiés par hash ni aux capacités
  des tables à partir d'un simple compteur observé.
- [ ] Équipes aléatoires « ? » : différées ; « − » = groupes natifs distincts.
- [ ] Améliorations de placement dédiées : terrains d'expansion/équipes et
  placements manuels seulement si nouveau lot décidé. Conserver modes actuels.

## v2.0 — reconstruction native Legacy, puis Custom

La **reconstruction complète des pipelines** est le périmètrev 2.0. Les moteurs
Legacy/Upgraded indépendants et les presets Custom sont implémentés ; histoire
dans CHANGELOG. Natif protégé, mineraisv 7 no-gap, géographie d'abord et bonus
hors quotas sont conservés. Maximum 768 ; Petites îles abandonné ; Archipel hors 2.0.

## v2.1 — ouverture

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

## Publication RC/STABLE — après DEV10

- [ ] Geler fonctionnalités, qualifier ressources/exports/settings/updater,
  intégrité, rollback et installation propre ; ZIP source et Windows portable.
- [x] Présentation courante des README français/anglais actualisée pour R66 ;
  historique détaillé conservé dans CHANGELOG et les références du ZIP.
- [ ] À la publication : revoir captures réelles, About/Topics et icône manuelle ;
  contrôler les informations publiques au moment de publier.
- [x] Notes et snapshot synchronisés avant promotion DEV10 ; nom sans suffixe R.
  Publication sur dev autorisée ; main/tags/releases exigent instruction explicite.

## Invariants

HEX 6, transitions et profils Legacy/Upgraded séparés ; inconnus restent inconnus.
Aucune image inventée. SAV copié inchangé. La documentation n'est pas une
implémentation ; validations automatiques, Windows et en jeu restent distinctes.
