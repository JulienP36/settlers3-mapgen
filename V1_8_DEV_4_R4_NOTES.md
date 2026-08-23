# v1.8 DEV_4_R4 — Visualisations joueurs v4

## Changements

- Nouvelle Vue `Départs` / `Starts`.
- Vue Global épurée : aucun label, contour ou marqueur de départ.
- Vue Départs : masque initial natif exact de 3500 cellules / bord HEX6 de 210 cellules ; exactement un petit sprite J1–J20 est centré sur chacune des 210 cellules du bord.
- Extraction déterministe des vingt sprites 36×48 depuis la référence fournie par l'utilisateur ; fond herbe uniforme converti en transparence, aucune interpolation ni image inventée.
- Marqueur central Carrée 18×24 / Parallélogramme 36×48 ; marqueurs de frontière sans chevauchement 1×1 / 2×2. Tous sont ancrés sur leur centre géométrique.
- Le curseur d'opacité fonctionne dans Départs : 100 % conserve les sprites complets, 0 % restitue exactement Global et les valeurs intermédiaires fondent seulement les sprites.
- Miniatures et grands aperçus Batch : marqueurs centraux compacts et recentrés, sans contour de zone initiale.
- Ordre des vues : Global, Départs, Territoires, puis les autres couches.
- Vue Territoires SAV : claims runtime valides 0..19 reliés strictement à la palette centralisée J1–J20.
- Vue Territoires EDM/MAP : couche visuelle reconstruite depuis le masque natif exact de 3500 cellules autour de chaque start ; aucune donnée source n'est modifiée ou inventée comme champ fichier.
- Modernisation/retouche manuelle des marqueurs reportée à la future refonte Pixel Art.

## Validation interne

- 121 tests de régression PASS.
- Rendu déterministe contrôlé depuis `data/upgraded_reference_768.edm` en Global/Départs, Carrée/Parallélogramme et miniatures Batch.
- Génération smoke : 49 validations PASS.
- Binary checksum PASS.
- Cinq hashes protégés inchangés.

## Checklist Windows

1. Vérifier que Global ne contient plus aucun départ ni contour initial.
2. Vérifier Départs en Carrée puis Parallélogramme : frontière très fine, composée de 210 marqueurs sans chevauchement et fidèle à la forme native.
3. Faire varier l'opacité de 100 à 0 : le terrain doit rester identique et seuls les sprites doivent disparaître progressivement.
4. Importer un EDM puis un MAP : Territoires doit afficher les zones initiales colorées autour des vrais starts.
5. Importer un SAV : Territoires doit toujours afficher ses claims runtime réels.
6. Générer un Batch : vérifier que les marqueurs compacts validés restent inchangés et sans contour initial.

Les labels restent volontairement absents : leur forme et leur position feront l'objet d'une passe de conception ultérieure. Validation Windows obtenue : rendu des frontières, ordre des vues, opacité et comportements Territoires EDM/MAP/SAV acceptés. Promotion non destructive sur `dev` autorisée.
