import psutil
import time
import logging

class ProcessWatcher:
    continuewatch = True
    defaulttimeout = 10
    pidvalue = 0
    currenttimeout = 0;
    logger = logging.getLogger("logger")
         
    def KillByName(self, name):
        for proc in psutil.process_iter(['pid','name','username']):
            if name in proc.info["name"]:
                self.logger.info("Match Found - killing process [{}] with PID [{}]".format(proc.info["name"],proc.info["pid"]))
                print("Match Found - killing process [{}] with PID [{}]".format(proc.info["name"],proc.info["pid"]))
                proc.kill()
            time.sleep(0.0100)
            
            
    def WatchForSelf(self,name, timeout, delay, maxprocs):
        proccount = 0;
        procset = dict()
        delset = set()
        while(self.continuewatch == True):
            for proc in psutil.process_iter(['pid','name','cmdline']):
                if name in proc.info["name"]:
                    self.logger.debug("process info name:{} proccount:{}".format(name, proccount))
                    activepid = int(proc.info['pid'])
                    
                    if activepid not in procset:
                        if proccount < maxprocs:
                            procset[activepid] = 'Y'
                        else:
                            procset[activepid] = 'N'
                            
                        proccount += 1                    
                        
                    if proccount > maxprocs:
                        if self.currenttimeout > timeout:
                            for proccers in procset:
                                if procset[proccers] == 'N':
                                    p = psutil.Process(int(proccers))
                                    self.logger.info("PID [{}] COMMAND [{}] timed out. Killing Process".format(p.pid, p.cmdline))
                                    p.kill()
                                    delset.add(int(proccers))
                                    proccount -= 1
                            
                            for deletethis in delset:
                                del procset[deletethis]
                                
                            delset.clear();
                            self.currenttimeout = 0
                        else:                     
                            self.currenttimeout += delay                                           
                    
                        time.sleep(delay)            
                time.sleep(0.0100)            