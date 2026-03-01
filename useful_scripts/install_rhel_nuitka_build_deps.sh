#!/usr/bin/env sh
set -eu

PKG_MANAGER=dnf
if ! command -v "$PKG_MANAGER" >/dev/null 2>&1; then
  PKG_MANAGER=microdnf
fi

"$PKG_MANAGER" install -y \
  findutils \
  gcc \
  gcc-c++ \
  make \
  patchelf \
  tk \
  tk-devel \
  unzip \
  which \
  zip

if ! python -c "import tkinter" >/dev/null 2>&1; then
  for tkinter_pkg in python3-tkinter python3.11-tkinter; do
    if "$PKG_MANAGER" install -y "$tkinter_pkg"; then
      break
    fi
  done
fi

python -c "import tkinter"
