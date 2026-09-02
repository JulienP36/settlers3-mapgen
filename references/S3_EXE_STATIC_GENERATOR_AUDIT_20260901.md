# Settlers III — audit statique du générateur natif

Date : 2026-09-01
Artefact analysé : `S3.EXE` (PE32 i386, 3 842 048 octets)
SHA-256 : `25a6de6703ea3f9d88537aa309192ff0399b81f8a1221f40a222f36dc6be37a6`

## Statuts

- **CONFIRMED** : démontré directement par les instructions désassemblées.
- **STRONG** : conclusion technique très étayée, mais nom fonctionnel à confirmer.
- **PARTIAL** : mécanisme délimité, sémantique incomplète.
- **TODO** : information à relier à des données visuelles ou à une autre routine.

## Portée

Analyse exclusivement statique et en lecture. Le binaire original n'est ni exécuté ni modifié. Ce document ne déduit aucune modification à appliquer à `s3mapgen` : seule une correspondance démontrée avec le binaire ou des SAV pourra le justifier.

Pour cette phase, l'objectif prioritaire est de reconstituer l'algorithme natif qui produit le champ terrain principal : relief, classification, eau, rivières, rives et pinceaux de surfaces. Les variantes graphiques, le rendu, les secteurs et les couches auxiliaires sont conservés comme contexte, mais ne constituent pas les objectifs courants de l'audit.

### Conclusion de portage

Pour les dimensions qui respectent le contrat de parcours natif (blocs de raffinement se terminant sur la dimension active, ce qui correspond aux tailles de cartes normalement utilisées par le jeu), le chemin qui produit le relief et le terrain principal est maintenant entièrement relié : chaque écriture de ces deux champs dans le chemin central est attribuée à l'initialisation, à la sculpture, à la classification, aux rivières, aux transitions, aux quatre familles, aux micro-pinceaux ou aux copies finales de mode. Il reste à valider l'égalité de sortie sur des cartes/SAV de référence ; il ne reste pas de branche inconnue à inventer dans ce contrat de terrain. Les points encore `PARTIAL` ci-dessous concernent soit le nom métier d'un mécanisme déjà décodé, soit les métadonnées secondaires, soit un cas de dimension non standard.

### Vérification de complétude des écritures de terrain

Le contrôle croisé du chemin central (`0x5166D0–0x518D05`) donne le ledger suivant :

| Écriture/effet | Emplacement ou routine native | Inclus dans la reconstruction |
|---|---|---|
| terrain initial `0x00`, marqueur initial `0x1F` | boucle d'initialisation autour de `0x516789` | oui |
| marqueurs temporaires `0x70`/`0xF0` | sculpture `0x516CDE–0x5172C0` | oui |
| relief issu de ces marqueurs | consommation autour de `0x5172C1` | oui |
| classification eau/herbe/roche/neige | `0x5175B7–0x51761E` | oui |
| codes rivière et conversion de chaîne | `0x517699–0x517E62` | oui |
| rives, profondeurs d'eau, transitions roche/neige | appels `0x519210`/`0x519270` | oui |
| désert, marais, boue, herbe sèche et micro-pinceaux | appels `0x51AED0`, `0x519440`, `0x519470` | oui |
| réécritures finales de relief/terrain selon le mode | copies `0x518A8F–0x518BBC` | oui |

Les routines centrales de variantes et objets (`0x51B010`, `0x51B1A0` et
associées), de ressources (`0x51AD40`) et de composantes (`0x51A580`) ont été
contrôlées séparément : elles n'écrivent aucune nouvelle valeur dans le champ
terrain principal, mais `0x51B010/0x51B1A0` écrivent directement le décor dans
`+0x6744B` et `0x51AD40` écrit les ressources dans `+0x67455`. Elles relèvent
donc de l'audit non-terrain, pas d'une omission du noyau terrain.

## 1. Point d'entrée du monde aléatoire

### CONFIRMED — routine centrale

- La routine de construction du monde est à `0x5166D0`, jusqu'au retour `ret 0x0C` à `0x518D05` : elle accepte trois arguments explicites.
- Son unique appel direct est à `0x53CE35`, dans l'initialisation logique du jeu.
- La chaîne de texte voisine est `Erstelle Zufallswelt %i %i %i` (« créer un monde aléatoire »).
- La routine initialise une grille, construit le relief, classe les surfaces,
  pose des variantes/détails et objets statiques, prépare les bords, finalise
  les transitions, puis pose les ressources de sol et les poissons.

### CONFIRMED — paramètres observables

L'appelant lit trois champs de l'enregistrement de configuration : `+0x14`, `+0x08`, `+0x10`, et les pousse dans cet ordre d'appel : `+0x10`, puis `+0x08`, puis `+0x14`.

