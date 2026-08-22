# Settlers III MapGen v1.8 DEV_2_R4

Date: 2026-08-22

## Objectif

Dernière passe de densité/organisation du header DEV_2 après les essais réels sur grand écran et petite surface d’affichage. Le moteur de génération v1.5 reste strictement inchangé.

## Changements

- Réservation du paramètre **Modificateurs** immédiatement après Archétype.
  - Contrôle volontairement construit comme un menu à cases cochables, pas une Combobox mono-choix.
  - Seul choix actuel : `Aucun` / `None`.
  - Architecture prête pour plusieurs modificateurs simultanés plus tard.
  - Paramètre déjà relié à la clé de cache, l’historique de session et les messages de génération/état.
- Historique session : largeur nominale réduite (`34` caractères au lieu de `52`) et plus d’étirement forcé en mode large.
- Session/Comparaison contrainte : `Charger` et `Vider cache` passent sur la seconde ligne afin de préserver la lisibilité de l’historique.
- Mode étroit : `Aide` et le bouton de thème descendent sous `Langue` pour réduire la largeur du header.
- Barre de progression/overlay : inchangée, considérée validée++ après essais de redimensionnement.

## Validation automatique

- 81 tests PASS.
- Smoke moteur : 49 validations PASS.
- Binary checksum PASS.
- 5 fichiers moteur/config protégés inchangés byte-for-byte.
