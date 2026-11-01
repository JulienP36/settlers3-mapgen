# DEV11 R1 — audit des surfaces (14 octobre 2026)

Le placement respecte ses supports, mais toutes les quantités globales ne
sont pas exprimées en densités de ces supports. Aucun recalibrage dans R1 :
les données mesurées ne montrent pas une saturation justifiant une correction
urgente, et changer les quotas modifierait l’économie des cartes validées.

## Contrat observé dans le code

| Famille | Base quantitative actuelle | Adaptation à la géographie |
|---|---|---|
| Minerais Amélioré/Custom | Proportion du support montagneux admissible, hors réservations bonus | Oui ; zones et stocks suivent le support |
| Poissons Amélioré/Custom | Pourcentage des candidats eau ou bande côtière | Oui ; exclut rivières/bords et réservations bonus |
| Terrains secondaires | Tentatives de pinceau natives proportionnelles à la surface totale | Homogénéité du support et expansion contrôlées ; pas un quota exact d’herbe |
| Arbres et pousses globaux | Quota 768 multiplié par (taille/768)², puis réglage Custom | Placement sur herbe admissible, collisions/marges ; densité par herbe variable |
| Palmiers | Quota 768 multiplié par (taille/768)² | Support désert effectif ; quota peut manquer si désert insuffisant |
| Pierres de construction globales | Quota 768 multiplié par (taille/768)² | Support herbe, empreinte et collisions ; bonus séparés |
| Décors globaux | Quotas familiaux calibrés 768 puis surface totale et réglage Custom | Supports par famille et collisions ; manque consigné |
| Récifs | Quota par taille plafonné aux candidats eau profonde | Ce plafond masque le manque par rapport au quota brut dans le diagnostic |

Le mode Classique conserve exactement ses routines natives. Cet audit ne
transforme pas ses tentatives ou ressources en quotas Amélioré. Les bonus de
départ restent hors quotas globaux : ne pas multiplier leur dotation par la
proportion terre/eau. Le nombre de joueurs et les réservations réduisent aussi
l’espace accessible aux objets ; un simple dénominateur « terre totale » ne
représenterait pas leur capacité de placement réelle.

Sources : `generation/generators/upgraded/content.py` (`_scaled_target`,
`_generate_minerals`, `_generate_fish`, `_place_trees`, `_place_decorations`,
`_place_building_stones`), `generation/custom/content.py` (`_place_custom_fish`),
`generation/custom/terrain.py` et `generation/generators/upgraded/native_terrain.py`
(`_brush`, `_apply_family_plan`). Lecture des références IDs/transitions/ressources
et proximité native ; les observations SAV historiques ne sont pas des garanties
pour toutes tailles ou toutes compositions.

## Mesures

12 cartes Amélioré : deux seeds (42,2026101010), deux formats (384/4P,768/12P),
trois géographies. Îles par équipe : deux équipes égales, labels alternés 1/2.
Réglages par défaut, aucune autre modification. Tous les départs et tous les
contrôles bloquants passent. Arbres adultes globaux et pierres globales atteignent
leur quota sur les 12 cartes ; aucun manque de décor consigné sur ces cas.
Les récifs utilisent déjà un quota plafonné : ce constat ne certifie pas le quota
brut de récifs. Les densités ci-dessous divisent les arbres globaux par la famille
herbe finale, avant exclusion des obstacles et des halos : indicateur comparable,
**pas** densité exacte du support libre au moment du placement.

| Taille | Seed | Géographie | Herbe finale | Arbres globaux | Arbres /1000 herbe | Pierres globales |
|---:|---:|---|---:|---:|---:|---:|
| 384 | 42 | Continental | 70480 | 684 | 9.7 | 421 |
| 384 | 42 | Îles individuelles | 63781 | 684 | 10.72 | 421 |
| 384 | 42 | Îles par équipe | 65131 | 684 | 10.5 | 421 |
| 384 | 2026101010 | Continental | 74299 | 684 | 9.21 | 421 |
| 384 | 2026101010 | Îles individuelles | 60824 | 684 | 11.25 | 421 |
| 384 | 2026101010 | Îles par équipe | 65415 | 684 | 10.46 | 421 |
| 768 | 42 | Continental | 342069 | 2736 | 8.0 | 1683 |
| 768 | 42 | Îles individuelles | 246424 | 2736 | 11.1 | 1683 |
| 768 | 42 | Îles par équipe | 293826 | 2736 | 9.31 | 1683 |
| 768 | 2026101010 | Continental | 342124 | 2736 | 8.0 | 1683 |
| 768 | 2026101010 | Îles individuelles | 245415 | 2736 | 11.15 | 1683 |
| 768 | 2026101010 | Îles par équipe | 295932 | 2736 | 9.25 | 1683 |

