from configparser import ConfigParser
import logging

logger = None 

class iniInfo:
    username = ""
    password = ""
    host = ""
    buildtype = ""
    installtype = ""
    resources = ""
    startinfo = ""
    installtitle = ""
    logoimage = ""
    buttontext = ""
    watchdog = bool()
    files = dict()
    repo = dict()
    rpms = dict()
    actions = dict()
    modify = dict()
    finalactions = dict()
    options = dict()
    optionvals = dict()
    userinput = dict()
    variables = dict()
    returnvars = dict()

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
            self.watchdog = eval(startup['watchdog'])
        except Exception as ex:
            logger.error(ex)
            print("Missing keyword {} in the [STARTUP] section".format(ex))
            raise SystemExit
        
        try:
            userinfo = config_object["USERINFO"]
            serverinfo = config_object["SERVERCONFIG"]
            build = config_object["BUILD"]
            self.resources = build["resources"]
            self.files = config_object._sections['FILES']
            self.username = userinfo["username"]
            self.password = userinfo["password"]
            self.host = serverinfo["host"]
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
        except Exception as ex:
            logger.error(ex)
            print("Missing keyword in .ini file.  check you .ini file for the following: {}".format(ex))
            raise SystemExit