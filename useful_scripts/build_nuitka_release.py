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


def binary_stem() -> str:
    return "tarpon_installer"


def run_command(command: list[str]) -> None:
    subprocess.run(command, cwd=REPO_ROOT, check=True)


def windows_version_tuple(version: str) -> tuple[int, int, int, int]:
    parts = [int(part) for part in version.split(".")]
    while len(parts) < 4:
        parts.append(0)
    return tuple(parts[:4])


def create_pyinstaller_version_file(output_dir: Path, version: str) -> Path:
    version_file = output_dir / "pyinstaller_version_info.txt"
    version_tuple = windows_version_tuple(version)
    version_commas = ", ".join(str(part) for part in version_tuple)
    version_dots = ".".join(str(part) for part in version_tuple)
    version_file.write_text(
        """VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=({version_commas}),
    prodvers=({version_commas}),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo([
      StringTable(
        '040904B0',
        [
          StringStruct('CompanyName', 'Tarpon Installer'),
          StringStruct('FileDescription', 'Tarpon Installer'),
          StringStruct('FileVersion', '{version_dots}'),
          StringStruct('InternalName', 'tarpon_installer'),
          StringStruct('OriginalFilename', 'tarpon_installer.exe'),
          StringStruct('ProductName', 'Tarpon Installer'),
          StringStruct('ProductVersion', '{version_dots}')
        ]
      )
    ]),
    VarFileInfo([VarStruct('Translation', [1033, 1200])])
  ]
)
""".format(version_commas=version_commas, version_dots=version_dots),
        encoding="utf-8",
    )
    return version_file


def build_nuitka_binary(output_dir: Path, build_mode: str) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    command = [
        detect_python(),
        "-m",
        "nuitka",
        "--assume-yes-for-downloads",
        "--mode={}".format(build_mode),
        "--output-filename={}".format(binary_name()),
        "--output-dir={}".format(output_dir),
        "--remove-output",
        "--enable-plugin=tk-inter",
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
    if build_mode == "standalone":
        return output_dir / "{}.dist".format(binary_name())
    return output_dir / binary_name()


def pyinstaller_data_separator() -> str:
    return ";" if os.name == "nt" else ":"


def build_pyinstaller_binary(output_dir: Path, version: str) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    data_sep = pyinstaller_data_separator()
    command = [
        detect_python(),
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--clean",
        "--onefile",
        "--name",
        binary_stem(),
        "--distpath",
        str(output_dir),
        "--workpath",
        str(output_dir / "build"),
        "--specpath",
        str(output_dir / "spec"),
        "--hidden-import",
        "PIL._tkinter_finder",
        "--add-data",
        "{}{}assets/icons".format(ICON_PNG, data_sep),
        "--add-data",
        "{}{}assets/icons".format(ICON_ICO, data_sep),
    ]

    if os.name == "nt":
        version_file = create_pyinstaller_version_file(output_dir, version)
        command.extend(["--version-file", str(version_file)])
        command.extend(["--icon", str(ICON_ICO)])

    command.append(str(ENTRYPOINT))
    run_command(command)
    return output_dir / binary_name()


def build_binary(output_dir: Path, backend: str, build_mode: str, version: str) -> Path:
    if backend == "pyinstaller":
        return build_pyinstaller_binary(output_dir, version)
    return build_nuitka_binary(output_dir, build_mode)


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

    if binary_path.is_dir():
        copy_tree(binary_path, release_dir / binary_path.name)
    else:
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
        description="Build a packaged release zip for tarpon-installer."
    )
    parser.add_argument(
        "--platform-id",
        default=detect_platform(),
        help="Artifact platform suffix, e.g. windows-x86_64 or macos-arm64.",
    )
    parser.add_argument(
        "--build-mode",
        choices=["onefile", "standalone"],
        default="onefile",
        help="Nuitka build mode for the packaged application.",
    )
    parser.add_argument(
        "--backend",
        choices=["nuitka", "pyinstaller"],
        default="nuitka",
        help="Packaging backend to use for the application binary.",
    )
    args = parser.parse_args()

    version = read_version()
    build_root = OUTPUT_ROOT / "build" / args.platform_id

    if build_root.exists():
        shutil.rmtree(build_root)

    binary_path = build_binary(build_root, args.backend, args.build_mode, version)
    archive_path = assemble_release(binary_path, version, args.platform_id)

    print(str(archive_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