En 768, les îles individuelles ont environ **39 % de densité d’arbres globale
en plus par herbe** que le Continental de même seed ; deux grandes îles d’équipe
en ont environ 16 %. Les dotations globales égales ne constituent pas une
illégalité de placement. Elles créent toutefois une densité économique différente.

Suite possible, à cadrer : densités par support libre ou par famille géographique,
avec référence explicite, paramètres Custom lisibles et bonus inchangés. Choisir
la normalisation nécessite de décider si l’objectif est une densité comparable
ou un stock comparable par joueur ; les deux ne sont pas équivalents. Aucun
correctif silencieux et aucun contrôle supplémentaire ajoutés dans R1.

Limites : campagne restreinte, ni mode Custom extrême, ni toutes les tailles,
ni garantie sur tout seed. Vérification du modèle native/Custom par lecture
et suite de régression, pas nouvelle qualification en jeu du Classic.
Données et script reproductible : références `dev_notes/DEV11_R1_QUALIFICATION/`.

## Brainstorm engagé — 14 octobre2026 (propositions, sans code)

Julien accepte le cadrage des quotas ; aucune stratégie de recalibrage encore
validée. Piste privilégiée : quotas globaux d’objets en densités sur leurs
terrains compatibles, comptés avant pose des objets pour éviter une dépendance
à l’ordre des familles. Référence de densité explicite à choisir ; conserver
les réglages Custom compréhensibles et les bonus par joueur séparés.
Classique reste natif ; poissons/minerais ne changent pas sans problème mesuré.
Terrains secondaires : distinguer quota obtenu et budget de tentatives. Les
sondages répartis sur la carte et leur refus sur support incompatible peuvent
déjà adapter la fréquence au support ; une seconde réduction peut doubler
l’effet. À mesurer avant toute transposition de la règle des objets.
Compromis à décider : densité comparable ou stock total comparable par joueur ;
moins de terrain avec une densité constante donne moins de stock global.

## Recherche approfondie — 14 octobre2026

Origine corrigée : demande utilisateur du20 septembre, DEV8 autour deR29/R30,
reprise dans des TODO ultérieurs. L’Archétype définit la macroforme ; le Générateur
adapte son contenu au terrain réellement disponible. Le calibrage d’une densité
constante est une proposition actuelle, pas une décision de l’époque.

### Routines à distinguer

Les passes natives de terrains et objets travaillent par tentatives, distribuées
sur la carte, puis refus sur support, voisinage et occupation. L’espérance des
acceptations suit donc déjà le support rencontré. Ne pas leur appliquer une
seconde réduction globale de tentatives proportionnelle au support. Cela
conserve en particulier le mode Classique natif. La croissance, l’érosion et la
fragmentation du support empêchent de promettre une proportion finale exacte.

Les objets globaux Amélioré utilisent des objectifs de quantité après recherche
de candidats compatibles. Les remplacements d’objets Custom basés sur Legacy
utilisent également des quantités calibrées par taille ; ce sont les routes à
revoir. Le commentaire de `_replace_legacy_decorations` suggère une base native
observée, mais `apply_custom_objects` remplace la base absente d’une famille
désactivée par un quota768 × (taille/768)². Ne pas conclure depuis le commentaire
seul que cette route adapte déjà sa base à la surface.

### Mesures des supports exacts

12 générations instrumentées sans changer le résultat des routines :
384/4P/seed42 et768/12P/seeds42,2026101010 ; Continental, Îles individuelles,
Îles par équipe à deux groupes égaux et à un groupe unique. Les12 cartes ont
leurs starts complets et aucun contrôle bloquant échoué. Arbres et pierres
atteignent leurs quotas globaux. Supports capturés au début de la passe d’arbres.
Dans ces presets, seuls les terrains16 sont supports des arbres ordinaires,
pas toute la famille herbe : l’option d’élargissement reste désactivée.

