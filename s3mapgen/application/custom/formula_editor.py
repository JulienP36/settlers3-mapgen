"""Inline formula editor: transactional commits and a bounded typing delay."""
from tkinter import ttk, StringVar, TclError
from ..ui.i18n.common import _lang_text
from ...generation.archetypes.formula import DEFAULT_FORMULA, FORMULA_EXAMPLES, NOISE_FUNCTIONS, normalize_formula
from ...generation.archetypes.noise_sources import generate_noise_source


class FormulaPanel(ttk.Frame):
    def __init__(self, parent, owner, variable, source_key, callback, language):
        super().__init__(parent)
        self.owner, self.variable, self.source_key, self.callback = owner, variable, source_key, callback
        self.language, self.pending, self.active, self.dirty = language, None, False, False
        self._committing = False
        self.columnconfigure(0, weight=1)
        ttk.Label(self, text=_lang_text(language, 'Formule', 'Formula', 'Formel', 'Fórmula')).grid(row=0, column=0, sticky='w')
        self.entry = ttk.Entry(self, textvariable=variable, width=65)
        self.entry.grid(row=1, column=0, sticky='ew')
        self.button = ttk.Button(self, text=_lang_text(language, 'Appliquer', 'Apply', 'Anwenden', 'Aplicar'), command=self.commit)
        self.button.grid(row=1, column=1, padx=(6,0))
        self.examples = StringVar(value='')
        self.combo = ttk.Combobox(self, textvariable=self.examples, values=FORMULA_EXAMPLES, state='readonly', width=65)
        self.combo.grid(row=2, column=0, sticky='ew', pady=(4,0))
        ttk.Label(self, text=_lang_text(language, 'Exemples', 'Examples', 'Beispiele', 'Ejemplos')).grid(row=2, column=1, padx=(6,0))
        self.combo.bind('<<ComboboxSelected>>', self.use_example)
        self.message = StringVar(value='')
        ttk.Label(self, textvariable=self.message, style='Hint.TLabel', wraplength=590).grid(row=3, column=0, columnspan=2, sticky='w')
        hint = _lang_text(language,
            'x/y : référence -1 à 1, avant transformations ; r : distance au centre. Bruit(fréquence, octaves, décalage seed). Résultat borné à [-1,1]. Décimales avec un point.',
            'x/y: -1 to 1; r: distance to centre. Noise(frequency, octaves, seed offset). Output clipped to [-1,1]. Use decimal points.',
            'x/y: -1 bis 1; r: Abstand zur Mitte. Rauschen(Frequenz, Oktaven, Seed-Versatz). Ausgabe auf [-1,1] begrenzt. Dezimalpunkt verwenden.',
            'x/y: -1 a 1; r: distancia al centro. Ruido(frecuencia, octavas, desplazamiento seed). Resultado limitado a [-1,1]. Usa punto decimal.')
        ttk.Label(self, text=hint, style='Hint.TLabel', wraplength=590).grid(row=4, column=0, columnspan=2, sticky='w', pady=(3,4))
        ttk.Label(self, text=', '.join(sorted(NOISE_FUNCTIONS)) + ' ; sin, cos, abs, sqrt, min, max, clamp, smoothstep', style='Hint.TLabel', wraplength=590).grid(row=5, column=0, columnspan=2, sticky='w')
        self.trace = variable.trace_add('write', lambda *_args: self.schedule())
        self.entry.bind('<Return>', self.commit)
        self.bind('<Destroy>', self.dispose, add='+')

    def set_active(self, active):
        if self.active and not active:
            self.dirty = False
            morphology = self.owner._custom_config.archetype_profile['morphology']
            saved = (morphology['relief_source_settings'] if self.source_key == 'primary'
                     else morphology['noise_layers'][int(self.source_key.split(':')[1])]['settings'])
            self.variable.set(saved.get('expression', DEFAULT_FORMULA))
        self.active = bool(active)
        if self.active:
            self.grid()
        else:
            self.cancel(); self.grid_remove()

    def cancel(self, _event=None):
        if self.pending is not None:
            try: self.after_cancel(self.pending)
            except TclError: pass
            self.pending = None

    def dispose(self, event):
        if event.widget is self:
            self.cancel()
            try: self.variable.trace_remove('write', self.trace)
            except TclError: pass

    def schedule(self, _event=None):
        if getattr(self, '_committing', False):
            return
        self.cancel()
        if self.active:
            morphology = self.owner._custom_config.archetype_profile['morphology']
            saved = (morphology['relief_source_settings'] if self.source_key == 'primary'
                     else morphology['noise_layers'][int(self.source_key.split(':')[1])]['settings'])
            if self.variable.get().strip() == saved.get('expression', DEFAULT_FORMULA):
                self.dirty = False
                self.message.set('')
                return
            self.dirty = True
            self.message.set(_lang_text(self.language, 'Modification non appliquée…', 'Change not applied…', 'Änderung noch nicht angewendet…', 'Cambio sin aplicar…'))
            self.pending = self.after(750, self.commit)

    def use_example(self, _event=None):
        self.dirty = True
        self.variable.set(self.examples.get()); self.commit()

    def commit(self, _event=None):
        self.cancel()
        if not self.active: return
        try:
            expression = normalize_formula(self.variable.get())
            profile = self.owner._custom_config.archetype_profile['morphology']
            settings = dict(profile['relief_source_settings'] if self.source_key == 'primary'
                            else profile['noise_layers'][int(self.source_key.split(':')[1])]['settings'])
            settings['expression'] = expression
            # Check the actual target resolution before replacing the last valid profile.
            side = min(768, max(64, int(self.owner.size.get())))
            generate_noise_source('formula', side, int(self.owner.seed.get()), settings)
            self._committing = True
            self.variable.set(expression)
            self.callback()
            current = self.owner._custom_config.archetype_profile['morphology']
            applied = (current['relief_source_settings'] if self.source_key == 'primary'
                       else current['noise_layers'][int(self.source_key.split(':')[1])]['settings'])
            if applied.get('expression', DEFAULT_FORMULA) != expression:
                raise ValueError(_lang_text(self.language, 'Vérifiez les autres paramètres de la source.', 'Check the other source parameters.', 'Andere Quellenparameter prüfen.', 'Comprueba los demás parámetros de la fuente.'))
            self.dirty = False
            self.message.set(_lang_text(self.language, 'Formule appliquée.', 'Formula applied.', 'Formel angewendet.', 'Fórmula aplicada.'))
        except (ValueError, TypeError, KeyError) as exc:
            self.message.set(_lang_text(self.language, f'Formule non appliquée : {exc}', f'Formula not applied: {exc}', f'Formel nicht angewendet: {exc}', f'Fórmula sin aplicar: {exc}'))
        finally:
            self._committing = False
        return 'break'


