# Settlers III MapGen — Snapshot complet des développements récents

Date de snapshot : **2026-08-18**
Projet : **Générateur procédural Settlers III**
Archetype principal : **Continental**
État : **validation longue 768×768 / 10P en cours**

> Ce fichier est un snapshot de reprise. Il doit être lu avant toute nouvelle génération afin d'éviter de réintroduire un bug ou d'oublier une règle validée.

---

# 1. BASELINE HISTORIQUE IMMÉDIATE

## 1.1 Checkpoint 384×384 / 4P start-first
Le checkpoint 384 reste la base historique validée de l'architecture start-first :
- 4 starts valides ;
- aucun crash c0000005 ;
- outer sea réduit ;
- géographie first, starts fair-play ;
- bonus forêt + Building Stone ;
- mini-marais bonus ;
- marais globaux petits/nombreux ;
- aucun cercle artificiel de Grass autour des starts.

Ne pas casser ces principes.

## 1.2 768×768 / 10P — validation courte avant longue partie
Version validée visuellement et techniquement avant découverte de bugs de gameplay :
`S3_Continental_10P_768x768_seed_2026081801_checkpoint_rules_v2_final.edm`

Validation utilisateur :
- **10/10 starts valides** ;
- **aucun crash** ;
- côte/marge jugées bonnes après correction ;
- mini-marais visibles ;
- bonus start renforcés ;
- hydrologie visuellement validée ;
- décor désert/marais ajusté.

Cette version a ensuite révélé deux bugs de gameplay majeurs lors de la vraie partie :
1. eau marchable ;
2. absence totale de poissons.

---

# 2. CORRECTION CRITIQUE — EAU NON MARCHABLE

## 2.1 Symptôme
Pendant la première vraie partie, les settlers/soldats pouvaient marcher sur Water0..7.

## 2.2 Diagnostic binaire
Le champ Area est :
`[height, terrain, object_id, claim, accessibility, resource]`.

La map générée avait :
- Water0..7 : `accessibility = 0`.

Dans le SAV runtime de début :
- ces cases devenaient `runtime byte16 = 1`, donc praticables.

Comparaison native :
- Water runtime byte16 = **0** sur toutes les cases d'eau natives observées.

## 2.3 Règle permanente verrouillée
**Water0..7 → accessibility = 1**

Règles associées :
- Shore reste praticable sauf objet bloquant ;
- Rivers restent praticables sauf objet bloquant ;
- Reefs restent bloquants selon leurs règles ;
- objets conservent leurs propres footprints/accessibility.

## 2.4 Validation réelle après correctif
Fichier joué :
`1-S3_Continental_10P_768x768_seed_2026081801_checkpoint_rules_v3_water_access_fix.map`

Nouvelle sauvegarde début :
`slot 1(2).sav`

Validation runtime :
- Water cells : **123,555**
- Water runtime byte16 = 0 : **123,555**
- Water runtime byte16 != 0 : **0**
- Retour utilisateur : **les soldats ne vont plus sur l'eau**.

Le bug eau est considéré **corrigé et confirmé en vraie partie**.

---

# 3. BUG CRITIQUE DÉCOUVERT ENSUITE — AUCUN POISSON

## 3.1 Symptôme
En continuant la partie corrigée pour l'eau, l'utilisateur constate :
**AUCUN poisson sur toute la map.**

## 3.2 Diagnostic
Le problème existait déjà dans l'EDM :
- EDM v3 : **0 fish cells**
- MAP v3 : **0 fish cells**
- SAV début v3 : **0 fish cells**

Donc ce n'était PAS une suppression runtime.
C'était une régression de génération : la couche poisson avait été perdue lors des passes récentes hydrologie/côte.

## 3.3 Couche poisson restaurée pour les prochaines générations
Référence 768 validée historique :
- **32,313 fish cells**
- quantité totale historique : **257,780**
- poissons uniquement sur Water0..7 ;
- aucun poisson sur Rivers ;
- aucun poisson > HEX12 de Shore ;
- distribution côtière validée.

Version restaurée :
`S3_Continental_10P_768x768_seed_2026081801_checkpoint_rules_v4_water_fish_fix.edm`

