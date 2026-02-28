import os

from iniinfo import iniInfo
from managers.actionmanager import ActionManager
from tarpl.tarplapi import TarpL
from tarpl.tarplclasses import TarpLAPIEnum


def test_headless_yesno_prompts_and_accepts_yes(monkeypatch, capsys) -> None:
    prompts = []
    monkeypatch.setenv("TARPL_HEADLESS", "1")
    monkeypatch.setattr("builtins.input", lambda prompt: prompts.append(prompt) or "yes")

    result = TarpL().YESNO("YESNO::Proceed with install?::echo go", None)

    output = capsys.readouterr()
    assert "USER CONFIRMATION REQUIRED" in output.out
    assert "Proceed with install?" in output.out
    assert "=" * 72 in output.out
    assert result.rtnstate is True
    assert result.rtnvalue == "echo go"
    assert result.tarpltype == TarpLAPIEnum.YESNO
    assert prompts == ["Enter choice [y/N]: "]


def test_headless_yesno_prompts_and_defaults_to_no(monkeypatch, capsys) -> None:
    prompts = []
    monkeypatch.setenv("TARPL_HEADLESS", "1")
    monkeypatch.setattr("builtins.input", lambda prompt: prompts.append(prompt) or "")

    result = TarpL().YESNO("YESNO::Proceed with install?::echo go", None)

    output = capsys.readouterr()
    assert "USER CONFIRMATION REQUIRED" in output.out
    assert "Proceed with install?" in output.out
    assert "=" * 72 in output.out
    assert result.rtnstate is False
    assert result.rtnvalue == "echo go"
    assert result.tarpltype == TarpLAPIEnum.YESNO
    assert prompts == ["Enter choice [y/N]: "]


def test_headless_msgbox_prints_message_and_waits_for_enter(monkeypatch, capsys) -> None:
    prompts = []
    monkeypatch.setenv("TARPL_HEADLESS", "1")
    monkeypatch.setattr("builtins.input", lambda prompt: prompts.append(prompt) or "")

    result = TarpL().MSGBOX("MSGBOX::Important maintenance notice", None)

    output = capsys.readouterr()
    assert "USER MESSAGE" in output.out
    assert "Important maintenance notice" in output.out
    assert "=" * 72 in output.out
    assert prompts == ["Press Enter to continue..."]
    assert result.rtnstate is False
    assert result.tarpltype == TarpLAPIEnum.MSGBOX


def test_headless_msgbox_defaults_cleanly_when_stdin_is_unavailable(monkeypatch, capsys) -> None:
    monkeypatch.setenv("TARPL_HEADLESS", "1")

    def raise_eof(_: str) -> str:
        raise EOFError

    monkeypatch.setattr("builtins.input", raise_eof)

    result = TarpL().MSGBOX("MSGBOX::Important maintenance notice", None)

    output = capsys.readouterr()
    assert "USER MESSAGE" in output.out
    assert "Important maintenance notice" in output.out
    assert result.rtnstate is False
    assert result.tarpltype == TarpLAPIEnum.MSGBOX


def test_headless_poplist_prompts_for_numbered_selection(monkeypatch, capsys) -> None:
    prompts = []
    monkeypatch.setenv("TARPL_HEADLESS", "1")
    monkeypatch.setattr("builtins.input", lambda prompt: prompts.append(prompt) or "2")

    result = TarpL().POPLIST("POPLIST::Pick deployment role::INPUTLIST::Admin,PowerUser,Viewer::selected_role", None)

    output = capsys.readouterr()
    assert "USER SELECTION REQUIRED" in output.out
    assert "Pick deployment role" in output.out
    assert "1. Admin" in output.out
    assert "2. PowerUser" in output.out
    assert "3. Viewer" in output.out
    assert prompts == ["Enter selection number (blank to cancel): "]
    assert result.rtnstate is True
    assert result.rtnvalue == "PowerUser"
    assert result.rtnvar == "selected_role"
    assert result.tarpltype == TarpLAPIEnum.POPLIST


