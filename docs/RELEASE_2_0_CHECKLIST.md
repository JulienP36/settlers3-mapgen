# Checklist de fin de 2.0 — état au 1er novembre 2026

Le périmètre fonctionnel est fixé dans RELEASE_2_0_SCOPE.md.
Cette checklist distingue les preuves reçues des étapes encore à exécuter.
DEV11 est validée ; Julien autorise son push et la publication 2.0 le 1er novembre.

## Terminé pour la passe courante

- [x] Équipes aléatoires, secteurs, quotas et presets globaux acceptés selon les retours consignés.
- [x] Mini-audit Équilibré effectué ; pas de correction urgente retenue.
- [x] Regroupement Diagnostic accepté ; amélioration de lisibilité reportée.
- [x] Updater supprimé ; téléchargements manuels uniquement.
- [x] Icônes utilisateur 16/64 et répartition acceptées ; dessin intermédiaire ultérieur non bloquant.
- [x] Lots contextuels, correction de finalisation et sprites : passe R13 acceptée par Julien.
- [x] Capture finale des lots avec cache/A-B reçue ; sept captures réelles intégrées aux README.
- [x] Audit source de conservation des données R11 et correctif du filtre sauvegardé.
- [x] Revue documentaire R15 : versions, légendes, limites et parcours de publication synchronisés.

Qualification fonctionnelle conservée : R13, 1367 tests distincts et 4 sous-tests,
67 contrôles UI Linux/Tk. Les R14/R15 sont documentaires ; leurs contrôles ciblés
ne constituent pas une nouvelle qualification Windows. La validation utilisateur
n’atteste pas chaque scénario individuel dans toutes les langues.

## Build et essai Windows — passe R15 validée

1. [x] Décompresser les sources actuelles sur Windows, Python 3.12 disponible.
2. [x] Lancer `build/windows/build_windows.bat` depuis ces sources ; le script
   installe les dépendances de construction, compile et qualifie une copie déplacée.
3. [x] Examiner les quatre fichiers de `artifacts/` : ZIP portable, SHA-256,
   SELFTEST.json et QUALIFICATION.json. Exiger PASS et la version/source attendues.
4. [x] Extraire le ZIP ailleurs et lancer `Settlers3MapGen.exe` sans installer
   Python ni télécharger de dépendances pour cette exécution ; garder `_internal`.
5. [x] Vérifier lancement/fermeture, génération et export d’une carte, puis
   présence des icônes dans Explorer, fenêtres, Alt+Tab, barre des tâches et
   Gestionnaire des tâches là où Windows les affiche.
6. [x] Vérifier langue, thème, raccourcis, filtre des départs, configurations et
   catalogue de masques retrouvés après changement de dossier/version. Sauvegarder
   les données personnelles avant cet essai ; garder les exports de l’ancien output.

Retour Julien le 1er novembre : « tout me semble en ordre :D », après les
essais demandés ; acceptation globale de cette passe, détails individuels non précisés.
ZIP SHA-256 : d8f9beaf8448a0a45ecc3b0c55fc51e92f0a6fc9380bbf0db4139b28c9b8dddf.
SELFTEST et QUALIFICATION PASS ; bilan externe BILAN_PORTABLE_DEV11_R15_20261101.md.

Les contrôles automatiques de construction utilisent un APPDATA temporaire ;
ils ne remplacent pas cette vérification avec les données habituelles.
Construction Windows non réalisable dans l’environnement Linux actuel (Wine/IPC).
Le BAT local permet de respecter l’absence de branche et de push intermédiaire.

## Clôture DEV11 puis publication

- [x] Aucun défaut signalé à l’issue de l’essai du portable R15 par Julien.
- [x] Validation globale et publication autorisées par Julien le 1er novembre.
- [ ] Consolider notes/snapshot/TODO, nommer le checkpoint DEV_11 sans suffixe,
  pousser le checkpoint complet sur dev et contrôler la CI Windows de ce commit.
- [ ] Qualifier les artefacts construits à partir de la source finale publiée.
- [ ] À la publication seulement, revoir About/Topics et les informations publiques.
- [ ] Autorisation STABLE reçue ; exécuter promotion main, tag v2.0, Release avec
  sources et portable qualifiés, notes et SHA-256 ; supprimer rc à cette étape.

Aucun nouvel archétype, onglet Départs, éditeur avancé de formules ou Stats 2
n’est nécessaire pour terminer la 2.0. Reports dans TODO_MAPGEN.md.
