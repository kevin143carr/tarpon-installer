import argparse
import sys
import ctypes
from configparser import ConfigParser
from dataclasses import dataclass
from datetime import datetime
from elevate import elevate
from managers.rpmmanager import RpmManager
from managers.guimanager import GuiManager
from iniinfo import (
    iniInfo,
    resolve_enabled_options,
    is_local_install_type,
    is_remote_linux_install_type,
    is_remote_windows_install_type,
)
from task import Task
import os.path
from os import path
import os
import platform
from pathlib import Path
import tkinter as tk
import ttkbootstrap as ttk
import threading
import logging
from typing import List, Optional
from stringutilities import StringUtilities
from tarpl.tarplapi import TarpL
from tarpon_installer_metadata import VERSION, resource_path
from ui_thread import call_on_ui_thread, set_var, quit_window

DEFAULT_CONFIGFILE = "config.ini"
DEFAULT_ICON_PNG = "assets/icons/tarpon_installer_image.png"
DEFAULT_ICON_ICO = "assets/icons/tarpon_installer.ico"
DISCOVERY_SKIP_DIRS = {
    ".git",
    ".venv",
    "__pycache__",
    "build",
    "dist",
    "node_modules",
    "site-packages",
}
REQUIRED_TARPON_SECTIONS = (
    "STARTUP",
    "USERINFO",
    "BUILD",
    "FILES",
    "REPO",
    "RPM",
    "ACTIONS",
    "MODIFY",
    "FINAL",
    "OPTIONS",
    "USERINPUT",
    "VARIABLES",
)
REQUIRED_TARPON_KEYS = {
    "STARTUP": {"usegui", "watchdog", "adminrights"},
    "BUILD": {"buildtype", "installtype", "resources"},
    "USERINFO": {"username", "password"},
}


@dataclass(frozen=True)
class InstallerCandidate:
    config_path: str
    title: str
    description: str


def print_banner(file=None) -> None:
    print("******************************************************************", file=file)
    print("******************************************************************", file=file)
    print(" ><###> Tarpon Installer <###>< is an open source install creator.", file=file)
    print(" It has been made open source under the MIT Licensing agreement.", file=file)
    print(" Feel free to use, modify and distribute", file=file)
    print(" as needed, as long as this banner remains in place", file=file)
    print("*  VERSION {}".format(VERSION), file=file)
    print("******************************************************************", file=file)
    print("******************************************************************", file=file)


class BannerArgumentParser(argparse.ArgumentParser):
    def print_help(self, file=None) -> None:
        print_banner(file=file)
        super().print_help(file=file)


class FinalErrorCollector(logging.Handler):
    def __init__(self, limit: int = 3) -> None:
        super().__init__(level=logging.ERROR)
        self.limit = limit
        self.messages = []
        self._lock = threading.Lock()

    def emit(self, record: logging.LogRecord) -> None:
        message = self.format(record) if self.formatter else record.getMessage()
        with self._lock:
            if len(self.messages) >= self.limit:
                return
            self.messages.append(message)

    def get_messages(self) -> List[str]:
        with self._lock:
            return list(self.messages)

