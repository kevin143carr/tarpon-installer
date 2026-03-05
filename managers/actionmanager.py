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

    def _resolve_action_command(self, action_value: str, ini_info: iniInfo, window):
        tarpLrtn = TarpLreturn()
        finalstr = self.string_utilities.checkForUserVariable(action_value, ini_info)
        skip_action = False

        while finalstr is not None and self._tarpL.CheckForTarpL(finalstr):
            tarpLrtn = self._tarpL.ExecuteTarpL(finalstr, ini_info, window)
            if tarpLrtn.rtnstate is False:
                skip_action = True
                break

            if tarpLrtn.rtnvar != "":
                if tarpLrtn.tarpltype == TarpLAPIEnum.IFGOTO:
                    finalstr = tarpLrtn.rtnvalue
                else:
                    ini_info.returnvars[tarpLrtn.rtnvar] = tarpLrtn.rtnvalue
                    skip_action = True
                    break
            else:
                finalstr = tarpLrtn.rtnvalue

        return finalstr, skip_action, tarpLrtn

    def _execute_local_command(self, finalstr: str, ini_info: iniInfo) -> int:
        if self.logger.level == logging.DEBUG:
            return self.process_manager.executeProcsDebug(finalstr, ini_info.watchdog, ini_info.process_timeout)
        return self.process_manager.executeProcs(finalstr, ini_info.watchdog, ini_info.process_timeout)

    def runDiagnosticsLocal(self, window, bar, taskitem, ini_info: iniInfo):
        diagnostics = ini_info.diagnostics
        results = []
        count = 0

        for key, action_value in diagnostics.items():
            count += 1
            set_bar_value(window, bar, (count / len(diagnostics.keys())) * 100 if diagnostics else 0)

            if isinstance(action_value, str) and action_value.startswith("DIAG::"):
                parts = action_value.split("::", 2)
                if len(parts) < 3:
                    self.logger.error("Invalid diagnostic definition for %s", key)
                    results.append({"label": key, "status": "FAILED"})
                    continue

                label_text = parts[1].strip()
                command_value = parts[2]
                set_var(window, taskitem, "Running diagnostic {}".format(label_text))

                try:
                    finalstr, skip_action, _ = self._resolve_action_command(command_value, ini_info, window)
                    passed = False
                    if not skip_action and finalstr is not None:
                        passed = (self._execute_local_command(finalstr, ini_info) == 0)
                    results.append({"label": label_text, "status": "PASS" if passed else "FAILED"})
                except Exception as ex:
                    self.logger.error("Diagnostic %s failed: %s", label_text, ex)
                    results.append({"label": label_text, "status": "FAILED"})
                continue

            try:
                finalstr, skip_action, _ = self._resolve_action_command(action_value, ini_info, window)
                if skip_action or finalstr is None:
                    continue
                set_var(window, taskitem, "Executing diagnostic action {} with {}".format(key, finalstr))
                self._execute_local_command(finalstr, ini_info)
            except Exception as ex:
                self.logger.error("Error in diagnostic action %s: %s", key, ex)
        return results
    
    def doActionsSSH(self, window, bar, taskitem, actions, ini_info: iniInfo) -> None:
        total = len(actions.keys())
        count = 0
        for action_key, action_value in actions.items():
            try:
                count += 1
                set_bar_value(window, bar, (count / total) * 100 if total else 0)

                exec_option = "1"
                if action_key in ini_info.options:
                    exec_option = ini_info.optionvals[action_key].get()
                if exec_option == "0":
                    continue

                finalstr, skip_action, _ = self._resolve_action_command(action_value, ini_info, window)
                if skip_action or finalstr is None:
                    continue
                if "%host%" in finalstr:
                    finalstr = finalstr.replace("%host%", self.hostname)

                set_var(window, taskitem, "Executing {} with {}".format(action_key, finalstr))
                self.logger.info("Executing Action %s with %s", action_key, finalstr)
                stdin, stdout, stderr = self.ssh.exec_command("{}".format(finalstr))
                for line in iter(stdout.readline, ""):
                    self.logger.info(line, end="")
                for line in iter(stderr.readline, ""):
                    self.logger.error(line, end="")
            except Exception as ex:
                self.logger.error("Error in remote action %s: %s", action_key, ex)
                continue


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
                finalstr = None
                skip_action = False

                if action in ini_info.options.keys():
                    exec_option = ini_info.optionvals[action].get()
                    
                if(exec_option != '0'):
                    finalstr, skip_action, tarpLrtn = self._resolve_action_command(ini_info.actions[action], ini_info, window)
                    if tarpLrtn.tarpltype == TarpLAPIEnum.IFGOTO and tarpLrtn.rtnvar != "":
                        gotoindex = tarpLrtn.rtnvar

                    if skip_action:
                        self.lock.release()
                        continue
                               
                    taskstr = 'Executing {} with {}'.format(action, finalstr)
                    set_var(window, taskitem, taskstr)
    
                    if(finalstr != None):
                        result = self._execute_local_command(finalstr, ini_info)
                        if self.logger.level != logging.DEBUG:
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
