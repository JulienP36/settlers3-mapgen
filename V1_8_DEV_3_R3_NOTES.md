# v1.8 DEV_3_R3 — Batch preview polish

## Changements depuis R2

- La miniature n'utilise plus des dimensions Tk ambiguës de 12×4 pixels.
- Chaque ligne réserve 152×88 pixels et affiche une carte réelle jusqu'à 144×80.
- Un dé dédié à la seed commune se trouve entre son champ et « Appliquer à toutes ».
- L'agrandissement n'est plus une fenêtre : il s'agit d'un tooltip sans chrome contenant uniquement la carte.
- Survol maintenu 700 ms : tooltip temporaire.
- Clic : tooltip épinglé ; second clic ou clic sur la grande carte : fermeture.
- En parallélogramme, les pixels transparents restent invisibles : aucun rectangle de fond autour de la carte sous Windows.

## Validation automatisée

- 103 tests de régression PASS.
- Génération smoke : 49 validations PASS.
- Binary checksum PASS.
- Moteur, profils et bibliothèque native protégés inchangés.

## Validation Windows demandée

1. Générer quatre cartes et vérifier que chaque miniature est immédiatement reconnaissable.
2. Tester le nouveau dé commun puis « Appliquer à toutes ».
3. Vérifier le tooltip par survol maintenu et par clic.
4. Vérifier qu'il n'existe aucune barre de titre, bordure ou bouton autour de la grande carte.
5. Basculer la projection principale sur Parallélogramme, rouvrir Batch puis générer une carte : le grand tooltip doit laisser les coins extérieurs totalement transparents.

Après validation, synchroniser exactement R3 sur `dev`, puis demander à l'utilisateur ses dernières notes du TODO local avant la suite.
