"""Viewer and heatmap translation catalogues."""

VIEW_LABELS={
 'fr':{'global':'Global','territories':'Territoires','initial_territory':'Masque initial','heightmap':'Élévation','resources':'Ressources','paths':'Chemins','crops':'Cultures','heatmap':'Carte thermique'},
 'en':{'global':'Global','territories':'Territories','initial_territory':'Initial mask','heightmap':'Elevation','resources':'Resources','paths':'Paths','crops':'Crops','heatmap':'Heatmap'},
}

HEATMAP_LABELS={
 'fr':{'trees':'Arbres','building_stones':'Pierres de construction','fish':'Poissons','coal':'Charbon','iron':'Fer','gold':'Or','gems':'Gemmes','sulfur':'Soufre'},
 'en':{'trees':'Trees','building_stones':'Building Stones','fish':'Fish','coal':'Coal','iron':'Iron','gold':'Gold','gems':'Gemstones','sulfur':'Sulfur'},
}

VIEW_LABELS.update({
 'de':{'global':'Global','territories':'Territorien','initial_territory':'Anfangsmaske','heightmap':'Höhen','resources':'Ressourcen','paths':'Wege','crops':'Anbau','heatmap':'Heatmap'},
 'es':{'global':'Global','territories':'Territorios','initial_territory':'Máscara inicial','heightmap':'Elevación','resources':'Recursos','paths':'Caminos','crops':'Cultivos','heatmap':'Mapa de calor'},
})

HEATMAP_LABELS.update({
 'de':{'trees':'Bäume','building_stones':'Bausteine','fish':'Fische','coal':'Kohle','iron':'Eisen','gold':'Gold','gems':'Edelsteine','sulfur':'Schwefel'},
 'es':{'trees':'Árboles','building_stones':'Piedras de construcción','fish':'Peces','coal':'Carbón','iron':'Hierro','gold':'Oro','gems':'Gemas','sulfur':'Azufre'},
})

VALID_START_LABELS = {}
for lang, names, before, current in (
    ('fr', ('Toutes les civilisations','Romains','Égyptiens','Asiatiques','Amazones'), 'avant objets', 'carte actuelle'),
    ('en', ('All civilizations','Romans','Egyptians','Asians','Amazons'), 'before objects', 'current map'),
    ('de', ('Alle Völker','Römer','Ägypter','Asiaten','Amazonen'), 'vor Objekten', 'aktuelle Karte'),
    ('es', ('Todas las civilizaciones','Romanos','Egipcios','Asiáticos','Amazonas'), 'antes de objetos', 'mapa actual'),
):
    keys=('valid_all','valid_0','valid_1','valid_2','valid_3')
    VALID_START_LABELS[lang] = {key: name+' — '+before for key,name in zip(keys,names)}
    VALID_START_LABELS[lang].update({key+':current': name+' — '+current for key,name in zip(keys,names)})
for lang, title in zip(('fr','en','de','es'), ('Départs valides','Valid starts','Gültige Starts','Inicios válidos')):
    VIEW_LABELS[lang]['valid_starts'] = title
