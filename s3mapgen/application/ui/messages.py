"""Readable, copyable application messages, grouped in one themed window."""
from __future__ import annotations

from dataclasses import dataclass
import tkinter as tk
from tkinter import ttk
import traceback
import struct

from ...version import APP_VERSION
from .theme.windows import ThemedWindow


TEXT = {
    'fr': {
        'error': 'Erreur', 'warning': 'Attention', 'info': 'Information',
        'generation': 'La génération de la carte a échoué.',
        'starts': 'Le placement des joueurs a échoué. La génération n’a pas été finalisée.',
        'import': 'Le fichier n’a pas pu être importé.',
        'invalid_file': 'La structure du fichier est invalide ou incomplète.',
        'file_action': 'Vérifiez le format du fichier et qu’il est complet.',
        'preview': 'La préparation de l’affichage ou de l’aperçu a échoué.',
        'preview_export': 'L’aperçu PNG n’a pas pu être enregistré.',
        'map_export': 'L’export de la carte n’a pas abouti.',
        'stats_export': 'L’export des statistiques n’a pas abouti.',
        'batch': 'Une carte du lot n’a pas pu être générée.',
        'ui': 'Une action de l’interface a rencontré une erreur.',
        'permission': 'Vérifiez les autorisations d’accès au fichier ou au dossier indiqué.',
        'missing': 'Vérifiez que le fichier ou le dossier indiqué existe encore.',
        'input': 'Vérifiez les paramètres indiqués dans le message.',
        'details': 'Afficher les détails techniques', 'hide': 'Masquer les détails techniques',
        'copy': 'Copier le message', 'copy_all': 'Copier tous les messages',
        'copied': 'Message copié.', 'copy_failed': 'Copie impossible : sélectionnez le texte dans les détails.',
        'close': 'Fermer', 'occurrences': 'Occurrences', 'cause': 'Cause',
        'context': 'Contexte', 'action': 'Action possible', 'operation': 'Opération',
    },
    'en': {
        'error': 'Error', 'warning': 'Warning', 'info': 'Information',
        'generation': 'Map generation failed.',
        'starts': 'Player placement failed. Generation was not completed.',
        'import': 'The file could not be imported.',
        'invalid_file': 'The file structure is invalid or incomplete.',
        'file_action': 'Check the file format and that the file is complete.',
        'preview': 'Preparing the display or preview failed.',
        'preview_export': 'The PNG preview could not be saved.',
        'map_export': 'The map could not be exported.',
        'stats_export': 'The statistics could not be exported.',
        'batch': 'A map in the batch could not be generated.',
        'ui': 'An interface action encountered an error.',
        'permission': 'Check access permissions for the indicated file or folder.',
        'missing': 'Check that the indicated file or folder still exists.',
        'input': 'Check the parameters indicated in the message.',
        'details': 'Show technical details', 'hide': 'Hide technical details',
        'copy': 'Copy message', 'copy_all': 'Copy all messages',
        'copied': 'Message copied.', 'copy_failed': 'Copy failed: select the text in the details.',
        'close': 'Close', 'occurrences': 'Occurrences', 'cause': 'Cause',
        'context': 'Context', 'action': 'Possible action', 'operation': 'Operation',
    },
    'de': {
        'error': 'Fehler', 'warning': 'Achtung', 'info': 'Information',
        'generation': 'Die Kartengenerierung ist fehlgeschlagen.',
        'starts': 'Die Spielerplatzierung ist fehlgeschlagen. Die Generierung wurde nicht abgeschlossen.',
        'import': 'Die Datei konnte nicht importiert werden.',
        'invalid_file': 'Die Dateistruktur ist ungültig oder unvollständig.',
        'file_action': 'Prüfen Sie das Dateiformat und die Vollständigkeit der Datei.',
        'preview': 'Die Vorbereitung der Anzeige oder Vorschau ist fehlgeschlagen.',
        'preview_export': 'Die PNG-Vorschau konnte nicht gespeichert werden.',
        'map_export': 'Die Karte konnte nicht exportiert werden.',
        'stats_export': 'Die Statistiken konnten nicht exportiert werden.',
        'batch': 'Eine Karte des Stapels konnte nicht generiert werden.',
        'ui': 'Bei einer Aktion der Oberfläche ist ein Fehler aufgetreten.',
        'permission': 'Prüfen Sie die Zugriffsrechte für die angegebene Datei oder den Ordner.',
        'missing': 'Prüfen Sie, ob die angegebene Datei oder der Ordner noch existiert.',
        'input': 'Prüfen Sie die im Bericht angegebenen Parameter.',
        'details': 'Technische Details anzeigen', 'hide': 'Technische Details ausblenden',
        'copy': 'Meldung kopieren', 'copy_all': 'Alle Meldungen kopieren',
        'copied': 'Meldung kopiert.', 'copy_failed': 'Kopieren fehlgeschlagen: Text in den Details auswählen.',
        'close': 'Schließen', 'occurrences': 'Vorkommen', 'cause': 'Ursache',
        'context': 'Kontext', 'action': 'Mögliche Aktion', 'operation': 'Vorgang',
    },
    'es': {
        'error': 'Error', 'warning': 'Aviso', 'info': 'Información',
        'generation': 'La generación del mapa ha fallado.',
        'starts': 'La colocación de jugadores ha fallado. La generación no se ha completado.',
        'import': 'No se ha podido importar el archivo.',
        'invalid_file': 'La estructura del archivo es inválida o incompleta.',
        'file_action': 'Compruebe el formato y que el archivo esté completo.',
        'preview': 'La preparación de la visualización o vista previa ha fallado.',
        'preview_export': 'No se ha podido guardar la vista previa PNG.',
        'map_export': 'No se ha podido exportar el mapa.',
        'stats_export': 'No se han podido exportar las estadísticas.',
        'batch': 'No se ha podido generar un mapa del lote.',
        'ui': 'Una acción de la interfaz ha encontrado un error.',
        'permission': 'Compruebe los permisos de acceso al archivo o carpeta indicado.',
        'missing': 'Compruebe que el archivo o carpeta indicado todavía existe.',
        'input': 'Compruebe los parámetros indicados en el mensaje.',
        'details': 'Mostrar detalles técnicos', 'hide': 'Ocultar detalles técnicos',
        'copy': 'Copiar mensaje', 'copy_all': 'Copiar todos los mensajes',
        'copied': 'Mensaje copiado.', 'copy_failed': 'No se puede copiar: seleccione el texto en los detalles.',
        'close': 'Cerrar', 'occurrences': 'Apariciones', 'cause': 'Causa',
        'context': 'Contexto', 'action': 'Acción posible', 'operation': 'Operación',
    },
}


