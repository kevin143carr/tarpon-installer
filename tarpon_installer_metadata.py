import os
import sys


APP_NAME = "tarpon_installer"
VERSION = "5.0.3b6"


def runtime_base_path() -> str:
    meipass = getattr(sys, "_MEIPASS", None)
    if meipass:
        return meipass

    module_base = os.path.dirname(os.path.abspath(__file__))
    if os.path.isdir(os.path.join(module_base, "assets")):
        return module_base

    if getattr(sys, "frozen", False):
        return os.path.dirname(os.path.abspath(sys.executable))

    return module_base


def resource_path(relative_path: str) -> str:
    return os.path.join(runtime_base_path(), relative_path)
