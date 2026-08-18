# Settlers III MapGen v1

Première itération du générateur persistant décidée après la validation longue du profil **Continental**.

## Pourquoi cette v1 existe

Les références Markdown étaient devenues suffisamment riches pour décrire les règles, mais les scripts ponctuels pouvaient encore oublier une étape. La v1 transforme donc les règles verrouillées en :

- pipeline explicite ;
- profil JSON unique ;
- modules génération / format / aperçu / validations ;
- HARD checks bloquant l'export ;
- GUI avec aperçu déterministe de la vraie grille Area ;
- tests de non-régression.

## Portée volontaire de la v1

**Continental 768×768, 2 à 20 joueurs.**

C'est volontaire : 768 est la taille pour laquelle les quotas et références sont les plus complets. L'architecture est prête à recevoir d'autres profils ensuite, sans inventer de scaling implicite.

## Lancer sous Windows

1. Installer Python 3.11+ depuis python.org en cochant `Add Python to PATH`.
2. Double-cliquer `install_and_run.bat` la première fois.
3. Les fois suivantes, `run_gui.bat` suffit.

Dépendances : NumPy, SciPy, Pillow. Tkinter est inclus dans l'installation CPython Windows standard.

## GUI

La fenêtre permet de choisir :

- Continental ;
- 768×768 ;
- 2–20 joueurs ;
- seed déterministe.

Elle affiche :

- aperçu visuel de la vraie `Area` générée ;
- liste PASS/FAIL des invariants ;
- étapes du pipeline ;
- métadonnées de génération.

`Exporter EDM + MAP` reste désactivé si un **HARD check** échoue.

## Règles déjà encodées

- morphologie basée sur la bibliothèque native 768, sans génération d'image imaginaire ;
- Water0..7 hauteur 0 / accessibility 1 ;
- dégradé d'eau contrôlé dans la bande extérieure ;
- suppression des inland Water components 1–4 et redistribution vers une masse d'eau existante ;
- rivières connectées à l'eau, arrêt au premier contact, 0 orpheline, plafond 55 ;
- poissons uniquement à distance 1–12 d'une **vraie Shore48** ; le bord du tableau ne compte jamais comme une côte ;
- 32 313 cases poisson ; quantité +30% par case, saturation 15 ;
- minerais v7 : familles/cellules exactes, petites croissances compactes, quantité +30% ;
- Snow reconstruit depuis relief / profondeur montagne ;
- adultes globaux 1352 + bonus de départ séparé ;
- SmallTree84 = 406 séparés, validés long-play ;
- Building Stones : quota global, stock, bonus local 53 unités/joueur, footprint 7 cellules, espacement conservateur >=4 HEX ;
- aucun objet ordinaire sur Mountain ;
- Swamp -> Reeds only ;
- starts choisis avant les objets, footprint 33 cellules et contraintes de relief ;
- export EDM/MAP via scaffold binaire + checksum validé.

## Important sur la morphologie v1

Pour éviter de réintroduire les régressions de formes, le backend v1 choisit actuellement un des terrains natifs 768 de la bibliothèque puis lui applique uniquement une transformation HEX-compatible globale (identité / 180° / transpose). C'est délibérément conservateur.

La prochaine étape pourra remplacer **uniquement** `morphology.native_template` par un compositeur procédural de formes natives plus varié. Tous les modules resources/objets/validators resteront alors inchangés.

## Structure

```text
s3mapgen/
  binary.py      lecture/écriture/checksum EDM/MAP
  engine.py      pipeline Continental v1
  hexgrid.py     HEX6 / distances / composantes
  model.py       MapState
  preview.py     rendu déterministe
  profile.py     profil JSON
  rules.py       registre pipeline + résultats validation
  gui.py         GUI Tkinter
  cli.py         mode ligne de commande
config/
  continental_768_v1.json
data/
  SETTLERS3_NATIVE_768_STATIC_LIBRARY_v1.npz
  scaffold_768.edm/.map
references/
  références canoniques copiées avec la release
tests/
  smoke tests
```

## CLI

```bash
python run_cli.py --players 20 --seed 2026081902 --out output/test
```

Le CLI refuse également l'export si un HARD validator échoue.

## Ce que la v1 ne prétend pas encore résoudre

- diversification procédurale complète des silhouettes ;
- autres tailles 384–704 ;
- calibration définitive de toutes les hitboxes d'objets ;
- validation runtime SAV automatique après lancement du jeu ;
- archétypes Large Islands / Small Islands ;
- GUI avancée (zoom, couches togglables, édition interactive, presets).

Ces éléments peuvent désormais être ajoutés sans réécrire les invariants déjà acquis.

## Dépannage Windows — Python introuvable

Les lanceurs testent maintenant `py -3` puis `python`.

Si aucun des deux ne fonctionne :

1. lancer `install_python_and_run.bat` pour tenter l'installation automatique via `winget` ;
2. ou installer Python 3.12 64 bits manuellement en cochant **Add Python to PATH** ;
3. relancer ensuite `install_and_run.bat`.

Le raccourci `python.exe` qui redirige uniquement vers le Microsoft Store n'est pas une installation Python utilisable par MapGen.

