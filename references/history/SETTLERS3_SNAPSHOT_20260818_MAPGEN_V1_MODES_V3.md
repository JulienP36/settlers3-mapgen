# Settlers III MapGen — Snapshot V3 — MapGen v1 + séparation des modes

Date : **2026-08-18**
Projet : **Settlers III MapGen**
Statut : **MapGen v1 fonctionnel ; architecture de génération à séparer en profils**

> Ce snapshot complète et supersède, pour l’état courant du programme et l’architecture des profils,
> `SETTLERS3_SNAPSHOT_20260818_LONGPLAY_V2.md`.
>
> Les règles techniques et gameplay détaillées de V2 restent valables pour le profil personnalisé/Continental+
> tant qu’elles ne sont pas explicitement remplacées ici.

---

# 1. MAPGEN V1 — ÉTAT ACTUEL

La première version du programme avec GUI est désormais fonctionnelle.

Fonctions déjà présentes / validées côté programme :
- GUI utilisable sous Windows ;
- installation/lancement Python corrigés ;
- choix du nombre de joueurs et du seed ;
- génération d’une map ;
- aperçu visuel déterministe depuis les vraies données de map ;
- validators PASS/FAIL ;
- export EDM/MAP ;
- architecture suffisamment bonne pour devenir la base durable du projet.

Retour utilisateur sur la GUI / programme :
- **excellent pour une v1** ;
- ne pas refondre le programme lui-même pour le moment ;
- priorité suivante = corriger/structurer les profils de génération.

Important :
- la génération actuellement produite par la v1 ressemble essentiellement à une génération **native/Settlers III classique** ;
- elle ne représente PAS encore le profil personnalisé raffiné construit au fil du projet ;
- aucun crash observé dans le test utilisateur récent ;
- **plusieurs positions de joueurs invalides** observées ;
- les starts Legacy devront donc être repris/calibrés séparément.

---

# 2. DÉCISION D’ARCHITECTURE — SÉPARER LES MODES DE GÉNÉRATION

Le terme unique « génération Continental » mélangeait deux objectifs différents :
1. reproduire fidèlement le générateur natif Settlers III ;
2. produire le profil personnalisé amélioré développé avec l’utilisateur.

Cette ambiguïté doit disparaître dans le programme.

## Mode A — LEGACY

Objectif :
**imiter le générateur procédural natif Settlers III aussi fidèlement que possible.**

Principes :
- les statistiques du corpus des 21 SAV natifs sont la source principale ;
- conserver les comportements natifs même lorsqu’ils diffèrent des choix custom ;
- très peu d’ajustements « qualité de vie » ;
- ne PAS importer automatiquement les règles personnalisées du profil Continental+ ;
- génération comparable au jeu original ;
- sert aussi de baseline de comparaison et de laboratoire de reverse-engineering.

État actuel :
- la génération MapGen v1 ressemble essentiellement à ce mode ;
- aucun crash observé sur le dernier test ;
- plusieurs starts invalides ;
- **TODO Legacy prioritaire : fiabiliser la génération des positions de départ sans dénaturer le reste.**

---

# 3. Mode B — CONTINENTAL+ / PERSONNALISÉ VALIDÉ

Nom recommandé : **Continental+** ou **Custom Balanced**.

Ce profil est **NOTRE génération personnalisée**, raffinée pendant toute la phase de reverse-engineering et de long-play.

Il ne faut surtout pas le reconstruire de mémoire à chaque fois :
il doit être implémenté comme un preset versionné à partir des références/checkpoints.

## Règles custom à récupérer / préserver

### Géographie / morphologie
- Continental ;
- formes naturelles, chaotiques, très irrégulières ;
- pas de formes géométriques propres ;
- pas de warp global déformant les formes ;
- côte non tronquée artificiellement ;
- marge océanique naturelle ;
- relief roulant ;
- montagnes/lacs/déserts/swamps selon les formes validées ;
- Snow uniquement via chaîne Rocky ;
- Mountain immuable face aux passes Water/Lake/River.

