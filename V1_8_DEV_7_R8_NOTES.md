# v1.8 DEV_7_R8 — États de loupe indépendants et parité de zoom

## Changements

1. Le bouton de confirmation `Réduire` reprend le style neutre d’`Annuler` afin d’éviter un contraste texte/fond dépendant du thème.
2. La loupe au repos devient plus translucide.
3. Les états sont renommés selon leur fonction : `idle`, `hover`, `active`, `active_hover`.
4. `active_hover` ajoute une croix dans la loupe de la miniature source pour indiquer qu’un clic fermera l’aperçu.
5. La source active et la miniature survolée sont deux informations indépendantes : A peut rester active pendant que B indique séparément qu’elle est cliquable.
6. Les événements d’entrée/sortie sont reliés au conteneur complet de chaque miniature ; une sortie réelle efface immédiatement l’état de survol sans course avec l’image enfant.
7. Le grand aperçu Batch reçoit le zoom molette déjà disponible dans l’Historique, avec les mêmes bornes de 35 à 125 %.
8. Drag, position conservée, clic d’ouverture/fermeture, survol de 700 ms et remplacement atomique restent inchangés.

## Garanties

1. Les loupes restent des calques RGBA déterministes sans fond rectangulaire opaque.
2. Une seule source d’aperçu peut être active, mais une autre miniature peut simultanément signaler son survol.
3. Moteur de génération v1.5, formats binaires et données déterministes inchangés.
4. Aucune publication sur `dev` avant validation Windows.

## Validation interne

1. 188 tests de régression PASS.
2. 49 validations moteur PASS.
3. Checksum binaire PASS.
4. Cinq hashes protégés inchangés.

## Checklist Windows

1. Vérifier que `Réduire` et `Annuler` ont le même style neutre en clair et sombre.
2. Vérifier la loupe au repos, plus discrète mais toujours identifiable.
3. Épingler l’aperçu de A, puis survoler B : A doit rester active et B devenir survolée.
4. Quitter B : seule B doit revenir immédiatement au repos ; A reste active.
5. Survoler A active : la loupe doit afficher l’état de fermeture, puis un clic doit fermer l’aperçu.
6. Passer rapidement entre les marges, l’image et plusieurs miniatures : aucun état de survol ne doit rester bloqué.
7. Vérifier ces transitions dans Batch et dans le Centre d’historique.
8. Utiliser la molette sur les deux grands aperçus : zoom/dézoom et position doivent être cohérents.

## Bug confirmé à corriger en R9

1. Ouvrir le Centre d’historique.
2. Le fermer avec la croix ou le bouton.
3. Lancer une génération simple.
4. Résultat actuel : la génération aboutit, puis l’interface déclenche `invalid command name` dans `_refresh_history_preview()` car `_history_preview_label` référence encore un widget détruit.
5. Correctif R9 prévu : nettoyage complet des références, ordre de fermeture sûr, annulation préalable des callbacks et garde d’existence Tk avant tout rafraîchissement.
