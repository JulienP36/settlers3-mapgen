# Export MAP/EDM — DEV10 R45

L’export prépare une copie de l’Area avec les routines United portées :
contexte côtes/marais 0 x 416370(0 x 10), hauteurs 0 x 417030, puis finalisation
0 x 416370(0 x 20). Le contexte traite seulement l’intérieur : les côtes ID 48
voisines d’un terrain ID 0 passent temporairement à ID 250 et hauteur zéro.
Les marais 80/81 perdent temporairement le bit 0 d’accès ; la finalisation
restaure les côtes et bloque les marais, bords compris. Les autres bits,
objets, claims et ressources sont conservés. Le test eau est ID 0 uniquement,
ni la famille entière 0..7 ni la hauteur zéro. Les six voisins HEX sont exacts.
La correction itérative des hauteurs conserve son parcours natif asymétrique.
La session affichée n’est pas modifiée. Cette préparation de compatibilité
est distincte de l’amplitude source R40 réglable dans Archétype.

La part 3 écrit (équipe, contrôle), contrôle 0=Choisir. Les équipes natives
commencent à zéro et ne présentent aucune lacune. Chaque « aucune équipe »
MapGen reçoit son propre groupe ; les mêmes étiquettes positives gardent une
alliance commune. Les groupes sont renumérotés par premier joueur rencontré,
ce qui place toujours le premier joueur exporté en équipe native 0.

La version du scaffold est conservée et promue à 11 pour une nation >2 et <255
(Amazones) ou une marchandise type >33 dans la part 9 confirmée : count uint 32,
records de huit octets, type à offset 4. Les parts opaques sont préservées.
Le fichier finit sur une frontière DWORD, après la part terminale 0/8, avec
les octets de padding natifs puis recalcul du checksum.

La miniature part 4 existante est reconstruite depuis la carte exportée :
256 × 256 pixels RGB 555 little-endian, couleurs schématiques communes au viewer
MapGen (pas une reproduction de la palette native). Le scaffold EDM ne contient
pas cette part ; son absence est conservée.

Le maximum proposé et exportable est désormais 768 × 768. Les fichiers de
plus grande taille sont refusés à l’import GUI et par le writer MAP/EDM.
Les exports EDM de test vides/partiels restent disponibles dans cette limite.

La corruption 1024 démontrée côté jeu est distincte de cette préparation.
Aucun changement d’entête ou de hauteur ne répare la superposition de la grille
et des données joueurs. Recherche >768 suspendue sur décision du propriétaire.

Preuves historiques : references/dev_notes/DEV10_R42_QUALIFICATION/.
Prochain lot : validités jeu/éditeur après essai des fichiers exacts R45.

## Conversion SAV → nouvelle carte — R65

La conversion utilise le terrain courant, les ressources restantes et les
positions de départ d’origine. Civilisations et alliances natives sont
conservées ; équipe native 0 est une alliance, traduite en étiquette UI positive
avant renumérotation. Les slots actifs sont compactés dans l’ordre du lecteur.
Contrôle joueur = Choisir ; ressources de départ = défaut Medium si non renseigné,
sans convertir les stocks de partie en dotation initiale.

Récifs runtime13–16 sur eau0–7 → objets carte111–114. Marqueurs chantier112/113
terrestres → aucun objet. Abattage128–207, variantes observées0–4/6 → souche208+v :
choix d’adaptation à une nouvelle carte sans bûcheron, pas reprise de l’animation.
Stades communs208–214/216–222/224–230 et cultures restent courants ; byte14 n’est
jamais utilisé pour ressusciter les arbres consommés. Objets runtime111/114,
variantes d’abattage5/7, chantier sur eau et IDs215/223/231 refusés avant écriture.

Claims →255 ; flags carte reconstruits depuis le seul bit0 confirmé du byte10,
avec nettoyage chantier/abattage et blocage eau/neige/sculpture. Les autres bits
runtime sont supprimés. Les filtres d’import ne lisent pas ces flags : ils restent
terrain seul ou terrain+objets, sans setup. La préparation United habituelle
s’applique ensuite à une copie et peut ajuster les hauteurs.

Aucun bâtiment, unité, pile, inventaire, temps ou état de partie n’est transféré.
Les parts7/8/9 du scaffold sont retirées pour cette conversion. Copie SAV brute
inchangée, exports ordinaires hors SAV conservés. MAP sans départ récupéré refusé ;
EDM vide permis. Aucune relocation pour satisfaire l’éditeur.

Voir `../references/dev_notes/DEV10_R65_QUALIFICATION/` pour tests et exports réels.
Lot R65 accepté par Julien, partie générée en cours fonctionnelle. Fichiers SAV exacts et parcours éditeur non précisés ; il ne s’agit pas d’un writer SAV.
