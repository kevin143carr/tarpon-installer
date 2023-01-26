import sys
import ctypes
import time
from elevate import elevate
from configparser import ConfigParser
from task import Task
import os.path
from os import path
from easygui import *
import tkinter as tk
import tkinter.ttk as ttk
from PIL import Image as Image, ImageTk as Itk
import threading
import logging

configfile = "config.ini"
version = "3.1.0"
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
    files = dict()
    repo = dict()
    rpms = dict()
    actions = dict()
    modify = dict()
    finalactions = dict()

    def __init__(self):
        config_object = ConfigParser()
        try:
            config_object.read(configfile)
            startup = config_object["STARTUP"]
            self.startinfo = startup['startupinfo']
            self.installtitle = startup['installtitle']
            self.logoimage = startup['logoimg']
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
        except Exception as ex:
            logger.error(ex)

class mainClass:
    display_list = []
    display_dict = {}  
    window = tk.Tk()

    border_effects = {
        "flat": tk.FLAT,
        "sunken": tk.SUNKEN,
        "raised": tk.RAISED,
        "groove": tk.GROOVE,
        "ridge": tk.RIDGE
        }

    def buildGUI(self, functiontitle, functiontitletext, display_list):
        ini_info = iniInfo()

        count = 0
        if "DISPLAY" in ini_info.username:
            self.display_list.append("Username")
            count+=1
        if "DISPLAY" in ini_info.password:
            self.display_list.append("Password")
            count+=1
        if "DISPLAY" in ini_info.host:
            self.display_list.append("Host IP")
            count+=1

        if count > 0:
            output = self.display_dict
            if output == None:
                logger.warning("Installation Cancelled")
                return

        self.window.geometry("800x400")
        self.window.title(ini_info.installtitle)
        self.window.resizable(False,False)

        section = tk.StringVar()
        taskitem = tk.StringVar()

        PicFrame = tk.Frame(self.window, height=380, width=380, relief=tk.RAISED, borderwidth=5)
        PicFrame.place(x=10,y=10)

        titleimage=Image.open(ini_info.logoimage)
        titleimage = titleimage.resize((300,300))
        titlepic = Itk.PhotoImage(titleimage)
        piclabel = tk.Label(PicFrame, image=titlepic)
        piclabel.image = titlepic
        piclabel.place(relx=.5, rely=.5, anchor=tk.CENTER)

        TitleFrame = tk.Frame(self.window, height=100, width=390, relief=tk.RAISED, borderwidth=5)
        TitleFrame.place(x=400, y=10)
        TitleLabel = tk.Label(TitleFrame, text=ini_info.installtitle, font="Arial 17 bold")
        TitleLabel.place(relx=.5, y=20, anchor=tk.CENTER)
        tk.Label(TitleFrame,textvariable=section).place(x=10, y=45, anchor="w")

        bar = ttk.Progressbar(TitleFrame,orient=tk.HORIZONTAL,length=310)
        bar.place(relx=.5, y=70,anchor=tk.CENTER)

        functionFrame = tk.Frame(self.window, height=270, width=390, relief=tk.RAISED, borderwidth=5)
        functionFrame.place(x=400, y=120)
        functionTitleLabel = tk.Label(functionFrame,text=functiontitle)
        functionTitleLabel.place(relx=.5, y=20, anchor=tk.CENTER)
        functionTitleTextLabel = tk.Label(functionFrame, text=functiontitletext)
        functionTitleTextLabel.place(relx=.5, y=40, anchor=tk.CENTER)

        posy = 60
        for entrylabel in display_list:
            var = tk.StringVar()
            tk.Label(functionFrame, text=entrylabel).place( x=10, y=posy, anchor="w")
            tk.Entry(functionFrame, textvariable=var).place( x=200, y=posy, anchor="center")
            self.display_dict[entrylabel] = var
            posy += 20

        section.set("SECTION:")
        taskitem.set("INSTALL TASK:")
        tk.Label(functionFrame,textvariable=taskitem, wraplength = 350, justify="left").place(x=10, y=190, anchor="w")

        InstallButton = tk.Button(functionFrame,text="Begin Install",command=lambda: self.installThread(ini_info, InstallButton, self.window, bar, section, taskitem))
        InstallButton.place(relx=.5, y=240, anchor=tk.CENTER)

    def installThread(self, ini_info, InstallButton, window, bar, percent, text):
        InstallButton['state'] = tk.DISABLED
        finished = False
        installthread = threading.Thread(target=self.beginInstall, args=(ini_info, window, bar, percent, text))
        installthread.start()

    def main(self):
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
        functiontitletext = 'Please Enter the Following Information'

        self.buildGUI(functiontitle, functiontitletext, self.display_list)
        self.window.mainloop()

    def beginInstall(self, ini_info, window, bar, section, taskitem):

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
                task.installRPMs(ini_info.resources, ini_info.rpms)

            # Local Install
            if ini_info.buildtype == 'LINUX':
                task.installLocalRepo(ini_info.resources, ini_info.repo)
                task.installLocalRPMs(ini_info.resources, ini_info.rpms)

            section.set("SECTION: Copying Files")
            task.copyFromResources(window, bar, taskitem, ini_info)

            section.set("SECTION: Doing Actions")
            taskitem.set("")
            task.doActions(window, bar, taskitem, ini_info)

            section.set("SECTION: Modifying Files")
            taskitem.set("")        
            task.modifyFiles(window, bar, taskitem, ini_info)

            section.set("SECTION: Final Actions")
            taskitem.set("")
            task.finalActions(window, bar, taskitem, ini_info)
        except Exception as ex:
            logger.error(ex)


def PrintHelp():
    logger.info("**********************************************************************")
    logger.info("*  ><###> Tarpon Installer <###>< is an open source install creator. *")
    logger.info("*  specify config.ini file on the commandline                        *")
    logger.info("*                                                                    *")
    logger.info("*  Usage: tarpon_installer.exe yourconfig.ini                        *")
    logger.info("*                                                                    *")
    logger.info("*  VERSION {}".format(version))
    logger.info("**********************************************************************")
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

    logger = logging.getLogger("mylogger")

    logging.basicConfig(filename="installer.log",
                    filemode='w', level = logging.INFO)

    if len(sys.argv) < 2:
        PrintHelp()

    for arg in sys.argv:
        if arg[0:1] == "-":
            option = arg
        else:
            params[option] = arg

    for item in params:
        configfile = params[item]
        logger.info("parameter {}".format(params[item]))

    if path.exists(configfile) == False:
        logger.error("ERROR: ><###> Cannot Find Configuration File. <###><")
        PrintHelp()

    if isAdmin():
        logger.info("Executing as Administrator")
    else:
        logger.info("Elevating Permissions because Administrator = {}".format(isAdmin()))
        elevate()
    
    mc = mainClass()
    mc.main()