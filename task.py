#!/usr/bin/env python3

import time
import paramiko
import os
import subprocess
import shutil
import sys
from zipfile import ZipFile
from shutil import copyfile
from pathlib import Path
from fileutilities import FileUtilities
from easygui import *
import logging

class Task:
    ssh = paramiko.SSHClient()
    username = ""
    password = ""
    hostname = ""
    resources = ""
    file_utilities = FileUtilities
    logger = logging.getLogger("mylogger")

    def loginSSH(self):
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh.connect(hostname = self.hostname, username = self.username, password = self.password)

    def installRemoteRepo(self, resources, repo):
        ftp = self.ssh.open_sftp()
        for key in repo:
            self.logger.info('copying and extracting Repo files {} to {}'.format(key, repo[key]))
            self.ssh.exec_command('mkdir {}'.format(repo[key]))
            src = "{}/{}".format(resources, key)
            dst = "{}/{}".format(repo[key],key)
            ftp.put(src , dst)
            stdin, stdout, stderr = self.ssh.exec_command('tar xvfz {}/{}'.format(repo[key],key))
            for line in iter(stdout.readline,""):
                self.logger.info (line, end="")
            stdin, stdout, stderr = self.ssh.exec_command('chmod 775 -f {}/{}'.format(repo[key],key))
            for line in iter(stdout.readline,""):
                self.logger.info (line, end="")
        ftp.close()

    def installLocalRepo(self, resources, repo):
        for key in repo:
            self.logger.info('copying and extracting Repo files {} to {}'.format(key, repo[key]))
            if key != "installpkg.sh":
                os.mkdir('{}'.format(repo[key]))
            src = "{}/{}".format(resources, key)
            dst = "{}/{}".format(repo[key],key)
            try:
                shutil.copy(src, dst)
            except:
                copyfile(src)
            try:    
                p = subprocess.run(['tar', 'xvfz', '{}/{}'.format(repo[key],key), '-C', '/root'])
            except:
                p = subprocess.check_output('tar xvfz {}/{}'.format(repo[key],key), '-C', '/root', shell=True)        
            for line in str(p).splitlines():
                self.logger.info(line, end="")
            p = subprocess.check_output('chmod 775 -f {}'.format(repo[key]), shell=True)
            for line in str(p).splitlines():
                self.logger.info(line, end="\n")

    def installRPMs(self, resources, rpms):
        for key in rpms:
            self.logger.info('install RPMs {} to {}'.format(key, rpms[key]))
            stdin, stdout, stderr = self.ssh.exec_command('/root/installpkg.sh {}'.format(rpms[key]))
            for line in str(p).splitlines():
                self.logger.info (line, end="")
            time.sleep(5)

    def installLocalRPMs(self, resources, rpms):
        p = subprocess.check_output('sudo chmod +x /root/installpkg.sh', shell=True)
        for key in rpms:
            self.logger.info('install RPMs {} to {}'.format(key, rpms[key]))
            try:
                p = subprocess.check_output('/root/installpkg.sh {} -f'.format(rpms[key]), shell=True)
                self.logger.info("PPP", p)
            except:
                p = subprocess.run(['/root/installpkg.sh {} -f'.format(rpms[key])])
            for line in str(p).splitlines():
                self.logger.info(line, end="\n")
            time.sleep(5)

    def copyFromResourcesLocal(self, window, bar, taskitem, resources, files):
        count = 0
        for key in files:
            count += 1;
            bar['value'] = (count/len(files.keys()))*100
            window.update_idletasks()
            firstfile = 0
            my_file = Path("{}/{}".format(resources,key))
            if my_file.is_file():
                taskstr = 'copying and extracting file {} to {}'.format(key, files[key])
                self.logger.info(taskstr)
                taskitem.set(taskstr)
                try:
                    if '.' in files[key]: # contains a file name
                        dirname = os.path.dirname(os.path.abspath(files[key])) # just get the path
                        os.makedirs(dirname, exist_ok = True)
                    else:
                        os.makedirs(files[key], exist_ok = True)
                    self.logger.info("Directory {} created successfully".format(files[key]))
                except OSError as error:
                    self.logger.warning("Directory {} can not be created".format(files[key]))

                dirtest = key.split('/')
                src = "{}{}".format(resources, key)
                if '.' in files[key]: # contains a file name, so do not append a filename from 'key'
                    dst = "{}".format(files[key])
                else:
                    if (len(dirtest) > 1):
                        keyname = dirtest[1]
                        dst = "{}/{}".format(files[key],keyname)
                    else:
                        dst = "{}/{}".format(files[key],key)

                copyfile(src,dst)

                if 'zip' in key:

                    with ZipFile(dst) as zf:
                        hasdirectory = False  # the zip file has an initial directory in which files will be extracted
                        for file in zf.namelist():

                            if firstfile == 0:
                                firstfile = 1
                                test = file.split('/')
                                if(len(test) > 1):
                                    hasdirectory = True

                            filename = os.path.basename(file)

                            # create directories
                            if not filename:
                                words = file.split('/')
                                filename = ""

                                if(hasdirectory == False):
                                    filename = file
                                else:
                                    for i in range(len(words)-1):
                                        if i == 0:
                                            filename += words[i+1]
                                        else:
                                            filename += "/"
                                            filename += words[i+1]

                                os.makedirs(files[key] +"/" + filename, exist_ok = True)
                                continue
    
                            # copy file (taken from zipfile's extract)
                            words = file.split('/')
                            filename = ""

                            if hasdirectory == False:
                                filename = file
                            else:
                                if len(words) > 1:
                                    for i in range(len(words)-1):
                                        if i == 0:
                                            filename += words[i+1]
                                        else:
                                            filename += "/"
                                            filename += words[i+1]
                                else:
                                    filename = words[0]

                            source = zf.open(file)
                            target = open(os.path.join(files[key], filename), "wb")
                            with source, target:
                                shutil.copyfileobj(source, target)
            else:
                self.logger.error("Error copying file {}/{}, it does not exist".format(resources,key))
        finished = True

    def copyFromResourcesSSH(self, resources, files):
        ftp = self.ssh.open_sftp()
        for key in files:
            my_file = Path("{}/{}".format(resources,key))
            if my_file.is_file():
                self.logger.info('copying and extracting file {} to {}'.format(key, files[key]))
                self.ssh.exec_command('mkdir -p {}'.format(files[key]))
                dirtest = key.split('/')
                src = "{}{}".format(resources, key)
                if '.' in files[key]: # contains a file name, so do not append a filename from 'key'
                    dst = "{}".format(files[key])
                else:
                    if (len(dirtest) > 1):
                        keyname = dirtest[1]
                        dst = "{}/{}".format(files[key],keyname)
                    else:
                        dst = "{}/{}".format(files[key],key)

                if(os.path.exists("{}/{}".format(os.getcwd(), src)) == False):
                    self.logger.error("Error could not find this file: {}/{}".format(os.getcwd(), src))
                    continue

                ftp.put(src , dst)

                if 'zip' in key:
                    stdin, stdout, stderr = self.ssh.exec_command('unzip -o {}/{} -d {}'.format(files[key],key,files[key]))
                    for line in iter(stdout.readline,""):
                        self.logger.info (line, end="")
            else:
                self.logger.error("Error copying file {}/{}, it does not exist".format(resources,key))
        ftp.close()

    def copyFromResources(self, window, bar, taskitem, ini_info):
        if(ini_info.installtype == 'REMOTE' and ini_info.buildtype == 'LINUX'):
            self.copyFromResourcesSSH(ini_info.resources, ini_info.files)
        elif ini_info.installtype == 'LOCAL':
            self.copyFromResourcesLocal(window, bar, taskitem, ini_info.resources, ini_info.files)

    def doActionsSSH(self, actions):
        for action in actions:
            if '%host%' in actions[action]:
                actions[action] = actions[action].replace("%host%",self.hostname)
            self.logger.info('Executing Action {} with {}'.format(action, actions[action]))
            stdin, stdout, stderr = self.ssh.exec_command('{}'.format(actions[action]))
            for line in iter(stdout.readline,""):
                self.logger.info (line, end="")

    def doActionsLocal(self, window, bar, taskitem, actions):
        count = 0
        for action in actions:
            count += 1;
            bar['value'] = (count/len(actions.keys()))*100
            window.update_idletasks()

            try:
                if '%host%' in actions[action]:
                    actions[action] = actions[action].replace("%host%",self.hostname)

                if 'YESNO' in actions[action]:
                    text = actions[action].split('::');
                    answer = ynbox(text[1],"User Question");
                    if answer == False:
                        continue;
                    else:
                        actions[action] = text[2];

                taskstr = 'Executing Action {} with {}'.format(action, actions[action])
                self.logger.info(taskstr)
                taskitem.set(taskstr)

                p = subprocess.check_output(actions[action], shell=True)
                for line in p.splitlines():
                    self.logger.info(line.decode('utf-8'))
            except Exception as e:
                self.logger.error("Error in Action {}".format(str(e)))

    def doActions(self, window, bar, taskitem, ini_info, type = "action"):
        if(ini_info.installtype == 'REMOTE' and ini_info.buildtype == 'LINUX'):
            self.doActionsSSH(ini_info.actions)
        elif ini_info.installtype == 'LOCAL':
            if(type == "action"):
                self.doActionsLocal(window, bar, taskitem, ini_info.actions)
            elif(type == "final"):
                self.doActionsLocal(window, bar, taskitem, ini_info.finalactions)

    def modifyFilesLocal(self, window, bar, taskitem, files):
        count = 0
        try:
            for file in files:
                count += 1;
                bar['value'] = (count/len(files.keys()))*100
                window.update_idletasks()

                ischange = True if("{CHANGE}" in files[file]) else False
                if(ischange):
                    result = files[file].split("{CHANGE}")
                else:
                    result = files[file].split("{ADD}")

                modifywith = result[1]
                file = files[file][len("{FILE}"):len(result[0])]

                my_file = Path("{}".format(file))

                taskstr = 'Modifying File {} with {}'.format(file, modifywith)
                self.logger.info(taskstr)
                taskitem.set(taskstr)

                if my_file.is_file():
                    modcontent = modifywith.split("||")
                    if ischange:
                        self.file_utilities.modifyFileContents(file, modcontent[0], modcontent[1])
                    else:
                        self.file_utilities.addFileContents(file, modifywith)
                else: # Create File Condition
                    self.file_utilities.createFileAddContents(file,modifywith.split("||"))
        except Exception as ex:
            self.logger.error(ex)


    def modifyFilesSSH(self, files):
        for file in files:
            result = files[file].split("||")
            file = file.split("-",1)
            stdin, stdout, stderr = self.ssh.exec_command('sed -i \"s/{}/{}/g\" {}'.format(result[0],result[1],file[1]))
            for line in iter(stderr.readline,""):
                self.logger.info (line, end="")

    def modifyFiles(self, window, bar, taskitem, ini_info):
        if(ini_info.installtype == 'REMOTE' and ini_info.buildtype == 'LINUX'):
            self.modifyFilesSSH(ini_info.modify)
        else:
            self.modifyFilesLocal(window, bar, taskitem, ini_info.modify)

    def finalActions(self, window, bar, taskitem, ini_info):
        self.doActions( window, bar, taskitem, ini_info, "final")

    def __init__(self, username, password, hostname, resources):
        self.username = username
        self.password = password
        self.hostname = hostname    
        self.resources = resources