MAP correspondante :
`1-S3_Continental_10P_768x768_seed_2026081801_checkpoint_rules_v4_water_fish_fix.map`

Important :
**la partie longue actuelle n'a PAS été recommencée après ce correctif**.
L'utilisateur continue volontairement la partie v3 sans poissons pour évaluer le reste du gameplay.

Conclusion :
- partie longue actuelle = valide pour géographie, construction, starts, expansion, minerais, bois, pierre, rivières, etc.
- partie longue actuelle = **NON exploitable pour juger la pêche/poissons**.

---

# 4. NOUVELLE RÈGLE POISSON — +30 % DE QUANTITÉ PAR CASE

Pour les prochaines générations :
- **ne pas augmenter le nombre de cases poissonneuses** ;
- conserver la même empreinte spatiale/densité de cases ;
- augmenter la **quantité de poisson par case de +30 % environ** ;
- agir uniquement sur le low nibble `1..15`;
- formule cible : `round(q * 1.30)`, plafonné à `15`.

Donc :
- surface poisson inchangée ;
- stock total de poisson augmenté ;
- pas de propagation en eau profonde ;
- toujours 0 poisson sur Rivers.

---

# 5. NOUVELLE RÈGLE MINERAIS — +30 % DE QUANTITÉ PAR CASE

Retour de partie longue :
les montagnes semblent sous-dotées en stock.

Pour les prochaines générations :
- **ne pas augmenter le nombre de cases minéralisées** ;
- conserver l'occupation spatiale actuelle ;
- augmenter de **~30 % la quantité portée par chaque case minéralisée** ;
- agir uniquement sur le low nibble de quantité ;
- conserver la famille de minerai dans le high nibble ;
- cap à 15.

Conserver les proportions relatives :
Coal dominant > Iron > Gold > Gems > Sulfur selon la distribution verrouillée actuelle.

Important :
on augmente le **stock par case**, pas la surface minéralisée.

---

# 6. RIVIÈRES — PROBLÈMES DE GAMEPLAY DÉCOUVERTS EN PARTIE LONGUE

## 6.1 Rivières orphelines
Observation utilisateur :
certaines rivières apparaissent au milieu de la map sans connexion à aucune masse d'eau.

Hypothèse probable :
- elles pouvaient être liées à d'anciens micro-étangs 1–4 cellules ;
- la suppression des micro-étangs a laissé les rivières derrière.

### Règle permanente
Après TOUTES les passes finales de correction hydrologique :
- analyser chaque composant River96..99 en HEX6 ;
- chaque système doit être relié à une vraie masse Water0..7 valide ;
- supprimer les systèmes orphelins ;
- ne jamais laisser un tronçon intérieur sans source/connexion eau.

Cette validation doit être faite **après** suppression/redistribution des micro-étangs.

---

# 7. RIVIÈRES — LONGUEUR MAX CALIBRÉE SUR LES 21 SAV NATIFS

Une analyse native dédiée existe sur :
- 21 SAV natifs ;
- 3,964 composants River >=5 cellules ;
- 2,878 chemins simples non branchés.

Statistiques chemins simples :
- médiane = **22**
- moyenne = **24**
- p90 = **34**
- p99 = **50**
- maximum absolu corpus = **70**

## 7.1 Plafonds pratiques verrouillés par taille de map
Utiliser environ le p99 natif comme plafond pratique :

| Taille map | plafond pratique |
|---:|---:|
| 384 | **44 cases** |
| 448 | **47 cases** |
| 512 | **48 cases** |
| 576 | **49 cases** |
| 640 | **47 cases** |
| 704 | **53 cases** |
| 768 | **55 cases** |

## 7.2 Maxima absolus natifs observés
À considérer seulement comme outliers exceptionnels, JAMAIS comme cible normale :

| Taille map | max absolu natif |
|---:|---:|
| 384 | 46 |
| 448 | 62 |
| 512 | 51 |
| 576 | 52 |
| 640 | 52 |
| 704 | 64 |
| 768 | 70 |

### Règle
Ne jamais utiliser un plafond universel.
La longueur maximale doit dépendre de la taille de map afin d'éviter des rivières géantes sur petite map.

