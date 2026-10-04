# Roadmap des archétypes Custom

## Cap actuel — DEV9 clôturée, 2026-10-04

- Grandes îles R25, rivières améliorées et raccordements validés ; checkpoint DEV9.
- Source alternative renommée « Grandes îles — relief ondulé ».
- Anciens reports hors scope transférés à DEV10 pour priorisation après push.
- Petites îles : DEV10 ou DEV11, fork de Grandes îles ; autres forks éventuels.
- Finitions/publication : à répartir après bilan, aucun jalon DEV11 figé.
- Archipel hors 2.0 ; aucun nouveau fork engagé dans ce checkpoint.

Les repères historiques ci-dessous ne redéfinissent pas le scope terminé.

## Objectif

Transformer l’onglet Archétype en atelier capable de produire, enregistrer et
qualifier plusieurs profils de macro-forme viables. Les noises restent tous
autonomes et réutilisables seuls. Les usages spécialisés passent par les
opérations, transformations et masques appliqués au bruit, pas par des
providers artificiellement enfermés dans un rôle.

## Prototype historique R76

R76 garde la grille d’ancres aléatoires et le raffinement natif de R75, avec
moins de basses ancres près des bords, une plage basse légèrement plus large
dans le cœur, et une variation des détails fins à 75 % par défaut pour Custom.
Les lacs émergent toujours du relief, sans estampage ni quota. Les previews
testées ont moins de petites cuvettes et en montrent davantage dans la zone
centrale. Le Legacy natif et les sources noise-map complètes restent
indépendants. Vérifier sous Windows à 384/512/768 ; les rivières restent
reportées.

## Repères historiques et idées à replanifier

- [x] **Pile de fusions lisible — première tranche R33** : ordre haut/bas,
  duplication, suppression, activation rapide et mode Solo d’aperçu sont
  disponibles par carte, avec un ordre d’exécution persistant et borné à six
  slots. L’indication claire du champ avant/après chaque fusion et les vues
  miniatures source brute / contribution après opération / résultat cumulé
  restent à faire.
- [x] **Cycle de preview clarifié — R34** : sans lissage, une seule preview
  exacte est calculée ; avec lissage, la passe indicative reste disponible
  comme accélérateur. Solo respecte l’activation de la fusion, la miniature
  Legacy montre la source native brute et les seuils restent proches de la
  morphologie dans l’éditeur.
- [x] **Fidélité d’affichage — R35** : aucune passe indicative n’est peinte
  avant le résultat exact, la miniature principale réutilise le raster
  « Bruit / hauteur » et le bloc des seuils est réellement aligné en colonne 2.
- [x] **Transformations de sortie — R36** : inversion partielle, valeur
  absolue partielle, gamma et terrasses avec mélange réglable, appliqués de la
  même façon à la source principale et aux fusions ; le lissage est invalidé
  proprement au changement, les miniatures font 128², les réglages des fusions
  ne sont plus recouverts par les boutons et la source principale reste
  distincte du résultat composé.
- [x] **Transformations de coordonnées — R37** : décalage X/Y, échelles X/Y
  indépendantes, répétition X/Y et symétrie X/Y, avant les remappages de
  sortie et dans le même cadre rectangulaire fini.
- [x] **Remappage avancé — R38** : points noir/blanc pour le remappage
  asymétrique, seuils bas/haut durs ou adoucis, plancher/plafond de sortie et
  courbe asymétrique ; les valeurs neutres conservent le champ R37.
- [x] **Ergonomie ciblée — R39** : deux resets locaux seulement (bloc
  morphologie/source du relief/seuils et éditeur de fusions), avec mise à jour
  en place des contrôles et previews ; grilles indépendantes par fusion pour
  séparer l’en-tête, les réglages et les actions sans perdre de paramètres.
- [x] **Regroupement lisible — R40** : fondamentaux visibles et trois groupes
  avancés repliables séparément dans chaque source (sortie, remappage,
  coordonnées), sans suppression de paramètres ni changement de génération.