| Argument de `0x5166D0` | Champ appelant | Usage démontré dans `0x5166D0` | Statut sémantique |
|---:|---|---|---|
| 1 | `+0x10` | aucune lecture observée dans la routine centrale | argument transmis mais non consommé par ce chemin |
| 2 | `+0x08` | mémorisé dans `world + 0x2D274` | masque de mode qui affecte le relief et la topologie, nom exact inconnu |
| 3 | `+0x14` (lu sur 16 bits à l'appel) | initialise le PRNG interne et est mémorisé comme taille active dans `world + 0x2D2D0` | valeur utilisée à la fois comme graine native et dimension de carte |

**Important :** après `sub esp,0x98` et les quatre sauvegardes de registres, `0x5166F0` lit le premier argument de la routine à `[esp+0xB0]`, c'est-à-dire le champ appelant `+0x14`, puis le donne à `0x4FEB40` et le recopie comme dimension à `0x516730`. Le champ appelant `+0x08` arrive en deuxième argument et est recopié dans `world + 0x2D274`. Le troisième argument, issu de `+0x10`, n'est pas relu dans le chemin central observé.

## 2. Modèle mémoire de la carte

### CONFIRMED — grille et dimensions

- Taille maximale adressée : `768 × 768`.
- Une cellule occupe **24 octets** (`0x18`).
- Un déplacement d'une ligne vaut `0x4800`, soit `768 × 24`.
- Les calculs d'adresse utilisent une zone préallouée pour le maximum 768, même pour une carte plus petite.

### CONFIRMED — voisinage hexagonal

Les fonctions de propagation consultent systématiquement les six positions suivantes autour d'une cellule :

- même colonne, ligne précédente et suivante ;
- même ligne, colonne précédente et suivante ;
- une diagonale dans chaque sens opposé.

Les décalages mémoire correspondants sont `±0x4800`, `±0x18`, `+0x4818` et `-0x4818` sur le champ considéré. C'est un voisinage de six directions, pas un voisinage carré à quatre ou huit directions.

### STRONG — champs par cellule

| Décalage relatif | Usage démontré | Interprétation prudente |
|---|---|---|
| `+0x00` | bruit et comparaisons de relief, valeurs bornées sur un octet | hauteur/relief interne |
| `+0x01` | marqueurs directionnels/temporaires de traçage | état de passage temporaire |
| `+0x02` | écrit par les pinceaux ; testé par familles via le demi-octet haut | **ID de terrain principal** (octet terrain EDM/MAP) |
| `+0x03` | écrit par les passes de variantes ; recopié vers une sortie 16 bits finale | variante graphique/topologique interne, pas l'ID EDM |
| `+0x06` | bits de protection/occupation utilisés par les poses | drapeaux de cellule |
| `+0x0D` | détails aléatoires, parfois remplis par un nibble | détail/variation visuelle |

Les noms proposés dans la troisième colonne restent descriptifs : ils ne remplacent pas les noms originaux inconnus.

## 3. PRNG interne

### CONFIRMED — état et initialisation

Le PRNG est initialisé par `0x4FEB40` dans trois mots de 16 bits :

```text
A = input mod 65536
B = (input + 1000) mod 65536
C = (input + 2000) mod 65536
```

### CONFIRMED — une itération (`0x4FEB70`)

La routine retourne un mot de 16 bits et met à jour les trois états. Pseudocode comportemental :

```text
u  = (B + A) mod 65536
A' = u XOR C
C' = (C + B) mod 65536
B' = ror16(B XOR C', 1)
C''= ror16(C', 1)
return A'
```

Il s'agit donc d'un petit générateur déterministe à états 16 bits, combinant addition, XOR et rotation ; ce n'est pas un LCG simple.

## 4. Ordre de pipeline démontré

### CONFIRMED — séquence générale

| Plage d'adresses | Passe observée | Ce que le code prouve |
|---|---|---|
| `0x5166D0–0x5167E5` | initialisation | remise à zéro/valeurs sentinelles de tous les champs de grille |
| `0x5167E6–0x5168D8` | bruit grossier | valeurs aléatoires posées sur une maille espacée de 64 cellules |
| `0x5168D9–0x516B7D` | raffinement | interpolation/perturbation répétée à pas décroissant (`32`, puis moitiés) |
| `0x516CDE–0x5172C0` | sculpture locale du relief | sélection de points, courts tracés de contraintes et marqueurs temporaires `0x70`/`0xF0` |
| `0x5172C1–0x5175B6` | lissage conditionné par le mode | bornage local des écarts de relief ; seuil 5 visible dans une branche |
| `0x5175B7–0x51761E` | classification initiale | conversion du relief en eau (`0x00`), herbe (`0x10`), roche (`0x20`) et neige (`0x80`) |
| `0x517699–0x517E62` | tracés locaux | marche basée sur les six voisins et le relief ; marqueurs `0x60–0x63` |
| `0x517E63–0x5182A8` | surfaces secondaires | pinceaux, expansions, lissages et conversions ordonnés de familles |
| `0x5182BF–0x5189CF` | variantes/patterns et objets statiques | génération d'IDs/motifs et décor direct dans `+0x6744B` |
| `0x5189D4–0x518A03` | ressources de sol initiales | cinq appels `0x51AD40`, minerais `0x10..0x50` |
| `0x518A08–0x518A70` | poissons sur l'eau | écriture du low nibble de `+0x67455` |
| `0x518A70–0x518D05` | copie/reset et finalisation | copies terrain/relief et champs selon masque |

### STRONG — conclusion sur les « chunks »

La maille initiale de 64 cellules est réelle. Elle sert de support à un bruit multi-résolution, raffiné sur toute la carte. Les passes suivantes restent des balayages globaux avec règles de voisinage. Aucune structure statique de sous-régions hexagonales indépendantes n'a été observée à ce stade.

Cette maille peut expliquer visuellement une impression de découpage, mais elle n'est pas une preuve de chunks de gameplay ou de conflits résolus par parcelles.

### CONFIRMED — sculpture locale pré-classification

Lorsque le masque de mode est nul, la routine `0x516CDE–0x5172C0` exécute `floor(taille² / 16)` tentatives pour une taille positive :

1. elle choisit un point intérieur aléatoire ;
2. elle exige une hauteur comprise entre `31` et `99`, ainsi qu'un écart local minimal ;
3. elle refuse les zones déjà marquées à proximité ;
4. elle parcourt localement les six directions en comparant les différences de hauteur au seuil `5` ;
5. elle pose des marqueurs temporaires `0x70` et `0xF0` dans le champ terrain ;
6. juste après, elle les consomme pour modifier la hauteur : `0x70` ajoute `8`, `0xF0` retire `8` puis devient `0x70`.

Cette passe intervient avant tout terrain visible. Elle façonne donc le relief qui déterminera ensuite eau, herbe, roche et neige. Le nom métier de cette sculpture (micro-crêtes, érosion ou autre) reste inconnu, mais son effet numérique, son ordre et toutes ses branches sont confirmés.

La sélection initiale est bornée par des formules précises :

```text
ligne = 1 + trunc((PRNG16 × taille − 2) / 65536)
colonne = 1 + floor(PRNG16 × (taille − 3) / 65536)
```

La hauteur du candidat doit être strictement supérieure à `30`, strictement inférieure à `100`, et satisfaire le test local strict `hauteur_courante − 10 > hauteur_voisine`. Le couple initial reçoit ensuite `0x70` sur le champ terrain de la cellule et `0xF0` sur la cellule décalée de `+0x18`. Un automate à quatre états (`4`, `3`, `2`, `1`) examine alors les directions et positions voisines ; son compteur de reprise permet au maximum deux passages pour le même candidat. La formule de ligne utilise bien la division signée native (troncature vers zéro après le `−2`) ; ce détail n'est pas interchangeable avec une simple multiplication entière suivie d'un plancher.

La garde située à `0x516CAE` teste le masque de mode juste après le raffinement. Si ce masque est non nul, le flot saute directement à `0x51749B` : les `floor(taille² / 16)` tentatives de sculpture ne sont alors pas exécutées. Le générateur passe par une branche de relaxation alternative avant la classification. Le masque de mode n'est donc pas seulement un paramètre de finalisation des bords ; il modifie aussi la construction du relief.

La garde de proximité `0x519960` rejette une tentative si l'une des dix positions de travail suivantes contient déjà `0x70` : `0`, `+0x4800`, `-0x4800`, `+0x18`, `-0x18`, `+0x4818`, `-0x4818`, `+0x30`, `-0x47E8` et `+0x4830`, mesurées depuis le champ terrain de la cellule candidate (`+0x6744A`). Elle ne traite pas `0xF0` comme un conflit dans ce test.

La routine `0x5198D0`, appelée par les branches internes de l'automate, est différente de cette garde de proximité. Elle reçoit une coordonnée et compte les six terrains voisins de la cellule indiquée (`S`, `SE`, `E`, `N`, `NW`, `W`) dont le marqueur vaut `0x70` **ou** `0xF0`. Elle renvoie vrai si ce compte est inférieur ou égal à `2`. Elle ne teste pas le centre lui-même. Ce filtre de densité de marqueurs explique pourquoi certaines branches de l'automate peuvent poursuivre une sculpture locale alors que d'autres s'arrêtent.

### CONFIRMED — branches exactes de l'automate

Le désassemblage permet de relier chaque état à ses lectures, ses écritures et ses déplacements. Seul le nom géométrique ou métier des quatre états reste inconnu. Les hauteurs ci-dessous sont celles des coordonnées locales `(x,y)` conservées par le code ; elles sont volontairement données sous cette forme pour ne pas imposer une convention graphique étrangère au binaire.

| Passage | État | Test de pente et écriture | Déplacement/état suivant |
|---:|---|---|---|
| `0` | `4` | si `H(x−1,y−1)−H(x−1,y)>5`, garde sur `(x−1,y−1)`, écrit `0x70` en `(x−1,y−1)` | `(x,y)←(x−1,y−1)`, état `3` |
| `0` | `3` | pose `0xF0` en `(x−1,y)` si `H(x,y)−H(x−1,y)` est la pente retenue ; sinon pose `0x70` au même endroit si `H(x−1,y)−H(x,y+1)>5` | branche `0xF0`: état `4`; branche `0x70`: `x←x−1`, état `2` |
| `0` | `2` | pose `0xF0` en `(x−1,y)` si `H(x,y)−H(x,y+1)` est la pente retenue ; sinon pose `0x70` au même endroit si `H(x,y+1)−H(x+1,y)>5` | branche `0xF0`: état `4`; branche `0x70`: `x←x−1`, état `2` |
| `0` | `1` | si `H(x,y)−H(x+1,y)>5`, garde sur `(x+1,y+1)`, écrit `0xF0` en `(x+1,y+1)` | état `2` |
| `1` | `4` | si `H(x,y)−H(x,y+1)>5`, garde sur `(x,y+1)`, écrit `0xF0` en `(x,y+1)` | état `3` |
| `1` | `3` | pose `0xF0` en `(x+1,y)` si `H(x,y)−H(x+1,y)` est la pente retenue ; sinon pose `0x70` en `(x+1,y+1)` si `H(x+1,y)−H(x,y+1)>5` | branche `0xF0`: état `2`; branche `0x70`: `(x,y)←(x+1,y+1)`, état `4` |
| `1` | `2` | pose `0xF0` en `(x+1,y)` si `H(x,y)−H(x,y+1)` est la pente retenue ; sinon pose `0x70` au même endroit si `H(x,y+1)−H(x+1,y)>5` | branche `0xF0`: état `1`; branche `0x70`: `x←x+1`, état `3` |
| `1` | `1` | si `H(x,y−1)−H(x−1,y)>5`, garde sur `(x,y−1)`, écrit `0x70` en `(x,y−1)` | `y←y−1`, état `2` |

Dans chaque ligne, l'écriture est précédée par la garde de densité `0x5198D0` lorsque le bloc natif l'appelle ; une comparaison `d2<=d1` choisit le premier cas, et l'égalité va donc toujours dans cette première branche. Si la pente retenue n'est pas strictement supérieure à `5`, la tentative échoue. Après chaque branche, le code relit la hauteur de la cellule courante ; il recommence avec le point et l'état initiaux au plus une fois, puis abandonne. Il n'y a aucun tirage PRNG dans cet automate.

Le rôle de `0x70` contre `0xF0` ne peut pas être inversé : la passe de consommation ultérieure ajoute `8` pour `0x70`, tandis qu'elle convertit `0xF0` en `0x70` et soustrait `8` modulo octet. Le nom métier de la sculpture reste le seul élément sémantique non nommé, pas une branche algorithmique manquante.

### CONFIRMED — relaxation du relief

Après la sculpture locale, le générateur exécute des balayages complets répétés jusqu'à stabilisation. Les écritures sont en place : une correction faite sur une cellule est visible par les cellules suivantes du même balayage.

En mode nul, pour `col=2..taille−1` puis `row=1..taille−2`, il pose `L=H(row,col−1)`, `low=L−7`, `high=L+5`, puis :

1. borne `H(row,col)` à `high` si elle est supérieure ;
2. si les quatre terrains `(row,col−1)`, `(row,col)`, `(row−1,col−1)`, `(row+1,col)` valent tous `0x70`, remonte `H(row,col−1)` à `H(row,col)+23` si la cellule courante est sous `low−16` ; sinon, si elle est sous `low`, remonte à `H(row,col)+7` ;
3. borne `H(row+1,col)` à `high` si elle est supérieure ;
4. applique la même logique avec le carré `(row,col−1)`, `(row+1,col)`, `(row,col)`, `(row+1,col−1)` : correction `+23` sous `low−16` si les quatre marqueurs valent `0x70`, sinon `+7` sous `low`.

En mode non nul, pour `col=2..taille−1` puis `row=2..taille−1`, il pose `NW=H(row−1,col−1)`, `low=NW−5`, `high=NW+5`, puis traite dans cet ordre `N=H(row−1,col)`, `C=H(row,col)`, `W=H(row,col−1)`. Chacune des trois cellules est bornée à `high` si elle est supérieure ; si elle est sous `low`, `NW` reçoit sa hauteur `+5` pour `N` et `C`, tandis que `W` reçoit sa propre hauteur `+5`. Le balayage recommence dès qu'une écriture a eu lieu.

Le relief final n'est donc pas un bruit brut. Il est explicitement régularisé par voisinage hexagonal avant la classification des terrains, avec deux automates numériques entièrement distincts selon le mode.

### CONFIRMED — coordonnées et distribution du bruit grossier

La maille espacée de 64 n'est pas une table auxiliaire séparée : elle écrit directement dans le champ de relief de la grille principale.

- La première adresse de cette passe, `this+0x187A48`, vaut `this+0x67448 + 0x120600`.
- `0x120600 = 64 × 0x4800 + 64 × 0x18` : le premier échantillon est donc la cellule de coordonnées `(64,64)` dans la grille préallouée.
- La boucle interne avance de `0x120000 = 64 × 0x4800` (64 lignes) et la boucle externe de `0x600 = 64 × 0x18` (64 colonnes).
- La passe n'est exécutée que si la taille active est strictement supérieure à 64 ; les coordonnées réellement écrites sont `64,128,192,...` tant qu'elles restent strictement inférieures à la taille.

Pour chaque point de la maille, un mot pseudo-aléatoire `u` sur 16 bits est transformé ainsi :

| Condition sur l'une des deux coordonnées | Valeur écrite dans le relief brut |
|---|---|
| coordonnée `< 65` ou `> taille−65` | `floor(u × 120 / 65536)` : `0..119` |
| sinon, coordonnée `< 129` ou `> taille−129` | `floor(u × 250 / 65536)` : `0..249` |
| sinon | `50 + floor(u × 200 / 65536)` : `50..249` |

Les conditions sont des comparaisons inclusives traduites par le code en bandes `<65`, `>taille−65`, puis `<129`, `>taille−129`. Il s'agit d'un profil de bord/continent numérique confirmé, pas d'un découpage en chunks indépendants.

### CONFIRMED — raffinement multi-résolution exact

Après les ancres 64, le générateur parcourt les échelles `s = 32,16,8,4,2,1`. Pour chaque bloc de pas `2s`, trois phases écrivent les points intermédiaires suivants :

1. le milieu entre les deux coins verticaux ;
2. le milieu entre les deux coins horizontaux ;
3. le centre diagonal du bloc.

Pour une paire de reliefs `a,b`, le chemin normal calcule :

```text
m = floor((a + b) / 2)
d = floor(110 × s / 64)
lo = max(m − d, 0)
hi = min(m + d, 255)
valeur = lo + floor(PRNG16 × (hi − lo) / 65536)
```

Les branches de bord empêchent certains doublons ou écritures hors de la zone active ; leurs conditions sont celles du tableau ci-dessous pour les blocs dont les extrémités sont dans le contrat natif. Après la dernière échelle, la normalisation est exacte : toute valeur brute `<31` devient `0`, sinon `30` est soustrait. La classification des terrains travaille donc sur ce relief normalisé, et non sur les octets bruts de la maille.

La lecture des branches de bord permet de préciser ce qui était encore regroupé sous « évite les doublons ». Pour un bloc d'origine `(r,c)`, le code calcule les extrémités nominales `R=r+2s` et `C=c+2s`. Lorsque l'une vaut exactement `taille`, elle est ramenée à `taille−1` avant l'accès. Pour les échelles `s=32`, la formule normale est conservée. Aux échelles `s≤16`, certaines positions de bord ne sont pas interpolées : la branche court-circuite la formule et écrit directement `0`.

En notant `R'` et `C'` les extrémités éventuellement ramenées à `taille−1`, les conditions exactes du chemin zéro sont :

| Famille de point intermédiaire | Écrit `0` si… |
|---|---|
| milieu vertical (entre `(r,c)` et `(R',c)`) | `c=0`, ou `s≤16` et (`r=0` ou `R'=taille−1`) |
| milieu horizontal (entre `(r,c)` et `(r,C')`) | `r=0`, ou `s≤16` et (`c=0` ou `C'=taille−1`) |
| centre diagonal (entre `(r,c)` et `(R',C')`) | `s≤16` et (`r=0` ou `R'=taille−1` ou `c=0` ou `C'=taille−1`) |

Dans tous les autres cas du domaine normalement parcouru, le code passe par la formule `m±floor(110s/64)` décrite ci-dessus. Cette asymétrie explique pourquoi les bords peuvent rester très bas alors que les points intérieurs sont bruités. Le désassemblage ne montre pas de traitement équivalent pour une extrémité strictement supérieure à `taille` ; les tailles natives semblent donc être choisies pour que les blocs rencontrent le bord par égalité. Ce seul cas de dimension non standard reste **PARTIAL** et est refusé explicitement par la reconstruction C++ plutôt que d'inventer un comportement.

### CONFIRMED — première classification relief → terrains structurants

La branche de classification à `0x5175B7` écrit directement le champ terrain principal selon la hauteur locale :

| Hauteur interne | Terrain écrit |
|---:|---:|
| `0` | eau niveau 1 (`0x00`) |
| `1..139` (`< 0x8C`) | herbe (`0x10`) |
| `140..189` (`0x8C..0xBD`) | roche (`0x20`) |
| `190..255` (`≥ 0xBE`) | neige (`0x80`) |

La branche manipule aussi quelques marqueurs de travail hérités des passes précédentes ; le tableau décrit le chemin normal de classification.

La classification ne parcourt pas le contour : ses deux boucles vont de `1` à `taille−2`. Comme l'initialisation avait placé le terrain principal à `0`, la bordure d'une cellule reste donc de l'eau `0x00` à ce stade ; les traitements de bords ultérieurs constituent une exception séparée liée au masque de mode.

**Conséquence d'ordre confirmée :** eau, herbe, roche et neige sont déterminées par le relief **avant** les rivières et avant les pinceaux désert/marais/boue/herbe sèche. Les pinceaux ultérieurs exigent une zone de source entièrement herbeuse : ils ne peuvent donc pas se poser à travers la roche ou la neige déjà classées.

### STRONG — origine des lacs

Dans la routine centrale, aucune passe de pinceau dédiée à la création de lacs n'a été observée. Avant la classification, les passes écrivent le relief et ses marqueurs ; la classification transforme ensuite toute hauteur normale égale à zéro en eau `0x00`. Les traitements ultérieurs ajustent les transitions et les rives, tandis que les seules nouvelles cellules aquatiques identifiées sont les rivières `0x60–0x63`.

La meilleure lecture actuelle est donc : **les lacs sont des dépressions de la construction relief/continent**, et non des zones ajoutées après coup par un générateur de lacs indépendant. La forme exacte dépend encore des contraintes et corrections de relief précédentes.

## 5. Pinceaux de surfaces et absence de liseré artificiel

### CONFIRMED — contrat du pinceau `0x51AED0`

La routine reçoit une surface source, une surface cible et un coefficient. Pour une taille positive, son nombre de groupes est exactement :

```text
n64 = floor(taille / 64)
groupes = floor(n64² × coefficient / 8)
```

Elle :

1. choisit un centre aléatoire ;
2. effectue huit essais autour de ce centre, avec décalages aléatoires dans une fenêtre approximative de `±16` cellules ;
3. n'autorise l'écriture que si la cellule et ses six voisins portent tous la surface source ;
4. écrit la surface cible dans le champ principal ;
5. répète `groupes` fois, avec le compteur ci-dessus. Les instructions de masque autour des divisions ne changent pas le résultat pour les tailles positives : elles implémentent ici une division signée par troncature.

Pour chaque essai, le centre est tiré dans `1..taille−2`. Les deux offsets sont indépendamment tirés par `PRNG16 & 0x1F − 0x10`, donc dans `−16..+15`. La cellule résultante doit encore rester dans `1..taille−2`, avoir son octet secondaire nul, et satisfaire le test des sept cellules homogènes.

Cela démontre une règle de séparation forte : deux surfaces incompatibles ne sont pas placées bord à bord par recouvrement naïf. Le code ne fabrique pas un trait neutre systématique entre deux pinceaux ; il refuse d'abord les emplacements non homogènes, puis applique les passes d'expansion/lissage.

### CONFIRMED — coefficients de pose par famille

Les séquences de pinceaux source `herbe (0x10)` → cible observées sont :

| Famille cible | Coefficients successifs de pinceau | Adresse des appels principaux |
|---|---|---|
| Désert (`0x40`) | `2`, puis `1` | `0x517F6A`, `0x517FAE` |
| Marais (`0x50`) | `1`, puis `1`, puis `1` | `0x51805D`, `0x518080`, `0x5180A3` |
| Boue (`0x90`) | `1`, puis `1` | `0x51811E`, `0x518158` |
| Herbe sèche (`0x18`) | `3`, puis `2`, puis `1` | `0x518204`, `0x518227`, `0x51824A` |

### CONFIRMED — chronologie exacte des opérateurs par famille

Les appels visibles dans la routine centrale distinguent le nombre de pinceaux, les expansions déterministes entre ces pinceaux et les quatre érosions probabilistes qui suivent chaque famille.

| Famille cible | Coefficients des pinceaux | Expansions `0x519440` après chaque pinceau | Érosions `0x519470` | Transitions ensuite |
|---|---:|---:|---:|---|
| Désert `0x40` | `2, 1` | `5, 6` | `80, 60, 40, 20` | `0x40 → 0x14 → 0x41` |
| Marais `0x50` | `1, 1, 1` | `2, 2, 1` | `80, 60, 40, 20` | `0x50 → 0x15 → 0x51` |
| Boue `0x90` | `1, 1` | `3, 3` | `80, 60, 40, 20` | `0x90 → 0x17 → 0x91` |
| Herbe sèche `0x18` | `3, 2, 1` | `2, 2, 3` | `80, 60, 40, 20` | aucune chaîne équivalente observée dans ce bloc |

Cette chronologie exclut une lecture simpliste en « pinceau puis lissage » : les expansions consomment les cellules source adjacentes à la famille cible, puis les érosions remettent certaines cellules de la famille à la source herbe.

Chaque série est suivie d'un nombre propre de passes d'expansion, nettoyage et lissage. Ces coefficients sont des paramètres de tentative/échelle du pinceau, non des pourcentages directs de surface finale.

### CONFIRMED — familles traitées dans la table

Après la classification initiale, les blocs principaux apparaissent dans cet ordre de famille interne :

1. transformations depuis l'herbe `0x10` vers le désert `0x40` ;
2. transformations depuis l'herbe `0x10` vers le marais `0x50` ;
3. transformations depuis l'herbe `0x10` vers la boue `0x90` ;
4. transformations depuis l'herbe `0x10` vers l'herbe sèche `0x18` ;
5. conversions complémentaires (`0x10→0x12`, `0x10→0x13`, `0x20→0x22`) ;
6. variantes numérotées et motifs ;
7. détails.

Les correspondances ci-dessus sont confirmées par la référence de format : `0x10=Grass`, `0x18=Dry grass`, `0x20=Rocky`, `0x30=Shore`, `0x40=Desert`, `0x50=Swamp`, `0x60–0x63=River widths 1–4`, `0x80=Snow`, `0x90=Mud`. Les valeurs de travail et certaines variantes de transition restent à établir.

### CONFIRMED — chaînes de transition des grandes familles

Le bloc central de transitions ne se contente pas de poser des noyaux de terrain. Les appels paramétrés à `0x519270` produisent les chaînes internes suivantes, avec nettoyage des sentinelles autour de chaque série :

| Famille | Chaîne observée |
|---|---|
| Désert | `0x40 → 0x14 → 0x41` |
| Marais | `0x50 → 0x15 → 0x51` |
| Boue | `0x90 → 0x17 → 0x91` |
| Herbe sèche | aucune chaîne de transition explicite équivalente dans ce bloc |

Les valeurs `0x14`, `0x15`, `0x17`, `0x41`, `0x51` et `0x91` sont des terrains/états internes de transition, et non des noms visuels définitivement établis. La séquence exacte des appels comprend des expansions, des lissages paramétrés et des conversions de sentinelles ; elle ne doit pas être réduite à un simple remplacement global de la famille source.

### CONFIRMED — micro-terrains après les grandes zones

Après les quatre grandes familles de pinceaux, trois poses supplémentaires sont appelées :

| Source | Cible | Coefficient | Lecture actuelle |
|---|---:|---:|---|
| Herbe `16` | `18` | 2 | micro-terrain / transition d'herbe sèche, nom précis à stabiliser |
| Herbe `16` | `19` | 2 | micro-terrain / transition d'herbe sèche, nom précis à stabiliser |
| Roche `32` | `34` | 2 | patch d’herbe rocheuse : petites inclusions d’herbe dans la roche |

Ces ajouts interviennent avant la génération des variantes graphiques et des détails, mais après les grandes zones et leurs lissages.

### CONFIRMED — opérateurs entre pinceaux

- `0x519210` : remplacement global d'une valeur dans le champ de surface, hors bord.
- `0x519270` : `remplacer(source, voisin_déclencheur, cible)` ; pour chaque cellule de valeur `source`, la remplacer par `cible` si **au moins un** de ses six voisins vaut `voisin_déclencheur`.
- `0x519440` : expansion suivie d'un nettoyage de sentinelle.
- `0x519470` : lissage probabiliste, suivi du même nettoyage.
- `0x51A2E0` / `0x51A400` : marquage puis remplacement d'une sentinelle de travail (`0xF3`).

Le comportement exact des deux wrappers est le suivant :

```text
expand(target, source):
    pour chaque cellule intérieure c:
        si terrain(c) == source et au moins un des six voisins vaut target:
            terrain(c) = 0xF0
    remplacer globalement 0xF0 par target

erode(target, source, chance):
    pour chaque cellule intérieure c:
        si terrain(c) == target et au moins un des six voisins vaut source:
            q = floor(PRNG16 × 100 / 65536)   # 0..99
            si q < chance:
                terrain(c) = 0xF0
    remplacer globalement 0xF0 par source
```

Dans l'appel central, `0x519440(target, source)` est donc déterministe, tandis que `0x519470(target, source, chance)` applique la probabilité exacte `q < chance`. Les seuils observés `0x50`, `0x3C`, `0x28` et `0x14` correspondent respectivement à `80 %`, `60 %`, `40 %` et `20 %` avec cette convention stricte.

### CONFIRMED — chaînes de transitions explicites

Les appels de `0x519270` et `0x519210` donnent les chaînes suivantes :

| Famille | Règles observées |
|---|---|
| Roche / herbe | `Rocky32 → Rock transition17` au contact de `Grass16`, puis `Rocky32 → Rock transition33` au contact de `17`. |
| Roche / neige | `Snow128 → Rock/Snow transition35` au contact de `Rocky32`, puis `Snow128 → Snow transition129` au contact de `35`. |
| Côte | eau et herbe adjacentes sont d'abord marquées par deux sentinelles, toutes deux converties en `Shore48`; une seconde série construit ensuite les niveaux d'eau `0..7` à partir du contact eau/rivage. |

Pour la première bordure, la séquence exacte est `Water0 → sentinel` au contact de `Grass16`, puis `Grass16 → sentinel` au contact de cette première sentinelle ; les deux sentinelles deviennent `Shore48`. La côte initiale couvre donc les deux côtés de la frontière eau/herbe avant la construction des profondeurs.

La seconde séquence part de `Water0` adjacent au rivage, génère successivement `Water1` à `Water7`, convertit l'eau résiduelle en `Water7`, puis rétablit la sentinelle de contact en `Water0`. La largeur apparente du rivage ne vient donc pas d'un unique anneau dessiné après coup, mais de conversions conditionnelles successives de cellules de part et d'autre de la frontière eau/herbe.

## 6. Objets statiques et détails hors terrain principal

### CONFIRMED

Les objets statiques n'écrivent pas dans le même champ que les surfaces
principales. Les routines `0x51B010` et `0x51B1A0` :

- sélectionne une position intérieure ;
- exige une zone compatible avec la famille de surface demandée ;
- vérifie l'absence de conflit avec les poses déjà effectuées ;
- écrit un ID d'objet statique dans le champ runtime `+0x6744B` ;
- peut marquer plusieurs voisins comme occupés.

Les appels couvrent de nombreuses plages d'objets (`1–0x7F`), groupées par
famille source (`0x10`, `0x30`, `0x40`, `0x50`). Les motifs plus structurés
passent par `0x51B1A0` et utilisent une table de décalages. Ces valeurs ne
sont pas les IDs terrain EDM/MAP : les IDs terrain sont déjà présents dans le
champ principal. La correspondance éventuelle avec un byte 2 Area exporté
reste à suivre séparément dans l'audit non-terrain.

Les appels directs à cinq paramètres couvrent notamment les groupes suivants :

| Terrain source | Plages d'IDs d'objets observées |
|---|---|
| Herbe `0x10` | `0x01–0x1C`, `0x22–0x2A`, `0x32–0x3D`, `0x44–0x4D`, `0x50–0x51`, `0x73–0x7F` |
| Rivage `0x30` | `0x1D–0x21` |
| Désert `0x40` | `0x2B–0x31`, `0x4E–0x4F` |
| Marais `0x50` | `0x3E–0x43` |

Une seconde routine structurée (`0x51B1A0`) couvre aussi les motifs de base `0x44–0x51` et `0x73–0x7E`, avec des décalages pré-calculés. Les valeurs sont bien écrites dans le champ objet runtime `+0x6744B` ; leur correspondance exacte avec les tuiles graphiques et le byte 2 d'un Area exporté reste à établir.

### CONFIRMED — paramètres de la pose structurée `0x51B1A0`

La routine structurée reçoit six paramètres après `this` :

- la famille source ;
- une borne minimale et une borne maximale de variante, inclusives ;
- un coefficient de densité ;
- un mode de marquage (`1` pour le centre, `2` pour les sept cellules du motif) ;
- un paramètre de limite de conflit.

Pour une taille positive, le nombre de tentatives est `floor(floor(taille / 64)² × coefficient / 16)`. L'objet écrit est calculé comme `min + (PRNG × (max−min+1) >> 16)`. Chaque tentative choisit un centre intérieur de la carte et lit les décalages de l'empreinte dans les tableaux pré-calculés du générateur. Le prédicat `0x51B450` exige à nouveau que le centre et ses six voisins appartiennent à la famille source ; `0x51B3C0` rejette les motifs qui entrent en conflit avec un objet ou un drapeau déjà présent.

### CONFIRMED — banque native d'offsets hexagonaux

L'initialisation `0x516530`, appelée une fois depuis `0x4FCA65`, construit une
banque d'offsets commune aux empreintes, aux métriques de départ et à plusieurs
placements structurés. Elle réserve `0xEA68` octets pour `5 000` candidats,
réinitialise les états à `world+0x110A588`, `+0x110A58C` et `+0x110A590`, puis
sélectionne `3 333` candidats selon leur métrique croissante. Il ne s'agit pas
de chunks de la carte : la banque est un ordre de voisinage réutilisable.

Les candidats sont énumérés par anneaux triangulaires : `x=1,2,3,...` et
`y=0..x−1`. Pour un candidat `(x,y)`, le désassemblage donne exactement :

```text
d = 2*x - y
metric = 2500*d*d + 7569*y*y
```

La sélection prend le plus petit score strictement (`<`, donc le premier en
cas d'égalité), puis remplace son score par `0x7FFFFFFF`. Chaque candidat
retenu produit six offsets dans l'ordre :

```text
( x,  y), ( x-y,  x), (-y, x-y),
(-x, -y), (y-x, -x), ( y, y-x)
```

Chaque entrée finale fait `0x10` octets et contient
`[dx, dy, ring_marker, orientation]`. Les six entrées d'un groupe partagent
le même `ring_marker`, initialisé à `1` et incrémenté après le groupe si le
candidat sélectionné avait `y==0`. L'orientation vaut `0,1,2,3,4,5` lorsque
`2*y <= x`, sinon `1,2,3,4,5,0`. L'origine est stockée séparément dans
`world+0x110A588` ; le pointeur consommé par les routines vise
`+0x110A58C`, et `+0x110A590` contient le marqueur de l'anneau d'origine,
pas un compteur. Le résultat contient donc `1 + 3333*6 = 19999` entrées.

Les routines consommatrices s'arrêtent selon leur propre sous-ensemble ou
marqueur d'anneau (`0x4D99E0` utilise notamment les anneaux `<=0x14`). La
table de tokens d'empreintes à `0x6AA174` est une table distincte : elle
décrit les cellules d'un motif, tandis que la banque ci-dessus fournit les
centres/décalages candidats. Cette séparation ne fournit aucune preuve de
sous-régions fixes de la carte.

### PARTIAL

La correspondance exacte entre les valeurs de variantes et les tuiles/rendus graphiques reste à établir par analyse des tables de paysage.

### CONFIRMED — graphe de compatibilité observé dans le runtime

Une routine distincte à `0x548D50`, appelée par le répartiteur d'opérations de surface autour de `0x5480B3`, accepte une paire de codes et retourne vrai uniquement pour les voisinages autorisés suivants :

| Code de référence | Codes compatibles observés |
|---|---|
| `0x10` | `0x10`, `0x11`, `0x30`, `0x12`, `0x13`, `0x14`, `0x15`, `0x60–0x63`, `0x70`, `0x71`, `0x16`, `0x17`, `0x18`, `0x1C` |
| `0x15` | `0x10`, `0x15`, `0x51` |
| `0x51` | `0x15`, `0x51`, `0x50` |
| `0x20` | `0x20–0x23` |
| `0x23` | `0x20`, `0x23`, `0x81` |
| `0x81` | `0x23`, `0x81`, `0x80` |
| `0x40` | `0x40`, `0x41` |
| `0x41` | `0x40`, `0x41`, `0x14` |
| `0x14` | `0x41`, `0x14`, `0x10` |
| `0x90` | `0x90`, `0x91` |
| `0x91` | `0x90`, `0x91`, `0x17` |
| `0x17` | `0x91`, `0x17`, `0x10` |

Ce graphe indépendant valide la cohérence des familles et des transitions déjà observées dans `0x517E63–0x5182A8`. Il confirme notamment que `0x14/0x41`, `0x15/0x51` et `0x17/0x91` ne sont pas des valeurs arbitraires du générateur. La fonction appartient toutefois à un chemin de traitement de surfaces en cours de partie ; elle ne constitue pas encore une table directe `variante → tuile graphique`, ni une preuve supplémentaire sur l'ordre de génération central.

## 7. Génération des rivières, antérieure aux pinceaux

### CONFIRMED

La phase `0x517699–0x517E62` :

- effectue `4 × taille²` tentatives sur un index qui avance de `0x97` modulo `taille²` ;
- ignore les candidats situés à moins de 8 cellules du bord ;
- n'engage une tentative qu'après un tirage PRNG inférieur à `0x07D0` (2 000 sur 65 536) ;
- mesure aussi un voisinage carré de 9×9 comme filtre local avant de tracer ;
- choisit certains points internes selon le PRNG ;
- consulte le relief et un voisinage local ;
- progresse de cellule en cellule parmi les six directions ;
- stocke les terrains rivière `0x60`, `0x61`, `0x62`, `0x63` (largeurs 1 à 4) dans le champ de surface ;
- remet ou adapte des cellules selon les voisins avant l'étape des pinceaux.

### CONFIRMED — conséquence d'ordre

Les rivières sont effectivement créées **avant** les pinceaux désert/marais/boue de la grande table. Ces pinceaux n'écrivent que là où la cellule et ses six voisins sont tous de la surface source (`0x10`, l'herbe) : une rivière déjà tracée fait donc échouer ce prérequis local et est préservée. L'ordre natif observé n'est donc pas « surfaces puis rivières », même si le résultat final donne visuellement l'impression inverse.

### CONFIRMED — énumération exacte des candidats

Le premier index de la boucle rivière n'est pas nul. La dernière échelle du raffinement laisse dans le local `0x50` la valeur `3 × 1 × 512 = 0x600`, consommée comme premier index. À chaque tentative :

```text
q = floor(index / taille)
r = index − q × taille
index = (index + 0x97) mod (taille × taille)
coordonnée_1 = r
coordonnée_2 = q
```

La tentative est rejetée si l'une des coordonnées est `<8` ou `>taille−8`, puis avec une probabilité exacte de `63536/65536` (`PRNG16 >= 0x07D0`). Il reste donc `4 × taille²` positions déterministes, chacune passant ce tirage.

À ce moment du pipeline, une cellule candidate non nulle n'est acceptée que si son marqueur de route `+0x01` vaut au moins `2`. Une cellule nulle (l'eau issue de la classification ou de la bordure) peut entrer dans le chemin normal. Pour ce chemin normal, le code compte dans le carré `9×9` centré sur le candidat les cellules dont le terrain principal est `<0x10`; il faut strictement plus de `25` occurrences. Comme les seuls terrains structurants déjà posés sont alors `0x00`, `0x10`, `0x20` et `0x80`, ce filtre sélectionne en pratique une zone suffisamment aquatique autour du point de départ.

