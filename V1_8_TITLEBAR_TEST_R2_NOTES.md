# Settlers III MapGen v1.8 TITLEBAR_TEST_R2

Candidate expérimentale dérivée de TITLEBAR_TEST_R1, elle-même fondée sur
DEV_7_R10 validée sous Windows.

## Objectif

Tester une identité de fenêtre stable avec barre de titre Windows toujours
sombre, tout en retrouvant une séparation visuelle sans remplacer le cadre
natif du système.

## Changement isolé

- barre native `#202124` dans les thèmes clair et sombre ;
- texte natif clair `#e8eaed` ;
- bordure DWM `#5f6368`, utilisée comme premier essai de séparateur ;
- rôles sémantiques dédiés, prêts à être adaptés par de futurs thèmes ;
- comportement dynamique, Windows Snap et redimensionnement natif conservés ;
- aucune boucle de surveillance et aucun faux cadre Tk ajouté.

## Contrôle Windows demandé

1. Vérifier que la barre de titre reste sombre en thème clair comme en thème sombre.
2. Vérifier si la bordure gris moyen restitue une séparation suffisamment lisible.
3. Contrôler la fenêtre principale et plusieurs fenêtres secondaires.
4. Confirmer que Réduire/Agrandir/Fermer, déplacement, Snap et redimensionnement restent natifs.

La fenêtre d’aide n’est pas incluse dans la liste des fenêtres thémées : elle
utilise encore le `messagebox` natif. Cette exception est inscrite au TODO pour
une décision ultérieure, sans modifier son comportement dans ce test.
