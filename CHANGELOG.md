# Changelog

## v1.5 — Legacy/Upgraded audit + start clusters + resource-state fixes — VALIDÉE
- Séparation conceptuelle puis implémentée entre **Legacy** et **Upgraded** : Legacy reste native-like hors correctifs de stabilité/validité ; Upgraded part de cette base et ajoute uniquement les améliorations explicitement validées.
- Morphologie macro commune par archétype ; starts toujours placés très tôt et protégés contre les passes suivantes.
- Hydrologie : Legacy conserve les petits étangs/rivières natives ; Upgraded supprime/redistribue les plans d'eau de 1–4 cellules et applique un trimming de rivière calibré par taille (`~0.0245*side + 34.7`).
- Neige commune Legacy/Upgraded, avec chaîne validée `Rocky32 -> 35 -> 129 -> Snow128`; Terrain34 reste une variante Rocky interne rare et minéralisable.
- **Minerais Upgraded : géométrie v7 no-gap canonique restaurée et revalidée visuellement**. Blobs pleins, compacts, légèrement ovoïdes, tailles lognormales calibrées, aucun trou/singleton/moat forcé, fusion naturelle autorisée.
- Minerais Upgraded : cible ~90 % du support montagneux, ratios empiriques natifs, quantité/case +30 % cap15, minerai sous Snow et Terrain34 valide ; Legacy conserve son comportement séparé native-like.
- Arbres : pool natif complet `68..77 + 80..81` dans les deux modes ; Palms `78..79` comptées comme bois récoltable. Upgraded utilise ~130 % du volume natif complet + SmallTree84 séparé.
- Mud conservé en Legacy, désactivé en Upgraded. Terrain24 conservé en Legacy et différé en Upgraded pour une passe isolée ultérieure.
- Swamp Upgraded ~+30 % global avec protection HEX6 ; Reeds restent natifs dans les deux modes.
- Decorative Stones : densité native Legacy, environ ÷10 Upgraded ; Reefs : Legacy 0, Upgraded rares et à au moins 2 cellules des bords.
- **Bonus de départ Upgraded** : forêt `41 adultes + 21 SmallTree84` par joueur ; tas de pierre `8 ancres / 84 unités`, centrés sur la bordure du territoire initial (~HEX34). Validation visuelle obtenue.
- Building Stones globales : états `115..127` variés, Upgraded biaisé vers les états plus pleins ; répartition visuelle validée.
- Building Stone 13 / ID127 : ~20 ancres globales sur 768, 0 stock, exclues du stock exploitable ; footprint statique libéré (`accessibility=0`).
- Validators v1.5 : quotas arbres/SmallTree84/Palms, ancres/stock/variété/ID127, constructibilité statique ID127, récifs, starts, hydrologie, minerais, poissons et transitions.
- Goods Default verrouillé : Legacy=Medium (`2`), Upgraded=High (`3`).
- Runtime final `generator_v15.py`; GUI/CLI/exports nommés v1.5.
- Référence validée : `S3_V1_5_V7NOGAP_CORRECTED_UPGRADED_4P_768x768_seed_2026082202`.
- L'ancienne candidate `seed_2026082201` est invalidée pour ses formes de minerais.
- **Validation finale utilisateur** : ouverture éditeur OK, starts OK, View Map/in-game sans crash, rendu général validé. Le test pratique ID127 est différé sur micro-map et n'est pas bloquant.
- **Statut : v1.5 VALIDÉE / STABLE.**

## v1.4 — dark mode / visualization comfort — VALIDÉE
- Nouveau thème **Sombre / Clair**, sombre par défaut, configurable dans un nouvel onglet `Paramètres`.
- Préférences d'affichage persistées dans le profil utilisateur Windows (`APPDATA/Settlers3MapGen/settings.json`).
- Listes déroulantes corrigées en thème sombre : fond sombre et texte clair, aussi bien fermées qu'ouvertes.
- Slider d'opacité pour Heightmap / Ressources / Territoires afin de superposer les couches à la map globale.
- Les sliders Zoom / Opacité / Sensibilité molette se positionnent directement à l'endroit cliqué sur leur barre.
- Projection optionnelle **Parallélogramme** pour rapprocher la visualisation de la géométrie affichée en jeu, sans modifier les données de map.
- Projection parallélogramme recalée sur un décalage de **0,5 cellule par ligne**.
- Navigation : drag de la carte dans le canvas.
- Zoom molette : recalcul temporisé + cache de la couche de base pour réduire la latence ; sensibilité réglable.
- Barre de progression : génération + import + export + aperçu PNG ; état terminé bleu puis disparition automatique, erreur rouge.
- Les aperçus exportés respectent maintenant la vue, l'opacité et la projection sélectionnées.
- Starts : ajout d'un contour non rempli du **territoire initial**, coloré selon le joueur et dimensionné d'après les SAV natifs : 3500 cellules, étendue ±35 cellules.
- Le territoire initial est un vrai cercle dans la géométrie parallélogramme et apparaît donc déformé/incliné en vue carrée.
- Marqueurs `P1` à `P20` : couleur du joueur et rendu bitmap net, sans anti-aliasing, cohérent avec le pixel art de la map.
- En projection parallélogramme, les textes `P1` à `P20` sont ajoutés après projection et restent donc droits / non déformés.
- Palette joueur unifiée avec la vue Territoires pour conserver la même correspondance de couleurs.
- Tests ajoutés / adaptés pour les préférences, le blend d'opacité, la projection parallélogramme et les marqueurs de starts.
- Validation visuelle utilisateur finale : cercle territoire et combobox sombre contrôlés OK ; v1.4 promue hors statut candidate.
- **Correctif Goods Default validé** : le 3e DWORD de Map Info n'est plus écrit comme `player_count - 1` ; il encode désormais un preset valide (`Legacy=Medium/2`, `Upgraded=High/3`, fallback Medium).
- Validation en jeu du correctif Goods Default sur deux générations fraîches v1.4 4P : réglages Medium/High visibles dans `Edit Map Settings` et aucun crash au démarrage avec `Défaut`.
- **Morphologie Upgraded indépendante : première candidate validée** (`seed 2026081908`, Continental 768×768 4P). Géographie jugée excellente, starts OK, aucun crash ; relief montagneux vérifié conforme à la référence native 768/4P source.

## v1.3.2 — editor-safe starts / snow blocking / swamp transitions — VALIDÉE
- Validation utilisateur sur **4 générations Continental 768×768** : Legacy 4 joueurs, Legacy 20 joueurs, Upgraded 4 joueurs et Upgraded 20 joueurs.
- Sur les 4 générations : positions de départ acceptées par l'éditeur et aucun crash lors de la vue in-game.
- Marais : correction confirmée lors des tests.
- Neige : zones intérieures désormais non traversables comme prévu.

## v1.3.1 — preview crash fix / README presentation
- Correction du crash `NameError: Image is not defined` lors de la génération/rafraîchissement de l'aperçu.
- Import explicite de `PIL.Image` utilisé par le redimensionnement/zoom.
- Ajout d'un test de non-régression dédié au rendu GUI.

## v1.3 — tooling / UX
- Ajout barre progression par étapes de pipeline.
- Bouton seed aléatoire.
- Import EDM/MAP/SAV (SAV en lecture seule).
- Vues Global / Heightmap / Ressources / Territoires.
- Zoom par slider et molette.
- Sélecteur de toutes les tailles natives + max joueurs dynamique.
