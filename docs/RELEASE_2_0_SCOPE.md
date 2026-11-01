# Fin de 2.0 — périmètre arrêté, état revu le 31 octobre 2026

R7 validée le 19 octobre ; passe R13 acceptée le 31 octobre. Captures finales intégrées.
DEV11 clôturée et validée le 1er novembre ; aucun push intermédiaire. Checklist : RELEASE_2_0_CHECKLIST.md.
La suppression de rc est autorisée uniquement au moment de publier la 2.0.
La publication STABLE main/tag/Release reste soumise à autorisation explicite.

## Ordre de travail

1. Mini-audit Équilibré : terminé, voir bilan ci-dessous. Aucune modification
   d’algorithme ni correction urgente proposée sur cet échantillon.
2. R8 : regroupement retenu sous Diagnostic avec trois sous-onglets :
   Validations, Pipeline et Métadonnées. Implémentation autorisée le 21 octobre.
   Amélioration de lisibilité des diagnostics reportée après 2.0 ; conserver
   le détail technique. Organisation acceptée provisoirement le 22 octobre.
3. R9 : ancien lanceur/script de mise à jour retirés et documentation active nettoyée. Aucun check
   automatique, notification, téléchargement/remplacement en un clic. Les
   utilisateurs téléchargent les publications GitHub manuellement. Un éventuel
   bouton manuel dans un futur À propos reste une idée sans échéance.
4. R9 : dessins originaux 16×16 et 64×64 retrouvés et intégrés, ICO multi-tailles
   sans retouche artistique. Répartition acceptée le 27 octobre : petite pour
   16/20/24, grande pour 32 et plus. Julien dessinera une version intermédiaire
   plus tard ; elle ne bloque pas 2.0. Reste à vérifier sous Windows : exécutable Explorer,
   raccourcis, fenêtres, Alt+Tab, barre des tâches et Gestionnaire des tâches
   là où Windows présente une icône. L’icône actuelle peut servir à la 2.0.
5. Qualification du portable Windows préparée dans build/windows/qualify_portable.py.
   Build/essai natif non exécutés ici : Wine bloqué par une restriction IPC.
   Avant clôture DEV11 : compiler localement sous Windows avec
   build/windows/build_windows.bat (Python 3.12 sur la machine de build).
   Le runner CI contrôlera ensuite le checkpoint complet publié. Pour l’utilisateur :
   décompresser et lancer le .exe,
   sans installation de Python ni téléchargement de dépendances ; aucun .bat
   superflu dans ce portable. Revue des quatre BAT source/build terminée R10 :
   rôles distincts, conservés ; code retour du lanceur de build corrigé.
   Aucune branche temporaire avant fin DEV11 (rappel Julien du 24 octobre).
   Conservation vérifiée au niveau source/modèles R11 : chemins stables,
   fichiers retrouvés après déplacement, ancien schéma de préférences conservé.
   Correction du filtre des départs non sauvegardé par la GUI.
   Confirmer séparément ces parcours avec le véritable portable Windows.
6. Contrôles finaux : tests adaptés puis suite complète avant candidate
   fonctionnelle, intégrité ZIP/source/portable, auto-test extrait et essai réel
   Windows. Vérifier exports/éditeur/jeu selon les parcours touchés, sans
   prétendre qu’un contrôle Python remplace ces essais.
7. Finaliser documentation FR/EN, captures réelles et présentation GitHub.
   Clôturer DEV11, publier le checkpoint complet sur dev après validation du
   périmètre, puis préparer publication STABLE explicite, sans étape RC.
   Supprimer la branche rc à cette publication, pas avant.

## Reports explicites

- Aucun nouvel archétype avant l’après-2.0 ; conserver deux continents,
  péninsules, détroits, mers intérieures et quasi-atoll comme idées.
- Futur onglet Départs/Joueurs après 2.0 : affecter une même équipe à plusieurs
  joueurs ; évaluer déplacement manuel des départs selon effort et périmètre.
  Ancien report du 7 octobre : onglet automatique/algorithmes et placement manuel
  colons/piles/bâtiments, sans version initialement fixée. Ce périmètre large
  devra être recadré avant implémentation ; mode éditeur complet reste lointain.
- Terrains d’expansion exclusifs : ancien raffinement d’Équilibré, définition
  fonctionnelle non retrouvée. Ne pas inventer de contrat. Recherche ultérieure,
  pas de nouvelle fonctionnalité imposée à la 2.0.
