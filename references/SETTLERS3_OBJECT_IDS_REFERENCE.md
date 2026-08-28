# Settlers III — registre des IDs d’objet

Baseline: **MapGen v1.9 DEV_3 — cartographie contrôlée 2026-08-28**.

- Domaine listé : IDs byte `0–255`.
- `Inconnu` signifie uniquement : **pas de nom validé dans notre nomenclature actuelle**.
- Les IDs 73–77 et 80–81 sont volontairement nommés seulement `Arbre adulte <ID>` : l’espèce exacte n’est pas validée.
- ID 84 est `Pousse d’arbre / Tree sapling`.
- Les IDs `208–214`, `216–222`, `224–230` et `232–255` ci-dessous sont
  confirmés par calibration visuelle contrôlée. Les IDs `215`, `223` et `231`
  ont provoqué un crash dans les cartes de test et restent hors nomenclature.
- Les IDs `82` et `83` sont la paire encore à identifier. La calibration qui les
  plaçait artificiellement est conservée comme contrôle historique, mais ne doit
  pas servir de preuve : la recherche doit porter sur les cartes et SAV déjà
  produits, hors objets volontairement injectés.
- Cette liste est destinée à être complétée au fil du reverse-engineering.

| ID | Nom FR | Nom EN | Statut |
|---:|---|---|---|
| 0 | Aucun objet | No object | Connu |
| 1 | Grosse pierre 1 | Big Stone 1 | Connu |
| 2 | Grosse pierre 2 | Big Stone 2 | Connu |
| 3 | Grosse pierre 3 | Big Stone 3 | Connu |
| 4 | Grosse pierre 4 | Big Stone 4 | Connu |
| 5 | Grosse pierre 5 | Big Stone 5 | Connu |
| 6 | Grosse pierre 6 | Big Stone 6 | Connu |
| 7 | Grosse pierre 7 | Big Stone 7 | Connu |
| 8 | Grosse pierre 8 | Big Stone 8 | Connu |
| 9 | Pierre décorative 1 | Stone 1 | Connu |
| 10 | Pierre décorative 2 | Stone 2 | Connu |
| 11 | Pierre décorative 3 | Stone 3 | Connu |
| 12 | Pierre décorative 4 | Stone 4 | Connu |
| 13 | Pierre de bordure 1 | Border Stone 1 | Connu |
| 14 | Pierre de bordure 2 | Border Stone 2 | Connu |
| 15 | Pierre de bordure 3 | Border Stone 3 | Connu |
| 16 | Pierre de bordure 4 | Border Stone 4 | Connu |
| 17 | Pierre de bordure 5 | Border Stone 5 | Connu |
| 18 | Pierre de bordure 6 | Border Stone 6 | Connu |
| 19 | Pierre de bordure 7 | Border Stone 7 | Connu |
| 20 | Pierre de bordure 8 | Border Stone 8 | Connu |
| 21 | Petite pierre 1 | Small Stone 1 | Connu |
| 22 | Petite pierre 2 | Small Stone 2 | Connu |
| 23 | Petite pierre 3 | Small Stone 3 | Connu |
| 24 | Petite pierre 4 | Small Stone 4 | Connu |
| 25 | Petite pierre 5 | Small Stone 5 | Connu |
| 26 | Petite pierre 6 | Small Stone 6 | Connu |
| 27 | Petite pierre 7 | Small Stone 7 | Connu |
| 28 | Petite pierre 8 | Small Stone 8 | Connu |
| 29 | Épave 1 | Wreck 1 | Connu |
| 30 | Épave 2 | Wreck 2 | Connu |
| 31 | Épave 3 | Wreck 3 | Connu |
| 32 | Épave 4 | Wreck 4 | Connu |
| 33 | Épave 5 | Wreck 5 | Connu |
| 34 | Tombe | Grave | Connu |
| 35 | Petite plante 1 | Small Plant 1 | Connu |
| 36 | Petite plante 2 | Small Plant 2 | Connu |
| 37 | Petite plante 3 | Small Plant 3 | Connu |
| 38 | Champignon 1 | Toadstool 1 | Connu |
| 39 | Champignon 2 | Toadstool 2 | Connu |
| 40 | Champignon 3 | Toadstool 3 | Connu |
| 41 | Souche 1 | Tree Stump 1 | Connu |
| 42 | Souche 2 | Tree Stump 2 | Connu |
| 43 | Arbre mort 1 | Dead Tree 1 | Connu |
| 44 | Arbre mort 2 | Dead Tree 2 | Connu |
| 45 | Cactus 1 | Cactus 1 | Connu |
| 46 | Cactus 2 | Cactus 2 | Connu |
| 47 | Cactus 3 | Cactus 3 | Connu |
| 48 | Cactus 4 | Cactus 4 | Connu |
| 49 | Squelette | Skeleton | Connu |
| 50 | Petite fleur 1 | Small Flower 1 | Connu |
| 51 | Petite fleur 2 | Small Flower 2 | Connu |
| 52 | Petite fleur 3 | Small Flower 3 | Connu |
| 53 | Petit buisson 1 | Small Bush 1 | Connu |
| 54 | Petit buisson 2 | Small Bush 2 | Connu |
| 55 | Petit buisson 3 | Small Bush 3 | Connu |
| 56 | Petit buisson 4 | Small Bush 4 | Connu |
| 57 | Buisson 1 | Bush 1 | Connu |
| 58 | Buisson 2 | Bush 2 | Connu |
| 59 | Buisson 3 | Bush 3 | Connu |
| 60 | Buisson 4 | Bush 4 | Connu |
| 61 | Buisson 5 | Bush 5 | Connu |
| 62 | Roseau 1 | Reed 1 | Connu |
| 63 | Roseau 2 | Reed 2 | Connu |
| 64 | Roseau 3 | Reed 3 | Connu |
| 65 | Roseau 4 | Reed 4 | Connu |
| 66 | Roseau 5 | Reed 5 | Connu |
| 67 | Roseau 6 | Reed 6 | Connu |
| 68 | Bouleau 1 | Birch 1 | Connu |
| 69 | Bouleau 2 | Birch 2 | Connu |
| 70 | Orme 1 | Elm 1 | Connu |
| 71 | Orme 2 | Elm 2 | Connu |
| 72 | Chêne | Oak | Connu |
| 73 | Arbre adulte 73 | Adult tree 73 | Famille connue, type exact à identifier |
| 74 | Arbre adulte 74 | Adult tree 74 | Famille connue, type exact à identifier |
| 75 | Arbre adulte 75 | Adult tree 75 | Famille connue, type exact à identifier |
| 76 | Arbre adulte 76 | Adult tree 76 | Famille connue, type exact à identifier |
| 77 | Arbre adulte 77 | Adult tree 77 | Famille connue, type exact à identifier |
| 78 | Palmier 1 | Palm 1 | Connu |
| 79 | Palmier 2 | Palm 2 | Connu |
| 80 | Arbre adulte 80 | Adult tree 80 | Famille connue, type exact à identifier |
| 81 | Arbre adulte 81 | Adult tree 81 | Famille connue, type exact à identifier |
| 82 | Inconnu | Inconnu | À identifier |
| 83 | Inconnu | Inconnu | À identifier |
| 84 | Pousse d’arbre | Tree sapling | Connu |
| 85 | Blé 1 | Wheat 1 | Connu |
| 86 | Blé 2 | Wheat 2 | Connu |
| 87 | Blé 3 | Wheat 3 | Connu |
| 88 | Blé 4 | Wheat 4 | Connu |
| 89 | Blé 5 | Wheat 5 | Connu |
| 90 | Blé 6 | Wheat 6 | Connu |
| 91 | Blé 7 | Wheat 7 | Connu |
| 92 | Blé 8 | Wheat 8 | Connu |
| 93 | Blé 9 | Wheat 9 | Connu |
| 94 | Vigne 1 | Vine 1 | Connu |
| 95 | Vigne 2 | Vine 2 | Connu |
| 96 | Vigne 3 | Vine 3 | Connu |
| 97 | Vigne 4 | Vine 4 | Connu |
| 98 | Vigne 5 | Vine 5 | Connu |
| 99 | Vigne 6 | Vine 6 | Connu |
| 100 | Vigne 7 | Vine 7 | Connu |
| 101 | Vigne 8 | Vine 8 | Connu |
| 102 | Vigne 9 | Vine 9 | Connu |
| 103 | Riz 1 | Rice 1 | Connu |
| 104 | Riz 2 | Rice 2 | Connu |
| 105 | Riz 3 | Rice 3 | Connu |
| 106 | Riz 4 | Rice 4 | Connu |
| 107 | Riz 5 | Rice 5 | Connu |
| 108 | Riz 6 | Rice 6 | Connu |
| 109 | Riz 7 | Rice 7 | Connu |
| 110 | Riz 8 | Rice 8 | Connu |
| 111 | Récif 1 | Reef 1 | Connu |
| 112 | Récif 2 | Reef 2 | Connu |
| 113 | Récif 3 | Reef 3 | Connu |
| 114 | Récif 4 | Reef 4 | Connu |
| 115 | Pierre de construction 1 | Building Stone 1 | Connu |
| 116 | Pierre de construction 2 | Building Stone 2 | Connu |
| 117 | Pierre de construction 3 | Building Stone 3 | Connu |
| 118 | Pierre de construction 4 | Building Stone 4 | Connu |
| 119 | Pierre de construction 5 | Building Stone 5 | Connu |
| 120 | Pierre de construction 6 | Building Stone 6 | Connu |
| 121 | Pierre de construction 7 | Building Stone 7 | Connu |
| 122 | Pierre de construction 8 | Building Stone 8 | Connu |
| 123 | Pierre de construction 9 | Building Stone 9 | Connu |
| 124 | Pierre de construction 10 | Building Stone 10 | Connu |
| 125 | Pierre de construction 11 | Building Stone 11 | Connu |
| 126 | Pierre de construction 12 | Building Stone 12 | Connu |
| 127 | Pierre de construction 13 | Building Stone 13 | Connu |
| 128 | Inconnu | Inconnu | À identifier |
| 129 | Inconnu | Inconnu | À identifier |
| 130 | Inconnu | Inconnu | À identifier |
| 131 | Inconnu | Inconnu | À identifier |
| 132 | Inconnu | Inconnu | À identifier |
| 133 | Inconnu | Inconnu | À identifier |
| 134 | Inconnu | Inconnu | À identifier |
| 135 | Inconnu | Inconnu | À identifier |
| 136 | Inconnu | Inconnu | À identifier |
| 137 | Inconnu | Inconnu | À identifier |
| 138 | Inconnu | Inconnu | À identifier |
| 139 | Inconnu | Inconnu | À identifier |
| 140 | Inconnu | Inconnu | À identifier |
| 141 | Inconnu | Inconnu | À identifier |
| 142 | Inconnu | Inconnu | À identifier |
| 143 | Inconnu | Inconnu | À identifier |
| 144 | Inconnu | Inconnu | À identifier |
| 145 | Inconnu | Inconnu | À identifier |
| 146 | Inconnu | Inconnu | À identifier |
| 147 | Inconnu | Inconnu | À identifier |
| 148 | Inconnu | Inconnu | À identifier |
| 149 | Inconnu | Inconnu | À identifier |
| 150 | Inconnu | Inconnu | À identifier |
| 151 | Inconnu | Inconnu | À identifier |
| 152 | Inconnu | Inconnu | À identifier |
| 153 | Inconnu | Inconnu | À identifier |
| 154 | Inconnu | Inconnu | À identifier |
| 155 | Inconnu | Inconnu | À identifier |
| 156 | Inconnu | Inconnu | À identifier |
| 157 | Inconnu | Inconnu | À identifier |
| 158 | Inconnu | Inconnu | À identifier |
| 159 | Inconnu | Inconnu | À identifier |
| 160 | Inconnu | Inconnu | À identifier |
| 161 | Inconnu | Inconnu | À identifier |
| 162 | Inconnu | Inconnu | À identifier |
| 163 | Inconnu | Inconnu | À identifier |
| 164 | Inconnu | Inconnu | À identifier |
| 165 | Inconnu | Inconnu | À identifier |
| 166 | Inconnu | Inconnu | À identifier |
| 167 | Inconnu | Inconnu | À identifier |
| 168 | Inconnu | Inconnu | À identifier |
| 169 | Inconnu | Inconnu | À identifier |
| 170 | Inconnu | Inconnu | À identifier |
| 171 | Inconnu | Inconnu | À identifier |
| 172 | Inconnu | Inconnu | À identifier |
| 173 | Inconnu | Inconnu | À identifier |
| 174 | Inconnu | Inconnu | À identifier |
| 175 | Inconnu | Inconnu | À identifier |
| 176 | Inconnu | Inconnu | À identifier |
| 177 | Inconnu | Inconnu | À identifier |
| 178 | Inconnu | Inconnu | À identifier |
| 179 | Inconnu | Inconnu | À identifier |
| 180 | Inconnu | Inconnu | À identifier |
| 181 | Inconnu | Inconnu | À identifier |
| 182 | Inconnu | Inconnu | À identifier |
| 183 | Inconnu | Inconnu | À identifier |
| 184 | Inconnu | Inconnu | À identifier |
| 185 | Inconnu | Inconnu | À identifier |
| 186 | Inconnu | Inconnu | À identifier |
| 187 | Inconnu | Inconnu | À identifier |
| 188 | Inconnu | Inconnu | À identifier |
| 189 | Inconnu | Inconnu | À identifier |
| 190 | Inconnu | Inconnu | À identifier |
| 191 | Inconnu | Inconnu | À identifier |
| 192 | Inconnu | Inconnu | À identifier |
| 193 | Inconnu | Inconnu | À identifier |
| 194 | Inconnu | Inconnu | À identifier |
| 195 | Inconnu | Inconnu | À identifier |
| 196 | Inconnu | Inconnu | À identifier |
| 197 | Inconnu | Inconnu | À identifier |
| 198 | Inconnu | Inconnu | À identifier |
| 199 | Inconnu | Inconnu | À identifier |
| 200 | Inconnu | Inconnu | À identifier |
| 201 | Inconnu | Inconnu | À identifier |
| 202 | Inconnu | Inconnu | À identifier |
| 203 | Inconnu | Inconnu | À identifier |
| 204 | Inconnu | Inconnu | À identifier |
| 205 | Inconnu | Inconnu | À identifier |
| 206 | Inconnu | Inconnu | À identifier |
| 207 | Inconnu | Inconnu | À identifier |
| 208 | Souche d’arbre — variante 1 | Tree stump — variant 1 | Confirmé en calibration |
| 209 | Souche d’arbre — variante 2 | Tree stump — variant 2 | Confirmé en calibration |
| 210 | Souche d’arbre — variante 3 | Tree stump — variant 3 | Confirmé en calibration |
| 211 | Souche d’arbre — variante 4 | Tree stump — variant 4 | Confirmé en calibration |
| 212 | Souche d’arbre — variante 5 | Tree stump — variant 5 | Confirmé en calibration |
| 213 | Souche d’arbre — variante 6 | Tree stump — variant 6 | Confirmé en calibration |
| 214 | Souche d’arbre — variante 7 | Tree stump — variant 7 | Confirmé en calibration |
| 215 | — | — | Crash-prone, hors nomenclature |
| 216 | Pousse d’arbre — stade 2 — variante 1 | Tree sapling — stage 2 — variant 1 | Confirmé en calibration |
| 217 | Pousse d’arbre — stade 2 — variante 2 | Tree sapling — stage 2 — variant 2 | Confirmé en calibration |
| 218 | Pousse d’arbre — stade 2 — variante 3 | Tree sapling — stage 2 — variant 3 | Confirmé en calibration |
| 219 | Pousse d’arbre — stade 2 — variante 4 | Tree sapling — stage 2 — variant 4 | Confirmé en calibration |
| 220 | Pousse d’arbre — stade 2 — variante 5 | Tree sapling — stage 2 — variant 5 | Confirmé en calibration |
| 221 | Pousse de palmier — stade 2 | Palm sapling — stage 2 | Validé en partie égyptienne |
| 222 | Pousse d’arbre — stade 2 — variante 7 | Tree sapling — stage 2 — variant 7 | Confirmé en calibration |
| 223 | — | — | Crash-prone, hors nomenclature |
| 224 | Pousse d’arbre — stade 1 — variante 1 | Tree sapling — stage 1 — variant 1 | Confirmé en calibration |
| 225 | Pousse d’arbre — stade 1 — variante 2 | Tree sapling — stage 1 — variant 2 | Confirmé en calibration |
| 226 | Pousse d’arbre — stade 1 — variante 3 | Tree sapling — stage 1 — variant 3 | Confirmé en calibration |
| 227 | Pousse d’arbre — stade 1 — variante 4 | Tree sapling — stage 1 — variant 4 | Confirmé en calibration |
| 228 | Pousse d’arbre — stade 1 — variante 5 | Tree sapling — stage 1 — variant 5 | Confirmé en calibration |
| 229 | Pousse de palmier — stade 1 | Palm sapling — stage 1 | Validé en partie égyptienne |
| 230 | Pousse d’arbre — stade 1 — variante 7 | Tree sapling — stage 1 — variant 7 | Confirmé en calibration |
| 231 | — | — | Crash-prone, hors nomenclature |
| 232 | Panneau de ressource — aucune | Resource panel — none | Confirmé en calibration |
| 233 | Panneau de ressource — charbon | Resource panel — coal | Confirmé en calibration |
| 234 | Panneau de ressource — charbon abondant | Resource panel — abundant coal | Confirmé en calibration |
| 235 | Panneau de ressource — fer | Resource panel — iron | Confirmé en calibration |
| 236 | Panneau de ressource — fer abondant | Resource panel — abundant iron | Confirmé en calibration |
| 237 | Panneau de ressource — or | Resource panel — gold | Confirmé en calibration |
| 238 | Panneau de ressource — or abondant | Resource panel — abundant gold | Confirmé en calibration |
| 239 | Panneau de ressource — gemmes | Resource panel — gemstones | Confirmé en calibration |
| 240 | Panneau de découverte de minerai 1 | Mineral discovery panel 1 | Confirmé en calibration |
| 241 | Panneau de découverte de minerai 2 | Mineral discovery panel 2 | Confirmé en calibration |
| 242 | Panneau de découverte de minerai 3 | Mineral discovery panel 3 | Confirmé en calibration |
| 243 | Arbre en feu — stade 1 | Burning tree — stage 1 | Confirmé en calibration |
| 244 | Arbre en feu — stade 2 | Burning tree — stage 2 | Confirmé en calibration |
| 245 | Arbre en feu — stade 3 | Burning tree — stage 3 | Confirmé en calibration |
| 246 | Arbre en feu — stade 4 | Burning tree — stage 4 | Confirmé en calibration |
| 247 | Nid d’abeilles — stade 1 | Bee nest — stage 1 | Confirmé en SAV |
| 248 | Nid d’abeilles — stade 2 | Bee nest — stage 2 | Confirmé en SAV |
| 249 | Nid d’abeilles — stade 3 | Bee nest — stage 3 | Confirmé en SAV |
| 250 | Nid d’abeilles — stade 4 | Bee nest — stage 4 | Confirmé en SAV |
| 251 | Nid d’abeilles — stade 5 | Bee nest — stage 5 | Confirmé en SAV |
| 252 | Nid d’abeilles — stade 6 | Bee nest — stage 6 | Confirmé en SAV |
| 253 | Nid d’abeilles — stade 7 | Bee nest — stage 7 | Confirmé en SAV |
| 254 | Borne de territoire rouge | Red territory marker | Confirmé en calibration |
| 255 | Drapeau rouge | Red flag | Confirmé en calibration |

## Preuves et limites de la passe 2026-08-28

- Les lignes `208–239` proviennent de la calibration en grille : souches après
  coupe, pousses stade 2, pousses stade 1 et panneaux de ressources. Les
  colonnes conservent le même type d'arbre ; `221` et `229` sont les deux
  pousses de palmier validées en partie égyptienne.
- `240–255` sont les visuels de calibration déjà identifiés : panneaux de
  minerai, arbre en feu, sept stades de nid, borne et drapeau rouges.
- `82` et `83` restent la paire manquante, reportée à Datamining v2. Les SAV et
  cartes réelles fournis à ce jour ne contiennent aucun de ces deux IDs ; la
  carte `S3_ObjectCalibration_256_UNKNOWN_82_83_TERRAIN28.edm` ne fait que les
  injecter volontairement et ne constitue pas une preuve d’usage.
- `215`, `223` et `231` ont fait crasher les cartes de test. Ils sont conservés
  uniquement comme trous documentaires et ne sont pas exposés comme objets
  valides dans le catalogue applicatif.
