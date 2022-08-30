import sys
import time
from configparser import ConfigParser
from task import Task
import os.path
from os import path
from easygui import *

configfile = "config.ini"
version = "2.6.6"

class iniInfo:
    username = ""
    password = ""
    host = ""
    buildtype = ""
    installtype = ""
    resources = ""
    files = dict()
    repo = dict()
    rpms = dict()
    actions = dict()
    modify = dict()
    finalactions = dict()

    def __init__(self):
        config_object = ConfigParser()
        config_object.read(configfile)
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
        self.modify =  config_object._sections['MODIFY']
        self.finalactions = config_object._sections['FINAL']

class mainClass:
    display_list = []
    display_dict = {}

    def main(self):
        print("******************************************************************")
        print("******************************************************************")
        print(" ><###> Tarpon Installer <###>< is an open source install creator.")
        print(" It has been made open source under the MIT Licensing agreement.")
        print(" Feel free to use, modify and distribute")
        print(" as needed, as long as this banner remains in place")
        print("*  VERSION {}".format(version))
        print("******************************************************************")
        print("******************************************************************")
        time.sleep(2)
        ini_info = iniInfo()

        title = 'Important Installation Information Needed'
        text =  'Please Enter the Following Information'

        count = 0;
        if "DISPLAY" in ini_info.username:
            self.display_list.append("Username")
            self.display_dict.update({"Username": count})
            count+=1
        if "DISPLAY" in ini_info.password:
            self.display_list.append("Password")
            self.display_dict.update({"Password": count})
            count+=1
        if "DISPLAY" in ini_info.host:
            self.display_list.append("Host IP")
            self.display_dict.update({"Host IP": count})

        output = multenterbox(text, title, self.display_list)

        for key in self.display_dict:
            if "Username" in key:
                ini_info.username = output[self.display_dict[key]]
            if "Password" in key:
                ini_info.password = output[self.display_dict[key]]
            if "Host IP" in key:
                ini_info.host = output[self.display_dict[key]]

        task = Task(ini_info.username, ini_info.password, ini_info.host, ini_info.resources)

        # if Remote Type then login via SSH
        if ini_info.installtype == 'REMOTE':
            task.loginSSH()

        # Repos and RPMs are Linux only
 
        # Remote Install
        if ini_info.buildtype == 'LINUX' and ini_info.installtype == 'REMOTE':
            task.installRemoteRepo(ini_info.resources, ini_info.repo)
            task.installRPMs(ini_info.resources, ini_info.rpms)

        # Local Install
        if ini_info.buildtype == 'LINUX':
            task.installLocalRepo(ini_info.resources, ini_info.repo)
            task.installLocalRPMs(ini_info.resources, ini_info.rpms)

        task.copyFromResources(ini_info.resources, ini_info.files, ini_info.installtype, ini_info.buildtype)
        task.doActions(ini_info.actions, ini_info.installtype, ini_info.buildtype)
        task.modifyFiles(ini_info.modify, ini_info.installtype, ini_info.buildtype)
        task.finalActions(ini_info.finalactions, ini_info.installtype, ini_info.buildtype)

    def __init__(self):
        print("Starting ><###> Tarpon Installer <###>< !!!")
#        print("Using the following parameters: {} : {} : {}"
#            .format(self.ini_info.host,self.ini_info.username,self.ini_info.password))


def PrintHelp():
    print("**********************************************************************")
    print("*  ><###> Tarpon Installer <###>< is an open source install creator. *")
    print("*  specify config.ini file on the commandline                        *")
    print("*                                                                    *")
    print("*  Usage: tarpon_installer.exe yourconfig.ini                        *")
    print("*                                                                    *")
    print("*  VERSION {}".format(version))
    print("**********************************************************************")
    raise SystemExit


if __name__ == "__main__":
    params = {}
    option = ""
    skipImport = False

    if len(sys.argv) < 2:
        PrintHelp()

    for arg in sys.argv:
        if arg[0:1] == "-":
            option = arg
        else:
            params[option] = arg

    for item in params:
        configfile = params[item]
        print("parameter {}".format(params[item]))

    if path.exists(configfile) == False:
        print("ERROR: ><###> Cannot Find Configuration File. <###><")
        PrintHelp()
    
    mc = mainClass()
    mc.main()