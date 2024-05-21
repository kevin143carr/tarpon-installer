
class StringUtilities:
    
    
    # The return value will either be what is in userinput or variables or original string sent in
    def checkForUserVariable(self, instring, ini_info):
        rtnstring = instring
        for input in ini_info.userinput:
            for i in range(len(instring.split('%')) -1):
                if input in instring:
                    resultstr = instring.replace('%'+input+'%',ini_info.userinput[input].get(),1)
                    rtnstring = resultstr
                    
        for input in ini_info.variables:
            for i in range(len(instring.split('%')) -1):
                if input in instring:
                    resultstr = instring.replace('%'+input+'%',ini_info.variables[input],1)
                    rtnstring = resultstr
                    
        for input in ini_info.returnvars:
            for i in range(len(instring.split('%')) -1):
                if input in instring:
                    resultstr = instring.replace('%'+input+'%',ini_info.returnvars[input],1)
                    rtnstring = resultstr                    
                    
        return rtnstring
                     