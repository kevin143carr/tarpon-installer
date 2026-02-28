#!/usr/bin/env sh
set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
REPO_ROOT=$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd)

cd "$REPO_ROOT"

rm -rf build/macos dist/macos

PYTHON_CMD=python
if ! command -v "$PYTHON_CMD" >/dev/null 2>&1; then
  PYTHON_CMD=python3
fi

"$PYTHON_CMD" -m PyInstaller \
  --noconfirm \
  --clean \
  --onefile \
  --name tarpon_installer \
  --distpath dist/macos \
  --workpath build/macos \
  --specpath build/macos \
  --hidden-import PIL._tkinter_finder \
  --add-data "$REPO_ROOT/assets/icons/tarpon_installer_image.png:assets/icons" \
  --add-data "$REPO_ROOT/assets/icons/tarpon_installer.ico:assets/icons" \
  tarpon_installer.py

echo "Built dist/macos/tarpon_installer"
