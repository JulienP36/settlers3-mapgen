# Settlers III MapGen — Release validation

Date: 2026-08-19

## v1.5 — CANDIDATE

### Scope
La v1.5 est la consolidation moteur après la v1.4 UI. Elle implémente l'audit complet Legacy/Upgraded et les derniers recalibrages de ressources/starts.

Points principaux :
- Legacy et Upgraded partagent la macro-morphologie mais ont désormais des politiques hydrologie/biomes/ressources/objets explicitement séparées ;
- starts toujours placés très tôt et protégés ;
- neige commune `Rocky32 -> 35 -> 129 -> Snow128`, Terrain34 conservé comme variante Rocky interne/minéralisable ;
- Upgraded : petits plans d'eau 1–4 supprimés/redistribués, trimming rivière size-scaled, minerais ~90 % support, Swamp ~+30 %, Mud désactivé, reefs rares, decorative stones réduites ;
- **géométrie minière Upgraded v7 no-gap canonique** : petits blobs élémentaires pleins, compacts, légèrement ovoïdes, tailles lognormales ~18–105 cellules, variations modestes d'aspect/orientation, aucun trou/singleton/moat forcé, fusion naturelle autorisée ;
- arbres `68..77 + 80..81` communs, Palms `78..79` comptées comme bois ; Upgraded ~130 % volume natif + SmallTree84 séparé ;
- bonus Upgraded : forêt `41 adultes + 21 SmallTree84` et tas de pierre `8 ancres / 84 unités`, tous deux centrés sur la bordure du territoire initial (~HEX34) ;
- Building Stones globales variées au lieu d'un état uniforme ; Legacy distribution native-like, Upgraded biaisée vers les états pleins ;
- environ 20 Building Stone 13 / ID127 vides sur les 1683 ancres globales, conformément aux références natives 768 ;
- ID127 compte dans la densité d'ancres mais pas dans le stock exploitable ;
- **ID127 est constructible** : le footprint 7 cellules est libéré (`accessibility=0`) avant validation/export, contrairement aux états actifs `115..126` ;
- récifs Upgraded à au moins 2 cellules des bords ;
- GUI/CLI/exports nommés v1.5.

### Validators v1.5
La candidate doit passer au minimum :
- quotas arbres adultes / SmallTree84 / Palms ;
- quotas d'ancres Building Stones incluant `127` ;
- stock pierre calculé seulement sur `115..126` ;
- variété d'états `115..127` ;
- nombre d'ID127 ;
- ID127 uniquement sur Grass ;
- `STONE_EXHAUSTED_BUILDABLE` : aucune des 7 cellules d'un tas épuisé ne reste bloquante ;
- `REEF_EDGE_MARGIN` ;
- validations existantes starts, transitions, Water/Snow, minerais, poissons et décorations.

### Validations visuelles utilisateur obtenues
- **Bonus de départ Upgraded** : validés. La bordure du territoire initial traverse les clusters bonus ; volumes forêt/pierres jugés bons.
- **Répartition des états Building Stones `115..127`** : validée visuellement.
- **Géométrie minière v7 no-gap** : revalidée explicitement sur `S3_V1_5_V7NOGAP_CORRECTED_UPGRADED_4P_768x768_seed_2026082202`. L'utilisateur confirme que les formes correspondent exactement à la référence de long-play recherchée.
- L'ancienne candidate `S3_V1_5_FINALCANDIDATE_UPGRADED_4P_768x768_seed_2026082201` est **invalidée pour la forme des minerais** : bons volumes/ratios mais croissance de blobs incorrecte. Elle ne doit pas servir de référence.

### Validation externe encore requise avant promotion
Sur la candidate v7 corrigée :
1. ouverture éditeur sans erreur ;
2. starts tous valides ;
3. View Map / lancement sans crash ;
4. confirmation pratique que les ID127 n'empêchent pas la construction ;
5. contrôle général final en jeu.

Tant que ces derniers points ne sont pas confirmés, **v1.5 reste candidate et ne doit pas être taguée stable**.

## v1.3.2 — VALIDÉE

