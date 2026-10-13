# Relief et tailles des îles — référence courante R63

La source Îles individuelles construit directement un relief plus bas quand la surface
par joueur devient faible. Taille et nombre de joueurs déterminent un rayon
équivalent. L’adaptation est de 50 % pour un rayon ≤60 cases, puis revient
progressivement à 100 % à partir de 100 cases. Aucun abaissement après génération.
Le nouveau Continental reprend le relief distribué de la grande masse, sans
contrat insulaire de starts. Les compositions gardent leurs réglages explicites. Les contrôles sont disponibles pour les deux sources insulaires.

Dans Archétype :
- « Adapter l’amplitude à la taille des îles » affiche l’amplitude effective.
  Décocher conserve cette valeur et rend le champ modifiable de 25 à 100 %.
- « Adapter les seuils montagne et neige » utilise la calibration de la source
  (références 140/200), compensée pour la relaxation native et la taille des îles.
  Décocher conserve les seuils effectifs et rend leurs champs modifiables.
- La ligne « Effectif » présente amplitude, montagne et neige. Taille/joueurs,
  langue, choix de source, chargement et réinitialisation actualisent les contrôles.
- Les paramètres automatiques sont conservés dans le profil ; les valeurs résolues
  sont calculées sans modifier ce profil. Les caches et les aperçus utilisent
  le même profil effectif que la génération. Les petits détails restent à leur
  réglage actuel ; l’amplitude reste distincte du contraste des compositions.

Le mode automatique est activé dans le profil Îles individuelles. Pour une composition
créée depuis un autre profil, il peut être activé explicitement. Les anciens
profils dont les seuils étaient personnalisés conservent ces seuils manuels.
Modifier l’amplitude en manuel n’implique pas une garantie de placement complet.
Fusions, masques et seuils libres peuvent toujours produire des départs incomplets.

Dans « Îles — par équipe » (R52), la calibration automatique utilise la plus
petite île effective du groupe de joueurs : une grande équipe ne force donc pas
une île individuelle minuscule à conserver un relief trop haut. Ce calcul se
retrouve dans l’aperçu de l’onglet Archétype et dans la génération ; il ne
compresse pas une heightmap après coup.

## Relief partagé, eau et lacs

Îles par équipe utilise un champ continu : aucune partition ni montagne imposée
par joueur. R57 répartit les crêtes, réduit la taille des lacs et augmente leur
nombre ; R58 fait croître les contours progressivement pour éviter les lobes
reliés par de fines plages. Peu de groupes permettent davantage de terre ;
un seul groupe se rapproche des proportions continentales. Les îles indépendantes
conservent l'espace de navigation adapté à leurs multiples masses.

Le nombre de bassins intérieurs dépend de la **surface**, pas directement des
joueurs. Pour les sources distribuées (équipes et nouveau Continental), `_inland_lake_count` prévoit un bassin par60 000
cases de terre, plafonné à huit bassins ; les emplacements légaux peuvent
réduire le résultat. Îles individuelles garde sa politique séparée :
un bassin par 125 000 cases, maximum trois. Centres à au moins 50 % de la profondeur maximale depuis
la mer, emprise à au moins 35 %, avec marges de taille. Pas de bassins littoraux
ajoutés comme substituts d'accès à l'eau.

La source Continental R60 réutilise la grande masse et ses petits lacs, sans
bonus mini-marais par défaut ; les contrôles R62 comptent 0/1/3/7 bassins source
en 256/384/512/768. Ce n'est pas un nombre garanti de composantes finales.
Calibration mer R62 : budget de contour avant relief/lacs, pas quota final.
Le départage des directions de rivières Amélioré R61 reste déterministe.

L'espacement des alliés est fortement favorisé par le solveur R59, sans
interdiction absolue des positions proches ; accès à montagne/eau reste utile.
Les graphes de distance actuels restent inchangés jusqu'à Stats 2.

Le graphique « Taille des îles » classe les vingt plus grandes masses terrestres,
comme les graphiques des massifs/lacs/rivières. Le survol cible la masse affichée.
Le calcul utilise le voisinage HEX 6 sur tout terrain hors eau 0–7 : rivages,
rivières, neige et terrains secondaires font partie des terres. Un lac intérieur
constitue un trou, pas une île ; une seule masse terrestre est un continent unique.
Les stats donnent nombre, tailles min/médiane/moyenne/max et part de la plus grande.
Les détails complets sont disponibles en JSON et les tailles en CSV. Mer seule : zéro île.

Mise à jour :13 octobre 2026. Îles par équipe validéesR 59, Continental validéR 62,
R63 validée avec défaut tooltip. Les résultats anciensR 54 sont historiques,
pas une formule actuelle des lacs. Qualification dans RELEASE_VALIDATION et
`../references/dev_notes/` ; aucune nouvelle ouverture Windows/jeu revendiquée ici.
