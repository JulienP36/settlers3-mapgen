# v1.8 DEV_4 PERF+ R1 — One-shot de performances

## Décision et garde-fous

Cette candidate est construite séparément depuis DEV_4_R6, déjà validée sous Windows et publiée sur `dev`. Elle doit être conservée uniquement si elle fonctionne immédiatement, sans régression visuelle ni fine tuning prolongé. Dans le cas contraire, elle sera abandonnée intégralement et R6 restera la référence.

- Aucun thread.
- Aucun changement du moteur, des profils ou de la bibliothèque native.
- Aucun changement attendu du rendu ou des interactions validées.
- Aucun raster fictif : toutes les images proviennent toujours des vraies données EDM/MAP/SAV ou générées.

## Optimisations testées

- Raster carré colorisé séparé de la projection et des sprites de départ.
- Réutilisation du même terrain carré pour Global et Départs.
- Projection Parallélogramme dérivée du raster carré déjà colorisé.
- Cache principal limité à la vue courante et à ses composites de projection.
- Cache Batch limité à une base carrée et une base projetée par résultat terminé.
- Langue et thème sans invalidation des pixels déterministes de la carte.
- Opacité Départs : recomposition des sprites seulement.
- Sauvegarde JSON des sliders Opacité et Zoom molette différée de 200 ms, puis forcée à la fermeture.

## Mesures locales sur la référence 768×768

Médiane de cinq exécutions dans l'environnement de validation interne :

| Opération | Temps médian |
|---|---:|
| Rendu complet Global Carré | 50,52 ms |
| Rendu complet Global Parallélogramme | 59,76 ms |
| Composition Carrée depuis cache | 0,10 ms |
| Projection depuis carré colorisé | 7,89 ms |
| Rendu complet Départs Parallélogramme | 63,42 ms |
| Recomposition des sprites Départs depuis cache projeté | 2,62 ms |

Gains mesurés : environ **7,6×** sur la construction d'une projection depuis le carré colorisé et **24×** sur un changement d'opacité Départs. Une projection déjà créée est ensuite récupérée directement par le cache applicatif.

Mémoire raster brute : carré RGB 768 = 1 769 472 octets ; parallélogramme RGBA = 14 149 632 octets. Avec quatre résultats Batch, les bases bornées représentent environ 60,7 Mio au maximum, hors objets Tk, miniatures et copies transitoires.

## Validation interne

- 139 tests de régression PASS.
- Parité pixel exacte entre pipeline direct et pipeline en calques : Global, Départs et Territoires ; Carrée et Parallélogramme.
- 49 validations moteur PASS.
- Checksum binaire PASS.
- Cinq hashes protégés inchangés.

## Checklist Windows

1. Alterner rapidement Carrée / Parallélogramme dans le viewer principal et dans Batch.
2. Faire varier l'opacité de Départs en continu et confirmer la fluidité ainsi que l'absence de clignotement.
3. Changer thème et langue avec une carte affichée : rendu inchangé et interface immédiatement actualisée.
4. Ouvrir quatre résultats Batch, changer projection et taille des marqueurs, puis déplacer/remplacer le grand aperçu.
5. Vérifier Global, Départs, Territoires et au moins une vue colorisée dans les deux projections.
6. Modifier les sliders puis fermer/rouvrir l'application afin de confirmer la persistance de la dernière valeur.
7. Observer la mémoire pendant plusieurs cycles de changements : elle doit se stabiliser, sans croissance continue.

## Validation Windows

Validation obtenue le 2026-08-23 : aucune fonctionnalité cassée, aucune baisse de performances observable et amélioration possible de la réactivité. Le one-shot ne nécessite aucun fine tuning supplémentaire ; PERF+ R1 est conservée et DEV_4_R6 reste son checkpoint historique de repli.