def test_headless_poplist_allows_blank_to_cancel(monkeypatch, capsys) -> None:
    prompts = []
    monkeypatch.setenv("TARPL_HEADLESS", "1")
    monkeypatch.setattr("builtins.input", lambda prompt: prompts.append(prompt) or "")

    result = TarpL().POPLIST("POPLIST::Pick deployment role::INPUTLIST::Admin,PowerUser,Viewer::selected_role", None)

    output = capsys.readouterr()
    assert "USER SELECTION REQUIRED" in output.out
    assert prompts == ["Enter selection number (blank to cancel): "]
    assert result.rtnstate is False
    assert result.tarpltype == TarpLAPIEnum.POPLIST


def test_headless_poplist_reads_options_from_file(monkeypatch, capsys, tmp_path) -> None:
    option_file = tmp_path / "options.txt"
    option_file.write_text("Alpha,Beta,Gamma", encoding="utf-8")
    prompts = []
    monkeypatch.setenv("TARPL_HEADLESS", "1")
    monkeypatch.setattr("builtins.input", lambda prompt: prompts.append(prompt) or "3")

    action = f"POPLIST::Pick value from file::INPUTFILE::{option_file}::selected_value"
    result = TarpL().POPLIST(action, None)

    output = capsys.readouterr()
    assert "1. Alpha" in output.out
    assert "2. Beta" in output.out
    assert "3. Gamma" in output.out
    assert prompts == ["Enter selection number (blank to cancel): "]
    assert result.rtnstate is True
    assert result.rtnvalue == "Gamma"
    assert result.rtnvar == "selected_value"
    assert result.tarpltype == TarpLAPIEnum.POPLIST


def test_if_then_else_returns_then_branch_when_condition_matches() -> None:
    info = iniInfo()
    info.variables = {"host": "127.0.0.1"}
    info.userinput = {}
    info.returnvars = {}

    result = TarpL().IFTHENELSE(
        "[IF]%host% == 127.0.0.1[THEN]echo localhost[ELSE]echo remote",
        info,
    )

    assert result.rtnstate is True
    assert result.rtnvalue == "echo localhost"
    assert result.tarpltype == TarpLAPIEnum.IFTHENELSE


def test_if_then_else_returns_else_branch_when_condition_does_not_match() -> None:
    info = iniInfo()
    info.variables = {"host": "10.0.0.9"}
    info.userinput = {}
    info.returnvars = {}

    result = TarpL().IFTHENELSE(
        "[IF]%host% == 127.0.0.1[THEN]echo localhost[ELSE]echo remote",
        info,
    )

    assert result.rtnstate is True
    assert result.rtnvalue == "echo remote"
    assert result.tarpltype == TarpLAPIEnum.IFTHENELSE


def test_action_manager_executes_nested_tarpl_branch_without_shelling(monkeypatch, capsys) -> None:
    class DummyWindow:
        def update_idletasks(self) -> None:
            return None

    class DummyVar:
        def set(self, value: str) -> None:
            return None

    info = iniInfo()
    info.installtype = "LOCAL"
    info.watchdog = False
    info.variables = {"host": "127.0.0.1"}
    info.userinput = {}
    info.returnvars = {}
    info.options = {}
    info.actions = {
        "checkip": "[IF]%host% == 127.0.0.1[THEN]MSGBOX::You are using localhost[ELSE]echo remote"
    }

    manager = ActionManager()

    def fail_execute(*args, **kwargs):
        raise AssertionError("executeProcs should not run for nested MSGBOX")

    monkeypatch.setenv("TARPL_HEADLESS", "1")
    monkeypatch.setattr("builtins.input", lambda prompt: "")
    monkeypatch.setattr(manager.process_manager, "executeProcs", fail_execute)
    monkeypatch.setattr(manager.process_manager, "executeProcsDebug", fail_execute)

    manager.doActionsLocal(DummyWindow(), {}, DummyVar(), info)

    output = capsys.readouterr()
    assert "USER MESSAGE" in output.out
    assert "You are using localhost" in output.out
