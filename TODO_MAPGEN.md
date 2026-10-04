# Settlers III MapGen — TODO
> Roadmap orientée **travail restant**. Reprise : `PROJECT_WORKFLOW.md`,
> `docs/DEV_9_CHECKPOINT.md`, puis snapshot/références du ZIP lorsqu’ils existent.

## Historique clôturé — v1.9 (non prescriptif)

Historique complet dans CHANGELOG et les journaux des références locales.
DEV8 publiée depuis R86 ; DEV9 clôturée le 2026-10-04 avec focus Grandes îles,
sur R25 validée et renommage de la source alternative. Détails dans le bilan DEV9.
Pas de nouvelle fonctionnalité de génération engagée avant le bilan DEV10.

## DEV9 clôturée — Grandes îles

- [x] Une île comparable et un départ par joueur, chenaux/marges et relief natif.
- [x] Formes, proportions et montagnes R25 validées ; neige reste 200.
- [x] Source insulaire raccordée aux fusions, masques, seuils et profils communs.
- [x] Algorithme général de rivières amélioré validé ; scaling taille/terre/masse.
- [x] Défauts rivières par profil et mini-marais visible unique validés R17.
- [x] Profils en place et Personnalisé conditionnel, correctifs UI individuels.
- [x] Variante renommée « Grandes îles — relief ondulé » ; sauvegardes compatibles.
- [x] Parité native terrain R9 qualifiée techniquement, moteurs séparés.

## DEV10 — panier repris, à prioriser après le push

Décision du 2026-10-04 : tout ancien report DEV9 hors du focus Grandes îles
passe à DEV10. Cette affectation n’engage pas à tout finir dans une seule DEV ;
répartir les finitions après l’état des lieux. Les tâches déjà prévues en 2.1
restent en 2.1. Aucun développement de ces reports n’est engagé ici.

- [ ] Trier les reports bonus/minerais, tooltips et masques détaillés plus bas.
- [ ] Planifier les algorithmes de départs sélectionnables pour l’équilibrage.
- [ ] Revoir la validité du terrain autour des tours selon l’algorithme du jeu.
- [ ] Confirmer les correctifs molette/resets sous Windows et les rappels
  éditeur/jeu encore non consignés, dont parité R9 et exports 832–1024.
- [ ] Suivre les rares îles pauvres en montagne si reproduites sur nouveaux seeds.
- [ ] Planifier les finitions de publication auparavant fléchées DEV11.

## Nouveaux archétypes — DEV10 ou DEV11

- [ ] Petites îles : fork de Grandes îles, jalon à fixer après bilan.
- [ ] Si le fork est vite fonctionnel, envisager un ou deux autres dérivés.
- Une DEV11 consacrée à plusieurs archétypes reste une possibilité, pas un plan figé.
- Archipel hors 2.0 ; ENDGAME reste pour la fin.

## Future release — après les finitions

- [ ] Geler les nouvelles fonctionnalités ; permettre corrections/polish/optimisation.
- [ ] Produire ZIP sources et Windows x64 portable `onedir`, sans installateur.
- [ ] Revalider ressources, exports, settings, installation propre, mise à jour,
  absence réseau, checksums et rollback.
- [ ] Finaliser l’icône à partir du pixel art manuel fourni, sans image IA.
- [ ] Finaliser updater v2, intégrité, settings et remplacement/rollback.
- [ ] Synchroniser README, notes, manifests et snapshot avant promotion.

## v2.1 — ouverture

- [ ] Fiabiliser la pose des minerais Amélioré, notamment montagne morcelée ;
  préserver quotas et supports légaux. Le repli Grandes îles n’est pas la
  correction générale. Demande du 2026-10-01.
- [ ] Lire obligatoirement le todo personnel de Julien au début de v2.1 DEV1,
  comme entrée de priorisation ; le demander s’il n’est pas disponible.

## v2.0 — reconstruction native Legacy, puis Custom
La **reconstruction complète des pipelines** est le périmètre v2.0. Le
générateur procédural Continental DEV_1 a été retiré ; le Legacy natif est
validé dans DEV_2 et l’Upgraded indépendant dans DEV_3/DEV_5.
### v2.0 — Upgraded indépendant

- [x] Dupliquer le pipeline terrain Legacy dans `generators/upgraded/` sans
  dépendance d’exécution vers `generators/legacy/`.
