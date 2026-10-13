# R41 — marais bonus et civilisations

## 2.0 DEV_10_R44 — maximum 768 et reprise DEV10

Décision de Julien du 2026-10-10 : maximum 768×768 pour l’application.
Tailles 832–1024 retirées de la génération, du batch et de la CLI ; imports
supérieurs à 768 refusés avant remplacement de la session ; export MAP/EDM
supérieur à 768 refusé, y compris par appel direct. Classique, filtres natifs
et moteurs indépendants bornés à 768. Identité Grandes îles de R43 conservée.

Le code du jeu fourni réserve une grille 768 et conserve ce pas de ligne lors
du chargement 1024 : écrasement des données joueurs, erreur reproduite à
+FD0B6. Une nation corrompue observée conduit à l’adresse de la capture.
Julien confirme également qu’une 1024 créée dans United échoue. Investigation
mise de côté à sa demande ; aucun EXE modifié. Les tailles intermédiaires
n’ont pas toutes été essayées individuellement.

Prochains lots : préparation native complète des côtes/marais à l’export,
puis « aucune équipe », puis comparaison des validités jeu/éditeur des starts.
Ne pas annoncer « valide en jeu » ni ajouter une catégorie jaune avant essai.
L’export EDM ne sera pas bloqué pour un départ refusé par l’éditeur.
Voir docs/MAP_EXPORT.md et dev_notes/DEV10_MAXIMUM_768_20261010.md.
Aucun push ni EXE ; DEV10 reste ouverte.


## 2.0 DEV_10_R43 — Classique étendu et identité Grandes îles

Classique accepte désormais les tailles 832, 896, 960 et 1024, avec les mêmes
règles de sélection et garde de carte neuve. Les filtres natifs couvrent aussi
ces tailles. Legacy + Équilibré conserve l’archétype final : l’aperçu de sélection
ne remplace plus Grandes îles par Continental dans les métadonnées/export.
Retour R42 : crash 1024 c0000005 à s3_united.exe+0xFD0B6. Cause non établie,
MAP exact requis ; ne pas annoncer ce crash corrigé. La capture est disponible.
Équipes toujours reportées. Aucun push ni EXE ; DEV10 reste ouverte.


## 2.0 DEV_10_R42 — export MAP/EDM conforme à United

Correction native des hauteurs appliquée à une copie au moment de l’export,
version 11 pour Amazones/marchandises étendues, padding natif et miniature
RGB555 actualisée. Dimensions 832–1024 conservées. Voir docs/MAP_EXPORT.md.
Les équipes restent inchangées et seront le prochain lot. Les sprites R41
sont confirmés impeccables par Julien. TEST_01 est jouable selon son retour ;
les exports exacts R42 restent à tester dans le jeu et l’éditeur United.
Aucun push ni EXE ; DEV10 reste ouverte.


R41 : marais bonus uniquement pour Chinois et civilisation libre (255), sur la
masse terrestre du joueur, avec distances et garde-fous existants. Les slots
retenus des cartes partielles gardent leur civilisation. Diagnostics des bonus
manquants et validations par île adaptés. Quatre sprites civils originaux dans
le filtre Départs valides et les sélecteurs Joueurs, menus thémés.
R40 validée pour les départs : 2780/2780 sur 240 cartes ; relief conservé.
Cas 512/15/4156456048 confirmé : bonus J8 sur île voisine dans R40, corrigé ici.
Validation Windows/éditeur/jeu attendue ; aucun push ni EXE.
Voir docs/PLAYER_STARTS.md et DEV_CANDIDATE_NOTES.md.

## 2.0 DEV_10_R40 — 2026-10-09 — relief et tailles des îles

Amplitude adaptative à la source pour les petites Grandes îles, aperçu partagé,
seuils et amplitude effectifs avec contrôle automatique/manuels. Graphique et
statistiques HEX6 des îles ; nouveaux cadenas et drapeau vert fournis. Comptage
des pierres globales conservé dans les bonus tardifs Équilibrés.
Validation Windows/éditeur/jeu attendue. Aucun push ni EXE.
Voir ISLAND_RELIEF.md et ../DEV_CANDIDATE_NOTES.md.

## 2.0 DEV_10_R39 — 2026-10-09 — diagnostic des départs

R39 : le diagnostic conserve l’état exact au moment de la sélection des départs.
Équilibré avant objets, Classique après objets ; autres placeurs à leur appel réel.
Les cartes importées sans cet historique sont explicitement analysées à l’état actuel.
Filtres MapGen et natifs : refus terrain/bord, occupation/accessibilité, nivellement
séparés ; comptes successifs globaux et par île. Label commun « Filtre ».
Aucune modification du relief, des positions, des ressources ou de l’export.
Validation Windows/éditeur/jeu attendue ; aucun push ni EXE.

# DEV10 — finitions par petits lots

## 2.0 DEV_10_R34 — civilisations communes et couleurs des joueurs

- Choix des quatre civilisations et Choisir disponible dans tous les algorithmes.
- Entrées transmises au cache, batch et CLI, puis exportées dans MAP et EDM.
- Carrés de couleur de 10 px devant les noms, palette existante J1–J20.
- Slots inactifs barrés/désactivés et configuration des vingt slots conservés.
- Algorithmes et reliefs inchangés ; contrôles conservateurs communs hors Classique.
- Choix des couleurs reporté à 2.1 ou après ; icône R33 conservée telle quelle.

## 2.0 DEV_10_R33 — fenêtre joueurs compacte et icône

