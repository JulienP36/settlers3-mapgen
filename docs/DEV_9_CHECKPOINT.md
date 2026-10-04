# v2.0 DEV_9 — Grandes îles

Checkpoint validé le 2026-10-04, issu de R25, avec renommage de la source
historique en « Grandes îles — relief ondulé ». Le nom visible change dans
les quatre langues ; la clé persistée `large_islands_r21` reste compatible.
Publication autorisée sur `dev`, sans tag ni GitHub Release.

## Périmètre terminé

- Grandes îles : une île de taille comparable et un départ par joueur,
  chenaux navigables et marge extérieure, relief construit indépendamment.
- Source principale Simplex multi-échelles, côte rugueuse et relief intérieur
  à directions plus variées. Cible source 56,5 % de terre, neige 200 ; les
  proportions finales dépendent des transitions et du relief effectif.
- Profil et source de relief raccordés à l’éditeur Archétype commun :
  fusions, masques, seuils, presets et profils sauvegardés.
- Rivières améliorées sélectionnables et générales : adaptation de la
  quantité/longueur à la taille et à la terre disponible ; longueur locale
  selon la masse connectée, branches conservées.
- Défauts : Classique pour le profil Classique, Amélioré pour les autres ;
  mini-marais Grandes îles visible et unique, désactivable.
- Profils chargés en place, Personnalisé conditionnel, molette verrouillée
  sur champs désactivés et resets individuels des sources/fusions/masques.
- Corrections de parité terrain native R9 communes aux moteurs séparés.

## Validation et limites

R25 : 818 tests PASS, sept cartes complètes et quatre exports MAP/EDM PASS,
six côtes R24 exactes, deux cartes R21 et deux Classique exactes ; compilation,
hashes protégés et auto-test extrait PASS. Validation visuelle Grandes îles
reçue de l’utilisateur. La finalisation change uniquement nom/version/docs ;
41 tests ciblés PASS, libellés des quatre langues PASS, smoke Legacy/Upgraded
et checksum PASS, compilation/hashes protégés PASS ; voir RELEASE_VALIDATION.md.

Les optimisations locales du placement et du bruit gagnent environ 30 % sur
ces étapes ; le temps total dépend de la carte et de la relaxation native.
Le push n’atteste pas de nouveaux essais Windows/en jeu sur toutes les tailles.
Les confirmations UI restantes et la viabilité étendue passent au bilan DEV10.
Les références complètes restent dans le ZIP source, hors du tree Git public.

## Suite décidée

DEV9 était centrée sur Grandes îles et est clôturée. Tout ancien report DEV9
hors de ce périmètre passe à DEV10 : bonus (extension, zones minérales,
gemmes/soufre), tooltips, masques enrichis, starts/viabilité et validations.
DEV10 est un panier de travail à trier après publication, pas l’engagement de
tout terminer dans une seule DEV. Les chantiers déjà fixés à la 2.1 restent
à la 2.1. Les finitions seront réparties après le bilan.

Petites îles : DEV10 ou DEV11, par fork de Grandes îles. D’autres archétypes
dérivés peuvent suivre si ce fork aboutit vite ; une DEV11 centrée sur plusieurs
archétypes reste une possibilité. Aucun nouvel archétype n’est implémenté.
Archipel reste hors 2.0. ENDGAME reste pour la fin.
