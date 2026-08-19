# Changelog

## v1.5 — Legacy/Upgraded audit + start clusters + resource-state fixes — CANDIDATE
- Séparation conceptuelle puis implémentée entre **Legacy** et **Upgraded** : Legacy reste native-like hors correctifs de stabilité/validité ; Upgraded part de cette base et ajoute uniquement les améliorations explicitement validées.
- Morphologie macro commune par archétype ; starts toujours placés très tôt et protégés contre les passes suivantes.
- Hydrologie : Legacy conserve les petits étangs/rivières natives ; Upgraded supprime/redistribue les plans d'eau de 1–4 cellules et applique un trimming de rivière calibré par taille (`~0.0245*side + 34.7`).
- Neige commune Legacy/Upgraded, avec chaîne validée `Rocky32 -> 35 -> 129 -> Snow128`; Terrain34 reste une variante Rocky interne rare et minéralisable.
- **Minerais Upgraded : géométrie v7 no-gap canonique restaurée et revalidée visuellement**. Les blobs élémentaires utilisent les tailles lognormales calibrées, une croissance solide légèrement ovoïde guidée par priorité elliptique, une légère irrégularité interne, aucun trou, aucun singleton et aucun moat forcé ; les blobs peuvent toucher/fusionner naturellement. L'ancienne croissance de frontière aléatoire est supprimée du runtime Upgraded v1.5.
- Minerais Upgraded : cible ~90 % du support montagneux, ratios empiriques natifs, quantité/case +30 % cap15, minerai sous Snow et Terrain34 valide ; Legacy conserve son comportement séparé native-like.
- Arbres : pool natif complet `68..77 + 80..81` dans les deux modes ; Palms `78..79` comptées comme bois récoltable. Upgraded utilise ~130 % du volume natif complet + SmallTree84 séparé.
- Désert commun natif-like : Dead Trees `43..44`, Cacti `45..48`, Skeleton `49`, Palms `78..79`.
- Petites végétations/fleurs/buissons/champignons identiques Legacy/Upgraded ; Wrecks/Grave/Stumps communs natifs.
- Mud conservé en Legacy, désactivé en Upgraded. Terrain24 conservé en Legacy et volontairement différé en Upgraded pour une passe isolée ultérieure.
- Swamp Upgraded ~+30 % global avec protection HEX6 contre les contacts incompatibles ; Reeds restent natifs dans les deux modes.
- Decorative Stones : densité native Legacy, environ ÷10 Upgraded ; Reefs : Legacy 0, Upgraded rares, navigation-safe et désormais à au moins 2 cellules des bords de map.
- **Bonus de départ Upgraded reconstruits comme de vrais clusters** centrés sur la bordure du territoire initial (~rayon HEX34) : forêt `41 adultes + 21 SmallTree84` par joueur ; tas de pierre `8 ancres / 84 unités`, états 9–12 unités/ancre. Validation visuelle utilisateur obtenue.
- Building Stones globales : suppression de l'uniformisation des états. Legacy génère une distribution variée native-like ; Upgraded une distribution variée biaisée vers les états plus pleins, avec correction fine pour atteindre exactement le stock cible. Répartition visuelle `115..127` validée.
- Building Stone 13 / ID127 est désormais générée comme dans le natif (~20 ancres globales sur 768), compte dans la densité d'ancres mais **jamais dans le stock exploitable**.
- **ID127 est constructible** : contrairement aux états actifs `115..126`, son ancien footprint 7 cellules est libéré (`accessibility=0`) avant validation/export.
- Validators v1.5 : ancres totales `115..127`, stock actif `115..126`, variété d'états, quota d'ID127, terrain légal, constructibilité de l'état épuisé et marge de bord des récifs.
- Goods Default reste verrouillé : Legacy=Medium (`2`), Upgraded=High (`3`).
- Nouveau wrapper GUI `gui_v15.py`; runtime final `generator_v15.py`; `run_gui.py` lance v1.5 et les exports sont nommés `MapGenV1_5`. CLI également mis à jour en v1.5.
- Nouvelle idée de modificateur futur **Réaliste** : distributions végétales guidées par l'environnement (plus d'arbres près de l'eau, champignons favorisés près des marais, etc.), à développer séparément sans modifier les modes de base.
- Candidate de référence actuelle pour la géométrie minière : `S3_V1_5_V7NOGAP_CORRECTED_UPGRADED_4P_768x768_seed_2026082202`. L'ancienne candidate `seed_2026082201` est explicitement invalidée pour ses formes de minerais.
- Statut : **candidate**. Les formes minières, bonus de starts et Building Stones sont validés visuellement ; dernier contrôle éditeur + View Map/in-game requis avant promotion/tag stable.

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
- La validation de cette candidate autorise la poursuite de la généralisation de la bibliothèque de formes sans revenir à l'ancien checkpoint EDM exécutable.
- Deux suivis non bloquants sont conservés : nettoyage des singletons terrain `34` lors du rebuild Snow, et identification des terrains natifs non nommés `18/19/24` dont le « grass jaune / herbes sèches » observé en Legacy.
- Développé avec l'assistance de ChatGPT.

