# Masques utilisateur et éditeur — DEV10 R15

Dans Archétype, ajouter un masque puis ouvrir **Éditeur / catalogue**.
Le bouton est disponible pour chaque masque modifiable ; un modèle géométrique
s’ouvre sous forme de copie raster, et ne devient Dessin libre qu’après Appliquer.

Les PNG carrés valides du dossier utilisateur sont également proposés dans
**Mes masques**, directement dans le sélecteur de type de chaque couche. Le menu
se réactualise à son ouverture et valide progressivement les fichiers. La sélection
copie immédiatement la grille dans le profil ; modifier la force ou la position
conserve cette grille. Les rectangles nécessitent le cadrage explicite du catalogue.

## Cible du masque

Chaque couche propose **Défaut (résultat)**, **Source principale** et **Fusion 1–6**.
Défaut agit après toutes les fusions, comme les anciens profils. Source principale
agit sur le bruit de départ avant les fusions. Fusion agit sur le bruit propre
à cette fusion avant son mélange avec le résultat précédent. Les opérations,
force et transformations géométriques restent disponibles sur toutes les cibles.
Dessin libre reste un masque capable de façonner le relief ; choisir Source
principale ne crée pas un nouveau fournisseur autonome de bruit.

Les miniatures de source et de fusion incluent les masques associés. La miniature
du masque montre sa forme, indépendamment de la cible. Plusieurs masques sur la
même cible s’appliquent dans l’ordre de la liste ; déplacer un masque change cet
ordre. Une fusion absente, désactivée ou de force nulle rend son masque sans
effet ; l’interface le signale. Réactiver cette fusion réactive ses masques.
Réduire le nombre de fusions conserve les couches masquées pour leur retour.

Déplacer une fusion déplace ses cibles ; dupliquer une fusion conserve les
masques sur l’original et ne les duplique pas. Supprimer une fusion laisse
**Fusion N supprimée**, inactive : sélectionner une nouvelle cible explicitement.
Un nouvel élément dans le même emplacement ne récupère pas ses anciens masques.
Les cibles et grilles font partie du profil sauvegardé, sans dépendre du PNG.
Les confirmations de l’éditeur restent thémées et centrées sur sa fenêtre.

## Icônes des outils

Les cinq dessins 24×24 de Julien identifient Pinceau, Gomme, Pipette et les
formes Rond/Carré. Ils apparaissent dans les menus et sur le choix courant,
avec leurs libellés traduits. Les pixels et la transparence d’origine sont conservés.
La sélection et le comportement des outils restent identiques ; les images
sont réutilisées entre éditeurs et suivent les menus thémés.
Rangement et suite des dessins : [guide des sprites](SPRITES.md).

## Masquage exact et inversion

L’opération **Masquer** utilise le gris comme permission : noir bloque la
cible, blanc conserve son effet, gris à 25% conserve 25% de l’effet.
La sélection initialise la force à 100% ; force 0% désactive le masquage,
force 50% atténue à moitié le blocage. Force maximale : 100% pour cette opération.
**Inverser** échange noir/blanc sans modifier le dessin ou le fichier PNG.
L’inversion est aussi utilisable avec les autres opérations existantes.

Pour une fusion, la permission multiplie la contribution au mélange : en noir,
la fusion laisse intact le résultat précédent, y compris en Mélanger/Minimum.
Pour Source principale et Résultat, elle atténue le champ de relief de sa cible.
Les permissions exactes se multiplient : deux permissions de 50% donnent 25%.
Les autres modulations gardent leur ordre ; elles ne réactivent pas une zone
bloquée par une permission sur la même cible. Des fusions suivantes peuvent
agir sur une source masquée ; cibler Résultat pour borner toute la composition.
Les contraintes du cadre océanique restent appliquées.

## Aperçus visibles et sélection

Les trois vues sont fixées en haut par défaut ; seules les options défilent.
Le sélecteur propose Libre, Haut, Droite et Automatique. La préférence est
conservée après fermeture et changement de langue. Droite empile les trois
vues et ajuste leur taille ; Auto privilégie Droite uniquement si l’espace
réel de l’onglet suffit, sinon Haut. Les séparateurs internes sont pris en compte.
Changer le placement ou la taille ne relance pas la génération.
Un clic sur une vue agrandit le dernier champ réellement calculé dans une
fenêtre thémée ; Détails/agrandir donne accès aux statistiques et à la légende.