@dataclass(frozen=True)
class MessageReport:
    title: str
    message: str
    cause: str
    action: str
    operation: str
    context: tuple[tuple[str, str], ...]
    details: str
    language: str
    severity: str

    def copy_text(self, occurrences=1):
        labels = TEXT[self.language]
        parts = [f'Settlers III MapGen {APP_VERSION}', self.title, self.message,
                 f"{labels['operation']}: {self.operation}"]
        if self.cause:
            parts.append(f"{labels['cause']}: {self.cause}")
        if self.action:
            parts.append(f"{labels['action']}: {self.action}")
        if self.context:
            parts.append(labels['context'] + ':\n' + '\n'.join(f'{k}: {v}' for k, v in self.context))
        if occurrences > 1:
            parts.append(f"{labels['occurrences']}: {occurrences}")
        if self.details:
            parts.append(self.details)
        return '\n\n'.join(parts)


def make_report(operation, *, message=None, exception=None, title=None,
                context=None, language='fr', severity='error', details=None):
    language = language if language in TEXT else 'en'
    labels = TEXT[language]
    cause = str(exception) if exception is not None else ''
    summary = message or labels.get(operation, labels['ui'])
    if operation in ('generation', 'batch') and (
        cause.startswith('Aucune position de départ suffisamment dégagée')
        or cause.startswith('Départ invalide après génération :')
        or cause.startswith('Positions compatibles avec terrain, objets et relief insuffisantes :')
        or cause.startswith('Aucun départ admissible respectant la séparation de l’éditeur')
        or cause.startswith('Aucun départ admissible sur l’île ')
    ):
        summary = labels['starts']
    action = ''
    if isinstance(exception, PermissionError):
        action = labels['permission']
    elif isinstance(exception, FileNotFoundError):
        action = labels['missing']
    elif isinstance(exception, ValueError):
        action = labels['input']
    elif operation == 'import' and isinstance(exception, struct.error):
        summary = labels['invalid_file']
        action = labels['file_action']
    if action == summary:
        action = ''
    if details is None:
        details = ''.join(traceback.format_exception(exception)) if exception is not None else ''
    return MessageReport(title or labels[severity], summary, cause, action, operation,
                         tuple((str(k), str(v)) for k, v in (context or {}).items()),
                         details, language, severity)