- Deux listes de dix joueurs, colonnes Joueur / Civilisation / Équipe.
- Équipe numérique courte sur la même ligne, rappel commun « 0 : aucune ».
- Noms des slots inutilisés barrés ; sélecteurs désactivés uniquement pour ces slots.
- Hors Classique, civilisation libre affichée comme texte normal pour les joueurs actifs.
- Icône fournie intégrée au runtime et à la configuration du build Windows.
- Aucune modification des algorithmes, paramètres d’équipes ou formats.

## 2.0 DEV_10_R32 — équipes et libellés

- Choisir en français ; labels joueurs simples, sélecteurs inutilisés grisés.
- Îles — seul ; futur Îles — par équipe noté au TODO.
- Départs → Joueurs… : équipe 0 à 20 par joueur, pour tous les algorithmes.
- Équipes conservées au cache/batch/CLI et exportées dans MAP et EDM.
- Setup corrigé : type Choisir et équipes configurées, plus de valeurs cycliques.
- Aucun changement des positions, règles de validité ou relief insulaire.

## 2.0 DEV_10_R31 — Choose et slots inactifs

- Option Choose (255) vérifiée dans les deux éditeurs et conservée à l’export.
- Slots inutilisés grisés et identifiés ; configuration conservée pour leur réactivation.
- Validité pour les quatre civilisations sur Choose, filtre supplémentaire documenté.
- Nations fixes R30 et génération insulaire R28 conservées.
- Correction documentaire : les Asiatiques acceptent la boue, pas les marais.
- Trois cas fonctionnels ajoutés ; outils de recherche exclus du programme.

## 2.0 DEV_10_R30 — départs Classique

- Retrait complet du repli de relief R29 ; Grandes îles restauré à R28.
- Classique actif dans le menu principal, batch et CLI ; nations explicites
  exportées, placement après contenu global et bonus MapGen de départ désactivés.
- Sélection native et effets successifs de ville : mêmes positions et PRNG
  que le .exe sur neuf scénarios de référence, dont l’échec à un million d’essais.
- Carte conservée si le Classique désactive un slot ; export incomplet explicite.
- 13 cas de régression fonctionnels, aucun outil de recherche ajouté au programme.
- Validation Windows/éditeur/jeu ouverte ; souci des starts insulaires reporté.

## 2.0 DEV_10_R28 — recherche des départs insulaires

- Suppression de l’échantillonnage ; toutes les positions admissibles conservées.
- Marge de carte et dégagement devenus préférences ; contrôles obligatoires inchangés.
- Recherche avec retour sur les choix précédents en cas de conflit de séparation.
- Erreurs précises : terrain/occupation, relief ou combinaison de séparation impossible.
- Quatre tests fonctionnels ajoutés ; aucun port de recherche inactif.
- Le cas Grandes îles 384/8p/seed 42 reste refusé par le relief ; aucune parité Classique revendiquée.
- Rejet global encore présent, aucune validation Windows/éditeur/jeu ni push.


## Candidate locale 2.0 DEV_10_R25 — départs et nivellement

Choix de placement principal/batch/cache/CLI raccordé. Contrat un joueur par île
conservé. Filtre de nivellement actif des domaines neufs pour les quatre profils ;
aucun aplatissement. 144 contrôles natifs sur 36 starts de cinq MAP acceptés.
32 premiers choix maximum pour réessayer une recherche continentale bloquée.
Voisins des rivières bonus vérifiés avant écriture puis réservés pendant les passes.
Les configurations sans assez de candidats admissibles sont explicitement refusées.
Classique exact et validation Windows/jeu restent ouverts. Voir PLAYER_STARTS.md.

## Candidate locale 2.0 DEV_10_R24 — départs visibles

Menu Départs principal/batch/CLI raccordé, stratégies et sécurité R20 conservées.
Quatre modules de recherche non raccordés, outils/fixtures et 171 tests retirés.
Trois nouveaux tests fonctionnels ; bilan détaillé dans docs/PLAYER_STARTS.md.
Classique exact et garantie de validité native restent ouverts. Essai provisoire
MAP→runtime retiré : pas assez qualifié pour devenir un filtre obligatoire.
Validation Windows, deux éditeurs et jeu attendue ; aucun push.


## Historique : 2.0 DEV_10_R22 — sélection des départs natifs

Poursuite autorisée par Julien après R21. Sélection 0x5074B0 portée, isolée :
62 scénarios exacts (appels, slots, PRNG), 1 000 distances et 1 536 tirages exacts ;
quatre épuisements réels d’un million de tentatives exacts.
19 999 offsets ordonnés exacts contre l’initialiseur du jeu. Validité/ville
remplacées par callbacks contrôlés dans ces essais ; pas de parité complète.
Placeur actif R20 conservé. Raccordement runtime/ville, Classique et îles à suivre.
Suite : 1 095 réussis ; un attendu de version R21 corrigé, puis 130 tests PASS.
Référence : references/history/DEPARTS_NATIFS_SELECTION_R22_20261006.md.
DEV10 ouverte, aucun push ; aucun nouvel essai visuel demandé pour ce lot.

## Historique : 2.0 DEV_10_R21 — noyau des départs natifs

Retour Julien : rien de visible signalé dans R20, essais difficiles ; poursuite
explicitement autorisée. Pas de validation complète Windows/jeu déduite.
Noyau isolé : nivellement normal 0x4DA440, filtre 0x4D99E0 et richesse 0x5081A0.
1 000 comparaisons directes EXE : valeur et buffers 31×31 exacts ; 359 essais
sur les seuils de richesse exacts. Objets/flags/claim runtime fournis explicitement,
sans conversion supposée depuis Area. Le placeur actif reste celui de R20.
Tests : 1 027 réussis (574,50 s), dont 45 du noyau ; 16 contrôles maintenance réussis.
Aucune nouvelle commande UI, aucun changement de carte ou bonus dans ce lot.
Classique complet à raccorder après port sélection/PRNG/contexte/initialisation ;
variante îles obligatoire avec un départ par île. DEV10 ouverte, aucun push.
Référence : references/history/DEPARTS_NATIFS_NOYAU_R21_20261006.md ; qualification :
references/dev_notes/DEV10_R21_QUALIFICATION.json.


