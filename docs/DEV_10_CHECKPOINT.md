# DEV10 — checkpoint validé, issu de R66

Le 13 octobre 2026, Julien valide Formule pour la 2.0, confirme avoir déjà testé
le parcours export EDM→éditeur→réexport MAP→jeu, et autorise explicitement le
push de R66 en tant que DEV10 complète. Aucun blocage fonctionnel restant.
Les fichiers/seeds exacts du parcours manuel ne sont pas précisés.

## Périmètre livré

- Finitions UI, masques et sprites utilisateur ; tooltips corrigés.
- Relief adaptatif insulaire, Îles individuelles et Îles par équipe au prorata
  des effectifs ; lacs intérieurs, montagnes réparties et espacement des alliés.
- Nouveau Continental issu de la grande île, calibration terre/océan et
  départage des directions de rivières Amélioré. Classique reste natif.
- Audit des placements et filtres jeu/éditeur (vert/jaune), terrain seul ou
  terrain+objets ; import/export cohérents, équipes indépendantes par défaut.
- Préparation native des exports EDM/MAP, maximum 768 ; import SAV contextuel
  et conversion SAV→nouvelle carte sans restaurer le setup de partie.
- Source Custom Formule V1 : expressions bornées, exemples, erreurs locales,
  source principale/fusions et sauvegarde du profil.

## Validation

Les étapes géographiques, filtres, tooltips/SAV et Formule ont été acceptées
par Julien ; jeu fonctionnel confirmé et parcours éditeur confirmé testé.
Qualification R66 : 1304 PASS distincts consolidés, 2 skips, aucun échec restant
sur les contrôles exécutés ; suite générale et finitions ciblées séparées.
Huit générations des exemples livrés et roundtrip EDM/MAP contrôlés.
Contrôle final : 16 tests de métadonnées/packaging/maintenance PASS ; auto-test
source PASS, 52 sprites présents et hashes protégés exacts.
Les preuves détaillées restent dans les références du ZIP source.

Seules la version du checkpoint, ses métadonnées Windows, le test correspondant
et la documentation changent depuis R66. Aucun algorithme, asset ou preset modifié.

## Reports

Éditeur Formule dédié avec visualiseur et explications : hors 2.0, sans échéance.
Stats 2 : après 2.1. Recherches binaires/runtime et seeds rares : surveillance ou
lots futurs. Tailles >768 et Petites îles abandonnées. Archipel hors 2.0.
Build portable, installation propre, updater et préparation de Release relèvent
de la qualification RC/STABLE ; ils ne sont pas annoncés validés par ce push.

Publication autorisée uniquement sur `dev`, sans suffixe R. Aucun tag ni Release.