class mainClass:
    """Using a main class because of the amount of work that needs to be done initially."""
    display_dict = {}
    rpm_manager = RpmManager()
    gui_manager = GuiManager()

    window = None
    logger = logging.getLogger("logger")
    final_error_collector = None

    def _set_current_section(self, window, section_name: str) -> None:
        set_var(window, self.gui_manager.section, "[{}]".format(section_name))

    def _set_app_icon(self, ini_info: iniInfo) -> None:
        """Set a custom window/app icon when icon assets are available."""
        if self.window is None:
            return

        icon_png = ini_info.iconpng
        if not icon_png:
            icon_png = resource_path(DEFAULT_ICON_PNG)
        elif not os.path.isabs(icon_png):
            icon_png = os.path.join(os.getcwd(), icon_png)

        icon_ico = ini_info.iconico
        if not icon_ico:
            icon_ico = resource_path(DEFAULT_ICON_ICO)
        elif not os.path.isabs(icon_ico):
            icon_ico = os.path.join(os.getcwd(), icon_ico)

        try:
            if os.path.exists(icon_png):
                app_icon = tk.PhotoImage(file=icon_png)
                self.window.iconphoto(True, app_icon)
                # Keep a reference so Tk doesn't garbage-collect the icon.
                setattr(self.window, "_app_icon_ref", app_icon)
        except Exception as ex:
            self.logger.warning("Could not apply PNG app icon: %s", ex)

        if platform.system() == "Windows":
            try:
                if os.path.exists(icon_ico):
                    self.window.iconbitmap(default=icon_ico)
            except Exception as ex:
                self.logger.warning("Could not apply ICO app icon: %s", ex)

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

        self._set_app_icon(ini_info)

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
        if is_remote_windows_install_type(ini_info.installtype):
            raise NotImplementedError("installtype REMOTEWINDOWS is not implemented yet.")

        if is_remote_linux_install_type(ini_info.installtype):
            task.loginSSH()

        diagnostics = []
        diagnostics_ran = False

        try:
            # Repos and RPMs are Linux only
 
            # Remote Linux install
            if ini_info.buildtype == 'LINUX' and is_remote_linux_install_type(ini_info.installtype):
                self._set_current_section(window, "RPM")
                self.rpm_manager.installRemoteRPMs(task.ssh, ini_info.resources, ini_info.rpms)

            # Local Install
            if ini_info.buildtype == 'LINUX' and is_local_install_type(ini_info.installtype):
                self._set_current_section(window, "RPM")
                self.rpm_manager.installLocalRPMs(window, self.gui_manager.bar, self.gui_manager.taskitem, ini_info.resources, ini_info.rpms, ini_info.watchdog, ini_info.process_timeout)

            self._set_current_section(window, "FILES")
            task.copyFromResources(window, self.gui_manager.bar, self.gui_manager.taskitem, ini_info)

            self._set_current_section(window, "ACTIONS")
            set_var(window, self.gui_manager.taskitem, "")
            task.doActions(window, self.gui_manager.bar, self.gui_manager.taskitem, ini_info)

            self._set_current_section(window, "MODIFY")
            set_var(window, self.gui_manager.taskitem, "")
            task.modifyFiles(window, self.gui_manager.bar, self.gui_manager.taskitem, ini_info)

            self._set_current_section(window, "FINAL")
            set_var(window, self.gui_manager.taskitem, "")
            task.finalActions(window, self.gui_manager.bar, self.gui_manager.taskitem, ini_info)
            if ini_info.usediagnostics:
                self._set_current_section(window, "DIAGNOSTICS")
                set_var(window, self.gui_manager.taskitem, "")
                diagnostics = task.runDiagnostics(window, self.gui_manager.bar, self.gui_manager.taskitem, ini_info)
                diagnostics_ran = True
        except Exception as ex:
            self.logger.error(ex)
        finally:
            if ini_info.usediagnostics and not diagnostics_ran:
                try:
                    self._set_current_section(window, "DIAGNOSTICS")
                    set_var(window, self.gui_manager.taskitem, "")
                    diagnostics = task.runDiagnostics(window, self.gui_manager.bar, self.gui_manager.taskitem, ini_info)
                    diagnostics_ran = True
                except Exception as diag_ex:
                    self.logger.error("Diagnostics failed: %s", diag_ex)

            if diagnostics:
                call_on_ui_thread(
                    self.window,
                    self.gui_manager.showDiagnosticsDialog,
                    self.window,
                    diagnostics,
                )

            if ini_info.displayfinalerrors and self.final_error_collector is not None:
                collected_errors = self.final_error_collector.get_messages()
                if collected_errors:
                    call_on_ui_thread(
                        self.window,
                        self.gui_manager.showFinalErrorsDialog,
                        self.window,
                        collected_errors,
                    )
            quit_window(self.window)


def build_parser() -> argparse.ArgumentParser:
    parser = BannerArgumentParser(
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
        "--userinput",
        action="append",
        default=[],
        metavar="KEY=VALUE",
        help="Set a USERINPUT value when [STARTUP] usegui = False. May be used multiple times.",
    )
    parser.add_argument(
        "--option",
        action="append",
        default=[],
        metavar="OPTION",
        help="Enable an option when [STARTUP] usegui = False. May be used multiple times.",
    )
    parser.add_argument(
        "--strict-tokens",
        action="store_true",
        help="Fail non-GUI runs if unresolved %%tokens%% remain.",
    )
    parser.add_argument(
        "--liveviewlog",
        action="store_true",
        help="When [STARTUP] usegui = False, also stream log output to the terminal.",
    )
    parser.add_argument(
        "--selectinstall",
        action="store_true",
        help="Discover Tarpon installer .ini files and show a selection popup before running.",
    )
    parser.add_argument(
        "--selectinstalldir",
        default="",
        metavar="DIR",
        help="Directory to scan for Tarpon installer .ini files when using --selectinstall.",
    )
    return parser


def parse_args(argv: List[str]) -> argparse.Namespace:
    return build_parser().parse_args(argv)


