"""Explicit nation inputs for the game's Classic departure solver."""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk, font as tkfont

from ..ui.theme.windows import ThemedWindow
from ..rendering.preview import PLAYER_COLORS
from ..ui.widgets.selectors import ColorMenuSelect
from ..ui.sprites import NATION_SPRITES

NATION_CHOICES = (0,1,2,3,255)

TEXT = {
    'fr': ('Joueurs — civilisations et équipes', 'Civilisations et équipes utilisées avec tous les algorithmes de départs.',
           ('Romains','Égyptiens','Asiatiques','Amazones','Choisir'), 'Joueur', 'Appliquer', 'Annuler',
           '{count} joueurs actifs · noms barrés : slots inutilisés', 'Civilisation', 'Équipe', '− : aucune équipe'),
    'en': ('Players — civilizations and teams', 'Civilizations and teams apply to all departure algorithms.',
           ('Romans','Egyptians','Asians','Amazons','Choose'), 'Player', 'Apply', 'Cancel',
           '{count} active players · crossed-out names: unused slots', 'Civilization', 'Team', '−: no team'),
    'de': ('Spieler — Völker und Teams', 'Völker und Teams gelten für alle Startalgorithmen.',
           ('Römer','Ägypter','Asiaten','Amazonen','Freie Auswahl'), 'Spieler', 'Übernehmen', 'Abbrechen',
           '{count} aktive Spieler · durchgestrichene Namen: ungenutzte Plätze', 'Volk', 'Team', '−: kein Team'),
    'es': ('Jugadores — civilizaciones y equipos', 'Civilizaciones y equipos utilizados con todos los algoritmos de inicio.',
           ('Romanos','Egipcios','Asiáticos','Amazonas','Elegir'), 'Jugador', 'Aplicar', 'Cancelar',
           '{count} jugadores activos · nombres tachados: espacios sin usar', 'Civilización', 'Equipo', '−: sin equipo'),
}


def choose_classic_nations(parent, nations, players, language='fr', *, teams=()):
    title, explanation, labels, player, apply, cancel, legend, civilization, team_label, team_hint = TEXT.get(language,TEXT['fr'])
    win = ThemedWindow(parent)
    win.withdraw()
    win.title(title)
    win.resizable(False,False)
    body = ttk.Frame(win,padding=16)
    body.pack(fill='both',expand=True)
    ttk.Label(body,text=explanation,wraplength=640).grid(row=0,column=0,columnspan=2,sticky='w',pady=(0,6))
    ttk.Label(body,text=legend.format(count=players)+' · '+team_hint,wraplength=640).grid(row=1,column=0,columnspan=2,sticky='w',pady=(0,12))
    win._inactive_font = tkfont.Font(win,font='TkDefaultFont')
    win._inactive_font.configure(overstrike=True)
    values, team_values = [], []
    win._player_swatches = []
    nation_width = max(11,max(map(len,labels)))
    tables = []
    for column in range(2):
        table = ttk.Frame(body,padding=(0,0,16 if column==0 else 0,0))
        table.grid(row=2,column=column,sticky='n')
        for col,heading in enumerate((player,civilization,team_label)):
            ttk.Label(table,text=heading).grid(row=0,column=col,sticky='w',padx=(0,8),pady=(0,6))
        tables.append(table)
    for i in range(20):
        table = tables[i//10]
        row = 1+(i%10)*2
        enabled = i < players
        if i == players:
            ttk.Separator(table,orient='horizontal').grid(row=row,column=0,columnspan=3,sticky='ew',pady=(3,5))
        options = {} if enabled else {'font':win._inactive_font}
        identity = ttk.Frame(table)
        identity.grid(row=row+1,column=0,sticky='w',padx=(0,8),pady=3)
        swatch = tk.PhotoImage(master=win,width=10,height=10)
        swatch.put('#%02x%02x%02x' % PLAYER_COLORS[i],to=(0,0,10,10))
        win._player_swatches.append(swatch)
        ttk.Label(identity,image=swatch).pack(side='left',padx=(0,4))
        ttk.Label(identity,text=f'{player} {i+1}',**options).pack(side='left')
        nation = nations[i] if i<len(nations) else 0
        variable = tk.StringVar(win,value=labels[NATION_CHOICES.index(nation)])
        selector = ColorMenuSelect(table, variable, width=nation_width)
        selector.set_items([(n, label, '#40e080',
            'sprite:'+NATION_SPRITES[n] if n in NATION_SPRITES else 'sprite:views/valid_starts')
            for n, label in zip(NATION_CHOICES, labels)])
        selector.set_enabled(enabled)
        selector.grid(row=row+1,column=1,sticky='ew',padx=(0,8),pady=3)
        win.theme_widget(selector.menu, background='field', foreground='text',
                         activebackground='panel', activeforeground='text', disabledforeground='disabled')
        values.append(variable)
        team = teams[i] if i < len(teams) else 0
        team_variable = tk.StringVar(win,value="−" if team == 0 else str(team))
        ttk.Combobox(table,values=("−", *map(str,range(1,21))),textvariable=team_variable,
                     state='readonly' if enabled else 'disabled',width=3).grid(row=row+1,column=2,sticky='w',pady=3)
        team_values.append(team_variable)
    result = None
    previous_grab = parent.grab_current()
    def finish(confirmed=False):
        nonlocal result
        if confirmed:
            result = (tuple(NATION_CHOICES[labels.index(v.get())] for v in values),
                      tuple(0 if v.get() == "−" else int(v.get()) for v in team_values))
        win.destroy()
        if previous_grab is not None and previous_grab.winfo_exists():
            previous_grab.grab_set()
            previous_grab.focus_set()
    buttons = ttk.Frame(body)
    buttons.grid(row=3,column=0,columnspan=2,sticky='e',pady=(8,0))
    ttk.Button(buttons,text=cancel,command=finish).pack(side='left',padx=(0,8))
    primary = ttk.Button(buttons,text=apply,style='Primary.TButton',command=lambda:finish(True))
    primary.pack(side='left')
    win.bind('<Escape>',lambda event:finish())
    win.bind('<Return>',lambda event:finish(True))
    win.protocol('WM_DELETE_WINDOW',finish)
    win.update_idletasks()
    owner = parent.winfo_toplevel()
    width,height = win.winfo_reqwidth(),win.winfo_reqheight()
    left = owner.winfo_rootx()+(owner.winfo_width()-width)//2
    top = owner.winfo_rooty()+(owner.winfo_height()-height)//2
    win.geometry(f'+{max(0,min(left,win.winfo_screenwidth()-width))}+{max(0,min(top,win.winfo_screenheight()-height))}')
    win.deiconify()
    win.wait_visibility()
    win.grab_set()
    primary.focus_set()
    parent.wait_window(win)
    return result