## Candidate locale 2.0 DEV_10_R20 — validité des départs

Autorisation du 2026-10-06 : correction terrain/objets et resets groupés.
Les placeurs continentaux filtrent désormais occupation/accessibilité, empreinte
normale et 70 offsets du contrôle éditeur. Grandes îles conserve un départ par
île et le même filtre ; séparation minimale 50 en coordonnées euclidiennes.
Les cellules utiles des tours sont protégées lors de la reprise des terrains
non archétypaux et des objets Legacy ; aucune peinture forcée d'herbe.
Contrôle final des départs : échec explicite en cas d'incompatibilité, sans
suppression silencieuse d'objets ni déplacement qui désynchroniserait les bonus.
Resets individuels : source/bruit/type de masque conservés ; dessin manuel
conservé avec remise à zéro des paramètres. Piles et reset global inchangés.
Les moteurs de terrain sans bonus et les assets protégés restent inchangés.

Exigence ferme : futur algorithme **Classique exactement identique au jeu**,
avec sous-algorithme pour les îles. Le placeur provisoire R20 n'est pas ce
Classique. Test de nivellement 0x4DA440 et sélection native complète à porter
et qualifier avant de déclarer la parité des départs. Aucun nouveau sélecteur
ni stratégie d'équilibrage livré ici. Risque : manque de candidats admissibles
sur une carte très dense ; échec explicite, pas de relâchement de sécurité.
DEV10 reste ouverte, aucun push. Validation Windows/éditeur/jeu attendue.
Audit : references/history/CONDITIONS_PLACEMENT_DEPARTS_20261006.md.
Qualification : references/dev_notes/DEV10_R20_QUALIFICATION.json.


## Candidate locale 2.0 DEV_10_R19 — catalogue allégé

R18 appréciée par Julien : « excellentes modifications ». Ajustements du catalogue
et du gap Copier seed/Importer autorisés le 2026-10-06, repris dans R19.
Catalogue : ligne unique Nom · Taille (Variable pour les modèles), sans retour
à la ligne ; noms longs tronqués selon la police, nom complet en infobulle.
Charger une copie et poubelle 24 × 24 sur la même rangée pour les fichiers custom,
avec 4 px d’écart. Suppression toujours confirmée, infobulle traduite et thémée.
Les messages des fichiers invalides restent visibles sur une ligne séparée.
Sprites originaux et reflow mesuré R18 conservés ; aucune relecture au resize.
Copier seed/Importer : gap de 7 à 4 px, identique aux autres boutons voisins.
Qualification : references/dev_notes/DEV10_R19_QUALIFICATION.json.
DEV10 ouverte ; aucun push ni EXE, génération/données natives inchangées.
R19 validée par Julien le 2026-10-06 ; étape 4 limitée à l’éditeur/catalogue clôturée. Aucun nouveau test ajouté.
974 tests PASS (856.51 s) ; Tk quatre langues/deux thèmes, compilation et packaging PASS.
Molette validée ; resets valides mais doivent conserver le bruit sélectionné (DEV10).
Exports/EDM/MAP et erreurs avec bouton Copier : chantier dédié DEV11 ou DEV12.
Ouverture 832–1024 validée globalement dans l’éditeur modifié Settlers United ; réexport vers le jeu non fonctionnel.
Future MAJ pixel art distincte du lot éditeur/catalogue et des dessins récents.

## Candidate locale 2.0 DEV_10_R18 — sprites et agencement adaptatif

R17 appréciée avec corrections demandées : réduction des sprites refusée et
agencement/repositionnement encore trop espacés. R18 reprend ces points.
Sprites originaux 24 × 24 conservés, y compris avec texte ; aucun redimensionnement.
Éditeur : annuler/rétablir, transformations et importer/exporter/catalogue
partagent padx 2/pady 1 ; boutons à padding (5,0,5,1), hauteur Tk mesurée 31 px.
Catalogue : libellés/actions regroupés à côté de la vignette, fiches compactes ;
colonnes calculées avec la largeur requise des fiches, sans seuil fixe ni plafond.
En français : fiche + marges 259 px, deux colonnes à 560 px, trois à 800 px.
En-tête, Session et barre Vue : demandes Tk et marges réelles remplacent les
seuils fixes ; en-tête recalculé après sa propre allocation, langues prises en compte.
À largeur minimale, les commandes globales passent sur une rangée supplémentaire.
Générateur/bonus : rangées indépendantes pour éviter les colonnes partagées qui
créaient des espaces ; réserve supplémentaire de 32 px supprimée, viewport mesuré.
Disposition automatique des previews et ses seuils de lisibilité conservés.
F11 55/45, infobulles et disponibilité PNG de R17 conservés.
DEV10 ouverte ; aucun push ni EXE. Génération et données natives inchangées.
Qualification : references/dev_notes/DEV10_R18_QUALIFICATION.json.
Validation visuelle Windows R18 attendue. Aucun nouveau test ajouté.
974 tests vérifiés : 918 PASS en suite complète ; 56 erreurs de simulateur corrigées, 57 tests concernés PASS en relance.
Compilation et contrôles de packaging PASS ; aucun changement applicatif après lancement de la suite.

