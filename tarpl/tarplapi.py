
import os
from tkinter import messagebox as msgbox
from tarpl.poplistbox import PopListbox
from tarpl.tarplclasses import TarpLreturn
from tarpl.tarplclasses import TarpLAPIEnum

#Tarpon Installer Language
class TarpL:
    API = ['YESNO', 'MSGBOX', 'IFGOTO', 'POPLIST', 'INPUTLIST', 'INPUTFILE','EXEC_PYSCRIPT']
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
        
    def ExecuteTarpL(self, actionstr, window):
        tarpltype = self.getTarpL(actionstr)
        if tarpltype == 'YESNO':
            return self.YESNO(actionstr, window)
        elif tarpltype == 'MSGBOX':
            return self.MSGBOX(actionstr, window)
        elif tarpltype == 'IFGOTO':
            return self.IFGOTO(actionstr)
        elif tarpltype == 'POPLIST':
            return self.POPLIST(actionstr, window)
        elif tarpltype == 'EXEC_PYSCRIPT':
            return self.EXEC_PYSCRIPT(actionstr)
        
        #match tarpltype:
            #case 'YESNO':
                #return self.YESNO(actionstr, window)
            #case 'MSGBOX':
                #return self.MSGBOX(actionstr, window)
            #case 'IFGOTO':                
                #return self.IFGOTO(actionstr)
            #case 'POPLIST':
                #return self.POPLIST(actionstr, window)
            
    def IFGOTO(self, instring):
        tarpLrtn = TarpLreturn()
        splitstr = instring.split('::');
        tarpLrtn.rtnstate = True        
        tarpLrtn.rtnvar = splitstr[2]
        tarpLrtn.rtnvalue = splitstr[1]
        tarpLrtn.tarpltype = TarpLAPIEnum.IFGOTO
        return tarpLrtn
    
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
        
    def EXEC_PYSCRIPT (self, instring):
        tarpLrtn = TarpLreturn()
        splitstr = instring.split('::');
        script_filename =  splitstr[1]
        function_name = splitstr[2]
        
        base_path = os.path.abspath(".")
        script_path = os.path.join(base_path, script_filename)

        if not os.path.isfile(script_path):
            print(f"Error: Script file '{script_filename}' not found.")
            return

        # Load and execute the script in a fresh namespace
        namespace = {}
        with open(script_path, 'r') as f:
            script_code = compile(f.read(), script_path, 'exec')
            exec(script_code, namespace)

        if function_name not in namespace:
            print(f"Error: Function '{function_name}' not found in '{script_filename}'.")
            return

        # Call the function
        func = namespace[function_name]
        if callable(func):
            func()
        else:
            print(f"Error: '{function_name}' is not callable.")
            
        return tarpLrtn