## v1.3.2 — editor-safe starts / snow blocking / swamp transitions — VALIDÉE
- Validation utilisateur sur **4 générations Continental 768×768** : Legacy 4 joueurs, Legacy 20 joueurs, Upgraded 4 joueurs et Upgraded 20 joueurs.
- Sur les 4 générations : positions de départ acceptées par l'éditeur et aucun crash lors de la vue in-game.
- Marais : correction confirmée lors des tests.
- Neige : zones intérieures désormais non traversables comme prévu.
- Starts : ajout d'une marge de sécurité éditeur autour des 33 cellules natives, sans nettoyage artificiel du terrain.
- Starts : distance conservatrice accrue vis-à-vis de l'eau et exclusion stricte des objets statiques dans le halo éditeur.
- Building Stones : le footprint complet doit désormais rester hors du halo protégé du start, pas seulement l'ancre.
- Neige : `Snow129` et `Snow128` deviennent non marchables via l'accessibility statique, sur le même principe que le correctif Water.
- Marais : reconstruction systématique `Grass16 -> 21 -> 81 -> 80` depuis le masque complet ; les mini-marais de départ utilisent désormais une famille cohérente.
- Validators : ajout de contrôles d'accessibilité Snow et de chaînes de transitions Desert/Swamp/Snow.
- TODO Markdown enrichi avec les prochaines améliorations UI/statistiques demandées.
- Suppression de `docs/user_todo_20260818.txt`, désormais entièrement absorbé dans `TODO_MAPGEN.md`.
- Développé avec l'assistance de ChatGPT.

## v1.3.1 — preview crash fix / README presentation
- Correction du crash `NameError: Image is not defined` lors de la génération/rafraîchissement de l'aperçu.
- Import explicite de `PIL.Image` utilisé par le redimensionnement/zoom.
- Ajout d'un test de non-régression dédié au rendu GUI.
- README entièrement remis à jour avec une présentation du projet, les modes, archétypes, architecture des starts et état réel de la v1.3.1.
- Aucun changement dans les règles de génération Legacy/Upgraded.

## v1.3 — tooling / UX
- Ajout barre de progression par étapes de pipeline.
- Bouton seed aléatoire.
- Import EDM/MAP/SAV (SAV en lecture seule).
- Vues Global / Heightmap / Ressources / Territoires.
- Zoom par slider et molette.
- Sélecteur de toutes les tailles natives + max joueurs dynamique.
- Génération reste volontairement limitée à 768 tant que les autres tailles ne sont pas calibrées.
- Onglet Statistiques basique.
- Scrollbars sur les onglets texte.
- Export SAV non inventé : copie inchangée seulement si la source importée est déjà un SAV.
- TODO actualisé avec la généralisation future de la morphologie Upgraded.
