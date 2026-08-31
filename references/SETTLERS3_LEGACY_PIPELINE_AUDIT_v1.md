# Settlers III — audit du pipeline Legacy v2.0 DEV_1_R6

> **Point 4 de la roadmap v2.0 — audit des règles, de l'occupation et de l'ordre**
>
> Audit réalisé le **30 août 2026** à partir du code R6, des références
> natives versionnées et de deux générations de contrôle 768×768. Ce document
> ne prétend pas déduire l'algorithme interne du jeu : il sépare ce qui est
> observé, calibré, reconstruit par approximation et encore inconnu.

## Conclusion opérationnelle

R6 est désormais un socle techniquement sûr pour poursuivre le travail : les
deux générations de contrôle ont produit **19/19 validations** et aucune
transition Eau→Herbe ou Eau→terrain sans rive. La règle de transition est donc
correctement protégée.

En revanche, R6 n'est pas encore une reproduction native fidèle sur quatre
points importants :

1. la **Shore48** est environ deux fois moins abondante que dans les SAV de
   référence, malgré une proportion d'eau globale correcte ;
2. les quotas et la géométrie des **ressources Legacy** sont encore ceux d'un
   ancien profil : trop de cellules minéralisées, pas assez de poissons,
   supports incomplets et blobs trop éloignés de la distribution native ;
3. les **objets décoratifs sont encore un no-op**, ce qui empêche de reproduire
   la densité et la proximité natives autour des départs ;
4. la sélection des départs et la protection des terrains sont cohérentes avec
   l'architecture start-first validée dans le projet, mais leur ordre exact dans
   le générateur natif reste non démontré.

La décision pour la suite est donc : **ne pas déplacer les starts à la fin et
ne pas relâcher les transitions**. Corriger d'abord les couches mesurées
ci-dessus dans une passe Legacy dédiée, après extension du corpus aux autres
tailles si nécessaire. Le mode Custom reste différé.

## Légende des niveaux de preuve

| Niveau | Signification |
|---|---|
| **Natif** | Règle directement observée dans les SAV ou validée explicitement dans le jeu/éditeur. |
| **Calibré** | Paramètre choisi pour reproduire une mesure native, sans preuve que le mécanisme interne soit identique. |
| **Approximé** | Reconstruction procédurale plausible : forme, bruit, sélection ou routage ne sont pas démontrés comme ceux du jeu. |
| **Inconnu** | La donnée finale ne permet pas de conclure, ou la sémantique n'est pas décodée. |

## 1. Périmètre et reproductibilité

### Corpus natif

- 16 SAV 768×768 : 8 cartes à 2 joueurs et 8 cartes à 20 joueurs ;
- checksums valides : **16/16** ;
- 176 départs décodés dans les blocs joueurs type 6 ;
- transitions et distances calculées avec HEX6 :
  `(+1,0), (-1,0), (0,+1), (0,-1), (+1,+1), (-1,-1)` ;
- terrain runtime `28` conservé comme état de démarrage et normalisé en
  `Grass16` uniquement pour les comparaisons statiques ;
- champ byte 14 séparé du byte 7 runtime pour les objets ; byte 9 toujours
  inconnu.

Sources principales :

- `references/native_terrain_audit/` ;
- `references/native_resource_object_audit/` ;
- `SETTLERS3_NATIVE_GENERATOR_REFERENCE_v2.md` ;
- `SETTLERS3_NATIVE_TERRAIN_TRANSITIONS_21_v2.md` ;
- `SETTLERS3_NATIVE_HEIGHTMAP_REFERENCE_21_v3.md` ;
- `SETTLERS3_NATIVE_RESOURCES_OBJECT_PROXIMITY_REFERENCE_v1.md`.

### Contrôles R6

Les contrôles ont utilisé le générateur procédural directement, sans SAV,
PNG, cache ou carte de référence à l'exécution :

