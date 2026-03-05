import re
from pathlib import Path

from tarpon_installer_metadata import VERSION, resource_path, runtime_base_path


def test_version_string_is_semver_like() -> None:
    assert re.fullmatch(r"\d+\.\d+\.\d+((a|b|rc)\d+)?", VERSION)


def test_runtime_base_path_points_at_repo_root_in_source_runs() -> None:
    base_path = Path(runtime_base_path())

    assert base_path == Path(__file__).resolve().parents[1]
    assert (base_path / "assets").is_dir()


def test_resource_path_resolves_repo_relative_assets() -> None:
    icon_path = Path(resource_path("assets/icons/tarpon_installer.ico"))

    assert icon_path.is_file()
