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
- [x] **Découpler Upgraded du checkpoint 768 comme référence exécutable** : la GUI/CLI utilisent désormais une façade où la macro-géographie vient de la bibliothèque d'archétype, indépendamment du mode.
- [x] **Terrain34 requalifié par analyse native** : sur les 3 SAV natives 768 analysées, toutes les cellules 34 sont des singletons entièrement entourés de Rocky32 et ne touchent jamais `35/129/128`. Ne plus normaliser `34 -> Rocky32` et ne pas l'insérer dans l'anneau Snow. Terrain34 est une variante rare interne Rocky, minéralisable si elle est valide.
- [x] **Chaîne Snow corrigée/validée visuellement** : `Rocky32 -> 35 (1 cellule) -> 129 (1 cellule) -> Snow128`. Terrain34 n'appartient pas à cette chaîne.
- [~] **Bibliothèque de formes Continental** : l'infrastructure `ArchetypeMorphologyLibrary` exploite les 3 templates natifs 768 + transformations HEX compatibles ; première candidate Upgraded validée.
- [x] **Audit Legacy / Upgraded terminé conceptuellement**. Référence canonique : `references/SETTLERS3_LEGACY_UPGRADED_AUDIT_20260819.md`.
- [x] **Minerais — séparation verrouillée** : Legacy reste native-like. Upgraded cible ~90 % du Rocky accessible, ratios natifs empiriques à lisser plus tard, v7 no-gap, +30 % quantité/case cap15, minerai sous Snow et Terrain34 valide.
- [x] **Hydrologie — séparation verrouillée** : étangs 1–4 supprimés/redistribués = Upgraded seulement. River trimming/cap = Upgraded seulement et size-scaled. Cible pratique p99 : `~0.0245*side + 34.7`, avec queue rare autorisée au-dessus ; Legacy garde le comportement natif.
- [x] **Arbres** : Legacy pool natif complet `68..77 + 80..81`, proportions/volume natifs. Upgraded même pool + volume total ~130 % de la vraie baseline native + SmallTree84 bonus séparé. Palms `78..79` = arbres récoltables et comptés dans les quotas bois.
- [x] **Building Stones** : états `115..127`, stock `127-id`, footprint 7 cellules commun/bugfix. Legacy densité/stock natifs ; Upgraded stock amélioré, petits clusters + dispersé.
- [x] **Décorations** : récifs `Legacy=0`, Upgraded rares/non gênants. Roseaux comportement natif identique dans les deux, seuls objets Swamp. Pierres décoratives native Legacy / ~native÷10 Upgraded. Petites plantes/fleurs/champignons/buissons = natif identique dans les deux. Wrecks `29..33`, Grave objet `34`, Tree Stumps `41..42` = comportement natif identique dans les deux.
- [x] **Désert** : comportement natif commun : Dead Trees `43..44`, Cacti `45..48`, Skeleton `49`, Palms `78..79`.
- [x] **Biomes** : Mud natif Legacy / désactivé Upgraded. Swamp global natif Legacy / ~+30 % Upgraded. Terrain24 généré en Legacy selon observations ; ajout Upgraded confirmé mais volontairement différé à un changement isolé.
- [x] **Snow** : même génération Legacy/Upgraded. Toute variante « montagnes plus réalistes » devra être un changement explicite/modificateur, pas une divergence cachée.
- [x] **Starts** : placés très tôt dans les deux modes, zones protégées des passes suivantes ; comportement actuel conservé tant qu'aucune seed ne réintroduit invalidité/crash. Pas de cercles Grass/flattening artificiels. Bonus mini-marais/forêt/pierre = Upgraded uniquement.
- [ ] **Implémenter maintenant la séparation Legacy / Upgraded dans le code** selon la référence canonique, puis générer des maps de contrôle.
- [ ] **Après séparation : recalibrer explicitement les bonus de départ Upgraded** (arbres + Building Stones), séparément des quotas globaux.
- [ ] Ajouter Terrain24 à Upgraded dans une passe isolée/testable, pas pendant la grosse séparation actuelle.
- [ ] Tester visuellement le nouveau volume d'arbres Upgraded basé sur le pool complet ; si trop forestier, revenir au volume Legacy sans réduire le pool d'IDs.
- [ ] Valider les scalings multi-tailles (arbres, stones, décorations, Swamp, reefs, désert, rivières) sur 384/448/512/576/640/704/768.
- [ ] Après ces contrôles, reprendre le **compositeur de formes natives / native stamps** pour diversifier réellement les seeds sans warp global.
- [ ] Produire plusieurs candidates 768 distinctes et valider la variété sans perdre la qualité de la seed `2026081908`.
- [ ] Reprendre ensuite la validation progressive multi-tailles, une map à la fois.

