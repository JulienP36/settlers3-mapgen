# Settlers III MapGen v1.8 DEV_2_R2

Révision responsive/feedback de DEV_2 après test Windows réel.

- 1080p devient explicitement une cible compacte (largeur, hauteur de fenêtre et hauteur d’écran prises en compte).
- Vue / Filtre carte thermique / Recentrer / Zoom quittent le bandeau global et passent dans une barre d’outils contextuelle au-dessus du viewer de carte.
- Cette barre du viewer possède son propre reflow 1 ligne / 2 lignes selon la largeur du panneau carte.
- L’ancienne Progressbar Tk du header est définitivement retirée du layout ; la progression rapide reste uniquement dans l’overlay moderne de la map.
- Feedback v1 enrichi : bascule A/B vers map identifiée, cache vide, bouton thème, recentrage, seed aléatoire, exports JSON/CSV/PNG Stats-Graphiques, opacité non applicable et synchronisation du nombre de joueurs.
- TODO enrichi : loupe carrée + curseur d’inspection fin, infos inspecteur près du pointeur, réflexion future sur un zoom plus compact.
- Aucun changement du moteur de génération v1.5.