| Contrôle | Seed | Temps | Validations | Eau | Objets | Minerais | Poissons |
|---|---:|---:|---:|---:|---:|---:|---:|
| Legacy 2P | `2026083001` | 13,3 s | 19/19 | 119 315 cellules (20,229 %) | 4 427 | 56 584 | 32 313 |
| Legacy 20P | `2026083002` | 15,4 s | 19/19 | 119 325 cellules (20,231 %) | 4 427 | 56 584 | 32 313 |

Le code analysé est au commit de base `a21514fa5305db37455d0fd6a0240cfecb99480f`
avec l'arbre de travail R6. Les hashes des modules directement audités sont
conservés dans le journal de travail et peuvent être régénérés par
`sha256sum`.

## 2. Ordre réel du pipeline R6

Le fichier exécutable est
`s3mapgen/generation/generators/legacy/pipeline.py`.

| Étape | Appel R6 réel | Ce que l'étape écrit/protège | Niveau |
|---:|---|---|---|
| 1 | `macro` | continent principal connecté, satellites, eau extérieure et première rive | Calibré + approximé |
| 2 | `starts` | positions maximin, footprint exact de 33 cellules, réservation technique | Natif pour le footprint ; approximé pour le choix |
| 3 | `mountains` | masque montagne complet puis IDs `17/33/32` | Natif pour la chaîne ; calibré/approximé pour les formes |
| 4 | `relief` | hauteur côtière et hauteur des massifs | Calibré statistiquement |
| 5 | `snow` | neige issue de la hauteur/profondeur, chaîne `32→35→129→128` | Natif pour la logique ; calibré/approximé pour le seuil |
| 6 | `lakes` | lacs intérieurs, reconstruction eau/rive/profondeur | Natif pour les garde-fous ; approximé pour les formes |
| 7 | `coastal_bands` | variation locale des IDs Water0..7, sans modifier Shore48 | Calibré sur 16 SAV ; garde-fou natif |
| 8 | `rivers` | chemins herbe-only vers une embouchure Shore/eau | Natif pour connexion/séparation ; approximé pour le tracé |
| 9 | `swamps` | masque `21/81/80` sur herbe disponible | Natif pour la chaîne ; calibré/approximé pour les quotas |
| 10 | `surface` | désert `20/65/64` sur herbe disponible | Natif pour la chaîne ; calibré/approximé pour les quotas |
| 11 | `trees` | arbres adultes et palmiers | Profil historique, non encore validé Legacy exhaustif |
| 12 | `stones` | ancres Building Stones et empreinte 7 cellules | Natif pour l'empreinte ; profil/occupation à confirmer |
| 13 | `decorations` | actuellement aucun objet | Incomplet |
| 14 | `minerals` | minerais sur un sous-ensemble de supports montagneux | Approximation actuellement divergente |
| 15 | `fish` | sélection uniforme dans la bande d'eau proche de Shore | Approximation actuellement divergente |
| 16 | `accessibility` | accessibilité technique finale | Partiel ; byte 9 SAV inconnu |
| 17 | `validate` | 19 contrôles structurels finaux | Garde-fou projet |

### Résolution des ordres concurrents

Les références de travail contiennent deux descriptions historiques :

- le pipeline start-first du projet (`PREGEN_READ_FIRST.md`, section E et
  checkpoint 384 validé) : macro → starts → terrains/hydrologie → objets ;
- l'ancienne section « current generation order » du master v15, qui place les
  starts à la fin après les ressources et les objets.

La priorité de résolution est celle du fichier `PREGEN_READ_FIRST.md` : la
validation utilisateur du jalon 384 impose de garder les starts tôt afin de
préserver les positions et l'équilibre des zones disponibles. L'analyse native
montre que le résultat final ressemble davantage à une sélection sur géographie
terminée, mais **un SAV final ne prouve pas l'ordre interne**. Il serait donc
incorrect de remplacer l'architecture start-first par l'ordre tardif sur cette
seule inférence.

Décision R6 conservée :

- starts tôt ;
- footprint exact protégé ;
- pas de disque de terrain visible autour du start ;
- terrains et objets ne doivent jamais produire de transition illégale.

### Écart documentaire à corriger