## Modificateurs futurs — architecture orthogonale aux modes
- [ ] Ne pas créer un quatrième générateur Barebone : implémenter un système de **modificateurs** combinables avec les modes (`Legacy + modifiers`, `Upgraded + modifiers`).
- [ ] **Barebone** : retire tout ce qui est purement cosmétique et sans utilité gameplay, sans toucher aux objets/terrains qui bloquent, fournissent des ressources ou ont un effet fonctionnel.
- [ ] Prévoir un modificateur **densité de forêt** configurable.
- [ ] Idée expérimentale : modificateur **cultures présentes au démarrage** (blé/vigne/riz), à étudier avec le decay runtime.
- [ ] Variante future possible : **montagnes plus réalistes** comme modificateur explicite plutôt que divergence silencieuse entre Legacy et Upgraded.

## Reverse engineering terrain/runtime — découvertes enregistrées
- [x] `Terrain24` : **herbe jaune / sèche**, variante visuelle de Grass ; blend propre uniquement avec Grass16 ; visible/générée nativement. Legacy oui ; Upgraded ajout futur confirmé mais différé.
- [x] `Terrain22` : **sol cultivé / terrain agricole runtime**, fortement corrélé au blé et à la vigne ; revient vers Grass lorsque les cultures/terres abandonnées disparaissent.
- [x] `Terrain28` : **sol runtime travaillé/usé** sous zones aplanies de bâtiments et chemins de passage ; retour à Grass confirmé, vitesse possiblement différente pour chemins.
- [~] `Terrain18`, `19`, `23` : terrains techniques/intermédiaires encore non résolus ; ne pas les générer volontairement.
- [x] `Terrain34` : rare détail interne Rocky observé nativement ; 100 % voisins HEX6 Rocky32 dans les trois références 768 ; peut porter du minerai.
- [x] `85..93` : famille runtime blé ; `92` récoltable, `93` = chaume.
- [x] `94..102` : famille runtime vigne/raisin ; `102` appartient au cycle.
- [x] `103..110` : famille runtime riz.
- [~] `82/83` : IDs techniques/persistants invisibles dans l'éditeur ; analyse visuelle close pour l'instant.

## UX / outillage
- [x] Barre de progression de génération.
- [x] Bouton seed aléatoire.
- [x] Import `.edm` / `.map` / `.sav` en lecture.
- [x] Export EDM + MAP pour les tailles disposant d'un scaffold validé (768 actuellement).
- [~] Export SAV : writer non validé ; copie inchangée autorisée uniquement pour SAV importé.
- [x] Visualisations : global / heightmap / ressources / territoires.
- [x] Vue territoires depuis `claim`.
- [ ] Ajouter vue **Chemins / zones creusées** basée sur `Terrain28`.
- [ ] Ajouter vue **Cultures** : blé `85..93`, vigne `94..102`, riz `103..110`.
- [ ] Corriger la **palette exacte des couleurs joueurs**.
- [ ] Sur import `.sav`, afficher aussi le **contour de zone de départ d'origine**.
- [x] Zoom, molette, drag, projection parallélogramme, labels P1..P20 nets, sliders corrigés, thème sombre et combobox corrigées.
- [x] Toutes tailles natives visibles : 384/448/512/576/640/704/768.
- [x] Max joueurs : 8/11/15/19/20/20/20.
- [~] Génération multi-tailles : sélecteur prêt, calibration moteur encore à compléter.
- [x] Onglet Statistiques basique + scrollbars + Paramètres persistants.

### Statistiques
- [ ] Enrichir fortement : ressources, pourcentages, objets-ressources, décorations, terrains, territoires.
- [ ] Inclure IDs terrain non identifiés séparément.
- [ ] Suivre explicitement Terrain24 et terrains runtime 22/28.
- [ ] Ajouter graphiques utiles plus tard.
- [ ] Édition directe de la map — pas maintenant.

## À préserver
- [x] Archetype = macro-forme uniquement.
- [x] Mode = contenu/règles/balance/objets/ressources/etc.
- [x] Starts générés très tôt et protégés par les passes suivantes.
- [x] Legacy / Upgraded restent conceptuellement séparés selon la référence canonique.
- [ ] Custom reste à définir proprement sans casser cette séparation.
- [x] Aucun aperçu imaginaire : rendu déterministe depuis les vraies données.