## Candidate locale 2.0 DEV_10_R17 — calibration et catalogue compact

R16 jugée « pas trop mal » par Julien ; ajustements demandés repris dans R17.
Boutons à icône seule : enveloppe commune 30 × 31 px mesurée (dé +1 px),
sprite 24 × 24 et marges minimales ; soleil/lune 20 × 20 avec compensation.
Images accompagnées de texte : affichage 16 × 16, cache par taille, PNG originaux
inchangés ; hauteur identique aux boutons textuels (33 px dans le banc Tk).
Les dimensions finales des boutons textuels suivent la police et l’échelle Tk/OS.
Infobulles traduites pour dé (principal/lot), thème (action suivante/raccourci)
et suppression des slots A/B ; autres actions compactes conservées.
Annuler/rétablir : mêmes colonnes, padx 2/pady 1 que les transformations.
Catalogue : modèles « Variable », fichiers utilisateur avec taille réelle ;
actions à 8 px des libellés, sans colonne centrale extensible, grille conservée.
F11 : vue 55 % / onglets 45 %, maximisation et ancrage supérieur conservés.
Enregistrer l’aperçu PNG désactivé au démarrage, activé au chargement comme Exporter.
DEV10 ouverte ; aucun push ni EXE. Génération et données natives inchangées.
Qualification : references/dev_notes/DEV10_R17_QUALIFICATION.json.
Suite complète : 974 tests PASS (1016.70 s), aucun nouveau test.
Tk réel quatre langues/deux thèmes, mesures et actions du lot PASS.
Compilation, intégrité et self-test après extraction PASS.
Validation visuelle Windows R17 attendue.


## Candidate locale 2.0 DEV_10_R16 — agencement et sprites partagés

R15 acceptée par Julien avec ajustements d’agencement demandés, repris dans R16.
Annuler/rétablir espacés ; importer/exporter côte à côte, catalogue en dessous.
Catalogue : actions alignées et séparées, grille adaptative de 1 à 4 colonnes.
Le redimensionnement réutilise les fiches et images ; aucun PNG relu à cette occasion.
Éditeur/catalogue : fenêtres redimensionnables avec agrandissement natif disponible.
Sprites réutilisés dans les actions compactes (infobulles localisées), l’historique
et les dialogues d’export ; cinq dessins de minerais dans le filtre thermique.
Nouveau dessin original Recentrer la carte intégré : 33 PNG, 54 sprites/frames.
F11 configurable : maximise le programme et rétablit les deux séparateurs
(position naturelle sous les contrôles, proportion vue/onglets 3:2).
F11 ne modifie ni le zoom ni la position de la carte ; Ctrl+R recentre la carte.
Un déplacement manuel reprend la main sur le séparateur horizontal.
DEV10 reste ouverte ; aucun push ni EXE. Génération et données natives inchangées.
Qualification : references/dev_notes/DEV10_R16_QUALIFICATION.json.
Suite complète : 974 tests PASS (557.10 s), un nouveau scénario F11.
Tk réel : quatre langues/deux thèmes, catalogue peuplé, historique/exports PASS.
Compilation, intégrité des sprites/génération et self-test après extraction PASS.
Validation visuelle Windows R16 attendue.


## Candidate locale 2.0 DEV_10_R15 — lot complet de sprites

R14 validée par Julien le 2026-10-05, avec inversion des deux miroirs signalée.
R15 corrige leur action selon les dessins : miroir horizontal inverse haut/bas,
miroir vertical inverse gauche/droite. Les actions restent annulables.
Les deux lots du 2026-10-06 couvrent les 24 sprites de l’éditeur/catalogue.
Les 13 existants sont remplacés par les dernières copies : seule la gomme change ;
les 12 autres sont identiques. Onze nouveaux dessins, PNG originaux conservés.
Icône + libellé sur les actions restantes, catalogue et dialogues thémés.
Fermer est également accessible dans le catalogue ; comportements conservés.
32 PNG au registre commun (53 sprites/frames). Aucun sprite du lot ne manque.
Suite complète : 973 tests PASS (545.88 s), aucun nouveau test.
Tk réel : boutons/catalogue/dialogues/sauvegarde, miroirs/undo, quatre langues
et deux thèmes PASS. Éditeur 686 px de haut sur écran 1366×768.
32 ressources, PNG originaux, génération inchangée, compilation et self-test PASS.
R15 acceptée avec remarques UI, traitées dans R16.
DEV10 reste ouverte, aucun push ni EXE ; génération et données natives inchangées.


## Candidate locale 2.0 DEV_10_R14 — deuxième lot d’icônes

R13 validée explicitement par Julien le 2026-10-05.
R14 intègre huit nouveaux PNG originaux 24×24 : annuler/rétablir, inverser les
gris, miroirs horizontal/vertical, rotations gauche/droite et remplissage.
Icônes + texte, cache partagé et thèmes/langues conservés. Remplissage par clic
de la zone contiguë de gris identique (4 voisins), avec le gris choisi.
Un clic = une action annulable ; cliquer sur le même gris ne crée pas d’historique.
Le clic droit reste la gomme ; rayon/bord doux ne changent pas le remplissage.
Rotations ±90° sans interpolation, annulables. Vingt-et-un PNG au registre.
Deux nouveaux scénarios automatisés pour frontières/historique et taille 512.
Génération et données natives inchangées ; DEV10 ouverte, aucun push ni EXE.
Suite complète : 973 tests PASS (564.66 s), deux nouveaux scénarios.
Tk réel : remplissage/historique/rotations, quatre langues/deux thèmes PASS.
Écran 1366×768 : éditeur 665 px de haut ; 21 sprites et self-test PASS.
55 fichiers de génération et 13 PNG précédents identiques à R13.
Compilation, maintenance documentaire et hashes protégés PASS.
R14 validée par Julien ; miroirs inversés signalés, corrigés dans R15. Suite des dessins par petits lots.


