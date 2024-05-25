import sys
import ctypes
from elevate import elevate
from configparser import ConfigParser
from managers.rpmmanager import RpmManager
from managers.guimanager import GuiManager
from task import Task
import os.path
from os import path
import tkinter as tk
import ttkbootstrap as ttk
import threading
import logging

configfile = "config.ini"
version = "4.0.4"
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

    def __init__(self):
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
            

class mainClass:
    display_dict = {}
    rpm_manager = RpmManager()
    gui_manager = GuiManager()

    window = None

    def installThread(self, ini_info, InstallButton, window):
        InstallButton['state'] = tk.DISABLED
        finished = False
        installthread = threading.Thread(target=self.beginInstall, args=(ini_info, window))
        installthread.start()

    def main(self):
        ini_info = iniInfo()
        # self.window = ttk.Window(themename="superhero")
        self.window = tk.Tk()
        logger.info("******************************************************************")
        logger.info("******************************************************************")
        logger.info(" ><###> Tarpon Installer <###>< is an open source install creator.")
        logger.info(" It has been made open source under the MIT Licensing agreement.")
        logger.info(" Feel free to use, modify and distribute")
        logger.info(" as needed, as long as this banner remains in place")
        logger.info("*  VERSION {}".format(version))
        logger.info("******************************************************************")
        logger.info("******************************************************************")

        functiontitle = 'Important Installation Information Needed'

        self.gui_manager.buildGUI(self.window, functiontitle, ini_info, self.installThread)
        self.window.mainloop()

    def beginInstall(self, ini_info, window):

        for key in self.display_dict:
            if "Username" in key:
                ini_info.username = self.display_dict[key].get()
            if "Password" in key:
                ini_info.password = self.display_dict[key].get()
            if "Host IP" in key:
                ini_info.host = self.display_dict[key].get()

        task = Task(ini_info.username, ini_info.password, ini_info.host, ini_info.resources)

        # if Remote Type then login via SSH
        if ini_info.installtype == 'REMOTE': 
            task.loginSSH()

        try:
            # Repos and RPMs are Linux only
 
            # Remote Install
            if ini_info.buildtype == 'LINUX' and ini_info.installtype == 'REMOTE':
                task.installRemoteRepo(ini_info.resources, ini_info.repo)
                self.rpm_manager.installRPMsRemote(ini_info.resources, ini_info.rpms)

            # Local Install
            if ini_info.buildtype == 'LINUX':
                self.gui_manager.section.set("SECTION: INSTALLING RPMs")
                self.rpm_manager.installLocalRPMs(window, self.gui_manager.bar, self.gui_manager.taskitem, ini_info.resources, ini_info.rpms, ini_info.watchdog)

            self.gui_manager.section.set("SECTION: COPYING FILES")
            task.copyFromResources(window, self.gui_manager.bar, self.gui_manager.taskitem, ini_info)

            self.gui_manager.section.set("SECTION: ACTIONS")
            self.gui_manager.taskitem.set("")
            task.doActions(window, self.gui_manager.bar, self.gui_manager.taskitem, ini_info)

            self.gui_manager.section.set("SECTION: MODIFYING FILES")
            self.gui_manager.taskitem.set("")        
            task.modifyFiles(window, self.gui_manager.bar, self.gui_manager.taskitem, ini_info)

            self.gui_manager.section.set("SECTION: FINAL ACTIONS")
            self.gui_manager.taskitem.set("")
            task.finalActions(window, self.gui_manager.bar, self.gui_manager.taskitem, ini_info)
            self.window.quit()
            
                
        except Exception as ex:
            logger.error(ex)


def PrintHelp():
    print("************************************************************************")
    print("*  ><###> Tarpon Installer <###>< is an open source install creator.   *")
    print("*  specify config.ini file on the commandline                          *")
    print("*                                                                      *")
    print("*  Usage: tarpon_installer.exe yourconfig.ini                          *")
    print("*  Alt Usage: tarpon_installer.exe -t yourconfig.ini -debuglevel DEBUG *")
    print("*                                                                      *")
    print("*  debug levels are: INFO (default) and DEBUG                          *")
    print("*                                                                      *")
    print("*  VERSION {}                                                          *".format(version))
    print("************************************************************************")
    raise SystemExit

def isAdmin():
    try:
        is_admin = (os.getuid() == 0)
    except AttributeError:
        is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
    return is_admin


if __name__ == "__main__":
    params = {}
    option = ""
    skipImport = False
    debuglevel = None

    logger = logging.getLogger("logger")
    
    for arg in sys.argv:
        if arg[0:1] == "-":
            option = arg
        else:
            params[option] = arg

    i = 0
    for item in params:
        print("parameter {}: {}".format(i, params[item]))
        i = i + 1    

    if len(sys.argv) < 2:
        PrintHelp()

    if len(sys.argv) == 2:
        for arg in sys.argv:
            if arg[0:1] == "-":
                option = arg
            else:
                params[option] = arg
                
        for item in params:
            configfile = params[item]
                
    elif len(sys.argv) > 3:            
        if "-t" in params:
            configfile = params["-t"]
    
        if "-debuglevel" in params:
            debuglevel = params["-debuglevel"]
    else:
        PrintHelp()

    for item in params:
        logger.info("parameter {}".format(params[item]))

    if path.exists(configfile) == False:
        logger.error("ERROR: ><###> Cannot Find Configuration File - '{}'. <###><".format(configfile))
        PrintHelp()

    if debuglevel == None:
        logging.basicConfig(filename="{}.log".format(os.path.splitext(configfile)[0]),
                        filemode='w', level = logging.INFO)
    elif 'DEBUG' in debuglevel:
        logging.basicConfig(filename="{}.log".format(os.path.splitext(configfile)[0]),
                        filemode='w', level = logging.DEBUG)
    else:
        logging.basicConfig(filename="{}.log".format(os.path.splitext(configfile)[0]),
                        filemode='w', level = logging.INFO)

    if isAdmin():
        logger.info("Executing as Administrator")
    else:
        logger.info("Elevating Permissions because Administrator = {}".format(isAdmin()))
        # elevate(graphical = True)
    
    mc = mainClass()
    mc.main()