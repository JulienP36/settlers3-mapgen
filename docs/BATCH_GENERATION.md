# Lots : seeds et variantes rapides — DEV11 R12

La fenêtre génère une à quatre cartes successivement, pour comparer des seeds et
quelques variantes sans préparer quatre profils complets.

## Base commune à l’ouverture

Le lot copie les réglages détaillés du générateur et de l’archétype, y compris
sources, fusions, formules appliquées, masques et bonus, ainsi que les vingt
choix de civilisations/équipes et le nombre d’équipes aléatoires. Ces copies
ne dépendent plus de l’éditeur principal. Le résumé visible indique les choix
à l’ouverture ; son infobulle détaille les civilisations et équipes des slots.
Seuls les joueurs demandés par chaque ligne sont utilisés.

Pour reprendre d’autres réglages communs, fermer cette fenêtre, les modifier
dans la fenêtre principale puis rouvrir les lots. Rouvrir une fenêtre de lots
déjà ouverte la remet au premier plan sans remplacer sa base.

## Choix contextuels indépendants

| Sélection principale à l’ouverture | Personnalisé proposé pour le générateur | Personnalisé proposé pour l’archétype |
|---|---|---|
| Deux choix standards | Non | Non |
| Générateur seul personnalisé | Oui, sélectionné | Non |
| Archétype seul personnalisé | Non | Oui, sélectionné |
| Deux choix personnalisés | Oui, sélectionné | Oui, sélectionné |

Les choix standards du générateur sont Classique et Amélioré. Ceux de l’archétype
sont Classique, Continental, Îles individuelles et Îles par équipe. Classique
est bien la géographie native ; Continental est la composition moderne.

Chaque ligne démarre avec les choix présents à l’ouverture. Passer de
Personnalisé à un choix standard puis revenir retrouve la copie initiale :
aucune édition ou destruction de la variante personnalisée. Les deux sélecteurs
sont indépendants : un générateur personnalisé peut utiliser un archétype
standard, et un générateur standard peut utiliser l’archétype personnalisé.

Un générateur standard reprend son preset de contenu pour la géographie choisie.
Un générateur personnalisé conserve ses sections et bonus copiés à l’ouverture.
Un archétype standard reprend son profil de relief ; Personnalisé retrouve le
profil copié, avec ses sources et grilles de masque. Le relief choisi ne remplace
pas le contenu personnalisé sauvegardé. Aucun changement dans la fenêtre principale.

## Paramètres rapides et exécution

Chaque ligne règle mode, archétype, départs, miroir, taille, joueurs et seed.
Le bouton commun Appliquer à tous concerne le seed ; il ne remplace pas les
paramètres des autres champs. Les équipes/civilisations restent communes, sans
nouveau dialogue par ligne. Les presets complets se chargent dans Configurations
avant d’ouvrir le lot ; pas de bibliothèque de presets distincte dans chaque ligne.

Au lancement, chaque requête conserve sa configuration effective et son identité
de cache. La génération utilise cette même copie, sans relire l’éditeur principal
entre deux cartes. Deux tâches identiques peuvent réutiliser le cache. Afficher
et affecter A/B portent sur les résultats générés, indépendamment des réglages
ensuite visibles dans la fenêtre principale.

L’annulation interrompt les tâches en attente après la carte courante. Les
résultats restent accessibles dans la fenêtre selon les règles existantes de
rétention du cache ; aucune modification du moteur de génération dans R12.

## Qualification

Tests des quatre contextes, des allers-retours standard/Personnalisé, des masques
embarqués, de la file et du cache. Essai Tk réel sous Linux/Xvfb, changement de
langue et invariance de la fenêtre principale. Les essais Windows restent
séparés ; capture Batch R12 finale à fournir après validation visuelle.