### CONFIRMED — choix du premier pas et marche hexagonale

Les six directions utilisées par la rivière, dans l'ordre du code, sont les suivantes. Les coordonnées sont les deux axes internes employés pour adresser la grille ; elles ne préjugent pas du nom `x/y` dans le format externe.

| Direction | `Δcoordonnée_1` | `Δcoordonnée_2` |
|---:|---:|---:|
| 1 | `+1` | `0` |
| 2 | `+1` | `+1` |
| 3 | `0` | `+1` |
| 4 | `−1` | `0` |
| 5 | `−1` | `−1` |
| 6 | `0` | `−1` |

Pour chaque direction, le voisin doit être exactement de l'herbe `0x10` et satisfaire `0x519860`, qui exige que les sept marqueurs de route de cette position et de ses couches hexagonales soient nuls. Parmi les voisins valides, le générateur conserve celui de **relief minimal** ; les égalités gardent le premier rencontré. En continuation, le marqueur du point source (qui vaut déjà au moins `2`) est temporairement remis à zéro pendant chaque test individuel de voisin, puis restauré avant le test suivant ; cette nuance doit être conservée dans un portage, car le test des sept marqueurs inclut le voisinage du point source.

Le candidat normal reçoit alors le marqueur temporaire `1`. La marche examine trois directions consécutives, en commençant par la direction précédente au premier meilleur voisin (`D−1`, avec rebouclage 6→1). Pour chaque direction proposée :

