# Conserver ses données lors d’un changement de version

Sous Windows, les versions source et portable utilisent le même dossier :
`%APPDATA%/Settlers3MapGen`. Il ne dépend pas du dossier où le programme est décompressé.

| Données | Emplacement |
|---|---|
| Préférences d’interface (langue, thème, raccourcis, filtre des départs…) | `settings.json` |
| Configurations de génération enregistrées | `configurations.json` |
| Dessins du catalogue personnel | `masks/` |

Pour changer de version : fermer l’ancienne, décompresser la nouvelle dans un
nouveau dossier, puis la lancer avec le même compte Windows. Aucune copie de ces
trois éléments dans le dossier du programme n’est nécessaire. Ils ne font pas
partie du ZIP distribué. Les configurations enregistrées embarquent leurs grilles
de masque et restent indépendantes des PNG du catalogue.

Le programme ne remplace pas lui-même sa version et ne vérifie pas les mises à jour.
La fermeture préalable évite que deux versions modifient simultanément le même
fichier de préférences ou la même collection.

## Sauvegarde et autre ordinateur

Programme fermé, copier le dossier `Settlers3MapGen` ci-dessus permet de sauvegarder
préférences, collection et PNG. Sur un autre compte/ordinateur, le replacer dans
le dossier APPDATA correspondant avant lancement. L’export de collection JSON
dans Configurations est une autre façon de transférer les presets avec leurs
masques embarqués ; il n’exporte ni les préférences ni le catalogue PNG complet.

Les cartes et exports du dossier `output/` restent à côté du programme. Décompresser
une nouvelle version ailleurs ne les déplace pas : conserver l’ancien dossier
ou copier ses exports avant de le supprimer. L’historique/cache de session n’est
pas une collection de configurations enregistrées et ne remplace pas les exports.

Sans APPDATA, les trois chemins utilisent `Settlers3MapGen` dans le répertoire
personnel. Ce repli sert notamment aux exécutions hors Windows.

## Contrôles de conservation

La lecture des préférences complète les anciens fichiers avec les valeurs par
défaut actuelles ; aucun fichier n’est modifié par cette lecture. Les valeurs
reconnues et valides restent conservées lorsqu’elles sont sauvegardées.
Une collection JSON illisible ou de version inconnue est refusée et bloque les
mutations depuis la GUI, au lieu d’être remplacée par une collection vide.
Les configurations sont validées avant écriture et remplacées par fichier
temporaire ; un échec de remplacement laisse le précédent fichier intact.
Le catalogue exige un écrasement explicite pour remplacer un PNG de même nom.

R11 corrige la sauvegarde GUI du filtre des départs valides, précédemment omise.
Les essais isolés et tests sont conservés dans references/dev_notes/DEV11_R11_QUALIFICATION/.
Ils ne remplacent pas la qualification du véritable portable Windows, encore à faire.
