# v1.8 DEV_9_R2 — candidate Windows

Date : 2026-08-25  
Base : DEV_8_R4 validée sous Windows  
Moteur : v1.5 protégé, inchangé

## Objet

Première distribution Windows x64 autonome de Settlers III MapGen. Le ZIP contient un dossier `Settlers3MapGen` complet avec l’exécutable et ses dépendances privées ; aucune installation Python/pip n’est requise.

R1 est rejetée : elle échouait dès le démarrage car `unittest` avait été exclu du bundle alors que SciPy l’importe via `numpy.testing`. R2 réintègre ce module et étend l’autodiagnostic pour charger toute la chaîne GUI normale ; cette classe de faux PASS est désormais couverte.

## Validation automatisée

- 213 tests de régression PASS localement ; suite rejouée dans le workflow Windows ;
- build PyInstaller `onedir` ;
- exécution du véritable `Settlers3MapGen.exe --self-test`, incluant l’import du runtime GUI normal ;
- lecture effective des profils, bibliothèque native, références/scaffolds et sprites J1–J20 ;
- production d’un rapport JSON et du SHA-256 du ZIP ;
- 49 validations moteur et checksum binaire PASS ; cinq hashes protégés inchangés (5/5).
- fins de ligne des ressources protégées explicitement stabilisées par `.gitattributes` ; les trois ressources embarquées sont revérifiées byte-for-byte par le véritable `.exe`.

## Checklist Windows R1

1. Décompresser entièrement le ZIP et lancer `Settlers3MapGen.exe` sans Python installé.
2. Tester le lancement depuis un dossier normal, le Bureau et un raccourci ; le répertoire courant ne doit rien changer.
3. Générer une carte simple puis un lot ; vérifier le viewer, l’historique, A/B, Stats et Graphiques.
4. Importer un EDM, un MAP et un SAV ; exporter les formats disponibles et confirmer que `output` est proposé à côté de l’exécutable.
5. Fermer/réouvrir après changements de langue, thème et raccourcis ; les préférences doivent persister dans `%APPDATA%/Settlers3MapGen`.
6. Tester clair/sombre, FR/EN/DE/ES, fenêtre d’aide et fenêtres secondaires.
7. Noter précisément le comportement SmartScreen/antivirus et le temps du premier démarrage.

## Limites intentionnelles

- candidate non signée ;
- icône finale pixel art non incluse ;
- updater pour le package exécutable reporté à DEV_10 ;
- aucune GitHub Release avant validation utilisateur.