| 768/12P, seed42 | Support herbe autorisé hors réservations | Arbres globaux | Arbres /1000 support |
|---|---:|---:|---:|
| Continental |319378|2736|8,567|
| Îles individuelles |229681|2736|11,912|
| Deux équipes |271286|2736|10,085|
| Une équipe |328072|2736|8,340|

Les réservations comptées sont celles renvoyées par `_content_core` à ce stade.
Elles ne constituent pas un inventaire exact des ancres libres après toutes
les collisions et placements futurs. Les capacités de placement et les quotas
souhaités doivent rester deux notions séparées.

### Expérience contrôlée des pinceaux

Grille synthétique512, bandes compatibles de25/50/100%,32 seeds0..31,
coefficient de pinceau8, une seule passe sans expansion/érosion. Pas de carte
exportée ni d’image produite. Les moyennes portent sur les amorces écrites,
pas les surfaces finales des familles après toutes les opérations natives.

| Part de support | Budget natif conservé | Budget lui aussi réduit par le support |
|---|---:|---:|
|25%|110,47|29,13|
|50%|234,28|119,25|
|100%|478,84|478,84|

Le budget conservé s’adapte déjà par refus. La seconde multiplication diminue
à nouveau la présence des terrains : raison mesurée de ne pas la généraliser.

### Custom Legacy : base de quantité et défaut de familles

384/4P/seed42, mêmes réglages hors variable explicitement changée :

| Carte | Arbres natifs par défaut | Arbres après quota Custom150% |
|---|---:|---:|
| Continental |544|1026|
| Îles individuelles |320|1026|

150% est appliqué au quota calibré de684 (2736/4), et non au résultat natif du
seed. Il faut une référence explicite pour rendre le futur pourcentage cohérent.

Défaut confirmé distinct : en Custom/Legacy, Continental384/4P/seed42, modifier
seulement cactus100→150 désactive toute la catégorie native « decorations ».
La passe Custom ne reconstruit que les familles considérées modifiées. Résultat :
49 grosses pierres décoratives,25 fleurs,34 buissons, etc. deviennent0, bien que
leurs taux restent100%. Cactus3→9. Les arbres et pierres de construction restent
présents ; leur PRNG peut changer lorsque d’autres appels natifs sont sautés.
Les contrôles bloquants actuels ne détectent pas la disparition de ces familles.
Fix à réaliser : désactivation/remplacement à la granularité des sous-familles
concernées et conservation des familles non modifiées. Aucun correctif de code
appliqué pendant cette recherche.

### Stratégie proposée et impact illustratif

1. Corriger la perte des familles de décor non modifiées en Custom/Legacy.
2. Pour les passes à quota, compter une fois leurs supports terrain compatibles,
   avec les réservations fixes connues, avant les objets globaux. Ne pas recalculer
   le quota selon les objets placés par les familles précédentes. Comptage de
   capacité/empreinte/collision au placement séparé, avec diagnostics de manque.
3. Cible = densité de référence × support retenu × pourcentageCustom/100.
   Ne pas multiplier une nouvelle fois par (taille/768)². Les forêts et groupes
   répartissent la cible ; ils ne la multiplient pas. Séparation des adultes et
   pousses et options de pool conservées. Bonus par joueur et moyennes de stock
   distincts et conservés. Pour pierres, normaliser ancres puis stocks avec leurs
   quantités ; ne pas garder un stock total fixe après réduction des ancres.
4. Calibrer chaque famille sur ses propres supports, avec une référence déclarée.
   Ne pas utiliser toute la terre pour cactus/palmiers/roseaux/récifs. Une rare
   famille ne doit pas disparaître systématiquement par arrondi : règle à définir.
5. Actualiser l’« Aperçu estimé » des pierres, qui calcule encore quota768 ×
   surface carte. Une projection de macroforme ne donne pas les supports exacts
   du terrain secondaire : distinguer estimation et quantité calculée sur une
   vraie carte, sans réutiliser silencieusement le support d’un autre seed.

