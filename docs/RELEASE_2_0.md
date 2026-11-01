# Settlers III MapGen 2.0

## Français

La 2.0 apporte un nouveau socle de génération et de personnalisation pour
The Settlers III, ainsi qu’un portable Windows utilisable sans installation.

- Générateur Classique reconstruit depuis la référence native, mode Amélioré
  et réglages Personnalisés du terrain, des ressources, du décor et des bonus.
- Quatre archétypes : Classique, Continental, Îles individuelles et Îles par équipe.
- Éditeur de relief : bruits, fusions, transformations, masques dessinables et formules.
- Départs et équipes configurables, équipes aléatoires, filtres de validité.
- Configurations complètes sauvegardées, import/export JSON avec masques embarqués.
- Génération de lots de 1 à 4 cartes, historique, cache et comparaison A/B.
- Imports EDM/MAP/SAV, exports EDM/MAP, statistiques et graphiques interactifs.
- Interface FR/EN/DE/ES, thèmes clair/sombre et sprites dessinés par Julien.

### Choisir son archive

**WINDOWS_X64.zip** : extraire entièrement puis lancer Settlers3MapGen.exe.
Garder _internal à côté. Aucun Python, installateur ou téléchargement de dépendances.

**SOURCES.zip** : code, ressources et lanceurs BAT ; Python et dépendances requis.
Les références internes de recherche ne font pas partie de cette archive publique.

Préférences, configurations et masques restent dans %APPDATA%/Settlers3MapGen.
Fermer l’ancienne version avant de lancer la nouvelle ; conserver les anciens exports.
Les mises à jour se téléchargent manuellement : aucun updater automatique.

### Validation et limites

DEV11 et le portable R15 ont été acceptés par le propriétaire après essais.
Le paquet final est reconstruit sur Windows depuis le commit de publication ;
les rapports SELFTEST/QUALIFICATION et les empreintes accompagnent les ZIP.
Tailles de 256 à 768, jusqu’à 20 joueurs selon taille. Les petites cartes natives
ne garantissent pas la viabilité économique. Les indicateurs de départs distinguent
éditeur et jeu ; un contrôle automatique ne remplace pas un essai en jeu.
La conversion SAV vers une nouvelle carte ne reconstruit pas bâtiments, unités
ou événements d’une partie en cours. Aucun éditeur complet, replay ni Stats 2.

Projet conçu, dirigé, testé et validé par Julien Poitreau avec une assistance
importante de ChatGPT/OpenAI pour l’implémentation et les recherches techniques.
Les cartes illustrées sont des rendus de données réelles ; dessins fournis par Julien.

## English

Version 2.0 introduces a new generation/customization foundation and a standalone
Windows portable for The Settlers III.

- Native-reference Classic generation, Improved and Custom settings.
- Classic, Continental, Individual Islands and Islands by Team archetypes.
- Relief sources/blends/transforms, paintable masks and formula-based noise.
- Configurable starts/teams, balanced random teams and valid-start filters.
- Full saved configurations and JSON exchange with embedded masks.
- Sequential batches of 1–4 maps, session cache/history and A/B comparison.
- EDM/MAP/SAV import, EDM/MAP export, statistics and interactive charts.
- FR/EN/DE/ES interface, light/dark themes and owner-drawn sprites.

Download WINDOWS_X64.zip for direct EXE startup: extract the whole folder and
keep _internal beside the executable. No Python or dependency installation.
SOURCES.zip contains code/resources/BAT launchers and requires Python/dependencies.
User data stays in %APPDATA%/Settlers3MapGen; keep old exports before deleting
an earlier program folder. Updates are manual.

Native sizes are capped at 768, with up to 20 players depending on size.
Small native maps do not guarantee economically viable gameplay. Editor and game
start rules differ. SAV-to-new-map conversion omits ongoing-game entities.
Full editor mode, replay and Stats 2 are outside this release.

The owner accepted DEV11 and the R15 portable. Final assets are rebuilt and
qualified on Windows from the release commit; checksums and reports are included.
The project is human-directed, with substantial ChatGPT/OpenAI implementation
assistance and technical research. All illustrated maps use actual data.
