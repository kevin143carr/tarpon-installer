import sys
from processwatcher import ProcessWatcher
import logging
import os.path
from os import path
from elevate import elevate
import threading

version = "1.0.2"
timeoutval = 10

class mainClass:
    process_watcher = ProcessWatcher
    
    def EnableWatchdog(self, processname, numprocesses,timeoutval):
        self.process_watcher.continuewatch = True
        actionthread = threading.Thread(target=self.process_watcher.WatchForSelf, args=(self.process_watcher, processname, int(timeoutval), 3, numprocesses))
        actionthread.start()                    
        actionthread.join() 
        self.process_watcher.continuewatch = False
        
    def KillWatchdog(self, name):
        logger.info("Attempting to kill process [{}]".format(name))
        print("Attempting to kill process [{}]".format(name))
        self.process_watcher.KillByName(self.process_watcher, name)
        raise SystemExit

def PrintHelp():
    print("************************************************************************")
    print("*  ><###> Tarpon Watch Dog <###>< Watches for Zombie Processes         *")
    print("*                                                                      *")
    print("*                                                                      *")
    print("*                                                                      *")
    print("* Usage: watchdog -p nameofprocess  -n num_processes_allowed -t timeout*")
    print("* To Kill Watchdog:  watchdog -k nameofprocess                         *")
    print("*                                                                      *")
    print("*                                                                      *")
    print("*  VERSION {}                                                          *".format(version))
    print("************************************************************************")
    raise SystemExit

def isAdmin():
    try:
        is_admin = (os.getuid() == 0)
    except AttributeError:
        is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
    return is_admin


if __name__ == "__main__":
    params = {}
    option = ""
    processname = None
    numprocesses = None
    killwatchdog = False

    logger = logging.getLogger("logger")
    
    for arg in sys.argv:
        if arg[0:1] == "-":
            option = arg
        else:
            params[option] = arg  

    if len(sys.argv) < 2:
        PrintHelp()

    if len(sys.argv) > 4:            
        if "-n" in params:
            numprocesses = params["-n"]
    
        if "-p" in params:
            processname = params["-p"]
            
        if "-t" in params:
            timeoutval = params["-t"]                       
    elif "-k" in params:
        killwatchdog = True
    else:
        PrintHelp()
        
    
    logging.basicConfig(filename="tarpon_watchdog.log", filemode='w', level = logging.INFO)        

    for item in params:
        logger.info("parameter {}".format(params[item]))

    if isAdmin():
        logger.info("Executing as Administrator")
    else:
        logger.info("Elevating Permissions because Administrator = {}".format(isAdmin()))
        elevate(graphical = False)
    
    mc = mainClass()
    if killwatchdog == True:
        mc.KillWatchdog(params["-k"]); 
    else:
        mc.EnableWatchdog(processname,int(numprocesses),int(timeoutval)); 