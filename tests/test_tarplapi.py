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


def test_headless_poplist_strips_quotes_and_whitespace_from_inputlist(monkeypatch, capsys) -> None:
    prompts = []
    monkeypatch.setenv("TARPL_HEADLESS", "1")
    monkeypatch.setattr("builtins.input", lambda prompt: prompts.append(prompt) or "2")

    result = TarpL().POPLIST('POPLIST::Pick cluster::INPUTLIST::" ecs, ecds "::selected_value', None)

    output = capsys.readouterr()
    assert "1. ecs" in output.out
    assert "2. ecds" in output.out
    assert prompts == ["Enter selection number (blank to cancel): "]
    assert result.rtnstate is True
    assert result.rtnvalue == "ecds"
    assert result.rtnvar == "selected_value"
    assert result.tarpltype == TarpLAPIEnum.POPLIST


def test_gui_poplist_dispatches_dialog_via_ui_thread(monkeypatch) -> None:
    tarpl = TarpL()
    window = object()
    dispatch = {}

    def fake_call_on_ui_thread(ui_window, func, *args, **kwargs):
        dispatch["window"] = ui_window
        dispatch["kwargs"] = kwargs
        func(*args, **kwargs)

    def fake_show_poplist(items, parent, titletext):
        dispatch["items"] = items
        dispatch["parent"] = parent
        dispatch["title"] = titletext
        return "PowerUser"

    monkeypatch.delenv("TARPL_HEADLESS", raising=False)
    monkeypatch.setattr("tarpl.tarplapi.call_on_ui_thread", fake_call_on_ui_thread)
    monkeypatch.setattr(tarpl.pop_listbox, "showPopListbox", fake_show_poplist)

    result = tarpl.POPLIST(
        "POPLIST::Pick deployment role::INPUTLIST::Admin,PowerUser,Viewer::selected_role",
        window,
    )

    assert dispatch["window"] is window
    assert dispatch["kwargs"] == {}
    assert dispatch["items"] == ["Admin", "PowerUser", "Viewer"]
    assert dispatch["parent"] is window
    assert dispatch["title"] == "Pick deployment role"
    assert result.rtnstate is True
    assert result.rtnvalue == "PowerUser"
    assert result.rtnvar == "selected_role"


def test_gui_yesno_dispatches_messagebox_via_ui_thread(monkeypatch) -> None:
    tarpl = TarpL()
    window = object()
    dispatch = {}

    def fake_call_on_ui_thread(ui_window, func, *args, **kwargs):
        dispatch["window"] = ui_window
        dispatch["kwargs"] = kwargs
        func(*args, **kwargs)

    def fake_askyesno(title, message, parent=None):
        dispatch["title"] = title
        dispatch["message"] = message
        dispatch["parent"] = parent
        return True

    monkeypatch.delenv("TARPL_HEADLESS", raising=False)
    monkeypatch.setattr("tarpl.tarplapi.call_on_ui_thread", fake_call_on_ui_thread)
    monkeypatch.setattr("tarpl.tarplapi.msgbox.askyesno", fake_askyesno)

    result = tarpl.YESNO("YESNO::Proceed with install?::echo go", window)

    assert dispatch["window"] is window
    assert dispatch["kwargs"] == {}
    assert dispatch["title"] == "User Question"
    assert dispatch["message"] == "Proceed with install?"
    assert dispatch["parent"] is window
    assert result.rtnstate is True
    assert result.rtnvalue == "echo go"


