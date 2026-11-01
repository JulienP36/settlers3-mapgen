# Relief et tailles des îles — référence courante DEV11 R6

Chaque île individuelle ou d’équipe reçoit sa calibration propre, fondée sur
la **surface réelle du contour construit avant les lacs**. Rayon équivalent
`r = sqrt(surface / pi)` ; amplitude 50 % si r≤60, 100 % si r≥100,
interpolation smoothstep entre les deux. Taille de carte et joueurs influencent
les contours, sans servir de substitut à leur mesure. Aucune compression de la
heightmap terminée ; la calibration entre directement dans la source du relief.
Les lacs ne changent pas leur propre référence d’amplitude.

Les seuils automatiques montagne/neige suivent l’amplitude locale et la
compensation native existante (références 140/200). Les champs de seuils suivent
les labels de source et sont partagés par aperçus exact/indicatif et les deux
classifications natives. Les fusions/masques libres restent libres et peuvent
modifier la viabilité ; ils ne déclenchent pas une recalibration rétroactive.

L’onglet Archétype montre une plage effective si les îles diffèrent. Les champs
numériques grisés affichent le minimum. Décocher une adaptation reprend ce
minimum comme valeur manuelle commune, modifiable ; les profils sauvegardent
les options et les valeurs manuelles, pas les champs de seuils calculés.
Continental n’utilise aucune adaptation insulaire, y compris en chargeant un
ancien profil avec ces options héritées. Amplitude manuelle conservée, défaut
100 % et seuils 140/200 ; les cases automatiques sont désactivées sur cette source.

R6 : les valeurs effectives sont résolues par le worker d’aperçu, jamais dans
les callbacks Tk. Hors onglet Archétype, aucun nouveau calcul n’est lancé.
L’affichage indique une attente jusqu’au résultat correspondant ; les bascules
automatiques vers le manuel attendent ce minimum exact. Les résultats périmés
sont ignorés dès changement des paramètres. La calibration ne change pas.

Les îles longues et étroites restent un cas à surveiller : la surface seule ne
mesure pas la largeur utile. Pas de nouvelle règle sans cas observé.

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

## Référence terre/océan R4

Le Continental R62 avait reçu une correction du budget de terre extérieur de
0/+3/+2,25/+1,5 points en256/384/512/768, interpolés. La source Îles par équipe
utilisait encore la référence antérieure. R4 utilise la référence corrigée dans
son mélange `56,5 + (référence_continentale_corrigée − 56,5)/nombre_d’îles`.
L’ajout au budget antérieur vaut donc correction/nombre d’îles. Le budget total
reste réparti selon les effectifs des équipes ; les canaux sont construits par
le même solveur. La référence des îles individuelles et le Continental restent
inchangés. C’est un budget de source avant relief/lacs et transitions, pas une
obligation de pourcentage final.

Mesure seed42/12P/768 : une équipe79,517→81,023% de terre ; deux équipes
68,866→69,630% ; quatre équipes63,541→63,913%. Le Continental reste80,842%.
La mer, séparée des lacs par connexité aux bords HEX6, diminue respectivement de
19,610→18,111%,30,657→29,899%,36,337→35,964%. Les règles de lacs restent inchangées ;
leur nombre ou forme peut suivre naturellement la nouvelle surface.
Qualification complète et limites : ../DEV_CANDIDATE_NOTES.md.