- [x] **Espace de travail adaptatif — R41** : fondamentaux repliables et ouverts
  par défaut, mini-previews redimensionnées depuis les tableaux en cache, et
  second séparateur vertical mémorisant la place de l’en-tête au-dessus des
  vues carte/onglets.
- [x] **Correction d’espace — R42** : contrôles de l’en-tête ancrés en haut
  lorsque le second séparateur est déplacé, reflow historique de Session /
  Comparaison conservé selon la largeur disponible, groupes resserrés et
  mini-previews revenues à leur taille fixe de 128².
- [x] **Pile de masques autonome — R46** : section séparée des fusions, avec
  compteur, activation, ordre, duplication, suppression, opérations,
  influence, réglages de forme et aperçu par slot. Les formes étoile, cœur,
  serpent et volcan modulent le champ après les fusions avec des bords doux et
  sans couper la variation hors silhouette ; les profils R44 migrent vers ce
  contrat.
- [x] **Contrat de masque générique — R47** : les cartes n’exposent plus les
  paramètres propres aux formes. Les six réglages spatiaux communs restent
  disponibles, tandis que le payload d’un provider est conservé séparément ;
  un profil neuf commence aussi avec zéro fusion active.
- [x] **Masque dessinable/importable — R48** : provider `Dessin libre` dans la
  même pile, grille 64×64 peignable/effaçable, import d’image en niveaux de
  gris, export PNG et preview issue du signal réellement appliqué. La grille
  reste une modulation spatiale et ne devient jamais une fusion cachée.
- [x] **Outillage de qualification du masque — R50** : rapport JSON
  déterministe sur plusieurs tailles, seeds et miroirs, avec gates de
  reproductibilité, effet, couverture, variation hors masque et bordure d’eau.
- [x] **Calibration Continental diagnostique — R51** : profil dérivé du contrat
  natif, avec ajustement limité de l’échelle de forme et du contraste du
  relief, rapport baseline/delta et gate dur du placement des joueurs sur le
  chemin Custom basé sur Legacy. Il reste historique et aucun preset actif
  n’est remplacé.
- [x] **Composition Continental Custom — R52** : preset indépendant composé
  uniquement d’une source fBm, d’un `domain_warp` en blend et d’un `ridged` en
  add. Les trois briques sont visibles dans le sélecteur et les cartes de
  fusions de l’onglet Archétype ; le Continental natif reste inchangé.
- [x] **Enveloppe océanique native — R53** : le cadre et la transition du
  preset Custom Continental sont calibrés en cellules absolues sur la
  bibliothèque native 768, sans modifier les moteurs Legacy/Upgraded.
- [ ] **Marge initiale R63** : marge de domaine à 0 % pour tous les archétypes ;
  la source Legacy l’ignore et le Custom R53 conserve son fondu de bord à 8 %.
  Le retour visuel Windows doit confirmer la couverture d’eau et l’effet sur le
  littoral avant de valider ce défaut. Le fondu carré reste à réexaminer ensuite.
- [x] **Première tranche de providers — R54** : ajout de `hybrid_fbm`,
  `turbulence`, `worley_f1`, `worley_f2` et `worley_f2_minus_f1` dans le
  contrat de source autonome, avec sélection possible comme source, fusion ou
  source de masque. Le preset R53 reste inchangé.
- [x] **Cadrage et providers multifractals — R55** : les miniatures de fusion
  et de masque réduisent maintenant l’enveloppe absolue depuis le côté réel de
  la carte ; le signal appliqué aux masques partage cette enveloppe. Ajout de
  `heterogeneous_fbm` et `ridged_multifractal`, sans modifier le preset R53.
- [x] **Calcul des miniatures — R56** : normalisation et enveloppe mutualisées,
  cache borné par composant (source/masque) et invalidation ciblée lorsque
  seed, taille ou paramètres changent. Le pipeline natif reste inchangé.
- [x] **Fréquences selon la taille — R57** : option désactivée par défaut,
  fréquences recalculées depuis le côté effectif du domaine et retrait des
  octaves trop fines. Les valeurs du profil restent la référence 768×768.
