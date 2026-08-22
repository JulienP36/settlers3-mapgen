# v1.8 DEV_2_R6

## Header — régions fonctionnelles indépendantes

- Remplace la grille globale widget-par-widget de R5_R5.
- Mode large : Génération à gauche, Session/Comparaison au centre, Langue/Aide/Thème à droite.
- Mode compact : déplacement de blocs entiers ; les contrôles globaux ne sont plus insérés dans les colonnes de Génération.
- Les sélecteurs conservent leurs petits groupes libellé/contrôle.
- Générer/Batch, seed et Importer/Exporter/Aperçu PNG utilisent des barres d'actions locales dont l'espacement ne dépend pas de la ligne supérieure.
- Importer, Exporter et Aperçu PNG utilisent leur largeur textuelle naturelle ; aucune largeur fixe compacte ne tronque les traductions.
- Le comportement du Zoom minimal reste volontairement inchangé pour cette passe.
- Aucun changement du moteur de génération v1.5.

## Validation automatisée

- 86 tests pytest PASS.
- Génération smoke : 49 validations PASS.
- Binary checksum PASS.
- Hashes protégés génération/configuration/bibliothèque native inchangés.

## Validation Windows demandée

1. Grand écran maximisé : vérifier les trois zones et Session/Comparaison au centre.
2. Petit écran maximisé : vérifier les trois zones tant que la place reste suffisante.
3. Minimum ~900 px : vérifier la séparation nette entre Génération et Langue/Aide/Thème, puis Session en dessous.
4. Vérifier les libellés complets Importer, Exporter et Aperçu PNG.
5. Vérifier l'espacement régulier des boutons et l'absence de chevauchement/disparition.
6. Vérifier rapidement Générer lot… (message d'attente uniquement), thème, langue, import/export et commandes existantes.
