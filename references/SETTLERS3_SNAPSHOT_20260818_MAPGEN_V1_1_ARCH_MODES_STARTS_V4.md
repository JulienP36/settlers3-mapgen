# Settlers III MapGen — Snapshot V4 — Archétypes, modes et starts précoces

Date : **2026-08-18**
État programme : **MapGen v1.1**

> Ce snapshot complète le snapshot long-play V2 et remplace la terminologie provisoire « Continental+ ».
> Les règles gameplay détaillées du snapshot long-play restent la source du futur mode **Upgraded** tant qu'elles ne sont pas transcrites dans le code.

---

# 1. Deux axes indépendants

## 1.1 Archétype = macro-forme uniquement

L'**archétype** décrit principalement la topologie globale :
- répartition terre/eau ;
- nombre et hiérarchie des grandes masses terrestres ;
- position relative / séparation des masses ;
- présence éventuelle d'une masse principale.

Exemples réservés :
- Continental ;
- Large Islands ;
- Small Islands ;
- futurs archipels / multi-continents, etc.

L'archétype **ne doit pas décider** :
- densité ou formes locales des montagnes ;
- déserts/marais ;
- objets ;
- ressources ;
- fish ;
- balance ;
- starts ;
- quotas gameplay.

Même la forme locale des côtes peut être influencée par le mode : l'archétype dit « où sont les masses », le mode dit « comment leurs contours locaux sont construits ».

---

## 1.2 Mode de génération = contenu et règles

Noms de travail validés :

### Legacy
Objectif : fidélité maximale à Settlers III / au corpus natif.

Le mode Legacy décide notamment :
- morphologie locale ;
- transitions ;
- relief ;
- formes de zones ;
- hydrologie détaillée ;
- ressources ;
- objets ;
- densités ;
- balance ;
- stratégie de starts ;
- validators Legacy.

Il peut être combiné avec un archétype que le jeu original ne proposait pas. Par exemple `Large Islands + Legacy` signifie : macro-forme Large Islands, remplissage/règles de style Legacy.

### Upgraded
C'est **notre preset personnalisé validé**, accumulé pendant le projet.

Il récupérera toutes les règles custom des références/checkpoints/long-play : eau bloquée, fish custom, minerais v7, micro-lacs interdits, rivières corrigées, bonus starts, SmallTree84, Building Stones, décorations, etc.

Important : ne pas activer Upgraded avec une implémentation partielle. Chaque règle récupérée doit devenir config + pipeline + validator/test quand pertinent.

### Custom
Mode manuel futur.

Même moteur, mais variables exposées à l'utilisateur. Les validators restent actifs. Les paramètres risqués/unsafe devront être clairement signalés.

---

# 2. Ordre architectural des starts — règle dure

Les **starts doivent être générés très tôt**.

Raison :
1. éviter les positions techniquement invalides ;
2. permettre au reste de la géographie de s'adapter ;
3. équilibrer les ressources autour de positions déjà connues ;
4. réserver les zones techniques avant objets/hydrologie détaillée ;
5. placer les bonus locaux hors quota global sans bricolage final.

Ordre canonique :

```text
1. MapConfig (taille / joueurs / seed)
2. Archetype.generate_macro_layout()
3. GenerationMode.prepare_startable_surface()
4. GenerationMode.place_starts()          <<< TRÈS TÔT
5. reserve_start_zones()
6. relief / biomes / hydrologie détaillée autour des starts
7. ressources globales
8. balance locale / bonus starts
9. objets / décorations
10. hydrologie finale + fish final si le mode le demande
11. validators
12. export
```

Une étape tardive **n'a pas le droit d'invalider un start réservé**.
Elle doit contourner/protéger sa zone ou provoquer un HARD FAIL du générateur.

Le placement des starts n'est donc jamais :
`générer toute la map -> chercher où caser les joueurs`.

---

# 3. Stratégies de starts par mode

## Legacy
- rechercher/imiter la logique native ;
- fidélité statistique souhaitée ;
- mais ne jamais accepter volontairement une position invalide ;
- les starts invalides observés dans la première v1 sont un TODO Legacy spécifique.

## Upgraded
- logique fair-play/maximin robuste ;
- footprint 33 cellules ;
- forte dispersion ;
- zone technique réservée ;
- terrain local naturel, aucun disque Grass artificiel ;
- bonus forêt/pierre/mini-marais hors quota ;
- géographie détaillée et balance adaptées aux starts déjà connus.

## Custom
- même infrastructure de réservation ;
- paramètres exposables ;
- impossibilité par défaut de désactiver les invariants binaires/crash-critical.

---

# 4. MapGen v1.1 — changement programme

La GUI conserve l'excellente base v1 et ajoute :
- champ **Mode de génération** : Legacy / Upgraded / Custom ;
- champ **Archétype** : Continental / Large Islands / Small Islands ;
- distinction explicite entre les deux axes ;
- métadonnées mode/archetype ;
- starts placés immédiatement après le macro-layout ;
- réservation de la zone start avant corrections hydrologiques détaillées.

État réel de l'implémentation :
- `Legacy + Continental` : activé ;
- `Upgraded` : réservé mais volontairement non activé ;
- `Custom` : réservé mais volontairement non activé ;
- Large Islands / Small Islands : réservés mais non activés.

Ce choix évite de produire encore une fausse version Upgraded incomplète.

---

# 5. Tests de non-régression ajoutés

La v1.1 teste explicitement :
- registres Mode et Archetype séparés ;
- noms Legacy / Upgraded / Custom ;
- starts placés avant l'hydrologie détaillée ;
- 20 starts restent valides après le pipeline complet Legacy/Continental ;
- Upgraded/Custom non implémentés échouent explicitement au lieu de fallback silencieux ;
- checksum/export existant reste valide.

---

# 6. Règle de non-régression du projet

> Une règle validée pour un mode doit finir dans le programme sous une forme vérifiable : configuration, étape de pipeline, validator ou test.

Les Markdown/checkpoints restent la source documentaire et historique.
Le programme devient progressivement la source exécutable de vérité.

---

# 7. Prochaine étape logique

Ne pas modifier davantage la GUI sans besoin.

Prochaine grosse tâche : **récupération exhaustive du preset Upgraded** depuis :
- PREGEN ;
- snapshot long-play V2 ;
- MapGen reference v15+ ;
- Continental profile ;
- références morphology/transitions/heightmap ;
- resource/object references ;
- checkpoints validés ;
- retours long-play.

Chaque règle devra être classée :
- COMMON ;
- LEGACY ;
- UPGRADED ;
- éventuellement CUSTOM-exposable.

Seulement après cette transcription, activer `Upgraded` dans la GUI.

---

# 8. Visuels

Toujours :
- aucun image_gen pour Settlers III ;
- aperçu GUI/PNG déterministe uniquement depuis la vraie `Area`/EDM/MAP/SAV.
