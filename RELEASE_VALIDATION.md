# Settlers III MapGen — Release validation

Date: 2026-08-19

## v1.3.2 — VALIDÉE

### Scope du patch
- Durcissement de la sélection des starts pour l'acceptation par l'éditeur officiel : halo Grass naturellement dégagé, marge Water accrue et exclusion stricte des objets statiques.
- Maintien de toutes les passes ultérieures d'objets/ressources hors du halo protégé, y compris le footprint complet des Building Stones.
- Neige intérieure `129/128` rendue non traversable via l'accessibility statique.
- Reconstruction systématique des transitions de marais `Grass16 -> 21 -> 81 -> 80`, y compris les mini-marais de départ.
- Validators HARD pour les marges de starts, l'accessibility Snow et les chaînes de transitions Desert/Swamp/Snow.

### Validation externe utilisateur
Quatre générations **Continental 768×768** ont été testées dans les outils officiels : Legacy 4P, Legacy 20P, Upgraded 4P et Upgraded 20P.

Résultats : starts acceptés par l'éditeur, aucun crash View Map/in-game, correction des marais confirmée et neige intérieure non traversable comme prévu.

Conclusion : **v1.3.2 validée** pour ce périmètre de contrôle.

## v1.4 — VALIDÉE

La v1.4 conserve le moteur/règles de génération validés de la v1.3.2 et ajoute les améliorations de visualisation et d'interface suivantes :

- thème sombre / clair et préférences persistantes ;
- overlays avec opacité réglable ;
- projection parallélogramme à décalage de 0,5 cellule par ligne ;
- drag et zoom améliorés ;
- barre de progression étendue ;
- palette joueurs unifiée ;
- marqueurs `P1` à `P20` nets, colorés et non déformés ;
- contour du territoire initial dérivé des SAV natifs : 3500 cellules, étendue ±35 cellules ;
- territoire initial rendu comme un vrai cercle dans la géométrie parallélogramme, avec déformation inverse en vue carrée ;
- listes déroulantes corrigées en mode sombre, ouvertes comme fermées ;
- sliders positionnables directement par clic sur leur barre.

### Validation utilisateur finale
Les deux derniers points restant à confirmer ont été contrôlés visuellement et validés :

- géométrie du cercle de territoire en vues parallélogramme et carrée : **OK** ;
- fond/texte des combobox fermées en thème sombre : **OK**.

Conclusion : **v1.4 sort du statut candidate et est considérée validée**.

## Problème connu séparé — prochaine investigation

Un crash a été observé en jeu quand les **fournitures de départ sont laissées sur `Défaut`**. Les presets explicites `Low`, `Medium` et `High` n'ont pas reproduit ce crash dans le contrôle concerné.

Ce problème est séparé de la validation v1.4 et devient la prochaine investigation prioritaire.
