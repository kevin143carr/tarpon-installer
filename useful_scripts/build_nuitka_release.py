#!/usr/bin/env python3
import argparse
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile


REPO_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_ROOT = REPO_ROOT / "dist" / "nuitka"
ENTRYPOINT = REPO_ROOT / "tarpon_installer.py"
ICON_PNG = REPO_ROOT / "assets" / "icons" / "tarpon_installer_image.png"
ICON_ICO = REPO_ROOT / "assets" / "icons" / "tarpon_installer.ico"
INCLUDED_RELEASE_DIRS = [
    "assets",
    "example-ini-files",
    "sample-python-scripts",
]
INCLUDED_RELEASE_FILES = []
NON_BUILD_USEFUL_SCRIPTS = [
    "remove_comma.bat",
    "remove_newline.bat",
    "search_and_replace.bat",
]


def read_version() -> str:
    namespace = {}
    metadata_path = REPO_ROOT / "tarpon_installer_metadata.py"
    exec(metadata_path.read_text(encoding="utf-8"), namespace)
    return namespace["VERSION"]


def detect_python() -> str:
    return sys.executable or "python"


def detect_platform() -> str:
    machine = platform.machine().lower()
    system = platform.system().lower()

    platform_name = {
        "darwin": "macos",
        "linux": "linux",
        "windows": "windows",
    }.get(system, system)

    arch_name = {
        "amd64": "x86_64",
        "x86_64": "x86_64",
        "x64": "x86_64",
        "arm64": "arm64",
        "aarch64": "arm64",
    }.get(machine, machine)

    return "{}-{}".format(platform_name, arch_name)


def binary_name() -> str:
    return "tarpon_installer.exe" if os.name == "nt" else "tarpon_installer"


def run_command(command: list[str]) -> None:
    subprocess.run(command, cwd=REPO_ROOT, check=True)


def build_binary(output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    command = [
        detect_python(),
        "-m",
        "nuitka",
        "--assume-yes-for-downloads",
        "--mode=onefile",
        "--output-filename={}".format(binary_name()),
        "--output-dir={}".format(output_dir),
        "--remove-output",
        "--include-module=PIL._tkinter_finder",
        "--include-package-data=ttkbootstrap",
        "--include-data-dir={}=assets".format(REPO_ROOT / "assets"),
    ]

    if os.name == "nt":
        command.append("--windows-icon-from-ico={}".format(ICON_ICO))
        command.append("--windows-console-mode=force")
    elif platform.system() == "Darwin":
        command.append("--macos-app-icon={}".format(ICON_PNG))

    command.append(str(ENTRYPOINT))
    run_command(command)
    return output_dir / binary_name()


def copy_tree(src: Path, dst: Path) -> None:
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst)


def assemble_release(binary_path: Path, version: str, platform_id: str) -> Path:
    release_name = "tarpon-installer-{}-{}".format(version, platform_id)
    release_dir = OUTPUT_ROOT / release_name

    if release_dir.exists():
        shutil.rmtree(release_dir)
    release_dir.mkdir(parents=True)

    shutil.copy2(binary_path, release_dir / binary_path.name)

    for relative_dir in INCLUDED_RELEASE_DIRS:
        copy_tree(REPO_ROOT / relative_dir, release_dir / relative_dir)

    useful_scripts_dir = release_dir / "useful_scripts"
    useful_scripts_dir.mkdir()
    for script_name in NON_BUILD_USEFUL_SCRIPTS:
        shutil.copy2(REPO_ROOT / "useful_scripts" / script_name, useful_scripts_dir / script_name)

    for relative_file in INCLUDED_RELEASE_FILES:
        source = REPO_ROOT / relative_file
        destination = release_dir / relative_file
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)

    archive_path = OUTPUT_ROOT / "{}.zip".format(release_name)
    if archive_path.exists():
        archive_path.unlink()

    with ZipFile(archive_path, "w", compression=ZIP_DEFLATED) as archive:
        for file_path in sorted(release_dir.rglob("*")):
            if file_path.is_file():
                arcname = Path(release_name) / file_path.relative_to(release_dir)
                archive.write(file_path, arcname=arcname)

    return archive_path


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build a Nuitka onefile release zip for tarpon-installer."
    )
    parser.add_argument(
        "--platform-id",
        default=detect_platform(),
        help="Artifact platform suffix, e.g. windows-x86_64 or macos-arm64.",
    )
    args = parser.parse_args()

    version = read_version()
    build_root = OUTPUT_ROOT / "build" / args.platform_id

    if build_root.exists():
        shutil.rmtree(build_root)

    binary_path = build_binary(build_root)
    archive_path = assemble_release(binary_path, version, args.platform_id)

    print(str(archive_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
