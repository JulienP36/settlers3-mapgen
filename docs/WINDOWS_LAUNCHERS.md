# Lanceurs Windows — revue du 27 octobre 2026

Les quatre BAT restants appartiennent aux sources et aux outils de développement.
Le portable se lance par `Settlers3MapGen.exe` et n'embarque aucun BAT.

| Script | Fonction | Décision |
|---|---|---|
| `run_gui.bat` | Détecte Python et lance la GUI depuis le dossier des sources, sans installation | Conserver pour les lancements courants |
| `install_and_run.bat` | Avec Python installé, installe les dépendances puis lance la GUI | Conserver pour préparer les sources |
| `install_python_and_run.bat` | Installe Python 3.12 via winget s'il manque ; sinon délègue au précédent | Conserver pour le premier démarrage source |
| `build/windows/build_windows.bat` | Lance la chaîne PowerShell de compilation et qualification du portable | Conserver pour construire le programme |

La détection de Python répétée dans les trois lanceurs ne signifie pas qu'ils
ont le même rôle. Aucune abstraction supplémentaire nécessaire pour ce lot.
Après installation par winget, le script demande de rouvrir le lanceur pour
recharger le PATH ; il ne prétend pas que la GUI a déjà démarré.

## Correction R10

L'ancienne ligne `if errorlevel 1 pause & exit /b 1` ne conditionnait que
`pause`. La sortie avec code 1 était donc exécutée aussi après succès.
R10 regroupe pause et sortie d'erreur dans le bloc conditionnel et retourne
explicitement 0 après succès. La pause est conservée pour l'usage par double clic.

## Portée et limites

Revue statique des quatre BAT, de leurs références README et de la composition
du portable. Ancien updater BAT/PowerShell absent depuis R9. Aucun script
d'installation, winget ou compilation Windows exécuté ici.
Les scripts d'installation dans les sources ne changent pas le contrat du
portable : aucune installation Python ni téléchargement pour son utilisateur.
La qualification native et le rendu des icônes restent ouverts.

Répartition acceptée par Julien le 27 octobre : petit dessin pour 16/20/24 pixels,
grand pour 32/40/48/64/128/256. Dessin intermédiaire prévu par Julien plus tard,
sans bloquer 2.0. Aucun dessin modifié ou créé.
DEV11 ouverte ; aucune branche créée ni push effectué.