`generation/rules.py` expose encore les anciens noms de stages
(`hydrology.micro_water_cleanup`, `snow.summit_rebuild`,
`resources.minerals_v7_nogap`, etc.), alors que le moteur journalise
`continental_v2.macro` jusqu'à `continental_v2.validate`. Cette divergence ne
change pas la carte, mais rend le diagnostic et les comparaisons de stages
ambigus. Elle doit être corrigée séparément avant d'ajouter de nouveaux
paramètres Custom.

## 3. Audit des transitions et de l'occupation

| Famille | Règle native mesurée | Implémentation R6 | Résultat du contrôle |
|---|---|---|---|
| Eau | `Shore48 ↔ Water0 ↔ 1 … 7`, bord profond | distance HEX6, reconstruction après lacs, bord `Water7` | PASS ; aucun contact Eau→Herbe direct |
| Montagne | `Grass16 ↔ 17 ↔ 33 ↔ Rocky32` | masque complet, profondeur HEX6, peinture extérieur→intérieur | PASS ; aucun contact illégal |
| Neige | `Rocky32 ↔ 35 ↔ 129 ↔ Snow128`, uniquement dans le massif | masque de neige issu de hauteur/profondeur | PASS ; accès et transitions contrôlés |
| Désert | `Grass16 ↔ 20 ↔ 65 ↔ Desert64` | masque herbe-only, profondeur HEX6 | PASS |
| Marais | `Grass16 ↔ 21 ↔ 81 ↔ Swamp80` | masque herbe-only, profondeur HEX6 | PASS |
| Rivières | HEX6, reliées à Shore/eau, sans traverser les familles incompatibles | champ de distance d'embouchure + routage borné | PASS ; aucun composant orphelin |
| Shore | uniquement sur une vraie rive, pas de singleton | produite par géométrie eau/terre, conservée par la bathymétrie | PASS structurel ; quantité insuffisante |
| Départs | footprint natif 33 cellules, herbe au moment de l'export généré | `_footprint_ok`, réservation exacte et revalidation finale | PASS ; `28` reste un effet runtime SAV, non généré |
| Objets | empreintes et hitboxes non entièrement démontrées | arbres/pierres à `dilate(reservation, 3)`, pierres avec footprint 7 | techniquement borné, fidélité native inconnue |

Le point essentiel demandé dans le projet est respecté : **l'eau ne touche pas
directement l'herbe**. La bathymétrie R6 ne supprime pas de Shore48 et ne crée
pas de correction graphique a posteriori. Si la rive paraît trop mince, le
problème est en amont — géométrie de la bordure ou masque Shore — et non une
raison de relâcher le validateur.

## 4. Comparaison quantitative R6 / Legacy natif 768

Les valeurs natives ci-dessous sont les moyennes de la tranche 16 SAV, sauf
mention contraire. Les contrôles R6 sont deux seeds isolées : ils servent à
détecter les écarts de mécanisme, pas à remplacer les distributions natives.

| Mesure | Natif 2P | R6 2P | Natif 20P | R6 20P | Lecture |
|---|---:|---:|---:|---:|---|
| Eau, % carte | 20,22 % | 20,229 % | 20,22 % | 20,231 % | Très bon calibrage global |
| Eau intérieure, cellules | 12 953 | 12 687 | 13 250 | 12 687 | Ordre de grandeur correct |
| Shore48, cellules | 20 892 | 10 149 | 21 188 | 9 698 | **Sous-production forte** |
| Famille montagne, cellules | 83 030 | 86 269 | 83 456 | 87 594 | Légèrement trop forte, surtout 20P |
| Famille neige, cellules | 14 029 | 12 717 | 14 060 | 8 897 | Seuil/relief trop variable, 20P trop bas |
| Famille désert, cellules | 21 757 | 14 363 | 20 119 | 14 309 | **Quota trop bas** |
| Famille marais, cellules | 2 113 | 1 689 | 2 308 | 1 686 | Bas, mais plus proche |
| Rivières, cellules | 9 689 | 5 228 | 9 751 | 5 387 | **Routage n'atteint pas la cible** |
| Objets statiques, densité /1000 cellules de carte | 9,70 | 7,50 | 9,79 | 7,50 | Décor manquant ; comparaison prudente |

