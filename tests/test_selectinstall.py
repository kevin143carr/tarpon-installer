from pathlib import Path

from tarpon_installer import (
    InstallerCandidate,
    discover_tarpon_installer_configs,
    main,
)


def _write_tarpon_like_ini(path: Path, title: str = "Test Installer", startup_info: str = "desc") -> None:
    path.write_text(
        f"""
[STARTUP]
usegui = False
startupinfo = {startup_info}
installtitle = {title}
buttontext = Install
watchdog = False
adminrights = False

[USERINFO]
username =
password =

[BUILD]
buildtype = WINDOWS
installtype = LOCAL
resources = .

[FILES]

[REPO]

[RPM]

[ACTIONS]

[MODIFY]

[FINAL]

[OPTIONS]

[USERINPUT]

[VARIABLES]
""".strip(),
        encoding="utf-8",
    )


def test_discover_tarpon_installer_configs_filters_non_tarpon_ini(tmp_path: Path) -> None:
    valid = tmp_path / "tarpon_install.ini"
    _write_tarpon_like_ini(valid, title="Alpha", startup_info="Alpha description")

    invalid = tmp_path / "buildadder.ini"
    invalid.write_text(
        """
[BUILDADDER]
name = not tarpon
""".strip(),
        encoding="utf-8",
    )

    matches = discover_tarpon_installer_configs(str(tmp_path))

    assert len(matches) == 1
    assert Path(matches[0].config_path) == valid
    assert matches[0].title == "Alpha"
    assert matches[0].description == "Alpha description"


def test_main_selectinstall_uses_selected_config(monkeypatch, tmp_path: Path) -> None:
    selected_config = tmp_path / "selected.ini"
    _write_tarpon_like_ini(selected_config)

    captured = {"configfile": None, "ran_headless": False, "scan_dir": None}

    def fake_discover(scan_dir: str):
        captured["scan_dir"] = scan_dir
        return [InstallerCandidate(str(selected_config), "Selected", "Chosen config")]

    monkeypatch.setattr("tarpon_installer.discover_tarpon_installer_configs", fake_discover)
    monkeypatch.setattr(
        "tarpon_installer.select_tarpon_installer_config",
        lambda _: str(selected_config),
    )

    def fake_read(self, configfile: str) -> None:
        captured["configfile"] = configfile
        self.usegui = False
        self.options = {}
        self.optionvals = {}
        self.userinput = {}
        self.variables = {}
        self.returnvars = {}
        self.actions = {}
        self.finalactions = {}
        self.modify = {}
        self.files = {}

    monkeypatch.setattr("iniinfo.iniInfo.readConfigFile", fake_read)
    monkeypatch.setattr("tarpon_installer.setup_logging", lambda *args, **kwargs: None)
    monkeypatch.setattr("tarpon_installer.ensure_admin", lambda *args, **kwargs: None)
    monkeypatch.setattr("tarpon_installer.show_headless_preflight_summary", lambda *args, **kwargs: None)
    monkeypatch.setattr(
        "tarpon_installer.run_headless",
        lambda *args, **kwargs: captured.__setitem__("ran_headless", True),
    )

    exit_code = main(["--selectinstall", "--selectinstalldir", str(tmp_path)])

    assert exit_code == 0
    assert captured["scan_dir"] == str(tmp_path)
    assert captured["configfile"] == str(selected_config)
    assert captured["ran_headless"] is True


def test_main_selectinstall_returns_error_when_no_profiles(monkeypatch) -> None:
    monkeypatch.setattr("tarpon_installer.discover_tarpon_installer_configs", lambda _: [])

    assert main(["--selectinstall", "--selectinstalldir", "/tmp/not-found"]) == 2


def test_main_selectinstall_returns_zero_when_user_cancels(monkeypatch) -> None:
    monkeypatch.setattr(
        "tarpon_installer.discover_tarpon_installer_configs",
        lambda _: [InstallerCandidate("config.ini", "Title", "Desc")],
    )
    monkeypatch.setattr("tarpon_installer.select_tarpon_installer_config", lambda _: None)

    assert main(["--selectinstall", "--selectinstalldir", "/tmp/somewhere"]) == 0


def test_main_selectinstall_requires_selectinstalldir() -> None:
    assert main(["--selectinstall"]) == 2


def test_main_selectinstalldir_without_selectinstall_returns_error() -> None:
    assert main(["--selectinstalldir", "/tmp/somewhere"]) == 2