- Stats 2 après 2.1 ; éditeur avancé de formules et mode éditeur complet reportés.
- Liste de configurations dans l’en-tête seulement lors d’un remaniement futur.

## Mini-audit Équilibré — résultats et limites

Base exacte : ZIP R7 livré, SHA-256
`d7b49e2fdeb2729391e972fcbe0948b1db58bc5d86943733f2b8aff93abc8be0`.
Code applicatif et données natives inchangés. Hashes protégés conformes.

14 cartes sur les deux moteurs, 256/384/512/768, de 2 à 12 joueurs :
92 départs demandés et placés, aucun échec de validation bloquante ni des
contrôles finaux des départs. Espacement préféré respecté dans les 14 cas.
Le seed historique 2026100817/512/4P passe sur les deux moteurs.
Six fonctions de tests existantes exécutées directement et réussies
(test_fair_starts.py, sauf celle qui nécessite monkeypatch). pytest absent de
l’environnement actuel : aucune exécution complète pytest revendiquée pour
cet audit. Les suites précédentes de R7 ne sont pas rejouées ; aucun code modifié.

L’algorithme score les cinq minerais accessibles localement par voie terrestre
(rayon 75 HEX6), pas les rivières ni une zone d’expansion exclusive. Le diagnostic
rivière ci-dessous mesure une distance géométrique HEX sur la même composante
terrestre, pas un trajet praticable ni une garantie économique.

Les deux cas Classique 256 ont zéro charbon et fer dans leur métrique locale :
leur validité de départ ne garantit pas la viabilité économique de cette taille.
La politique antérieure conserve les petites tailles natives sans exiger de les
rendre viables. Sur les 12 autres cartes, chaque départ dispose de charbon et
fer non nuls selon la métrique locale ; quantité égale et exclusivité non garanties.

Sur les îles individuelles 512/8P, huit départs se répartissent sur cinq masses
terrestres avec Legacy et six avec Upgraded. C’est conforme à l’absence de quota
par île de Fair ; utiliser Auto/Îles pour un départ par île. Fair reste refusé
sur Îles par équipe, par contrat existant, non ajouté dans la campagne supportée.

Conclusion : pas de défaut bloquant observé ni de correction urgente recommandée
sur cet échantillon. Ce mini-audit n’est pas une certification statistique,
un essai Windows/éditeur/jeu, ni une preuve d’optimalité. Les améliorations
rivières/expansion/garantie insulaire éventuelles demandent un lot distinct.

| Moteur | Géographie | Taille | Joueurs | Seed | Distance mini / cible* | Rivière min–max** |
|---|---|---:|---:|---:|---:|---:|
| legacy | Classique (source native) | 256 | 2 | 2026102001 | 173.4 / 83.2 | 12–12 (absence sur une masse) |
| legacy | Classique (source native) | 384 | 4 | 2026102002 | 95.0 / 94.3 | 21–81 |
| legacy | Classique (source native) | 512 | 4 | 2026100817 | 142.2 / 141.0 | 23–91 |
| legacy | Classique (source native) | 768 | 12 | 2026102003 | 131.6 / 129.5 | 7–165 |
| legacy | Îles individuelles | 512 | 8 | 2026102004 | 95.1 / 90.7 | 12–48 |
| upgraded | Classique (source native) | 256 | 2 | 2026102001 | 190.4 / 83.2 | 10–12 |
| upgraded | Classique (source native) | 384 | 4 | 2026102002 | 97.4 / 94.3 | 7–61 |
| upgraded | Classique (source native) | 512 | 4 | 2026100817 | 154.2 / 141.0 | 6–83 |
| upgraded | Classique (source native) | 768 | 12 | 2026102003 | 138.6 / 129.5 | 25–213 |
| upgraded | Îles individuelles | 512 | 8 | 2026102004 | 97.0 / 90.7 | 11–35 |
| legacy | Continental | 384 | 4 | 2026102005 | 104.8 / 100.6 | 40–106 |
| legacy | Continental | 768 | 12 | 2026102006 | 129.4 / 129.1 | 9–126 |
| upgraded | Continental | 384 | 4 | 2026102005 | 112.0 / 100.6 | 31–81 |
| upgraded | Continental | 768 | 12 | 2026102006 | 129.6 / 129.1 | 8–105 |

*Distance de coordonnées utilisée par le solveur, pas distance HEX.
**Distance HEX géométrique à une rivière sur la même masse, sans calcul de trajet.

