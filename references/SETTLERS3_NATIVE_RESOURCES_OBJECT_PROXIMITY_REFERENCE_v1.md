# Settlers III — référence native ressources Legacy et proximité des objets v1

> Première tranche empirique de la v2.0, produite le 30 août 2026 à partir de 16 SAV natifs 768×768 : 8 cartes à 2 joueurs et 8 cartes à 20 joueurs.

## Périmètre

Cette référence couvre uniquement les ressources Legacy et la proximité des objets avec les starts. Elle ne mélange pas les règles de ressources Upgraded et ne modifie pas le générateur.

Les 16 fichiers ont un checksum valide. Les 176 starts sont décodés depuis les blocs type 6 natifs. Les distances et composantes utilisent la topologie HEX6 confirmée.

## Ressources

Le byte 17 est exploitable directement pour les ressources initiales :

- `0x10` = charbon, `0x20` = fer, `0x30` = or, `0x40` = gemmes, `0x50` = soufre ; le low-nibble porte la quantité.
- Les poissons sont identifiés par un low-nibble non nul sur les terrains Water 0..7. Aucun poisson n’a été observé sur les IDs de rivière 96..99.
- Aucun code de ressource non classé n’a été rencontré.
- Toutes les cellules minéralisées sont sur la famille de supports montagneux observée (`17, 32, 33, 34, 35, 128, 129`) ; aucune cellule ne se trouve hors support attendu.
- La quantité moyenne est voisine de 8 par cellule codée pour toutes les familles, avec les valeurs 1..15 observées.

Médianes par carte sur cette tranche :

| Groupe | Minerais — cellules | Minerais — stock | Poissons — cellules | Poissons — stock |
|---|---:|---:|---:|---:|
| 2P | 39 937 | 318 893,5 | 46 071 | 362 478 |
| 20P | 39 935,5 | 320 330 | 43 736,5 | 343 577,5 |

Autour des starts, aucune cellule de minerai ou de poisson n’apparaît dans les rayons 10 ou 25. La distance médiane de la ressource la plus proche est de 42,5 hex pour les minerais et 35,5 hex pour les poissons en 2P ; 29 hex et 38 hex en 20P. Cela décrit une disponibilité locale observée, pas un rayon dur universel.

## Objets proches des starts

Le byte 14 est la représentation statique/base de l’objet et doit servir à reproduire le décor initial. Le byte 7 est conservé séparément : il contient des modifications runtime. Sur les 16 SAV, les différences byte 14/byte 7 totalisent 144 cellules exactes en 2P et 2 506 en 20P, principalement des suppressions/remplacements runtime.

Il n’existe pas de halo statique vide de 14 hex :

| Groupe | Premier objet statique médian | Cellules statiques dans r≤14 médianes | Cellules dans les empreintes nominales de 33 cellules |
|---|---:|---:|---:|
| 2P | 3,5 hex | 10,5 | 6 sur 16 starts |
| 20P | 5 hex | 9,5 | 26 sur 160 starts |

La densité statique `world_decor` est également supérieure localement à la densité globale :

| Groupe | Globale /1000 cellules | r10 | r25 | r50 | r100 |
|---|---:|---:|---:|---:|---:|
| 2P | 9,70 | 16,62 | 15,63 | 15,68 | 12,44 |
| 20P | 9,79 | 12,08 | 16,40 | 14,38 | 11,18 |

Les objets observés à très faible distance comprennent des pierres, petites plantes, champignons et buissons, mais aussi ponctuellement des arbres adultes et pierres de construction. Cela montre que le générateur ne réserve probablement pas une zone visuellement vide autour des starts ; cela ne prouve pas que ces objets sont sans collision.

Les roseaux, épaves, cactus, arbres morts, squelettes et palmiers sont généralement plus éloignés. Leur éloignement est compatible avec leurs terrains/biomes supports et ne permet pas d’isoler une règle de clearance des starts.

## Limite hitbox

Le catalogue et les distances ne suffisent pas à déduire une hitbox. La cellule d’ancrage d’un objet peut avoir une empreinte d’occupation plus large, et le byte 9 du SAV reste inconnu ; il ne doit pas être appelé « accessibilité ». Toute réduction de la marge de sécurité du générateur doit donc être validée par une calibration contrôlée dans l’éditeur/jeu.

## Conséquence de génération

1. Garder l’ordre terrain/supports puis ressources et objets.
2. Utiliser byte 14 comme référence du décor initial ; traiter byte 7 comme état runtime.
3. Ne pas imposer le halo générique de 14 hex pour le décor visuel ; différencier au besoin petits décors, arbres et objets potentiellement bloquants, mais seulement après validation d’occupation.
4. Ne pas figer encore les profils multi-size : cette tranche est complète pour 768×768, pas pour les sept tailles natives.

Les mesures détaillées sont dans `references/native_resource_object_audit/`, notamment le rapport Markdown, le JSON, les CSV de cellules/composantes et les tableaux de proximité par start.
