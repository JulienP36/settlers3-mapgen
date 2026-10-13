"""Departure menu labels; keys remain stable across languages."""

START_LABELS = {'fr': {'auto': 'Automatique',
        'balanced': 'Éloignement',
        'fair': 'Équilibré',
        'islands': 'Îles',
        'classic': 'Classique'},
 'en': {'auto': 'Automatic',
        'balanced': 'Distance',
        'fair': 'Balanced',
        'islands': 'Islands',
        'classic': 'Classic'},
 'de': {'auto': 'Automatisch',
        'balanced': 'Abstand',
        'fair': 'Ausgeglichen',
        'islands': 'Inseln',
        'classic': 'Klassisch'},
 'es': {'auto': 'Automático',
        'balanced': 'Distancia',
        'fair': 'Equilibrado',
        'islands': 'Islas',
        'classic': 'Clásico'}}

for language,label in dict(fr="Joueurs…",en="Players…",de="Spieler…",es="Jugadores…").items():
    START_LABELS[language]["nations"] = label

# Keep saved/legacy batch labels readable after the solo-specific caption
# becomes the shared individual/team island caption. Internal IDs never change.
START_LABEL_ALIASES = {
    'Îles — seul': 'islands', 'Islands — solo': 'islands',
    'Inseln — einzeln': 'islands', 'Islas — individual': 'islands',
}

START_TOOLTIPS = {
    'fr': {
        'auto': "Choisit le placement selon la géographie : Éloignement sur continent, Îles sur une géographie insulaire reconnue.",
        'balanced': "Privilégie l'espacement entre joueurs sur continent. Sur une géographie insulaire reconnue, utilise le placement Îles.",
        'fair': "Compare l'accès terrestre aux minerais proches, en favorisant des départs espacés. Ne garantit pas un joueur par île ; incompatible avec Îles par équipe.",
        'islands': "Place un joueur par île individuelle ou regroupe les alliés par île d'équipe. Privilégie les zones dégagées, et l'accès aux montagnes/rivières par équipe. Nécessite des îles reconnues.",
        'classic': "Utilise la sélection native du jeu selon les civilisations choisies. Ne garantit ni répartition par île ni validité dans l'éditeur ; incompatible avec Îles par équipe.",
        'nations': "Règle les civilisations et les équipes des joueurs. Ces réglages sont partagés par les algorithmes de départ.",
    },
    'en': {
        'auto': "Chooses by geography: Distance on a continent, Islands on recognized island geography.",
        'balanced': "Favors player spacing on a continent. On recognized island geography, uses Islands placement.",
        'fair': "Compares land access to nearby ore while favoring spaced starts. Does not guarantee one player per island; unavailable for Islands by team.",
        'islands': "Places one player per individual island or groups allies on team islands. Favors clear ground; on team islands, favors mountain/river access. Requires recognized islands.",
        'classic': "Uses the game's native selection for the chosen civilizations. Guarantees neither island distribution nor editor validity; unavailable for Islands by team.",
        'nations': "Sets player civilizations and teams. These settings are shared by the start algorithms.",
    },
    'de': {
        'auto': "Wählt nach Geografie: Abstand auf einem Kontinent, Inseln bei erkannter Inselgeografie.",
        'balanced': "Bevorzugt Abstand zwischen Spielern auf einem Kontinent. Bei erkannter Inselgeografie wird die Inselplatzierung verwendet.",
        'fair': "Vergleicht den Landzugang zu nahen Erzen und bevorzugt entfernte Startpunkte. Garantiert keinen Spieler pro Insel; nicht für Inseln nach Team verfügbar.",
        'islands': "Ein Spieler pro Einzelinsel oder Verbündete auf Teaminseln. Bevorzugt freie Flächen, auf Teaminseln den Zugang zu Bergen und Flüssen. Erfordert erkannte Inseln.",
        'classic': "Verwendet die native Spielauswahl für die gewählten Zivilisationen. Garantiert weder Inselverteilung noch Editor-Gültigkeit; nicht für Inseln nach Team verfügbar.",
        'nations': "Legt Zivilisationen und Teams der Spieler fest. Diese Einstellungen gelten für alle Startalgorithmen.",
    },
    'es': {
        'auto': "Elige según la geografía: Distancia en un continente, Islas en una geografía insular reconocida.",
        'balanced': "Prioriza la separación entre jugadores en un continente. En una geografía insular reconocida utiliza la colocación Islas.",
        'fair': "Compara el acceso terrestre a minerales cercanos y favorece inicios separados. No garantiza un jugador por isla; no disponible para Islas por equipo.",
        'islands': "Un jugador por isla individual o aliados agrupados en islas de equipo. Prioriza terreno libre y, en islas de equipo, acceso a montañas y ríos. Requiere islas reconocidas.",
        'classic': "Usa la selección nativa del juego según las civilizaciones elegidas. No garantiza reparto por islas ni validez en el editor; no disponible para Islas por equipo.",
        'nations': "Configura las civilizaciones y los equipos. Estos ajustes se comparten entre los algoritmos de inicio.",
    },
}