## Candidate locale 2.0 DEV_10_R13 — premier lot d’icônes et rangement

R12 : vignettes jugées très bien par Julien ; calcul hors ligne confirmé.
R13 intègre le premier lot dessiné par Julien : pinceau, gomme, pipette, rond,
carré. Les cinq PNG RGBA 24×24 sont copiés à l’identique, sans redessin.
Icône et libellé dans les menus et la sélection ; comportements de dessin,
événements, langues et thèmes conservés. Images réutilisées entre éditeurs.
Les sprites fournis sont regroupés sous assets/sprites par usage : éditeur,
minerais, marqueurs de joueurs et interface. Treize PNG (34 sprites/frames),
chargeur commun, registre, provenance/hashes et packaging source/Windows adaptés.
Les huit PNG précédents sont déplacés byte pour byte. Le self-test contrôle
les treize ressources. Vignettes procédurales et captures restent distinctes.
Suite complète : 971 tests PASS (578.37 s), deux nouveaux scénarios.
Tk réel : outils/formes, quatre langues/deux thèmes et photos partagées PASS.
Treize ressources, huit anciens PNG exacts et génération inchangée : PASS.
Compilation/self-test/protected hashes PASS.
Guide : docs/SPRITES.md ; qualification : references/dev_notes/DEV10_R13_QUALIFICATION.json.
R13 validée explicitement par Julien le 2026-10-05 ; DEV10 ouverte, aucun push ni EXE.


## Candidate locale 2.0 DEV_10_R12 — vignettes des sources

R11 validée et fonctionnelle selon Julien le 2026-10-05.
R12 ajoute vingt vignettes fixes pour les bruits et compositions dans le choix
de source principale et les six fusions. PNG 64×64 affichés en 24×24 ;
échantillons réels, seed/réglages constants, sans fusions ni masques.
Ce sont des repères de sélection ; les aperçus de travail restent dynamiques.
Images partagées entre sélecteurs, réutilisées après changement de langue ;
aucune génération au démarrage ou à l’ouverture des menus. Menus thémés,
état désactivé et navigation clavier conservés ; sélection inchangée sans action.
Provenance et hashes : data/source_thumbnails/manifest.json ; reconstruction
hors interface : tools/generate_source_thumbnails.py. Aucune règle native modifiée.
Suite complète : 969 tests PASS (599.00 s), deux nouveaux scénarios.
Tk réel : sept sélecteurs, quatre langues, deux thèmes, menus sans recalcul PASS.
55 fichiers de génération identiques à R11 ; compilation/self-test/hashes PASS.
Qualification : references/dev_notes/DEV10_R12_QUALIFICATION.json.
Validation Windows R12 attendue ; DEV10 ouverte, aucun push ni EXE.


## Candidate locale 2.0 DEV_10_R11 — masquage exact et vues persistantes

R10 validée par Julien le 2026-10-05. R11 ajoute le lot autorisé :
Masquer, permissions exactes noir=0/blanc=100%, gris proportionnel, force
0–100% initialisée à 100% lors du choix et inversion conservée dans le profil.
Les permissions se cumulent ; sur une fusion elles bornent sa contribution,
et ne remplacent pas le champ par zéro avant Mélanger/Minimum/etc.
Les modulations existantes gardent leur ordre ; aucune ne réactive une zone
bloquée par une permission sur la même cible. Une fusion suivante peut agir
sur une source masquée ; cible Résultat pour masquer la composition entière.
Vues libres, fixées en haut (défaut), à droite ou automatiques ; préférence
persistante. Zone de réglages indépendante du panneau fixe ; auto selon la
largeur/hauteur réelle de l’onglet, avec hystérésis. Changer le placement ou
la taille redessine les champs en cache sans relancer la génération ni
reconstruire les réglages. Clic sur une vue : agrandissement thémé du dernier
champ calculé, statistiques et légende macro accessibles.
Vignettes 24×24 dans le menu de masques et sur la sélection ; formes calculées
une fois, dessins copiés dans le profil, PNG invalides exclus, caches bornés.
Vignettes fixes des bruits/compositions : lot suivant distinct, pas implémentées.
Six nouveaux scénarios ; suite complète : 967 tests PASS (588.60 s).
Tk réel PASS : défilement fixe, placements sans régénération, masques et caches.
Parité exacte R10/R11 sur quatre previews 384 ; deux cartes complètes masquées
Legacy/Amélioré et exports EDM/MAP (checksums) PASS. Compilation/self-test PASS.
Détails : references/dev_notes/DEV10_R11_QUALIFICATION.json.
R11 validée et fonctionnelle selon Julien le 2026-10-05.
DEV10 reste ouverte ; aucune publication Git ni construction EXE.


## Candidate locale 2.0 DEV_10_R10 — cibles des masques et dialogues centrés

