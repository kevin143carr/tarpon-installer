
import os
from iniinfo import iniInfo
from tkinter import messagebox as msgbox
from tarpl.poplistbox import PopListbox
from tarpl.tarplclasses import TarpLreturn
from tarpl.tarplclasses import TarpLAPIEnum

#Tarpon Installer Language
class TarpL:
    API = ['YESNO', 'MSGBOX', 'IFGOTO', 'POPLIST', 'INPUTLIST', 'INPUTFILE','EXEC_PYFUNC', 'IFOPTION', 'ALSOCHECKOPTION']
    pop_listbox = PopListbox()    
    
    def CheckForTarpL(self, inputstr):
        res = any(ele in inputstr for ele in self.API)
        if res == True:
            return True
        else:
            return False
        
    def getTarpL(self, actionstr):
        tarpl = [word for word in self.API if word in actionstr]
        
        if len(tarpl) > 0:            
            return tarpl[0]
        else:
            return ""
        
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
            return self.EXEC_PYFUNC(actionstr)
        elif tarpltype == 'IFOPTION':
            return self.IFOPTION(actionstr, ini_info)
        elif tarpltype == 'ALSOCHECKOPTION':
            return self.ALSOCHECKOPTION(ini_info, optionone, optiontwo)                   
    
    def POPLIST (self, instring, window):
        tarpLrtn = TarpLreturn()
        rtnval = None
        try:
            splitstr = instring.split('::');
            inputype = self.getTarpL(splitstr[2])
            titletext = splitstr[1]
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
    
    
    def YESNO (self, instring, window):
        tarpLrtn = TarpLreturn()        
        try:
            splitstr = instring.split('::');
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
        
    def EXEC_PYFUNC (self, instring):
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
    
            func(*args)
    
        except Exception as e:
            print(f"Error while executing function: {e}")
            
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
        
        if ini_info.optionvals[changed_key].get() == '1':
            ini_info.optionvals[otheroption].set('1')            
        return tarpLrtn
