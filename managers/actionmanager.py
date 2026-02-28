from tkinter import messagebox as msgbox
import logging
import threading
from managers.processmanager import ProcessManager
from iniinfo import iniInfo
from tarpl.tarplapi import TarpL
from tarpl.tarplapi import TarpLreturn
from tarpl.tarplclasses import TarpLAPIEnum
from stringutilities import StringUtilities
from ui_thread import set_bar_value, set_var


class ActionManager:
    """ This class handles the action portions of the .ini file """
    def __init__(self) -> None:
        self.logger = logging.getLogger("logger")
        self.process_manager = ProcessManager()
        self.string_utilities = StringUtilities()
        self._tarpL = TarpL()
        self.lock = threading.Lock()
        self.ssh = None
        self.hostname = ""
    
    def doActionsSSH(self, actions) -> None:
        for action in actions:
            if '%host%' in actions[action]:
                actions[action] = actions[action].replace("%host%",self.hostname)
            self.logger.info('Executing Action {} with {}'.format(action, actions[action]))
            stdin, stdout, stderr = self.ssh.exec_command('{}'.format(actions[action]))
            for line in iter(stdout.readline,""):
                self.logger.info (line, end="")        


    def doActionsLocal(self, window, bar, taskitem, ini_info: iniInfo, final=False) -> None:
        """
        This class executes local actions from the .ini file.
        
        Args:
            self:       This class
            window:     Either ttk window or ttkboostrap window
            bar:        pointer to the progressbar
            taskitem:   This is the string for the current task
            ini_info:   Information from the ini file
            final:      Whether this is initial or final actions
            
        Returns:
            None
        """
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
                set_bar_value(window, bar, (count/len(ini_info.actions.keys()))*100)
                exec_option = '1'
                
                # check for user input otherwise it returns string in ini_info.actions[action]
                finalstr = self.string_utilities.checkForUserVariable(ini_info.actions[action], ini_info)
                skip_action = False

                if action in ini_info.options.keys():
                    exec_option = ini_info.optionvals[action].get()
                    
                if(exec_option != '0'):
                    while self._tarpL.CheckForTarpL(finalstr):
                        tarpLrtn = self._tarpL.ExecuteTarpL(finalstr, ini_info, window)
                        if tarpLrtn.rtnstate == False:
                            skip_action = True
                            break
                        else:
                            if tarpLrtn.rtnvar != "":
                                if tarpLrtn.tarpltype == TarpLAPIEnum.IFGOTO:
                                    finalstr = tarpLrtn.rtnvalue
                                    gotoindex = tarpLrtn.rtnvar
                                else: # This ends up setting a variable, so no execution is needed
                                    ini_info.returnvars[tarpLrtn.rtnvar] = tarpLrtn.rtnvalue
                                    skip_action = True
                                    break
                            else:
                                finalstr = tarpLrtn.rtnvalue
                                if finalstr is None:
                                    break

                    if skip_action:
                        self.lock.release()
                        continue
                               
                    taskstr = 'Executing {} with {}'.format(action, finalstr)
                    set_var(window, taskitem, taskstr)
    
                    if(finalstr != None):
                        if self.logger.level == logging.DEBUG:
                            self.process_manager.executeProcsDebug(finalstr, ini_info.watchdog, ini_info.process_timeout)
                        else:
                            result = self.process_manager.executeProcs(finalstr, ini_info.watchdog, ini_info.process_timeout)
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
                    self.logger.error("Timeout Error in Action {}".format(str(e)))
                else:
                    self.logger.error("Error in Action {}".format(str(e)))
    
                self.lock.release()
                continue                                           
    
            self.lock.release()
