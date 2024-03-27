import sys
import os
import subprocess
import time
from configparser import ConfigParser
from os import path
import fnmatch
import shutil

version = "2.1.1"
ticonfigfile = "config.ini"
baconfigfile = "buildadderconfig.ini"

def PrintHelp():
    print("")
    print("buildadder adds latest builds in a folder to the Tarpon Installer Config.ini File.")
    print("THE FOLDER MUST RESIDE UNDER THE [resources] FOLDER IN YOUR TARPON INSTALLER DIRECTORY")
    print("")
    print("This requires the following comments in your tarponconfig.ini file:")
    print("")
    print("#BUILDS START HERE")
    print("#BUILDS END HERE")
    print("")
    print("")
    print("Usage: buildadder -d yes -t tarponconfig.ini -b buildadderconfig.ini -f buildfolder1,buildfolder2 <--[UNDER THE resources FOLDER]")
    print("")
    print("Required Arguments:")
    print("	-t     name of tarpon config file, such as win_local_config_3_2_7.ini")
    print("	-b     name of buildadder config file, such as win_local_builder.ini")
    print("	-f     folder in which the build files are located, can be multiple separated by comma")
    print("	-r     folder in which the RPM files are located, can be multiple separated by comma")
    print("	-d     cleans out the buildadder section in the ini file (yes or no) default no")
    print("")
    print("")
    print("     VERSION {}".format(version))
    print("")
    raise SystemExit

class iniInfo:
    files = dict()
    rpms = dict()

    def __init__(self):
        config_object = ConfigParser()
        config_object.optionxform = str
        config_object.read(baconfigfile)
        self.files = config_object._sections['FILES']
        self.rpms = config_object._sections['RPMS']



