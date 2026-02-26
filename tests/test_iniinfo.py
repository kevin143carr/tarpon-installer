from pathlib import Path

from iniinfo import iniInfo


def test_read_config_file_parses_booleans_and_host(tmp_path: Path) -> None:
    config_text = """
[STARTUP]
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
    assert info.adminrights is False
    assert info.hostname == "1.2.3.4"
    assert info.buildtype == "LINUX"
    assert info.installtype == "LOCAL"
    assert info.files.get("foo.txt") == "/tmp/foo.txt"
