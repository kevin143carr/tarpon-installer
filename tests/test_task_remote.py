import logging
from pathlib import Path

from iniinfo import iniInfo
from managers.actionmanager import ActionManager
from task import Task
from tarpon_installer import HeadlessVar, run_headless


class DummyWindow:
    def update_idletasks(self) -> None:
        return None


class DummyVar:
    def __init__(self) -> None:
        self.value = ""

    def set(self, value: str) -> None:
        self.value = value

    def get(self) -> str:
        return self.value


class DummyInput:
    def __init__(self, value: str) -> None:
        self.value = value

    def get(self) -> str:
        return self.value


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
    def __init__(self, exit_status_by_command=None, stderr_by_command=None) -> None:
        self.commands = []
        self.exit_status_by_command = dict(exit_status_by_command or {})
        self.stderr_by_command = dict(stderr_by_command or {})

    def exec_command(self, command):
        self.commands.append(command)
        exit_status = self.exit_status_by_command.get(command, 0)
        stderr_lines = self.stderr_by_command.get(command, [])
        return None, FakeStream(exit_status=exit_status), FakeStream(lines=stderr_lines)


def test_do_actions_remote_uses_finalactions_for_final_phase(monkeypatch) -> None:
    info = iniInfo()
    info.installtype = "REMOTELINUX"
    info.buildtype = "LINUX"
    info.actions = {"action_a": "echo action"}
    info.finalactions = {"final_a": "echo final"}
    info.options = {}
    info.optionvals = {}

    task = Task(info)
    captured = {}

    def fake_do_actions_ssh(window, bar, taskitem, actions, ini_info):
        captured["actions"] = actions

    monkeypatch.setattr(task.action_manager, "doActionsSSH", fake_do_actions_ssh)

    task.doActions(DummyWindow(), {}, DummyVar(), info, actiontype="final")

    assert captured["actions"] == info.finalactions


def test_action_manager_do_actions_ssh_applies_option_gating_and_tokens() -> None:
    info = iniInfo()
    info.userinput = {"customer_name": DummyInput("acme")}
    info.variables = {}
    info.returnvars = {}
    info.options = {
        "option_run": "Run optional command",
        "option_skip": "Skip optional command",
    }
    info.optionvals = {
        "option_run": HeadlessVar("1"),
        "option_skip": HeadlessVar("0"),
    }

    manager = ActionManager()
    manager.ssh = FakeSSH()
    manager.hostname = "10.0.0.5"

    actions = {
        "option_run": "echo customer=%customer_name% host=%host%",
        "option_skip": "echo should_not_run",
    }

    manager.doActionsSSH(DummyWindow(), {}, DummyVar(), actions, info)

    assert manager.ssh.commands == ["echo customer=acme host=10.0.0.5"]


def test_action_manager_do_actions_ssh_uses_defaultchecked_when_option_value_missing() -> None:
    info = iniInfo()
    info.userinput = {}
    info.variables = {}
    info.returnvars = {}
    info.options = {
        "option_default_on": "DEFAULTCHECKED::Run by default",
        "option_default_off": "Run only when selected",
    }
    info.optionvals = {}

    manager = ActionManager()
    manager.ssh = FakeSSH()
    manager.hostname = "10.0.0.5"

    actions = {
        "option_default_on": "echo run_default_on",
        "option_default_off": "echo should_not_run",
    }

    manager.doActionsSSH(DummyWindow(), {}, DummyVar(), actions, info)

    assert manager.ssh.commands == ["echo run_default_on"]


def test_action_manager_do_actions_ssh_ifgoto_branches_on_remote_exit_code() -> None:
    info = iniInfo()
    info.userinput = {}
    info.variables = {}
    info.returnvars = {}
    info.options = {}
    info.optionvals = {}
    info.continuewitherrors = False

    manager = ActionManager()
    manager.ssh = FakeSSH(exit_status_by_command={"echo branch-check": 0, "echo target": 0})
    manager.hostname = "10.0.0.5"

    actions = {
        "step1": "IFGOTO::echo branch-check::step3",
        "step2": "echo should-not-run",
        "step3": "echo target",
    }

    manager.doActionsSSH(DummyWindow(), {}, DummyVar(), actions, info)

    assert manager.ssh.commands == ["echo branch-check", "echo target"]