1. le voisin proposé doit être de l'herbe `0x10`, sans marqueur local, et ne peut pas être plus bas de plus d'une unité (`relief_courant − relief_voisin ≤ 1`) ;
2. autour de ce voisin, les six voisins d'herbe et sans marqueur ajoutent au score de la direction `relief_voisin_suivant − relief_voisin + offset` ;
3. la direction au score strictement maximal est retenue, avec priorité à la première en cas d'égalité.

L'`offset` commence à `2`. Après un déplacement, il devient `min(relief_nouveau − relief_ancien + 1, 2)` ; la condition du premier point implique qu'il est alors dans la plage `0..2`. Une même direction retenue trois fois de suite est ensuite écartée dans la phase de recherche correspondante, ce qui évite une marche droite indéfinie. Après le premier pas, une fenêtre carrée `9×9` centrée sur le candidat est également rejetée si elle contient un marqueur de route supérieur ou égal à `8`. Le score exact et sa règle de départ à zéro sont confirmés ; il sert uniquement à choisir la direction suivante et n'est pas encodé tel quel dans le marqueur final.

### CONFIRMED — longueur minimale, retour et promotion des rivières

Le compteur de marche commence à `1`. Le chemin normal vise le seuil `16`, tandis qu'une cellule déjà porteuse d'un marqueur `2..` suit le chemin de continuation avec le seuil `7`. Les cellules explorées sont chaînées par le marqueur temporaire `1`. Quand le seuil est atteint, le générateur convertit la cellule courante en `0x60`, puis remonte la chaîne des marqueurs `1` pour convertir le tracé.

