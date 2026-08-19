# Settlers III MapGen — TODO programme

## État de validation
- [x] **v1.3.2 validée** sur 4 générations Continental 768×768 : Legacy 4P / 20P et Upgraded 4P / 20P.
- [x] Starts acceptés par l'éditeur sur ces 4 contrôles.
- [x] Aucun crash en View Map / vue in-game sur ces 4 contrôles.
- [x] Marais : correction visuelle confirmée.
- [x] Neige intérieure : non traversable comme prévu.
- [x] **v1.4 validée** : visualisation, thème sombre, combobox fermées/ouvertes, sliders, projection parallélogramme, labels joueurs et contour de territoire initial contrôlés visuellement.
- [x] **Goods Default corrigé et validé** : le writer encode explicitement un preset valide dans Map Info (`Legacy=Medium`, `Upgraded=High`) ; les deux contrôles 4P frais démarrent sans crash avec `Défaut`.
- [x] **Première morphologie Upgraded indépendante validée** : `S3_Continental_Upgraded_4P_768x768_seed_2026081908_archetype_library_v1` jugée excellente, starts OK, aucun crash, relief conservé dans l'enveloppe native 768.

## Prochaine grosse étape génération
- [x] **Découpler Upgraded du checkpoint 768 comme référence exécutable** : la GUI/CLI utilisent désormais une façade où la macro-géographie vient de la bibliothèque d'archétype, indépendamment du mode. Test dédié avec chemin de checkpoint inexistant : OK.
- [~] **Bibliothèque de formes Continental** : l'infrastructure `ArchetypeMorphologyLibrary` est en place et exploite actuellement les 3 templates natifs 768 existants + transformations ; la première candidate Upgraded issue de cette architecture est validée. Élargir ensuite la variété/procédure de formes et préparer les autres archétypes.
- [x] Valider visuellement la première candidate Upgraded issue de la bibliothèque Continental commune avant d'augmenter davantage la variété.
- [ ] Nettoyer le résidu terrain `34` lors du rebuild Snow (`34 -> Rocky32` avant reconstruction) ; ce résidu est visuellement bénin mais ne doit pas survivre comme singleton parasite.
- [ ] Reprendre ensuite la validation progressive multi-tailles, une map à la fois.

## Reverse engineering terrain/runtime — découvertes enregistrées
- [x] `Terrain24` : **herbe jaune / sèche**, variante visuelle de Grass ; blend propre **uniquement avec Grass16** ; visible dans les générations natives/Legacy, mais ne pas l'ajouter volontairement à Upgraded pour l'instant.
- [x] `Terrain22` : **sol cultivé / terrain agricole runtime**, fortement corrélé au blé et à la vigne ; revient vers Grass lorsque les cultures/terres abandonnées disparaissent.
- [x] `Terrain28` : **sol runtime travaillé/usé**. Confirmé sous zones aplanies/creusées de bâtiments et sur petits chemins de passage. Retour rapide à Grass après disparition d'une zone bâtiment ; persistance des chemins possiblement différente, à tester seulement si utile plus tard.
- [~] `Terrain18`, `19`, `23`, `34` : terrains techniques/intermédiaires encore non résolus ; ne pas les générer volontairement.
- [x] `85..93` : famille runtime blé ; `92` récoltable, `93` = **chaume**.
- [x] `94..102` : famille runtime vigne/raisin ; `102` appartient bien au cycle, mécanique exacte du retour vers `94` encore ouverte.
- [x] `103..110` : famille runtime riz ; observée sur terrain marais/runtime compatible.
- [~] `82/83` : IDs techniques/persistants invisibles dans l'éditeur, y compris sur Terrain28 ; analyse visuelle close pour l'instant.

