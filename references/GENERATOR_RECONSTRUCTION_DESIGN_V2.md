# Reconstruction du générateur — conception v2

> Document de travail pour le premier générateur réellement procédural.
> Il ne remplace pas la référence v1.5 : celle-ci reste disponible pour
> régression, comparaison et extraction de mesures natives.

## Diagnostic établi le 28 août 2026

Le moteur v1.5 ne calcule pas sa macro-géographie à partir de la seed.

- `SETTLERS3_NATIVE_768_STATIC_LIBRARY_v1.npz` contient trois couples
  `terrain + height`, tous en 768×768 ;
- la sélection est `template = Random(seed).randrange(3)` ;
- la seule variation de forme est une des quatre symétries compatibles déjà
  codées (identité, rotation 180°, transposition, transposition+rotation) ;
- Legacy et Upgraded appellent la même sélection de morphologie ; leurs
  différences ne commencent qu'après cette étape.

Ainsi, 64 seeds échantillonnées produisent exactement 12 macro-formes
(`3 templates × 4 transforms`) dans chacun des deux modes. Les ressources et
objets changent, mais la silhouette continentale ne peut pas être nouvelle.

## Objectif

Créer deux implémentations explicites et indépendantes :

- `ContinentalLegacyGenerator` : profil proche des distributions natives ;
- `ContinentalUpgradedGenerator` : profil de jeu du projet, notamment les
  corrections/accessibilités et les quotas explicitement validés.

Elles partagent seulement des primitives sans politique : topologie HEX6,
masques, bruit déterministe, profondeur, validation et sérialisation. Un mode
ne doit pas devenir une succession de `if mode == ...` dans un générateur
unique. Les futurs archétypes auront leur propre générateur ; les modificateurs
seront des couches déclarées après une carte Continental valide.

## Précondition non négociable : corpus brut

Les références actuellement versionnées contiennent des statistiques déjà
extraites, mais les 21 SAV natifs bruts ne sont pas dans le dépôt. Ils sont
nécessaires pour recalculer les signatures, vérifier les hypothèses et dériver
des distributions par taille sans figer un nombre moyen.

Un prototype de macro-forme fondé uniquement sur du bruit a été volontairement
retiré le 28 août 2026 : il aurait produit des cartes nouvelles, mais pas une
génération suffisamment démontrée comme native-compatible. Le prochain code
de géographie ne sera ajouté qu'après l'outillage d'analyse du corpus et sa
calibration contre les fichiers source.

## Calibration de la côte — 29 août 2026

Le générateur Continental Legacy v2 dispose maintenant d'une bibliothèque
compacte de silhouettes littorales dérivées hors ligne des 8 SAV 768 à 2
joueurs et des 8 SAV 768 à 20 joueurs fournis pour la calibration. Elle ne
contient ni terrain intérieur, ni objets, ni territoires, ni données de joueur :
uniquement les masques remplis du continent principal.

À l'exécution, la banque 2 joueurs est utilisée pour les faibles densités et la
banque 20 joueurs au-delà de 8 joueurs. Une symétrie HEX sûre et une petite
déformation continue sont tirées par seed, puis la croissance connectée impose
la surface cible. Les SAV bruts et les images ne sont donc jamais lus par le
générateur. Les tailles inférieures à 768 conservent le chemin procédural de
secours jusqu'à disposer de silhouettes calibrées à ces tailles.

## Contrat d'exécution

Une requête de génération contient au minimum : `side`, `players`, `seed`,
`archetype`, `mode` et plus tard `modifiers`.

La seed est dérivée en sous-flux nommés, stables et indépendants :
`macro`, `starts`, `mountains`, `biomes`, `lakes`, `rivers`, `height`,
`resources`, `objects`. Modifier une couche ne doit pas modifier les tirages
des autres couches.

Le résultat contient la `MapState`, le journal des sous-flux, les métriques de
forme et les résultats des validateurs. Une même requête donne les mêmes
octets ; deux seeds ne sont considérées diverses qu'après comparaison de leurs
masques macro-géographiques canonisés par symétries.

## Découpage source adopté

```text
generation/
  core/                         # contrats et algorithmes neutres
  archetypes/                   # catalogue des macro-topologies et capacités
  generators/
    legacy/                     # moteur Legacy actuel (Continental en premier)
```

