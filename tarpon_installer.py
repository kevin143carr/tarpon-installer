import argparse
import sys
import ctypes
from elevate import elevate
from managers.rpmmanager import RpmManager
from managers.guimanager import GuiManager
from iniinfo import iniInfo
from task import Task
import os.path
from os import path
import os
import platform
import tkinter as tk
import ttkbootstrap as ttk
import threading
import logging
from typing import List
from ui_thread import set_var, quit_window

VERSION = "5.0.0"
DEFAULT_CONFIGFILE = "config.ini"

class mainClass:
    """Using a main class because of the amount of work that needs to be done initially."""
    display_dict = {}
    rpm_manager = RpmManager()
    gui_manager = GuiManager()

    window = None
    logger = logging.getLogger("logger")

    def installThread(self, ini_info, InstallButton, window) -> None:
        InstallButton['state'] = tk.DISABLED
        installthread = threading.Thread(target=self.beginInstall, args=(ini_info, window))
        installthread.start()

    def main(self, ini_info: iniInfo) -> None:
        """Main entry point for the GUI workflow."""
        if sys.version_info[:3] < (3,9):
            self.window = tk.Tk()
        else:
            self.window = ttk.Window(themename=ini_info.themename)

        self.logger.info("******************************************************************")
        self.logger.info("******************************************************************")
        self.logger.info(" ><###> Tarpon Installer <###>< is an open source install creator.")
        self.logger.info(" It has been made open source under the MIT Licensing agreement.")
        self.logger.info(" Feel free to use, modify and distribute")
        self.logger.info(" as needed, as long as this banner remains in place")
        self.logger.info("*  VERSION {}".format(VERSION))
        self.logger.info("******************************************************************")
        self.logger.info("******************************************************************")

        functiontitle = 'Important Installation Information Needed'

        self.gui_manager.buildGUI(self.window, functiontitle, ini_info, self.installThread)
        self.window.mainloop()

    def beginInstall(self, ini_info: iniInfo, window) -> None:

        for key in self.display_dict:
            if "Username" in key:
                ini_info.username = self.display_dict[key].get()
            if "Password" in key:
                ini_info.password = self.display_dict[key].get()

        task = Task(ini_info)

        # if Remote Type then login via SSH
        if ini_info.installtype == 'REMOTE': 
            task.loginSSH()

        try:
            # Repos and RPMs are Linux only
 
            # Remote Install
            #if ini_info.buildtype == 'LINUX' and ini_info.installtype == 'REMOTE':
                #task.installRemoteRepo(ini_info.resources, ini_info.repo)
                #self.rpm_manager.installRPMsRemote(ini_info.resources, ini_info.rpms)

            # Local Install
            if ini_info.buildtype == 'LINUX':
                set_var(window, self.gui_manager.section, "SECTION: INSTALLING RPMs")
                self.rpm_manager.installLocalRPMs(window, self.gui_manager.bar, self.gui_manager.taskitem, ini_info.resources, ini_info.rpms, ini_info.watchdog)

            set_var(window, self.gui_manager.section, "SECTION: COPYING FILES")
            task.copyFromResources(window, self.gui_manager.bar, self.gui_manager.taskitem, ini_info)

            set_var(window, self.gui_manager.section, "SECTION: ACTIONS")
            set_var(window, self.gui_manager.taskitem, "")
            task.doActions(window, self.gui_manager.bar, self.gui_manager.taskitem, ini_info)

            set_var(window, self.gui_manager.section, "SECTION: MODIFYING FILES")
            set_var(window, self.gui_manager.taskitem, "")
            task.modifyFiles(window, self.gui_manager.bar, self.gui_manager.taskitem, ini_info)

            set_var(window, self.gui_manager.section, "SECTION: FINAL ACTIONS")
            set_var(window, self.gui_manager.taskitem, "")
            task.finalActions(window, self.gui_manager.bar, self.gui_manager.taskitem, ini_info)
            quit_window(self.window)
            
                
        except Exception as ex:
            self.logger.error(ex)


def parse_args(argv: List[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="tarpon_installer",
        description="Tarpon Installer - config-driven installer for Windows/Linux."
    )
    parser.add_argument(
        "-t",
        "--configfile",
        default=DEFAULT_CONFIGFILE,
        help="Path to configuration .ini file (default: config.ini).",
    )
    parser.add_argument(
        "-d",
        "--debuglevel",
        choices=["INFO", "DEBUG"],
        default="INFO",
        help="Logging level (default: INFO).",
    )
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s {}".format(VERSION),
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Run without GUI and execute the .ini directly.",
    )
    parser.add_argument(
        "--userinput",
        action="append",
        default=[],
        metavar="KEY=VALUE",
        help="Set a USERINPUT value when running headless. May be used multiple times.",
    )
    parser.add_argument(
        "--option",
        action="append",
        default=[],
        metavar="OPTION",
        help="Enable an option when running headless. May be used multiple times.",
    )
    parser.add_argument(
        "--strict-tokens",
        action="store_true",
        help="Fail headless runs if unresolved %tokens% remain.",
    )
    return parser.parse_args(argv)


def setup_logging(configfile: str, debuglevel: str) -> None:
    level = logging.DEBUG if debuglevel == "DEBUG" else logging.INFO
    logging.basicConfig(
        filename="{}.log".format(os.path.splitext(configfile)[0]),
        filemode="w",
        level=level,
    )


def is_admin() -> bool:
    try:
        is_admin_value = (os.getuid() == 0)
    except AttributeError:
        is_admin_value = ctypes.windll.shell32.IsUserAnAdmin() != 0
    return is_admin_value


