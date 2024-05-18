import time
import subprocess
from fileutilities import FileUtilities
from managers.processmanager import ProcessManager
import logging

class RpmManager:
    file_utilities = FileUtilities
    process_manager =  ProcessManager
    logger = logging.getLogger("logger")
    
    def installRPMsRemote(self, resources, rpms):
        for key in rpms:
            self.logger.info('install RPMs {} to {}'.format(key, rpms[key]))
            p = subprocess.check_output('/root/installpkg.sh {}'.format(rpms[key]))
            for line in str(p).splitlines():
                self.logger.info (line, end="")
            time.sleep(5)
            
    def installLocalRPMs(self, window, bar, taskitem, resources, rpms, watchdog):
        p = None
        count = 0
        for key in rpms:
            count += 1;
            bar['value'] = (count/len(rpms.keys()))*100
            
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
                taskitem.set(taskstr)
                
                self.process_manager.executeProcs(execstr, watchdog)
                    
            except Exception as ex:
                self.logger.error("{} : file {}".format(ex,rpms[key]))    