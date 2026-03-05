#!/usr/bin/env python3
import sys

from build_nuitka_release import main as build_release_main


def main() -> int:
    argv = list(sys.argv[1:])
    if "--backend" in argv:
        raise SystemExit("Do not pass --backend to build_pyinstaller_release.py; it always uses pyinstaller.")
    return build_release_main([*argv, "--backend", "pyinstaller"])


if __name__ == "__main__":
    raise SystemExit(main())
