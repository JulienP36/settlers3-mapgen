# Settlers III MapGen — Release validation

Date: 2026-08-19

## v1.3.2 — VALIDÉE

### Scope du patch
- Durcissement de la sélection des starts pour l'acceptation par l'éditeur officiel : halo Grass naturellement dégagé, marge Water accrue et exclusion stricte des objets statiques.
- Maintien de toutes les passes ultérieures d'objets/ressources hors du halo protégé, y compris le footprint complet des Building Stones.
- Neige intérieure `129/128` rendue non traversable via l'accessibility statique.
- Reconstruction systématique des transitions de marais `Grass16 -> 21 -> 81 -> 80`, y compris les mini-marais de départ.
- Validators HARD pour les marges de starts, l'accessibility Snow et les chaînes de transitions Desert/Swamp/Snow.

### Contrôles automatisés
- Compilation des modules Python : PASS.
- Legacy 4P : génération sans HARD failure.
- Upgraded 4P : génération sans HARD failure.
- Upgraded 20P : génération sans HARD failure.
- Tests de non-régression ciblés : PASS.
- `SNOW_ACCESS`, `SWAMP_TRANSITIONS` et halos start : contrôlés par validators HARD.

### Validation externe utilisateur
Quatre générations **Continental 768×768** ont été testées dans les outils officiels :

- Legacy 4 joueurs ;
- Legacy 20 joueurs ;
- Upgraded 4 joueurs ;
- Upgraded 20 joueurs.

Résultats sur les quatre :

- positions de départ acceptées par l'éditeur ;
- aucun crash lors de la vue in-game / View Map ;
- correction des marais jugée effective ;
- neige intérieure non traversable comme prévu.

Conclusion : **la v1.3.2 sort du statut candidate et est considérée validée pour ce périmètre de contrôle**. Cette validation ne signifie pas que tous les seeds possibles ont été exhaustivement testés.

## v1.4 candidate — validation en cours

La v1.4 conserve le moteur/règles de génération validés de la v1.3.2 et ajoute principalement des améliorations de visualisation et d'interface :

- thème sombre / clair et préférences persistantes ;
- overlays avec opacité réglable ;
- projection parallélogramme ;
- drag et zoom améliorés ;
- barre de progression étendue ;
- palette joueurs unifiée ;
- marqueurs `P1` à `P20` nets et colorés ;
- contour du territoire initial des starts dérivé des données SAV natives (3500 cellules, étendue ±35 cellules) ;
- projection parallélogramme à décalage de 0,5 cellule par ligne, sans déformer les labels ;
- listes déroulantes corrigées en mode sombre ;
- sliders positionnables directement par clic sur la barre.

Les dernières corrections v1.4 restent à revalider visuellement par l'utilisateur avant promotion hors statut candidate.

## Problème connu séparé

Un crash a été observé en jeu quand les **fournitures de départ sont laissées sur `Défaut`**. Les presets explicites `Low`, `Medium` et `High` n'ont pas reproduit ce crash dans le contrôle concerné.

Ce problème n'est pas attribué pour l'instant aux corrections Snow/Swamp/start de la v1.3.2 et doit faire l'objet d'une investigation dédiée.
