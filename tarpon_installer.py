import sys
import ctypes
from elevate import elevate
from configparser import ConfigParser
from managers.rpmmanager import RpmManager
from task import Task
import os.path
from os import path
from easygui import *
import tkinter as tk
import tkinter.ttk as ttk
from PIL import Image as Image, ImageTk as Itk
from tkscrolledframe import ScrolledFrame
import threading
import logging

configfile = "config.ini"
version = "3.5.7"
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
    watchdog = None
    files = dict()
    repo = dict()
    rpms = dict()
    actions = dict()
    modify = dict()
    finalactions = dict()
    options = dict()
    optionvals = dict()
    userinput = dict()

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
            self.watchdog = bool(startup['watchdog'])
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
        except Exception as ex:
            logger.error(ex)
            print("Missing keyword in .ini file.  check you .ini file for the following: {}".format(ex))
            raise SystemExit
            

class mainClass:
    display_list = []
    display_dict = {}
    rpm_manager = RpmManager

    window = tk.Tk()

    border_effects = {
        "flat": tk.FLAT,
        "sunken": tk.SUNKEN,
        "raised": tk.RAISED,
        "groove": tk.GROOVE,
        "ridge": tk.RIDGE
        }


    def optionsDialog(self, parent, ini_info):
        optionsWindow = tk.Toplevel(self.window)
        optionsWindow.geometry("600x300")
        # window.title(ini_info.installtitle)
        optionsWindow.resizable(False,False)
        optionsWindow.focusmodel(model="active")
        optionsWindow.after(100, lambda: optionsWindow.focus_force())

        # This centers the window
        optionsWindow.wait_visibility()
        x = parent.winfo_x() + parent.winfo_width()//2 - optionsWindow.winfo_width()//2
        y = parent.winfo_y() + parent.winfo_height()//2 - optionsWindow.winfo_height()//2
        optionsWindow.geometry(f"+{x}+{y}")

        functionFrame = tk.Frame(optionsWindow, height=240, width=340)
        functionFrame.pack(side="top", expand=0, fill="both")

        scrolledFrame = ScrolledFrame(functionFrame, height=240, width=360)
        scrolledFrame.pack(side="top", expand=0, fill="both")

        scrolledFrame.bind_arrow_keys(functionFrame)
        scrolledFrame.bind_scroll_wheel(functionFrame)
        inner_frame = scrolledFrame.display_widget(tk.Frame)

        for row in range(len(ini_info.options)):
            vals = ini_info.options.keys()
            value = list(vals)[row]

            ini_info.optionvals[value]=tk.StringVar(value='0')

            lb = tk.Label(inner_frame, justify = "left", text=ini_info.options[value])
            cb = tk.Checkbutton(inner_frame, justify = "left", variable=ini_info.optionvals[value], onvalue='1', offvalue='0')
            lb.grid(row=row,
                    column=1, stick="W")
            cb.grid(row=row,
                    column=0, stick="W")

        optionsButton = tk.Button(optionsWindow, text="Close", width=20, font="Arial 10 bold", command=optionsWindow.destroy).place(relx=.5, y=280,anchor=tk.CENTER)


    def buildGUI(self, functiontitle):
        ini_info = iniInfo()
        optionbuttonresize = 0
            
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

        self.window.geometry("800x420")
        self.window.title(ini_info.installtitle)
        self.window.resizable(False,False)
        self.window.focusmodel(model="passive")

        for row in range(len(ini_info.options)):
            vals = ini_info.options.keys()
            value = list(vals)[row]
            ini_info.optionvals[value]=tk.StringVar(value='0')

        section = tk.StringVar()
        taskitem = tk.StringVar()

        PicFrame = tk.Frame(self.window, height=380, width=380, relief=tk.RAISED, borderwidth=3)
        PicFrame.place(x=10,y=10)

        titleimage=Image.open(ini_info.logoimage)
        titleimage = titleimage.resize((300,300))
        titlepic = Itk.PhotoImage(titleimage)
        piclabel = tk.Label(PicFrame, image=titlepic)
        piclabel.image = titlepic
        piclabel.place(relx=.5, rely=.5, anchor=tk.CENTER)

        TitleFrame = tk.Frame(self.window, height=100, width=390, relief=tk.RAISED, borderwidth=3)
        TitleFrame.place(x=400, y=10)
        TitleLabel = tk.Label(TitleFrame, text=ini_info.installtitle, font="Arial 17 bold")
        TitleLabel.place(relx=.5, y=20, anchor=tk.CENTER)
        tk.Label(TitleFrame,textvariable=section).place(x=10, y=45, anchor="w")

        bar = ttk.Progressbar(TitleFrame,orient=tk.HORIZONTAL,length=310)
        bar.place(relx=.5, y=70,anchor=tk.CENTER)
        
        if(len(ini_info.options) > 0):
            optionbuttonresize = 30
            
        functionFrame = tk.Frame(self.window, height=155 - optionbuttonresize, width=365, relief=tk.RAISED, borderwidth=3)
        functionFrame.place(x=400, y=120)

        scrolledFrame = ScrolledFrame(functionFrame, height=155 - optionbuttonresize, width=365)
        scrolledFrame.pack(side="top", expand=0, fill="both")

        scrolledFrame.bind_arrow_keys(functionFrame)
        scrolledFrame.bind_scroll_wheel(functionFrame)
        inner_frame = scrolledFrame.display_widget(tk.Frame)

        functionTitleLabel = tk.Label(inner_frame,text=functiontitle, font="Arial 12 bold")

        row = 0
        functionTitleLabel.grid(row=row, column=0, sticky='W',padx=10, columnspan = 2)
        row += 1

        for entrylabel in self.display_list:
            var = tk.StringVar()
            lb = tk.Label(inner_frame, text=entrylabel, justify = "left")
            lb.grid(row=row, column=0, sticky='W',padx=10)
            en = tk.Entry(inner_frame, textvariable=var, justify = "left")
            en.grid(row=row, column=1, sticky='W',padx=10)
            self.display_dict[entrylabel] = var
            row += 1

        for entrylabel in ini_info.userinput:
            var = tk.StringVar()
            lb = tk.Label(inner_frame, justify = "left", text=ini_info.userinput[entrylabel])
            lb.grid(row=row, column=0, sticky='W',padx=10)

            en = tk.Entry(inner_frame, justify = "left", text=entrylabel, textvariable=var)
            en.grid(row=row, column=1, sticky='W',padx=10)
            ini_info.userinput[entrylabel] = var
            row += 1

        row += 1
        lb = tk.Label(inner_frame, justify = "left", text="")
        lb.grid(row=row, column=0, sticky='W',padx=10)
        row += 1
        lb2 = tk.Label(inner_frame, justify = "left", text="")
        lb2.grid(row=row, column=0, sticky='W',padx=10)

        if(len(ini_info.options) > 0):
            optionsButton = tk.Button(self.window, text="Options", width=20, font="Arial 10 bold", command=lambda: self.optionsDialog(self.window, ini_info)).place(x=595, y=290,anchor=tk.CENTER)

        taskFrame = tk.Frame(self.window, height=85, width=390, relief=tk.RAISED, borderwidth=3)
        taskFrame.place(x=400, y=305)

        section.set("SECTION:")
        taskitem.set("INSTALL TASK:")
        tk.Label(taskFrame,textvariable=taskitem, wraplength = 350, justify="left").place(x=10, y=17, anchor="w")

        InstallButton = tk.Button(taskFrame,text=ini_info.buttontext, width=10, font="Arial 10 bold", command=lambda: self.installThread(ini_info, InstallButton, self.window, bar, section, taskitem))
        InstallButton.place(relx=.5, y=60, anchor=tk.CENTER)

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

        self.buildGUI(functiontitle)
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
                self.rpm_manager.installRPMsRemote(ini_info.resources, ini_info.rpms)

            # Local Install
            if ini_info.buildtype == 'LINUX':
                section.set("SECTION: Installing RPMs")
                self.rpm_manager.installLocalRPMs(window, bar, taskitem, ini_info.resources, ini_info.rpms, ini_info.watchdog)

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
        elevate(graphical = True)
    
    mc = mainClass()
    mc.main()