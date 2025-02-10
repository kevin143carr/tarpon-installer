import sys, getopt
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

version = "4.0.5"
logger = None
configfile = "config.ini"

class mainClass:
    """Using a main class because of the amount of work that needs to be done initially."""
    display_dict = {}
    rpm_manager = RpmManager()
    gui_manager = GuiManager()

    window = None

    def installThread(self, ini_info, InstallButton, window) -> None:
        InstallButton['state'] = tk.DISABLED
        installthread = threading.Thread(target=self.beginInstall, args=(ini_info, window))
        installthread.start()

    def main(self) -> None:
        """This is the main entry point for the mainClass. It does not take any parameters
        Args:
            None
        Returns:
            None
        """
        if sys.version_info[:3] < (3,9):
            self.window = tk.Tk()
        else:
            self.window = ttk.Window(themename=ini_info.themename)

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


def PrintHelp() -> None:
    print("************************************************************************")
    print("*  ><###> Tarpon Installer <###>< is an open source install creator.   *")
    print("*  specify config.ini file on the commandline                          *")
    print("*                                                                      *")
    print("*  Usage: tarpon_installer.exe -t yourconfig.ini                       *")
    print("*  Alt Usage: tarpon_installer.exe -t yourconfig.ini --debuglevel DEBUG*")
    print("*                                                                      *")
    print("*  debug levels are: INFO (default) and DEBUG                          *")
    print("*                                                                      *")
    print(f"*  VERSION {version}                                                  *")
    print("************************************************************************")
    raise SystemExit

def isAdmin() -> None:
    try:
        is_admin = (os.getuid() == 0)
    except AttributeError:
        is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
    return is_admin


if __name__ == "__main__":
    global ini_info
    
    params = {}
    option = ""
    skipImport = False
    debuglevel = None
    ini_info = iniInfo()
    arglist = []

    logger = logging.getLogger("logger")
    print(f"len of args {len(sys.argv)}")
    
    try:
        # during elevation an additional arg of the .exe itself is added
        # and messes things up.  So let's remove it.
        for args in sys.argv[1:]:
            if "tarpon_installer.exe" not in args:
                arglist.append(args)
                
        opts, args = getopt.getopt(arglist,"t:d",["debuglevel=","configfile="])
    except getopt.GetoptError:
        PrintHelp()
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-t", "--configfile"):
            configfile = arg
            print(f"using {configfile} for installation instruction")
        elif opt in ("-d", "--debuglevel"):
            debuglevel = arg

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
        
    ini_info.readConfigFile(configfile)    
        
    if isAdmin():
        logger.info("Executing as Administrator")
    else:
        logger.info("Elevating Permissions because Administrator = {}".format(isAdmin()))
        if ini_info.adminrights == True:
            if (platform.system() == 'Windows'):
                elevate(show_console = True)
            else:
                logger.error("This install requires admin/root privelages")
                print("Error - This install requires admin/root privelages")
                print("** Set the [adminrights] value to False in the xxxx.ini file if not needed. **")
                raise SystemExit
    
    mc = mainClass()
    mc.main()