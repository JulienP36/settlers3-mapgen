# Vignettes des sources — DEV10 R12

Le sélecteur Source du relief et les six sélecteurs de fusion affichent une
vignette à côté de chaque bruit/composition et du choix courant. Les libellés
restent traduits ; les images sont identiques dans toutes les langues et thèmes.

Les vingt PNG sont de vrais échantillons des providers de génération :
seed 20261005, référence 384, quatre joueurs pour les îles, réglages par défaut,
aucune fusion ni masque. Résolution fournie 64×64, affichage 24×24 en gris.
Les bruits simples sont échantillonnés directement ; les compositions complètes
utilisent leur champ de source réel. Ce sont des repères visuels fixes : changer
un réglage, la seed ou la taille ne change pas ces images. Les aperçus de travail
restent la référence pour le résultat personnalisé réellement calculé.

Aucun bruit n’est généré pour un menu : les images sont fournies dans
`data/source_thumbnails/`, chargées une fois et partagées par les sélecteurs.
Une image absente laisse le texte utilisable, sans régénération automatique.
Les menus suivent les thèmes présents/futurs et l’état désactivé.
Les flèches haut/bas changent le choix ; répéter le choix courant ne déclenche rien.

Pour reconstruire volontairement les échantillons après une évolution de source :
`python tools/generate_source_thumbnails.py` depuis les sources. Le manifest
consigne paramètres et hashes ; les PNG et le manifest doivent être livrés ensemble.
Le packager source et PyInstaller embarquent les fichiers du dossier data.
