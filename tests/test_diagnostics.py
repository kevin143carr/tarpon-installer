import logging

from iniinfo import iniInfo
from managers.actionmanager import ActionManager
from tarpon_installer import run_headless


class DummyWindow:
    def update_idletasks(self) -> None:
        return None


class DummyVar:
    def __init__(self) -> None:
        self.value = ""

    def set(self, value: str) -> None:
        self.value = value


def test_run_diagnostics_local_collects_pass_and_fail_results(monkeypatch) -> None:
    info = iniInfo()
    info.installtype = "LOCAL"
    info.buildtype = "WINDOWS"
    info.watchdog = False
    info.process_timeout = 180
    info.userinput = {}
    info.variables = {}
    info.returnvars = {}
    info.diagnostics = {
        "check_ok": "DIAG::Checking OK::echo ok",
        "delay": "echo after",
        "check_fail": "DIAG::Checking Fail::cmd /c exit 1",
    }

    manager = ActionManager()
    executed = []

    def fake_execute(command, watchdog=False, timeout=180):
        executed.append(command)
        return 0 if command in {"echo ok", "echo after"} else 1

    monkeypatch.setattr(manager.process_manager, "executeProcs", fake_execute)
    monkeypatch.setattr(manager.process_manager, "executeProcsDebug", fake_execute)

    results = manager.runDiagnosticsLocal(DummyWindow(), {}, DummyVar(), info)

    assert results == [
        {"label": "Checking OK", "status": "PASS"},
        {"label": "Checking Fail", "status": "FAILED"},
    ]
    assert executed == ["echo ok", "echo after", "cmd /c exit 1"]


def test_run_diagnostics_local_supports_yesno_wrapped_diag(monkeypatch) -> None:
    info = iniInfo()
    info.installtype = "LOCAL"
    info.buildtype = "WINDOWS"
    info.watchdog = False
    info.process_timeout = 180
    info.userinput = {}
    info.variables = {}
    info.returnvars = {}
    info.diagnostics = {
        "prompted_check": "DIAG::Prompted restart::YESNO::Restart now?::echo restart"
    }

    manager = ActionManager()
    monkeypatch.setenv("TARPL_HEADLESS", "1")
    monkeypatch.setattr("builtins.input", lambda prompt: "yes")
    monkeypatch.setattr(manager.process_manager, "executeProcs", lambda *args, **kwargs: 0)
    monkeypatch.setattr(manager.process_manager, "executeProcsDebug", lambda *args, **kwargs: 0)

    results = manager.runDiagnosticsLocal(DummyWindow(), {}, DummyVar(), info)

    assert results == [{"label": "Prompted restart", "status": "PASS"}]


def test_run_headless_prints_diagnostics_results(monkeypatch, capsys) -> None:
    info = iniInfo()
    info.usegui = False
    info.installtitle = "Diag Run"
    info.buttontext = "Run"
    info.buildtype = "WINDOWS"
    info.installtype = "LOCAL"
    info.resources = "."
    info.watchdog = False
    info.process_timeout = 180
    info.actions = {}
    info.finalactions = {}
    info.modify = {}
    info.rpms = {}
    info.files = {}
    info.options = {}
    info.optionvals = {}
    info.userinput = {}
    info.variables = {}
    info.returnvars = {}
    info.usediagnostics = True
    info.diagnostics = {
        "check_ok": "DIAG::Checking OK::echo ok",
    }

    logger = logging.getLogger("test")

    monkeypatch.setenv("TARPL_HEADLESS", "1")
    monkeypatch.setattr("managers.processmanager.ProcessManager.executeProcs", lambda self, *args, **kwargs: 0)
    monkeypatch.setattr("managers.processmanager.ProcessManager.executeProcsDebug", lambda self, *args, **kwargs: 0)

    run_headless(info, logger)

    output = capsys.readouterr()
    assert "DIAGNOSTICS RESULTS" in output.out
    assert "Checking OK [PASS]" in output.out
