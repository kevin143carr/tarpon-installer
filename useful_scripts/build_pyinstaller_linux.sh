#!/usr/bin/env sh
set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
REPO_ROOT=$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd)

cd "$REPO_ROOT"

rm -rf build/linux dist/linux

python3 -m PyInstaller \
  --noconfirm \
  --clean \
  --onefile \
  --name tarpon_installer \
  --distpath dist/linux \
  --workpath build/linux \
  --specpath build/linux \
  --hidden-import PIL._tkinter_finder \
  --add-data "assets/icons/tarpon_installer_image.png:assets/icons" \
  --add-data "assets/icons/tarpon_installer.ico:assets/icons" \
  tarpon_installer.py

echo "Built dist/linux/tarpon_installer"
