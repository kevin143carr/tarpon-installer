import sys
import time
from configparser import ConfigParser
from task import Task
import os.path
from os import path

configfile = "config.ini"
version = "2.5.5"

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
        task = Task(ini_info.username, ini_info.password, ini_info.host, ini_info.resources)

        # if Remote Type then login via SSH
        if ini_info.installtype == 'REMOTE':
            task.loginSSH()

        # Repos and RPMs are Linux only
        if ini_info.buildtype == 'LINUX':
            task.installRepo(ini_info.resources, ini_info.repo)
            task.installRPMs(ini_info.resources, ini_info.rpms)

        task.copyFromResources(ini_info.resources, ini_info.files, ini_info.installtype, ini_info.buildtype)
        task.doActions(ini_info.actions, ini_info.installtype, ini_info.buildtype)
        task.modifyFiles(ini_info.modify)
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