- [x] Réintégrer la génération calibrée des minerais de montagnes.
- [x] Réintégrer poissons, arbres, décorations et pierres de construction.
- [x] Dev 5 validé : calquer les objets statiques sur les familles Legacy, conserver les récifs Upgraded, restaurer les bonus arbres/pierres/mini-marais, placer 30 % des adultes en mini-forêts, réserver les pousses aux forêts et créer les clusters de pierres.
- [x] Désactiver toute génération de boue dans Upgraded.
- [x] Garder le positionnement des joueurs isolé pour une passe dédiée ; le pont actuel reste provisoire et ne crée ni ressources ni colons de départ.
- [x] Calibrer les blobs miniers avec compensation de la projection parallélogramme, sans changer la topologie HEX6, les quotas, les quantités ou la règle no-gap.
- [x] Documenter le terrain `34` comme **Patch d’herbe rocheuse**, l’ajouter au graphique Montagne avec une couleur dédiée et harmoniser sa couleur de carte.
- [x] Ajouter les tests de parité terrain et les validations spécifiques Upgraded du checkpoint DEV_3 ; la parité externe complète reste à rejouer dans l’éditeur/jeu lors de la prochaine validation dédiée.

- [x] Ancien pipeline Legacy DEV_1 retiré ; chemin Upgraded isolé avec ses
  règles, profils et validations. La comparaison minière DEV_1/natif est
  archivée et ses formes fragmentées ne sont pas reconduites.
- [x] Audits non-terrain complétés : ordre Area/bâtiments/colons/départs,
  cellules runtime, registre type 9, catalogue `0x51B010/0x51B1A0`, chemin
  `GameDataSave::Save`, offsets hexagonaux, filtre des départs et stock initial
  (`0x506CF0 -> 0x5046B0 -> 0x504420`).
- [ ] Poursuivre séparément les résidus de format : couverture complète des tokens
  d’empreinte, nomenclature des IDs/champs, source externe type 9 et writer EDM/MAP ;
  voir `references/S3_EXE_STATIC_NON_TERRAIN_AUDIT_20260901.md`.
- [x] Documenter l'ordre natif complet observable : noyau terrain, objets et ressources
  de sol, re-seed, départs, ville/stock et finalisation.
- [x] Implémenter le noyau Legacy natif séparé : seed, relief, familles de
  terrains, transitions, hydrologie et ordre d’écriture démontrés.
- [x] Définir l’archétype Continental v1 au-dessus de ce noyau sans lui
  appliquer une seconde macro-forme.
- [x] Reproduire le terrain, les ressources globales (minerais/poissons), les objets/décorations et les validations Legacy avec les mesures natives ; les objets/ressources de départ, colons et writer SAV restent hors périmètre.
- [x] Exposer les tailles natives 256–1024, les miroirs Axe long/Axe court/Les deux pour Legacy et Upgraded, les avertissements de viabilité et l'export MAP/EDM multi-tailles via scaffold de test.
- [x] Laisser toutes les tailles du contrat générables et exportables pour
  test, sans refus lié au statut « non testé » ; conserver les avertissements
  uniquement comme information.
- [x] **Dev 6 — générateur Custom** : socle déclaratif décrit dans
  `references/SETTLERS3_CUSTOM_GENERATOR_ARCHITECTURE_DEV6.md`. Les sections
  Custom et les cinq bonus sont raccordés aux deux moteurs ; les validations de
  génération restantes sont suivies par R61 et les tests spécialisés.
- [x] R17–R19 — transition Custom sans reconstruction au premier changement,
  rollback de l’essai R18 et clôture des points 1 à 6 de la mini-roadmap UI par
  validation utilisateur.
- [x] R34–R58 — moteur des cinq bonus, forçage par couronnes, hitboxes,
  formes minérales et lac/rivière documentés dans les notes de candidate.
- [x] R20–R26 — refonte ergonomique du panneau Bonus : règles communes, groupes
  lisibles, panneaux verticaux, microcopy/tooltips ; R21 conserve uniquement
  l’aperçu calculé des Pierres de construction et R22 isole la matrice rocheuse
  et resserre tous les cadres internes ; R23 ajoute une grille responsive des
  sections, R24 l’applique aussi aux panneaux internes du Bonus et rapproche
  « Réinitialiser » de « modifié » ; R25 corrige le reflow par largeur de
  fenêtre, équilibre les couples Terrains/Décorations et aligne les sections
  en haut de leurs lignes ; R26 retire l’aide redondante de Terrains, place le
  bloc dense à gauche, ajoute la troisième colonne du Bonus et avance le seuil
  de séparation, sans reconstruction lors des edits. Aucun changement de
  génération.
  Validation utilisateur reçue ; le checkpoint DEV7 est publié.
- [x] **DEV_6_R61** — bonus lac/rivière et fignolages visuels. Cette candidate
  est antérieure à DEV7 ; ses contrôles de panneau sont historiques et ne
  constituent plus une tâche active.
