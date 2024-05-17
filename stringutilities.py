
class StringUtilities:
    
    def checkForUserVariable(self, string, userinputs):
        rtnstring = string
        for input in userinputs:
            for i in range(len(string.split('%')) -1):
                if input in string:
                    string = string.replace('%'+input+'%',userinputs[input].get(),1)
                    rtnstring = string
        return rtnstring    