# Settlers III MapGen — journal de développement v1.8

Ce document consolide les 39 notes de candidates auparavant dispersées à la racine du dépôt. Il conserve les décisions finales, les essais structurants et les régressions importantes de DEV_1 à DEV_8. Les textes intégraux des anciennes notes restent récupérables dans l’historique Git, notamment au commit `94f48d1` qui clôture DEV_8.

## Règles communes

- Le moteur de génération v1.5, les formats EDM/MAP/SAV et les cinq éléments protégés sont restés inchangés pendant ces passes UI/outillage.
- Toutes les miniatures et tous les aperçus proviennent de données réelles générées ou importées ; aucun raster fictif n’est utilisé.
- Les changements visuels ont été validés sous Windows avant leur publication comme checkpoint final.
- Les nombres de tests indiqués correspondent au dernier checkpoint automatisé de chaque passe.

## Chronologie compacte

| Passe | Checkpoint retenu | Résultat principal | Tests finaux |
|---|---|---|---:|
| DEV_1 | DEV_1 | A/B simplifié, titre FR/EN et références post-v1.7 | — |
| DEV_2 | DEV_2_R7 | Header responsive stable et feedback utilisateur | 90 |
| DEV_3 | DEV_3_R7 | Génération Batch 1–4 cartes et aperçus réels | 109 |
| DEV_4 | DEV_4_R6 + PERF+ R1 | Vues Départs/Territoires, sprites natifs et rendu en calques | 139 |
| DEV_5 | DEV_5_R3 | Centres d’export cartes et graphiques | 151 |
| DEV_6 | DEV_6_R1 | Interface dynamique FR/EN/DE/ES | 156 |
| DEV_7 | DEV_7_R10 | Historique unifié, protections et aperçus robustes | 192 |
| Expérience | TITLEBAR_TEST_R4 | Barres de titre Windows sémantiques | inclus dans la suite |
| DEV_8 | DEV_8_R4 | Raccourcis configurables v2 et Aide dynamique | 207 |

Chaque checkpoint final a également passé les 49 validations moteur, le checksum binaire et le contrôle des cinq hashes protégés.

## DEV_1 — premier polish post-v1.7

- Titre de fenêtre entièrement localisé FR/EN.
- Suppression du résumé A/B redondant ; commandes Vider A, Vider B et Vider A+B avec états cohérents.
- Conservation des identités courtes et indicateurs directement sur les boutons A/B.
- Création des registres vivants de reverse-engineering Terrain/Object et du snapshot post-v1.7.
- Ajout au README de la note de transparence sur l’assistance importante de ChatGPT/OpenAI.

## DEV_2 — responsive UI et header fonctionnel

État final DEV_2_R7 :

- fenêtre adaptée à la résolution réelle, minimum 900×650 ;
- trois régions fonctionnelles indépendantes : Génération, Session/Comparaison et contrôles globaux ;
- passage compact avant que Langue/Aide/Thème ou A/B soient tronqués ;
- outils Vue/Carte thermique/Recentrer/Zoom placés dans la barre contextuelle du viewer ;
- progression rapide conservée dans l’overlay carte, feedback utilisateur semi-persistant séparé ;
- emplacement Modificateurs réservé après Archétype et déjà intégré à l’identité de cache ;
- croix rouge active pour vider individuellement A ou B.

Leçon conservée : la tentative R5 de réorganisation tardive par `PanedWindow`/reparenting a été abandonnée. La construction directe des blocs dans leurs parents définitifs est la base stable à privilégier.

## DEV_3 — génération par lots

État final DEV_3_R7 :

- fenêtre Batch FR/EN, 1 à 4 cartes et paramètres indépendants ;
- seed commune, application globale, dés global et dés individuels ;
- génération séquentielle, réutilisation du cache, annulation des cartes en attente et ajout à l’historique ;
- progression/feedback par ligne, affichage et affectation A/B exclusive ;
- miniatures déterministes et grand aperçu sans chrome, transparent en parallélogramme ;
- projection actualisée en direct, placement prévisible et fenêtre dimensionnée depuis son contenu ;
- nombre de cartes appliqué immédiatement, sans bouton de confirmation redondant ;
- zone finale de miniature 182×122, rendu maximal 180×120.

La faible diversité morphologique observée entre plusieurs seeds a été archivée pour l’audit moteur v1.10, sans modification spéculative dans DEV_3.

## DEV_4 — vues joueurs, marqueurs et performances

### Vues et sprites — DEV_4_R4

- Global épurée ; nouvelle vue Départs ; Territoires placée immédiatement après.
- Vingt sprites J1–J20 extraits de la référence utilisateur, fond herbe rendu transparent et ancrage au centre géométrique.
- Masque initial natif : 3500 cellules, frontière HEX6 exacte de 210 cellules.
- Départs : 210 marqueurs sans chevauchement, 1×1 en Carrée et 2×2 en Parallélogramme, plus le marqueur central.
- Opacité 0–100 % appliquée uniquement au calque des sprites.
- Territoires SAV fondée sur les claims runtime réels ; EDM/MAP reconstruits uniquement à l’écran depuis le masque initial connu.

### Aperçus — DEV_4_R5/R6

- Réglage persistant `Masqués / Petits / Normaux`, valeur par défaut `Petits`.
- Base raster sans marqueurs réutilisée ; changement de taille limité à la recomposition des sprites.
- Grand aperçu Batch épinglable, déplaçable et remplaçable à position constante.
- Recliquer la miniature source ferme l’aperçu ; `Échap` reste une sortie de secours.
- Double tampon lors des changements de projection/miniature afin d’éviter le clignotement.

### PERF+ R1

