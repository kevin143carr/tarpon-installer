import time
import timeit
import paramiko
import subprocess
from fileutilities import FileUtilities
from subprocess import PIPE
import logging
import threading

class ProcessManager:
    def __init__(self) -> None:
        self.ssh = paramiko.SSHClient()
        self.username = ""
        self.password = ""
        self.hostname = ""
        self.resources = ""
        self.file_utilities = FileUtilities()
        self.logger = logging.getLogger("logger")
        self.lock = threading.Lock()
    
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

    def _log_subprocess_output(self, stdout: str, stderr: str, debug: bool = False) -> None:
        out_logger = self.logger.debug if debug else self.logger.info
        err_logger = self.logger.debug if debug else self.logger.error

        for line in str(stdout).splitlines():
            if line:
                out_logger(line)

        for line in str(stderr).splitlines():
            if line:
                err_logger(line)
    
    def executeProcsDebug(self, action, watchdog = False, timeout = 180):
        start = timeit.default_timer()
        self.logger.info("ACTION START COMMAND [{}] TIMEOUT [{}s]".format(action, timeout))
        p = subprocess.Popen(action, shell=True, stdout=PIPE, stderr=PIPE,
                             start_new_session=True, text=True)
        self.logger.info("PID [{}] COMMAND [{}]".format(p.pid, action))
        try:
            stdout, stderr = p.communicate(timeout=timeout)
        except subprocess.TimeoutExpired:
            p.kill()
            p.communicate()
            self.logger.error("ACTION TIMEOUT COMMAND [{}]".format(action))
            raise Exception("Process timed out: {}".format(action))

        time.sleep(1)

        if watchdog == True:
            pidval = "PID [{}]".format(p.pid)
            self.checkForWatchdogEvent(pidval, action)
        
        self._log_subprocess_output(stdout, stderr, debug=True)
        elapsed = timeit.default_timer() - start
        self.logger.info("ACTION END COMMAND [{}] RC [{}] ELAPSED [{:.2f}s]".format(action, p.returncode, elapsed))
        return p.returncode            
            
    def executeProcs(self, action, watchdog = False, timeout = 180):
        start = timeit.default_timer()
        self.logger.info("ACTION START COMMAND [{}] TIMEOUT [{}s]".format(action, timeout))
        p = subprocess.Popen(action, shell=True, stdout=PIPE, stderr=PIPE,
                             start_new_session=False, text=True)
        self.logger.info("PID [{}] COMMAND [{}]".format(p.pid, action))
        try:
            stdout, stderr = p.communicate(timeout=timeout)
        except subprocess.TimeoutExpired:
            p.kill()
            p.communicate()
            self.logger.error("ACTION TIMEOUT COMMAND [{}]".format(action))
            raise Exception("Process timed out: {}".format(action))

        time.sleep(1)

        if watchdog == True:
            pidval = "PID [{}]".format(p.pid)
            self.checkForWatchdogEvent(pidval, action)

        self._log_subprocess_output(stdout, stderr, debug=False)
        elapsed = timeit.default_timer() - start
        self.logger.info("ACTION END COMMAND [{}] RC [{}] ELAPSED [{:.2f}s]".format(action, p.returncode, elapsed))
        return p.returncode
