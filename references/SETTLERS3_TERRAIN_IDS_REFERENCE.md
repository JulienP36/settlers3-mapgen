# Settlers III — registre des IDs de terrain

Baseline: **MapGen v1.7 STABLE**.

Les IDs **18** et **19** sont validés comme détails d’herbe : ils apparaissent
uniquement sous forme de blobs d’une cellule, entourés exclusivement d’herbe
ordinaire (ID 16). Ils appartiennent donc à la famille `Herbe`; leur distinction
1/2 reste uniquement visuelle.

- Domaine listé : IDs byte `0–255`.
- `Inconnu` signifie uniquement : **pas de nom validé dans notre nomenclature actuelle**.
- Cette liste est volontairement conservative : aucune sémantique n’est inventée.
- Elle est destinée à être complétée au fil du reverse-engineering.

| ID | Nom FR | Nom EN | Statut |
|---:|---|---|---|
| 0 | Eau 1 | Water 1 | Connu |
| 1 | Eau 2 | Water 2 | Connu |
| 2 | Eau 3 | Water 3 | Connu |
| 3 | Eau 4 | Water 4 | Connu |
| 4 | Eau 5 | Water 5 | Connu |
| 5 | Eau 6 | Water 6 | Connu |
| 6 | Eau 7 | Water 7 | Connu |
| 7 | Eau 8 | Water 8 | Connu |
| 8 | Inconnu | Inconnu | À identifier |
| 9 | Inconnu | Inconnu | À identifier |
| 10 | Inconnu | Inconnu | À identifier |
| 11 | Inconnu | Inconnu | À identifier |
| 12 | Inconnu | Inconnu | À identifier |
| 13 | Inconnu | Inconnu | À identifier |
| 14 | Inconnu | Inconnu | À identifier |
| 15 | Inconnu | Inconnu | À identifier |
| 16 | Herbe | Grass | Connu |
| 17 | Transition roche 1 | Rock transition 1 | Connu |
| 18 | Détail herbe 1 | Grass detail 1 | Confirmé — blob singleton entouré d’herbe |
| 19 | Détail herbe 2 | Grass detail 2 | Confirmé — blob singleton entouré d’herbe |
| 20 | Transition herbe/désert | Grass/desert transition | Connu |
| 21 | Transition herbe/marais | Grass/swamp transition | Connu |
| 22 | Agriculture runtime | Runtime agriculture | Connu |
| 23 | Boue | Mud | Connu |
| 24 | Herbe sèche | Dry grass | Connu |
| 25 | Inconnu | Inconnu | À identifier |
| 26 | Inconnu | Inconnu | À identifier |
| 27 | Inconnu | Inconnu | À identifier |
| 28 | Chemin runtime | Runtime path | Connu |
| 29 | Inconnu | Inconnu | À identifier |
| 30 | Inconnu | Inconnu | À identifier |
| 31 | Inconnu | Inconnu | À identifier |
| 32 | Roche | Rocky | Connu |
| 33 | Transition roche 2 | Rock transition 2 | Connu |
| 34 | Patch d’herbe rocheuse | Rocky grass patch | Confirmé — petit patch d’herbe dans la roche |
| 35 | Transition roche/neige | Rock/snow transition | Connu |
| 36 | Inconnu | Inconnu | À identifier |
| 37 | Inconnu | Inconnu | À identifier |
| 38 | Inconnu | Inconnu | À identifier |
| 39 | Inconnu | Inconnu | À identifier |
| 40 | Inconnu | Inconnu | À identifier |
| 41 | Inconnu | Inconnu | À identifier |
| 42 | Inconnu | Inconnu | À identifier |
| 43 | Inconnu | Inconnu | À identifier |
| 44 | Inconnu | Inconnu | À identifier |
| 45 | Inconnu | Inconnu | À identifier |
| 46 | Inconnu | Inconnu | À identifier |
| 47 | Inconnu | Inconnu | À identifier |
| 48 | Rivage | Shore | Connu |
| 49 | Inconnu | Inconnu | À identifier |
| 50 | Inconnu | Inconnu | À identifier |
| 51 | Inconnu | Inconnu | À identifier |
| 52 | Inconnu | Inconnu | À identifier |
| 53 | Inconnu | Inconnu | À identifier |
| 54 | Inconnu | Inconnu | À identifier |
| 55 | Inconnu | Inconnu | À identifier |
| 56 | Inconnu | Inconnu | À identifier |
| 57 | Inconnu | Inconnu | À identifier |
| 58 | Inconnu | Inconnu | À identifier |
| 59 | Inconnu | Inconnu | À identifier |
| 60 | Inconnu | Inconnu | À identifier |
| 61 | Inconnu | Inconnu | À identifier |
| 62 | Inconnu | Inconnu | À identifier |
| 63 | Inconnu | Inconnu | À identifier |
| 64 | Désert | Desert | Connu |
| 65 | Transition désert | Desert transition | Connu |
| 66 | Inconnu | Inconnu | À identifier |
| 67 | Inconnu | Inconnu | À identifier |
| 68 | Inconnu | Inconnu | À identifier |
| 69 | Inconnu | Inconnu | À identifier |
| 70 | Inconnu | Inconnu | À identifier |
| 71 | Inconnu | Inconnu | À identifier |
| 72 | Inconnu | Inconnu | À identifier |
| 73 | Inconnu | Inconnu | À identifier |
| 74 | Inconnu | Inconnu | À identifier |
| 75 | Inconnu | Inconnu | À identifier |
| 76 | Inconnu | Inconnu | À identifier |
| 77 | Inconnu | Inconnu | À identifier |
| 78 | Inconnu | Inconnu | À identifier |
| 79 | Inconnu | Inconnu | À identifier |
| 80 | Marais | Swamp | Connu |
| 81 | Transition marais | Swamp transition | Connu |
| 82 | Inconnu | Inconnu | À identifier |
| 83 | Inconnu | Inconnu | À identifier |
| 84 | Inconnu | Inconnu | À identifier |
| 85 | Inconnu | Inconnu | À identifier |
| 86 | Inconnu | Inconnu | À identifier |
| 87 | Inconnu | Inconnu | À identifier |
| 88 | Inconnu | Inconnu | À identifier |
| 89 | Inconnu | Inconnu | À identifier |
| 90 | Inconnu | Inconnu | À identifier |
| 91 | Inconnu | Inconnu | À identifier |
| 92 | Inconnu | Inconnu | À identifier |
| 93 | Inconnu | Inconnu | À identifier |
| 94 | Inconnu | Inconnu | À identifier |
| 95 | Inconnu | Inconnu | À identifier |
| 96 | Rivière 1 | River 1 | Connu |
| 97 | Rivière 2 | River 2 | Connu |
| 98 | Rivière 3 | River 3 | Connu |
| 99 | Rivière 4 | River 4 | Connu |
| 100 | Inconnu | Inconnu | À identifier |
| 101 | Inconnu | Inconnu | À identifier |
| 102 | Inconnu | Inconnu | À identifier |
| 103 | Inconnu | Inconnu | À identifier |
| 104 | Inconnu | Inconnu | À identifier |
| 105 | Inconnu | Inconnu | À identifier |
| 106 | Inconnu | Inconnu | À identifier |
| 107 | Inconnu | Inconnu | À identifier |
| 108 | Inconnu | Inconnu | À identifier |
| 109 | Inconnu | Inconnu | À identifier |
| 110 | Inconnu | Inconnu | À identifier |
| 111 | Inconnu | Inconnu | À identifier |
| 112 | Inconnu | Inconnu | À identifier |
| 113 | Inconnu | Inconnu | À identifier |
| 114 | Inconnu | Inconnu | À identifier |
| 115 | Inconnu | Inconnu | À identifier |
| 116 | Inconnu | Inconnu | À identifier |
| 117 | Inconnu | Inconnu | À identifier |
| 118 | Inconnu | Inconnu | À identifier |
| 119 | Inconnu | Inconnu | À identifier |
| 120 | Inconnu | Inconnu | À identifier |
| 121 | Inconnu | Inconnu | À identifier |
| 122 | Inconnu | Inconnu | À identifier |
| 123 | Inconnu | Inconnu | À identifier |
| 124 | Inconnu | Inconnu | À identifier |
| 125 | Inconnu | Inconnu | À identifier |
| 126 | Inconnu | Inconnu | À identifier |
| 127 | Inconnu | Inconnu | À identifier |
| 128 | Neige | Snow | Connu |
| 129 | Transition neige | Snow transition | Connu |
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
| 144 | Boue / transition 144 | Mud / transition 144 | Connu |
| 145 | Boue / transition 145 | Mud / transition 145 | Connu |
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
| 208 | Inconnu | Inconnu | À identifier |
| 209 | Inconnu | Inconnu | À identifier |
| 210 | Inconnu | Inconnu | À identifier |
| 211 | Inconnu | Inconnu | À identifier |
| 212 | Inconnu | Inconnu | À identifier |
| 213 | Inconnu | Inconnu | À identifier |
| 214 | Inconnu | Inconnu | À identifier |
| 215 | Inconnu | Inconnu | À identifier |
| 216 | Inconnu | Inconnu | À identifier |
| 217 | Inconnu | Inconnu | À identifier |
| 218 | Inconnu | Inconnu | À identifier |
| 219 | Inconnu | Inconnu | À identifier |
| 220 | Inconnu | Inconnu | À identifier |
| 221 | Inconnu | Inconnu | À identifier |
| 222 | Inconnu | Inconnu | À identifier |
| 223 | Inconnu | Inconnu | À identifier |
| 224 | Inconnu | Inconnu | À identifier |
| 225 | Inconnu | Inconnu | À identifier |
| 226 | Inconnu | Inconnu | À identifier |
| 227 | Inconnu | Inconnu | À identifier |
| 228 | Inconnu | Inconnu | À identifier |
| 229 | Inconnu | Inconnu | À identifier |
| 230 | Inconnu | Inconnu | À identifier |
| 231 | Inconnu | Inconnu | À identifier |
| 232 | Inconnu | Inconnu | À identifier |
| 233 | Inconnu | Inconnu | À identifier |
| 234 | Inconnu | Inconnu | À identifier |
| 235 | Inconnu | Inconnu | À identifier |
| 236 | Inconnu | Inconnu | À identifier |
| 237 | Inconnu | Inconnu | À identifier |
| 238 | Inconnu | Inconnu | À identifier |
| 239 | Inconnu | Inconnu | À identifier |
| 240 | Inconnu | Inconnu | À identifier |
| 241 | Inconnu | Inconnu | À identifier |
| 242 | Inconnu | Inconnu | À identifier |
| 243 | Inconnu | Inconnu | À identifier |
| 244 | Inconnu | Inconnu | À identifier |
| 245 | Inconnu | Inconnu | À identifier |
| 246 | Inconnu | Inconnu | À identifier |
| 247 | Inconnu | Inconnu | À identifier |
| 248 | Inconnu | Inconnu | À identifier |
| 249 | Inconnu | Inconnu | À identifier |
| 250 | Inconnu | Inconnu | À identifier |
| 251 | Inconnu | Inconnu | À identifier |
| 252 | Inconnu | Inconnu | À identifier |
| 253 | Inconnu | Inconnu | À identifier |
| 254 | Inconnu | Inconnu | À identifier |
| 255 | Inconnu | Inconnu | À identifier |
