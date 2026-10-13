# Agencement adaptatif — DEV10 R19

Les seuils de passage à la ligne utilisent les demandes réelles des widgets,
avec leurs marges. La langue, la police et l’échelle Tk contribuent à ces demandes.
Les sprites ne sont pas réduits pour faire tenir les boutons.

| Zone | Calcul / correction |
| --- | --- |
| Éditeur | Padding boutons (5,0,5,1), grille padx 2/pady 1 partout ; sprites 24 px |
| Catalogue | Fiches compactes, largeur maximale requise +16 px de marges ; Nom · Taille sur une ligne ; charger/poubelle côte à côte ; pas de plafond de colonnes |
| En-tête | Génération + Session naturelle + commandes globales + gouttières ; recalcul sur allocation réelle du conteneur |
| Session | Minima de colonnes et contraintes des widgets couvrant plusieurs colonnes ; largeur compacte uniquement si nécessaire |
| Vue | Somme des demandes et des 36 px de marges réelles ; padding du conteneur déduit |
| Générateur / bonus | Largeur réelle du viewport moins padding ; rangées indépendantes, réserve supplémentaire supprimée |

L’en-tête conserve ses régions fonctionnelles. À la largeur minimale, les commandes
globales peuvent occuper une rangée supplémentaire avant Session pour éviter le rognage.
Les rangées indépendantes ont chacune leurs colonnes : une grande fiche dans une
rangée ne peut pas élargir les espaces dans une autre. Les hôtes de rangées sont
réutilisés ; aucun rechargement de fiches, sprites ou masques lors du redimensionnement.

Le placement automatique des trois previews garde ses seuils et son hystérésis
pour leur lisibilité ; ce n’est pas un calcul d’empaquetage de boutons. Les tailles
minimum utiles des contrôles et les groupements préférés sont également conservés.
F11 conserve le partage vue/onglets 55/45 ; génération et formats natifs inchangés.

Mesures Tk en français : sprites 24 px, boutons de l’éditeur 31 px de haut ; fiche
catalogue avec marges 259 px, deux colonnes à 560 px, trois à 800 px. Les dimensions
Windows peuvent varier avec la police et le DPI ; contrôle visuel Windows requis.

R19 : gap Copier seed/Importer 4 px au lieu de 7 ; taille des sprites inchangée.