def test_action_manager_do_actions_ssh_raises_on_nonzero_when_continuewitherrors_false() -> None:
    info = iniInfo()
    info.userinput = {}
    info.variables = {}
    info.returnvars = {}
    info.options = {}
    info.optionvals = {}
    info.continuewitherrors = False

    manager = ActionManager()
    manager.ssh = FakeSSH(exit_status_by_command={"echo fail": 2})
    manager.hostname = "10.0.0.5"

    actions = {
        "bad_action": "echo fail",
        "later_action": "echo should-not-run",
    }

    try:
        manager.doActionsSSH(DummyWindow(), {}, DummyVar(), actions, info)
        raise AssertionError("Expected RuntimeError for failed remote action")
    except RuntimeError as ex:
        assert "bad_action" in str(ex)
        assert "exit code 2" in str(ex)


def test_action_manager_do_actions_ssh_continues_on_nonzero_when_continuewitherrors_true() -> None:
    info = iniInfo()
    info.userinput = {}
    info.variables = {}
    info.returnvars = {}
    info.options = {}
    info.optionvals = {}
    info.continuewitherrors = True

    manager = ActionManager()
    manager.ssh = FakeSSH(exit_status_by_command={"echo fail": 2, "echo later": 0})
    manager.hostname = "10.0.0.5"

    actions = {
        "bad_action": "echo fail",
        "later_action": "echo later",
    }

    manager.doActionsSSH(DummyWindow(), {}, DummyVar(), actions, info)

    assert manager.ssh.commands == ["echo fail", "echo later"]


def test_modify_files_ssh_supports_current_add_and_change_format() -> None:
    info = iniInfo()
    info.installtype = "REMOTELINUX"
    info.buildtype = "LINUX"
    info.userinput = {"customer_name": DummyInput("acme"), "environment": DummyInput("qa")}
    info.variables = {"remote_stage": "/tmp/tarpon_remote"}
    info.returnvars = {}
    info.continuewitherrors = False
    info.modify = {
        "1": "{FILE}%remote_stage%/%customer_name%/%environment%/generated.conf{ADD}a=1||b=2",
        "2": "{FILE}%remote_stage%/%customer_name%/%environment%/generated.conf{CHANGE}a=1||a=9",
    }

    task = Task(info)
    task.ssh = FakeSSH()

    task.modifyFilesSSH(info.modify, info)

    assert any("mkdir -p /tmp/tarpon_remote/acme/qa" in command for command in task.ssh.commands)
    assert any(
        "printf '%s\\n' a=1 b=2 >> /tmp/tarpon_remote/acme/qa/generated.conf" in command
        for command in task.ssh.commands
    )
    assert any("sed -i 's|a=1|a=9|g'" in command for command in task.ssh.commands)


def test_run_headless_skips_local_rpm_install_for_remote(monkeypatch) -> None:
    info = iniInfo()
    info.usegui = False
    info.buildtype = "LINUX"
    info.installtype = "REMOTELINUX"
    info.resources = str(Path("."))
    info.watchdog = False
    info.process_timeout = 180
    info.actions = {}
    info.finalactions = {}
    info.modify = {}
    info.rpms = {"example": "example.rpm"}
    info.files = {}
    info.options = {}
    info.optionvals = {}
    info.userinput = {}
    info.variables = {}
    info.returnvars = {}
    info.usediagnostics = False

    rpm_called = {"value": False}
    remote_rpm_called = {"value": False}

    def fail_rpm(*args, **kwargs):
        rpm_called["value"] = True
        raise AssertionError("RPM install should not run for REMOTELINUX installs")

    def mark_remote_rpm(*args, **kwargs):
        remote_rpm_called["value"] = True

    monkeypatch.setattr("managers.rpmmanager.RpmManager.installLocalRPMs", fail_rpm)
    monkeypatch.setattr("managers.rpmmanager.RpmManager.installRemoteRPMs", mark_remote_rpm)
    monkeypatch.setattr(Task, "loginSSH", lambda self: None)
    monkeypatch.setattr(Task, "copyFromResources", lambda self, *args, **kwargs: None)
    monkeypatch.setattr(Task, "doActions", lambda self, *args, **kwargs: None)
    monkeypatch.setattr(Task, "modifyFiles", lambda self, *args, **kwargs: None)
    monkeypatch.setattr(Task, "finalActions", lambda self, *args, **kwargs: None)

    run_headless(info, logging.getLogger("test"))

    assert rpm_called["value"] is False
    assert remote_rpm_called["value"] is True
