import time
import paramiko
import subprocess
from fileutilities import FileUtilities
from subprocess import PIPE
import logging
import threading

class ProcessManager:
    ssh = paramiko.SSHClient()
    username = ""
    password = ""
    hostname = ""
    resources = ""
    file_utilities = FileUtilities()
    logger = logging.getLogger("logger")
    lock = threading.Lock()
    
    def checkForWatchdogEvent(self,pid, action):
        watchdogfile = open('tarpon_watchdog.log','r')
        lines = watchdogfile.readlines()
        
        for line in lines:
            if pid in line:
                print("watchdog event occured - re-issueing command {}".format(action))
                self.logger.error("watchdog event occured - re-issueing command in Action {}".format(action))
                watchdogfile.close()
                self.executeProcs(action, True)
                
        watchdogfile.close()    
    
    def executeProcsDebug(self, action, watchdog = False):
        p = subprocess.Popen(action,shell=True, stdout=PIPE, stderr=PIPE, 
                             start_new_session=True, encoding='utf-8')
        self.logger.info("PID [{}] COMMAND [{}]".format(p.pid,action))
        p.wait()
        
        time.sleep(1)

        if watchdog == True:
            pidval = "PID [{}]".format(p.pid)
            self.checkForWatchdogEvent(pidval, action)
        
        stdout,stderr = p.communicate(timeout=180)
        
        for line in str(stdout).splitlines():
            self.logger.debug(line)
                
        for line in str(stderr).splitlines():
            self.logger.debug(line)
            
        return p.returncode            
            
    def executeProcs(self, action, watchdog = False):
        p = subprocess.Popen(action,shell=True, stdout=None, stderr=None, 
                             start_new_session=False, encoding=None)
        self.logger.info("PID [{}] COMMAND [{}]".format(p.pid,action))
        p.wait()
        
        time.sleep(1)

        if watchdog == True:
            pidval = "PID [{}]".format(p.pid)
            self.checkForWatchdogEvent(pidval, action)
            
        return p.returncode