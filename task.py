#!/usr/bin/env python3
import os
import sys
import shutil
import tarfile
import threading
import logging
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

class Task:
    def __init__(self, ini_info: iniInfo):
        self.ssh = paramiko.SSHClient()
        self.username = ini_info.username
        self.password = ini_info.password
        self.hostname = getattr(ini_info, "host", "")
        self.resources = ini_info.resources
        self.file_utilities = FileUtilities()
        self.action_manager = ActionManager()
        self.string_utilities = StringUtilities()
        self.logger = logging.getLogger("logger")
        self.lock = threading.Lock()

    def loginSSH(self) -> None:
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh.connect(hostname=self.hostname, username=self.username, password=self.password)

    def _set_progress(self, window, bar: ttk.Progressbar, count: int, total: int) -> None:
        if total <= 0:
            return
        bar['value'] = (count / total) * 100
        window.update_idletasks()

    def _is_file_target(self, target: str) -> bool:
        target_path = Path(target)
        return bool(target_path.suffix) and not target.endswith(os.sep)

    def _build_copy_paths(self, resources: str, key: str, target: str) -> tuple[str, str]:
        dirtest = key.split('/')
        src = f"{resources}/{key}"
        if self._is_file_target(target):
            dst = target
        else:
            if len(dirtest) > 1:
                keyname = dirtest[1]
                dst = f"{target}/{keyname}"
            else:
                dst = f"{target}/{key}"
        return src, dst

    def _strip_first_component(self, path: str) -> str:
        parts = [p for p in path.split('/') if p]
        if len(parts) <= 1:
            return path
        return "/".join(parts[1:])

    def _extract_archive(self, archive_path: str, dest_dir: str) -> None:
        lower_name = archive_path.lower()
        if lower_name.endswith(".zip"):
            with ZipFile(archive_path) as zf:
                self._extract_zip(zf, dest_dir)
            return

        if lower_name.endswith(".tar.gz") or lower_name.endswith(".tgz"):
            with tarfile.open(archive_path) as tf:
                self._extract_tar(tf, dest_dir)
            return

    def _extract_zip(self, zf: ZipFile, dest_dir: str) -> None:
        members = zf.namelist()
        if not members:
            return

        has_directory = "/" in members[0]
        for member in members:
            if member.endswith("/"):
                target_dir = self._strip_first_component(member) if has_directory else member
                os.makedirs(os.path.join(dest_dir, target_dir), exist_ok=True)
                continue

            target_name = self._strip_first_component(member) if has_directory else member
            target_path = os.path.join(dest_dir, target_name)
            os.makedirs(os.path.dirname(target_path), exist_ok=True)
            with zf.open(member) as source, open(target_path, "wb") as target:
                shutil.copyfileobj(source, target)

    def _extract_tar(self, tf: tarfile.TarFile, dest_dir: str) -> None:
        members = tf.getmembers()
        if not members:
            return

        has_directory = "/" in members[0].name
        for member in members:
            if member.isdir():
                target_dir = self._strip_first_component(member.name) if has_directory else member.name
                os.makedirs(os.path.join(dest_dir, target_dir), exist_ok=True)
                continue

            target_name = self._strip_first_component(member.name) if has_directory else member.name
            target_path = os.path.join(dest_dir, target_name)
            os.makedirs(os.path.dirname(target_path), exist_ok=True)
            source = tf.extractfile(member)
            if source is None:
                continue
            with source, open(target_path, "wb") as target:
                shutil.copyfileobj(source, target)

    def copyFromResourcesLocal(self, window, bar: ttk.Progressbar, taskitem: tk.StringVar, ini_info: iniInfo) -> None:
        count = 0
        for key in ini_info.files:
            count += 1
            self._set_progress(window, bar, count, len(ini_info.files.keys()))
            my_file = Path("{}/{}/{}".format(os.getcwd(), ini_info.resources, key))

            if ini_info.buildtype != 'LINUX':
                # check for user input
                userinput = self.string_utilities.checkForUserVariable(ini_info.files[key], ini_info)
                if userinput is not None:
                    ini_info.files[key] = userinput

            if my_file.is_file():
                taskstr = 'copying and extracting file {} to {}'.format(key, ini_info.files[key])
                self.logger.info(taskstr)
                taskitem.set(taskstr)
                try:
                    if self._is_file_target(ini_info.files[key]): # contains a file name
                        dirname = os.path.dirname(os.path.abspath(ini_info.files[key])) # just get the path
                        os.makedirs(dirname, exist_ok=True)
                    else:
                        os.makedirs(ini_info.files[key], exist_ok=True)
                except OSError:
                    self.logger.warning("Directory {} can not be created".format(ini_info.files[key]))

                src, dst = self._build_copy_paths(ini_info.resources, key, ini_info.files[key])

                copyfile(src, dst)
                self._extract_archive(dst, ini_info.files[key])
            else:
                self.logger.error("Error copying file {}/{}, it does not exist".format(ini_info.resources,key))

    def copyFromResourcesSSH(self, resources, files) -> None:
        ftp = self.ssh.open_sftp()
        for key in files:
            my_file = Path("{}/{}".format(resources, key))
            if my_file.is_file():
                self.logger.info('copying and extracting file {} to {}'.format(key, files[key]))
                self.ssh.exec_command('mkdir -p {}'.format(files[key]))
                src, dst = self._build_copy_paths(resources, key, files[key])

                if os.path.exists("{}/{}".format(os.getcwd(), src)) is False:
                    self.logger.error("Error could not find this file: {}/{}".format(os.getcwd(), src))
                    continue

                ftp.put(src, dst)

                if key.lower().endswith(".zip"):
                    stdin, stdout, stderr = self.ssh.exec_command(
                        'unzip -o {}/{} -d {}'.format(files[key], key, files[key])
                    )
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
            self.action_manager.ssh = self.ssh
            self.action_manager.hostname = self.hostname
            self.action_manager.doActionsSSH(ini_info.actions)
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
            stdin, stdout, stderr = self.ssh.exec_command(
                'sed -i \"s/{}/{}/g\" {}'.format(result[0], result[1], file[1])
            )
            for line in iter(stderr.readline,""):
                self.logger.info (line, end="")

    def modifyFiles(self, window, bar, taskitem, ini_info: iniInfo) -> None:
        if(ini_info.installtype == 'REMOTE' and ini_info.buildtype == 'LINUX'):
            self.modifyFilesSSH(ini_info.modify)
        else:
            self.modifyFilesLocal(window, bar, taskitem, ini_info)

    def finalActions(self, window, bar, taskitem, ini_info: iniInfo) -> None:
        self.doActions( window, bar, taskitem, ini_info, "final")
