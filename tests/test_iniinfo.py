from pathlib import Path

import pytest

from iniinfo import iniInfo


def test_read_config_file_parses_headless_startup_with_minimal_fields(tmp_path: Path) -> None:
    config_text = """
[STARTUP]
usegui = False
startupinfo = info
installtitle = title
buttontext = Install
watchdog = True
process_timeout = 600
adminrights = False

[USERINFO]
username = user
password = pass

[SERVERCONFIG]
host = 1.2.3.4

[BUILD]
buildtype = LINUX
installtype = LOCAL
resources = resources

[FILES]
foo.txt = /tmp/foo.txt

[REPO]

[RPM]

[ACTIONS]

[MODIFY]

[FINAL]

[OPTIONS]

[USERINPUT]

[VARIABLES]
"""
    config_path = tmp_path / "config.ini"
    config_path.write_text(config_text.strip(), encoding="utf-8")

    info = iniInfo()
    info.readConfigFile(str(config_path))

    assert info.watchdog is True
    assert info.process_timeout == 600
    assert info.adminrights is False
    assert info.usegui is False
    assert info.hostname == "1.2.3.4"
    assert info.buildtype == "LINUX"
    assert info.installtype == "LOCAL"
    assert info.files.get("foo.txt") == "/tmp/foo.txt"
    assert info.logoimage == ""
    assert info.themename == "superhero"
    assert info.displayfinalerrors is False


def test_read_config_file_requires_logoimg_for_gui_mode(tmp_path: Path) -> None:
    config_text = """
[STARTUP]
usegui = True
startupinfo = info
installtitle = title
buttontext = Install
watchdog = True
adminrights = False
themename = superhero

[USERINFO]
username = user
password = pass

[BUILD]
buildtype = LINUX
installtype = LOCAL
resources = resources

[FILES]

[REPO]

[RPM]

[ACTIONS]

[MODIFY]

[FINAL]

[OPTIONS]

[USERINPUT]

[VARIABLES]
"""
    config_path = tmp_path / "config.ini"
    config_path.write_text(config_text.strip(), encoding="utf-8")

    info = iniInfo()
    with pytest.raises(SystemExit):
        info.readConfigFile(str(config_path))


def test_read_config_file_parses_optional_displayfinalerrors_flag(tmp_path: Path) -> None:
    config_text = """
[STARTUP]
usegui = True
startupinfo = info
installtitle = title
logoimg = logo.png
buttontext = Install
watchdog = True
adminrights = False
themename = superhero
displayfinalerrors = True

[USERINFO]
username = user
password = pass

[BUILD]
buildtype = LINUX
installtype = LOCAL
resources = resources

[FILES]

[REPO]

[RPM]

[ACTIONS]

[MODIFY]

[FINAL]

[OPTIONS]

[USERINPUT]

[VARIABLES]
"""
    config_path = tmp_path / "config.ini"
    config_path.write_text(config_text.strip(), encoding="utf-8")

    info = iniInfo()
    info.readConfigFile(str(config_path))

    assert info.displayfinalerrors is True


def test_read_config_file_defaults_continuewitherrors_to_false(tmp_path: Path) -> None:
    config_text = """
[STARTUP]
usegui = True
startupinfo = info
installtitle = title
logoimg = logo.png
buttontext = Install
watchdog = True
adminrights = False
themename = superhero

[USERINFO]
username = user
password = pass

[BUILD]
buildtype = LINUX
installtype = LOCAL
resources = resources

[FILES]

[REPO]

[RPM]

[ACTIONS]

[MODIFY]

[FINAL]

[OPTIONS]

[USERINPUT]

[VARIABLES]
"""
    config_path = tmp_path / "config.ini"
    config_path.write_text(config_text.strip(), encoding="utf-8")

    info = iniInfo()
    info.readConfigFile(str(config_path))

    assert info.continuewitherrors is False


def test_read_config_file_parses_optional_continuewitherrors_flag(tmp_path: Path) -> None:
    config_text = """
[STARTUP]
usegui = True
startupinfo = info
installtitle = title
logoimg = logo.png
buttontext = Install
watchdog = True
adminrights = False
themename = superhero
continuewitherrors = True

[USERINFO]
username = user
password = pass

[BUILD]
buildtype = LINUX
installtype = LOCAL
resources = resources

[FILES]

[REPO]

[RPM]

[ACTIONS]

[MODIFY]

[FINAL]

[OPTIONS]

[USERINPUT]

[VARIABLES]
"""
    config_path = tmp_path / "config.ini"
    config_path.write_text(config_text.strip(), encoding="utf-8")

    info = iniInfo()
    info.readConfigFile(str(config_path))

    assert info.continuewitherrors is True


def test_read_config_file_allows_disabling_process_timeout(tmp_path: Path) -> None:
    config_text = """
[STARTUP]
usegui = False
startupinfo = info
installtitle = title
buttontext = Install
watchdog = False
process_timeout = 0
adminrights = False

[USERINFO]
username = user
password = pass

[BUILD]
buildtype = LINUX
installtype = LOCAL
resources = resources

[FILES]

[REPO]

[RPM]

[ACTIONS]

[MODIFY]

[FINAL]

[OPTIONS]

[USERINPUT]

[VARIABLES]
"""
    config_path = tmp_path / "config.ini"
    config_path.write_text(config_text.strip(), encoding="utf-8")

    info = iniInfo()
    info.readConfigFile(str(config_path))

    assert info.process_timeout is None


def test_read_config_file_defaults_usediagnostics_to_false(tmp_path: Path) -> None:
    config_text = """
[STARTUP]
usegui = False
startupinfo = info
installtitle = title
buttontext = Install
watchdog = False
adminrights = False

[USERINFO]
username = user
password = pass

[BUILD]
buildtype = LINUX
installtype = LOCAL
resources = resources

[FILES]

[REPO]

[RPM]

[ACTIONS]

[MODIFY]

[FINAL]

[OPTIONS]

[USERINPUT]

[VARIABLES]
"""
    config_path = tmp_path / "config.ini"
    config_path.write_text(config_text.strip(), encoding="utf-8")

    info = iniInfo()
    info.readConfigFile(str(config_path))

    assert info.usediagnostics is False
    assert info.diagnostics == {}


def test_read_config_file_parses_usediagnostics_and_diagnostics_section(tmp_path: Path) -> None:
    config_text = """
[STARTUP]
usegui = False
startupinfo = info
installtitle = title
buttontext = Install
watchdog = False
adminrights = False
usediagnostics = True

[USERINFO]
username = user
password = pass

[BUILD]
buildtype = LINUX
installtype = LOCAL
resources = resources

[FILES]

[REPO]

[RPM]

[ACTIONS]

[MODIFY]

[FINAL]

[DIAGNOSTICS]
checkservice = DIAG::Checking service::echo ok

[OPTIONS]

[USERINPUT]

[VARIABLES]
"""
    config_path = tmp_path / "config.ini"
    config_path.write_text(config_text.strip(), encoding="utf-8")

    info = iniInfo()
    info.readConfigFile(str(config_path))

    assert info.usediagnostics is True
    assert info.diagnostics == {"checkservice": "DIAG::Checking service::echo ok"}