La valeur `macro_water` R6 est correcte, mais elle ne garantit pas la bonne
forme de la rive. Dans R6, `coastal_bands` vérifie volontairement que le nombre
de cellules Shore48 ne change pas ; la différence native doit donc être traitée
dans la production de la bordure et des lacs, pas dans la passe Water0..7.

## 5. Écarts Legacy de ressources et d'objets

### Minerais

La référence native donne environ **39 937 cellules** par carte en 2P et
**39 936** en 20P, avec une quantité moyenne proche de 8 et une distribution
de familles `Coal/Iron/Gold/Gems/Sulfur = 50,19/21,56/14,42/5,45/8,39 %`.

R6 produit 56 584 cellules, soit environ 41 % de plus que la médiane native.
En outre, `resources.py` autorise actuellement seulement
`ROCKY32, ROCK_SNOW_TRANS35, SNOW_TRANS129, SNOW128`, alors que les SAV montrent
des ressources sur le support complet `17,32,33,34,35,128,129`. Les cellules
`17/33/34` sont donc aujourd'hui exclues à tort.

Le contrôle R6 montre aussi déjà le mauvais couplage avec les départs : des
cellules minéralisées apparaissent dans `r≤25` (jusqu'à la distance 5 dans la
carte 20P de contrôle), alors que les 16 SAV natifs n'en contiennent aucune dans
ce rayon. Ce n'est pas une raison pour ajouter un grand halo de terrain : il
faut distinguer la réservation du start, la sélection des supports et le
placement économique final.

La géométrie diverge aussi : le code utilise des blobs `_blob` de tailles tirées
autour d'un quota par famille et retire chaque cellule de `available`. La
référence native mesure environ 481–506 composantes minérales agrégées, une
médiane de composante de 3 cellules, un p90 autour de 148–158 et une longue
queue de gros ensembles. La simple liste de quotas R6 (`500+240+165+75+100`)
ne constitue pas cette distribution native.

**Classement :** supports natifs connus mais implémentation actuelle
approximée et quantitativement divergente.

### Poissons

Les SAV donnent une médiane de **46 071 cellules** en 2P et **43 737** en 20P.
R6 force 32 313 cellules dans les deux groupes. R6 respecte bien l'exclusion
des rivières et la bande `distance Shore 1..12`, mais choisit uniformément dans
cette bande. La référence master demande une probabilité décroissante par
tranches `1–3 / 4–6 / 7–9 / 10–12 = 68 / 55 / 40 / 24 %`.

**Classement :** garde-fou de support correct, densité et distribution de
distance approximées et encore divergentes.

Dans la carte 20P de contrôle, des poissons apparaissent aussi dans plusieurs
rayons `r≤25`, avec une distance minimale observée de 12. Les SAV natifs de la
tranche ne montrent aucun poisson ni minerai dans `r≤25`. Le futur placement
doit donc appliquer cette contrainte économique sans la confondre avec une
zone de terrain artificiellement vide.

### Objets proches des starts

La référence native ne montre pas de halo vide fixe de 14 hexagones : les
petits décors peuvent être très proches, et quelques arbres/pierres aussi.
Les mesures statiques donnent environ 10,5 cellules dans `r≤14` en 2P et 9,5
en 20P, avec des objets dans l'empreinte nominale de 33 cellules sur certains
départs.

R6 interdit actuellement arbres et Building Stones dans
`dilate(reservation, 3)` et ne pose aucune décoration. Cette protection reste
utile pour les hitboxes non décodées, mais elle ne reproduit pas la densité
locale native. Elle devra être différenciée par type d'objet après calibration
éditeur/jeu ; le byte 9 ne peut pas servir de preuve de collision.

**Classement :** footprint Building Stone natif connu ; clearance d'objet et
répartition décorative inconnues/approximées.

## 6. Matrice de décision par règle

