import PySimpleGUI as sg
from tkinter import messagebox as msgbox
from tarpl.poplistbox import PopListbox
from tarpl.tarplrtnclass import TarpLreturn
#Tarpon Installer Language
class TarpL:
    API = ['YESNO', 'MSGBOX', 'IF', 'THEN', 'ELSE', 'DIREXISTS', 'FILEEXISTS', 'POPLIST', 'INPUTLIST', 'INPUTFILE']
    pop_listbox = PopListbox()
    tarpLrtn = TarpLreturn()
    
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
        match tarpltype:
            case 'YESNO':
                return self.YESNO(actionstr, window)
            case 'MSGBOX':
                return self.MSGBOX(actionstr, window)
            case 'IF':
                return 0
            case 'THEN':
                return 0
            case 'ELSE':
                return 0
            case 'DIREXISTS':
                return 0
            case 'FILEEXISTS':
                return 0
            case 'POPLIST':
                return self.POPLIST(actionstr, window)          
    
    def POPLIST (self, instring, window):
        rtnval = None
        try:
            text = instring.split('::');
            inputype = self.getTarpL(text[2])
            if inputype == 'INPUTLIST':
                selectlist = text[3].split(',')
                rtnval = self.pop_listbox.showPopListbox(selectlist, window)
                if rtnval != "":
                    TarpLreturn.rtnstate = True
                    TarpLreturn.rtnvalue = rtnval
                    TarpLreturn.rtnvar = text[4]
                else:
                    TarpLreturn.rtnstate = False
            elif inputype == 'INPUTFILE' :
                fp =  open(text[3],"r")
                fromfile = fp.readline()
                print(fromfile)
                selectlist = fromfile.split(',')
                rtnval = self.pop_listbox.showPopListbox(selectlist, window)
                if rtnval != "":
                    TarpLreturn.rtnstate = True
                    TarpLreturn.rtnvalue = rtnval
                    TarpLreturn.rtnvar = text[4]
                else:
                    TarpLreturn.rtnstate = False                
        except Exception as ex:
            print("Error in yes no {}".format(ex))
        return TarpLreturn
    
    
    def YESNO (self, instring, window):
        try:
            text = instring.split('::');
            answer = msgbox.askyesno("User Question", text[1], parent = window);
        except Exception as ex:
            print("Error in yes no {}".format(ex))
            
        return answer
    
    def MSGBOX (self, instring, window):
        try:
            text = instring.split('::');
            answer = msgbox.showinfo("Information", text[1], parent = window);
        except Exception as ex:
            print("Error in yes no {}".format(ex))
            
        return False
