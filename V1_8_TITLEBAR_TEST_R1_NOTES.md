# Settlers III MapGen v1.8 TITLEBAR_TEST_R1

Candidate expérimentale dérivée strictement de DEV_7_R10 validée sous Windows.

## Objectif

Tester l'intégration des barres de titre Windows aux thèmes MapGen sans remplacer
le cadre natif du système.

## Comportement attendu

- thème sombre : barre, texte et bordure accordés à la palette sombre ;
- thème clair : retour immédiat aux couleurs claires ;
- changement dynamique sur la fenêtre principale et les fenêtres secondaires ;
- boutons Réduire/Agrandir/Fermer, Windows Snap et redimensionnement natifs conservés ;
- aperçus sans bordure ignorés ;
- repli silencieux si DWM ou un attribut de couleur n'est pas disponible ;
- aucune boucle de surveillance : mise à jour uniquement au changement de thème et
  à l'affichage d'une nouvelle fenêtre.

## Contrôle Windows demandé

- fenêtre principale ;
- Génération par lots ;
- Centre d'historique ;
- centres d'export Carte et Graphiques ;
- boîtes de dialogue personnalisées de capacité et de génération Batch ;
- bascule clair/sombre lorsque plusieurs de ces fenêtres sont déjà ouvertes.

Les sélecteurs de fichiers et boîtes entièrement fournis par Windows peuvent
continuer à suivre le thème du système. Si le résultat n'est pas concluant, cette
candidate sera abandonnée sans modifier DEV_7_R10.