- [x] **Rivières Custom hors Legacy** — dernier retour utilisateur du
  2026-09-30 : les anomalies sont réglées par un champ de bruit plus doux près
  des bords d’eau. Le tracé Legacy natif reste inchangé ; ne rouvrir qu’en cas
  de nouvelle reproduction.
- [x] **R50 — qualification des masques manuels** : l’outil déterministe couvre
  les tailles `384/512/768`, trois seeds et les quatre miroirs ; il mesure
  reproductibilité, effet, couverture, variation hors masque et bordure d’eau.
  La validation visuelle Windows d’une silhouette dessinée/importée reste à
  faire avant de fermer ce gate.
- [x] **R51 — calibration Continental provisoire** : le profil dérivé
  `relief compact` est comparé au Continental natif sur la matrice ; le gate
  dur des départs passe sur `54/54` cas et le diagnostic `startable_mass`
  reste souple. Il reste un diagnostic et n’est pas installé comme preset.
- [x] **R52 — composition Continental Custom** : le preset nommé
  `fBm + domain warp + crêtes` remplit une source et deux fusions inspectables
  dans l’onglet Archétype ; le Continental natif et les moteurs Legacy/Upgraded
  restent inchangés. Le rapport de qualification rejoue aussi le gate dur des
  départs sur le chemin Custom basé sur Legacy.
- [x] **DEV8 — archétypes Custom, publiée sur `dev` (base R86)** : providers, fusions,
  masques, previews et relief dérivé Legacy ; profils Classique/Continental,
  état dynamique Personnalisé et synchronisation des sélecteurs. L’utilisateur
  confirme la validation UI Windows, les tests multi-tailles et la résolution
  des anomalies de rivières Custom. Les anciens reports hors focus Grandes îles passent en DEV10 ; la
  chronologie détaillée est dans `CHANGELOG.md`.
- [ ] DEV10 — reprendre tous les autres points ouverts du TODO selon leur
  priorité : validité résiduelle des starts, viabilité au-delà des tailles
  testées, polissage et vérifications de release.
- [ ] DEV10 — revalider progressivement terrains, transitions, joueurs,
  ressources, macro-forme, côtes et exports 832–1024 dans l’éditeur/jeu.
## Raffinements différés — DEV10
- [ ] Rendre configurable l’**extension maximale du forçage des bonus de
  départ**. Le réglage devra être exprimé en hexagones au-delà de `D`, avec
  `34` conservé comme valeur par défaut actuelle ; il ne devra pas modifier le
  comportement du forçage désactivé ni l’ordre de recherche par couronnes.
  Ne pas ouvrir ce chantier avant la bilan de priorisation DEV10.
- [ ] Ajouter éventuellement un **nombre de zones par minerai** indépendant
  du mode de surface, puis recalculer les surfaces en conséquence.
- [ ] Étendre ultérieurement le bonus rocheux aux familles **gemmes** et
  **soufre**, avec validation de leurs transitions et de leurs quotas.
- [ ] DEV10 : ajouter des tooltips courts aux contrôles minéraux et bonus.

### Reports supplémentaires — DEV10
- [ ] Refaire l’éditeur de masques : plusieurs types de pinceaux ; dessin en
  niveaux de gris au lieu d’un choix noir/blanc ; ajout et suppression
  persistants des masques utilisateur, avec protections pour les masques par
  défaut et un repère visuel distinct pour les masques modifiables.
- [ ] Revoir le placement des terrains/objets hors macro-forme selon le terrain réellement disponible, non selon Continental Legacy ; DEV ultérieure ou au plus tard v2.1.
- [ ] Repenser à terme le rendu des onglets avec des widgets persistants et des
  mises à jour en place (mode, langue, redimensionnement), afin de supprimer
  durablement les reconstructions et les artefacts visuels ; chantier
  compatible avec la consolidation, l’amélioration et le débogage poussés de
  la v2.1, sans lui assigner une version cible. L’essai R18 de staging n’est
  pas la solution de référence.
- [ ] Étudier un réglage indépendant du rayon et de l’espacement des forêts
  globales, seulement si les quotas actuels ne suffisent pas.
- [ ] Étudier des variantes de forme et de répartition des groupes de pierres
  de construction.
- [ ] Étudier une granularité supplémentaire pour le remplissage des poissons
  et les paramètres des lacs bonus, sans modifier les règles natives validées.
- [x] Accélérer exactement la preview macro autour de `_relax_relief` sans changer la génération native ; l’étape indicative de R13 reste séparée et explicitement signalée, sans version cible supplémentaire.

### Garde-fous

- [ ] Préserver la chaîne eau → plage/rive → terrain, la topologie HEX6 et les
  règles hydrologiques mesurées.
- [ ] Ne jamais mélanger les calibrations internes Legacy et Upgraded : chaque
  moteur garde profils, références et tests séparés ; les sélections publiques
  et futurs archétypes suivent néanmoins la route Custom commune par presets.