Les menus de masques et le bouton de sélection montrent une vignette 24×24.
Elle identifie le dessin d’origine (avec inversion pour la sélection), tandis
que l’aperçu de la couche montre ses transformations et son cadre effectifs.
Les formes fournies sont calculées une fois ; PNG/grilles sont réutilisés en
cache. Un PNG modifié est revalidé ; les fichiers invalides restent exclus.
Les vignettes fixes des bruits/compositions sont ajoutées dans R12 ;
voir [les échantillons de référence](SOURCE_THUMBNAILS.md).

## Catalogue et dossier

Le dossier Windows est `%APPDATA%/Settlers3MapGen/masks`, à côté des préférences.
Sans APPDATA, le dossier Settlers3MapGen du répertoire personnel est utilisé.
**Ouvrir le dossier** permet d’y déposer directement des PNG, puis **Actualiser**
met à jour le catalogue. Aucun fichier de configuration supplémentaire requis.
Les modèles Fournis sont calculés, protégés et chargeables en copie ; seuls les
PNG du dossier utilisateur peuvent être supprimés. La suppression demande une
confirmation ; les copies déjà appliquées à un profil ne sont pas affectées.

PNG valide sur son contenu réel, image fixe, côté maximal 2048 et fichier ≤32 Mio.
Couleur convertie en gris, transparence compositée sur noir. PNG illisible, faux
PNG, animé ou excessif signalé individuellement ; les autres restent utilisables.
Une image uniforme est acceptée avec indication. Un rectangle est signalé dans
le catalogue et chargeable via un choix de cadrage : marges noires (préserver les
proportions), recadrage central, étirement explicite. L’import de l’éditeur accepte
également JPEG/BMP et applique les mêmes limites ; sauvegarde utilisateur en PNG.

Les PNG externes restent intacts. Les carrés sont échantillonnés à la première
résolution de travail ≥ leur côté, avec un plafond 512. L’image d’origine garde
sa résolution sur disque ; enregistrer le dessin produit la résolution choisie.
Les miniatures sont ajoutées progressivement, cache borné et invalidé après
changement de taille/date du fichier. Actualisation explicite, pas de surveillance.

## Dessin et profil

Résolutions 64, 128, 256 et 512 de côté, redimensionnables dans l’éditeur.
Pinceau rond ou carré, dur ou doux : gris 0–255, rayon en pixels et bord doux
0–100 %. Chaque valeur a un curseur et un champ numérique synchronisés. Le
dégradé est cliquable et la pastille indique le gris choisi ; la pipette met
aussi à jour le curseur. Clic droit = gomme,
pipette = valeur sous le curseur. Annuler/rétablir : boutons ou Ctrl+Z/Ctrl+Y ;
un trait continu compte pour une action. Historique limité aux 32 dernières actions.
Effacer, inverser les gris, miroirs horizontal/vertical et rotation de 90° disponibles.

**Effacer tout** vide le dessin en conservant son nom et son historique :
Annuler récupère le dessin. **Nouveau masque**, dans le catalogue, crée un document
vide à la résolution actuelle, sans nom ni historique antérieur. Remplacer un
dessin modifié demande confirmation. Charger une autre copie démarre également
un document distinct ; Annuler reste réservé aux modifications du dessin courant.

L’éditeur conserve sa dimension initiale, mais sa fenêtre est redimensionnable.
Le dessin reste carré et centré ; l’agrandissement de l’affichage ne modifie pas
sa résolution de travail. Le contour du pinceau suit sa forme et son rayon réels.
Nom, état d’enregistrement PNG et modifications non appliquées au profil sont
visibles séparément et restent cohérents après Annuler/Rétablir.

Les trois boutons du bas sont sur une ligne. Nom, écrasement et confirmations
utilisent les fenêtres thémées communes, compatibles avec les rôles des futurs
thèmes. Les fenêtres ouvertes suivent les changements de palette. Les sélecteurs
de fichiers natifs sont affichés par le système d’exploitation.

**Appliquer au profil** copie la grille et sa résolution dans le profil courant.
Aucun chemin de fichier n’est nécessaire pour retrouver le relief. **Enregistrer
dans mes masques** demande un nom et écrit le PNG dans le dossier ; remplacer un
nom existant demande confirmation. **Exporter** écrit un PNG à l’endroit choisi.
Sauvegarder un PNG n’applique pas le masque au profil ; appliquer ne sauvegarde
pas de fichier. Fermer avec des changements non appliqués demande confirmation.

