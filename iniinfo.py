from configparser import ConfigParser
import logging

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
        self.buttontext = ""
        self.watchdog = False
        self.adminrights = False
        self.files = {}
        self.repo = {}
        self.rpms = {}
        self.actions = {}
        self.modify = {}
        self.finalactions = {}
        self.options = {}
        self.optionvals = {}
        self.userinput = {}
        self.variables = {}
        self.returnvars = {}
        self.themename = "superhero"

    def readConfigFile(self, configfile):
        logger = logging.getLogger("logger")
        config_object = ConfigParser()
        config_object.optionxform = str
        try:
            config_object.read(configfile)
            startup = config_object["STARTUP"]
            self.startinfo = startup['startupinfo']
            self.installtitle = startup['installtitle']
            self.logoimage = startup['logoimg']
            self.buttontext = startup['buttontext']
            self.watchdog = config_object.getboolean("STARTUP", "watchdog")
            self.adminrights = config_object.getboolean("STARTUP", "adminrights")
            self.themename = startup["themename"]
        except Exception as ex:
            logger.error(ex)
            print("Missing keyword {} in the [STARTUP] section".format(ex))
            raise SystemExit
        
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
            self.userinput = config_object._sections['USERINPUT']
            self.variables = config_object._sections['VARIABLES']
            if config_object.has_section("SERVERCONFIG") and "host" in config_object["SERVERCONFIG"]:
                self.hostname = config_object["SERVERCONFIG"]["host"]
        except Exception as ex:
            logger.error(ex)
            print("Missing keyword in .ini file.  check you .ini file for the following: {}".format(ex))
            raise SystemExit
