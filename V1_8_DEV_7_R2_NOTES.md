# v1.8 DEV_7_R2 — Historique v2, thèmes et mémoire protégée

## Périmètre

- palette sémantique globale claire/sombre servant de règle aux nouveaux blocs ;
- états explicites pour les familles ttk courantes : normal, survol, pressé, sélectionné, focus et désactivé ;
- styles dédiés au tableau Historique et couleurs alternées maîtrisées ;
- aperçu déterministe de la carte sélectionnée, synchronisé avec projection et réglage des marqueurs ;
- panneau limité aux informations absentes des colonnes : présence A/B, carte affichée, position MRU et chemin source complet ;
- réglage renommé `Capacité de l’historique` ;
- confirmation avant réduction destructive de capacité ;
- sélection conservée au même index après suppression ;
- carte courante et sorties A/B protégées des évictions automatiques ;
- suppression manuelle et vidage total avertissent puis libèrent les slots A/B concernés ;
- un lot complet de quatre cartes reste présent avec la capacité minimale de quatre.

## Garanties

- historique toujours uniquement en mémoire ;
- imports EDM/MAP/SAV, dédoublonnage, source SAV exacte et ordre MRU de R1 conservés ;
- traduction dynamique FR/EN/DE/ES et changement de thème avec le Centre ouvert ;
- moteur de génération v1.5, formats binaires et rendu des cartes inchangés ;
- aucune publication sur `dev` avant validation Windows.

## Validation interne

- 162 tests de régression PASS ;
- 49 validations moteur PASS ;
- checksum binaire PASS ;
- cinq hashes protégés inchangés.

## Checklist Windows

1. En sombre puis en clair, survoler les trois en-têtes et chaque ligne : texte et fond doivent rester lisibles dans tous les états.
2. Parcourir rapidement boutons, cases, listes, onglets, champs et contrôles désactivés dans les fenêtres principale, Batch et exports afin de repérer toute régression du socle global.
3. Sélectionner plusieurs entrées : vérifier miniature, A/B, carte courante, position MRU et chemin complet d’un import.
4. Changer projection, taille des marqueurs, langue et thème avec le Centre ouvert.
5. Supprimer successivement plusieurs lignes : la sélection doit rester au même emplacement, puis reculer sur la dernière ligne restante.
6. Supprimer une carte A ou B, annuler puis confirmer : le slot ne doit être vidé qu’après confirmation.
7. Réduire la capacité sous le nombre d’entrées, annuler puis confirmer ; vérifier le nombre annoncé et la protection de la carte affichée/A/B.
8. Générer un lot de quatre cartes avec une capacité de quatre et vérifier que les quatre résultats restent visibles.
