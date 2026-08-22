# v1.8 DEV_3_R2 — Batch Generation polish

## Changements depuis R1

- Les quatre cartes reprennent la même seed courante/par défaut à l'ouverture.
- Les dés globaux et individuels sont conservés.
- Une seed commune peut être saisie puis appliquée aux quatre lignes.
- Chaque résultat possède une miniature déterministe calculée depuis la vraie carte.
- Clic sur la miniature : grande vue immédiate.
- Survol maintenu 700 ms : grande vue ; un passage rapide ne déclenche rien.
- Ordre inférieur : Afficher, Affecter à A, Affecter à B, barre progression/feedback.
- Couleurs sémantiques : vert génération/réussite, bleu cache, rouge erreur, gris annulation.
- Les boutons A/B affichent leur pastille d'occupation.
- Une même sortie ne peut plus occuper A et B : la réaffectation la déplace et affiche un feedback explicite.
- Une fenêtre Batch déjà ouverte se retraduit directement lorsque la langue principale change.

## Validation automatisée

- 100 tests de régression PASS.
- Génération smoke : 49 validations PASS.
- Binary checksum PASS.
- Moteur, profils et bibliothèque native protégés inchangés.

## Validation Windows demandée

1. Ouvrir Batch et vérifier que les quatre seeds sont identiques à la seed principale.
2. Tester le dé global, chacun des dés individuels et « Appliquer à toutes ».
3. Changer FR/EN pendant que Batch reste ouverte et vérifier la traduction sans perte des valeurs.
4. Générer au moins deux cartes puis vérifier miniature, clic immédiat et survol maintenu 700 ms.
5. Vérifier l'ordre des trois actions et le feedback intégré à la barre colorée.
6. Affecter deux cartes à A/B et contrôler les pastilles.
7. Affecter la même carte à l'autre slot : elle doit être déplacée, jamais dupliquée, avec feedback explicite.

Après validation, synchroniser exactement R2 sur `dev`, puis demander à l'utilisateur ses dernières notes du TODO local avant la suite.
