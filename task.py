#!/usr/bin/env python3
import os
import sys
import shutil
import tarfile
import threading
import logging
import shlex
from pathlib import Path
from shutil import copyfile
from typing import Iterable, Optional

import paramiko
import tkinter as tk
if sys.version_info[:3] < (3, 9):
    try:
        from ttkbootstrap import ttk
    except ImportError:
        import ttkbootstrap as ttk
else:
    import ttkbootstrap as ttk
from zipfile import ZipFile

from fileutilities import FileUtilities
from iniinfo import iniInfo
from managers.actionmanager import ActionManager
from stringutilities import StringUtilities
from ui_thread import set_bar_value, set_var, update_idletasks

class Task:
    def __init__(self, ini_info: iniInfo):
        self.ssh = paramiko.SSHClient()
        self.username = ini_info.username
        self.password = ini_info.password
        self.hostname = ini_info.hostname
        self.resources = ini_info.resources
        self.file_utilities = FileUtilities()
        self.action_manager = ActionManager()
        self.string_utilities = StringUtilities()
        self.logger = logging.getLogger("logger")
        self.lock = threading.Lock()

    def _handle_step_error(self, ini_info: iniInfo, message: str, ex: Exception) -> None:
        error_message = "{}: {}".format(message, ex)
        self.logger.error(error_message)
        if not getattr(ini_info, "continuewitherrors", False):
            raise ex

    def _set_progress(self, window, bar: ttk.Progressbar, count: int, total: int) -> None:
        if total <= 0:
            set_bar_value(window, bar, 0)
            return
        set_bar_value(window, bar, (count / total) * 100)
        update_idletasks(window)

    def loginSSH(self) -> None:
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh.connect(hostname = self.hostname, username = self.username, password = self.password)

    def copyFromResourcesLocal(self, window, bar: ttk.Progressbar, taskitem: tk.StringVar, ini_info: iniInfo) -> None:
        count = 0
        resources_path = Path(ini_info.resources)
        if not resources_path.is_absolute():
            resources_path = Path.cwd() / resources_path
        for key in ini_info.files:
            try:
                count += 1;
                self._set_progress(window, bar, count, len(ini_info.files.keys()))
                firstfile = 0
                my_file = resources_path / key
                destination = self.string_utilities.checkForUserVariable(ini_info.files[key], ini_info)
                if destination is None:
                    destination = ini_info.files[key]

                if my_file.is_file():
                    taskstr = 'copying and extracting file {} to {}'.format(key, destination)
                    self.logger.info(taskstr)
                    set_var(window, taskitem, taskstr)
                    try:
                        if '.' in destination: # contains a file name
                            dirname = os.path.dirname(os.path.abspath(destination)) # just get the path
                            os.makedirs(dirname, exist_ok = True)
                        else:
                            os.makedirs(destination, exist_ok = True)
                    except OSError:
                        self.logger.warning("Directory {} can not be created".format(destination))

                    dirtest = key.split('/')
                    src = str(resources_path / key)
                    if '.' in destination: # contains a file name, so do not append a filename from 'key'
                        dst = "{}".format(destination)
                    else:
                        if (len(dirtest) > 1):
                            keyname = dirtest[1]
                            dst = "{}/{}".format(destination,keyname)
                        else:
                            dst = "{}/{}".format(destination,key)

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
        
                                os.makedirs(destination +"/" + filename, exist_ok = True)
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
                                    os.makedirs(destination +"/" + file, exist_ok = True)
                                    continue
                                else:
                                    source = tf.extractfile(source)
                                    if(hasdirectory == True):
                                        getfoldername = os.path.dirname(filename)
                                        os.makedirs(destination +"/" + getfoldername, exist_ok = True)
                                
                            target = open(os.path.join(destination, filename), "wb")
        
                            with source, target:
                                shutil.copyfileobj(source, target)
                                target.close()
                else:
                    self.logger.error("Error copying file {}/{}, it does not exist".format(ini_info.resources,key))
            except Exception as ex:
                self._handle_step_error(ini_info, "Error copying file {}".format(key), ex)
                continue

    def copyFromResourcesSSH(self, resources, files, ini_info: iniInfo) -> None:
        ftp = self.ssh.open_sftp()
        resources_path = Path(resources)
        if not resources_path.is_absolute():
            resources_path = Path.cwd() / resources_path
        for key in files:
            destination = self.string_utilities.checkForUserVariable(files[key], ini_info)
            if destination is None:
                destination = files[key]
            my_file = resources_path / key
            if my_file.is_file():
                self.logger.info('copying and extracting file {} to {}'.format(key, destination))
                self.ssh.exec_command('mkdir -p {}'.format(destination))
                dirtest = key.split('/')
                src = str(resources_path / key)
                if '.' in destination: # contains a file name, so do not append a filename from 'key'
                    dst = "{}".format(destination)
                else:
                    if (len(dirtest) > 1):
                        keyname = dirtest[1]
                        dst = "{}/{}".format(destination,keyname)
                    else:
                        dst = "{}/{}".format(destination,key)

                if(os.path.exists(src) == False):
                    self.logger.error("Error could not find this file: {}".format(src))
                    continue

                ftp.put(src , dst)

                if 'zip' in key:
                    stdin, stdout, stderr = self.ssh.exec_command('unzip -o {}/{} -d {}'.format(destination,key,destination))
                    for line in iter(stdout.readline,""):
                        self.logger.info (line, end="")
            else:
                self.logger.error("Error copying file {}/{}, it does not exist".format(resources,key))
        ftp.close()

    def copyFromResources(self, window, bar: ttk.Progressbar, taskitem, ini_info: iniInfo) -> None:
        if(ini_info.installtype == 'REMOTE' and ini_info.buildtype == 'LINUX'):
            self.copyFromResourcesSSH(ini_info.resources, ini_info.files, ini_info)
        elif ini_info.installtype == 'LOCAL':
            self.copyFromResourcesLocal(window, bar, taskitem, ini_info)                                                                   
            
    def doActions(self, window, bar: ttk.Progressbar, taskitem: tk.StringVar, ini_info: iniInfo, actiontype: str = "action") -> None:
        if(ini_info.installtype == 'REMOTE' and ini_info.buildtype == 'LINUX'):
            self.action_manager.ssh = self.ssh
            self.action_manager.hostname = self.hostname
            actions = ini_info.finalactions if actiontype == "final" else ini_info.actions
            self.action_manager.doActionsSSH(window, bar, taskitem, actions, ini_info)
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
                count += 1
                self._set_progress(window, bar, count, len(files.keys()))

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
                set_var(window, taskitem, taskstr)

                if my_file.is_file():
                    modcontent = modifywith.split("||")
                    if ischange:
                        # CHANGE entries are "old||new"; only the replacement side gets token expansion.
                        userinput = self.string_utilities.checkForUserVariable(modcontent[1], ini_info)
                        self.file_utilities.modifyFileContents(file, modcontent[0], userinput)
                    else:
                        addcontent = self.string_utilities.checkForUserVariable(modifywith, ini_info)
                        self.file_utilities.addFileContents(file, addcontent)
                else: # Create File Condition
                    addcontent = self.string_utilities.checkForUserVariable(modifywith, ini_info)
                    self.file_utilities.createFileAddContents(file, addcontent.split("||"))
                    
            except Exception as ex:
                self.logger.error(ex)
                continue


    def modifyFilesSSH(self, files, ini_info: iniInfo) -> None:
        for key, raw_instruction in files.items():
            try:
                instruction = self.string_utilities.checkForUserVariable(raw_instruction, ini_info)
                if instruction is None:
                    instruction = raw_instruction
                if not instruction.startswith("{FILE}"):
                    self.logger.error("Invalid remote MODIFY entry '%s': missing {FILE} prefix", key)
                    continue

                if "{CHANGE}" in instruction:
                    file_part, payload = instruction.split("{CHANGE}", 1)
                    is_change = True
                elif "{ADD}" in instruction:
                    file_part, payload = instruction.split("{ADD}", 1)
                    is_change = False
                else:
                    self.logger.error("Invalid remote MODIFY entry '%s': missing {CHANGE} or {ADD}", key)
                    continue

                remote_file = file_part[len("{FILE}") :].strip()
                remote_file = self.string_utilities.checkForUserVariable(remote_file, ini_info) or remote_file
                if not remote_file:
                    self.logger.error("Invalid remote MODIFY entry '%s': empty target path", key)
                    continue

                remote_dir = os.path.dirname(remote_file)
                if remote_dir:
                    self.ssh.exec_command("mkdir -p {}".format(shlex.quote(remote_dir)))

                if is_change:
                    parts = payload.split("||", 1)
                    if len(parts) < 2:
                        self.logger.error("Invalid remote CHANGE entry '%s': expected old||new", key)
                        continue
                    old_value, new_value = parts[0], parts[1]
                    command = (
                        "if [ -f {file} ]; then sed -i 's|{old}|{new}|g' {file}; "
                        "else printf '%s\\n' {new_q} > {file}; fi"
                    ).format(
                        file=shlex.quote(remote_file),
                        old=old_value.replace("|", "\\|").replace("'", "'\"'\"'"),
                        new=new_value.replace("|", "\\|").replace("'", "'\"'\"'"),
                        new_q=shlex.quote(new_value),
                    )
                else:
                    lines = payload.split("||")
                    line_payload = " ".join(shlex.quote(line) for line in lines if line != "")
                    if line_payload == "":
                        continue
                    command = "printf '%s\\n' {} >> {}".format(line_payload, shlex.quote(remote_file))

                stdin, stdout, stderr = self.ssh.exec_command(command)
                for line in iter(stdout.readline, ""):
                    self.logger.info(line, end="")
                for line in iter(stderr.readline, ""):
                    self.logger.info(line, end="")
            except Exception as ex:
                self._handle_step_error(ini_info, "Error modifying remote file {}".format(key), ex)
                continue

    def modifyFiles(self, window, bar, taskitem, ini_info: iniInfo) -> None:
        if(ini_info.installtype == 'REMOTE' and ini_info.buildtype == 'LINUX'):
            self.modifyFilesSSH(ini_info.modify, ini_info)
        else:
            self.modifyFilesLocal(window, bar, taskitem, ini_info)

    def finalActions(self, window, bar, taskitem, ini_info: iniInfo) -> None:
        self.doActions( window, bar, taskitem, ini_info, "final")

    def runDiagnostics(self, window, bar, taskitem, ini_info: iniInfo):
        if not getattr(ini_info, "usediagnostics", False):
            return []
        if ini_info.installtype == 'REMOTE' and ini_info.buildtype == 'LINUX':
            self.logger.warning("Diagnostics are not implemented for remote installs")
            return []
        return self.action_manager.runDiagnosticsLocal(window, bar, taskitem, ini_info)

 
