# Settlers III MapGen — TODO programme

## État de validation
- [x] **v1.3.2 validée** sur 4 générations Continental 768×768 : Legacy 4P / 20P et Upgraded 4P / 20P.
- [x] Starts acceptés par l'éditeur sur ces 4 contrôles.
- [x] Aucun crash en View Map / vue in-game sur ces 4 contrôles.
- [x] Marais : correction visuelle confirmée.
- [x] Neige intérieure : non traversable comme prévu.
- [x] **v1.4 validée** : visualisation, thème sombre, combobox, sliders, projection parallélogramme, labels joueurs et territoire initial.
- [x] **Goods Default corrigé et validé** : `Legacy=Medium`, `Upgraded=High`.
- [x] **Première morphologie Upgraded indépendante validée** : seed `2026081908`, starts OK, aucun crash, relief natif conservé.

## Prochaine grosse étape génération
- [x] Macro-géographie découplée du mode via `ArchetypeMorphologyLibrary`.
- [x] Terrain34 requalifié : variante Rocky rare, singleton entouré de Rocky32, minéralisable ; jamais anneau Snow.
- [x] Chaîne Snow validée : `Rocky32 -> 35 (1 cellule) -> 129 (1 cellule) -> Snow128`.
- [x] **Audit Legacy / Upgraded terminé conceptuellement**. Référence : `references/SETTLERS3_LEGACY_UPGRADED_AUDIT_20260819.md`.
- [x] **Séparation Legacy / Upgraded implémentée** dans `s3mapgen/generator.py` + profils 768 ; tests de verrouillage dans `tests/test_legacy_upgraded_audit.py`.
- [x] **Smoke statique local de la séparation : PASS** sur Legacy 4P/20P et Upgraded 4P/20P, 0 HARD failure. La copie locale a été reconstruite depuis l'archive v1.4 complète + la façade/profils audités ; ce smoke ne remplace pas le test officiel éditeur/View Map.
- [~] **Validation externe restante** : tester les deux candidates 4P auditées dans l'éditeur puis View Map/in-game avant promotion.
- [x] Minerais : Legacy reste sur son comportement courant ; Upgraded cible ~90 % du support minier, ratios natifs empiriques, v7 no-gap, +30 % quantité/case cap15, minerai sous Snow + Terrain34 valide.
- [x] Hydrologie : Legacy conserve étangs/rivières natifs ; Upgraded supprime/redistribue 1–4 cellules et applique un p99 river size-scaled `~0.0245*side + 34.7`.
- [x] Arbres : pool `68..77 + 80..81` dans les deux. Legacy volume natif ; Upgraded ~130 % + SmallTree84 séparé. Palms `78..79` comptés dans le bois.
- [x] Building Stones : footprint 7 cellules commun ; Legacy stock/densité natifs, Upgraded stock amélioré + clusters/dispersé.
- [x] Décorations : reefs Legacy=0 / Upgraded rares ; Reeds natifs communs ; pierres déco native Legacy / ~÷10 Upgraded ; petites végétations, Wrecks, Grave, Stumps communs natifs.
- [x] Désert : Dead Trees `43..44`, Cacti `45..48`, Skeleton `49`, Palms `78..79`, comportement commun natif.
- [x] Biomes : Mud natif Legacy / désactivé Upgraded ; Swamp natif Legacy / ~+30 % global Upgraded ; mini-marais start Upgraded uniquement. L'expansion Swamp Upgraded refuse désormais tout nouveau contact HEX6 avec un terrain incompatible.
- [x] Terrain24 : conservé en Legacy ; retiré temporairement d'Upgraded pendant cette grosse passe. **Ajout Upgraded confirmé mais différé à une modification isolée.**
- [x] Snow : même génération Legacy/Upgraded. Terrain34 est neutralisé seulement pendant le calcul de profondeur Snow puis restauré uniquement s'il reste entièrement entouré de Rocky32.
- [x] Starts : placement précoce commun et protection conservée ; bonus mini-marais/forêt/pierre Upgraded seulement.
- [ ] **Prochaine action immédiate : test éditeur/View Map des candidates Legacy + Upgraded 4P auditées.**
- [ ] **Après ce contrôle : recalibrer les bonus de départ Upgraded** (arbres + Building Stones), séparément des quotas globaux.
- [ ] Tester visuellement le nouveau volume d'arbres Upgraded ; si trop forestier, revenir au volume Legacy sans réduire le pool d'IDs.
- [ ] Ajouter Terrain24 à Upgraded dans une passe isolée/testable.
- [ ] Valider les scalings multi-tailles : arbres, stones, décorations, Swamp, reefs, désert, rivières.
- [ ] Reprendre ensuite le compositeur de formes natives / native stamps et produire plusieurs seeds 768 distinctes.

## Modificateurs futurs — orthogonaux aux modes
- [ ] Système de modificateurs combinables avec Legacy/Upgraded, pas de quatrième générateur Barebone.
- [ ] **Barebone** : retire seulement le cosmétique sans fonction gameplay.
- [ ] **Densité de forêt** configurable.
- [ ] Idée : **cultures présentes au démarrage** (blé/vigne/riz), à étudier avec le decay runtime.
- [ ] Variante possible : **montagnes plus réalistes** comme modificateur explicite.

## Reverse engineering terrain/runtime
- [x] Terrain24 = herbe jaune/sèche, blend uniquement Grass16, native.
- [x] Terrain22 = terrain agricole runtime.
- [x] Terrain28 = sol runtime travaillé/usé, bâtiments + chemins.
- [~] Terrain18/19/23 encore non résolus.
- [x] Terrain34 = détail Rocky rare/minéralisable, entièrement entouré de 32 dans les références contrôlées.
- [x] `85..93` blé (`92` récoltable, `93` chaume).
- [x] `94..102` vigne/raisin.
- [x] `103..110` riz.
- [~] `82/83` techniques/invisibles, différés.

## UX / outillage
- [x] Barre progression, seed aléatoire, import EDM/MAP/SAV, export EDM+MAP 768.
- [~] Export SAV non validé ; copie inchangée d'un SAV importé seulement.
- [x] Vues global / heightmap / ressources / territoires.
- [ ] Vue **Chemins / zones creusées** Terrain28.
- [ ] Vue **Cultures** blé/vigne/riz.
- [ ] Palette exacte des couleurs joueurs.
- [ ] Contour de zone de départ d'origine sur import SAV.
- [x] Zoom/molette/drag/projection parallélogramme/labels/sliders/thème sombre.
- [x] Tailles natives visibles 384..768 et max joueurs adaptés.
- [~] Génération multi-tailles : UI prête, calibration moteur à compléter.

### Statistiques
- [ ] Enrichir fortement les statistiques ressources/objets/terrains/territoires.
- [ ] Garder les IDs terrain non résolus séparés.
- [ ] Suivre Terrain24 et terrains runtime 22/28.
- [ ] Graphiques utiles plus tard.
- [ ] Édition directe de map — pas maintenant.

## À préserver
- [x] Archetype = macro-forme uniquement.
- [x] Mode = contenu/règles/balance/objets/ressources.
- [x] Starts générés très tôt et protégés.
- [x] Legacy / Upgraded séparés selon l'audit canonique.
- [ ] Custom reste à définir proprement.
- [x] Aucun aperçu imaginaire ; seulement rendu déterministe depuis EDM/MAP/SAV.