Illustration uniquement, non recalibrage actif : moyenne des supports hors
réservations des deux Continental768/12P =319046,5 cases ;2736 arbres donnent
8,57555 arbres/1000 cases. Avec cette densité, les cibles seraient environ2739
sur Continental/seed42,1970 sur Îles individuelles,2326 sur deux équipes et2813
sur une équipe. En384/4P/seed42, Continental passerait de684 à563. Ce dernier
écart est un choix économique réel, à valider ; deux seeds ne suffisent pas
à fixer définitivement une référence de production. Les valeurs de pierres
calculées dans le JSON sur le même masque ne sont qu’une illustration, pas une
prédiction : leur support admissible doit tenir compte de l’empreinte propre.

Décisions restantes : référence de densité finale, invariance entre tailles ou
conservation des dotations usuelles par taille, arrondi des petites familles,
et formulation des estimations UI. La recherche ne change aucun preset, code,
asset, format ou quota et ne produit pas de candidate fonctionnelleR2.

Contrôle de non-interférence : Continental384/4P/seed42 généré avec et sans
l’instrumentation ; Area, starts, journal et validations identiques. Ce contrôle
ne constitue pas une nouvelle qualification Windows ou une modification native.

Les preuves annexes de cette recherche historique ne sont pas récupérables
dans l’archive R1 tronquée. Les résultats ci-dessus restent un compte rendu
historique ; les preuves R2 nouvelles sont livrées séparément ci-dessous.


## Implémentation DEV11 R2 — 14 octobre 2026

Le feu vert de Julien couvre le remplacement par densité des quotas globaux
Amélioré et Custom, la conservation des décors inchangés et les estimations UI.
Il ne couvre aucun nouvel algorithme de départs par équipes.

### Contrat actif

`N = N0 × S / S0 × taux/100`, sans second multiplicateur de taille.
`S` compte les terrains compatibles hors réservations fixes et bord, une seule
fois avant les objets globaux. Il ignore les objets déjà présents ; empreintes,
collisions, distances et saturation restent contrôlées séparément au placement.
Les contraintes de proximité des forêts/groupes peuvent donc créer des manques,
qui ne sont pas compensés en augmentant le quota ou la richesse des pierres.
Les objets posés restent soumis aux supports légaux précédemment définis.

Référence fixe : médiane par ID de cinq Continental768/12P R1, seeds42,
2026101010,2026101011,984499091,1241516019. `object_quotas.py` contient ces valeurs.
Herbe16 :305350 ; plage48 :17408 ; désert64 :12983 ; marais80 :101 ; eau7 :66023.
Les supports multi-ID additionnent ces références. L’extension herbe sèche et
 détails ajoute les supports actuels en conservant la référence herbe16.
Le choix garde les quotas de profil comme dotations du Continental de référence,
avec une densité stable entre tailles ; il ne garantit pas les anciens quotas
sur chaque terrain, taille ou seed. Les valeurs historiques illustratives de
1970 arbres ne sont pas la nouvelle calibration : Îles individuelles768/12P/
seed42 demande et place2058 adultes ; Continental2862 ; deux équipes2431.

Arrondi : plancher plus tirage fractionnaire déterministe SHA-256 par seed et
famille, sans minimum forcé et sans consommation du PRNG natif. La famille rare
peut légitimement demander zéro sur un terrain très pauvre en supports.
Bonus par joueur, budgets de tentatives natifs, terrain secondaire et rivières
restent séparés et inchangés. Les arbres/pousses gardent leurs règles de pool ;
les forêts/groupes répartissent le quota. Le stock des pierres suit les ancres
actives réellement placées et la moyenne réglée, y compris en cas de saturation.

Custom/Legacy désactive dans la passe native seulement les IDs des familles
modifiées ; les autres décors conservent leurs règles natives. Les positions
peuvent varier lorsqu’on saute certains appels du PRNG. En Classique par défaut,
aucun ID désactivé : mêmes octets, starts et contrôles sur quatre cas comparés R1/R2.