Les états de marqueur observés sont :

- `1` : cellule temporaire de la chaîne en cours ;
- `2..7` ou `8..13` : direction/état de continuation, traité par décrément puis réduction modulo six ;
- `0x0E` : terminaison ;
- lors de la conversion, chaque cellule suivante de la chaîne reçoit la direction inverse de son arête d'entrée, encodée par `direction_inverse + 1` ; si l'entrée dépasse `6`, le code retranche `6`. Le score de relief n'est pas réutilisé pour fabriquer ce marqueur.

En mode normal, le point de départ reçoit `0x0E` et la chaîne est remontée via les cellules `1`. En mode continuation, le point de départ conserve d'abord son marqueur existant et reçoit sa valeur augmentée de `6`, tandis que les cellules suivantes reçoivent les directions inverses. L'extension repart du point de départ : elle promeut séquentiellement `0x60→0x61→0x62→0x63`, suit les directions `2..7` et `8..13` après réduction par `−6`, s'arrête sur `0x0E`, et écrit la variante `1` si le marqueur rencontré est hors de `2..0x0E`. Cela explique pourquoi les quatre codes rivière sont des états successifs de la marche, et pas quatre surfaces indépendantes posées par des pinceaux.

### CONFIRMED — nettoyage après les tentatives

Après les `4 × taille²` tentatives, le générateur parcourt les cellules dont le demi-octet haut vaut `0x60`. Si l'un de leurs six voisins n'est ni une rivière `0x60..0x63`, ni l'herbe `0x10`, ni le rivage `0x30`, ni l'eau `0x00`, la cellule rivière est réécrite en herbe `0x10`. Ce nettoyage confirme que le tracé natif se construit sur l'eau et l'herbe ; il ne traverse pas durablement les terrains structurants rocheux/neigeux, et les pinceaux de biomes ultérieurs ne peuvent pas l'écraser.