## UX / outillage
- [x] Barre de progression de génération (progression par étapes du pipeline).
- [x] Bouton seed aléatoire.
- [x] Import `.edm` / `.map` / `.sav` en lecture.
- [x] Export EDM + MAP pour les tailles disposant d'un scaffold validé (768 actuellement).
- [~] Export SAV : **writer SAV non validé** ; copie inchangée autorisée uniquement pour un SAV importé.
- [x] Visualisations : global / heightmap / ressources / territoires.
- [x] Vue territoires depuis `claim`, particulièrement utile sur SAV.
- [ ] Ajouter une vue **Chemins / zones creusées** basée sur `Terrain28`, utilisable sur tout format mais surtout utile sur SAV.
- [ ] Ajouter une vue **Cultures** pour SAV : distinguer visuellement au minimum blé (`85..93`), vigne (`94..102`) et riz (`103..110`) avec des couleurs différentes ; exploiter les états runtime plutôt que les seuls objets statiques.
- [ ] Corriger la **palette des couleurs joueurs** pour correspondre exactement aux couleurs du jeu, si les valeurs exactes peuvent être récupérées/calibrées.
- [ ] Lors d'un import `.sav`, afficher aussi le **contour de la zone de départ d'origine** des joueurs comme pour EDM/MAP ; ne pas confondre avec la vue Territoires dynamique.
- [x] Zoom sur la visualisation (slider + molette).
- [x] Toutes les tailles natives visibles : 384/448/512/576/640/704/768.
- [x] Nombre max joueurs adapté : 8/11/15/19/20/20/20.
- [~] Génération multi-tailles : sélecteur prêt, mais seule 768 est calibrée dans le moteur actuel.
- [x] Onglet Statistiques basique.
- [x] Scrollbars dans Validations / Pipeline / Métadonnées / Statistiques.
- [x] Onglet **Paramètres** avec préférences persistantes dans le profil utilisateur.
- [x] Thème sombre / clair, sombre par défaut.
- [x] Listes déroulantes lisibles en mode sombre, ouvertes comme fermées.

### Visualisation / confort
- [x] Slider de transparence pour les vues **Heightmap**, **Ressources** et **Territoires** ; 0 % montre la map globale, 100 % la couche seule.
- [x] À la fin d'un processus, la barre passe en état terminé bleu puis disparaît automatiquement ; état erreur rouge.
- [x] Barre de progression étendue aux générations, imports, exports et sauvegardes d'aperçu.
- [x] Déplacement de la visualisation par drag.
- [x] Zoom molette temporisé/caché pour réduire la latence et sensibilité réglable.
- [x] Projection **parallélogramme** optionnelle pour la visualisation, sans modifier les données réelles de la map.
- [x] Projection parallélogramme recalée sur un décalage de **0,5 cellule par ligne**.
- [x] Marqueurs `P1` à `P20` en bitmap net et couleur joueur.
- [x] Les textes `P1` à `P20` restent droits / non déformés en projection parallélogramme.
- [x] Contour du territoire initial des starts : vrai cercle dans la géométrie parallélogramme, déformation inverse en vue carrée, couleur joueur, dimension dérivée des SAV natifs (**3500 cellules, ±35 cellules**).
- [x] Clic sur la barre des sliders = déplacement immédiat du curseur à la position cliquée.

### Statistiques
- [ ] Enrichir fortement les statistiques, potentiellement sur plusieurs pages : quantités de ressources, pourcentages, comptes exacts des objets-ressources, objets décoratifs, terrains, territoires, etc.
- [ ] Inclure les IDs terrain encore non identifiés (`18`, `19`, `23`, `34`, etc.) dans les statistiques exactes au lieu de les fusionner prématurément dans une famille nommée.
- [ ] Suivre explicitement `Terrain24` dans les stats comme herbe jaune/sèche et `Terrain22/28` comme terrains runtime lorsqu'ils sont présents dans un SAV.
- [ ] Ajouter plus tard des graphiques pour les statistiques qui gagnent à être visualisées.
- [ ] Édition directe de la map — gros morceau, **pas maintenant**.

## À préserver
- [x] Archetype = macro-forme uniquement.
- [x] Mode = contenu/règles/balance/objets/ressources/etc.
- [ ] Starts générés très tôt et protégés par les passes suivantes.
- [ ] Legacy / Upgraded / Custom restent séparés.
- [ ] Aucun aperçu imaginaire : rendu déterministe depuis les vraies données.
