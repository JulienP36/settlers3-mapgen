# Settlers III MapGen v1.7 DEV_5

Refonte visuelle et sémantique de la passe Statistiques à partir du retour utilisateur DEV_4.

## Graphiques
- orientation générale testée en barres verticales : échelle à gauche, labels en bas ;
- couleurs rapprochées de la carte et des vues existantes ;
- familles terrain segmentées : Eau = Mer + Lacs ; Montagne = Roche/non-neige + famille Neige ;
- stock minier segmenté : partie hors neige + partie sous famille Neige ;
- états Building Stones renommés par stock réel `12 pierres` → `1 pierre` → `Épuisé`, gradient vert → rouge ;
- `Végétation` renommée `Ressources forestières`, avec Pousses / Arbres adultes / Palmiers ;
- agriculture reprend les couleurs de la vue Agriculture ;
- distance au plus proche adversaire : gradient rouge (proche) → vert (loin) ;
- graphes de proximité arbres/pierre/poisson : gradient faible → fort ;
- stock minier joueur R40 empilé par type de minerai ;
- suppression du graphe redondant `Montagne proche — R40` du catalogue ;
- massifs/lacs/rivières utilisent des dégradés dédiés.

## Comparaison A/B
- format compact : une ligne par métrique ;
- barre A et barre B côte à côte ;
- valeur de chaque map centrée directement dans sa barre ;
- plus de deux lignes séparées `A - métrique` / `B - métrique`.

## Stats / données
- schema Stats v3 ;
- eau : `ocean_cells` + `inland_water_cells` ;
- montagne : `mountain_non_snow_cells` + `snow_family_cells` ;
- minerais : stock/cases hors neige et sous famille neige ;
- distribution des hauteurs terrestres ajoutée ; le graphe n'affiche plus le minimum global mécaniquement pollué par l'eau.

## UX
- Validations / Pipeline / Métadonnées / Statistiques deviennent read-only tout en restant sélectionnables/copiëables ;
- calcul Stats sur chargement historique/comparaison relié à l'overlay/barre de progression quand le cache manque.

## Validation
- 49 tests PASS ;
- smoke réel SAV 768×768 / 10 joueurs ;
- invariants exacts vérifiés pour toutes les nouvelles barres segmentées ;
- moteur v1.5 et fichiers protégés inchangés.