### Hydrologie custom
- **0 inland Water components 1–4** ;
- redistribution uniquement vers des lacs existants >4 ;
- jamais créer un nouveau lac uniquement pour compensation ;
- River HEX6 ;
- River connectée à une masse Water valide ;
- **0 River orpheline** ;
- River s’arrête au premier contact avec Water ;
- aucune River ne traverse ou continue dans Water ;
- longueurs pratiques par taille : 384→44, 448→47, 512→48, 576→49, 640→47, 704→53, 768→55 ;
- forme/meandering validés à conserver ;
- Water0..7 height=0 ;
- Water0..7 accessibility=1 ;
- Shore praticable sauf objet ;
- bathymétrie naturelle Shore → Water0 → … → Water7 ;
- bords externes en deep Water7 sans logique poisson dérivée du bord de tableau.

### Fish custom
- généré APRÈS la dernière passe hydrologique ;
- Water0..7 uniquement ;
- River96..99 = 0 poisson ;
- distribution basée sur les **vraies côtes/rives**, jamais sur le bord de map ;
- aucun poisson > HEX12 d’une rive valide ;
- pour 768, empreinte spatiale validée ≈ **32 313 fish cells** ;
- ne pas augmenter le nombre de cases ;
- **+30 % de quantité par case**, cap15 ;
- distribution indépendante/aléatoire par bande, pas de blobs cohérents.

### Minerais custom
Distribution spatiale v7 no-gap :
- nombreux petits blobs ;
- pleins/compacts ;
- légèrement ovoïdes ;
- pas de trous internes ;
- pas de singleton ;
- pas de moat vide forcé ;
- blobs peuvent fusionner naturellement.

Familles / proportions verrouillées :
- Coal 50.186 %
- Iron 21.564 %
- Gold 14.417 %
- Gems 5.446 %
- Sulfur 8.388 %

Pour 768, counts occupés verrouillés :
- Coal 28 375
- Iron 12 202
- Gold 8 164
- Gems 3 098
- Sulfur 4 745

Stock :
- empreinte spatiale inchangée ;
- **+30 % quantité par case**, cap15 ;
- famille high nibble conservée.

### Bois
Pour 768 :
- adult trees IDs68..72 : quota global validé **1 352** ;
- clusters naturels, lâches, nombreuses petites forêts ;
- **SmallTree84 séparé**, bonus, ne remplace jamais le quota adulte ;
- SmallTree84 long-play validé ;
- cible 768 actuelle autour de 406 selon le profil ;
- forêt bonus de start hors quota global.

### Building Stones
- stock fini ;
- global + bonus start ;
- bonus start hors quota global ;
- volume start +50 % vs ancienne règle 384 ;
- aucun Building Stone sur Rocky ;
- Building Stone IDs115..126 ; 127 = épuisé ;
- footprint calibré obligatoire :

```text
1 1 .
1 X 1
. 1 1
```

- sérialiser/réserver les 7 cellules ;
- collision footprint vs footprint interdite ;
- collision avec arbres/décors/objets interdite ;
- éviter qu’un bâtiment puisse overlap le footprint ;
- gameplay long-play : une pierre bloquée est redevenue minable après démolition d’un bâtiment adjacent ;
- espacement réel exact de hitbox encore à calibrer ;
- **ne pas considérer le simple footprint 7-cell comme calibration finale de distance éditeur.**

### Starts custom
- architecture géographie + placement start fair-play ;
- footprint natif 33 cellules ;
- terrain local naturel ;
- pas de disque/cercle artificiel Grass ;
- sécurité technique locale uniquement ;
- forte dispersion ;
- bonus hors quota ;
- chaque joueur : petite forêt bonus + Building Stones bonus + mini-marais visible contrôlé ;
- mini-marais hors zone technique dangereuse ;
- global Swamp interdit dans la zone technique start.

### Décorations
- aucun objet normal/décor/ressource sur Rocky ;
- Swamp → Reeds uniquement ;
- Desert → Dead Trees / Cacti / Skeletons / Palms selon règles ;
- décor désert ×2 ;
- décor marais ×2 ;
- décor stones /10 ;
- reefs rares ≈10–12 sur 768, open sea et contournables.

---

# 4. Mode C — EXPERT / CUSTOM MANUEL

Nom recommandé : **Expert**.

Objectif : permettre à l’utilisateur de modifier manuellement les paramètres du moteur.

Ce mode ne remplace PAS Continental+.
Il dérive des mêmes modules, mais expose les variables.