### Scope du patch
- Durcissement de la sélection des starts pour l'acceptation par l'éditeur officiel : halo Grass naturellement dégagé, marge Water accrue et exclusion stricte des objets statiques.
- Maintien de toutes les passes ultérieures d'objets/ressources hors du halo protégé, y compris le footprint complet des Building Stones.
- Neige intérieure `129/128` rendue non traversable via l'accessibility statique.
- Reconstruction systématique des transitions de marais `Grass16 -> 21 -> 81 -> 80`, y compris les mini-marais de départ.
- Validators HARD pour les marges de starts, l'accessibility Snow et les chaînes de transitions Desert/Swamp/Snow.

### Validation externe utilisateur
Quatre générations **Continental 768×768** ont été testées dans les outils officiels : Legacy 4P, Legacy 20P, Upgraded 4P et Upgraded 20P.

Résultats : starts acceptés par l'éditeur, aucun crash View Map/in-game, correction des marais confirmée et neige intérieure non traversable comme prévu.

Conclusion : **v1.3.2 validée** pour ce périmètre de contrôle.

## v1.4 — VALIDÉE

La v1.4 conserve le moteur/règles de génération validés de la v1.3.2 et ajoute les améliorations de visualisation et d'interface suivantes :

- thème sombre / clair et préférences persistantes ;
- overlays avec opacité réglable ;
- projection parallélogramme à décalage de 0,5 cellule par ligne ;
- drag et zoom améliorés ;
- barre de progression étendue ;
- palette joueurs unifiée ;
- marqueurs `P1` à `P20` nets, colorés et non déformés ;
- contour du territoire initial dérivé des SAV natifs : 3500 cellules, étendue ±35 cellules ;
- territoire initial rendu comme un vrai cercle dans la géométrie parallélogramme, avec déformation inverse en vue carrée ;
- listes déroulantes corrigées en mode sombre, ouvertes comme fermées ;
- sliders positionnables directement par clic sur leur barre.

### Validation utilisateur finale
Les deux derniers points restant à confirmer ont été contrôlés visuellement et validés :

- géométrie du cercle de territoire en vues parallélogramme et carrée : **OK** ;
- fond/texte des combobox fermées en thème sombre : **OK**.

Conclusion : **v1.4 sort du statut candidate et est considérée validée**.

## Correctif Goods Default — VALIDÉ

### Cause racine
Le writer MapGen écrivait par erreur `player_count - 1` dans le 3e DWORD du bloc Map Info. Ce DWORD correspond au réglage éditeur **Goods Default** :

- `1` = Low ;
- `2` = Medium ;
- `3` = High.

Sur une map 20 joueurs, l'ancienne écriture produisait donc `19`, valeur invalide : dans `Edit Map Settings`, aucun preset Low/Medium/High n'était sélectionné et le lancement avec `Défaut` pouvait provoquer une erreur/crash.

### Correctif
Le writer sérialise désormais explicitement :

- **Legacy → Medium (`2`)** ;
- **Upgraded → High (`3`)** ;
- fallback sûr → Medium pour un mode inconnu/importé.

Un test de non-régression verrouille le champ afin que le nombre de joueurs ne puisse plus être écrit comme Goods Default.

### Validation utilisateur
Deux générations **fraîches v1.4 4P** ont été testées :

- Legacy : `Edit Map Settings` affiche bien **Medium**, démarrage avec `Défaut` sans crash ;
- Upgraded : `Edit Map Settings` affiche bien **High**, démarrage avec `Défaut` sans crash.

Aucun message `You have lost` et aucun divide-by-zero sur ces deux contrôles.

Conclusion : **le crash Goods Default est corrigé et validé**.

## Morphologie Upgraded indépendante — PREMIÈRE CANDIDATE VALIDÉE

### Candidate
`S3_Continental_Upgraded_4P_768x768_seed_2026081908_archetype_library_v1`

Cette candidate est la première génération Upgraded évaluée après découplage de la macro-morphologie vis-à-vis de l'ancien checkpoint EDM exécutable. La géographie est fournie par la bibliothèque d'archétype puis les règles Upgraded sont appliquées par-dessus.

### Validation utilisateur
Contrôle dans l'éditeur et en jeu :

- géographie globale jugée **excellente** ;
- forme du continent / côtes / biomes / hydrologie : aucun défaut bloquant signalé ;
- starts : **OK** ;
- démarrage / vue in-game : **aucun crash** ;
- heightmap générale jugée correcte ; vérification statistique effectuée ensuite : le relief montagneux correspond à la référence native 768/4P source et reste dans l'enveloppe des trois références 768.

Conclusion : **la première morphologie Upgraded indépendante est validée comme base de généralisation**.
