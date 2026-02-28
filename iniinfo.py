from configparser import ConfigParser
import logging
from typing import Dict, Mapping

logger = None


class iniInfo:
    def __init__(self) -> None:
        self.username = ""
        self.password = ""
        self.hostname = ""
        self.buildtype = ""
        self.installtype = ""
        self.resources = ""
        self.startinfo = ""
        self.installtitle = ""
        self.logoimage = ""
        self.iconpng = ""
        self.iconico = ""
        self.buttontext = ""
        self.watchdog = False
        self.adminrights = False
        self.usegui = True
        self.displayfinalerrors = False
        self.files = {}
        self.repo = {}
        self.rpms = {}
        self.actions = {}
        self.modify = {}
        self.finalactions = {}
        self.options = {}
        self.optionvals = {}
        self.userinput = {}
        self.userinput_defaults = {}
        self.variables = {}
        self.returnvars = {}
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

    def _optional_section(self, config: ConfigParser, name: str) -> Mapping[str, str]:
        if config.has_section(name):
            return config[name]
        return {}

    def readConfigFile(self, configfile: str) -> None:
        logger = logging.getLogger("logger")
        config_object = ConfigParser(interpolation=None)
        config_object.optionxform = str

        config_object.read(configfile)

        try:
            config_object.read(configfile)
            startup = config_object["STARTUP"]
            self.usegui = config_object.getboolean("STARTUP", "usegui")
            self.startinfo = startup.get('startupinfo', "")
            self.installtitle = startup.get('installtitle', "Tarpon Installer")
            self.logoimage = startup.get('logoimg', "")
            self.iconpng = startup.get("iconpng", "")
            self.iconico = startup.get("iconico", "")
            self.buttontext = startup.get('buttontext', "Install")
            self.watchdog = config_object.getboolean("STARTUP", "watchdog")
            self.adminrights = config_object.getboolean("STARTUP", "adminrights")
            self.themename = startup.get("themename", "superhero")
            self.displayfinalerrors = startup.get("displayfinalerrors", "").strip().lower() in {"1", "true", "yes", "on"}
            if self.usegui:
                if not self.startinfo:
                    raise KeyError("'startupinfo' option")
                if not self.installtitle:
                    raise KeyError("'installtitle' option")
                if not self.logoimage:
                    raise KeyError("'logoimg' option")
                if not self.buttontext:
                    raise KeyError("'buttontext' option")
                if not self.themename:
                    raise KeyError("'themename' option")
        except Exception as ex:
            logger.error(ex)
            raise SystemExit("Missing keyword {} in the [STARTUP] section".format(ex))

        try:
            userinfo = config_object["USERINFO"]
            build = config_object["BUILD"]
            self.resources = build["resources"]
            self.files = config_object._sections['FILES']
            self.username = userinfo["username"]
            self.password = userinfo["password"]
            self.buildtype = build["buildtype"]
            self.installtype = build["installtype"]
            self.repo = config_object._sections['REPO']
            self.rpms = config_object._sections['RPM']
            self.actions = config_object._sections['ACTIONS']
            self.modify = config_object._sections['MODIFY']
            self.finalactions = config_object._sections['FINAL']
            self.options = config_object._sections['OPTIONS']
            raw_userinput = config_object._sections['USERINPUT']
            self.userinput = {}
            self.userinput_defaults = {}
            for key, value in raw_userinput.items():
                parts = value.split("||", 1)
                prompt = parts[0].strip()
                default = parts[1].strip() if len(parts) > 1 else ""
                self.userinput[key] = prompt
                if default:
                    self.userinput_defaults[key] = default
            self.variables = config_object._sections['VARIABLES']
            if config_object.has_section("SERVERCONFIG") and "host" in config_object["SERVERCONFIG"]:
                self.hostname = config_object["SERVERCONFIG"]["host"]
        except Exception as ex:
            logger.error(ex)
            print("Missing keyword in .ini file.  check you .ini file for the following: {}".format(ex))
            raise SystemExit
