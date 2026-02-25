from configparser import ConfigParser
import logging
from typing import Dict, Mapping


class iniInfo:
    def __init__(self) -> None:
        self.username = ""
        self.password = ""
        self.buildtype = ""
        self.installtype = ""
        self.resources = ""
        self.startinfo = ""
        self.installtitle = ""
        self.logoimage = ""
        self.buttontext = ""
        self.watchdog = False
        self.adminrights = False
        self.files: Dict[str, str] = {}
        self.repo: Dict[str, str] = {}
        self.rpms: Dict[str, str] = {}
        self.actions: Dict[str, str] = {}
        self.modify: Dict[str, str] = {}
        self.finalactions: Dict[str, str] = {}
        self.options: Dict[str, str] = {}
        self.optionvals: Dict[str, str] = {}
        self.userinput: Dict[str, str] = {}
        self.variables: Dict[str, str] = {}
        self.returnvars: Dict[str, str] = {}
        self.themename = "superhero"

    def _require_section(self, config: ConfigParser, name: str) -> Mapping[str, str]:
        if not config.has_section(name):
            raise KeyError(f"[{name}] section")
        return config[name]

    def _require_option(self, section: Mapping[str, str], name: str) -> str:
        if name not in section:
            raise KeyError(f"'{name}' option")
        return section[name]

    def _parse_bool(self, section: Mapping[str, str], name: str) -> bool:
        value = self._require_option(section, name)
        return value.strip().lower() in {"1", "true", "yes", "on"}

    def _section_items(self, config: ConfigParser, name: str) -> Dict[str, str]:
        self._require_section(config, name)
        return dict(config.items(name, raw=True))

    def readConfigFile(self, configfile: str) -> None:
        logger = logging.getLogger("logger")
        config_object = ConfigParser(interpolation=None)
        config_object.optionxform = str

        config_object.read(configfile)

        try:
            startup = self._require_section(config_object, "STARTUP")
            self.startinfo = self._require_option(startup, "startupinfo")
            self.installtitle = self._require_option(startup, "installtitle")
            self.logoimage = self._require_option(startup, "logoimg")
            self.buttontext = self._require_option(startup, "buttontext")
            self.watchdog = self._parse_bool(startup, "watchdog")
            self.adminrights = self._parse_bool(startup, "adminrights")
            self.themename = self._require_option(startup, "themename")
        except Exception as ex:
            logger.error(ex)
            raise SystemExit("Missing keyword {} in the [STARTUP] section".format(ex))

        try:
            userinfo = self._require_section(config_object, "USERINFO")
            build = self._require_section(config_object, "BUILD")
            self.resources = self._require_option(build, "resources")
            self.files = self._section_items(config_object, "FILES")
            self.username = self._require_option(userinfo, "username")
            self.password = self._require_option(userinfo, "password")
            self.buildtype = self._require_option(build, "buildtype")
            self.installtype = self._require_option(build, "installtype")
            self.repo = self._section_items(config_object, "REPO")
            self.rpms = self._section_items(config_object, "RPM")
            self.actions = self._section_items(config_object, "ACTIONS")
            self.modify = self._section_items(config_object, "MODIFY")
            self.finalactions = self._section_items(config_object, "FINAL")
            self.options = self._section_items(config_object, "OPTIONS")
            self.userinput = self._section_items(config_object, "USERINPUT")
            self.variables = self._section_items(config_object, "VARIABLES")
        except Exception as ex:
            logger.error(ex)
            raise SystemExit(
                "Missing keyword in .ini file. Check your .ini file for the following: {}".format(ex)
            )
