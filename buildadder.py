import sys
import os
import subprocess
import time
from configparser import ConfigParser
from os import path
import fnmatch
import shutil

version = "1.0.0"
configfile = "config.ini"
adderconfigfile = "buildadderconfig.ini"

def PrintHelp():
    print("")
    print("buildadder adds latest builds in a folder to the Tarpon Installer Config.ini File.")
    print("THE FOLDER MUST RESIDE UNDER THE [resources] FOLDER IN YOUR TARPON INSTALLER DIRECTORY")
    print("")
    print("This requires the following comments in your config.ini file:")
    print("")
    print("#BUILDS START HERE")
    print("#BUILDS END HERE")
    print("")
    print("")
    print("Usage: buildadder -c tarponconfig.ini -f buildfolder <--[UNDER THE resources FOLDER]")
    print("")
    print("Required Arguments:")
    print("	-c     name of tarpon config file, such as win_local_config_3_2_7.ini")
    print("	-f     folder in which the build files are located")
    print("")
    print("")
    print("     VERSION {}".format(version))
    print("")
    raise SystemExit

class iniInfo:
    files = dict()

    def __init__(self):
        config_object = ConfigParser()
        config_object.read(adderconfigfile)
        self.files = config_object._sections['FILES']



class Task:
    files = dict()
    userfiles = dict()
    userconfigfile = ''
    buildstartshere = 'BUILDS START HERE'
    buildendshere = 'BUILDS END HERE'
    builddir = []

    def __init__(self, files, userconfigfile, builddir):
        self.files = files
        self.userconfigfile = userconfigfile
        self.builddir = os.listdir("resources/" + builddir)

    def copyFromResourcesLocal(self, files):
        found = False
        outF = open(self.userconfigfile + '.tmp', "w")
        fp =  open(self.userconfigfile,"r")
        for line in fp.readlines():
            if self.buildstartshere in line:
                found = True
                outF.write(line)
                for key in files:
                    pattern = '*{}*'.format(key)
                    matching = fnmatch.filter(self.builddir, pattern)
                    outF.write('{}/{} = {}\n'.format(builddir,matching[0],files[key]))

            if found == True:               
                found = False
            else:
                outF.write(line)

        outF.close()
        fp.close()
        shutil.copy(self.userconfigfile + '.tmp', self.userconfigfile)
        os.remove(self.userconfigfile + '.tmp')

class mainClass:

    def main(self, userconfig, builddir):
        print("******************************************************************")
        print("******************************************************************")
        print("* ><###> buildadder <###><")
        print("*  VERSION {}".format(version))
        print("******************************************************************")
        print("******************************************************************")
        time.sleep(2)
        ini_info = iniInfo()
        task = Task(ini_info.files, userconfig, builddir)
        task.copyFromResourcesLocal(ini_info.files)


if __name__ == '__main__':
    params = {}
    option = ""
    skipImport = False

    for arg in sys.argv:
        if arg[0:1] == "-":
            option = arg
        else:
            params[option] = arg

    i = 0
    for item in params:
        print("parameter {}: {}".format(i, params[item]))
        i = i + 1

    if i < 2:
        PrintHelp()

    if "-c" in params:
        configfile = params["-c"]

    if "-f" in params:
        builddir = params["-f"]

    if path.exists(configfile) == False:
        print("ERROR: ><###> Cannot Find Configuration File. <###><")
        PrintHelp()

    mc = mainClass()
    mc.main(configfile, builddir)