def ensure_applied_formula_inputs(owner, config):
    """Never generate the previous valid expression while a visible edit is pending."""
    morphology = config.archetype_profile['morphology']
    entries = []
    if morphology.get('relief_source') == 'formula':
        entries.append(('primary', getattr(owner, '_custom_archetype_relief_source_vars', {}), morphology['relief_source_settings']))
    for index, layer in enumerate(morphology['noise_layers'][:morphology['noise_layer_count']]):
        if layer['enabled'] and layer['strength_percent'] > 0 and layer['source'] == 'formula':
            entries.append((f'layer:{index}', getattr(owner, '_custom_archetype_noise_layer_vars', {}).get(index, {}), layer['settings']))
    for key, variables, settings in entries:
        panel = getattr(owner, '_custom_formula_panels', {}).get(key)
        if panel is None or not panel.active or not panel.dirty:
            continue
        variable = variables.get('expression')
        if variable is not None and variable.get().strip() != settings.get('expression', DEFAULT_FORMULA):
            raise ValueError(_lang_text(owner._custom_language(),
                'Une formule modifiée n’est pas appliquée : corrigez-la puis cliquez sur Appliquer.',
                'A changed formula has not been applied: correct it and click Apply.',
                'Eine geänderte Formel wurde nicht angewendet: korrigieren und Anwenden wählen.',
                'Una fórmula modificada no se ha aplicado: corrígela y pulsa Aplicar.'))
