import os
import sys
from datetime import datetime
from sys import platform

def find_file(file_name, directory_name):
    files_found = []
    for path, subdirs, files in os.walk(directory_name):
        for name in files:
            if(file_name == name):
                file_path = os.path.join(path,name)
                files_found.append(file_path)
    return files_found

def FindPostgresHBAPath(linuxpath = '/var/lib/pgsql'):
    if platform == 'linux':
        path = linuxpath
    else:
        path = "C:\\Program Files\\PostGreSQL"

    exists = os.path.exists(path)
    if(exists == False):
        path = "C:\\Program Files (x86)\\PostGreSQL"

    exists = os.path.exists(path)
    if(exists == False):
        print("Failed to find PostGreSQL")

    file_found = find_file("pg_hba.conf", path)
    return file_found[0]

def modifypostgresHBA(hba_path, IPAddress):

    IPAddress = IPAddress[0:IPAddress.rfind('.')] + ".0/24"
    print("modifying {} with {}".format(hba_path,IPAddress))
    with open(hba_path, "r") as f:
        lines = f.readlines()
        f.close()

    with open(hba_path, "w") as f:
        for line in lines:
            if('# IPv4 local connections:' in line):
                f.write(line)
                if platform == 'linux':
                    line = "host\tall\t\tall\t\t{}\t\tmd5".format(IPAddress);
                else:
                    line = "host\tall\t\t\t\tall\t\t\t\t{}\t\t\tmd5".format(IPAddress);
                f.write(line + "\n")
            else:
                f.write(line)

        f.close()

def PrintHelp():
    print("**********************************************************************")
    print("*  ><###> Modify pg_hba.conf files <###>< is an open source install creator. *")
    print("*  usage: modifypostgreshba --address xxx.xxx.xxx.xxx (where xxx = IP address) --directory /var/lib/pgsql  *")
    print("*  VERSION 2.2                                                                         *")
    print("**********************************************************************")
    raise SystemExit

if __name__ == "__main__":
    params = {}
    option = ""
    if len(sys.argv) < 2:
        PrintHelp()

    for arg in sys.argv:
        if arg[0:1] == "-":
            option = arg
        else:
            params[option] = arg

    for item in params:
        print("parameter {}".format(params[item]))

    ipaddr = params['--address']        
    directory = params['--directory']

    if directory == '':
        file_path = FindPostgresHBAPath()
    else:
        file_path = FindPostgresHBAPath(directory)
    modifypostgresHBA(file_path, ipaddr)
