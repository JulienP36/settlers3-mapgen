# v1.8 DEV_5_R1 — Centre d’export v1

## Cartes

Le bouton principal `Exporter…` ouvre maintenant une fenêtre dédiée avec :

- dossier de destination modifiable ou sélectionnable ;
- nom de base commun, nettoyé uniquement des caractères incompatibles avec Windows ;
- sélection indépendante EDM, MAP, SAV, PNG Global et PNG Vue actuelle ;
- liste en direct des noms exacts qui seront produits ;
- confirmation unique regroupant tous les fichiers déjà existants.

Règles de disponibilité :

- EDM/MAP uniquement pour 768×768, seule taille disposant actuellement de scaffolds validés ;
- SAV uniquement comme copie inchangée d’un véritable SAV importé ;
- l’identité du fichier SAV source est conservée dans les métadonnées de l’output, y compris après affectation et navigation A/B ;
- PNG Global = terrain global sans marqueurs, dans la projection active ;
- PNG Vue actuelle = vue, opacité, projection et marqueurs actuellement sélectionnés.

## Statistiques et Graphiques

Les trois anciens boutons sont remplacés par `Exporter…`, qui ouvre un second centre d’export :

- JSON complet ;
- CSV complet ;
- PNG du graphique actuellement affiché, avec thème, langue et comparaison A/B courants.

Les trois formats partagent le même dossier et le même nom de base. La liste des fichiers et la gestion groupée des écrasements suivent les mêmes règles que pour les cartes.

## Garanties

- Aucun writer SAV ajouté.
- Aucun format binaire ou moteur modifié.
- Aucun export automatique non demandé.
- Aucun rendu imaginaire : les PNG proviennent exclusivement des données réelles de la carte courante.

## Validation interne

- 146 tests de régression PASS.
- Export d’intégration réel EDM/MAP/PNG Global/PNG Vue actuelle PASS.
- 49 validations moteur PASS.
- Checksum binaire PASS.
- Cinq hashes protégés inchangés.

## Checklist Windows

1. Ouvrir `Exporter…` sur une carte générée 768 et vérifier les choix EDM/MAP/PNG.
2. Modifier le dossier, le nom de base et plusieurs cases ; contrôler la liste des fichiers en direct.
3. Exporter EDM/MAP puis recharger les fichiers produits.
4. Comparer PNG Global et PNG Vue actuelle avec une vue non globale et/ou Départs.
5. Refaire l’export vers les mêmes noms et vérifier la confirmation groupée d’écrasement.
6. Importer un SAV, l’affecter à A ou B, afficher une autre carte puis y revenir : la copie SAV doit rester disponible et identique.
7. Dans Graphiques, exporter ensemble JSON/CSV/PNG et vérifier que le PNG correspond au graphique affiché.
8. Vérifier les deux fenêtres en français et en anglais, thème clair et sombre.
