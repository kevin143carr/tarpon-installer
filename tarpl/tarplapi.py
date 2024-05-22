import PySimpleGUI as sg
from tkinter import messagebox as msgbox
from tarpl.poplistbox import PopListbox
from tarpl.tarplclasses import TarpLreturn
from tarpl.tarplclasses import TarpLAPIEnum

#Tarpon Installer Language
class TarpL:
    API = ['YESNO', 'MSGBOX', 'IFGOTO', 'POPLIST', 'INPUTLIST', 'INPUTFILE']
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
        match tarpltype:
            case 'YESNO':
                return self.YESNO(actionstr, window)
            case 'MSGBOX':
                return self.MSGBOX(actionstr, window)
            case 'IFGOTO':                
                return self.IFGOTO(actionstr)
            case 'POPLIST':
                return self.POPLIST(actionstr, window)
            
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
            if inputype == 'INPUTLIST':
                selectlist = splitstr[3].split(',')
                rtnval = self.pop_listbox.showPopListbox(selectlist, window)
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
                rtnval = self.pop_listbox.showPopListbox(selectlist, window)
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
