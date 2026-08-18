# Settlers III MapGen v1.1

Mise à jour architecturale de la première GUI fonctionnelle.

## Principe central

MapGen sépare désormais explicitement deux notions :

- **Archétype** = macro-forme de la carte (répartition globale terre/eau et grandes masses).
- **Mode de génération** = tout le reste : relief, formes locales des zones, hydrologie détaillée, ressources, objets, balance, starts et validators spécifiques.

Les deux axes sont indépendants. À terme, n'importe quel archétype pourra être combiné avec n'importe quel mode.

## Modes réservés

- **Legacy** — fonctionnel actuellement. Base fidèle au comportement Settlers III / reverse-engineering.
- **Upgraded** — réservé dans l'architecture, non activé tant que toutes les règles custom validées n'ont pas été récupérées proprement depuis les références/checkpoints.
- **Custom** — réservé dans l'architecture, futur mode manuel avec paramètres exposés et avertissements.

La GUI affiche les trois noms dès maintenant, mais refuse explicitement de générer avec un mode non implémenté plutôt que de produire un faux preset incomplet.

## Archétypes

- **Continental** — fonctionnel actuellement.
- **Large Islands** — réservé.
- **Small Islands** — réservé.

L'archétype doit rester une couche de macro-topologie. Les formes locales des montagnes, biomes, rivières, objets, ressources et leur balance relèvent du mode.

## Ordre de génération verrouillé

La v1.1 corrige un point architectural important : **les starts sont placés très tôt**.

Ordre conceptuel :

```text
1. Archetype: macro-layout
2. STARTS maximin / fair-play
3. Réservation des zones techniques et zones de bonus
4. Hydrologie détaillée / corrections
5. Biomes / relief / Snow
6. Ressources
7. Balance locale autour des starts
8. Objets / décorations
9. Accessibilité finale
10. Validators
11. Export
```

Une passe tardive doit s'adapter aux starts réservés ; elle ne doit pas repousser leur placement à la fin.

## GUI

La GUI conserve les fonctions de v1 :

- aperçu déterministe de la vraie `Area` ;
- nombre de joueurs / seed ;
- PASS/FAIL validators ;
- journal du pipeline ;
- métadonnées ;
- export EDM/MAP bloqué si HARD FAIL.

Elle ajoute maintenant :

- sélecteur **Mode de génération** ;
- sélecteur **Archétype** ;
- état explicite lorsqu'un mode/archétype est réservé mais non implémenté.

## Portée actuelle

- 768×768 ;
- 2–20 joueurs ;
- Legacy + Continental seulement réellement générables.

Cette limitation est volontaire : Upgraded ne sera activé qu'après transcription exhaustive des règles custom en configuration + pipeline + validators/tests.

## Installation Windows

- première installation : `install_python_and_run.bat` ou `install_and_run.bat` ;
- ensuite : `run_gui.bat`.

Les lanceurs testent `py -3` puis `python`.

## Tests de release

La v1.1 vérifie notamment :

- registre séparé modes / archétypes ;
- starts placés avant l'hydrologie détaillée ;
- 20 starts survivent au pipeline complet ;
- HARD checks du moteur ;
- export checksum ;
- refus explicite de Upgraded/Custom tant qu'ils ne sont pas implémentés.

## Règle de non-régression

Une règle validée pour un profil doit progressivement exister sous une forme exécutable : configuration, étape du pipeline, validator ou test. Les références Markdown restent la documentation historique ; le programme devient la source exécutable de vérité.
