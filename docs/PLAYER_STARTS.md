> Actualisation R64 : les défauts R63 décrits historiquement ci-dessous sont
> corrigés dans le rendu, compteurs et focus par format/terrain ; byte7 courant
> et byte14 original séparés. Marqueurs de chantier exclus du filtre terrain+objets.
> Conversion SAV→EDM/MAP reste à auditer ; validation visuelle Windows attendue.

# Départs des joueurs — guide courant

État : R63 validée le 13 octobre 2026. R64 les ancre désormais au pointeur ;
leur position est à confirmer sur le poste Windows.

## Algorithmes

| Choix | Comportement |
|---|---|
| Auto | Éloignement sur continent, Îles si labels insulaires disponibles |
| Éloignement | Cherche l'espacement ; respecte le contrat insulaire si présent |
| Équilibré | Accès minier local et espacement avant objets ; aucun quota par île |
| Îles | Solveur sur masses identifiées, individuel ou par équipe |
| Classique | Sélecteur natif après objets, avec civilisations ; pas de quota par île |

Fair/Classique refusés sur Îles par équipe ; Îles explicite nécessite les labels.
IDs stables : `auto`, `balanced`, `fair`, `islands`, `classic`. Détails, bancs
natifs et limites : `../references/SETTLERS3_START_ALGORITHMS_REFERENCE.md`.

## Civilisations et équipes

Joueurs… configure les slots actifs : Romains 0, Égyptiens 1, Chinois 2, Amazones 3,
Choisir 255. Choisir reste exporté 255 ; l'éditeur le traite comme Romain, le
contrôle de génération conserve la sécurité des quatre nations. Le jeu résout
le choix avant ses tables métier. Aucun humain/bot n'est imposé par le choix.
« − » (0 interne) = aucune alliance ; chaque joueur obtient une équipe native
distincte à l'export. Numéros positifs égaux = alliance commune ; groupes natifs
contigus à partir de 0, en ordre de première apparition. « ? » reste différé.
Sur Îles par équipe, ces groupes définissent les masses et surfaces.
CLI : `--start-algorithm classic --start-nations 0,1,2,3` ;
`--player-teams 1,1,2,2`. Maximum768.

## Filtre des départs valides

- Avant objets : terrain/relief seul. Carte actuelle : terrain/relief + objets
  Area. Bâtiments, unités, piles de ressources et claims sont ignorés dans
  les deux contextes, sur copie, sans modifier l'import.
- Vert = prédicat éditeur admis ; jaune = contrôle exact jeu admis, éditeur
  refusé. Un vert peut échouer au contrôle exact jeu : le survol signale la
  recherche voisine possible. Aucune garantie de position voisine ni de lancement.
- Éditeur : empreinte 70 positions, herbe 16 pour tous, terrain 20/64/65 aussi pour
  Égyptiens, occupation nulle ; son prédicat local ne vérifie pas la hauteur.
  Espacement>=50 pour starts réellement posés, distinct du raster des candidats.
- Jeu : prédicats de terrain, empreinte et nivellement. Toutes civilisations
  = intersection des quatre contrôles, jamais union. Famille herbe 16/18/19/23/24
  et terrain 20 admis par le prédicat terrain ; désert 64/65 Égyptiens seulement ;
  boue 144/145 Chinois seulement. Autres conditions peuvent encore refuser.
- Même préparation United sur copie que l'export, pour éviter l'écart entre
  génération et réimport. Badges des starts : état final et espacement.
- SAV : objet courant byte 7, pas original byte 14. Le catalogue runtime diffère
  des cartes : interprétation contextuelle à compléter dans R63. Marqueurs de
  chantier 112/113 ne doivent pas réintroduire les bâtiments dans ce filtre.

## Bonus marais et preuves

Bonus marais seulement Chinois/Choisir, sur la masse terrestre du start ;
distances et forçage conservés, omission diagnostiquée si aucune place légale.
Les autres bonus suivent leurs règles. Le nouveau Continental n'active pas ce
bonus par défaut. Sprites de civilisation fournis par Julien.

R63 :58 générations,8 refus attendus,36 roundtrips,77 tests ciblés passent.
Qualification : `../references/dev_notes/DEV10_R63_QUALIFICATION/`.
Historique des primitives et tests natifs :
`../references/history/SETTLERS3_STARTS_RESEARCH_BEFORE_R63.md`.
Validations automatisées et retour utilisateur distingués ; défaut tooltip
et échec hydrologique hérité consignés dans TODO/RELEASE_VALIDATION.
