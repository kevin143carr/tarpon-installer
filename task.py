#!/usr/bin/env python3
import paramiko
import os
import shutil
import tkinter as tk
from ttkbootstrap import ttk
from zipfile import ZipFile
from tarfile import TarFile
from shutil import copyfile
from pathlib import Path
from fileutilities import FileUtilities
from iniinfo import iniInfo
from managers.actionmanager import ActionManager
from stringutilities import StringUtilities
import logging
import threading

class Task:
    ssh = paramiko.SSHClient()
    username = ""
    password = ""
    hostname = ""
    resources = ""
    file_utilities = FileUtilities()
    action_manager =  ActionManager()
    string_utilities =  StringUtilities()
    logger = logging.getLogger("logger")
    lock = threading.Lock()

    def loginSSH(self) -> None:
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh.connect(hostname = self.hostname, username = self.username, password = self.password)

    def copyFromResourcesLocal(self, window, bar: ttk.Progressbar, taskitem: tk.StringVar, ini_info: iniInfo) -> None:
        count = 0
        for key in ini_info.files:
            count += 1;
            bar['value'] = (count/len(ini_info.files.keys()))*100
            window.update_idletasks()
            firstfile = 0
            my_file = Path("{}/{}/{}".format(os.getcwd(),ini_info.resources,key))

            if ini_info.buildtype != 'LINUX':
                # check for user input
                userinput = self.string_utilities.checkForUserVariable(ini_info.files[key], ini_info)
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
                except OSError:
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

    def copyFromResourcesSSH(self, resources, files) -> None:
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

    def copyFromResources(self, window, bar: ttk.Progressbar, taskitem, ini_info: iniInfo) -> None:
        if(ini_info.installtype == 'REMOTE' and ini_info.buildtype == 'LINUX'):
            self.copyFromResourcesSSH(ini_info.resources, ini_info.files)
        elif ini_info.installtype == 'LOCAL':
            self.copyFromResourcesLocal(window, bar, taskitem, ini_info)                                                                   
            
    def doActions(self, window, bar: ttk.Progressbar, taskitem: tk.StringVar, ini_info: iniInfo, actiontype: str = "action") -> None:
        if(ini_info.installtype == 'REMOTE' and ini_info.buildtype == 'LINUX'):
            ActionManager.doActionsSSH(ini_info.actions)
        elif ini_info.installtype == 'LOCAL':
            try:                
                if(actiontype == "action"):
                    self.action_manager.doActionsLocal(window, bar, taskitem, ini_info)
                elif(actiontype == "final"):
                    self.action_manager.doActionsLocal(window, bar, taskitem, ini_info, True)
            except Exception as e:
                self.logger.error(e)

    def modifyFilesLocal(self, window, bar: ttk.Progressbar, taskitem: tk.StringVar, ini_info: iniInfo) -> None:
        count = 0
        files = ini_info.modify
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
                
                file = self.string_utilities.checkForUserVariable(file, ini_info)

                my_file = Path("{}".format(file))

                taskstr = 'Modifying File {} with {}'.format(file, modifywith)
                self.logger.info(taskstr)
                taskitem.set(taskstr)

                if my_file.is_file():
                    modcontent = modifywith.split("||")
                    # check for user input
                    userinput = self.string_utilities.checkForUserVariable(modcontent[1], ini_info)                      
                    if ischange:
                        self.file_utilities.modifyFileContents(file, modcontent[0], userinput)
                    else:
                        self.file_utilities.addFileContents(file, modifywith)
                else: # Create File Condition
                    self.file_utilities.createFileAddContents(file,modifywith.split("||"))
                    
            except Exception as ex:
                self.logger.error(ex)
                continue


    def modifyFilesSSH(self, files) -> None:
        for file in files:
            result = files[file].split("||")
            file = file.split("-",1)
            stdin, stdout, stderr = self.ssh.exec_command('sed -i \"s/{}/{}/g\" {}'.format(result[0],result[1],file[1]))
            for line in iter(stderr.readline,""):
                self.logger.info (line, end="")

    def modifyFiles(self, window, bar, taskitem, ini_info: iniInfo) -> None:
        if(ini_info.installtype == 'REMOTE' and ini_info.buildtype == 'LINUX'):
            self.modifyFilesSSH(ini_info.modify)
        else:
            self.modifyFilesLocal(window, bar, taskitem, ini_info)

    def finalActions(self, window, bar, taskitem, ini_info: iniInfo) -> None:
        self.doActions( window, bar, taskitem, ini_info, "final")

    def __init__(self, username, password, hostname, resources):
        self.username = username
        self.password = password
        self.hostname = hostname    
        self.resources = resources
