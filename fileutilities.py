import os
import sys
from datetime import datetime

class FileUtilities:

    def addFileContents(file, entry):
        try:
            print("Adding to {} with {}".format(file, entry))
            with open(file, "a") as f:
                f.write(entry + "\n")
            f.close()
        except:
            print("Error updating file")

    def modifyFileContents(file, searchline, update):
        print("modifying {} with {}".format(file, update))
        with open(file, "r") as f:
            lines = f.readlines()
            f.close()

        with open(file, "w") as f:
            found = False
            for line in lines:

                if(found == True):
                    f.write(line)
                    continue;

                searchval = " {0} ".format(line).lower().count(" {0} ".format(searchline).lower())
                if(searchval != 0):
                    f.write(update + "\n")
                    found = True
                else:
                    f.write(line)

            f.close()

    def createFileAddContents(file, contents):
        print("Creating {} and adding contents".format(file))
        with open(file, "w") as f:
            for line in contents:
                    f.write(line + "\n")
            f.close()

    def find_file(file_name, directory_name):
        files_found = []
        for path, subdirs, files in os.walk(directory_name):
            for name in files:
                if(file_name == name):
                    file_path = os.path.join(path,name)
                    files_found.append(file_path)
        return files_found