class MessageWindow(ThemedWindow):
    """Non-blocking reports; repeated errors do not create a cascade of dialogs."""
    def __init__(self, owner):
        super().__init__(owner)
        self.withdraw()
        self.reports = []
        self.counts = []
        self.previous_grab = None
        self.expanded = False
        self.body = ttk.Frame(self, padding=16)
        self.body.pack(fill='both', expand=True)
        self.selector = ttk.Combobox(self.body, state='readonly')
        self.selector.bind('<<ComboboxSelected>>', lambda event: self.refresh())
        self.summary = ttk.Label(self.body, justify='left', wraplength=620)
        self.summary.pack(fill='x', pady=(0, 10))
        self.cause = ttk.Label(self.body, justify='left', wraplength=620)
        self.cause.pack(fill='x', pady=(0, 8))
        self.action = ttk.Label(self.body, justify='left', wraplength=620)
        self.action.pack(fill='x', pady=(0, 8))
        self.toggle_button = ttk.Button(self.body, command=self.toggle_details)
        self.toggle_button.pack(anchor='w', pady=(0, 10))
        self.detail_frame = ttk.Frame(self.body)
        self.detail_text = self.theme_widget(tk.Text(self.detail_frame, width=76, height=12,
                                                    wrap='word', state='disabled'),
                                             background='field', foreground='fg',
                                             insertbackground='fg', selectbackground='selection',
                                             selectforeground='selection_text')
        self.detail_text.pack(side='left', fill='both', expand=True)
        scrollbar = ttk.Scrollbar(self.detail_frame, command=self.detail_text.yview)
        scrollbar.pack(side='right', fill='y')
        self.detail_text.configure(yscrollcommand=scrollbar.set)
        self.status = ttk.Label(self.body, style='Hint.TLabel')
        self.status.pack(fill='x', pady=(8, 0))
        self.actions = ttk.Frame(self.body)
        self.actions.pack(fill='x', pady=(10, 0))
        self.copy_button = ttk.Button(self.actions, command=self.copy_message)
        self.copy_button.pack(side='left')
        self.copy_all_button = ttk.Button(self.actions, command=lambda: self.copy_message(all_reports=True))
        self.close_button = ttk.Button(self.actions, command=self.destroy)
        self.close_button.pack(side='right')
        self.protocol('WM_DELETE_WINDOW', self.destroy)
        self.bind('<Escape>', lambda event: self.destroy())
        self.bind('<Configure>', self._resize_wrap, add='+')
        self.minsize(440, 200)

    def _resize_wrap(self, event):
        if event.widget is self:
            for label in (self.summary, self.cause, self.action):
                label.configure(wraplength=max(200, event.width - 40))

    def add_report(self, report):
        if report in self.reports:
            index = self.reports.index(report)
            self.counts[index] += 1
        else:
            index = len(self.reports)
            self.reports.append(report)
            self.counts.append(1)
        self.selector.configure(values=[f'{i+1}. {r.title} — {r.message[:70]}'
                                       for i, r in enumerate(self.reports)])
        self.selector.current(index)
        if len(self.reports) > 1:
            self.selector.pack(before=self.summary, fill='x', pady=(0, 12))
            self.copy_all_button.pack(side='left', padx=(8, 0))
        grab = self.theme_owner.grab_current()
        if grab is not None:
            self.previous_grab = grab
            grab.grab_release()
        self.refresh()
        self.update_idletasks()
        if not self.winfo_ismapped():
            owner = self.theme_owner
            width = min(680, self.winfo_screenwidth() - 32)
            height = min(self.winfo_reqheight(), self.winfo_screenheight() - 64)
            left = max(0, min(owner.winfo_rootx() + (owner.winfo_width()-width)//2,
                              self.winfo_screenwidth()-width))
            top = max(0, min(owner.winfo_rooty() + (owner.winfo_height()-height)//2,
                             self.winfo_screenheight()-height))
            self.geometry(f'{width}x{height}+{left}+{top}')
        else:
            self.geometry(f'{self.winfo_width()}x{min(self.winfo_reqheight(), self.winfo_screenheight()-64)}')
        self.deiconify()
        self.lift()
        self.copy_button.focus_set()

    def refresh(self):
        index = self.selector.current()
        report = self.reports[index]
        labels = TEXT[report.language]
        self.title(report.title)
        self.summary.configure(text=report.message)
        # Bound the brief cause; the complete original is always copied and
        # available in the scrollable details, including very long exceptions.
        readable_cause = ' '.join(report.cause.split())
        brief = readable_cause[:400] + ('…' if len(readable_cause) > 400 else '')
        self.cause.configure(text=brief)
        self.action.configure(text=report.action)
        self.toggle_button.configure(text=labels['hide' if self.expanded else 'details'])
        self.copy_button.configure(text=labels['copy'])
        self.copy_all_button.configure(text=labels['copy_all'])
        self.close_button.configure(text=labels['close'])
        self.status.configure(text=f"{labels['occurrences']}: {self.counts[index]}" if self.counts[index] > 1 else '')
        self.detail_text.configure(state='normal')
        self.detail_text.delete('1.0', 'end')
        self.detail_text.insert('1.0', report.copy_text(self.counts[index]))
        self.detail_text.configure(state='disabled')

    def toggle_details(self):
        self.expanded = not self.expanded
        if self.expanded:
            self.detail_frame.pack(before=self.status, fill='both', expand=True)
        else:
            self.detail_frame.pack_forget()
        self.refresh()
        self.update_idletasks()
        self.geometry(f'{self.winfo_width()}x{min(self.winfo_reqheight(), self.winfo_screenheight()-64)}')

    def copy_message(self, *, all_reports=False):
        index = self.selector.current()
        labels = TEXT[self.reports[index].language]
        text = ('\n\n' + '='*48 + '\n\n').join(
            report.copy_text(count) for report, count in zip(self.reports, self.counts)
        ) if all_reports else self.reports[index].copy_text(self.counts[index])
        try:
            self.theme_owner.clipboard_clear()
            self.theme_owner.clipboard_append(text)
            self.status.configure(text=labels['copied'])
        except tk.TclError:
            self.status.configure(text=labels['copy_failed'])

    def destroy(self):
        owner = self.theme_owner
        if getattr(owner, '_message_window', None) is self:
            owner._message_window = None
        previous = self.previous_grab
        super().destroy()
        if previous is not None and previous.winfo_exists() and owner.grab_current() is None:
            previous.grab_set()
            previous.focus_set()


def show_message(parent, operation='ui', **options):
    owner = parent
    while getattr(owner, 'master', None) is not None:
        owner = owner.master
    options.setdefault('language', getattr(owner, 'prefs', {}).get('language', 'fr'))
    report = make_report(operation, **options)
    return show_report(parent, report)


def show_report(parent, report):
    owner = parent
    while getattr(owner, 'master', None) is not None:
        owner = owner.master
    window = getattr(owner, '_message_window', None)
    if window is None or not window.winfo_exists():
        window = owner._message_window = MessageWindow(owner)
    window.add_report(report)
    return window
