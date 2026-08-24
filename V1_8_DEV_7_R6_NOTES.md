# v1.8 DEV_7_R6 — Prévision exacte et rétention Batch

## Périmètre

- simulation exacte du cache avant Batch pour toutes les capacités proposées : 4, 8, 12 et 16 cartes ;
- distinction entre les anciennes cartes qui sortiront de l’historique et les nouveaux résultats qui ne pourront pas y rester ;
- avertissement dédié, modal, cohérent avec le thème clair/sombre et disponible en FR/EN/DE/ES ;
- état orange explicite après génération lorsqu’un résultat a bien été produit mais n’est finalement plus conservé dans le cache ;
- résumé de fin indiquant le nombre de résultats hors cache ;
- conservation des comportements R5 validés : annulation, viewer non remplacé s’il est déjà occupé et remplissage pratique d’un viewer vide.

## Garanties

- les résultats hors cache restent consultables dans la fenêtre Batch tant qu’elle demeure ouverte ;
- le calcul prévisionnel ne modifie jamais le vrai cache ;
- moteur de génération v1.5, formats binaires et données déterministes inchangés ;
- aucune publication sur `dev` avant validation Windows.

## Validation interne

- 181 tests de régression PASS ;
- 49 validations moteur PASS ;
- checksum binaire PASS ;
- cinq hashes protégés inchangés.

## Checklist Windows

1. Tester un lot avec chacune des capacités 4/8/12/16 lorsque le cache est plein : un avertissement doit apparaître dès qu’une ancienne carte sera évincée ou qu’un résultat ne sera pas conservé.
2. Vérifier que l’avertissement distingue clairement ces deux quantités et suit le thème actif.
3. Ouvrir l’avertissement en FR/EN/DE/ES et vérifier sa traduction à chaque nouvelle ouverture.
4. Annuler depuis l’avertissement : aucune génération ne doit démarrer.
5. Continuer un scénario trop contraint : les cartes générées mais absentes du cache doivent devenir orange et indiquer qu’elles ne sont pas conservées.
6. Vérifier qu’un lot sans aucune éviction ni perte démarre sans avertissement.
7. Confirmer une dernière fois que le lot ne remplace pas une carte déjà affichée et remplit seulement un viewer vide.