L’aperçu des pierres indique soit le support figé d’une génération dont les
paramètres géographiques, seed, taille, joueurs, équipes, nations, miroirs et
placement correspondent, soit une référence continentale explicitement estimée.
Modifier seulement les quotas globaux peut réutiliser le support ; une carte
importée ou un changement géographique ne réemploie pas un support obsolète.
Les stocks affichés restent des estimations : saturation et nombre aléatoire
de pierres épuisées peuvent faire varier le placement et le stock réels.

### Qualification et provenance

12 générations Amélioré :384/4P et768/12P, seeds42 et2026101010, Continental,
Îles individuelles et Îles par équipe avec deux équipes égales. Tous les starts
et contrôles bloquants passent. 24 exports EDM/MAP relus et checksums contrôlés.
Comparaison Classique R1/R2 : quatre cartes384/4P identiques octet par octet.
Interface Tk sous Xvfb :57 contrôles Custom/Tcl,1 desktop quatre langues/deux
thèmes/trois tailles et3 messages passent. Aucun essai Windows/éditeur/jeu R2
revendiqué. Résultats de régression consolidés : notes de candidate.

Preuves R2 : `references/dev_notes/DEV11_R2_QUALIFICATION/` contient calibration,
campagne, parité native, scripts et résultats. Les scripts s’exécutent depuis la
racine source avec `PYTHONPATH=.` ; les chemins Xvfb sont propres à cet environnement.
`calibrate.py` doit viser R1 pour reproduire la référence historique exacte.
Archive R1 récupérée :837 entrées locales ZIP vérifiées par CRC/taille, tous les
156 modules applicatifs disponibles. La fin de l’archive est manquante ; les
fichiers de baseline manquants viennent de Git origin/dev823c8f0. Le test R1 des
équipes a été reconstitué depuis le contrat testé, puis requalifié. La référence
R2 ne présente pas ces données récupérées comme un ZIP R1 complet.

## Option DEV11 R3 — validée comme choix le16 octobre2026

La calibration R2 est conservée ; Julien trouve les taux satisfaisants. La case
`objects.terrain_scaled_quotas` est ON par défaut, y compris anciens profils.
OFF : N0×(taille/768)²×taux/100, arrondi usuel, sans prorata des supports. Les
supports légaux, empreintes, collisions et manques restent contrôlés. Les stocks
de pierres suivent toujours les ancres actives posées ; aucun rétablissement de
l’ancien stock total fixe. Les bonus par joueur et les passes natives restent
indépendants. La case se trouve au-dessus des sections du générateur et se
sauvegarde avec le profil Custom ; Réinitialiser le Custom restaure ON.
L’aperçu des pierres distingue explicitement base surface totale et support.

## Diagnostic et correction R4 — 17 octobre2026

Julien confirme avoir testé sur base Classique. La case OFF seule ne déclenchait
aucun remplacement à100% : `semantic_object_changes` ne comparait que les taux
et l’extension d’herbe. R3 mesuré384/4P/seed42 : case ON/OFF donne544 adultes sur
Continental,320 sur Îles individuelles et342 sur deux îles d’équipe, sans changer
les octets. En Amélioré, la case fonctionnait déjà (exemple Îles individuelles :
533→684 adultes et328→421 pierres).

R4 : OFF est une demande explicite de remplacement de toutes les familles par
les quotas de surface carte. Les familles de décor sont désactivées en natif
avant leur reconstruction, y compris celles restées à100%. ON conserve les
familles natives inchangées ; les familles encore personnalisées suivent leur
taux et les supports. Aucun changement du Classique par défaut. Les bonus sont
séparés. Un profil Custom entièrement matérialisé peut déjà personnaliser les
ressources à100% selon le contrat préexistant : la vérification de retour ON
porte sur les objets, le terrain, le relief et les starts, sans prétendre que
recocher seul équivaut au reset intégral de tous les paramètres Custom.

Essai réel GUI R4,384/4P/Îles individuelles/seed42 : bouton Générer, bascule de
la case seule, second Générer ;320→684 adultes, nouvelle clé de cache, contrôles
bloquants PASS. Source R3 et hashes protégés vérifiés. Preuves dans
`references/dev_notes/DEV11_R4_QUALIFICATION/`.

Validation Julien du 18 octobre 2026 : case de prorata fonctionnelle, quotas
meilleurs. Cette validation porte sur ses essais, sans campagne exhaustive
utilisateur revendiquée.
