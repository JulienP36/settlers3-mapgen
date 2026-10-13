# Sprites fournis — DEV10 R19

Toutes les ressources fournies sont sous assets/sprites, par usage.
PNG originaux, transparence et pixels conservés. Texte ou infobulle selon la place disponible.
Registre/chargeur : application/ui/sprites.py ; provenance/hashes : manifest.json.
PhotoImage partagées par interpréteur Tk, y compris les dialogues.

| Usage | Dossier | PNG | Sprites/frames |
|---|---|---:|---:|
| Éditeur et catalogue | mask_editor | 24 | 24 |
| Minerais | minerals | 5 | 5 |
| Marqueurs de joueurs | players | 1 bande | 20 |
| Dé, aide et recentrage | ui | 3 | 5 |
| Total | | 33 | 54 |

Les dernières copies du 2026-10-06 remplacent les treize dessins précédents.
Seule la gomme change ; les douze autres fichiers sont identiques à R14.
Les onze autres complètent le lot : nouveau, supprimer, importer/exporter,
actualiser, dossier, fermer/annuler, appliquer/confirmer, sauvegarder,
catalogue, effacer tout. Aucun sprite prévu ne manque.

| Fichier fourni | Action |
|---|---|
| nouveau | Nouveau masque (catalogue) |
| poubelle | Supprimer un fichier utilisateur |
| balais | Effacer tout le dessin |
| annuler | Fermer / annuler un dialogue |
| valider | Appliquer / confirmer |
| sauvegarde | Enregistrer dans mes masques |
| importer | Importer / charger une copie |
| exporter | Exporter en PNG |
| rafraichir | Actualiser le catalogue |
| ouvrir-dossier | Ouvrir le dossier utilisateur |
| catalogue | Ouvrir le catalogue |

Miroirs selon la convention des dessins de Julien : horizontal = réflexion
haut/bas (axe horizontal), vertical = gauche/droite (axe vertical).
Rotations gauche/droite et inversion des gris conservées.
Les transformations restent annulables. Les miniatures procédurales sont
séparées dans data/source_thumbnails ; les captures restent dans docs.
Packaging source/Windows et self-test couvrent tout le registre.
R16 réutilise les dessins dans les actions principales compactes et l’historique
(icône seule + infobulle traduite), les exports (icône + texte) et les cinq
minerais du filtre thermique (dessins existants 16 × 16, cache partagé).
Recentrer la carte utilise le PNG original 24 × 24 reçu le 2026-10-06.
Futurs dessins : huit Vue 16 × 16, trois filtres thermiques 16 × 16
(arbres/pierres de construction/poissons), icône du programme. À réception,
quelle que soit la DEV active ; aucune date fixée.
R18 : tous les sprites restent à leur taille originale (24 × 24 pour les actions,
20 × 20 pour soleil/lune). Aucun cache de versions réduites. Boutons compacts
30 × 31 px mesurés ; boutons icône + texte avec padding (5,0,5,1), hauteur 31 px
sur le banc Tk. La largeur suit la traduction/police et l’échelle Tk/OS.
Marges de grille de l’éditeur : 2 px horizontal/1 px vertical sur toutes les rangées.
Les PNG originaux restent inchangés. Dé/thème/slots A/B gardent leurs infobulles.
R19 : poubelle du catalogue seule, 24 × 24, texte en infobulle.
Éditeur/catalogue R19 validés par Julien le 2026-10-06 ; agencement : [UI_LAYOUT.md](UI_LAYOUT.md).

R40 : nouveaux lock_closed/lock_open 16×16 et drapeau vert views/valid_starts,
fournis le 2026-10-09 ; originaux conservés octet par octet. Manifest mis à jour.

R41 : quatre sprites civilisations originaux fournis par Julien, 16×16 RGBA, copiés sans transformation dans civilizations/. Registre commun, manifest et packaging à jour.
