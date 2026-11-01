"""Global generation presets; loading never touches the currently displayed map."""
from __future__ import annotations

from copy import deepcopy
from tkinter import filedialog, ttk
import tkinter as tk

from ...generation.custom.config import CustomGenerationConfig
from ...generation.archetypes.profiles import CONTINENTAL_CUSTOM_PROFILE_KEY
from ...generation.core import NATIVE_PLAYER_LIMITS
from ..ui.i18n.shell import ARCHETYPE_INPUT_LABELS, ARCHETYPE_LABELS, MIRROR_LABELS, MODE_LABELS
from ..ui.i18n.starts import START_LABELS
from ..ui.messages import show_message
from ..ui.theme.windows import ThemedWindow, themed_prompt
from .model import (collection_path, merge_collections, preset, read_collection,
                    validate_snapshot, write_collection)
from .text import TEXT


class ConfigurationsController:
    def _configuration_text(self):
        return TEXT.get(self.prefs.get('language', 'fr'), TEXT['en'])

    def _build_configurations_tab(self):
        self._configuration_entries = []
        self._configuration_active = None
        self._configuration_load_error = None
        self._configuration_signature = None
        self._configuration_modified = False
        self._configuration_path = collection_path()
        if self._configuration_path.exists():
            try:
                self._configuration_entries = read_collection(self._configuration_path)
            except (OSError, ValueError, TypeError, KeyError) as exc:
                self._configuration_load_error = exc
        root = self._scroll_notebook_tab('Configurations')
        root._scroll_fit_width = True
        self._configuration_root = root
        self._configuration_tab = root._scroll_host
        root.columnconfigure(0, weight=1)
        root.rowconfigure(2, weight=1)
        self._configuration_intro = ttk.Label(root, wraplength=720)
        self._configuration_intro.grid(row=0, column=0, sticky='ew', pady=(0, 10))
        actions = ttk.Frame(root)
        actions.grid(row=1, column=0, sticky='w', pady=(0, 8))
        self._configuration_buttons = {}
        for index, (key, command) in enumerate((
            ('load', self._configuration_load), ('save', self._configuration_save),
            ('rename', self._configuration_rename), ('replace', self._configuration_replace),
            ('delete', self._configuration_delete),
        )):
            button = ttk.Button(actions, command=command)
            button.grid(row=index // 3, column=index % 3, sticky='ew', padx=(0, 5), pady=3)
            self._configuration_buttons[key] = button
        body = ttk.Frame(root)
        body.grid(row=2, column=0, sticky='nsew')
        body.columnconfigure(0, weight=1)
        body.rowconfigure(0, weight=1)
        self._configuration_tree = ttk.Treeview(body, show='tree', selectmode='browse', height=5)
        self._configuration_tree.column('#0', width=220, minwidth=80)
        self._configuration_tree.grid(row=0, column=0, sticky='nsew')
        scroll = ttk.Scrollbar(body, command=self._configuration_tree.yview)
        scroll.grid(row=0, column=1, sticky='ns')
        self._configuration_tree.configure(yscrollcommand=scroll.set)
        self._configuration_tree.bind('<<TreeviewSelect>>', lambda _: self._configuration_refresh_selection())
        self._configuration_tree.bind('<Double-1>', lambda _: self._configuration_load())
        self._configuration_summary = ttk.Label(root, justify='left', wraplength=720)
        self._configuration_summary.grid(row=3, column=0, sticky='ew', pady=10)
        self._configuration_status = ttk.Label(root, wraplength=720)
        self._configuration_status.grid(row=4, column=0, sticky='ew', pady=(0, 6))
        transfer = ttk.Frame(root)
        transfer.grid(row=5, column=0, sticky='w')
        for index, (key, command) in enumerate((('import', self._configuration_import), ('export', self._configuration_export))):
            button = ttk.Button(transfer, command=command)
            button.grid(row=0, column=index, padx=(0, 5))
            self._configuration_buttons[key] = button
        root.bind('<Configure>', lambda event: self._configuration_resize(event.width), add='+')
        self.nb.bind('<<NotebookTabChanged>>', lambda _: self._configuration_refresh_selection(), add='+')
        self._configuration_refresh_language()
        self.after(500, self._configuration_poll)

    def _configuration_resize(self, width):
        for widget in (self._configuration_intro, self._configuration_summary, self._configuration_status):
            widget.configure(wraplength=max(200, width - 25))

    def _configuration_capture(self, include_seed=False):
        mode, arch = self._mode_key(), self._arch_key()
        self._custom_config_for_generation(mode, arch)  # Commit applied formula inputs.
        config = self._custom_profile_for_display()
        def slots(attribute, default):
            return (list(getattr(self, attribute, ())) + [default] * 20)[:20]
        snapshot = dict(mode=mode, archetype=arch, size=int(self.size.get()),
                        players=int(self.players.get()), mirror=self._mirror_key(),
                        starts=self._start_algorithm_key(),
                        nations=slots('classic_start_nations', 255),
                        teams=slots('player_teams', 0),
                        random_team_count=getattr(self, 'random_team_count', 2),
                        custom=config.to_dict())
        if include_seed:
            snapshot['seed'] = int(self.seed.get())
        return validate_snapshot(snapshot)

    def _configuration_apply(self, snapshot):
        data = validate_snapshot(snapshot)
        config = CustomGenerationConfig.from_dict(data['custom'])
        lang = self.prefs.get('language', 'fr')
        # Seed/player traces are deferred; establish the full source identity
        # before synchronizing so they cannot reset the loaded custom profile.
        self._custom_config = config
        self._custom_last_concrete_mode = config.base_mode
        self._custom_last_concrete_archetype = config.base_archetype
        self._custom_last_ui_mode = data['mode']
        self._custom_last_ui_archetype = data['archetype']
        self._custom_last_render_digest = None
        self.mode.set(MODE_LABELS[lang][data['mode']])
        self.arch.set(ARCHETYPE_LABELS[lang][data['archetype']])
        self.size.set(str(data['size']))
        self.players.set(data['players'])
        if 'seed' in data:
            self.seed.set(str(data['seed']))
        self.mirror.set(MIRROR_LABELS[lang][data['mirror']])
        self.classic_start_nations = tuple(data['nations'])
        self.player_teams = tuple(data['teams'])
        self.random_team_count = data['random_team_count']
        self.start_algorithm.set(data['starts'])
        self._previous_start_algorithm = data['starts']
        self.start_text.set(START_LABELS[lang][data['starts']])
        self.players_spin.configure(to=NATIVE_PLAYER_LIMITS[data['size']])
        self._selection_changed()
        self._custom_refresh_main_archetype_input()
        self._custom_schedule_archetype_preview_refresh()
        self.nb.select(self._configuration_tab)

    def _configuration_selected(self):
        selected = self._configuration_tree.selection()
        return next((item for item in self._configuration_entries if selected and item['id'] == selected[0]), None)

    def _configuration_refresh_language(self):
        if not hasattr(self, '_configuration_tab'):
            return
        texts = self._configuration_text()
        self.nb.tab(self._configuration_tab, text=texts['title'])
        self._configuration_intro.configure(text=texts['intro'])
        for key, button in self._configuration_buttons.items():
            button.configure(text=texts[key])
        self._configuration_rebuild_list()
        self._configuration_refresh_status()

    def _configuration_rebuild_list(self, selected=None):
        tree = self._configuration_tree
        selected = selected or (tree.selection() or (None,))[0]
        tree.delete(*tree.get_children())
        for item in self._configuration_entries:
            tree.insert('', 'end', iid=item['id'], text=item['name'])
        if selected and tree.exists(selected):
            tree.selection_set(selected)
            tree.see(selected)
        self._configuration_refresh_selection()

    def _configuration_refresh_selection(self):
        if not hasattr(self, '_configuration_tree'):
            return
        item = self._configuration_selected()
        texts = self._configuration_text()
        for key in ('load', 'rename', 'replace', 'delete'):
            enabled = item is not None and (key == 'load' or self._configuration_load_error is None)
            self._configuration_buttons[key].configure(state='normal' if enabled else 'disabled')
        for key in ('save', 'import'):
            self._configuration_buttons[key].configure(state='disabled' if self._configuration_load_error else 'normal')
        self._configuration_buttons['export'].configure(state='normal' if self._configuration_entries else 'disabled')
        if item is None:
            self._configuration_summary.configure(text=texts['choose'] if self._configuration_entries else texts['empty'])
            return
        data = item['configuration']
        lang = self.prefs.get('language', 'fr')
        profile_key = self._custom_archetype_profile_selection_key(data['custom']['archetype_profile'])
        source_key = {'native': 'classic', CONTINENTAL_CUSTOM_PROFILE_KEY: 'continental',
                      'large_islands': 'large_islands', 'team_islands': 'team_islands'}.get(profile_key, 'edited')
        archetype_label = ARCHETYPE_INPUT_LABELS[lang][source_key]
        nations = {'fr': ('Romain', 'Égyptien', 'Asiatique', 'Amazone'),
                   'en': ('Roman', 'Egyptian', 'Asian', 'Amazon'),
                   'de': ('Römer', 'Ägypter', 'Asiate', 'Amazone'),
                   'es': ('Romano', 'Egipcio', 'Asiático', 'Amazona')}[lang]
        players = []
        for index in range(data['players']):
            nation, team = data['nations'][index], data['teams'][index]
            players.append(f"P{index+1}: {texts['random'] if nation == 255 else nations[nation]} / {'−' if team == 0 else '?' if team == -1 else team}")
        self._configuration_summary.configure(text='\n'.join((
            item['name'],
            f"{MODE_LABELS[lang][data['mode']]} · {archetype_label} · {data['size']}×{data['size']} · {data['players']} {texts['players']}",
            f"{START_LABELS[lang][data['starts']]} · {texts['mirror']}: {MIRROR_LABELS[lang][data['mirror']]}",
            f"Seed: {data['seed']}" if 'seed' in data else texts['preserved'],
            ' · '.join(players), f"{texts['teams']}: {data['random_team_count']}",
            texts['details'],
        )))

    def _configuration_refresh_status(self):
        texts = self._configuration_text()
        item = next((item for item in self._configuration_entries if item['id'] == self._configuration_active), None)
        message = texts['loaded'].format(name=item['name']) if item else ''
        if item and self._configuration_modified:
            message += ' — ' + texts['modified']
        if self._configuration_load_error:
            message = texts['broken'] + '\n' + str(self._configuration_load_error)
        self._configuration_status.configure(text=message)

    def _configuration_poll(self):
        # Only the visible tab observes edits. Never compute terrain/contours.
        if self.nb.select() == str(self._configuration_tab):
            item = next((item for item in self._configuration_entries if item['id'] == self._configuration_active), None)
            if item:
                variables = (self.mode, self.arch, self.size, self.players, self.mirror, self.start_algorithm)
                try:
                    signature = (id(self._custom_config), *(var.get() for var in variables),
                                 tuple(getattr(self, 'classic_start_nations', ())),
                                 tuple(getattr(self, 'player_teams', ())), getattr(self, 'random_team_count', 2),
                                 self.seed.get() if 'seed' in item['configuration'] else None, item['id'])
                    if signature != self._configuration_signature:
                        self._configuration_modified = self._configuration_capture('seed' in item['configuration']) != item['configuration']
                        self._configuration_signature = signature
                except (ValueError, TypeError, tk.TclError):
                    self._configuration_modified = True
                self._configuration_refresh_status()
        self.after(500, self._configuration_poll)

    def _configuration_error(self, exc):
        show_message(self, 'ui', exception=exc, details=self._configuration_text()['error'])

    def _configuration_commit(self, entries, selected=None):
        if self._configuration_load_error:
            raise ValueError(self._configuration_text()['broken'])
        write_collection(self._configuration_path, entries)
        self._configuration_entries = entries
        self._configuration_signature = None
        self._configuration_rebuild_list(selected)
        self._configuration_refresh_status()

    def _configuration_load(self):
        item = self._configuration_selected()
        if item:
            try:
                self._configuration_apply(item['configuration'])
                self._configuration_active = item['id']
                self._configuration_modified = False
                self._configuration_signature = None
                self._configuration_refresh_status()
            except (ValueError, TypeError, KeyError, tk.TclError) as exc:
                self._configuration_error(exc)

    def _configuration_save_dialog(self, existing=None):
        texts = self._configuration_text()
        dialog = ThemedWindow(self)
        dialog.title(texts['replace'] if existing else texts['save'])
        dialog.resizable(False, False)
        name = tk.StringVar(dialog, value=existing['name'] if existing else '')
        seed = tk.BooleanVar(dialog, value=bool(existing and 'seed' in existing['configuration']))
        ttk.Label(dialog, text=texts['name']).grid(row=0, column=0, columnspan=2, sticky='w', padx=16, pady=(16, 4))
        entry = ttk.Entry(dialog, textvariable=name, width=40)
        entry.grid(row=1, column=0, columnspan=2, sticky='ew', padx=16)
        ttk.Checkbutton(dialog, text=texts['seed'], variable=seed).grid(row=2, column=0, columnspan=2, sticky='w', padx=16, pady=8)
        ttk.Label(dialog, text=texts['seed_hint'], wraplength=380).grid(row=3, column=0, columnspan=2, sticky='w', padx=16)
        error = ttk.Label(dialog, wraplength=380)
        error.grid(row=4, column=0, columnspan=2, sticky='w', padx=16)
        def accept():
            try:
                item = preset(name.get(), self._configuration_capture(seed.get()), identity=existing['id'] if existing else None)
                entries = [deepcopy(value) for value in self._configuration_entries if not existing or value['id'] != existing['id']]
                if any(value['name'].casefold() == item['name'].casefold() for value in entries):
                    raise ValueError(texts['duplicate'])
                entries.append(item)
                self._configuration_commit(entries, item['id'])
                self._configuration_active = item['id']
                self._configuration_modified = False
                self._configuration_refresh_status()
                dialog.destroy()
            except (OSError, ValueError, TypeError, KeyError) as exc:
                error.configure(text=str(exc))
        ttk.Button(dialog, text=texts['cancel'], command=dialog.destroy).grid(row=5, column=0, padx=16, pady=16)
        ttk.Button(dialog, text=texts['accept'], command=accept).grid(row=5, column=1, padx=16, pady=16)
        dialog.bind('<Return>', lambda _: accept())
        dialog.bind('<Escape>', lambda _: dialog.destroy())
        dialog.update_idletasks()
        dialog.geometry(f'+{max(0, self.winfo_rootx() + (self.winfo_width()-dialog.winfo_reqwidth())//2)}+{max(0, self.winfo_rooty() + (self.winfo_height()-dialog.winfo_reqheight())//2)}')
        dialog.grab_set()
        entry.focus_set()
        entry.selection_range(0, 'end')

    def _configuration_save(self):
        self._configuration_save_dialog()

    def _configuration_replace(self):
        item = self._configuration_selected()
        if item:
            self._configuration_save_dialog(item)

    def _configuration_rename(self):
        item = self._configuration_selected()
        if not item:
            return
        texts = self._configuration_text()
        name = themed_prompt(self, texts['rename'], texts['name'], accept=texts['accept'], cancel=texts['cancel'], initial=item['name'])
        if name is None:
            return
        try:
            replacement = preset(name, item['configuration'], identity=item['id'])
            entries = [replacement if value['id'] == item['id'] else deepcopy(value) for value in self._configuration_entries]
            if sum(value['name'].casefold() == replacement['name'].casefold() for value in entries) != 1:
                raise ValueError(texts['duplicate'])
            self._configuration_commit(entries, item['id'])
        except (OSError, ValueError, TypeError) as exc:
            self._configuration_error(exc)

    def _configuration_delete(self):
        item = self._configuration_selected()
        if not item:
            return
        texts = self._configuration_text()
        if themed_prompt(self, texts['delete'], texts['remove'].format(name=item['name']), accept=texts['delete'], cancel=texts['cancel']):
            try:
                self._configuration_commit([deepcopy(value) for value in self._configuration_entries if value['id'] != item['id']])
            except (OSError, ValueError) as exc:
                self._configuration_error(exc)

    def _configuration_import(self):
        path = filedialog.askopenfilename(parent=self, title=self._configuration_text()['import'], filetypes=[('JSON', '*.json')])
        if path:
            try:
                incoming = read_collection(path)
                self._configuration_commit(merge_collections(self._configuration_entries, incoming))
                self._configuration_status.configure(text=self._configuration_text()['merged'].format(count=len(incoming)))
            except (OSError, ValueError, TypeError, KeyError) as exc:
                self._configuration_error(exc)

    def _configuration_export(self):
        path = filedialog.asksaveasfilename(parent=self, title=self._configuration_text()['export'], defaultextension='.json', initialfile='MapGen_configurations.json', filetypes=[('JSON', '*.json')])
        if path:
            try:
                write_collection(path, self._configuration_entries)
                self._configuration_status.configure(text=self._configuration_text()['exported'])
            except (OSError, ValueError, TypeError) as exc:
                self._configuration_error(exc)