## 7.3 Formes des rivières
Retour utilisateur :
**les formes sont bonnes**.

Donc ne pas modifier arbitrairement la morphologie/meandering actuelle.

Règles natives conservées :
- HEX6 confirmé : `(+1,0), (-1,0), (0,+1), (0,-1), (+1,+1), (-1,-1)` ;
- chemin map 1 cellule de large ;
- River1..4 utilisés pour variation visuelle de largeur ;
- maximum segment droit natif observé = 4 ;
- pratique naturelle ≈3 ;
- aucune cassure 120°/180° sur chemins simples natifs ;
- virages par directions HEX adjacentes ~60°.

---

# 8. MICRO-ÉTANGS / LACS — RÈGLE TOUJOURS VERROUILLÉE

Pour Continental custom :
- **0 composant Water intérieur de taille 1–4** ;
- les cellules supprimées doivent être redistribuées uniquement en agrandissant des lacs EXISTANTS >4 ;
- ne jamais créer un nouveau lac uniquement pour compenser ;
- après cette correction, refaire la validation des rivières ;
- après toute reconstruction finale de l'eau/côte/lacs, reconstruire et valider explicitement la couche poissons.

---

# 9. CÔTE / MARGE OCÉANIQUE

Retour précédent corrigé et validé :
le continent ne doit pas sembler découpé par une bande droite près du bord.

Règles :
- marge océanique suffisante ;
- ne jamais générer une terre puis la tronquer brutalement par une bande rectiligne ;
- construire/repousser naturellement la silhouette à l'intérieur de la marge ;
- conserver une côte chaotique/irrégulière ;
- bord externe deep Water7 ;
- bathymétrie Shore → Water0 → Water1 → ... → Water7 ;
- Water0..7 height = 0 ;
- global HEX neighbor height delta <=5.

---

# 10. STARTS — ÉTAT VALIDÉ 10P

Sur 768×768 / 10P :
- **10/10 starts valides**
- pas de crash
- forte dispersion
- start-first robuste à grande échelle.

Règles :
- pas de disque/cercle artificiel de Grass ;
- footprint start natif exact 33 cells ;
- terrain local naturel ;
- seulement sécurité technique locale ;
- pas d'objet statique bloquant dans la zone technique ;
- bonus de start hors quota global.

---

# 11. BONUS DE START — RÈGLES RÉCENTES

Chaque joueur doit avoir :
1. petite forêt bonus ;
2. cluster Building Stone bonus ;
3. mini-marais bonus contrôlé.

## 11.1 Bonus forêt + Building Stone
Toujours **hors quota global de la map**.

Nouveau volume :
**+50 % par rapport à la règle initiale 384**.

Le style doit rester naturel :
- clusters lâches ;
- même espacement que les clusters ordinaires ;
- pas de blobs compacts optimisés.

## 11.2 Mini-marais bonus
Doit être :
- garanti pour chaque start ;
- clairement visible ;
- proche mais hors zone technique dangereuse ;
- séparé de la logique des marais globaux.

Marais globaux :
- interdits dans la zone technique locale du start ;
- nombreux ;
- petits ;
- irréguliers.

---

# 12. DÉCORATIONS RÉCENTES

## Désert
Quota décoratif :
**×2** par rapport au quota antérieur.

Familles :
- Dead Trees ;
- Cacti ;
- Skeletons ;
- Palms selon règles existantes.

## Marais
Quota décoratif :
**×2** par rapport au quota antérieur.

Swamp → Reeds uniquement.

Ne pas confondre décoration et ressources utiles.

---

# 13. WATER ACCESSIBILITY — CHECKLIST OBLIGATOIRE FUTURE

Avant toute exportation/test d'une future map :
- [ ] Water0..7 accessibility = 1
- [ ] Shore pas bloqué artificiellement
- [ ] Rivers pas bloquées artificiellement
- [ ] Reefs seulement selon règles connues
- [ ] test SAV immédiat possible : toutes les Water doivent avoir runtime walkability bloquée

Ce check est désormais un invariant de sérialisation/gameplay.

---

# 14. POISSONS — CHECKLIST OBLIGATOIRE FUTURE

