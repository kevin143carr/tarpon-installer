
class StringUtilities:
    
    def checkForUserInput(self, string, userinputs):
        rtnstring = string
        for input in userinputs:
            for i in range(len(string.split('%')) -1):
                if input in string:
                    string = string.replace('%'+input+'%',userinputs[input].get(),1)
                    rtnstring = string
        return rtnstring    
     
    # The return value will either be what is in userinput or variables or original string sent in
    def checkForUserVariable(self, instring, ini_info):
        rtnstring = instring
        for input in ini_info.userinput:
            for i in range(len(instring.split('%')) -1):
                if input in instring:
                    rtnstring = instring.replace('%'+input+'%',ini_info.userinput[input].get(),1)
                    instring = rtnstring
                    
        for input in ini_info.variables:
            for i in range(len(instring.split('%')) -1):
                if input in instring:
                    rtnstring = instring.replace('%'+input+'%',ini_info.variables[input],1)
                    instring = rtnstring
                    
        for input in ini_info.returnvars:
            for i in range(len(instring.split('%')) -1):
                if input in instring:
                    rtnstring = instring.replace('%'+input+'%',ini_info.returnvars[input],1)
                    instring = rtnstring                    
                    
        return rtnstring
                     