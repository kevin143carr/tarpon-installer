from pathlib import Path

from useful_scripts.build_nuitka_release import create_pyinstaller_version_file, windows_version_tuple


def test_windows_version_tuple_supports_prerelease_suffix() -> None:
    assert windows_version_tuple("5.0.3b5") == (5, 0, 3, 5)


def test_create_pyinstaller_version_file_uses_display_version(tmp_path: Path) -> None:
    version_file = create_pyinstaller_version_file(tmp_path, "5.0.3b5")
    contents = version_file.read_text(encoding="utf-8")

    assert "filevers=(5, 0, 3, 5)" in contents
    assert "prodvers=(5, 0, 3, 5)" in contents
    assert "StringStruct('FileVersion', '5.0.3b5')" in contents
    assert "StringStruct('ProductVersion', '5.0.3b5')" in contents


def test_windows_pyinstaller_script_uses_release_builder() -> None:
    script_contents = Path("useful_scripts/build_pyinstaller_windows.bat").read_text(encoding="utf-8")
    assert "build_pyinstaller_release.py" in script_contents
