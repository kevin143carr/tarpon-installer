#!/usr/bin/env python3

import time
import paramiko
import os
import subprocess
import shutil
import sys
from zipfile import ZipFile
from tarfile import TarFile, TarInfo
from shutil import copyfile
from pathlib import Path
from fileutilities import FileUtilities
from processwatcher import ProcessWatcher
from easygui import *
from subprocess import STDOUT, PIPE
import logging
import threading

class Task:
    ssh = paramiko.SSHClient()
    username = ""
    password = ""
    hostname = ""
    resources = ""
    file_utilities = FileUtilities
    process_watcher = ProcessWatcher
    logger = logging.getLogger("logger")
    lock = threading.Lock()

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
            p = subprocess.check_output('/root/installpkg.sh {}'.format(rpms[key]))
            for line in str(p).splitlines():
                self.logger.info (line, end="")
            time.sleep(5)

    def installLocalRPMs(self, window, bar, taskitem, resources, rpms):
        p = None
        count = 0
        for key in rpms:
            count += 1;
            bar['value'] = (count/len(rpms.keys()))*100
            
            cwd = os.getcwd()
            self.logger.info('install RPMs {} {}'.format(key, rpms[key]))
            try:
                multilinerpm = rpms[key].split(",")
                if len(multilinerpm) > 0:
                    execstr = ''
                    for line in multilinerpm:
                        if execstr == '':
                            execstr = 'rpm --install {}/{} '.format(resources, line)
                        else:
                            execstr = execstr + '{}/{} '.format(resources, line)
                            
                    taskstr = 'Installing RPM - {}'.format(execstr)
                    self.logger.info(taskstr)
                    taskitem.set(taskstr)                            

                    p = subprocess.check_output('{}'.format(execstr),shell=True)
                    for line in p.splitlines():
                        self.logger.info(line.decode('utf-8'))
                    time.sleep(5)
                else:
                    p = subprocess.check_output('rpm --install {}/{}'.format(resources,rpms[key]),shell=True)
                    for line in p.splitlines():
                        self.logger.info(line.decode('utf-8'))
                    time.sleep(5)
            except Exception as ex:
                self.logger.error("{} : file {}".format(ex,rpms[key]))

    def checkForUserInput(self, string, userinputs):
        rtnstring = string
        for input in userinputs:
            for i in range(len(string.split('%')) -1):
                if input in string:
                    string = string.replace('%'+input+'%',userinputs[input].get(),1)
                    rtnstring = string
        return rtnstring


    def copyFromResourcesLocal(self, window, bar, taskitem, ini_info):
        count = 0
        for key in ini_info.files:
            count += 1;
            bar['value'] = (count/len(ini_info.files.keys()))*100
            window.update_idletasks()
            firstfile = 0
            my_file = Path("{}/{}/{}".format(os.getcwd(),ini_info.resources,key))

            if ini_info.buildtype != 'LINUX':
                # check for user input
                userinput = self.checkForUserInput(ini_info.files[key], ini_info.userinput)
                if(userinput != None):
                    ini_info.files[key] = userinput

            if my_file.is_file():
                taskstr = 'copying and extracting file {} to {}'.format(key, ini_info.files[key])
                self.logger.info(taskstr)
                taskitem.set(taskstr)
                try:
                    if '.' in ini_info.files[key]: # contains a file name
                        dirname = os.path.dirname(os.path.abspath(ini_info.files[key])) # just get the path
                        os.makedirs(dirname, exist_ok = True)
                    else:
                        os.makedirs(ini_info.files[key], exist_ok = True)
                except OSError as error:
                    self.logger.warning("Directory {} can not be created".format(ini_info.files[key]))

                dirtest = key.split('/')
                src = "{}/{}".format(ini_info.resources, key)
                if '.' in ini_info.files[key]: # contains a file name, so do not append a filename from 'key'
                    dst = "{}".format(ini_info.files[key])
                else:
                    if (len(dirtest) > 1):
                        keyname = dirtest[1]
                        dst = "{}/{}".format(ini_info.files[key],keyname)
                    else:
                        dst = "{}/{}".format(ini_info.files[key],key)

                copyfile(src,dst)
                
                filetype ='zip'
                if 'zip' in key:
                    zf = ZipFile(dst)
                    files = zf.namelist()

                elif 'tar.gz' in key:
                    filetype = 'tar.gz'
                    tf = TarFile.open(dst)
                    files = tf.getnames()
                else:
                    files = None                    
                    
                hasdirectory = False
                
                if (files != None):                  
                    for file in files:
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
    
                            os.makedirs(ini_info.files[key] +"/" + filename, exist_ok = True)
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
    
                        if filetype == 'zip':
                            source = zf.open(file)
                        else:
                            source = tf.getmember(file)
                            testagain = source.type
                            if(source.isdir()):
                                os.makedirs(ini_info.files[key] +"/" + file, exist_ok = True)
                                continue
                            else:
                                source = tf.extractfile(source)
                                if(hasdirectory == True):
                                    getfoldername = os.path.dirname(filename)
                                    os.makedirs(ini_info.files[key] +"/" + getfoldername, exist_ok = True)
                            
                        target = open(os.path.join(ini_info.files[key], filename), "wb")                        
    
                        with source, target:
                            shutil.copyfileobj(source, target)
                            target.close()
            else:
                self.logger.error("Error copying file {}/{}, it does not exist".format(ini_info.resources,key))
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
            self.copyFromResourcesLocal(window, bar, taskitem, ini_info)

    def doActionsSSH(self, actions):
        for action in actions:
            if '%host%' in actions[action]:
                actions[action] = actions[action].replace("%host%",self.hostname)
            self.logger.info('Executing Action {} with {}'.format(action, actions[action]))
            stdin, stdout, stderr = self.ssh.exec_command('{}'.format(actions[action]))
            for line in iter(stdout.readline,""):
                self.logger.info (line, end="")                             
    
    # def doActionsLocal(self, window, bar, taskitem, actions, options, userinputs):
    def doActionsLocal(self, window, bar, taskitem, ini_info, final=False):
        count = 0
        actionthread = None
        timeoutval = ini_info.defaultactiontimeout
        
        if final == True:
            ini_info.actions = ini_info.finalactions

        if ini_info.watchdog == True:            
            self.process_watcher.continuewatch = True
            actionthread = threading.Thread(target=self.process_watcher.WatchForSelf, args=(self.process_watcher, "tarpon_installer", int(timeoutval), 3, 3))
            actionthread.start()               

        for action in ini_info.actions:
            timeoutval = ini_info.defaultactiontimeout
            
            if '[timeout =' in ini_info.actions[action]:
                timeoutval = ini_info.actions[action].split(']',maxsplit=1)[0]
                ini_info.actions[action] = ini_info.actions[action].replace(timeoutval+']',"")
                timeoutval = timeoutval.split('=')[1].strip()
                
            # actionthread = threading.Thread(target=self.process_watcher.WatchForPid, args=(self.process_watcher, "python3", int(timeoutval), 3))
            # actionthread.start()
            
            try:
                self.lock.acquire()
                
                count += 1;
                bar['value'] = (count/len(ini_info.actions.keys()))*100
                exec_option = '1'
    
                if '%host%' in ini_info.actions[action]:
                    actions[action] = ini_info.actions[action].replace("%host%",self.hostname)
    
                if 'YESNO' in ini_info.actions[action]:
                    text = ini_info.actions[action].split('::');
                    answer = ynbox(text[1],"User Question");
                    if answer == False:
                        continue;
                    else:
                        ini_info.actions[action] = text[2];
    
                taskstr = 'Executing {} with {}'.format(action, ini_info.actions[action])
                taskitem.set(taskstr)
                
                if action in ini_info.options.keys():
                    exec_option = ini_info.options[action].get()
    
                if(exec_option != '0'):
                    # check for user input
                    userinput = self.checkForUserInput(ini_info.actions[action], ini_info.userinput)
                    if(userinput != None):
                        ini_info.actions[action] = userinput
                        
                        if ini_info.buildtype == 'LINUX':                            
                            p = subprocess.Popen(ini_info.actions[action],shell=True,start_new_session=True)
                            self.process_watcher.pidvalue = p.pid
                            self.logger.info("launching process {} with PID {}".format(ini_info.actions[action], self.process_watcher.pidvalue))
                            p.wait()
                            time.sleep(1)
                        else:                        
                            p = subprocess.run(ini_info.actions[action],shell=True,timeout=300,encoding='utf-8', stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                            
                            for line in str(p.stdout).splitlines():
                                self.logger.info(line)
                                
                            for line in str(p.stderr).splitlines():
                                self.logger.info(line)
                            
            except Exception as e:
                if "Process timed out" in str(e):
                    self.logger.error("Timeout Error in Action {}".format(str(e)))
                    p.kill()
                else:
                    self.logger.error("Error in Action {}".format(str(e)))
                    
                self.lock.release()
                continue                                           
            
            self.lock.release()
            
        if ini_info.watchdog == True:            
            self.process_watcher.continuewatch = False
            actionthread.join()
            

    def doActions(self, window, bar, taskitem, ini_info, type = "action"):
        if(ini_info.installtype == 'REMOTE' and ini_info.buildtype == 'LINUX'):
            self.doActionsSSH(ini_info.actions)
        elif ini_info.installtype == 'LOCAL':
            if(type == "action"):
                self.doActionsLocal(window, bar, taskitem, ini_info)
            elif(type == "final"):
                self.doActionsLocal(window, bar, taskitem, ini_info, True)

    def modifyFilesLocal(self, window, bar, taskitem, files, userinputs):
        count = 0
        for file in files:
            try:              
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
                
                file = self.checkForUserInput(file, userinputs)

                my_file = Path("{}".format(file))

                taskstr = 'Modifying File {} with {}'.format(file, modifywith)
                self.logger.info(taskstr)
                taskitem.set(taskstr)

                if my_file.is_file():
                    modcontent = modifywith.split("||")
                    # check for user input
                    userinput = self.checkForUserInput(modcontent[1], userinputs)                      
                    if ischange:
                        self.file_utilities.modifyFileContents(file, modcontent[0], userinput)
                    else:
                        self.file_utilities.addFileContents(file, modifywith)
                else: # Create File Condition
                    self.file_utilities.createFileAddContents(file,modifywith.split("||"))
                    
            except Exception as ex:
                self.logger.error(ex)
                continue


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
            self.modifyFilesLocal(window, bar, taskitem, ini_info.modify,ini_info.userinput)

    def finalActions(self, window, bar, taskitem, ini_info):
        self.doActions( window, bar, taskitem, ini_info, "final")

    def __init__(self, username, password, hostname, resources):
        self.username = username
        self.password = password
        self.hostname = hostname    
        self.resources = resources