def _is_tarpon_installer_config(config: ConfigParser) -> bool:
    for section in REQUIRED_TARPON_SECTIONS:
        if not config.has_section(section):
            return False
    for section, keys in REQUIRED_TARPON_KEYS.items():
        section_obj = config[section]
        for key in keys:
            if key not in section_obj:
                return False
    return True


def discover_tarpon_installer_configs(search_root: str) -> List[InstallerCandidate]:
    root = Path(search_root).resolve()
    if not root.exists():
        return []

    matches: List[InstallerCandidate] = []
    for ini_path in sorted(root.rglob("*.ini")):
        if any(part in DISCOVERY_SKIP_DIRS for part in ini_path.parts):
            continue

        config = ConfigParser(interpolation=None)
        config.optionxform = str
        try:
            config.read(ini_path, encoding="utf-8")
        except Exception:
            continue

        if not _is_tarpon_installer_config(config):
            continue

        startup = config["STARTUP"]
        title = startup.get("installtitle", "").strip() or ini_path.stem
        description = startup.get("startupinfo", "").strip()
        matches.append(
            InstallerCandidate(
                config_path=str(ini_path),
                title=title,
                description=description,
            )
        )

    return sorted(matches, key=lambda item: (item.title.lower(), item.config_path.lower()))


def select_tarpon_installer_config(candidates: List[InstallerCandidate]) -> Optional[str]:
    if not candidates:
        return None

    selected = {"index": None}
    root = tk.Tk()
    root.withdraw()
    root.title("Select Tarpon Installer Profile")
    root.geometry("920x520")

    container = tk.Frame(root, padx=12, pady=12)
    container.pack(fill=tk.BOTH, expand=True)

    heading = tk.Label(
        container,
        text="Choose a Tarpon Installer profile before starting",
        anchor="w",
        justify="left",
        font=("Arial", 12, "bold"),
    )
    heading.pack(fill=tk.X, pady=(0, 8))

    list_frame = tk.Frame(container)
    list_frame.pack(fill=tk.BOTH, expand=True)

    scrollbar = tk.Scrollbar(list_frame, orient=tk.VERTICAL)
    listbox = tk.Listbox(
        list_frame,
        yscrollcommand=scrollbar.set,
        exportselection=False,
        activestyle="none",
    )
    scrollbar.config(command=listbox.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    details_var = tk.StringVar()
    details = tk.Label(
        container,
        textvariable=details_var,
        anchor="w",
        justify="left",
        wraplength=880,
    )
    details.pack(fill=tk.X, pady=(10, 8))

    for candidate in candidates:
        summary = candidate.title
        if candidate.description:
            summary = "{} - {}".format(candidate.title, candidate.description)
        listbox.insert(tk.END, summary)

    def update_details(*_args) -> None:
        selection = listbox.curselection()
        if not selection:
            details_var.set("")
            return
        candidate = candidates[selection[0]]
        details_var.set("Path: {}\nDescription: {}".format(candidate.config_path, candidate.description or "(none)"))

    def select_current() -> None:
        selection = listbox.curselection()
        if not selection:
            return
        selected["index"] = selection[0]
        root.destroy()

    def cancel_selection() -> None:
        root.destroy()

    def center_window() -> None:
        root.update_idletasks()
        width = root.winfo_width()
        height = root.winfo_height()
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        pos_x = max(0, (screen_width - width) // 2)
        pos_y = max(0, (screen_height - height) // 2)
        root.geometry("{}x{}+{}+{}".format(width, height, pos_x, pos_y))

    button_frame = tk.Frame(container)
    button_frame.pack(fill=tk.X)
    cancel_button = tk.Button(button_frame, text="Cancel", width=14, command=cancel_selection)
    cancel_button.pack(side=tk.RIGHT, padx=(8, 0))
    select_button = tk.Button(button_frame, text="Use Selected Install", width=20, command=select_current)
    select_button.pack(side=tk.RIGHT)

    listbox.bind("<<ListboxSelect>>", update_details)
    listbox.bind("<Double-Button-1>", lambda _event: select_current())
    root.protocol("WM_DELETE_WINDOW", cancel_selection)

    if candidates:
        listbox.selection_set(0)
        listbox.activate(0)
        update_details()

    center_window()
    root.deiconify()
    root.lift()
    root.after_idle(root.focus_force)
    root.mainloop()

    index = selected["index"]
    if index is None:
        return None
    return candidates[index].config_path


def build_logfile_path(configfile: str) -> str:
    config_base = os.path.splitext(configfile)[0]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return "{}_{}.log".format(config_base, timestamp)


def setup_logging(configfile: str, debuglevel: str, liveviewlog: bool = False) -> None:
    level = logging.DEBUG if debuglevel == "DEBUG" else logging.INFO
    logfile = build_logfile_path(configfile)
    logger = logging.getLogger()
    logger.handlers.clear()
    logger.setLevel(level)
    formatter = logging.Formatter(
        "%(asctime)s %(levelname)s %(name)s: %(message)s",
        "%Y-%m-%d %H:%M:%S",
    )

    file_handler = logging.FileHandler(logfile, mode="w")
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    if liveviewlog:
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setLevel(level)
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)


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


def _print_headless_terminal_block(title: str, message: str) -> None:
    border = "=" * 72
    print()
    print(border)
    print(title)
    print("-" * 72)
    print(message)
    print(border)


def prompt_for_headless_userinput(prompt_text: str) -> str:
    _print_headless_terminal_block("USER INPUT REQUIRED", prompt_text)
    while True:
        try:
            value = input("Enter value: ")
        except EOFError as ex:
            raise SystemExit("Error - No stdin available for required headless USERINPUT.") from ex

        if value.strip() != "":
            return value
        print("A value is required.", file=sys.stderr)


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
    enabled_option_set = resolve_enabled_options(ini_info.options, set(enabled_options))

    for key in ini_info.userinput:
        default_value = ""
        if hasattr(ini_info, "userinput_defaults"):
            default_value = ini_info.userinput_defaults.get(key, "")
        if key in userinput_overrides and userinput_overrides[key] != "":
            value = userinput_overrides[key]
        elif default_value != "":
            value = default_value
        else:
            value = prompt_for_headless_userinput(ini_info.userinput[key])
        ini_info.userinput[key] = HeadlessVar(value)

    for key in userinput_overrides:
        if key not in ini_info.userinput:
            logger.warning("Headless USERINPUT override provided but key not found: %s", key)

    for key in ini_info.options:
        ini_info.optionvals[key] = HeadlessVar("1" if key in enabled_option_set else "0")

    for key in enabled_option_set:
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


def _extract_headless_prompt_entries(ini_info: iniInfo) -> List[str]:
    tarpl = TarpL()
    string_utilities = StringUtilities()
    prompt_entries = []

    for source in (ini_info.actions, ini_info.finalactions):
        for key, value in source.items():
            if key in ini_info.options and ini_info.optionvals.get(key, HeadlessVar("0")).get() == "0":
                continue

            resolved_value = string_utilities.checkForUserVariable(str(value), ini_info)
            while True:
                tarpltype = tarpl.getTarpL(resolved_value)
                if tarpltype != "IFTHENELSE":
                    break
                resolved_value = tarpl.IFTHENELSE(resolved_value, ini_info).rtnvalue

            if tarpltype not in {"YESNO", "MSGBOX", "POPLIST"}:
                continue

            parts = resolved_value.split("::")
            if len(parts) < 2:
                continue
            prompt_entries.append(f"- {tarpltype}: {parts[1].strip()}")

    return prompt_entries


def build_headless_summary_lines(configfile: str, ini_info: iniInfo) -> List[str]:
    enabled_options = sorted(
        key for key, value in ini_info.optionvals.items() if value.get() != "0"
    )
    userinput_defaults = [
        f"- {key} = {ini_info.userinput[key].get()}"
        for key in ini_info.userinput
    ]
    prompt_entries = _extract_headless_prompt_entries(ini_info)

    lines = [
        f"Config file: {configfile}",
        "Mode: headless",
        f"Install title: {ini_info.installtitle}",
        f"Action prompt: {ini_info.buttontext}",
        f"Build type: {ini_info.buildtype}",
        f"Install type: {ini_info.installtype}",
        f"Resources: {ini_info.resources}",
        "",
        "Enabled options:",
    ]
    if enabled_options:
        lines.extend(f"- {option}" for option in enabled_options)
    else:
        lines.append("- None")

    lines.extend(["", "User input defaults:"])
    if userinput_defaults:
        lines.extend(userinput_defaults)
    else:
        lines.append("- None")

    lines.extend(["", "Expected user prompts:"])
    if prompt_entries:
        lines.extend(prompt_entries)
    else:
        lines.append("- None")

    lines.extend(["", "Press Enter to begin..."])
    return lines


def show_headless_preflight_summary(configfile: str, ini_info: iniInfo) -> None:
    border = "=" * 72
    print()
    print(border)
    print("HEADLESS RUN SUMMARY")
    print("-" * 72)
    print("\n".join(build_headless_summary_lines(configfile, ini_info)))
    print(border)
    try:
        input()
    except EOFError:
        return


def run_headless(ini_info: iniInfo, logger: logging.Logger) -> None:
    window = DummyWindow()
    bar = DummyBar()
    taskitem = HeadlessVar()

    if ini_info.installtitle:
        logger.info("INSTALL TITLE: %s", ini_info.installtitle)
    if ini_info.startinfo:
        logger.info("STARTUP INFO: %s", ini_info.startinfo)
    if ini_info.buttontext:
        logger.info("ACTION PROMPT: %s", ini_info.buttontext)

    task = Task(ini_info)
    if is_remote_windows_install_type(ini_info.installtype):
        raise NotImplementedError("installtype REMOTEWINDOWS is not implemented yet.")

    if is_remote_linux_install_type(ini_info.installtype):
        task.loginSSH()

    if ini_info.buildtype == "LINUX" and is_local_install_type(ini_info.installtype):
        logger.info("SECTION: INSTALLING RPMs")
        RpmManager().installLocalRPMs(
            window, bar, taskitem, ini_info.resources, ini_info.rpms, ini_info.watchdog, ini_info.process_timeout
        )
    elif ini_info.buildtype == "LINUX" and is_remote_linux_install_type(ini_info.installtype):
        logger.info("SECTION: INSTALLING RPMs (REMOTE)")
        RpmManager().installRemoteRPMs(task.ssh, ini_info.resources, ini_info.rpms)

    logger.info("SECTION: COPYING FILES")
    task.copyFromResources(window, bar, taskitem, ini_info)

    logger.info("SECTION: ACTIONS")
    task.doActions(window, bar, taskitem, ini_info)

    logger.info("SECTION: MODIFYING FILES")
    task.modifyFiles(window, bar, taskitem, ini_info)

    logger.info("SECTION: FINAL ACTIONS")
    task.finalActions(window, bar, taskitem, ini_info)

    if ini_info.usediagnostics:
        logger.info("SECTION: DIAGNOSTICS")
        diagnostics = task.runDiagnostics(window, bar, taskitem, ini_info)
        if diagnostics:
            print()
            print("=" * 72)
            print("DIAGNOSTICS RESULTS")
            print("-" * 72)
            for result in diagnostics:
                print("{} [{}]".format(result["label"], result["status"]))
            print("=" * 72)


def main(argv: List[str]) -> int:
    # During elevation an additional arg of the .exe itself is added and messes things up.
    filtered_args = [arg for arg in argv if "tarpon_installer.exe" not in arg]
    if not filtered_args:
        build_parser().print_help()
        return 0
    args = parse_args(filtered_args)

    if args.selectinstall:
        if not args.selectinstalldir:
            print("ERROR: --selectinstall requires --selectinstalldir DIR.")
            return 2
        candidates = discover_tarpon_installer_configs(args.selectinstalldir)
        if not candidates:
            print("ERROR: No Tarpon installer profiles found under '{}'.".format(args.selectinstalldir))
            return 2
        try:
            selected = select_tarpon_installer_config(candidates)
        except Exception as ex:
            print("ERROR: Could not open installer selection window: {}".format(ex))
            return 2
        if selected is None:
            print("No installer selected. Exiting.")
            return 0
        args.configfile = selected
    elif args.selectinstalldir:
        print("ERROR: --selectinstalldir can only be used with --selectinstall.")
        return 2

    if path.exists(args.configfile) is False:
        print("ERROR: ><###> Cannot Find Configuration File - '{}'.".format(args.configfile))
        return 2

    ini_info = iniInfo()
    ini_info.readConfigFile(args.configfile)
    if is_remote_windows_install_type(ini_info.installtype):
        print("ERROR: installtype REMOTEWINDOWS is not implemented yet.")
        return 2

    setup_logging(args.configfile, args.debuglevel, liveviewlog=(ini_info.usegui is False and args.liveviewlog))
    logger = logging.getLogger("logger")

    ensure_admin(ini_info, logger)

    if ini_info.usegui is False:
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
        show_headless_preflight_summary(args.configfile, ini_info)
        run_headless(ini_info, logger)
    else:
        if args.userinput or args.option or args.strict_tokens or args.liveviewlog:
            logger.warning(
                "Ignoring --userinput/--option/--strict-tokens/--liveviewlog because [STARTUP] usegui is True"
            )
        app = mainClass()
        if ini_info.displayfinalerrors:
            collector = FinalErrorCollector(limit=3)
            logging.getLogger("logger").addHandler(collector)
            app.final_error_collector = collector
        app.main(ini_info)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
