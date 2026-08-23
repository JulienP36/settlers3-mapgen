# v1.8 DEV_6_R1 — Interface FR/EN/DE/ES

## Périmètre

- ajout de l’allemand et de l’espagnol au sélecteur de langue avec drapeaux raster déterministes ;
- préférence de langue persistante et bascule dynamique sans redémarrage ;
- fenêtre principale, Batch, paramètres, feedback, progression, aide, raccourcis et états indisponibles traduits ;
- centres d’export Cartes et Graphiques traduits ;
- rapports Statistiques, quinze Graphiques, légendes, unités et tooltips traduits ;
- titres de fenêtres entièrement localisés ;
- anglais utilisé comme repli de sécurité lorsqu’une entrée manque.

## Qualité linguistique et limite connue

- FR/EN sont les versions de référence relues et considérées comme correctes.
- DE/ES sont des traductions automatiques seulement partiellement revues ; elles ne sont pas présentées comme validées par des locuteurs.
- Lorsqu’une carte est déjà chargée, le rapport texte de l’onglet Statistiques ne se retraduit actuellement qu’après rechargement de la carte. Ce point est non bloquant pour DEV_6 et reporté à la future amélioration de l’onglet.

## Garanties

- aucun changement du moteur de génération v1.5 ;
- aucun changement des formats EDM/MAP/SAV ;
- aucun changement du rendu des cartes ;
- aucune image générée : les nouveaux drapeaux sont dessinés localement par primitives raster déterministes.

## Validation interne

- 156 tests de régression PASS ;
- 49 validations moteur PASS ;
- checksum binaire PASS ;
- cinq hashes protégés inchangés.

## Validation Windows

- Interface principale, Batch, exports, thèmes et langues jugés fonctionnels.
- DEV_6_R1 validée par l’utilisateur le 2026-08-23.
- Retraduction tardive du rapport texte Statistiques acceptée comme limite non bloquante et reportée.

## Checklist Windows

1. Passer successivement FR → EN → DE → ES dans la fenêtre principale et vérifier que les contrôles déjà ouverts se retraduisent immédiatement.
2. Ouvrir Batch, modifier quelques paramètres, changer de langue et vérifier que la fenêtre se retraduit sans perdre ses valeurs.
3. Contrôler les thèmes clair/sombre, les paramètres, l’aide F1, les raccourcis et les feedbacks dans les quatre langues.
4. Ouvrir les deux centres d’export dans chaque langue et vérifier titres, formats, états indisponibles et messages.
5. Parcourir Statistiques et les quinze Graphiques, notamment légendes et tooltips, en allemand puis en espagnol.
6. Fermer l’application en DE ou ES, la relancer et vérifier la persistance de la langue.