Les archétypes et les moteurs sont deux axes distincts : un archétype décrit
la macro-géographie et son catalogue, tandis qu'un moteur porte le cycle de
génération, le contenu, les règles et l'équilibrage d'un mode. Un moteur ne
doit donc pas contenir un sous-arbre reproduisant tous les archétypes. Le
moteur Legacy actuel implémente l'archétype Continental ; un futur moteur
Upgraded aura son propre paquet frère sous `generators/`, sans copier le
catalogue `archetypes/`.

Chaque moteur concret porte ses propres modules de cycle de vie (`macro`,
`terrain`, `height`, `starts`, `content`, `validators` et `generator`). `core`
reste sans connaissance d'un archétype ou d'un mode. Une primitive réellement
neutre va dans `core/`; une règle ou une identité d'archétype va dans
`archetypes/`; une politique de contenu ou d'équilibrage reste dans le moteur
qui l'exécute.

## Ordre du pipeline des générateurs

L'ordre ci-dessous est le workflow de référence pour **chaque générateur**.
Les générateurs restent des implémentations séparées (Legacy, Upgraded et
futurs archétypes) ; chacun peut activer ou paramétrer ses familles, mais ne
doit pas réordonner arbitrairement ces phases sans justification documentée.

1. **Océan initial** : remplir la carte d'eau, avec des bordures valides et
   non franchissables.
2. **Continent** : ouvrir une masse continentale irrégulière, entièrement
   entourée d'eau ; la côte ne doit jamais être coupée par une limite droite.
3. **Starts** : placer les joueurs sur la géographie exploitable et réserver
   leurs zones immédiates. Les terrains suivants évitent ces réservations sans
   imposer un hexagone d'interdiction excessif.
4. **Montagnes puis neige** : poser les massifs, puis la neige issue des
   sommets/altitudes compatibles. Après cette phase, aucune zone nouvelle ne
   peut recouvrir une autre famille ni y laisser de trou.
5. **Lacs et rivières** : créer les lacs, puis tracer les rivières HEX6 vers
   un lac ou l'océan. Les deux respectent les masques déjà occupés et leurs
   règles de transitions ; aucune eau parasite ne doit être introduite dans
   un massif ou une zone incompatible.
6. **Marais** : placer les zones de marais uniquement sur les cellules encore
   compatibles, sans trouer les familles précédentes.
7. **Autres terrains activés** : désert, boue, herbe sèche et toute autre
   famille du profil, dans les espaces restants et avec leurs transitions
   légales.
8. **Objets de ressources** : arbres, pierres de construction et autres
   objets nécessaires aux ressources ; leurs empreintes complètes sont
   réservées et validées.
9. **Objets décoratifs** : ajouter les décorations après les ressources, sans
   modifier les masques de terrain ni les halos réservés.
10. **Poissons et minerais** : placer les ressources finales après tous les
    objets, avec leurs contraintes de côte, de rivière, de relief et de stock.

### Contrat d'occupation et de transitions

Chaque phase terrain reçoit le masque d'occupation produit par les phases
précédentes et ne peut écrire que sur des cellules explicitement compatibles.
Une nouvelle zone ne peut donc ni remplacer silencieusement une famille
existante, ni créer de trous internes, ni laisser une transition illégale sur
son contour. Les bandes de transition et la shore/bathymétrie sont des
cellules produites intentionnellement par la phase concernée, pas des
corrections visuelles a posteriori.

Les phases d'objets et de ressources ne doivent commencer qu'une fois les
terrains, leurs formes et leurs transitions validés. Cette séparation est
obligatoire pour permettre d'affiner la géométrie sans masquer ses erreurs.

## Échelle et validation

Le moteur accepte dès sa première version les tailles natives 384, 448, 512,
576, 640, 704 et 768, avec leurs limites de joueurs. Les règles physiques
absolues restent absolues lorsqu'elles sont liées au jeu (marge océanique,
bandes de poisson, halos, tailles de blobs) ; les nombres de systèmes et les
quotas suivent les distributions natives par taille.

L'implémentation est calibrée initialement contre 768, mais n'est pas
considérée fonctionnelle avant une matrice multi-seeds sur toutes les tailles,
au moins faible densité, 8 joueurs si légal et maximum natif, puis tests
éditeur/jeu. Les modificateurs et les autres archétypes restent hors du
premier jalon.