def ensure_admin(ini_info: iniInfo, logger: logging.Logger) -> None:
    if is_admin():
        logger.info("Executing as Administrator")
        return

    logger.info("Elevating Permissions because Administrator = False")
    if ini_info.adminrights is True:
        if platform.system() == "Windows":
            elevate(show_console=True)
        else:
            logger.error("This install requires admin/root privelages")
            raise SystemExit(
                "Error - This install requires admin/root privelages. "
                "Set [adminrights] = False in the .ini file if not needed."
            )


class HeadlessVar:
    def __init__(self, value: str = "") -> None:
        self._value = value

    def get(self) -> str:
        return self._value

    def set(self, value: str) -> None:
        self._value = value


class DummyWindow:
    def update_idletasks(self) -> None:
        return


class DummyBar:
    def __setitem__(self, key: str, value) -> None:
        return


def parse_userinput_overrides(values: List[str]) -> dict:
    overrides = {}
    for entry in values:
        if "=" not in entry:
            raise ValueError(f"Invalid --userinput '{entry}'. Expected KEY=VALUE.")
        key, value = entry.split("=", 1)
        overrides[key] = value
    return overrides


def setup_headless_inputs(
    ini_info: iniInfo,
    userinput_overrides: dict,
    enabled_options: List[str],
    logger: logging.Logger,
) -> None:
    for key in ini_info.userinput:
        ini_info.userinput[key] = HeadlessVar(userinput_overrides.get(key, ""))

    for key in userinput_overrides:
        if key not in ini_info.userinput:
            logger.warning("Headless USERINPUT override provided but key not found: %s", key)

    for key in ini_info.options:
        ini_info.optionvals[key] = HeadlessVar("1" if key in enabled_options else "0")

    for key in enabled_options:
        if key not in ini_info.options:
            logger.warning("Headless option enabled but key not found: %s", key)


def _find_unresolved_tokens(value: str) -> List[str]:
    tokens = []
    start = 0
    while True:
        start = value.find("%", start)
        if start == -1:
            break
        end = value.find("%", start + 1)
        if end == -1:
            break
        token = value[start + 1:end]
        if token:
            tokens.append(token)
        start = end + 1
    return tokens


def _collect_declared_returnvars(ini_info: iniInfo) -> set:
    declared = set()
    sources = [
        ini_info.actions,
        ini_info.finalactions,
    ]
    for source in sources:
        for value in source.values():
            if "POPLIST::" in str(value):
                parts = str(value).split("::")
                if len(parts) >= 5:
                    declared.add(parts[4].strip())
    return declared


def _collect_unresolved_tokens(ini_info: iniInfo, declared_returnvars: set) -> List[str]:
    unresolved = set()
    sources = [
        ini_info.files,
        ini_info.actions,
        ini_info.modify,
        ini_info.finalactions,
    ]
    for source in sources:
        for value in source.values():
            for token in _find_unresolved_tokens(str(value)):
                if token == "username" and getattr(ini_info, "username", ""):
                    continue
                if token in ini_info.userinput:
                    continue
                elif token in ini_info.variables:
                    continue
                elif token in ini_info.returnvars:
                    continue
                elif token in declared_returnvars:
                    continue
                else:
                    unresolved.add(token)
    return sorted(unresolved)


def run_headless(ini_info: iniInfo, logger: logging.Logger) -> None:
    window = DummyWindow()
    bar = DummyBar()
    taskitem = HeadlessVar()

    task = Task(ini_info)
    if ini_info.installtype == "REMOTE":
        task.loginSSH()

    if ini_info.buildtype == "LINUX":
        logger.info("SECTION: INSTALLING RPMs")
        RpmManager().installLocalRPMs(
            window, bar, taskitem, ini_info.resources, ini_info.rpms, ini_info.watchdog
        )

    logger.info("SECTION: COPYING FILES")
    task.copyFromResources(window, bar, taskitem, ini_info)

    logger.info("SECTION: ACTIONS")
    task.doActions(window, bar, taskitem, ini_info)

    logger.info("SECTION: MODIFYING FILES")
    task.modifyFiles(window, bar, taskitem, ini_info)

    logger.info("SECTION: FINAL ACTIONS")
    task.finalActions(window, bar, taskitem, ini_info)


def main(argv: List[str]) -> int:
    # During elevation an additional arg of the .exe itself is added and messes things up.
    filtered_args = [arg for arg in argv if "tarpon_installer.exe" not in arg]
    args = parse_args(filtered_args)

    if path.exists(args.configfile) is False:
        print("ERROR: ><###> Cannot Find Configuration File - '{}'.".format(args.configfile))
        return 2

    setup_logging(args.configfile, args.debuglevel)
    logger = logging.getLogger("logger")

    ini_info = iniInfo()
    ini_info.readConfigFile(args.configfile)

    ensure_admin(ini_info, logger)

    if args.headless:
        os.environ["TARPL_HEADLESS"] = "1"
        try:
            userinput_overrides = parse_userinput_overrides(args.userinput)
        except ValueError as ex:
            logger.error(str(ex))
            return 2

        setup_headless_inputs(ini_info, userinput_overrides, args.option, logger)
        if args.strict_tokens:
            declared_returnvars = _collect_declared_returnvars(ini_info)
            unresolved = _collect_unresolved_tokens(ini_info, declared_returnvars)
            if unresolved:
                logger.error("Unresolved tokens: %s", ", ".join(unresolved))
                return 2
        run_headless(ini_info, logger)
    else:
        app = mainClass()
        app.main(ini_info)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