R9 validée par Julien le 2026-10-05. R10 implémente l’étape 3 autorisée :
chaque masque cible Défaut (résultat), Source principale ou Fusion 1–6.
Source : avant les fusions ; fusion : sur son propre bruit avant mélange ;
résultat : après toutes les fusions. Les profils anciens gardent Défaut.
Plusieurs masques sur une cible suivent l’ordre de la liste. Les miniatures
source/fusion affichent leur masque ; une cible absente/désactivée est signalée
et sans effet, sans redirection. Le masque suit sa fusion réordonnée ; sa
suppression conserve une cible supprimée à réaffecter explicitement.
Les dialogues thémés sont centrés sur leur parent, après calcul de leur taille,
et bornés à l’écran. Aucun changement de générateur/format binaire demandé.
Cinq nouveaux scénarios fonctionnels. Suite complète : 961 tests PASS (557,36 s).
Tk réel PASS : cibles, édition, déplacement/suppression et dialogues centrés.
Parité exacte R9/R10 : quatre previews 384 avec/sans masques résultat ; deux
cartes complètes ciblées passent leurs contrôles obligatoires. Compilation,
hashes protégés, auto-test extrait, CRC/parité archive PASS. Qualification :
references/dev_notes/DEV10_R10_QUALIFICATION.json. Fonctionnement R10 confirmé par Julien le 2026-10-05.
DEV10 reste ouverte ; candidate source locale, aucun push ni build EXE.
Suite du lot masques : bilan des sprites existants et des dessins/taille à fournir
avec Julien, après validation de l’étape 3 ; réorganisation non faite ici.
Les menus « suite » restent centrés sur la branche actuelle.


## Candidate locale 2.0 DEV_10_R9 — éditeur et sélection directe des masques

R8 : fonctionnement confirmé par Julien, avec remarques UI reprises dans R9.
R9 : fenêtres et confirmations de masques sous une infrastructure commune de
thèmes sémantiques, y compris changement de thème sur les fenêtres ouvertes.
Les sélecteurs de fichiers natifs restent régis par le système. Nouveau masque
est déplacé dans le catalogue : nouveau document vide, confirmation des dessins
modifiés, nom et historique remis à zéro ; Effacer tout reste une édition annulable.
Fermer / Enregistrer dans mes masques / Appliquer au profil sur une ligne.
Éditeur redimensionnable, dessin carré centré, coordonnées adaptées sans changer
la résolution, rafraîchissements regroupés au prochain idle. Contour du pinceau
rond/carré et nom/états PNG et profil visibles séparément.
Mes masques est directement accessible dans le sélecteur de la couche : PNG
carrés valides, vérifiés progressivement ; invalides/rectangles restent au
catalogue avec diagnostic/cadrage. Actualisation à chaque ouverture du menu et
relecture du fichier choisi ; cache partagé borné. Grille, résolution et nom sont
copiés dans le profil, sans dépendance au fichier après sélection.
Étape 3 différée. Réorganisation des sprites lors du prochain ajout fourni par
Julien, avec inventaire des fichiers et dessins effectués par le code ; pas maintenant.
Préférence de collaboration : proposer spontanément des améliorations pertinentes,
en distinguant le lot actuel des idées pour plus tard.
18 tests ciblés PASS (1,44 s), deux nouveaux scénarios seulement ; compilation PASS.
Essais Tk réels sous Linux PASS : redimensionnement/dessin, boîte de nom et sauvegarde,
restauration du focus/grab, catalogue, exclusion PNG invalide et rectangle,
démarrage MainWindow et propagation clair/sombre sur l’éditeur ouvert.
956 scénarios vérifiés : suite complète (946 PASS), puis reprise des dix contrôles
UI/docs corrigés (10 PASS). Aucun échec restant. Auto-test de ressources PASS.
R9 validée par Julien le 2026-10-05 : tout fonctionne bien. Réserve mineure :
le dialogue de confirmation de sortie apparaît en haut à gauche de l’écran.
À corriger dans la prochaine révision : centrer les dialogues de l’éditeur sur
leur fenêtre parente, après calcul de leur taille, en restant dans l’écran utile.
Aucun code modifié pour cette prise de notes ; aucun push.


## Candidate locale 2.0 DEV_10_R8 — commandes de dessin et sauvegarde visible

R7 validée par Julien le 2026-10-04 : « c’est parfait, tout semble bien fonctionner ».
Retour complémentaire : l’étape 2 doit être enrichie avec un curseur de sélection
et des commandes de dessin ; ne pas passer à l’étape 3 dans cette candidate.
R8 ajoute un curseur de gris, un dégradé cliquable et une pastille de la valeur
choisie ; curseurs rayon/bord doux synchronisés aux champs, y compris la pipette.
Choix rond/carré, chacun dur ou doux. Nouveau masque remet une copie à zéro et
vide son nom, avec undo possible ; aucune application automatique au profil.
La sauvegarde existait en R7 : son bouton est désormais visible en bas près
 d’Appliquer au profil. Un nouveau nom enregistre un nouveau PNG utilisateur.
Boutons groupés sur deux colonnes pour limiter la hauteur de la fenêtre.
22 ciblés PASS (1,66 s), dont deux nouveaux tests, traces Tcl réelles et fichiers PNG.
Compilation PASS. Suite complète : 954 tests PASS (546.00 s). Archive : CRC, parité source et auto-test extrait PASS. Fonctionnement R8 confirmé par Julien ; remarques UI traitées dans R9.
Toute la génération et les données exactes R7. Aucun push, DEV10 reste ouverte.
Étape 3 ciblage/source dessinée différée. Étape 4 éventuelle : icônes dessinées
et fournies par Julien pour apporter de la couleur, sans asset généré par IA.
Qualification : references/dev_notes/DEV10_R8_QUALIFICATION.json.

## Candidate locale 2.0 DEV_10_R7 — catalogue et éditeur de masques

