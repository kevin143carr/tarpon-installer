from enum import Enum

class TarpLAPIEnum(Enum):
    YESNO = 1
    MSGBOX = 2
    POPLIST = 3
    INPUTLIST = 4
    INPUTFILE = 5
    IFGOTO = 6  

class TarpLreturn:
    rtnstate = bool()
    rtnvalue = str()
    rtnvar = str()
    tarpltype = TarpLAPIEnum