# Configurations de génération — DEV11 R7

L’onglet **Configurations** s’applique à l’ensemble du paramétrage. Enregistrer
l’actuelle demande un nom et propose **Inclure le seed**, décoché par défaut.
Charger une configuration applique ses réglages, reste dans cet onglet et ne
génère aucune carte. Sans seed enregistré, le seed courant reste inchangé.
La carte déjà affichée reste disponible jusqu’à la prochaine génération.

Sont conservés : mode du générateur, profil et sections sémantiques complets,
packages de départ, archétype (sources, compositions/fusions, réglages et grilles
manuelles/importées), taille, nombre de joueurs, vingt sélections de civilisations
et équipes, nombre demandé d’équipes aléatoires, algorithme de départ et miroir.
Les choix aléatoires restent des choix : ils ne figent pas un tirage antérieur.
Les préférences d’interface (langue, thème, zoom, filtres, panneaux) sont exclues.
Une formule doit être appliquée dans son éditeur avant d’enregistrer le preset.

Après chargement/enregistrement, un changement de réglage affiche **modifié**
pour la configuration active lorsque l’onglet est visible. Modifier les réglages
ne remplace jamais un preset. **Remplacer** ouvre le dialogue d’enregistrement
avec le nom et l’option seed existants ; **Renommer** et **Supprimer** agissent
sur la collection sauvegardée. Aucun preset intégré imposé ni héritage.

## Collection et portabilité

L’application gère automatiquement un unique `configurations.json` dans
`%APPDATA%/Settlers3MapGen` sous Windows, à côté de `settings.json` ; sans APPDATA,
le dossier est placé sous le répertoire personnel. Aucune écriture dans les
ressources du programme. Les écritures passent par un temporaire dans le même
dossier puis un remplacement atomique. Un échec ne modifie pas la collection
précédente. Une collection locale illisible bloque ses mutations et affiche le
problème ; son contenu n’est pas remplacé silencieusement.

**Exporter la collection** produit un seul JSON contenant toutes les
configurations et leurs masques déjà embarqués en niveaux de gris. Le catalogue
PNG externe n’est pas une dépendance du preset. **Importer la collection** valide
tout le fichier, puis fusionne : chaque entrée est conservée, les noms en conflit
reçoivent `(2)`, `(3)`, etc., sans distinction majuscules/minuscules et sans
écrasement. Réimporter un même fichier ajoute donc de nouvelles copies.

## Contrat technique v1

Racine : `format = "settlers3-mapgen-configurations"`, `version = 1`,
`configurations = [...]`. Chaque entrée contient `id`, `name`, `configuration`.
Une configuration contient :

| Champ | Contenu |
|---|---|
| `mode`, `archetype` | Clés internes indépendantes de la langue |
| `size`, `players` | Taille native autorisée, joueurs dans sa limite |
| `mirror`, `starts` | Axe de miroir 0–3 et clé de placement |
| `nations` | 20 valeurs : 0–3 ou 255 (choix aléatoire) |
| `teams` | 20 valeurs : 0 (indépendant), −1 (aléatoire), 1–20 |
| `random_team_count` | Nombre demandé 2–20 |
| `custom` | Objet `CustomGenerationConfig.to_dict()` complet, schéma 2 |
| `seed` | Entier facultatif ; absence = conserver le seed courant |

Noms uniques dans chaque collection, 1–100 caractères ; identifiants stables
pour renommer/remplacer, renouvelés pour les entrées importées. Import/export
limités à 64 Mio par collection, versions inconnues refusées explicitement.
Implémentation : `application/configurations/`, sans changement du moteur.
