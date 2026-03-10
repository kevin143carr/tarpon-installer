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


class FakeStream:
    def __init__(self, lines=None, exit_status: int = 0) -> None:
        self._lines = list(lines or [])
        self._index = 0
        self.channel = type("Channel", (), {"recv_exit_status": lambda _self: exit_status})()

    def readline(self) -> str:
        if self._index >= len(self._lines):
            return ""
        line = self._lines[self._index]
        self._index += 1
        return line


class FakeSSH:
    def __init__(self, exit_status_by_command=None) -> None:
        self.commands = []
        self.exit_status_by_command = dict(exit_status_by_command or {})

    def exec_command(self, command):
        self.commands.append(command)
        exit_status = self.exit_status_by_command.get(command, 0)
        return None, FakeStream(exit_status=exit_status), FakeStream()


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


def test_run_diagnostics_remote_collects_pass_and_fail_results() -> None:
    info = iniInfo()
    info.installtype = "REMOTELINUX"
    info.buildtype = "LINUX"
    info.userinput = {}
    info.variables = {}
    info.returnvars = {}
    info.diagnostics = {
        "check_pg": "DIAG::Checking PostgreSQL active::sudo systemctl is-active --quiet postgresql",
        "check_httpd": "DIAG::Checking httpd active::sudo systemctl is-active --quiet httpd",
    }

    manager = ActionManager()
    manager.hostname = "10.0.0.5"
    manager.ssh = FakeSSH(
        exit_status_by_command={
            "sudo systemctl is-active --quiet postgresql": 0,
            "sudo systemctl is-active --quiet httpd": 3,
        }
    )

    results = manager.runDiagnosticsSSH(DummyWindow(), {}, DummyVar(), info)

    assert results == [
        {"label": "Checking PostgreSQL active", "status": "PASS"},
        {"label": "Checking httpd active", "status": "FAILED"},
    ]


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
