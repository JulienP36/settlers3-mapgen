# v1.8 DEV_7_R1 — Historique de session v2

## Périmètre

- historique MRU commun aux générations simples, résultats Batch et imports EDM/MAP/SAV ;
- origine explicite et métadonnées utiles dans le sélecteur rapide et le Centre d’historique ;
- imports identiques dédoublonnés à partir du SHA-256 de leur contenu, quel que soit leur chemin ;
- capacité persistante réglable à 4, 8, 12 ou 16 entrées, avec 8 par défaut ;
- actions Afficher, Affecter à A, Affecter à B, Supprimer et Tout vider ;
- historique exclusivement en mémoire, sans fichier de base de données ni surveillance permanente ;
- conservation des références déjà affichées ou affectées à A/B lors d'une suppression ou éviction ;
- restauration du vrai chemin source d'un import, notamment pour garantir la copie SAV inchangée.

## Interface

- sélecteur rapide existant conservé dans l'en-tête ;
- fenêtre redimensionnable `Centre d’historique`, non modale, avec colonnes Origine / Carte / Détails ;
- actualisation dynamique en FR/EN/DE/ES et dans les thèmes clair/sombre ;
- double-clic équivalent à Afficher ;
- ordre MRU : une carte réutilisée remonte en tête sans créer de doublon.

## Garanties

- moteur de génération v1.5 inchangé ;
- formats EDM/MAP/SAV et rendu des cartes inchangés ;
- cinq hashes protégés inchangés ;
- aucune publication sur `dev` avant validation Windows.

## Validation interne

- 160 tests de régression PASS ;
- 49 validations moteur PASS ;
- checksum binaire PASS ;
- cinq hashes protégés inchangés.

## Checklist Windows

1. Générer une carte simple, un lot, puis importer un EDM, un MAP et un SAV : vérifier les cinq origines/entrées dans le Centre.
2. Réutiliser une génération ou réimporter le même fichier : vérifier qu'il remonte en tête sans doublon.
3. Tester Afficher et Affecter à A/B sur une génération, un résultat Batch et chaque format importé.
4. Charger le SAV depuis l'historique après plusieurs bascules, puis vérifier qu'un export SAV reste une copie strictement inchangée.
5. Supprimer une entrée affectée à A ou B : vérifier que le slot reste utilisable.
6. Tester Tout vider, puis les capacités 4/8/12/16 et leur persistance après redémarrage.
7. Changer langue et thème avec le Centre ouvert ; vérifier titres, colonnes, boutons et contraste.
