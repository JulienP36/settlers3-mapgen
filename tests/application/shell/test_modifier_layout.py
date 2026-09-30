from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
MAIN_WINDOW = (PROJECT_ROOT / "s3mapgen/application/main_window.py").read_text(encoding="utf-8")
BATCH_CONTROLLER = (PROJECT_ROOT / "s3mapgen/application/batch/controller.py").read_text(encoding="utf-8")


def test_main_modifier_selector_remains_reserved_and_disabled():
    assert "modifier_group=selector_group(primary_row,'Modificateurs')" in MAIN_WINDOW
    assert MAIN_WINDOW.index("arch_group=selector_group") < MAIN_WINDOW.index("modifier_group=selector_group")
    assert MAIN_WINDOW.index("modifier_group=selector_group") < MAIN_WINDOW.index("mirror_group=selector_group")
    assert "style='ImageSelect.TMenubutton',state='disabled'" in MAIN_WINDOW
    assert "command=self._modifier_none_selected,state='disabled'" in MAIN_WINDOW


def test_batch_modifier_slot_remains_reserved_and_disabled():
    assert "box=group('modifiers')" in BATCH_CONTROLLER
    assert "values=[bt['none']],state='disabled'" in BATCH_CONTROLLER
    assert "input_widgets.append((row['modifier'],'disabled'))" in BATCH_CONTROLLER
