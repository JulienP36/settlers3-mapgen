# Départs des joueurs — guide courant

État : DEV11 R3 locale, placement par équipes à tester ; tirage R1 validé. Base DEV10 validée ;
position des tooltips et objets SAV corrigés/acceptés en R64, conversion en R65.

## Algorithmes

| Choix | Comportement |
|---|---|
| Auto | Éloignement sur continent, Îles si labels insulaires disponibles |
| Éloignement | Cherche l'espacement ; respecte le contrat insulaire si présent |
| Équilibré | Accès minier local et espacement avant objets ; aucun quota par île |
| Îles | Solveur sur masses identifiées, individuel ou par équipe |
| Par équipes | Chaque équipe dans son secteur, alliés espacés ; respecte les îles |
| Classique | Sélecteur natif après objets, avec civilisations ; pas de quota par île |

Fair/Classique refusés sur Îles par équipe ; Îles explicite nécessite les labels.
IDs stables : `auto`, `balanced`, `fair`, `islands`, `classic`, `teams`. Détails, bancs
natifs et limites : `../references/SETTLERS3_START_ALGORITHMS_REFERENCE.md`.

## Civilisations et équipes

Joueurs… configure les slots actifs : Romains 0, Égyptiens 1, Chinois 2, Amazones 3,
Choisir 255. Choisir reste exporté 255 ; l'éditeur le traite comme Romain, le
contrôle de génération conserve la sécurité des quatre nations. Le jeu résout
le choix avant ses tables métier. Aucun humain/bot n'est imposé par le choix.
« − » (0 interne) = aucune alliance ; chaque joueur obtient une équipe native
distincte à l'export. Numéros positifs égaux = alliance commune ; groupes natifs
contigus à partir de 0, en ordre de première apparition. « ? » (-1 dans la demande) tire une équipe selon le seed. Le nombre se règle
dans Joueurs… (2 par défaut, 2 à 20). Seuls les joueurs actifs « ? » participent ;
les joueurs « − » et les équipes positives restent fixés. Les tirages rejoignent
les équipes les moins nombreuses, avec départage par seed. Le nombre inclut les
alliances manuelles ; il augmente si elles sont plus nombreuses et diminue
si trop peu de joueurs peuvent participer. Les étiquettes manuelles sont
conservées, les nouvelles utilisent les premiers numéros disponibles.
Sur Îles par équipe, ces groupes définissent les masses et surfaces.
CLI : `--start-algorithm classic --start-nations 0,1,2,3` ;
`--player-teams "?,?,?,?" --random-team-count 2` ou équipes explicites. Maximum768.
Les exports n’écrivent jamais « ? » : ils utilisent le résultat de ce tirage,
y compris pour former les îles. Aucun tirage ne consomme le PRNG natif du relief.
La demande reste sélectionnée dans la session pour les seeds suivants ; les
équipes et leur nombre ne sont pas des préférences persistées.

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
  des cartes : interprétation contextuelle intégrée en R64. Marqueurs de
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
Validations automatisées et retour utilisateur distingués. Tooltips R64 et
hydrologie Amélioré clôturés dans DEV10 ; aucun changement Classic natif.

## Par équipes — R3

Choix explicite, sans changement du routage Auto. Sur continent : choisit des
centres admissibles et espacés en préférant montagnes/rivières de la même masse,
puis attribue les équipes à des secteurs. Deux groupes ont une séparation par
un axe ; plusieurs groupes occupent des secteurs angulaires contigus, avec les
effectifs exacts. Les rotations et ordres d’affectation dépendent du seed.
Le solveur ne rapproche aucun allié vers un centre commun. « − » forme un
groupe indépendant ; « ? » est résolu avant cette étape. Une seule équipe garde
la répartition sur toute la carte. Les espaces inutilisables ne sont pas forcés.
Sur Îles individuelles : un start par île conservé, propriété attribuée par
secteurs. Sur Îles par équipe : correspondance joueurs/îles et placement validé
conservés. Terrains, objets et nivellement restent des conditions de validité ;
proximité et secteurs ne garantissent pas richesse ni trajet praticable en jeu.
CLI : `--start-algorithm teams`. La clé est distincte dans le cache de session.