- [x] Maintenir l'ordre natif démontré : terrain/objets/ressources, re-seed,
  départs, ville/stock puis finalisation ; conserver le footprint natif et la
  protection sans halo.
- [x] Séparer décor initial byte 14, objet runtime byte 7 et byte 9 SAV encore
  inconnu.
- [ ] Toute comparaison visuelle doit venir d'un EDM/MAP/SAV réel ou d'une génération déterministe identifiée.

## Analyse et UI futures

- [ ] Auditer et réduire les clignotements visuels lors des changements
  d’options (notamment la langue), ainsi que les artefacts provoqués par les
  redimensionnements d’onglets ou de fenêtres ; privilégier les mises à jour
  en place et les rafraîchissements regroupés.
- [ ] Rafraîchir le rapport Statistiques après changement de langue ; améliorer inventaires, IDs absents, familles runtime et distributions.
- [ ] Étudier histogrammes, profils radiaux/cumulatifs et références corpus sans
  produire de visualisation trompeuse.
- [ ] Garder exactement deux rayons configurables pour les ressources proches.
- [ ] Revoir résolution des exports PNG et éventuellement transformer Hauteurs
  en carte topographique/classes d'altitude.
- [x] Première liaison Graphiques → Vue avec payloads sémantiques, cache de
  surbrillance et conservation du cadrage ; A/B reste volontairement
  informatif (tooltip uniquement).
- [x] Router tous les graphes **X proche(s)** vers la vue globale, ancrer leur
  flèche aux bordures des territoires de départ d’origine et conserver le
  contexte des départs via les marqueurs/cercle partagés.
- [x] Ajouter les tailles de marqueurs Petits / Normaux / Grands (plus
  Masqués), conserver la compatibilité des préférences historiques et propager
  le réglage à toutes les vues, Batch et Historique.
- [x] Supprimer la vue dédiée Départs et ajouter l’option indépendante
  **Cercles de départ**, propagée à toutes les vues et previews sans lien avec
  l’opacité couche.
- [x] Renommer le graphique des objets en **Familles d’objets** et figer son
  ordre de colonnes sur les nombres rouges de la référence utilisateur.
- [x] Corriger le flash initial de la fenêtre **Générer un lot** en la gardant
  masquée pendant la construction de ses contrôles et de sa géométrie.
- [x] Corriger le centre d’export multi-taille et conserver `references/` dans
  les ZIP sources tout en l’excluant des commits/push GitHub.
- [ ] Étendre le pilotage de la vue depuis les Graphiques : légendes, conflits,
  clic persistant et multi-cartes 3+.
- [ ] Repenser Comparaison, signalétique Chargée/Affichée/Affectée et A/B avancé
  seulement si l'usage le justifie ; multi-cartes 3+ après le générateur.
- [ ] Concevoir labels J1–J20, loupe locale, inspecteur près du curseur et
  indépendance des toggles.
- [ ] Reporter responsive UI v2, Status/Feedback v2, centres d'export et
  diagnostic mémoire à une passe dédiée avec mesures factuelles.
- [ ] Implémenter dans Upgraded la passe séparée du positionnement des starts et
  des données natives `.sav` ; Dev 5 utilise le pont de coordonnées existant
  sans le recalculer.

## Personnalisation, après Continental et ENDGAME

- [ ] Relire DE/ES, versionner les packs de langue et thèmes déclaratifs, puis
  étendre éventuellement les commandes rebindables.
- [ ] Créer l'iconographie UI et le pixel art manuellement ; maintenir la
  provenance des assets et ne rien importer sans validation.
- [ ] Après DEV9, étudier des forks de **Grandes îles**,
  puis **Small Islands**.
- [ ] Garder ENDGAME pour la fin : générer, importer, inspecter, modifier,
  valider et exporter seulement les données EDM/MAP/SAV comprises.
## Invariants

- Archétype = contexte macro-géographique et futur contrat des masses jouables ;
  Legacy/Upgraded = exécution du relief, hydrologie, contenu, règles, balance,
  ressources et objets. Les montagnes et lacs natifs sont dérivés de ces passes ;
  les bonus rocheux/lacustres sont des zones locales explicites, jamais des objets.
- Legacy : terrain/objets/ressources avant re-seed, puis starts/ville/stock ; Upgraded :
  terrain copié indépendant, contenu global spécifique, minerais v7 no-gap préservés et
  bonus de contenu autour des coordonnées de départ provisoires.
- Aucun aperçu ou asset imaginaire ; SAV lu sans réinvention et copié inchangé.
- IDs inconnus explicitement inconnus ; ne jamais repartir d'une version
  invalidée du générateur.