## 8. Bords et topologie

### CONFIRMED — effet exact du masque de mode

Le troisième argument réellement consommé (`mode`) n'est pas seulement un indicateur de bord. Tout `mode != 0` sélectionne d'abord la relaxation de relief alternative et supprime la sculpture locale. Ses bits `0x01` et `0x02` ont ensuite les effets déterministes suivants ; aucun autre bit n'a été observé dans le chemin central :

1. **Avant les trois micro-pinceaux**, `0x518D10(mode)` écrit `variant=0xFF` sur la diagonale principale `(i,i)` si `mode&0x01`, puis sur la diagonale opposée `(i,taille−1−i)` et les deux lignes adjacentes `(i,taille−2−i)` / `(i+1,taille−1−i)` si `mode&0x02`. Ces écritures ne changent pas directement le terrain principal, mais le pinceau vérifie `variant==0` au centre : elles changent donc bien les cellules éligibles aux micro-pinceaux.
2. **Après les passes secondaires**, `0x518DC0(mode)` remet à zéro ces mêmes familles de variantes. Cet effacement n'altère ni le relief ni le terrain principal.
3. Si `mode&0x02`, la copie anti-diagonale parcourt les sources `src=(i,j)` avec `j=0..taille−2` et `i=0..taille−j−2`, puis écrit vers `dst=(taille−1−j,taille−1−i)` le relief, le terrain principal, la variante, le champ natif `+0x06` et le détail `+0x0D`.
4. Si `mode&0x01`, la copie diagonale principale parcourt les sources `src=(i,j)` avec `j=1..taille−1` et `i=0..j−1`, puis écrit vers `dst=(j,i)` les mêmes cinq groupes de champs. La copie `0x02` intervient avant la copie `0x01`.

