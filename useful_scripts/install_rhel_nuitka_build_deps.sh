#!/usr/bin/env sh
set -eu

PKG_MANAGER=dnf
if ! command -v "$PKG_MANAGER" >/dev/null 2>&1; then
  PKG_MANAGER=microdnf
fi

install_if_available() {
  pkg_name=$1
  if "$PKG_MANAGER" install -y "$pkg_name"; then
    return 0
  fi
  echo "Skipping unavailable package: $pkg_name"
  return 1
}

try_install_optional() {
  pkg_name=$1
  install_if_available "$pkg_name" || true
}

"$PKG_MANAGER" install -y \
  findutils \
  gcc \
  gcc-c++ \
  make \
  tk \
  unzip \
  which \
  zip

try_install_optional patchelf
try_install_optional tk-devel

if ! python -c "import tkinter" >/dev/null 2>&1; then
  for tkinter_pkg in python3.11-tkinter python3-tkinter; do
    if install_if_available "$tkinter_pkg"; then
      break
    fi
  done
fi

python -c "import tkinter"