Avant toute exportation/test :
- [ ] fish cells > 0
- [ ] quantité/empreinte cohérente à la taille
- [ ] 0 poisson sur River96..99
- [ ] aucun poisson > HEX12 de Shore
- [ ] couche poisson reconstruite après la DERNIÈRE modification hydrologique
- [ ] +30 % de quantité par fish cell, cap 15
- [ ] ne pas augmenter artificiellement le nombre de fish cells

Pour 768, référence spatiale actuelle :
**32,313 fish cells** avant future augmentation de quantité par case.

---

# 15. MINERAIS — CHECKLIST OBLIGATOIRE FUTURE

- [ ] même surface minéralisée que la distribution verrouillée
- [ ] pas de trous dans les blobs v7
- [ ] +30 % de quantité par case minéralisée
- [ ] conserver famille high nibble
- [ ] cap low nibble 15
- [ ] aucun objet normal/décoratif/ressource statique sur Rocky
- [ ] montagne protégée contre Water/Lake/River overwrite

---

# 16. ORDRE DE VALIDATION HYDROLOGIQUE FINAL RECOMMANDÉ

Pour éviter les régressions rencontrées :

1. générer Water/Lakes ;
2. éliminer micro-étangs 1–4 ;
3. redistribuer dans lacs existants >4 ;
4. construire/valider Rivers ;
5. supprimer Rivers orphelines ;
6. appliquer plafond de longueur selon taille ;
7. reconstruire Shore/bathymétrie ;
8. fixer Water height=0 ;
9. fixer Water accessibility=1 ;
10. reconstruire Fish EN DERNIER ;
11. vérifier fish distribution + quantité + absence sur Rivers ;
12. checksum ;
13. export MAP ;
14. test SAV immédiat des invariants runtime.

---

# 17. PARTIE LONGUE EN COURS — STATUT EXACT

Partie actuellement continuée par l'utilisateur :
- map v3 avec **water accessibility fix** ;
- eau non marchable confirmée ;
- **aucun poisson**, bug connu ;
- utilisateur choisit de NE PAS recommencer.

Cette partie reste une excellente validation longue pour :
- starts ;
- expansion ;
- construction ;
- relief ;
- accessibilité terrestre ;
- bois ;
- Building Stone ;
- minerais ;
- biomes ;
- rivières ;
- obstacles de construction ;
- comportement global des joueurs ;
- crashs tardifs éventuels ;
- victoire de partie.

Elle ne doit PAS servir à juger :
- abondance de poissons ;
- économie de pêche ;
- équilibre fish par joueur.

Retours déjà tirés de cette partie :
1. Water accessibility bug trouvé puis corrigé.
2. Poissons absents trouvés ; couche à restaurer.
3. Minerais : +30 % quantité par case souhaitée.
4. Poissons futures : +30 % quantité par case souhaitée.
5. Rivières orphelines détectées.
6. Certaines rivières trop longues détectées.
7. Longueur max recalibrée sur corpus natif 21 SAV.

---

# 18. VALIDATION LONGUE FUTURE

Lorsque l'utilisateur finit la partie :
- enregistrer la save finale/victoire ;
- idéalement conserver quelques saves intermédiaires ;
- comparer au SAV début `slot 1(2).sav`.

Cette validation longue pourra renseigner :
- expansion territoriale ;
- consommation/épuisement minerais ;
- consommation pierre ;
- usage des forêts ;
- blocages de construction ;
- impact réel des rivières ;
- accessibilité des massifs ;
- équilibre entre joueurs ;
- stabilité runtime sur plusieurs heures ;
- conditions de victoire.

Le défaut poisson de la partie doit rester explicitement annoté.

---

# 19. ARCHÉTYPE GRANDES ÎLES — TANGENTE À NE PAS PERDRE

Prototype 384×384 / 4P Grandes Îles :
- une grande île par joueur ;
- taille/formes jugées très cool dès le premier prototype ;
- terrain balancing mauvais ;
- starts P1/P4 invalides probablement objets trop proches ;
- aucun crash.

