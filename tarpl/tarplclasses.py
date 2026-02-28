from enum import Enum

class TarpLAPIEnum(Enum):
    YESNO = 1
    MSGBOX = 2
    POPLIST = 3
    INPUTLIST = 4
    INPUTFILE = 5
    IFGOTO = 6
    EXEC_PYFUNC = 7
    IFOPTION = 8
    ALSOCHECKOPTION = 9
    IFTHENELSE = 10

class TarpLreturn:
    def __init__(self) -> None:
        self.rtnstate = False
        self.rtnvalue = ""
        self.rtnvar = ""
        self.tarpltype = TarpLAPIEnum
