from pathlib import Path

from s3mapgen.application.ui.i18n.shell import FEEDBACK_TEXT

SRC = Path(__file__).resolve().parents[3] / "s3mapgen" / "application" / "main_window.py"
TEXT = "\n".join(
    path.read_text(encoding="utf-8")
    for path in (
        SRC,
        SRC.parent / "history" / "controller.py",
        SRC.parent / "workflows" / "generation.py",
    )
)

def test_modifiers_reserve_multi_select_menu_after_archetype():
    assert "self.modifier_button=ttk.Menubutton" in TEXT
    assert "self.modifier_menu.add_checkbutton" in TEXT
    assert "modifier_group=selector_group(primary_row,'Modificateurs')" in TEXT
    assert TEXT.index("arch_group=selector_group") < TEXT.index("modifier_group=selector_group")
    assert "def _modifier_keys(self):" in TEXT

def test_modifiers_are_part_of_cache_history_and_feedback():
    assert "modifiers=self._modifier_keys()" in TEXT
    assert "key.modifiers" in TEXT
    assert "modificateurs : {modifiers}" in FEEDBACK_TEXT["fr"]["ready"]
    assert "modifiers: {modifiers}" in FEEDBACK_TEXT["en"]["ready"]

def test_session_history_uses_stable_two_row_layout():
    assert "self.history_combo=ttk.Combobox(self.session_box,textvariable=self.history_var,state='readonly',width=27)" in TEXT
    assert "Keep full A/B identities when space allows" in TEXT
    assert "self.history_load_button.grid(row=1" in TEXT
    assert "self.history_clear_button.grid(row=1" in TEXT

def test_compact_global_controls_remain_in_their_own_panel():
    assert "self.global_panel=ttk.Frame(self._header_shell)" in TEXT
    assert "def _layout_global_controls(self,compact):" in TEXT
    assert "self.help_button.grid(row=2,column=0" in TEXT
    assert "self._theme_button.grid(row=2,column=2" in TEXT

def test_batch_slot_opens_the_batch_window_from_the_generation_header():
    assert "self.batch_generate_button=ttk.Button" in TEXT
    assert "Générer lot…" in TEXT
    assert "command=self._open_batch_window" in TEXT