R6 validée et fonctionnelle selon Julien le 2026-10-04. R7 implémente les étapes
1 et 2 du brainstorm approuvé : dossier masks dans les données utilisateur,
catalogue avec miniatures, ouverture du dossier/actualisation, ajout/suppression
et protection des modèles fournis. PNG externe reconnu sur son contenu réel ;
fichier illisible, animé ou excessif écarté individuellement avec un motif.
Couleur convertie en gris, transparence sur noir, masque uniforme utilisable.
Rectangle : choix explicite entre marges noires, recadrage central et étirement.
Éditeur : gris 0–255, rayon, bord dur/doux, gomme, pipette, undo/redo par trait,
inversion, miroirs et rotation. Résolutions 64/128/256/512, profil portable à sa
résolution ; cache du catalogue borné, miniatures ajoutées au prochain cycle idle.
Appliquer au profil, enregistrer dans mes masques et exporter sont distincts.
Six comparaisons de calcul 64 × 64 exactes R6 ; moteurs/données natives inchangés.
159 ciblés profils/masques PASS (90,98 s) ; 21 ciblés UI/architecture PASS (1,48 s).
Huit nouveaux tests au total. Compilation PASS. Suite complète : 952 tests PASS (544.24 s). Archive : CRC, parité source et auto-test extrait PASS.
R7 validée par Julien le 2026-10-04 ; aucun push, DEV10 reste ouverte.
Étape 3 proposée par Julien : cibler source principale/fusion ou utiliser le dessin
comme source de relief autonome. À cadrer après validation R7, non implémentée.
Qualification : references/dev_notes/DEV10_R7_QUALIFICATION.json.

## Candidate locale 2.0 DEV_10_R6 — langue du rapport Statistiques

R5 acceptable pour le moment selon Julien le 2026-10-04 : « on va dire qu’on est bon
pour le moment ». Aucun détail de scénarios Windows fourni ; DEV10 reste ouverte.
R6 corrige le rapport resté dans l’ancienne langue sans régénération. Le callback
existait mais Tk ignorait ses écritures dans le champ Text désactivé. L’écriture
est maintenant temporairement autorisée, puis l’état lecture seule et le défilement
sont restaurés. Carte, widget et statistiques en cache conservés.
L’audit statique précédent avait conclu à tort que cette traduction fonctionnait.
Un seul nouveau test reproduit ce défaut avant correction, puis vérifie EN/DE/ES/FR.
75 ciblés PASS (1,56 s). Suite complète : 944 tests PASS (684.70 s). Archive : CRC, parité source et auto-test extrait PASS.
R6 validée et fonctionnelle selon Julien le 2026-10-04 ; aucun push de candidate.
Refonte complète Statistiques : mise à jour dédiée après 2.1, contenu enrichi,
organisation et visuels plus jolis et interactifs ; version précise non décidée.
Qualification : references/dev_notes/DEV10_R6_QUALIFICATION.json.

## Candidate locale 2.0 DEV_10_R5 — blocage au démarrage R4

Julien signale le 2026-10-04 : run_gui.bat tourne sans fenêtre ni erreur.
Cause reproduite dans le constructeur des onglets : winfo_ismapped est faux
sur une page masquée même si ses barres sont déjà placées dans grid. R4 les
replaçait donc à chaque callback idle, puis reprogrammait le même callback.
La boucle pouvait empêcher update_idletasks de rendre la main au démarrage.
R5 compare le gestionnaire grid, indépendant de la visibilité de l’onglet.
Les mises à jour regroupées et correctifs des séparateurs R4 sont conservés.
Le lanceur BAT est inchangé ; aucun délai visuel fixe réintroduit.
Deux scénarios reproduisent la boucle avant correctif (échecs attendus), puis
se stabilisent après : onglet masqué et retrait/retour de ses barres.
193 ciblés PASS (8,64 s), deux nouveaux scénarios ; compilation PASS.
Suite complète : 943 tests PASS (729.71 s). Archive : CRC, parité source et auto-test extrait PASS. Démarrage/rendu Windows à confirmer.
R4 n’est pas validée ; ses tests/auto-test de ressources ne testaient pas ce cycle.
Génération et données natives exactes R4 ; hashes protégés PASS. Aucun push.
Qualification : references/dev_notes/DEV10_R5_QUALIFICATION.json.

## Candidate locale 2.0 DEV_10_R4 — séparateurs internes

Retour Julien sur R3 : peu de différence visible ; les redimensionnements
visés sont les séparateurs vue/onglets et contenu/inputs, pas seulement la fenêtre.
R3 n’est pas validée visuellement ; ses changements internes sont conservés.
R4 supprime les limites 160 px/20–65 % du séparateur supérieur. Par défaut,
il suit la hauteur réelle des inputs ; le haut ne reçoit plus l’espace gagné
par agrandissement. Une position manuelle reste en pixels, y compris zéro ou
un panneau partiellement masqué. Position proche des inputs = ancrage automatique.
Préférence vertical_split_height ; anciens ratios ignorés pour ce comportement.

Délais visuels fixes retirés : vue/graphique/onglets 24 ms, miniature adaptative
100 ms. Une seule mise à jour par lot au prochain cycle idle, sans temporisateur
relancé pendant le glissement. La carte n’est plus déplacée à son ancienne taille
avant son redessin. Ancienne PhotoImage conservée jusqu’au remplacement attaché
au canvas, pour la vue et le graphique. Délais calcul de relief et molette inchangés.
220 ciblés PASS (7,55 s), dont cinq nouveaux scénarios ; compilation PASS.
Suite complète : 941 tests PASS (684.16 s). Archive : CRC, parité source et auto-test extrait PASS. Validation visuelle Windows à venir.
Génération/formats/données natives identiques R3 ; hashes protégés PASS.
Bruit Custom via une ou plusieurs équations manuelles non implémenté : bilan
fin DEV10 pour faisabilité/intérêt, puis décision de programmation éventuelle.
Aucun push ; DEV10 ouverte. Qualification : references/dev_notes/DEV10_R4_QUALIFICATION.json.

