# Settlers III MapGen — Release validation

Date: 2026-08-19

## v1.5 — VALIDÉE / STABLE

### Scope
La v1.5 consolide le moteur après la v1.4 UI : séparation Legacy/Upgraded auditée, ressources/objets recalibrés, starts bonus reconstruits et runtime final v1.5.

Points principaux :
- Legacy et Upgraded partagent la macro-morphologie mais ont des politiques hydrologie/biomes/ressources/objets explicitement séparées ;
- starts placés très tôt et protégés ;
- neige commune `Rocky32 -> 35 -> 129 -> Snow128`, Terrain34 variante Rocky interne/minéralisable ;
- Upgraded : plans d'eau 1–4 supprimés/redistribués, trimming rivière size-scaled, minerais ~90 % support, Swamp ~+30 %, Mud désactivé ;
- **géométrie minière v7 no-gap canonique** : blobs élémentaires pleins, compacts, légèrement ovoïdes, tailles lognormales ~18–105 cellules, aucun trou/singleton/moat forcé, fusion naturelle autorisée ;
- arbres `68..77 + 80..81`, Palms `78..79` comptées comme bois ; Upgraded ~130 % volume natif + SmallTree84 séparé ;
- bonus Upgraded : forêt `41 adultes + 21 SmallTree84` et Building Stones `8 ancres / 84 unités`, centrés sur la bordure du territoire initial (~HEX34) ;
- Building Stones globales variées `115..127`, environ 20 ID127 vides sur 768 ;
- ID127 compte dans la densité mais pas dans le stock exploitable et son ancien footprint est statiquement libéré (`accessibility=0`) ;
- récifs Upgraded à au moins 2 cellules des bords ;
- Goods Default : Legacy=Medium (`2`), Upgraded=High (`3`) ;
- GUI/CLI/exports nommés v1.5.

### Référence finale
`S3_V1_5_V7NOGAP_CORRECTED_UPGRADED_4P_768x768_seed_2026082202`

L'ancienne candidate `S3_V1_5_FINALCANDIDATE_UPGRADED_4P_768x768_seed_2026082201` est explicitement invalidée pour la **forme des minerais** et ne doit jamais servir de référence.

### Validation utilisateur finale
Sur la candidate v7 corrigée :
1. ouverture éditeur : **PASS** ;
2. starts : **PASS** ;
3. View Map / lancement in-game : **PASS, aucun crash** ;
4. rendu général : **PASS** ;
5. bonus de starts : **validés** ;
6. répartition visuelle Building Stones `115..127` : **validée** ;
7. géométrie minière v7 no-gap : **validée explicitement comme exactement conforme au style recherché**.

Le test pratique « construire directement sur l'ancien footprint d'un ID127 » est différé vers une **micro-map de régression dédiée**. Ce test n'est pas bloquant pour v1.5 : le comportement natif est connu et le modèle statique v1.5 libère déjà les 7 cellules avec le validator `STONE_EXHAUSTED_BUILDABLE`.

Conclusion : **v1.5 est validée et considérée stable pour le périmètre Continental 768 actuellement calibré.**

## v1.4 — VALIDÉE
La v1.4 est la release UI validée : thème sombre/clair, overlays/opacité, projection parallélogramme, drag/zoom, marqueurs joueurs, territoire initial, combobox sombre et sliders améliorés. Goods Default corrigé et morphologie Upgraded indépendante validée.

## v1.3.2 — VALIDÉE
Validation externe sur Continental 768 Legacy/Upgraded 4P et 20P : starts acceptés, aucun crash View Map/in-game, marais corrigés, neige intérieure non traversable.

## Correctif Goods Default — VALIDÉ
Legacy sérialise Medium (`2`), Upgraded High (`3`), fallback Medium. Contrôle en jeu validé sans crash.

## Morphologie Upgraded indépendante — VALIDÉE
Candidate `S3_Continental_Upgraded_4P_768x768_seed_2026081908_archetype_library_v1` validée : géographie excellente, starts OK, aucun crash et relief conforme à la référence native source.