def test_gui_msgbox_dispatches_messagebox_via_ui_thread(monkeypatch) -> None:
    tarpl = TarpL()
    window = object()
    dispatch = {}

    def fake_call_on_ui_thread(ui_window, func, *args, **kwargs):
        dispatch["window"] = ui_window
        dispatch["kwargs"] = kwargs
        func(*args, **kwargs)

    def fake_showinfo(title, message, parent=None):
        dispatch["title"] = title
        dispatch["message"] = message
        dispatch["parent"] = parent
        return "ok"

    monkeypatch.delenv("TARPL_HEADLESS", raising=False)
    monkeypatch.setattr("tarpl.tarplapi.call_on_ui_thread", fake_call_on_ui_thread)
    monkeypatch.setattr("tarpl.tarplapi.msgbox.showinfo", fake_showinfo)

    result = tarpl.MSGBOX("MSGBOX::Important maintenance notice", window)

    assert dispatch["window"] is window
    assert dispatch["kwargs"] == {}
    assert dispatch["title"] == "Information"
    assert dispatch["message"] == "Important maintenance notice"
    assert dispatch["parent"] is window
    assert result.rtnstate is False
    assert result.tarpltype == TarpLAPIEnum.MSGBOX


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


def test_tarpl_detection_does_not_match_keywords_inside_shell_commands() -> None:
    tarpl = TarpL()

    assert tarpl.CheckForTarpL("echo User accepted YESNO prompt") is False
    assert tarpl.getTarpL("echo User accepted YESNO prompt") == ""


def test_action_manager_yesno_command_can_return_shell_text_containing_yesno(monkeypatch) -> None:
    info = iniInfo()
    info.variables = {}
    info.userinput = {}
    info.returnvars = {}

    manager = ActionManager()

    monkeypatch.setattr(
        manager._tarpL,
        "YESNO",
        lambda action, window: type(
            "Result",
            (),
            {
                "rtnstate": True,
                "rtnvalue": "echo User accepted YESNO prompt",
                "rtnvar": "",
                "tarpltype": TarpLAPIEnum.YESNO,
            },
        )(),
    )

    finalstr, skip_action, tarpLrtn = manager._resolve_action_command(
        "YESNO::Proceed with install?::echo User accepted YESNO prompt",
        info,
        None,
    )

    assert skip_action is False
    assert finalstr == "echo User accepted YESNO prompt"
    assert tarpLrtn.tarpltype == TarpLAPIEnum.YESNO


def test_action_manager_runs_defaultchecked_option_action_without_opening_options_dialog(monkeypatch) -> None:
    class DummyWindow:
        def update_idletasks(self) -> None:
            return None

    class DummyVar:
        def set(self, value: str) -> None:
            return None

    info = iniInfo()
    info.installtype = "LOCAL"
    info.watchdog = False
    info.variables = {}
    info.userinput = {}
    info.returnvars = {}
    info.options = {
        "option_prepare_workspace": "DEFAULTCHECKED||Prepare workspace",
    }
    info.actions = {
        "option_prepare_workspace": "echo should_run",
    }
    info.optionvals = {}

    manager = ActionManager()
    calls = []
    monkeypatch.setattr(
        manager.process_manager,
        "executeProcs",
        lambda cmd, watchdog, timeout: calls.append(cmd) or 0,
    )
    monkeypatch.setattr(
        manager.process_manager,
        "executeProcsDebug",
        lambda cmd, watchdog, timeout: calls.append(cmd) or 0,
    )

    manager.doActionsLocal(DummyWindow(), {}, DummyVar(), info)

    assert calls == ["echo should_run"]


def test_action_manager_skips_unchecked_option_action(monkeypatch) -> None:
    class DummyWindow:
        def update_idletasks(self) -> None:
            return None

    class DummyVar:
        def set(self, value: str) -> None:
            return None

    class FakeVar:
        def __init__(self, value: str) -> None:
            self.value = value

        def get(self) -> str:
            return self.value

    info = iniInfo()
    info.installtype = "LOCAL"
    info.watchdog = False
    info.variables = {}
    info.userinput = {}
    info.returnvars = {}
    info.options = {
        "option_prepare_workspace": "Prepare workspace",
    }
    info.actions = {
        "option_prepare_workspace": "echo should_not_run",
    }
    info.optionvals = {
        "option_prepare_workspace": FakeVar("0"),
    }

    manager = ActionManager()
    calls = []
    monkeypatch.setattr(
        manager.process_manager,
        "executeProcs",
        lambda cmd, watchdog, timeout: calls.append(cmd) or 0,
    )
    monkeypatch.setattr(
        manager.process_manager,
        "executeProcsDebug",
        lambda cmd, watchdog, timeout: calls.append(cmd) or 0,
    )

    manager.doActionsLocal(DummyWindow(), {}, DummyVar(), info)

    assert calls == []


