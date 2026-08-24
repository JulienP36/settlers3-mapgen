# Settlers III MapGen v1.8 TITLEBAR_TEST_R3

Candidate expérimentale corrigeant l’interprétation visuelle de R2.

## Les trois zones sont distinctes

- contenu : couleur normale du thème actif ;
- barre de titre native : `#15171a` dans les deux thèmes ;
- séparateur sous la barre : ligne de 1 px `#6f7378` ;
- contour Windows extérieur : `#3c4043`.

La ligne est placée au sommet de la zone cliente et ne modifie ni sa géométrie,
ni son gestionnaire de disposition. La mise à jour reste entièrement
événementielle, sans surveillance permanente.

## Contrôle Windows demandé

1. Vérifier en clair puis en sombre que la barre ne se confond plus avec le contenu.
2. Vérifier que la ligne de séparation est visible sans paraître trop lumineuse.
3. Contrôler la fenêtre principale et plusieurs fenêtres secondaires.
4. Vérifier que Snap, déplacement et redimensionnement natifs sont inchangés.

La fenêtre d’aide reste une boîte native hors de l’inventaire thémé et demeure
consignée au TODO.