Les deux copies finales réécrivent donc réellement le relief et l'octet de terrain principal ; elles font partie du résultat à porter. Leur géométrie est maintenant connue, même si le nom fonctionnel du mode (symétrie, bord, format de scénario ou autre) reste inconnu. Les compléments aléatoires de détail, les variantes et les autres drapeaux demeurent hors du contrat minimal du terrain.

## 9. Post-traitement des composantes et marqueurs auxiliaires

### CONFIRMED — routine partagée après construction ou chargement

La routine `0x51A580` est appelée à la toute fin de `0x5166D0`, mais aussi dans le chemin de chargement d'une carte autour de `0x4FD89C`. Elle ne crée pas de nouvelles familles de terrain dans le champ principal ; elle prépare des informations auxiliaires à partir d'une carte déjà construite.

#### Première sous-passe : composantes sur le masque d'accessibilité

La routine :

1. marque toutes les cellules avec le bit de travail `0x10` ;
2. cherche une cellule encore marquée et dont le bit `0x01` est absent ;
3. réserve un identifiant via `0x51D5B0` dans la table `this+0xE114DC` (plage d'identifiants `1..0xFF`) ;
4. appelle `0x51D450`, qui écrit l'identifiant dans le champ cellule `+0x0C` et propage par six voisins via `0x51D3D0` ;
5. efface le bit de travail au fur et à mesure.

Le mécanisme est donc une labellisation de composantes connexes selon un prédicat de drapeaux. Le terme « secteur » est plausible, mais le sens exact du bit `0x01` et du champ `+0x0C` reste à confirmer.

#### Deuxième sous-passe : masque de 61 positions

Après remise à zéro du bit de travail, les cellules dont le terrain principal est une eau `0..7`, dont la variante secondaire est comprise entre `0x0D` et `0x10`, et qui satisfont le masque de drapeaux sont testées contre 61 décalages stockés à `this+0x110A58C`. Les cellules correspondant au motif reçoivent le bit `0x80`.

Cette opération est confirmée comme un marquage spatial ; sa fonction de jeu ou de rendu est encore **TODO**.

#### Troisième sous-passe : composantes d'eau profonde

Une nouvelle remise à zéro du bit de travail précède une recherche limitée aux terrains principaux `5`, `6` et `7` (eaux profondes), sans bit `0x80` :

- un identifiant est réservé via `0x51D570` dans `this+0xE115E4` (`1..0xFF`) ;
- `0x51CEE0` écrit un code 16 bits `identifiant + 0x8000` dans le champ cellule `+0x10` ;
- `0x51CE50` propage ce code uniquement dans les cellules d'eau profonde compatibles.

C'est une seconde labellisation de composantes, cette fois explicitement restreinte aux eaux profondes. Elle pourrait servir à distinguer mers, lacs ou zones navigables, mais le nom métier ne doit pas encore être figé.

#### Quatrième sous-passe : composantes compatibles pour une autre couche

La dernière partie travaille avec une autre couche de données autour de `this+0x62C4E`, et non uniquement avec le tableau principal des terrains. Elle vérifie un voisinage étendu :

- plusieurs drapeaux voisins doivent être compatibles ;
- un voisinage présentant le demi-octet haut `0x20` (roche) est rejeté ;
- un identifiant jusqu'à `0x1FFF` est réservé via `0x51C040` dans `this+0xE125E8` ;
- `0x51D2B0` écrit l'identifiant comme mot dans le champ cellule `+0x12` et le propage via `0x51D000`.

Le calcul forme donc encore des régions connexes, mais sa couche source et son usage exact sont **PARTIAL/TODO**. Il peut s'agir d'une préparation pour la navigation ou le placement d'objets, sans que le désassemblage seul permette de le trancher.

### PARTIAL — ne pas relier automatiquement à `sectors done`

Le texte `sectors done` est référencé à `0x519F80`, dans une fonction appelée depuis le chemin de chargement autour de `0x4FD024`, puis suivie de l'appel à `0x51A420`. Ce n'est pas un appel direct à `0x51A580` dans le chemin de génération aléatoire. Le message confirme l'existence d'une préparation de secteurs dans le programme, mais ne permet pas de donner ce nom à chacune des quatre sous-passes de `0x51A580`.

## 10. Processus complet dans l'ordre — champ terrain principal

Cette séquence est la reconstruction ordonnée du chemin central, limitée volontairement au résultat que nous cherchons : le relief et l'octet de terrain principal. Chaque étape est placée selon le flot `0x5166D0–0x5182A8`; les variantes graphiques et le post-traitement auxiliaire sont indiqués à la fin mais ne sont pas mélangés à l'algorithme des terrains.

```text
generate_primary_terrain(config):
    # Entrée réellement consommée par le chemin central
    side = config.argument_2              # champ appelant +0x08
    mode = config.argument_3              # champ appelant +0x10
    native_rng.init(side)                 # même argument que side
    # argument_1 (champ appelant +0x14) est poussé mais non lu ici

    initialize_all_cells(side)
        relief = 0
        marker = 0x1F                  # ensuite effacé avant les rivières
        terrain = 0x00
        autres_champs = sentinelles/valeurs initiales

    if side > 64:
        seed_relief_on_64_cell_lattice()

    for s in [32, 16, 8, 4, 2, 1]:
        refine_three_midpoint_families(s)
            vertical midpoint
            horizontal midpoint
            diagonal center

    normalize_relief()                    # <31 -> 0, sinon -30

    if mode == 0:
        repeat floor(side*side/16) times:
            ligne = 1 + trunc((PRNG16 * side - 2) / 65536)
            colonne = 1 + floor(PRNG16 * (side - 3) / 65536)
            if candidate_is_valid_and_519960_allows_it:
                run_local_sculptor_states_4_3_2_1()
                allow_at_most_two_passes_for_this_candidate()
        consume_70_and_F0_markers_into_relief()
        relax_relief_mode_0_until_stable()
    else:
        relax_relief_alternate_mode_until_stable()

    classify_interior_relief()
        0       -> 0x00 water
        1..139  -> 0x10 grass
        140..189-> 0x20 rocky
        190..255-> 0x80 snow

    clear_variant_and_marker_work_fields() # deux balayages avant les rivières
    generate_rivers()                      # 4*side*side attempts
        deterministic index walk + PRNG gate
        first step on grass, six-direction scoring
        temporary marker chain, backtrack, widths 0x60..0x63
        remove river cells with incompatible neighbours

    apply_structural_transitions()
        coast/shores and water depths 0x00..0x07
        rock/grass transitions 0x11 and 0x21
        snow/rock transitions 0x23 and 0x81

    for family in [desert, swamp, mud, dry_grass]:
        protect_grass_boundary_with_F3()
        run_exact_brushes_and_deterministic_expansions(family)
        restore_F3_to_grass_boundary()
        run_erosions_80_60_40_20(family)
        run_family_transition_chain_if_present(family)

    if mode != 0:
        set_variant_sentinels_before_micro_brushes(mode)
    run_micro_brushes(0x10->0x12, 0x10->0x13, 0x20->0x22)

    if mode != 0:
        clear_variant_sentinels_after_secondary_passes(mode)
        if mode & 0x02: copy_anti_diagonal_relief_terrain_and_fields()
        if mode & 0x01: copy_main_diagonal_relief_terrain_and_fields()

    # Suite native suivante, hors champ terrain principal
    generate_graphic_variants_and_patterns()
    add_details_and_finalize_edges()
    build_shared_auxiliary_components()
```

### Chronologie numérotée et preuves

1. **Initialisation et état aléatoire** (`0x5166D0–0x5167E5`) : la grille active est remise à zéro, le PRNG trois-mots est initialisé à partir du deuxième argument réellement lu, et les sentinelles des champs sont posées.
2. **Ancres de relief** (`0x5167E6–0x5168D8`) : pour `side>64`, des points espacés de 64 sont écrits directement dans le champ hauteur, avec les trois distributions de bord `0..119`, de couronne `0..249` et d'intérieur `50..249`.
3. **Raffinement** (`0x5168D9–0x516B7D`) : les six échelles sont parcourues par blocs de `2s`, dans l'ordre vertical, horizontal, diagonal. Les zéros de bord aux petites échelles suivent le tableau des conditions exactes de la section 4.
4. **Normalisation** (`0x516B89–0x516BD0`) : toute hauteur brute inférieure à `31` devient `0`, sinon l'octet perd `30` unités.
5. **Relief conditionné par le mode** (`0x516CAE–0x5175B6`) : mode nul, sculpture locale puis consommation des marqueurs et relaxation dédiée ; mode non nul, saut de la sculpture et relaxation alternative. Cette bifurcation est exécutée avant la classification.
6. **Classification structurante** (`0x5175B7–0x51761E`) : eau, herbe, roche et neige sont écrites dans le champ principal uniquement pour l'intérieur `1..side−2`.
7. **Rivières** (`0x517699–0x517E62`) : quatre fois `side²` tentatives, filtre de départ, marche hexagonale, chaîne temporaire et nettoyage des incompatibilités.
8. **Rives et transitions roche/neige** (`0x517E63–0x517F68`, puis appels associés) : la côte est construite par sentinelles successives et profondeurs `0..7`; les contacts roche/herbe et neige/roche reçoivent leurs états de transition.
9. **Grandes familles de surfaces** (`0x517F6A–0x51824A`) : désert, marais, boue, puis herbe sèche. Chaque famille suit son propre nombre de pinceaux, ses expansions, ses quatre érosions probabilistes et, pour les trois premières, sa chaîne de transitions.
10. **Micro-terrains** (`0x51824A` et appels voisins) : les trois pinceaux complémentaires ajoutent `0x12`, `0x13` et `0x22` après les grandes familles.
11. **Finalisation dépendante du mode** (`0x5182AD–0x518BBC`) : les sentinelles de variante sont posées avant les trois micro-pinceaux, puis effacées après les passes secondaires. Les copies bit `0x02` puis bit `0x01` réécrivent effectivement relief et terrain principal dans les triangles correspondants ; elles sont donc incluses dans la reconstruction. Les autres variantes, motifs, détails et bords n'ajoutent pas d'écriture de terrain principal observée sur ce chemin. La routine partagée `0x51A580` construit ensuite des composantes et marqueurs auxiliaires à partir de la carte finale.

Les points `PARTIAL` de cette séquence sont localisés, et non diffus : le comportement d'une dimension qui fait dépasser strictement une extrémité de raffinement, le nom géométrique des états `4/3/2/1`, le sens métier du masque de mode et les champs graphiques/auxiliaires hors terrain principal. L'ordre des grandes phases, les écritures de terrain et leurs seuils numériques sont, eux, confirmés.

## 11. Extraction technique progressive

Le désassemblage mécanique du noyau du générateur, couvrant le PRNG, la grille, le relief, les transitions, les pinceaux, les variantes et le post-traitement jusqu'au voisinage de `0x51D6D0`, est archivé séparément sous le nom `S3_EXE_GENERATOR_CORE_DISASSEMBLY_20260901.txt`.

Une extraction complète de la section `.text` est maintenant également disponible sous `S3_EXE_FULL_TEXT_DISASSEMBLY_20260901.txt` : 39 929 051 octets, 826 773 lignes, SHA-256 `c714f4c6f9f4520a1bc666dc95643fd6310ce6bf00903f905ffebfff5ae5bd14`. Elle permettra une relecture globale sans relancer la décompilation mécanique. Les deux fichiers sont des sorties brutes reproductibles ; l'audit reste la référence interprétée et annotée.

## 12. Ce qui reste à vérifier avant de déclarer le portage validé

1. Comparer la reconstruction à une ou plusieurs cartes/SAV de référence ou à une sortie connue, sans exécuter ni altérer l'original. Cette étape valide l'égalité de résultat ; elle ne remplace pas les preuves statiques déjà réunies.
2. Vérifier le contrat de dimension réellement accepté par l'interface du jeu. Pour une dimension non multiple du pas naturel, le désassemblage ne définit pas le cas où un bloc de raffinement dépasse strictement la taille active ; la reconstruction le refuse explicitement.
3. Si l'objectif devient un rendu ou un fichier parfaitement identique cellule par cellule, décoder séparément les variantes, détails, drapeaux et composantes auxiliaires. Ces couches ne sont pas nécessaires pour porter le relief et le terrain principal.

Il n'y a plus de branche inconnue dans le chemin du **terrain principal** pour les dimensions natives prises en charge : le PRNG, les ancres, le raffinement, la sculpture, les deux relaxations, la classification, les rivières, les transitions, les quatre familles, les micro-pinceaux et les copies finales de mode sont reliés dans l'ordre. Les inconnues restantes portent sur les noms métier, le contrat d'entrée hors format normal et les couches secondaires.

## Révision

Ce document constitue la spécification statique de portage du terrain principal. Les éléments `PARTIAL` ou `TODO` sont explicitement hors du contrat exact (noms métier, dimensions non standard, métadonnées secondaires) et ne doivent pas être transformés en règles du générateur sans nouvelle preuve ou comparaison de sortie. La reconstruction C++ associée est une traduction comportementale relisible, pas le source original.
