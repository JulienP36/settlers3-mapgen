# v1.8 DEV_2_R7

## Dernier polish du header R6

- La colonne élastique historique 11 du header v1.3 est remise à zéro : Langue/Aide/Thème peut atteindre le véritable bord droit.
- Le breakpoint compact passe de 1600 à 1750 px afin d'éviter la coupure du bouton Thème observée dans le GIF R6.
- Les boutons d'identité A/B utilisent leur largeur textuelle naturelle lorsque Session dispose d'espace.
- En mode compact, ils ne passent à une largeur bornée que lorsque Session descend sous 900 px.
- Les boutons individuels de suppression A/B affichent une croix rouge raster lorsque le slot est rempli ; vide, ils restent gris et désactivés.
- Structure R6, minimum et Zoom inchangés.
- Aucun changement du moteur de génération v1.5.

## Validation automatisée

- 90 tests pytest PASS.
- Génération smoke : 49 validations PASS.
- Binary checksum PASS.
- Hashes protégés génération/configuration/bibliothèque native inchangés.

## Validation Windows terminée

- GIF utilisateur contrôlé avec et sans slots A/B définis.
- Grand écran : Langue/Aide/Thème réellement à droite.
- Rétrécissement : aucun contrôle global coupé avant le passage compact.
- A et B remplis : texte complet lorsque la place le permet et croix rouge active.
- Près du minimum : boutons A/B compacts sans chevauchement.
- Header responsive R7 validé sous Windows par l'utilisateur le 2026-08-22.