| Règle à préserver ou réviser | Classe | Décision pour la prochaine passe |
|---|---|---|
| HEX6 pour voisinage, composantes, profondeur et rivières | Natif | Préserver sans exception |
| Chaînes de transitions | Natif | Préserver et maintenir les validateurs durs |
| Eau→Shore→Water, bord Water7 | Natif | Préserver ; corriger la quantité Shore en amont |
| Eau globale 768 ≈20,22 % | Calibré | Préserver comme cible de distribution, pas comme constante universelle |
| Marge océanique absolue ≈40 cellules | Natif mesuré / mécanisme approximé | Recontrôler la marge réelle, ne pas confondre avec `macro_margin=24..29` |
| Continent connecté + silhouettes NPZ dérivées | Calibré | Préserver pour R6 ; l'algorithme natif reste inconnu |
| Starts tôt | Validé projet | Préserver ; ne pas appliquer l'ordre tardif ancien |
| Footprint start 33 cellules | Natif/validé | Préserver ; ne pas générer terrain28 |
| Absence de grand halo de terrain visible | Validé projet + natif compatible | Préserver, mais mesurer un buffer de terrain statistique léger si nécessaire |
| Montagnes 17,71 % de terre environ | Calibré | Recalibrer le dénominateur et la variance avant modification |
| Relief par distance à l'eau/profondeur de massif | Calibré | Comparer pentes et amplitudes multi-échelle, pas seulement la hauteur moyenne |
| Lacs sans micro-composants 1–4 | Natif | Préserver ; revoir seulement la distribution des grandes formes |
| Rivières connectées et largeur 1 dominante | Natif | Préserver ; augmenter/réorganiser le routage pour atteindre la densité native |
| Désert/marais | Natif pour transitions, calibré pour quotas | Revoir les cibles sur la terre finale et la distribution de composants |
| Minerais Legacy | Natif pour familles/supports/quantités, code actuel divergent | Séparer le profil Legacy du profil Upgraded et remplacer les cibles actuelles |
| Poissons Legacy | Natif pour support/exclusion rivière, code actuel divergent | Recalibrer le nombre et appliquer une densité décroissante par distance |
| Arbres/pierres/décorations | Partiel | Implémenter le décor après les supports et mesurer les clearances par famille |
| Byte9 SAV = hitbox/accessibilité | Inconnu | Ne jamais l'utiliser comme règle |
| Ordre interne exact du jeu | Inconnu | Tester par signatures finales ; ne pas l'affirmer à partir d'un SAV |
| Graine, bruit et transform exacts du jeu | Inconnu | Hors périmètre actuel |

## 7. Ordre recommandé pour le point 5/6

Sans changer les garde-fous, la prochaine amélioration Legacy doit être
séquencée ainsi :

1. **corriger la métrique Shore** à la source de la géométrie eau/terre et
   vérifier les profondeurs Water0..7 après l'ajustement ;
2. **recaler les masques de terrain** sur les dénominateurs natifs : désert,
   marais, neige et rivières, en gardant les chaînes légales ;
3. **remplacer le bloc Legacy ressources** par les supports et distributions
   mesurés, sans importer la règle Upgraded `v7 no-gap` ;
4. **ajouter les décorations et distinguer les clearances** petits décors,
   arbres et pierres, avec validation dans l'éditeur/jeu ;
5. seulement ensuite comparer des PNG déterministes et reprendre les contours
   macro/côtes si les statistiques restent compatibles ;
6. exposer le générateur Custom quand ces règles Legacy sont stables et que ses
   paramètres peuvent être reliés à des règles de transition sûres.

## 8. Limites et prochaines preuves nécessaires

- étendre les mesures aux six autres tailles natives avant de figer un profil
  multi-size ;
- faire une campagne contrôlée dans l'éditeur/jeu pour les hitboxes d'objets et
  la survie des starts après construction ;
- ajouter un validateur intermédiaire « terrains finis » avant les objets,
  sans supprimer le validateur final ;
- synchroniser les noms de `PIPELINE_STAGES` avec les stages effectivement
  journalisés ;
- ne pas appeler « native » une valeur seulement ajustée sur deux seeds R6.

Ce document clôt l'audit du **point 4**. Il ne clôt ni l'amélioration Legacy,
ni la validation Windows/éditeur/jeu, ni le mode Custom.
