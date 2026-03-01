#!/usr/bin/env sh
set -eu

PKG_MANAGER=dnf
if ! command -v "$PKG_MANAGER" >/dev/null 2>&1; then
  PKG_MANAGER=microdnf
fi

PATCHELF_VERSION=0.18.0

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

install_patchelf_from_release() {
  python - <<'PY'
import io
import os
import stat
import tarfile
import urllib.request

version = os.environ["PATCHELF_VERSION"]
arch = os.environ["PATCHELF_ARCH"]
url = f"https://github.com/NixOS/patchelf/releases/download/{version}/patchelf-{version}-{arch}.tar.gz"

with urllib.request.urlopen(url) as response:
    archive_bytes = response.read()

with tarfile.open(fileobj=io.BytesIO(archive_bytes), mode="r:gz") as archive:
    member = next(member for member in archive.getmembers() if member.name.endswith("/bin/patchelf"))
    extracted = archive.extractfile(member)
    if extracted is None:
        raise SystemExit("Could not extract patchelf binary from upstream release archive")
    target_path = "/usr/local/bin/patchelf"
    with open(target_path, "wb") as target_file:
        target_file.write(extracted.read())
    os.chmod(target_path, os.stat(target_path).st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
PY
}

ensure_patchelf() {
  arch_name=$(uname -m)
  case "$arch_name" in
    x86_64) patchelf_arch=x86_64 ;;
    aarch64) patchelf_arch=aarch64 ;;
    *)
      echo "Unsupported architecture for patchelf release download: $arch_name"
      return 1
      ;;
  esac

  if command -v patchelf >/dev/null 2>&1; then
    return 0
  fi

  try_install_optional patchelf

  if command -v patchelf >/dev/null 2>&1; then
    return 0
  fi

  PATCHELF_ARCH=$patchelf_arch PATCHELF_VERSION=$PATCHELF_VERSION install_patchelf_from_release
  command -v patchelf >/dev/null 2>&1
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

try_install_optional tk-devel
ensure_patchelf

if ! python -c "import tkinter" >/dev/null 2>&1; then
  for tkinter_pkg in python3.11-tkinter python3-tkinter; do
    if install_if_available "$tkinter_pkg"; then
      break
    fi
  done
fi

python -c "import tkinter"