class Task:
    files = dict()
    userfiles = dict()
    userconfigfile = ''
    buildstartshere = 'BUILDS START HERE'
    buildendshere = 'BUILDS END HERE'
    rpmsstarthere = 'RPMS START HERE'
    rpmsendhere = 'RPMS END HERE'
    builddirfiles = list()
    rpmdirfiles = list()

    def __init__(self, files, userconfigfile, builddir, rpmdir):
        self.files = files
        self.userconfigfile = userconfigfile
        
        if '\r' in rpmdir:
            rpmdir = rpmdir.strip('\r')  
            
        if '\r' in builddir:
            builddir = builddir.strip('\r')          
        
        if ',' in builddir:
            dirs = builddir.split(',')
            for dir in dirs:
                files = os.listdir("resources/" + dir)
                for file in files:
                    self.builddirfiles.append("{}/{}".format(dir,file))
        else:
            files = os.listdir("resources/" + builddir)
            for file in files:
                self.builddirfiles.append("{}/{}".format(builddir,file))

        if ',' in rpmdir:
            dirs = rpmdir.split(',')
            for dir in dirs:
                files = os.listdir("resources/" + dir)
                for file in files:
                    self.rpmdirfiles.append("{}/{}".format(dir,file))
        else:          
            files = os.listdir("resources/" + rpmdir)            
            for file in files:
                self.rpmdirfiles.append("{}/{}".format(rpmdir,file))        

    def insertFilenamesFromResources(self, files):
        found = False
        outF = open(self.userconfigfile + '.tmp', "w")
        fp =  open(self.userconfigfile,"r")
        for line in fp.readlines():
            if self.buildstartshere in line:
                found = True
                outF.write(line)
                for key in files:
                    pattern = '*{}*'.format(key)
                    matching = fnmatch.filter(self.builddirfiles, pattern)
                    if(len(matching) == 0):
                        print("Error finding matching file to '{}'".format(key))
                        raise SystemExit
                    else:
                        outF.write('{} = {}\n'.format(matching[0],files[key]))

            if found == True:               
                found = False
            else:
                outF.write(line)

        outF.close()
        fp.close()
        shutil.copy(self.userconfigfile + '.tmp', self.userconfigfile)
        os.remove(self.userconfigfile + '.tmp')

    def insertRPMsFromResources(self, files):
        found = False
        outF = open(self.userconfigfile + '.tmp', "w")
        fp =  open(self.userconfigfile,"r")
        for line in fp.readlines():
            if self.rpmsstarthere in line:
                found = True
                outF.write(line)
                for key in files:
                    if ',' in files[key]:
                        filestr = ''
                        valx = files[key].split(',')
                        for val in valx:
                            pattern = '*{}*'.format(val)
                            matching = fnmatch.filter(self.rpmdirfiles, pattern)
                            for match in matching:
                                if filestr == '':
                                    filestr = match
                                else:
                                    if match not in filestr:
                                        filestr = filestr + ',' + match

                        outF.write('install{} = {}\n'.format(key,filestr))

                    else:
                        pattern = '*{}*'.format(key)
                        matching = fnmatch.filter(self.rpmdirfiles, pattern)
                        if(len(matching) == 0):
                            print("Error finding matching file to '{}'".format(key))
                            raise SystemExit
                        else:
                            outF.write('install{} = {}\n'.format(key,matching[0]))

            if found == True:               
                found = False
            else:
                outF.write(line)

        outF.close()
        fp.close()
        shutil.copy(self.userconfigfile + '.tmp', self.userconfigfile)
        os.remove(self.userconfigfile + '.tmp')        

    def deletefilesbuildsection(self):
        found = False
        outF = open(self.userconfigfile + '.tmp', "w")
        fp =  open(self.userconfigfile,"r")
        for line in fp.readlines():
            if self.buildstartshere in line:
                outF.write(line)
                found = True

            if self.buildendshere in line:
                found = False

            if found != True:               
                outF.write(line)

        outF.close()
        fp.close()
        shutil.copy(self.userconfigfile + '.tmp', self.userconfigfile)
        os.remove(self.userconfigfile + '.tmp')                

    def deleterpmsbuildsection(self):
        found = False
        outF = open(self.userconfigfile + '.tmp', "w")
        fp =  open(self.userconfigfile,"r")
        for line in fp.readlines():
            if self.rpmsstarthere in line:
                outF.write(line)
                found = True

            if self.rpmsendhere in line:
                found = False

            if found != True:               
                outF.write(line)                

        outF.close()
        fp.close()
        shutil.copy(self.userconfigfile + '.tmp', self.userconfigfile)
        os.remove(self.userconfigfile + '.tmp')

class mainClass:

    def main(self, userconfig, builddir, rpmdir, deletebuildsection):
        print("******************************************************************")
        print("******************************************************************")
        print("* ><###> buildadder <###><")
        print("*  VERSION {}".format(version))
        print("******************************************************************")
        print("******************************************************************")
        time.sleep(2)
        ini_info = iniInfo()
        task = Task(ini_info.files, userconfig, builddir, rpmdir)
        if deletebuildsection == True:
            task.deletefilesbuildsection()
            task.deleterpmsbuildsection()
        
        task.insertFilenamesFromResources(ini_info.files)
        task.insertRPMsFromResources(ini_info.rpms)


if __name__ == '__main__':
    params = {}
    option = ""
    skipImport = False
    builddir = ''
    rpmdir = ''

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

    if "-t" in params:
        ticonfigfile = params["-t"]

    if "-b" in params:
        baconfigfile = params["-b"]

    if "-f" in params:
        builddir = params["-f"]

    if "-r" in params:
        rpmdir = params["-r"]

    if "-d" in params:
        if 'y' in params["-d"]:
            deletebuildsection = True
        else:
            deletebuildsection = False

    if path.exists(ticonfigfile) == False:
        print("ERROR: ><###> Cannot Find Tarpon Configuration File. <###><")
        PrintHelp()

    mc = mainClass()
    mc.main(ticonfigfile, builddir, rpmdir, deletebuildsection)