- [ ] **Validation visuelle R53 et R57** : comparer l’option désactivée puis
  activée sous Windows sur les petites et grandes tailles ; ajuster le profil
  uniquement si les essais réels le justifient.
- [ ] **Qualification visuelle du masque — après R50** : rejouer sous Windows
  un masque réellement dessiné et un masque importé, puis conserver les
  éventuels écarts comme régressions ciblées avant le calibrage des archétypes.
- [x] **Gabarit de formes — R44, contrat migré** : première exploration des
  formes étoile, cœur, serpent et volcan. Son enveloppe globale dure n’est
  plus utilisée ; elle est conservée seulement pour lire et migrer les anciens
  profils vers la pile R46.
- [ ] **Gabarits complémentaires** : spirale, sablier, anneau, péninsule,
  dorsale, couloir et formes multi-masses, avec un champ de distance plutôt
  qu’un simple découpage binaire.
- [ ] **Qualifier le provider manuel au niveau utilisateur** : tester des
  silhouettes dessinées et importées sous Windows sur plusieurs seeds, tailles
  et miroirs ; décider ensuite si un format de points/vectoriel apporte un
  gain réel par rapport à la grille de niveaux de gris.
- [ ] **Modulations croisées** : modulation avancée des coordonnées par une
  seconde source, explicitement séparée du gabarit de forme et des fusions.
- [ ] **Formules avancées** : provider `formula` et/ou transformation
  `expression` avec une syntaxe limitée et déterministe (`x`, `y`, `noise`,
  distance au bord, seed, fonctions mathématiques autorisées). Ne jamais
  exécuter directement du Python fourni par l’utilisateur ; une courbe de
  remappage doit couvrir les besoins simples avant ce chantier.
- [ ] **Providers complémentaires** : crêtes directionnelles, bruit spectral
  et déformation par une autre source ; la première tranche Worley et
  multifractale/turbulente est livrée par R54.
- [ ] **Profils et comparaison** : nommer, dupliquer, enregistrer et charger un
  archétype ; comparer deux profils avec la même seed ; produire une galerie
  multi-seeds pour éviter de calibrer sur un cas chanceux.
- [ ] **Qualification reproductible** : tester plusieurs seeds, tailles et
  miroirs sur bordure d’eau, proportion terre/eau, masses connectées, diversité
  du relief, part montagne/neige et formes non coupées.

## Historique DEV9 — clôturé

- [x] **Rivières Custom hors Legacy** : réglées selon le retour utilisateur
  avec un bruit plus doux près des bords d’eau. Ne pas rouvrir sans nouvelle
  reproduction ; le Legacy natif reste protégé.

## Idées de profils à replanifier

- [ ] Continental compact irrégulier.
- [ ] Continent fragmenté avec mers intérieures.
- Grandes îles : DEV9 validée et clôturée ; Archipel : hors 2.0.
- [ ] Deux continents opposés, péninsules et détroits.
- [ ] Dorsale montagneuse, hauts plateaux et bassins.
- [ ] Profils circulaires ou quasi-atoll lorsque les masques le permettent.

Une seule seed réussie ne suffit pas : un profil doit conserver son identité
sur plusieurs seeds, tailles et miroirs, garder une distribution terre/eau
contrôlable, éviter le relief plat et les micro-masses accidentelles, puis
rester compatible avec la génération jouable.

## Principes de qualification et équilibrage ultérieur

Le placement légal des joueurs reste qualifié avec chaque archétype. Comparer
plusieurs algorithmes pour leur équilibrage est un chantier futur distinct.

- [ ] Pour Grandes îles et Petites îles, comparer « une île principale par
  joueur », « un joueur par île » et « plusieurs joueurs sur une même île »
  selon le nombre de joueurs et la taille.
- [ ] Définir par archétype la masse jouable, les distances, la connectivité,
  les îles neutres autorisées, les halos de sécurité et la compatibilité avec
  ressources/objets.
- [ ] Rejouer le solveur de starts dès qu’une macro-forme modifie la surface
  disponible ; conserver la règle des starts placés tôt pour la balance et la
  prévention des positions invalides.
