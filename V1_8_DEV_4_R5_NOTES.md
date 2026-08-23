# v1.8 DEV_4_R5 — Réglage des marqueurs d'aperçu

## Périmètre

- Nouveau réglage dans `Paramètres → Affichage` : `Marqueurs dans les aperçus`.
- Choix FR/EN persistants : `Masqués / Petits / Normaux` (`Hidden / Small / Normal`).
- Valeur par défaut : `Petits`.
- Application aux miniatures Batch et à leur grand aperçu survol/clic.
- Une base sans marqueurs est calculée une fois par résultat/projection puis réutilisée ; changer l'option ne recompose que les sprites.
- Actualisation immédiate des résultats déjà visibles ; le grand aperçu ouvert reçoit sa nouvelle image sans destruction de sa fenêtre.

## Correspondance

- `Masqués` : aucun marqueur de départ dans les aperçus Batch.
- `Petits` : échelle minimale, plus discrète que R4.
- `Normaux` : taille compacte validée dans R4.

La Vue Départs principale, son marqueur central, sa frontière exacte de 210 marqueurs et son curseur d'opacité ne sont pas modifiés. Les données de carte et le moteur de génération restent inchangés.

## Validation interne

- 127 tests de régression PASS, dont égalité pixel par pixel entre rendu direct et composition par couche en Carrée/Parallélogramme.
- Génération smoke : 49 validations PASS.
- Binary checksum PASS.
- Cinq hashes protégés inchangés.
- Benchmark de composition seule sur la référence 768 : environ 0,08–0,09 ms en Carrée et 0,57–0,64 ms en Parallélogramme dans l'environnement de validation.

## Checklist Windows

1. Ouvrir Batch et générer au moins une carte.
2. Dans `Paramètres → Affichage`, passer successivement sur `Petits`, `Normaux` et `Masqués`.
3. Vérifier l'actualisation immédiate de la miniature Batch.
4. Garder le grand aperçu ouvert pendant un changement : son image doit changer sans disparition/réapparition du tooltip.
5. Changer la langue : le libellé et les trois choix doivent suivre FR/EN sans perdre la valeur sélectionnée.
6. Vérifier que la Vue Départs et ses frontières restent identiques à R4.

Validation Windows obtenue : les trois modes, la fluidité de la composition par couche et l'actualisation sans clignotement du tooltip sont acceptés. Promotion non destructive sur `dev` autorisée.
