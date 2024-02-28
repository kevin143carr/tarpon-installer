import os
import sys
import ctypes
import time
import logging
from elevate import elevate
from datetime import datetime
from sys import platform

logger = None


def PrintHelp():
    print("**********************************************************************")
    print("*  Modify Hostnames                                                  *")
    print("*  modifies the hosts files with as many IP you need                 *")
    print("*                                                                    *")
    print("*  --searchfor jaar --addresses test1=a.a.a.a,test2=b.b.b.b --modifier testkevin *")
    print("* --searchfor = previous entry keyword                               *")
    print("* --addresses = name and IP address to put in                        *")
    print("* --modifier = identifies application or person who made the change       *")
    print("*                                                                    *")
    print("**********************************************************************")
    raise SystemExit

def modify_host_file(entry):
    try:
        if platform == 'linux':
            winhosts = "/etc/hosts"
        else:
            winhosts = os.environ['windir']+"\System32\drivers\etc\hosts"

        print("Modifying {} with {}".format(winhosts,entry))
        filename=winhosts
        answ=os.path.exists(filename)
        with open(filename, "a") as f:
            f.write('\n')
            f.write(entry)
        f.close()
    except:
        print("Error updating host file")

def search_for_previous_host_entries(searchfor):
        if platform == 'linux':
            winhosts = "/etc/hosts"
        else:
            winhosts = os.environ['windir']+"\System32\drivers\etc\hosts"

        print(winhosts)
        filename=winhosts
        answ=os.path.exists(filename)
        with open(filename, "r") as f:
            lines = f.readlines()
            f.close()
        
        with open(filename, "w") as f:
            for line in lines:
                if(searchfor in line):
                    if('#' in line):
                        f.write(line)
                    else:
                        line = '#' + line
                        f.write(line)
                else:
                    f.write(line)
            f.close()

def isAdmin():
    try:
        is_admin = (os.getuid() == 0)
    except AttributeError:
        is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
    return is_admin

if __name__ == "__main__":
    params = {}
    option = ""

    logger = logging.getLogger("logger")

    logging.basicConfig(filename="modifyhostnames.log",
                    filemode='w', level = logging.INFO)

    if isAdmin():
        logger.info("Executing as Administrator")
    else:
        logger.info("Elevating Permissions because Administrator = {}".format(isAdmin()))
#        elevate()

    if len(sys.argv) < 2:
        PrintHelp()

    for arg in sys.argv:
        if arg[0:1] == "-":
            option = arg
        else:
            params[option] = arg

    for item in params:
        ipaddr = params[item]
        print("parameter {}".format(params[item]))

    search_for_previous_host_entries(params['--searchfor'])

    addresses = params['--addresses'].split(',')
    modify_host_file("## modified by {} on {} ##".format(params['--modifier'],str(datetime.now())));

    for address in addresses:
        result = address.split('=')
        modify_host_file("{}\t\t{}".format(result[1],result[0]))
