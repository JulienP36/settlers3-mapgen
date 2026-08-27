from pathlib import Path


SRC = (Path(__file__).resolve().parents[3] / "s3mapgen" / "application" / "main_window.py").read_text(encoding="utf-8")


def test_wide_header_has_generation_session_and_global_regions():
    assert "self.generation_panel.grid(row=0,column=0" in SRC
    assert "self.session_box.grid(row=0,column=2" in SRC
    assert "self.global_panel.grid(row=0,column=4" in SRC
    assert "shell.columnconfigure(1,weight=1);shell.columnconfigure(3,weight=1)" in SRC


def test_compact_header_moves_whole_session_block_below():
    assert "self.generation_panel.grid(row=0,column=0" in SRC
    assert "self.global_panel.grid(row=0,column=1" in SRC
    assert "self.session_box.grid(row=1,column=0,columnspan=2" in SRC


def test_generation_actions_use_independent_local_button_bars():
    assert "primary_actions=ttk.Frame(primary_row)" in SRC
    assert "seed_actions=ttk.Frame(secondary_row)" in SRC
    assert "self.file_actions=ttk.Frame(secondary_row)" in SRC
    assert "self.import_button.pack(side='left'" in SRC
    assert "self.export_btn.pack(side='left'" in SRC
    assert "self.preview_button.pack(side='left'" in SRC


def test_file_action_buttons_keep_natural_text_width():
    for line in SRC.splitlines():
        if any(name in line for name in ("self.import_button=", "self.export_btn=", "self.preview_button=")):
            assert "width=" not in line
    assert "for w in file_actions" not in SRC