Exemples de paramètres futurs :
- % eau ;
- marge océanique ;
- % montagne ;
- densité Snow ;
- nombre/taille lacs ;
- nombre/longueur rivières ;
- % Desert/Swamp ;
- quotas arbres/SmallTree84 ;
- quantité de pierre ;
- minerai par famille ;
- fish coverage / quantity ;
- nombre de reefs ;
- bonus starts ;
- tailles de buffers ;
- profils de décorations ;
- paramètres de relief.

## Sécurité / UX

Ce mode doit clairement signaler :
**« paramètres non validés — à vos risques et périls »**.

Catégories proposées :
- SAFE : modifiables sans casser la structure ;
- RISKY : peuvent déséquilibrer/causer starts invalides ;
- HARD / LOCKED : ne devraient pas être désactivables par défaut car crash/game corruption possible.

Les validators restent actifs même en Expert.
Une map expérimentale FAIL doit être explicitement marquée **UNSAFE / DEBUG**.

---

# 5. NOMMAGE RECOMMANDÉ DANS LA GUI

```text
Generation Profile:
  Legacy (Settlers III)
  Continental+ (Balanced Custom)
  Expert
```

Alternative française :
- Legacy / Fidèle au jeu
- Continental+ / Personnalisé validé
- Expert / Manuel

---

# 6. ARCHITECTURE PROGRAMME À VISER

Le programme ne doit pas avoir trois générateurs totalement séparés.

Préférer :
- un même moteur/pipeline ;
- plusieurs **profiles** de configuration ;
- quelques stratégies spécifiques lorsqu’un comportement Legacy diffère réellement du Custom.

Exemple :

```text
profiles/
  legacy.json
  continental_plus.json
  expert_user.json

generation/
  geography/
  terrain/
  hydrology/
  resources/
  objects/
  starts/

validators/
  common/
  legacy/
  continental_plus/
```

Ainsi :
- une correction binaire commune profite à tous les profils ;
- Legacy et Continental+ peuvent diverger sur leurs règles de gameplay ;
- Expert réutilise la même infrastructure ;
- les règles ne sont plus éparpillées dans des scripts ponctuels.

---

# 7. VALIDATION MAPGEN V1 — IMPORTANT

Les validations de la v1 montrent que le programme sait appliquer **les règles actuellement encodées** de manière cohérente.

Cela ne veut PAS dire que ces règles sont déjà le bon profil Continental+.

Le test utilisateur récent établit :
- GUI/programme : bonne base ;
- map produite : proche d’un mode Legacy ;
- pas de crash observé ;
- plusieurs starts invalides ;
- notre profil custom raffiné doit encore être récupéré des références/checkpoints et encodé explicitement.

Donc :
**ne pas corriger la génération actuelle en mélangeant Legacy et Continental+.**
La conserver comme base du futur profil Legacy et développer Continental+ à côté.

---

# 8. PRIORITÉS APRÈS CE SNAPSHOT

1. **Ne pas refondre la GUI v1.**
2. Introduire conceptuellement les trois profils.
3. Conserver l’implémentation actuelle comme base Legacy.
4. Legacy : reprendre les starts invalides séparément.
5. Reconstituer `continental_plus` depuis snapshot long-play V2, PREGEN, MapGen v15+, Continental profile, resource/object references, checkpoints validés et retours long-play.
6. Transformer chaque règle Continental+ en config + étape + validator.
7. Seulement après, générer une première map Continental+ depuis le programme.
8. Expert viendra après stabilisation de Legacy + Continental+.

---

# 9. RÈGLE DE NON-RÉGRESSION DU PROJET

À partir de maintenant :

> Une règle validée pour un profil doit exister dans le code sous au moins une forme vérifiable : configuration versionnée, implémentation de pipeline, validator ou test.

Ne plus dépendre uniquement :
- de la mémoire conversationnelle ;
- d’un Markdown lu manuellement ;
- d’un script jetable.

Les Markdown restent la documentation/source historique.
Le programme devient progressivement la **source exécutable de vérité**.

---

# 10. VISUELS

Règle permanente :
- jamais de génération d’image imaginaire pour Settlers III ;
- aperçu GUI/PNG uniquement déterministe depuis les vraies données EDM/MAP/SAV / modèle Area réellement généré.
