# DEV11 — checkpoint complet validé le 1er novembre 2026

Julien autorise explicitement la clôture DEV11, le push du checkpoint complet
sur dev, puis la publication 2.0 sur main avec tag, sources et portable.
Base fonctionnelle : R13 ; R14/R15 documentaires ; portable Windows R15 essayé.

## Changements livrés

- Équipes aléatoires, départs par secteurs et quotas par support compatible.
- Calibration insulaire et préférences sauvegardées, dont le filtre des départs.
- Configurations globales avec sources/masques embarqués et collection JSON.
- Diagnostic regroupé ; mini-audit Équilibré sans correction urgente retenue.
- Lots contextuels, archétype Classique, copies Custom réversibles, cache/A-B ;
  correction du plantage de finalisation et messages insulaires traduits.
- Drapeaux, pipette, soleil/lune et icônes fournis par Julien, sans retouche.
- Updater retiré, README FR/EN et captures réelles actualisés.
- Chaîne de build/qualification du portable Windows et conservation des données.

## Preuves et limites

R13 : 1367 tests distincts, 4 sous-tests, 67 contrôles UI Linux/Tk.
R14/R15 : contrôles documentaires/packaging ciblés, aucune modification moteur.
Portable R15 construit par Julien : SELFTEST et QUALIFICATION PASS ; x64 GUI,
58 sprites, icônes 16–256, démarrage déplacé et Python externe indisponible.
ZIP SHA-256 : d8f9beaf8448a0a45ecc3b0c55fc51e92f0a6fc9380bbf0db4139b28c9b8dddf.
Retour après les essais demandés : « tout me semble en ordre :D ».
Ce retour accepte la passe ; détails de chaque scénario non précisés.
Le parcours éditeur→réexport→jeu avait été confirmé à la clôture DEV10.
Pas de nouvelle attestation exhaustive d’éditeur/jeu par ce checkpoint.
Les références et rapports originaux restent dans l’archive de reprise locale.

## Publication autorisée

Aucun changement fonctionnel entre R15 et DEV11. Version sans suffixe et notes
consolidées ; CI Windows sur le commit exact avant promotion STABLE.
La 2.0 finale sera reconstruite et qualifiée depuis sa source estampillée STABLE,
avec tag annoté v2.0, deux ZIP publics (sources/portable), empreintes et notes.
Le workflow de publication vérifie les empreintes des assets puis publie la
Release et supprime rc seulement après succès. Aucun push intermédiaire Rn.

## Reports

Diagnostic plus lisible, futur onglet Départs et équipes en lot, améliorations
supplémentaires des lots et nouveaux archétypes après 2.0 ; Stats 2 après 2.1.
Éditeur avancé de formules et dessin d’icône intermédiaire ultérieurs, non bloquants.
