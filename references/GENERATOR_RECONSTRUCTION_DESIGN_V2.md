# Reconstruction du générateur — conception v2

> Document de conception pour le portage fidèle du générateur Legacy natif.
> Le chemin procédural DEV_1 a été retiré ; les références historiques restent
> disponibles uniquement pour comparaison.

## Diagnostic historique établi le 28 août 2026

Cette section décrit le chemin de compatibilité v1.5 mesuré avant le portage
Legacy natif ; elle ne décrit pas la morphologie générée par le moteur actif
DEV_2.

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

Définir deux axes explicites et indépendants :

- `Continental v1` : archétype, macro-forme et contexte géographique ;
- `Legacy v1` : moteur de génération natif, avec terrain, objets, ressources,
  départs, entités et finalisation dans l'ordre du binaire.

Le chemin `Upgraded` reste un moteur de compatibilité distinct et validé ; il
ne doit pas être fusionné avec le portage Legacy.

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

Un prototype de macro-forme fondé uniquement sur du bruit et l'ancien pipeline
Legacy DEV_1 ont été volontairement retirés : ils produisaient des cartes
plausibles, mais ne portaient pas l'algorithme natif. Le corpus brut reste
nécessaire pour la validation de sortie ; le premier portage du noyau est
désormais présent dans le moteur legacy natif.

## Calibration de la côte — 29 août 2026

La bibliothèque de silhouettes littorales et le chemin de déformation du
Legacy DEV_1 sont historiques et ne font plus partie du moteur actif. Pour le
portage natif, `Continental v1` doit fournir le contexte attendu par
`Legacy v1`; il ne faut pas réinjecter une banque de formes dérivées à la place
des ancres et raffinements de `0x5166D0`.

## Contrat d'exécution

Une requête de génération contient au minimum : `side`, `players`, `seed`,
`archetype`, `mode` et plus tard `modifiers`.

Pour le mode exact Legacy, la seed n'est pas dérivée en sous-flux indépendants
par famille : le binaire consomme son PRNG commun dans le noyau terrain puis
le réinitialise avant les couches de partie. L'application peut journaliser
des sous-étapes, mais ne doit pas changer cette consommation native dans le
portage de fidélité.

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
  facade.py                     # dispatch Legacy/Upgraded sans mélanger leurs règles
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

## Ordre du pipeline : contrat séparé et ordre natif observé

L'ancien ordre générique de ce document est retiré : il plaçait les départs et
les lacs à des endroits qui ne sont pas démontrés par `S3.EXE`. Il faut
séparer l'architecture cible de l'ordre d'exécution réellement observé.

### Contrat des deux composants

| Composant | Responsabilité |
|---|---|
| `Continental v1` | fournit la macro-forme et le contexte géographique attendus par le moteur ; il ne recode ni les starts ni les minerais |
| `Legacy v1` | porte le pipeline natif, son PRNG, ses tables et ses sorties terrain/runtime |

Le moteur `Legacy v1` reste utilisable avec un contexte continental v1, mais
`Continental v1` ne doit pas lui appliquer une seconde sculpture de continent.
Les couches de format/export sont des adaptateurs après le résultat du moteur ;
elles ne doivent pas être confondues avec une phase de génération.

### Ordre natif démontré pour une nouvelle carte

1. **Initialisation du contexte monde** : création de la grille runtime et de
   la banque d'offsets hexagonaux `0x516530` (origine + `3333×6` offsets,
   métrique et anneaux exacts documentés dans les audits).
2. **Noyau aléatoire `0x5166D0`** : initialisation du PRNG, relief par ancres et
   raffinements, sculpture conditionnée par le mode, classification des
   surfaces, rivières, rives/transitions, désert/marais/boue/herbe sèche,
   micro-terrains et copies finales de mode.
3. **Objets et ressources directement écrits par le noyau** : les appels
   `0x51B010/0x51B1A0` posent les objets statiques, puis `0x51AD40` pose les
   ressources de sol dans l'ordre soufre, gemmes, or, fer, charbon ;
   `0x518A08` pose ensuite les poissons.
4. **Re-seed de partie** : l'orchestrateur retire la configuration type 5,
   puis réinitialise le même PRNG à partir de la valeur globale lue par
   `0x437050 -> 0x4FEB40`.
5. **Départs** : `0x5074B0` parcourt les slots actifs, tire ou cherche les
   coordonnées, applique la séparation, les miroirs, l'empreinte
   `0x4D99E0` et le filtre de qualité relâché ; il appelle `0x506CF0` pour
   chaque point accepté.
6. **Ville, entités et stock initial** : `0x506CF0` crée le noyau de ville,
   les lots `0x50CB20`, puis les records type 9 via `0x5046B0` et le registre
   `0x504420`. Les listes de types/valeurs dépendent de la branche
   `0x412300` et restent conservées comme tables natives.
7. **Finalisation runtime** : `0x4FD540` traite les records non-terrain
   éventuellement présents, puis `0x4FD020` construit les index et masques
   auxiliaires. Sur une carte chargée, le chemin commence au contraire par
   `0x508FA0` et `0x4FD540` matérialise conditionnellement l'Area/type 6,
   les bâtiments, les colons et les records sérialisés.

Il n'existe donc pas, dans le chemin aléatoire démontré, de phase de starts
avant le terrain, de passe type 8 cachée dans `0x5166D0`, ni de subdivision en
chunks de carte. Les rivières et les familles de surfaces sont des phases
internes du noyau terrain ; les départs appartiennent à l'orchestrateur qui
suit le re-seed.

### Contrat d'occupation et de transitions

Le portage doit respecter les prédicats écrits par le binaire : voisinage
HEX6, familles/chaînes de transition, empreintes de sept cellules ou de
motifs, flags d'accès et absence d'écrasement là où le helper le refuse. Les
tables opaques restent des données natives ; aucune règle visuelle de
remplacement ne doit être ajoutée pour combler un manque de nom métier.

## Échelle et validation

Le moteur accepte dès cette version les tailles `256, 320, 384, 448, 512, 576,
640, 704, 768, 832, 896, 960 et 1024`, avec leurs limites de joueurs. Les
tailles sous 384 et au-dessus de 768 restent générables pour les éditeurs
compatibles ; l'application les signale comme candidates de viabilité, sans
les bloquer. Les règles physiques absolues restent absolues lorsqu'elles sont
liées au jeu (marge océanique, bandes de poisson, halos, tailles de blobs) ;
les nombres de systèmes et les quotas suivent les distributions natives par
taille lorsque le profil les fournit.

Le portage est calibré initialement contre 768 et exerce également les tailles
du contrat natif en mémoire. Il n'est pas considéré homologué avant une matrice
multi-seeds sur toutes les tailles, au moins faible densité, 8 joueurs si légal
et maximum natif, puis tests éditeur/jeu. Les modificateurs et les autres
archétypes restent hors du premier jalon.
