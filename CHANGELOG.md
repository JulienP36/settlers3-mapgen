# Changelog

## v1.4 candidate — dark mode / visualization comfort
- Nouveau thème **Sombre / Clair**, sombre par défaut, configurable dans un nouvel onglet `Paramètres`.
- Préférences d'affichage persistées dans le profil utilisateur Windows (`APPDATA/Settlers3MapGen/settings.json`).
- Slider d'opacité pour Heightmap / Ressources / Territoires afin de superposer les couches à la map globale.
- Projection optionnelle **Parallélogramme** pour rapprocher la visualisation de la géométrie affichée en jeu, sans modifier les données de map.
- Navigation : drag de la carte dans le canvas.
- Zoom molette : recalcul temporisé + cache de la couche de base pour réduire la latence ; sensibilité réglable.
- Barre de progression : génération + import + export + aperçu PNG ; état terminé bleu puis disparition automatique, erreur rouge.
- Les aperçus exportés respectent maintenant la vue, l'opacité et la projection sélectionnées.
- Starts : ajout d'un contour non rempli autour du footprint initial, coloré selon le joueur.
- Marqueurs `P1` à `P20` : couleur du joueur et rendu bitmap net, sans anti-aliasing, cohérent avec le pixel art de la map.
- Palette joueur unifiée avec la vue Territoires pour conserver la même correspondance de couleurs.
- Aucun changement dans les règles Legacy/Upgraded ni dans les formats EDM/MAP/SAV.
- Tests ajoutés pour les préférences, le blend d'opacité, la projection parallélogramme et les nouveaux marqueurs de starts.
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
