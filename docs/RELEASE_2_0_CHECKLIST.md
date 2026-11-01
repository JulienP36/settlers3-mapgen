# Validation et publication de la 2.0 — 1er novembre 2026

DEV11 et la publication STABLE ont été explicitement autorisées par Julien.
Bilan fonctionnel : DEV_11_CHECKPOINT.md. Périmètre : RELEASE_2_0_SCOPE.md.

## Recette accomplie

- [x] Fonctionnalités DEV11, profils/presets, quotas et secteurs acceptés.
- [x] Mini-audit Équilibré, regroupement Diagnostic et reports post-2.0 consignés.
- [x] Lots, correction de finalisation, sprites et capture finale acceptés.
- [x] Données utilisateur auditées et oubli du filtre sauvegardé corrigé.
- [x] Portable R15 construit par Julien sous Windows : SELFTEST/QUALIFICATION PASS.
- [x] ZIP et empreinte contrôlés ; essai utilisateur accepté globalement.
- [x] Documentation FR/EN, captures réelles, About et Topics revus.
- [x] Clôture DEV11 et publication 2.0 autorisées ; checkpoint complet publié sur dev.

Le retour utilisateur accepte la passe, sans détailler chaque scénario individuel.
La source fonctionnelle reste celle essayée ; la promotion change sa version et
les documents/outils de publication. La CI Windows du checkpoint dev doit réussir
avant la promotion main.

## Publication automatique depuis main

Le workflow release-2-0.yml constitue la preuve d’exécution de cette procédure :

1. Vérifier la version STABLE, les hashes protégés, les tests et smokes.
2. Construire le portable x64 et qualifier le runtime figé déplacé.
3. Préparer le ZIP public de sources depuis le commit exact, hors references/.
4. Créer le tag annoté v2.0 ; téléverser les deux ZIP, SHA-256 et rapports dans une Release brouillon.
5. Vérifier les empreintes renvoyées par GitHub, puis publier la Release STABLE.
6. Supprimer rc après succès, seulement si sa pointe est toujours celle autorisée.

Les rapports joints à la Release et publication.json conservé dans les artefacts
Actions font foi pour le build final et la publication. Les sources de reprise
privées conservent séparément references/. Aucun updater automatique.

Après la release : discuter avec Julien de l’usage d’Actions, sans généraliser
les déclenchements à toutes les petites modifications. Aucun nouvel archétype,
onglet Départs, éditeur avancé de formules ou Stats 2 requis pour cette 2.0.