## Lot 3 — 2.0 DEV_10_R3 — mises à jour UI

Base R2 validée ; candidat source local, validation visuelle Windows à venir.
Les modes Classique/Amélioré et les resets Générateur chargent désormais les
valeurs dans les contrôles existants. Les dépendances sont rafraîchies après
le chargement complet, sans états intermédiaires propagés par les traces Tcl.
Une sortie de champ sans modification ne crée plus de profil Personnalisé.
Une modification Générateur seule ne recalcule plus le relief Archétype.
Les reconstructions de langue restent autorisées ; leurs anciens callbacks
de redimensionnement et travaux différés sont retirés. Les dispositions
inchangées ne sont plus réappliquées et le dernier aperçu calculé est redessiné
sur les nouveaux canvas pendant la reconstruction.

179 tests ciblés PASS (9,41 s), dont 57 cas de cycle UI avec traces Tcl réelles,
modes/resets dans les quatre langues, identité des contrôles, dépendances,
callbacks et aperçus. Géométrie testée avec des widgets de simulation : aucun
contrôle visuel Windows revendiqué. Suite complète : 936 tests PASS (745.40 s). Archive : CRC, parité source et auto-test extrait PASS.
Génération, formats et données natifs identiques aux octets R2 ; hashes protégés PASS.
R1/R2 restent validées ; DEV10 ouverte, aucun push de candidate.
Détail : references/dev_notes/DEV10_R3_QUALIFICATION.json.

Le 2026-10-04, Julien demande de commencer par les tâches courtes puis de
réévaluer la charge au fur et à mesure. Le périmètre final de DEV10 reste ouvert.

## Lot 1 — 2.0 DEV_10_R1

Extension maximale commune du forçage des cinq bonus : 2–512 HEX au-delà
de la cible, défaut 34. Les anciennes sauvegardes retrouvent 34 ; le réglage
participe au digest/cache et au reset Bonus. Le champ est grisé lorsque le
forçage est OFF. Aucun changement des couronnes, hitboxes ou quotas.
Aides minérales/bonus complétées en FR/EN/DE/ES, occupation clarifiée.

Contrôles ciblés : 150 PASS (11,34 s). Quatre générations complètes comparées
à DEV9 : Area et départs exacts, Legacy/Upgraded et forçage ON/OFF,
validations dures PASS. Hashes protégés PASS. Suite complète : 851 PASS (539.10 s).
R1 validée par Julien le 2026-10-04 ; détail des manipulations non fourni.
Candidate locale sans push. Base publiée : DEV9,
`9b0cf36d4f07a7bdbee4dafae5aa2399fdf16f8d`, CI Windows PASS.

Archive : CRC, parité avec la copie source et auto-test extrait PASS.

## Lot 2 — 2.0 DEV_10_R2

Gemmes et soufre optionnels dans le bonus rocheux : activation, surface et
quantité moyenne propres ; sprites et libellés FR/EN/DE/ES communs aux minerais.
Égal, Prorata et Par minerai utilisent les cinq familles. Chaque cœur reste
borné à 820 cases ; le total maximum est 820 × actifs, jusqu’à 4 100.
Nouveautés OFF par défaut et dans les anciens profils ; digest, édition en
place et reset Bonus raccordés. Placeur/formes/transitions et règles des tours
conservés. Les bonus restent hors des quotas globaux.

191 ciblés PASS (8,25 s). Douze poses et quatre cartes complètes comparées à R1
avec nouveautés OFF : Area et départs exacts. Quatre cartes avec cinq minerais
et deux joueurs, dix zones posées chacune ; huit exports MAP/EDM, checksums
et relecture Area PASS. Suite complète : 879 tests PASS (545.70 s). Hashes protégés PASS.
R2 validée par Julien le 2026-10-04 : « ok c’est validé ça fonctionne ».
Détail des manipulations non fourni. Candidate locale, aucun push, DEV10 non clôturée.

Archive R2 : CRC, parité avec la copie source et auto-test extrait PASS.

## Travail restant — actualisé le 2026-10-06

R19 validée ; chapitre masques et étape 4 sprites de l’éditeur/catalogue clos.
Les dessins Vue/thermiques/icône à fournir et la future MAJ pixel art restent
indépendants ; la clôture des sprites ne concerne pas toute l’iconographie.
Molette désactivée validée. Resets validés, mais bruit sélectionné à conserver.

Reste à trier dans DEV10 : ajustement des resets, algorithmes de départ,
validité du terrain autour des tours, cas reproductibles d’îles pauvres en
montagnes, bilan du bruit par équations et finitions de publication.
Petites îles reste DEV10 ou DEV11 ; aucune répartition ferme. Nombre de zones
par minerai déprogrammé sans échéance, reprise uniquement sur demande.

Exports/construction EDM-MAP, bouton Copier et présentation des erreurs :
chantier dédié DEV11 ou DEV12 selon Julien. Analyse des éditeurs à envisager.
Tests 832–1024 globalement valides dans l’éditeur modifié Settlers United ;
réexport vers le jeu non fonctionnel, cause à établir. Aucune validation
éditeur/jeu globale ou viabilité étendue prétendue.
Détails : ../references/dev_notes/DEV10_VALIDATIONS_ET_REPORTS_20261006.md.

R20 : 982 cas exécutés (977 PASS initiaux ; cinq écarts de références/version/fixture
corrigés et requalifiés par les suites ciblées). Aucun changement du code de
génération après lancement de la suite. Maintenance 10 PASS, resets 17 PASS,
packaging 6 PASS ; quatre générations désert/bonus, hashes et auto-test extrait PASS.
