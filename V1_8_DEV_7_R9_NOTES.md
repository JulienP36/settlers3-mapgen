# Settlers III MapGen v1.8 DEV_7_R9 — notes de test Windows

Cette candidate corrige le crash Tk confirmé après fermeture du Centre d’historique et termine les ajustements de loupe et de zoom issus de la revue R8.

- Le Centre d’historique annule désormais ses callbacks et invalide toutes ses références de widgets avant destruction.
- Les rafraîchissements tardifs ignorent proprement une fenêtre fermée ou un widget Tk détruit.
- La loupe possède cinq états distincts : repos, survol, source active, aperçu temporaire et action de fermeture.
- L’aperçu ouvert par pause souris utilise un état violet sans croix : un clic l’épingle au lieu de le fermer.
- La croix orange apparaît uniquement sur l’aperçu épinglé, lorsque le clic ferme réellement celui-ci.
- Le grand aperçu Batch emploie les mêmes contraintes d’écran que l’Historique ; sa plage réelle reste 35–125 %.
- Déplacement, position mémorisée et remplacement atomique sans clignotement sont conservés.

Validation interne : 190 tests de régression, 49 validations moteur, checksum binaire et cinq hashes protégés.

## Vérification Windows

1. Ouvrir le Centre d’historique, le fermer par la croix, puis lancer une génération simple : aucune erreur Tk ne doit apparaître.
2. Refaire le test en fermant le Centre avec son bouton `Fermer`.
3. Répéter l’ouverture/fermeture plusieurs fois, puis rouvrir le Centre et vérifier son aperçu.
4. Laisser la souris 700 ms sur une miniature : l’aperçu temporaire doit afficher une loupe violette sans croix.
5. Cliquer sur cette miniature : l’aperçu devient épinglé et la croix orange apparaît lorsque la miniature source est survolée.
6. Quitter la miniature : la source reste indiquée par l’état actif normal.
7. Revenir dessus puis cliquer : l’aperçu épinglé doit se fermer.
8. Vérifier ces états dans Batch et dans le Centre d’historique.
9. Comparer le zoom des deux grands aperçus : l’amplitude Batch doit désormais être comparable à celle de l’Historique.