Pour reprise future :
- préserver style/taille des îles ;
- équilibrer terrain/économie PAR île ;
- diagnostiquer objets proches avant de modifier terrain ;
- natural start zones ;
- bonus économie par île.

Cette tangente est garée pendant finalisation Continental.

---

# 20. PROCHAINE REPRISE NORMALE APRÈS PARTIE LONGUE

Après intégration du retour final :
1. appliquer tous les correctifs ci-dessus au générateur Continental ;
2. produire une nouvelle map de validation ;
3. checklist statique complète ;
4. test éditeur ;
5. test MAP/SAV immédiat ;
6. seulement ensuite reprendre validation multi-tailles.

Ordre prévu :
- 448
- 512
- 576
- 640
- 704
- 768

Une map à la fois.

---

# 21. INVARIANTS HISTORIQUES TOUJOURS ACTIFS

- ne jamais utiliser image_gen pour Settlers III ;
- previews seulement déterministes depuis EDM/MAP/SAV ;
- checksum toujours valide ;
- Rocky : aucun objet normal/décor/resource statique ;
- Rivers HEX6 ;
- Fish jamais sur Rivers ;
- Snow uniquement via Rocky chain ;
- Snow jamais directement Grass ;
- aucun Lake/River ne remplace Mountain ;
- décoration pierres /10 ;
- reefs rares (~10–12 sur 768), open sea, contournables ;
- Small Tree84 bonus séparé, ne remplace pas quota adult trees ;
- Building Stone stock fini, clusters naturels ;
- starts fair-play sans symétrie miroir imposée ;
- géographie naturelle/chaotique, éviter formes géométriques propres ;
- conserver les règles déjà validées sauf instruction explicite contraire.

---

# 22. FICHIERS / HASHES DU SNAPSHOT

- `S3_Continental_10P_768x768_seed_2026081801_checkpoint_rules_v2_final.edm` — 3,550,861 bytes — SHA-256 `f101f2fcf067d66435a939366d4393c8e821f50cb599e3ad509b828fa78f7ff7`
- `S3_Continental_10P_768x768_seed_2026081801_checkpoint_rules_v3_water_access_fix.edm` — 3,550,861 bytes — SHA-256 `363960f2dba98cf4bf0edaae67521e3844641c0a490a194d7ec067534807bc95`
- `1-S3_Continental_10P_768x768_seed_2026081801_checkpoint_rules_v3_water_access_fix.map` — 3,681,281 bytes — SHA-256 `bab3533bed6d7db54395cafa2f4f20f4bb40162a134e8ea9c518b64a2f2a8405`
- `S3_Continental_10P_768x768_seed_2026081801_checkpoint_rules_v4_water_fish_fix.edm` — 3,550,861 bytes — SHA-256 `aa983361b08af11d88c08aea3ec06f8d1b7be4bf0e8ec3e61e8a091e4eca06fc`
- `1-S3_Continental_10P_768x768_seed_2026081801_checkpoint_rules_v4_water_fish_fix.map` — 3,681,281 bytes — SHA-256 `a59caf5439e660b2a4438be3f37d51c63d3abe19f994adb40ed43f33273c120e`
- `SETTLERS3_WATER_WALKABILITY_FIX_20260818.md` — 1,985 bytes — SHA-256 `994c75c2daac062aea94df53fed66fa6bb3af47b4246c25e0ec931d2eaad06ad`
- `SETTLERS3_FISH_LAYER_RESTORE_20260818.md` — 1,556 bytes — SHA-256 `e163875c7fa3df4fc32953214673da4ddb619939260acec97208124c355d90bb`
- `slot 1(2).sav` — 22,214,329 bytes — SHA-256 `abbc64589e4958824fb6b4d42104a5cc12e037462c15b9126640f60d9af22882`
- `slot 1(1).sav` — 22,198,481 bytes — SHA-256 `71608676d27e6f45c43136240f290a2978fbc172cc6aa4d5fd050162007bbdb0`
- `SETTLERS3_MAPGEN_REFERENCE_v14_768_10P_VALIDATED.md` — 16,713 bytes — SHA-256 `7e10cbb83a7d95c66591a96546b8a1f92a6ecc04f22894c64226cf85616928a6`
- `SETTLERS3_TODO_POSTCHECKPOINT_v3.md` — 3,499 bytes — SHA-256 `3a5c534e739eb40082a3fde7bbd13893ad066f704f38cf1b09e8d18d3b679818`

