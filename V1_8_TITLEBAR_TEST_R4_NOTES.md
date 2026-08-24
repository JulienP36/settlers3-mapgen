# Settlers III MapGen v1.8 TITLEBAR_TEST_R4

Candidate finale de l’expérience de barre de titre, dérivée de R3.

## Thème sombre inchangé

- barre native : `#15171a` ;
- texte : `#e8eaed` ;
- séparateur interne : `#6f7378` ;
- contour Windows : `#3c4043`.

## Thème clair corrigé

- barre native claire distincte du contenu : `#dfe3e8` ;
- texte sombre : `#202124` ;
- séparateur interne : `#8f969e` ;
- contour Windows : `#aeb3b8`.

## Coût d’exécution

Il n’existe aucune boucle de surveillance. Les attributs DWM et la ligne sont
actualisés uniquement lors de l’affichage d’une fenêtre ou d’un changement de
thème. La ligne est ensuite un widget statique de 1 px, sans activité CPU.

## Contrôle Windows demandé

1. Confirmer que le thème sombre reste visuellement identique à R3.
2. Vérifier que la barre du thème clair est claire, mais distincte du contenu.
3. Vérifier le séparateur dans les deux thèmes et sur les fenêtres secondaires.
4. Confirmer le fonctionnement natif de Snap, déplacement et redimensionnement.

La fenêtre d’aide reste une boîte native hors de l’inventaire thémé et demeure
consignée au TODO.