Le masque continue d’utiliser les opérations, force, position, dimensions et
rotation de sa couche existante. Les gris décrivent une influence intermédiaire,
ils ne fixent pas directement les IDs de terrain. Aucun ciblage individuel de
source/fusion ou source de relief dessinée autonome n’est ajouté dans R7 :
cette idée est conservée pour le cadrage de l’étape 3.

## Parcours de validation Windows

1. Tester thèmes clair/sombre et langues FR/EN/DE/ES ; ouvrir l’éditeur depuis
   chaque type et vérifier que fermer sans appliquer laisse le profil intact.
2. Déposer un carré PNG, un rectangle, un fichier corrompu et une image uniforme.
   Actualiser : les valides apparaissent ; les refus ont un motif sans blocage.
3. Charger, peindre à différents gris, tester bord doux, gomme et pipette, traits
   rapides et undo/redo ; tester inversion/rotation/miroirs et les quatre tailles.
4. Enregistrer, relancer l’application, retrouver le PNG ; supprimer une copie,
   vérifier que les modèles fournis sont protégés et qu’un profil garde sa grille.
5. Importer un rectangle avec chaque cadrage puis une image transparente ; vérifier
   la différence des cadrages et le noir sous la transparence.
6. Appliquer un dessin 256/512 : vérifier preview, profil/historique et génération.

R7 et le fonctionnement R8 confirmés par Julien. Les améliorations R9
validées par Julien le 2026-10-05 ; le centrage de la confirmation de sortie
reste à corriger dans la prochaine révision. Les tests automatisés utilisent de
vrais fichiers PNG et données de masque, aucun contrôle visuel Windows revendiqué.

## Suite différée

Étape 3 : ciblage de source/fusion et relief dessiné autonome, non implémentés.
Étape 4 éventuelle : petites icônes dessinées et fournies par Julien.

Réorganisation des sprites : au prochain ajout d’icônes fourni par Julien.

## Remplissage et transformations

Choisir Remplissage puis cliquer : toute la zone contiguë du même gris reçoit
le gris sélectionné. Les diagonales seules ne relient pas les zones. Le rayon
et le bord doux concernent le pinceau ; le clic droit reste la gomme.
Un clic s’annule/rétablit en une action ; le même gris ne crée pas d’action.
Les boutons 90° à gauche et à droite tournent sans interpolation.

Miroirs selon leur axe : horizontal inverse haut/bas, vertical gauche/droite.
Les actions de l’éditeur, catalogue et confirmations affichent icône + texte.

## Agencement R16

Annuler/rétablir espacés, importer/exporter côte à côte et catalogue dessous.
Le catalogue adapte ses fiches selon leur largeur requise et la place disponible,
sans relecture des fichiers lors du redimensionnement. Charger une copie et
supprimer le fichier sont côte à côte depuis R19.
Éditeur/catalogue peuvent être agrandis au maximum via leur barre de titre.
Le dialogue de confirmation reste centré sur l’éditeur et suit les thèmes.

## Ajustements R18

Annuler/rétablir, rotations et commandes de fichiers partagent les mêmes marges
(2 px horizontal, 1 px vertical). Les images restent à leur taille originale 24 × 24.
Les modèles affichent « Variable », les fichiers utilisateur leur taille réelle.
Les actions se placent sous les libellés, à côté de la vignette, avec 4 px entre boutons depuis R19.
La grille est calculée sur les demandes Tk des fiches, sans largeur fixe ni plafond
arbitraire. Les fiches et vignettes sont réutilisées lors du redimensionnement.

## Ajustements R19

Le nom et la taille s’affichent sur une ligne avec « · ». Les modèles indiquent
Variable, les fichiers leur taille réelle. Les noms longs sont tronqués selon
la police, avec le nom complet en infobulle ; le nom réel du fichier reste intact.
Le bouton Charger une copie et la poubelle (sprite seul 24 × 24) sont sur la même
rangée ; 4 px d’écart. La poubelle a une infobulle traduite et la confirmation reste
obligatoire. Les infobulles suivent la palette et disparaissent avec leur widget.
Les fichiers invalides gardent un diagnostic visible sous le nom.
