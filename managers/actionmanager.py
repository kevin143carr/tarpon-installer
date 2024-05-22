from tkinter import messagebox as msgbox
import logging
import threading
from managers.processmanager import ProcessManager
from tarpl.tarplapi import TarpL
from tarpl.tarplapi import TarpLreturn
from tarpl.tarplclasses import TarpLAPIEnum
from stringutilities import StringUtilities


class ActionManager:
    logger = logging.getLogger("logger")
    process_manager = ProcessManager()
    string_utilities =  StringUtilities()
    _tarpL = TarpL()
    lock = threading.Lock()
    
    def doActionsSSH(self, actions):
        for action in actions:
            if '%host%' in actions[action]:
                actions[action] = actions[action].replace("%host%",self.hostname)
            self.logger.info('Executing Action {} with {}'.format(action, actions[action]))
            stdin, stdout, stderr = self.ssh.exec_command('{}'.format(actions[action]))
            for line in iter(stdout.readline,""):
                self.logger.info (line, end="")        


    def doActionsLocal(self, window, bar, taskitem, ini_info, final=False):
        count = 0
        enablegoto = False
        gotoindex = ""
    
        if final == True:
            ini_info.actions = ini_info.finalactions         
    
        for action in ini_info.actions:
            if enablegoto:
                if gotoindex != action:
                    continue
                else:
                    gotoindex = ""
                    enablegoto = False
                
            tarpLrtn = TarpLreturn()            
    
            try:
                self.lock.acquire()
    
                count += 1;
                bar['value'] = (count/len(ini_info.actions.keys()))*100
                exec_option = '1'
    
                if '%host%' in ini_info.actions[action]:
                    ini_info.actions[action] = ini_info.actions[action].replace("%host%",ini_info.host)

                # check for user input otherwise it returns string in ini_info.actions[action]
                finalstr = self.string_utilities.checkForUserVariable(ini_info.actions[action], ini_info)

                if action in ini_info.options.keys():
                    exec_option = ini_info.optionvals[action].get()
                    
                if(exec_option != '0'):
                    isTarpL = self._tarpL.CheckForTarpL(finalstr)
                    text = finalstr.split('::');
                    if (isTarpL == True):
                        tarpLrtn = self._tarpL.ExecuteTarpL(finalstr, window)
                        if tarpLrtn.rtnstate == False:
                            self.lock.release()
                            continue;
                        else:
                            if tarpLrtn.rtnvar != "":
                                if tarpLrtn.tarpltype == TarpLAPIEnum.IFGOTO:
                                    finalstr = tarpLrtn.rtnvalue
                                    gotoindex = tarpLrtn.rtnvar
                                else: # This ends up setting a variable, so no execution is needed
                                    ini_info.returnvars[tarpLrtn.rtnvar] = tarpLrtn.rtnvalue                                    
                                    self.lock.release()
                                    continue
                            else:
                                finalstr = tarpLrtn.rtnvalue;
                               
                    taskstr = 'Executing {} with {}'.format(action, finalstr)
                    taskitem.set(taskstr)  
    
                    if(finalstr != None):
                        if self.logger.level == logging.DEBUG:
                            self.process_manager.executeProcsDebug(finalstr, ini_info.watchdog)
                        else:
                            result = self.process_manager.executeProcs(finalstr, ini_info.watchdog)
                            if tarpLrtn.tarpltype == TarpLAPIEnum.IFGOTO:
                                if result == 0:
                                    enablegoto = True
                                    self.lock.release()
                                    continue
                                else:
                                    enablegoto = False
                                    self.lock.release()
                                    continue
                    else:
                        continue
    
            except Exception as e:
                if "Process timed out" in str(e):
                    ActionManager.logger.error("Timeout Error in Action {}".format(str(e)))
                else:
                    ActionManager.logger.error("Error in Action {}".format(str(e)))
    
                self.lock.release()
                continue                                           
    
            self.lock.release()