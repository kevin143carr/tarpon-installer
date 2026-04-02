import sys
import types

from iniinfo import iniInfo

sys.modules.setdefault("ttkbootstrap", types.ModuleType("ttkbootstrap"))

tkscrolledframe_module = types.ModuleType("tkscrolledframe")
tkscrolledframe_module.ScrolledFrame = object
sys.modules.setdefault("tkscrolledframe", tkscrolledframe_module)

pil_module = types.ModuleType("PIL")
pil_image_module = types.ModuleType("PIL.Image")
pil_imagetk_module = types.ModuleType("PIL.ImageTk")
pil_module.Image = pil_image_module
pil_module.ImageTk = pil_imagetk_module
sys.modules.setdefault("PIL", pil_module)
sys.modules.setdefault("PIL.Image", pil_image_module)
sys.modules.setdefault("PIL.ImageTk", pil_imagetk_module)

import managers.guimanager as guimanager
from managers.guimanager import GuiManager


class FakeVar:
    def __init__(self, value: str) -> None:
        self.value = value

    def get(self) -> str:
        return self.value

    def set(self, value: str) -> None:
        self.value = value


def test_apply_option_defaults_checks_default_and_dependent_options() -> None:
    original_stringvar = guimanager.tk.StringVar
    guimanager.tk.StringVar = FakeVar
    info = iniInfo()
    info.options = {
        "option_prepare_workspace": "DEFAULTCHECKED||ALSOCHECKOPTION||option_show_summary,option_exec_python||Prepare workspace",
        "option_show_summary": "Show completion summary",
        "option_exec_python": "Execute Python callback popup",
    }
    info.optionvals = {}

    try:
        GuiManager()._apply_option_defaults(info)
    finally:
        guimanager.tk.StringVar = original_stringvar

    assert info.optionvals["option_prepare_workspace"].get() == "1"
    assert info.optionvals["option_show_summary"].get() == "1"
    assert info.optionvals["option_exec_python"].get() == "1"


def test_apply_option_toggle_checks_dependent_options_once() -> None:
    info = iniInfo()
    info.options = {
        "option_prepare_workspace": "ALSOCHECKOPTION||option_show_summary||Prepare workspace",
        "option_show_summary": "Show completion summary",
    }
    info.optionvals = {
        "option_prepare_workspace": FakeVar("1"),
        "option_show_summary": FakeVar("0"),
    }

    GuiManager()._apply_option_toggle("option_prepare_workspace", info)

    assert info.optionvals["option_prepare_workspace"].get() == "1"
    assert info.optionvals["option_show_summary"].get() == "1"


def test_apply_option_toggle_does_not_recheck_child_when_parent_stays_checked() -> None:
    info = iniInfo()
    info.options = {
        "option_prepare_workspace": "ALSOCHECKOPTION||option_show_summary||Prepare workspace",
        "option_show_summary": "Show completion summary",
    }
    info.optionvals = {
        "option_prepare_workspace": FakeVar("1"),
        "option_show_summary": FakeVar("0"),
    }

    manager = GuiManager()
    manager._apply_option_toggle("option_prepare_workspace", info)
    info.optionvals["option_show_summary"].set("0")
    manager._apply_option_toggle("option_show_summary", info)

    assert info.optionvals["option_prepare_workspace"].get() == "1"
    assert info.optionvals["option_show_summary"].get() == "0"


def test_apply_option_defaults_preserves_existing_values_when_dialog_reopens() -> None:
    info = iniInfo()
    info.options = {
        "option_prepare_workspace": "DEFAULTCHECKED||ALSOCHECKOPTION||option_show_summary||Prepare workspace",
        "option_show_summary": "Show completion summary",
    }
    info.optionvals = {
        "option_prepare_workspace": FakeVar("1"),
        "option_show_summary": FakeVar("0"),
    }

    GuiManager()._apply_option_defaults(info)

    assert info.optionvals["option_prepare_workspace"].get() == "1"
    assert info.optionvals["option_show_summary"].get() == "0"
