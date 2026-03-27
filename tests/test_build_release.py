from pathlib import Path

from useful_scripts.build_nuitka_release import (
    create_pyinstaller_version_file,
    nuitka_output_path,
    windows_version_tuple,
)


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


def test_nuitka_output_path_uses_app_bundle_on_macos(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr("useful_scripts.build_nuitka_release.platform.system", lambda: "Darwin")
    assert nuitka_output_path(tmp_path, "app") == tmp_path / "tarpon_installer.app"


def test_macos_nuitka_script_defaults_to_onefile_mode() -> None:
    script_contents = Path("useful_scripts/build_nuitka_macos.sh").read_text(encoding="utf-8")
    assert "--build-mode onefile" in script_contents


def test_build_artifacts_workflow_includes_experimental_macos_nuitka_jobs() -> None:
    workflow_contents = Path(".github/workflows/build-artifacts.yml").read_text(encoding="utf-8")
    assert "runner: macos-15-intel" in workflow_contents
    assert "platform_id: macos-x86_64" in workflow_contents
    assert "runner: macos-15" in workflow_contents
    assert "platform_id: macos-arm64" in workflow_contents
    assert "build_mode: onefile" in workflow_contents
    assert "experimental: true" in workflow_contents


def test_release_workflow_remains_without_macos_entries() -> None:
    workflow_contents = Path(".github/workflows/release.yml").read_text(encoding="utf-8")
    assert "macos-" not in workflow_contents
