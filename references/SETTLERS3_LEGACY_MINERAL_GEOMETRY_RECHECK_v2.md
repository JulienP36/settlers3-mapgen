# Settlers III — recontrôle de la géométrie des minerais Legacy v2

> Vérification ciblée du 30 août 2026 sur les 16 SAV Legacy 768×768 : 8 cartes
> à 2 joueurs et 8 cartes à 20 joueurs.

## Conclusion

L’hypothèse d’un rayon minimal proche de 3 est compatible avec les données.
Les masques finaux contiennent aussi des concentrations compatibles avec des
enveloppes de rayon 4 et 5, donc avec des diamètres 7, 9 et 11.

Le diamètre 13 (rayon 6) n’est pas confirmé. Des fenêtres locales presque
pleines de cette taille existent, mais elles peuvent venir de plusieurs
hexagones voisins, de regroupements ou de l’écrasement successif des familles.
Elles ne prouvent pas qu’un hexagone natif de rayon 6 a été posé.

Pour la calibration, les rayons 3–5 sont donc la plage la plus défendable ; le
rayon 6 doit rester exceptionnel ou désactivé jusqu’à preuve supplémentaire.

## Méthode

L’analyse a repris les cellules finales non dilatées des 16 SAV. Pour chaque
famille et chaque centre possible, elle a balayé des disques HEX6 de rayon 3,
4, 5 et 6, en séparant le nombre de cellules remplies, la capacité théorique
(`1 + 3r(r+1)`) et la structure des composantes finales. La dilatation HEX1
de l’ancien rapport n’a pas servi à conclure sur les diamètres.

| Rayon candidat | Diamètre | Capacité HEX | Maximum local observé |
|---:|---:|---:|---|
| 3 | 7 | 37 | 37 pour toutes les familles |
| 4 | 9 | 61 | 61 pour toutes les familles |
| 5 | 11 | 91 | 87–91 selon la famille |
| 6 | 13 | 127 | 98–125, sans preuve d’enveloppe native |

Ces maxima sont des fenêtres dans le masque final, pas des traces directes de
la fonction interne du jeu. De même, les composantes finales dépassant le
diamètre 13 ne réfutent pas de petites enveloppes : des hexagones voisins ou
des familles superposées peuvent les fusionner.

## Conséquence R11 puis implémentation R12

La réduction de dispersion de R11 était pertinente, mais elle ne doit pas
produire un rayon unique. La suite doit utiliser une petite palette discrète,
vraisemblablement 3, 4 et 5, avec un remplissage réellement variable et
indépendant du rayon. Les hexagones proches, les recouvrements
charbon → fer → or → gemmes → soufre, l’absence de halo autour des starts et
la séparation des règles Upgraded v7 no-gap sont conservés.

Un SAV final ne conserve pas l’historique des écritures ; un état intermédiaire
du générateur du jeu serait nécessaire pour confirmer définitivement les
centres, rayons et l’ordre réel.

R12 applique cette conclusion sans élargir l’hypothèse : les tailles groupées
calibrées dans le profil sont découpées en hexagones élémentaires de rayon 3,
4 ou 5. Le rayon est tiré indépendamment du remplissage ; les groupes gardent
un centre voisin d’un élément au suivant, et un garde d’un seul hexagone
empêche seulement la répétition exacte d’un centre dans une même famille.
Les sondes 768×768 2P et 20P terminent sans shortfall et sans rayon supérieur
à 5. Cette implémentation reste une approximation contrôlée : elle ne prétend
pas révéler l’algorithme interne du jeu.
