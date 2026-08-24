# v1.8 DEV_7_R4 — Historique stable, protections explicites et aperçu unifié

## Périmètre

- consulter, afficher ou affecter une carte depuis l’interface ne change plus son ordre LRU ; seuls les vrais accès du pipeline de génération peuvent promouvoir une entrée ;
- cadenas compacts et distincts `V`, `A`, `B`, combinables, avec infobulle ; rôle `M` réservé à un futur verrouillage manuel ;
- cercle coché actif agrandi dans la même enveloppe de bouton ;
- libellés contextuels `Chargée !`, `Affichée !`, `Affectée à A/B !` dans les quatre langues ;
- loupe en trois états sur les miniatures du Centre et de Batch ;
- grand aperçu Historique aligné sur Batch : survol 700 ms, clic pour épingler, déplacement, zoom, fermeture par second clic et conservation de la position ;
- remplacement atomique du rendu lors des changements de projection, marqueurs, zoom ou sélection ;
- infobulle explicative sur le signalement d’une carte affichée hors historique ;
- avertissement avant Batch si les résultats distincts excèdent les places disponibles après protections A/B et futurs verrous manuels.

## Garanties

- moteur de génération v1.5, formats binaires et résultats déterministes inchangés ;
- ordre du Centre stable lors des actions purement visuelles ;
- suppression seule autorisée à modifier les rangs visibles en dehors de la génération/cache ;
- aucune Issue GitHub créée avant la passe de réflexion dédiée ;
- aucune publication sur `dev` avant validation Windows.

## Validation interne

- 174 tests de régression PASS ;
- 49 validations moteur PASS ;
- checksum binaire PASS ;
- cinq hashes protégés inchangés.

## Checklist Windows

1. Charger/Afficher/Affecter plusieurs cartes et vérifier que l’ordre `#` ne change pas.
2. Vérifier les cadenas `V`, `A`, `B` seuls et combinés, ainsi que leurs infobulles.
3. Vérifier le cercle coché agrandi et les libellés actifs dans le header, le Centre et Batch.
4. Tester la loupe, le survol de 700 ms, l’épinglage, le déplacement, le zoom et le second clic de fermeture.
5. Changer de sélection, projection et taille de marqueurs avec l’aperçu ouvert : pas de clignotement et position conservée.
6. Supprimer la carte affichée, puis survoler le signalement hors historique.
7. Réduire volontairement la place disponible du cache avant un lot et vérifier l’avertissement prévisionnel.
8. Refaire les points essentiels en clair/sombre et FR/EN/DE/ES.
