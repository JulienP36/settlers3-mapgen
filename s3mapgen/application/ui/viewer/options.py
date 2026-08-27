"""Stable viewer option order and deterministic selector colors."""

VIEW_CHOICES = {
    "Global": "global",
    "Départs": "starts",
    "Territoires": "territories",
    "Élévation": "heightmap",
    "Ressources": "resources",
    "Chemins": "paths",
    "Cultures": "crops",
    "Carte thermique": "heatmap",
}

VIEW_ICON_COLORS={
 'global':'#2698e8','starts':'#cd1e10','heightmap':'#8f55d6','resources':'#ff9418','territories':'#31a354',
 'paths':'#9a6438','crops':'#e4c83d','heatmap':'#d83737',
}

HEATMAP_ICON_COLORS={
 'trees':'#2b9a4a','building_stones':'#dedede','fish':'#278fd4','coal':'#101010',
 'iron':'#ff9400','gold':'#ffff00','gems':'#ce0000','sulfur':'#c4b25c',
}
