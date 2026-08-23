# v1.8 DEV_5_R2 — Ajustements des centres d’export

## Corrections

- Lorsque la vue active est Global, `PNG Vue actuelle` est désactivé : son résultat serait identique à `PNG Global`.
- Dans ce cas, `PNG Global` devient le choix PNG coché par défaut.
- Une explication FR/EN accompagne l’option désactivée.
- Les deux fenêtres disposent d’une marge basse de sécurité indépendante du thème.
- Leur Frame principal remplit désormais toute la zone cliente, y compris lorsque Windows ajuste tardivement les métriques ttk.
- Le fond natif du Toplevel reçoit la couleur du thème actif afin qu’aucune bande système claire ne soit exposée.
- Les cases à cocher possèdent des couleurs explicites pour les états normal, désactivé, survolé et pressé ; le thème sombre ne doit plus produire de flash clair au passage de la souris.

## Éléments préservés

- Tous les exports et garde-fous R1.
- EDM/MAP limités aux scaffolds 768 validés.
- SAV exclusivement copié à l’identique depuis sa vraie source.
- Deux PNG issus des données réelles de la carte.
- Gestion groupée des écrasements.
- Moteur v1.5 et cinq assets protégés inchangés.

## Validation interne

- 149 tests PASS.
- 49 validations moteur PASS.
- Checksum binaire PASS.
- Cinq hashes protégés inchangés.

## Checklist Windows ciblée

1. Ouvrir l’export Carte avec Global : Vue actuelle doit être grisée, Global coché.
2. Ouvrir avec Départs, Territoires ou une autre vue : Vue actuelle doit redevenir disponible et cochée par défaut.
3. Contrôler le bas des deux fenêtres en thème clair puis sombre.
4. Survoler lentement chaque case, notamment les formats désactivés, dans les deux thèmes.