def test_exec_pyfunc_passes_window_keyword_when_supported(tmp_path, monkeypatch, capsys) -> None:
    script = tmp_path / "callback.py"
    script.write_text(
        "def capture(arg1, window=None):\n"
        "    print(f'{arg1}|{window is not None}')\n",
        encoding="utf-8",
    )

    tarpl = TarpL()
    window = object()
    monkeypatch.chdir(tmp_path)

    result = tarpl.EXEC_PYFUNC("EXEC_PYFUNC::callback.py::capture::hello", window)
    output = capsys.readouterr()

    assert result.tarpltype == TarpLAPIEnum.EXEC_PYFUNC
    assert result.rtnstate is False
    assert "hello|True" in output.out


def test_exec_pyfunc_dispatches_window_callbacks_via_ui_thread(tmp_path, monkeypatch) -> None:
    script = tmp_path / "callback.py"
    script.write_text(
        "def capture(arg1, window=None):\n"
        "    window.calls.append((arg1, window is not None))\n",
        encoding="utf-8",
    )

    tarpl = TarpL()

    class DummyWindow:
        def __init__(self) -> None:
            self.calls = []

    window = DummyWindow()
    dispatch = {}

    def fake_call_on_ui_thread(ui_window, func, *args, **kwargs):
        dispatch["window"] = ui_window
        dispatch["kwargs"] = kwargs
        func(*args, **kwargs)

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr("tarpl.tarplapi.call_on_ui_thread", fake_call_on_ui_thread)

    tarpl.EXEC_PYFUNC("EXEC_PYFUNC::callback.py::capture::hello", window)

    assert dispatch["window"] is window
    assert dispatch["kwargs"] == {}
    assert window.calls == [("hello", True)]


def test_exec_pyfunc_keeps_legacy_signature_without_window(tmp_path, monkeypatch, capsys) -> None:
    script = tmp_path / "legacy.py"
    script.write_text(
        "called = []\n"
        "def capture(arg1, arg2):\n"
        "    called.extend([arg1, arg2])\n"
        "    print('|'.join(called))\n",
        encoding="utf-8",
    )

    tarpl = TarpL()
    monkeypatch.chdir(tmp_path)

    tarpl.EXEC_PYFUNC("EXEC_PYFUNC::legacy.py::capture::hello,world", object())

    output = capsys.readouterr()
    assert "hello|world" in output.out


def test_exec_pyfunc_preserves_blank_trailing_argument(tmp_path, monkeypatch, capsys) -> None:
    script = tmp_path / "callback.py"
    script.write_text(
        "def capture(label, value, window=None):\n"
        "    print(f'{label}|{value}|{window is not None}')\n",
        encoding="utf-8",
    )

    tarpl = TarpL()
    monkeypatch.chdir(tmp_path)

    tarpl.EXEC_PYFUNC('EXEC_PYFUNC::callback.py::capture::HLA DX Files Location,', object())

    output = capsys.readouterr()
    assert "HLA DX Files Location||True" in output.out


def test_exec_pyfunc_supports_quoted_arguments_with_commas(tmp_path, monkeypatch, capsys) -> None:
    script = tmp_path / "callback.py"
    script.write_text(
        "def capture(label, value):\n"
        "    print(f'{label}|{value}')\n",
        encoding="utf-8",
    )

    tarpl = TarpL()
    monkeypatch.chdir(tmp_path)

    tarpl.EXEC_PYFUNC('EXEC_PYFUNC::callback.py::capture::\"HLA, DX Files Location\",/tmp/example', object())

    output = capsys.readouterr()
    assert "HLA, DX Files Location|/tmp/example" in output.out
