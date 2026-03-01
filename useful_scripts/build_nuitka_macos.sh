#!/usr/bin/env sh
set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
REPO_ROOT=$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd)

cd "$REPO_ROOT"

PYTHON_CMD=python
if ! command -v "$PYTHON_CMD" >/dev/null 2>&1; then
  PYTHON_CMD=python3
fi

PLATFORM_ID=$(uname -m)
case "$PLATFORM_ID" in
  arm64) PLATFORM_ID="macos-arm64" ;;
  x86_64) PLATFORM_ID="macos-x86_64" ;;
  *) PLATFORM_ID="macos-$PLATFORM_ID" ;;
esac

"$PYTHON_CMD" useful_scripts/build_nuitka_release.py --platform-id "$PLATFORM_ID"
