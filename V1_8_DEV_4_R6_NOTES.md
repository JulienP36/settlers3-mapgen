# v1.8 DEV_4_R6 — Déplacement du grand aperçu Batch

## Changements

- Un aperçu ouvert par clic reste épinglé et peut être déplacé en glissant directement la carte.
- Cliquer sur la grande carte ne ferme plus l'aperçu.
- Recliquer sur sa miniature source ferme l'aperçu.
- Cliquer sur une autre miniature remplace la carte tout en conservant exactement la position de la fenêtre précédente.
- Les changements de marqueurs ou de projection conservent aussi la position courante.
- Un changement de projection ou de miniature construit et affiche la nouvelle surface transparente au-dessus de l'ancienne avant de détruire cette dernière ; les changements de marqueurs gardent le remplacement direct déjà validé en R5.
- Le déplacement est contraint aux limites visibles de l'écran.
- `Échap` ferme toujours l'aperçu.
- Le survol temporisé de 700 ms reste temporaire et non déplaçable.

## Éléments préservés

- Cache R5 de la base sans marqueurs et composition légère des sprites.
- Transparence du parallélogramme.
- Placement initial automatique relatif à la miniature.
- Génération, vues et moteur v1.5 inchangés.

## Validation interne

- 133 tests de régression PASS, dont déplacement par delta du pointeur, limites écran, conservation de position, interactions de fermeture/remplacement et ordre du double tampon.
- Génération smoke : 49 validations PASS.
- Binary checksum PASS.
- Cinq hashes protégés inchangés.

## Checklist Windows

1. Épingler un aperçu par clic puis le déplacer depuis plusieurs zones de la carte.
2. Vérifier qu'un simple clic sur la grande carte ne le ferme plus.
3. Cliquer une autre miniature : la nouvelle carte doit apparaître exactement au même endroit.
4. Recliquer la miniature actuellement affichée : l'aperçu doit se fermer.
5. Déplacer l'aperçu contre chaque bord de l'écran : il doit rester visible.
6. Modifier la taille des marqueurs puis la projection : la position manuelle doit être conservée et la projection ne doit plus produire de disparition intermédiaire.
7. Vérifier le survol temporaire et la fermeture avec `Échap`.

Validation Windows obtenue : déplacement, fermeture, remplacement à position constante, limites écran et double tampon de projection acceptés. Promotion non destructive sur `dev` autorisée.
