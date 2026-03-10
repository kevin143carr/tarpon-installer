import time
import subprocess
import os
import shlex
from pathlib import Path
from fileutilities import FileUtilities
from managers.processmanager import ProcessManager
import logging
from typing import Optional
from ui_thread import set_bar_value, set_var

class RpmManager:
    def __init__(self) -> None:
        self.file_utilities = FileUtilities()
        self.process_manager = ProcessManager()
        self.logger = logging.getLogger("logger")
    
    def _run_remote_checked(self, ssh, command: str) -> tuple[int, str, str]:
        stdin, stdout, stderr = ssh.exec_command(command)
        rc = stdout.channel.recv_exit_status()
        out = stdout.read().decode("utf-8", errors="replace").strip()
        err = stderr.read().decode("utf-8", errors="replace").strip()
        return rc, out, err

    def installRemoteRPMs(self, ssh, resources, rpms):
        resources_path = Path(resources)
        if not resources_path.is_absolute():
            resources_path = Path.cwd() / resources_path

        staging_dir = "/tmp/tarpon-installer-rpms"
        rc, _, err = self._run_remote_checked(ssh, "mkdir -p {}".format(shlex.quote(staging_dir)))
        if rc != 0:
            raise RuntimeError("Unable to create remote RPM staging directory {}: {}".format(staging_dir, err))

        ftp = ssh.open_sftp()
        try:
            for key in rpms:
                self.logger.info("install RPMs %s %s", key, rpms[key])
                entries = [entry.strip() for entry in str(rpms[key]).split(",") if entry.strip()]
                if not entries:
                    continue

                rpm_entries = [entry for entry in entries if entry.lower().endswith(".rpm")]
                package_entries = [entry for entry in entries if not entry.lower().endswith(".rpm")]

                staged_files = []
                for rpm_entry in rpm_entries:
                    local_rpm = resources_path / rpm_entry
                    if not local_rpm.is_file():
                        raise FileNotFoundError("Could not find RPM file '{}'".format(local_rpm))
                    remote_rpm = "{}/{}".format(staging_dir, os.path.basename(rpm_entry))
                    ftp.put(str(local_rpm), remote_rpm)
                    staged_files.append(remote_rpm)

                if staged_files:
                    localinstall_list = " ".join(shlex.quote(path) for path in staged_files)
                    install_cmd = (
                        "if command -v dnf >/dev/null 2>&1; then "
                        "sudo dnf install -y --disablerepo='*' --allowerasing --nogpgcheck {rpms}; "
                        "elif command -v yum >/dev/null 2>&1; then "
                        "sudo yum localinstall -y --disablerepo='*' {rpms}; "
                        "else echo 'Neither dnf nor yum found'; exit 1; fi"
                    ).format(rpms=localinstall_list)
                    rc, out, err = self._run_remote_checked(ssh, install_cmd)
                    if out:
                        self.logger.info(out)
                    if err:
                        self.logger.error(err)
                    if rc != 0:
                        raise RuntimeError("Remote RPM install failed for '{}': rc={}".format(key, rc))

                if package_entries:
                    raise RuntimeError(
                        "Remote RPM entry '{}' contains package names {}. Offline mode requires explicit .rpm filenames only.".format(
                            key,
                            package_entries,
                        )
                    )
        finally:
            ftp.close()
            
    def installLocalRPMs(self, window, bar, taskitem, resources, rpms, watchdog, timeout: Optional[int] = 180):
        p = None
        count = 0
        for key in rpms:
            count += 1;
            set_bar_value(window, bar, (count/len(rpms.keys()))*100)
            
            self.logger.info('install RPMs {} {}'.format(key, rpms[key]))
            try:
                multilinerpm = rpms[key].split(",")
                execstr = ''
                for line in multilinerpm:
                    if execstr == '':
                        execstr = 'rpm --install {}/{} '.format(resources, line)
                    else:
                        execstr = execstr + '{}/{} '.format(resources, line)
                        
                taskstr = 'Installing RPM - {}'.format(execstr)
                self.logger.info(taskstr)
                set_var(window, taskitem, taskstr)
                
                self.process_manager.executeProcs(execstr, watchdog, timeout)
                    
            except Exception as ex:
                self.logger.error("{} : file {}".format(ex,rpms[key]))    
