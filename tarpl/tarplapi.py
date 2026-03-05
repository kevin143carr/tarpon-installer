
import os
import sys
import inspect
from iniinfo import iniInfo
from stringutilities import StringUtilities
from tkinter import messagebox as msgbox
from tarpl.poplistbox import PopListbox
from tarpl.tarplclasses import TarpLreturn
from tarpl.tarplclasses import TarpLAPIEnum
from ui_thread import call_on_ui_thread

#Tarpon Installer Language
class TarpL:
    API = ['YESNO', 'MSGBOX', 'IFGOTO', 'POPLIST', 'INPUTLIST', 'INPUTFILE','EXEC_PYFUNC', 'IFOPTION', 'ALSOCHECKOPTION']
    pop_listbox = PopListbox()    

    def _get_directive(self, inputstr):
        if not isinstance(inputstr, str):
            return ""

        stripped = inputstr.strip()
        if stripped.startswith("[IF]") and "[THEN]" in stripped and "[ELSE]" in stripped:
            return "IFTHENELSE"

        directive = stripped.split("::", 1)[0].strip()
        if directive in self.API:
            return directive
        return ""
    
    def CheckForTarpL(self, inputstr):
        return self._get_directive(inputstr) != ""
        
    def getTarpL(self, actionstr):
        return self._get_directive(actionstr)
        
    def ExecuteTarpL(self, actionstr, ini_info: iniInfo, window = None, optionone: str = 'none', optiontwo: str = 'none'):
        tarpltype = self.getTarpL(actionstr)
        if tarpltype == 'YESNO':
            return self.YESNO(actionstr, window)
        elif tarpltype == 'MSGBOX':
            return self.MSGBOX(actionstr, window)
        elif tarpltype == 'IFGOTO':
            return self.IFGOTO(actionstr)
        elif tarpltype == 'POPLIST':
            return self.POPLIST(actionstr, window)
        elif tarpltype == 'EXEC_PYFUNC':
            return self.EXEC_PYFUNC(actionstr, window)
        elif tarpltype == 'IFOPTION':
            return self.IFOPTION(actionstr, ini_info)
        elif tarpltype == 'ALSOCHECKOPTION':
            return self.ALSOCHECKOPTION(ini_info, optionone, optiontwo)
        elif tarpltype == 'IFTHENELSE':
            return self.IFTHENELSE(actionstr, ini_info)
    
    def _is_headless(self) -> bool:
        return os.environ.get("TARPL_HEADLESS", "").strip().lower() in {"1", "true", "yes", "on"}

    def _print_headless_prompt_block(self, title: str, message: str) -> None:
        border = "=" * 72
        print()
        print(border)
        print(title)
        print("-" * 72)
        print(message)
        print(border)

    def _prompt_headless_poplist_selection(self, title: str, selectlist) -> str:
        lines = [title]
        for index, item in enumerate(selectlist, start=1):
            lines.append(f"{index}. {item}")
        self._print_headless_prompt_block("USER SELECTION REQUIRED", "\n".join(lines))

        while True:
            try:
                answer = input("Enter selection number (blank to cancel): ").strip()
            except EOFError:
                answer = ""

            if answer == "":
                return ""
            if answer.isdigit():
                selection_index = int(answer)
                if 1 <= selection_index <= len(selectlist):
                    return selectlist[selection_index - 1]
            print("Please enter a valid selection number.", file=sys.stderr)

    def POPLIST (self, instring, window):
        tarpLrtn = TarpLreturn()
        rtnval = None
        try:
            splitstr = instring.split('::');
            inputype = self.getTarpL(splitstr[2])
            titletext = splitstr[1]
            if self._is_headless():
                if inputype == 'INPUTLIST':
                    selectlist = splitstr[3].split(',')
                elif inputype == 'INPUTFILE':
                    fp = open(splitstr[3], "r")
                    fromfile = fp.readline()
                    fp.close()
                    selectlist = fromfile.split(',')
                else:
                    selectlist = []

                selectlist = [item.strip() for item in selectlist if item.strip()]
                if selectlist:
                    rtnval = self._prompt_headless_poplist_selection(titletext, selectlist)
                    if rtnval != "":
                        tarpLrtn.rtnstate = True
                        tarpLrtn.rtnvalue = rtnval
                        tarpLrtn.rtnvar = splitstr[4]
                        tarpLrtn.tarpltype = TarpLAPIEnum.POPLIST
                    else:
                        tarpLrtn.rtnstate = False
                        tarpLrtn.tarpltype = TarpLAPIEnum.POPLIST
                else:
                    tarpLrtn.rtnstate = False
                    tarpLrtn.tarpltype = TarpLAPIEnum.POPLIST
                return tarpLrtn

            if inputype == 'INPUTLIST':
                selectlist = splitstr[3].split(',')
                rtnval = self.pop_listbox.showPopListbox(selectlist, window, titletext)
                if rtnval != "":
                    tarpLrtn.rtnstate = True
                    tarpLrtn.rtnvalue = rtnval
                    tarpLrtn.rtnvar = splitstr[4]
                else:
                    tarpLrtn.rtnstate = False
            elif inputype == 'INPUTFILE' :
                fp =  open(splitstr[3],"r")
                fromfile = fp.readline()
                print(fromfile)
                selectlist = fromfile.split(',')
                rtnval = self.pop_listbox.showPopListbox(selectlist, window, titletext)
                if rtnval != "":
                    tarpLrtn.rtnstate = True
                    tarpLrtn.rtnvalue = rtnval
                    tarpLrtn.rtnvar = splitstr[4]
                    tarpLrtn.tarpltype = TarpLAPIEnum.POPLIST
                else:
                    tarpLrtn.tarpltype = TarpLAPIEnum.POPLIST                    
                    tarpLrtn.rtnstate = False                
        except Exception as ex:
            print("Error in yes no {}".format(ex))
        return tarpLrtn

    def _parse_if_then_else(self, instring: str):
        if not instring.startswith("[IF]"):
            raise ValueError("Invalid [IF][THEN][ELSE] syntax")

        then_start = instring.find("[THEN]")
        else_start = instring.find("[ELSE]")
        if then_start == -1 or else_start == -1 or then_start > else_start:
            raise ValueError("Invalid [IF][THEN][ELSE] syntax")

        condition = instring[len("[IF]"):then_start].strip()
        then_action = instring[then_start + len("[THEN]"):else_start].strip()
        else_action = instring[else_start + len("[ELSE]"):].strip()
        return condition, then_action, else_action

    def _evaluate_if_condition(self, condition: str) -> bool:
        for operator in ("==", "!=", " contains "):
            if operator not in condition:
                continue

            if operator.strip() == "contains":
                left, right = condition.split(operator, 1)
                return right.strip() in left.strip()

            left, right = condition.split(operator, 1)
            if operator == "==":
                return left.strip() == right.strip()
            return left.strip() != right.strip()

        raise ValueError("Unsupported [IF] condition: {}".format(condition))

    def IFTHENELSE(self, instring: str, ini_info: iniInfo):
        tarpLrtn = TarpLreturn()
        condition, then_action, else_action = self._parse_if_then_else(instring)
        condition = StringUtilities().checkForUserVariable(condition, ini_info)

        tarpLrtn.rtnstate = True
        tarpLrtn.rtnvalue = then_action if self._evaluate_if_condition(condition) else else_action
        tarpLrtn.tarpltype = TarpLAPIEnum.IFTHENELSE
        return tarpLrtn
    
    
    def YESNO (self, instring, window):
        tarpLrtn = TarpLreturn()        
        try:
            splitstr = instring.split('::');
            if self._is_headless():
                prompt = splitstr[1].strip()
                self._print_headless_prompt_block("USER CONFIRMATION REQUIRED", prompt)
                while True:
                    try:
                        answer = input("Enter choice [y/N]: ").strip().lower()
                    except EOFError:
                        answer = ""
                    if answer in {"y", "yes"}:
                        tarpLrtn.rtnstate = True
                        break
                    if answer in {"", "n", "no"}:
                        tarpLrtn.rtnstate = False
                        break
                    print("Please answer yes or no.", file=sys.stderr)
                tarpLrtn.rtnvalue = splitstr[2]
                tarpLrtn.tarpltype = TarpLAPIEnum.YESNO
                return tarpLrtn
            tarpLrtn.rtnstate = msgbox.askyesno("User Question", splitstr[1], parent = window);
            tarpLrtn.rtnvalue = splitstr[2]
            tarpLrtn.tarpltype = TarpLAPIEnum.YESNO
        except Exception as ex:
            print("Error in yes no {}".format(ex))
            
        return tarpLrtn
    
    def MSGBOX (self, instring, window):
        tarpLrtn = TarpLreturn()         
        try:
            splitstr = instring.split('::');
            if self._is_headless():
                message = splitstr[1].strip()
                self._print_headless_prompt_block("USER MESSAGE", message)
                try:
                    input("Press Enter to continue...")
                except EOFError:
                    pass
                tarpLrtn.rtnstate = False
                tarpLrtn.tarpltype = TarpLAPIEnum.MSGBOX
                return tarpLrtn
            answer = msgbox.showinfo("Information", splitstr[1], parent = window);
            tarpLrtn.rtnstate = False
            tarpLrtn.tarpltype = TarpLAPIEnum.MSGBOX
        except Exception as ex:
            print("Error in yes no {}".format(ex))
            
        return tarpLrtn
    
    
    
    def parse_arg(self, val):
        # Try to convert to int, float, or leave as string
        for cast in (int, float):
            try:
                return cast(val)
            except ValueError:
                continue
        return val      
        
    def EXEC_PYFUNC (self, instring, window=None):
        tarpLrtn = TarpLreturn()
        splitstr = instring.split('::');
        script_filename =  splitstr[1]
        function_name = splitstr[2]
        args_string =  splitstr[3]
        
        tarpLrtn.rtnstate = False
        tarpLrtn.tarpltype = TarpLAPIEnum.EXEC_PYFUNC                
        
        base_path = os.path.abspath(".")
        script_path = os.path.join(base_path, script_filename)
    
        if not os.path.isfile(script_path):
            print(f"Error: Script file '{script_filename}' not found.")
            return tarpLrtn
    
        # Split the string into a list of raw strings
        args = []
        if args_string:
            args = [arg.strip() for arg in args_string.split(',') if arg.strip()]
    
        namespace = {}
        try:
            with open(script_path, 'r') as f:
                script_code = compile(f.read(), script_path, 'exec')
                exec(script_code, namespace)
    
            func = namespace.get(function_name)
            if not callable(func):
                print(f"Error: '{function_name}' is not callable or not found.")
                return tarpLrtn

            signature = inspect.signature(func)
            supports_kwargs = any(
                parameter.kind == inspect.Parameter.VAR_KEYWORD
                for parameter in signature.parameters.values()
            )
            if window is not None and (
                supports_kwargs or "window" in signature.parameters or "parent" in signature.parameters
            ):
                if "parent" in signature.parameters and "window" not in signature.parameters:
                    call_on_ui_thread(window, lambda: func(*args, parent=window))
                else:
                    call_on_ui_thread(window, lambda: func(*args, window=window))
            else:
                func(*args)
    
        except Exception as e:
            print(f"Error while executing function: {e!r}")
            
        return tarpLrtn
    
    def IFGOTO(self, instring):
        tarpLrtn = TarpLreturn()
        splitstr = instring.split('::');
        tarpLrtn.rtnstate = True        
        tarpLrtn.rtnvar = splitstr[2]
        tarpLrtn.rtnvalue = splitstr[1]
        tarpLrtn.tarpltype = TarpLAPIEnum.IFGOTO
        return tarpLrtn    
    
    def IFOPTION (self, instring: str, ini_info: iniInfo):
        tarpLrtn = TarpLreturn()
        splitstr = instring.split('::');
        exec_option = '1'
        
        if splitstr[1] in ini_info.optionvals.keys():
            exec_option = ini_info.optionvals[splitstr[1]].get()
            if(exec_option != '0'):            
                tarpLrtn.rtnvalue =  splitstr[2]
            else:
                tarpLrtn.rtnvalue =  "echo option {} not set".format(splitstr[1])
        else:
            tarpLrtn.rtnvalue =  "echo option {} not found".format(splitstr[1])
        
            
        tarpLrtn.rtnstate = True
        tarpLrtn.tarpltype = TarpLAPIEnum.IFOPTION        
        return tarpLrtn
    
    def ALSOCHECKOPTION (self, ini_info: iniInfo, changed_key, otheroption):
        tarpLrtn = TarpLreturn()
        
        options = otheroption.split(',')
        
        if len(options) > 1:
            for option in options:                
                if ini_info.optionvals[changed_key].get() == '1':
                    ini_info.optionvals[option].set('1')
        else:
            if ini_info.optionvals[changed_key].get() == '1':
                ini_info.optionvals[otheroption].set('1')
        return tarpLrtn
