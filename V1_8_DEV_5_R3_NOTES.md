# v1.8 DEV_5_R3 — Modalité stricte et états indisponibles

## Corrections

- Sous Windows, la fenêtre principale est désactivée au niveau système pendant l’ouverture d’un centre d’export.
- Le clic, la molette, le clavier et les raccourcis ne peuvent plus agir sur les contrôles extérieurs tant que la fenêtre modale reste ouverte.
- La fenêtre principale est systématiquement réactivée et refocalisée à la fermeture du centre.
- Les formats indisponibles utilisent un style dédié : texte grisé et barré dans les thèmes clair et sombre.
- Aucun suffixe textuel n’est ajouté aux libellés ; les explications bilingues détaillées restent sous la liste.

## Éléments préservés

- Tous les exports, garde-fous et corrections R1/R2.
- Géométrie basse et survols clair/sombre corrigés en R2.
- EDM/MAP limités aux scaffolds 768 validés.
- SAV exclusivement copié à l’identique depuis sa vraie source.
- Deux PNG issus des données réelles de la carte.
- Gestion groupée des écrasements.
- Moteur v1.5 et cinq assets protégés inchangés.

## Checklist Windows ciblée

1. Ouvrir chacun des deux centres d’export et tenter clic, molette et raccourcis sur la fenêtre principale : aucun contrôle extérieur ne doit réagir.
2. Fermer avec Annuler puis avec la croix : la fenêtre principale doit être immédiatement réactivée.
3. Contrôler les formats indisponibles en clair et sombre : case + texte grisés, texte barré, explication lisible dessous.
4. Recontrôler le bas des fenêtres et les survols corrigés en R2.

## Validation interne

- 151 tests PASS.
- 49 validations moteur PASS.
- Checksum binaire PASS.
- Cinq hashes protégés inchangés.

## Validation Windows

- Modalité stricte validée : aucune interaction extérieure, y compris via la molette.
- Réactivation de la fenêtre principale validée.
- Formats indisponibles grisés/barrés et explications validés dans les deux thèmes.
- Géométrie basse et corrections de survol R2 validées.
- DEV_5_R3 devient le checkpoint DEV_5 retenu.