Le pilote en calques a été conservé après validation Windows sans régression visible : terrain carré colorisé séparé, projection dérivée, sprites composés en dernier et invalidations ciblées.

Mesures locales indicatives sur 768×768 :

| Opération | Médiane |
|---|---:|
| Rendu Global Carré complet | 50,52 ms |
| Rendu Global Parallélogramme complet | 59,76 ms |
| Composition Carrée depuis cache | 0,10 ms |
| Projection depuis carré colorisé | 7,89 ms |
| Recomposition Départs depuis cache projeté | 2,62 ms |

Les bases raster Batch bornées à quatre résultats représentent environ 60,7 Mio au maximum, hors objets Tk, miniatures et copies transitoires.

## DEV_5 — centres d’export

État final DEV_5_R3 :

- centre Cartes : EDM, MAP, copie SAV strictement inchangée, PNG Global et PNG Vue actuelle ;
- centre Graphiques : JSON, CSV et PNG du graphique affiché ;
- dossier et nom communs, noms produits actualisés en direct et confirmation groupée des écrasements ;
- formats impossibles désactivés, grisés et barrés avec explication séparée ;
- PNG Vue actuelle désactivé lorsque Global produirait le même résultat ;
- modalité Windows stricte : aucune interaction extérieure par clic, molette, clavier ou raccourci ;
- géométrie basse, survols et thèmes clair/sombre corrigés.

La hauteur initiale est calculée depuis le contenu. Toute extension future doit rester contrainte à l’écran et introduire une zone défilable si le contenu ne tient plus.

## DEV_6 — langues dynamiques

- FR/EN/DE/ES dynamiques et persistants dans l’interface principale, Batch, exports, aide, statistiques, graphiques, légendes et tooltips.
- Repli anglais lorsqu’une entrée manque.
- FR/EN sont les références relues ; DE/ES sont automatiques et seulement partiellement revues.
- Limite acceptée : le rapport texte Statistiques déjà calculé ne change de langue qu’après rechargement de la carte. Correction reportée à la future amélioration de l’onglet.

## DEV_7 — historique de session et grands aperçus

État final DEV_7_R10 :

- historique de session commun aux générations simples, Batch et imports EDM/MAP/SAV ;
- dédoublonnage des imports par SHA-256 et conservation exacte de la source SAV ;
- capacité persistante 4/8/12/16, ordre stable pour les actions visuelles et compteur utilisé/capacité ;
- Centre d’historique avec rang `#`, détails, sélection stable, miniature et aperçu agrandi ;
- protections explicites `V`, `A`, `B`, combinables et accompagnées d’infobulles ; rôle `M` réservé au futur verrouillage manuel ;
- suppression/vidage avertissant puis libérant correctement A/B, tandis qu’une carte courante retirée peut rester visible avec signalement hors historique ;
- prévision Batch exacte des évictions et résultats non conservés pour toutes les capacités ;
- aperçu Batch/Historique à cinq états visuels, survol 700 ms, clic, drag, zoom 35–125 %, remplacement atomique et parité d’interaction ;
- aperçu temporaire automatiquement placé/réduit afin de ne jamais masquer sa miniature source ; aperçu épinglé volontairement libre.

Régression structurante corrigée en R9 : fermer le Centre laissait une référence Tk détruite utilisée au prochain rafraîchissement. Les callbacks sont désormais annulés avant destruction et chaque rafraîchissement vérifie l’existence réelle de la fenêtre et du widget.

Anomalie non reproduite, conservée pour surveillance : un calcul Statistiques a semblé exceptionnellement long pendant un test R5.

## Expérience barres de titre Windows — TITLEBAR_TEST_R4

- Utilisation du cadre natif Windows : boutons système, Snap, déplacement et redimensionnement préservés.
- Actualisation uniquement à l’ouverture d’une fenêtre ou au changement de thème ; aucune boucle de surveillance.
- Thème sombre : barre `#15171a`, texte `#e8eaed`, séparateur `#6f7378`, contour `#3c4043`.
- Thème clair : barre `#dfe3e8`, texte `#202124`, séparateur `#8f969e`, contour `#aeb3b8`.
- Rôles sémantiques réutilisables par de futurs thèmes.

L’ancienne Aide native, initialement hors inventaire, a été remplacée et intégrée au système thémé dans DEV_8.

## DEV_8 — raccourcis configurables v2

État final DEV_8_R4 :

- capture directe d’une combinaison depuis le contrôle focalisé ;
- désactivation et réinitialisation par action, conflits inline et changements non appliqués visibles ;
- défilement horizontal et vertical automatique de Paramètres/Raccourcis lorsque nécessaire ;
- commandes supplémentaires et persistance dans l’unique JSON de préférences ;
- migration entrée par entrée vers le schéma 2, avec repli indépendant des entrées invalides ;
- fenêtre Aide réutilisable, thémée, FR/EN/DE/ES et actualisée depuis les raccourcis réellement configurés.

Leçon Windows : les bits étendus Tk puis l’interrogation globale de l’état clavier ont produit des faux positifs `Alt` ou raté `Shift`. R4 ne consulte plus aucun état global : la combinaison est construite uniquement depuis les événements d’appui/relâchement de modificateurs réellement reçus. Touches simples et vrais Ctrl/Shift/Alt ont été validés sous Windows.

## Politique de notes à partir de DEV_9

- Une candidate en cours utilise uniquement `DEV_CANDIDATE_NOTES.md` à la racine.
- Ce fichier est remplacé à chaque révision R au lieu d’en créer un nouveau.
- À la clôture d’une DEV, les décisions finales et les essais structurants sont intégrés à ce journal ; le fichier roulant est ensuite retiré.
- Le détail intégral des candidates publiées reste disponible dans l’historique Git.