---

# 23. RÉSUMÉ ULTRA-COURT À LIRE AVANT LA PROCHAINE GÉNÉRATION

**NE PAS OUBLIER :**
- Water accessibility = 1.
- Fish layer obligatoire après dernière passe hydrologie.
- Fish +30 % quantité/case, surface inchangée.
- Minerais +30 % quantité/case, surface inchangée.
- 0 micro-étang 1–4.
- 0 rivière orpheline.
- longueur rivière plafonnée PAR taille : 44/47/48/49/47/53/55.
- starts bonus hors quota, +50 % forêt/pierre.
- mini-marais bonus garanti.
- décor désert ×2.
- décor marais ×2.
- côte jamais tronquée par marge droite.
- tout test final doit passer EDM → MAP → SAV runtime.

---

# 24. POST-SNAPSHOT LONG-PLAY DEVELOPMENTS — BUILDING STONES / SMALLTREE84

## 24.1 Building Stone harvestability issue

User-reported non-harvestable stone areas:
- near x493 y126 -> anchor `(494,126)`;
- near x483 y105 -> anchor `(482,104)`;
- near x493 y140 -> anchor `(492,139)`.

Initial static checks ruled out obvious causes:
- active Building Stone IDs;
- Grass terrain;
- ordinary local slopes;
- normal runtime anchor state;
- territory ownership alone.

Map-wide analysis showed the generated stones usually have **only the anchor** flagged for accessibility/occupation, despite the previously calibrated 7-cell Building Stone footprint.

AI/territory analysis:
- all 10 player claims contain untouched stones while other stones in the same claim have already been harvested;
- a heuristic identified hundreds of untouched-in-owned-territory candidates near harvested stones;
- these are candidate problem stones, not proof that every one is blocked.

## 24.2 Strong runtime overlap evidence

Latest save:
`slot 6(2).sav`
SHA-256: `0397cc782839a92ae7ef37b3bbd3bec3c4d5b520249c4e75610f9b6e3589ced9`

Key observation:
- anchor `(492,139)` was previously runtime stage120 and non-harvestable;
- user demolished an adjacent building;
- the stone then became harvestable;
- latest runtime stage is **125**.

Interpretation:
the incorrect/incomplete stone footprint likely allows a building footprint or work/pathfinding occupation to overlap cells that should belong to the stone, temporarily preventing the stone from being selected/worked.

This is now a **high-confidence causal hypothesis backed by direct gameplay behavior**.

## 24.3 Building Stone future rule

Every future Building Stone must serialize/reserve the full calibrated 7-cell footprint:

```text
1 1 .
1 X 1
. 1 1
```

Apply full collision validation against:
- other Building Stone footprints;
- trees;
- decorations;
- static objects;
- technical start zones;
- building occupancy semantics.

Do not merely make stones sparser.

## 24.4 SmallTree84 validated

Initial SmallTree84 count in analyzed long-play lineage: **393**.

Advanced save:
- runtime ID84 remaining: **0**;
- 390/393 (~99.24%) evolved into tree-like runtime states or disappeared;
- user explicitly accepts disappearance as evidence of growth followed by felling.

Conclusion:
**current SmallTree84 bonus placement method is validated.**

Keep:
- separate SmallTree84 pool;
- does not replace adult-tree quota;
- current placement method.

## 24.5 Mandatory pre-generation protocol created

New mandatory entry point:
`SETTLERS3_PREGEN_READ_FIRST.md`

No future map generation/modification/export should begin from conversation memory alone.
The mandatory canonical set is listed in that file.

New canonical generation reference:
`SETTLERS3_MAPGEN_REFERENCE_v15_LONGPLAY_RULES.md`

New resource-object supplement:
`SETTLERS3_RESOURCE_OBJECTS_REFERENCE_v3_LONGPLAY.md`

New TODO:
`SETTLERS3_TODO_POSTCHECKPOINT_v4_LONGPLAY.md`

