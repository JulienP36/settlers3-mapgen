# Settlers III MapGen — instructions de travail

- Répondre en français sauf demande contraire.
- Au début d’une tâche, lire `PROJECT_WORKFLOW.md`,
  `references/SETTLERS3_CURRENT_SNAPSHOT.md`, puis uniquement la section utile
  de `TODO_MAPGEN.md`.
- Ordre de confiance : dernière validation utilisateur, build exacte testée,
  état Git vérifié, documentation correspondant à cette build, puis références
  historiques.
- Avant toute modification de génération, EDM/MAP/SAV, export ou données
  natives, lire `references/SETTLERS3_PREGEN_READ_FIRST.md` et vérifier les
  hashes protégés de `PROJECT_WORKFLOW.md`. Ne jamais modifier le moteur v1.5
  sans demande explicite.
- Ne jamais inventer une règle, un ID, une structure binaire ou un résultat de
  validation. Toute carte/preview doit être un rendu déterministe de données
  EDM/MAP/SAV réelles. Aucun asset visuel généré par IA.
- Une suite automatisée réussie ne remplace pas une validation Windows,
  éditeur ou en jeu lorsqu’elle est requise.
- Conserver les candidates `DEV_X_Rn` localement. Ne pousser sur `dev` qu’un
  checkpoint `DEV_X` complet et explicitement validé. Ne jamais pousser sur
  `main`, créer de tag/Release ou réécrire l’historique sans autorisation
  explicite.
- Après une validation, synchroniser le snapshot vivant, le TODO, le changelog
  et les notes utiles. Préserver les changements utilisateur sans rapport.
- Limiter le contexte : lectures et recherches ciblées, sorties bornées, tests
  ciblés pendant le travail puis une suite complète avant livraison. Le dépôt
  est la mémoire canonique ; ne pas rejouer les anciens chats si les documents
  courants suffisent.
