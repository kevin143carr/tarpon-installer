# ><###> Tarpon-Installer <###><
Tarpon Installer allows for local and remote installations based on a configuration file.  
It is command line based. Currently it supports remote installs from Windows to Linux, 
Linux to Linux and Local Windows and Local Linux installs.

I originally developed it to distribute different kinds of builds to raspberry pi(s), but
ended up using it at my work for many different purposes, including providing updates.

It uses a config.ini (which can be named [anything].ini) and a resource folder.

# CONFIG.INI EXPLAINED

## [STARTUP] # A startup task gives you the opportunity to choose logo and title.
\
**Example**\
usegui = True - True to use GUI, false to be console application
logoimg = mylogo.png\
installtitle = MY INSTALLER NAME GOES HERE\
startupinfo = information about the installer like: "This will install MY APP on this machine"\
buttontext = The word for the install button usually just 'Install', but it can say any word.\
watchdog = True/False - This will allow tarpon_installer to use the watchdog app which will kill stalled processes.\
adminrights = True/False - This forces the application to be run as privelaged user.


## [USERINFO] # Information needed to log into the machine
This is the username and password fields.  Yes it is in plaintext!  This is often
used to update hosts files and other files that need this information, especially when
doing remote installations.  The username and password will be used to ssh into a linux
box when doing a "Remote Linux Install".  if it is blank it will not show up on the install GUI.\
\
**Example**\
username = \
password = 

## [SERVERCONFIG] # ip address information
Perhaps not the best name, but this field is used as the Remote IP that will be ssh(d) into
as well as used to update hosts files and other configuration files that is needed.  You can use the %host% 
to use as a variable to the host field.  Again this is usually for a remote Linux install.  DISPLAY means to show the field.
If it is blank, it will not show up in the install GUI.\
\
**Example**\
host = DISPLAY

## [BUILD] # buildtype:(WINDOWS OR LINUX) -- installtype:(LOCAL OR REMOTE) -- resources:(Relative or Full path)
**buildtype** = *Used to determine if the installed files are going on a LINUX or WINDOWS system.  Use upper case!*\
**installtype** =	*Used to determine if it is a LOCAL or REMOTE style install.*\
**resources** = *Used to tell the installer where the resource directory is it can be either a*\
*full path such as C:\Resources or a relative path to the executable '/resources'.*\
\
**Example**
buildtype = WINDOWS\
installtype = LOCAL\
resources = resources\

## [USERINPUT] # Used to create input boxes on the dialog.  
The key becomes a installer variable that can be used in the [FILES],[ACTIONS] AND [FINAL] sections.
Just put percent signs around the key like: %userdatafolder% and add it to the line item in the previously mentioned sections\
\
**Example**\
userdatafolder = Please enter data folder name\
databaseip = Please enter database IP addresss\

You would then use %userdatafolder% and %databseip% as variables in your [FILES], [ACTIONS] and [FINAL]

## [VARIABLES] # Used to define variables that will be used during installation.
**Example**\
userdatafolder = c:\userdata\
databaseip = 172.16.20.25

## [OPTIONS] # Allows for optional task that may be done inside the [ACTIONS] and [FINAL] sections.
An option button will automatically be displayed when using the GUI.  Options can then be checked.
For console programs, a numbered list will show up for the user to choose.
**Example**\
optionmakenewdir = Do you wish to make a new directory.\
optiondeleteolddata = Do you wish to delete old data?\
\
Notice I put the word 'option' on the front of my keyword.  That will remind me when I an in the\
[ACTIONS] or [FINAL] sections to use it there as an optional action.\
\
**[ACTION] Section**\
optionmakenewdir = mkdir %userdatafolder%\
optiondeleteolddata = rm -rf %userdatafolder%\
\
## [REPO] # NO LONGER SUPPORTED

## [RPM] #RPMs that will be used during a Linux installation.
Begin this section with #RPMS START HERE and end it with #RPMS END HERE .  When used with the buildadder it will\
automatically place the rpms in this section if a [RPMS] section is added to a buildadderconfig.ini file.  See BuildAdder.\
This section tells the installer what RPMs should be installed on a Linux based system.\
\
**Example**\
#RPMS START HERE\
installbzip2 = rpms/bzip2-libs-1.0.6-26.el8.x86_64.rpm\
installapr = rpms/apr-1.6.3-12.el8.x86_64.rpm,rpms/apr-util-1.6.1-6.el8_8.1.x86_64.rpm,rpms\
installhttpdfilesystem = rpms/httpd-filesystem-2.4.37-56.module+el8.8.0+1284+07ef499e.6.noarch.rpm\
installhttpdtools = rpms/httpd-tools-2.4.37-56.module+el8.8.0+1284+07ef499e.6.x86_64.rpm\
installhttpd = rpms/httpd-2.4.37-56.module+el8.8.0+1284+07ef499e.6.x86_64.rpm,rpms/rocky-logos-httpd-86.3-1.el8.noarch.rpm\
installunzip = rpms/unzip-6.0-46.el8.x86_64.rpm\
#RPMS END HERE

Notice how some of the RPMs are grouped together, that is to make sure all the dependencies are in place.

## [FILES] # Copies files from the resource folder to the paths and unzips if necessary.
Begin this section with #BUILDS START HERE and end it with #BUILDS END HERE.  When used with buildadder it will\
automatically place the files in this section if a [FILES] section exists in a buildadderconfig.ini file.  See BuildAdder.\
This section is used with both Linux and Windows files.\
\
*if a specified directory does not exists it will create it.  It will unzip in the specified folder*\
*as well as keeping the subdirectories.  BUT it will ignore an initial folder in the zip file if one exists*\
\
**Simple Copy Example:** *httpd.conf = c:/support/httpd/Apache24/conf*\
**Rename copy Example:** *myappsettings.json = c:/support/thing/appsettings.json*\
**Unzip file Example:** *transformer.zip = c:/support/newtransform*\
\
**Example**\
#BUILDS START HERE\
latestlinuxbuilds/coolfile = /opt/coolfile/folder\
latestwindowsbuilds/coolfile.exe = c:\coolfile\%userfolder%\
#BUILDS END HERE\
anotherFolderUnderResources/thisfile.dat = c:\shouldgo\here\
\
When used with the buildadder app you can designate files to be copied into a particular folder,\
regardless of the version.\
Outside the builds section you can add files from a folder within your resources folder and have them\
copied to wherever you like.\
Notice the %userfolder%, it is a uservariable I setup in the [USERINPUT]section.\

## [ACTIONS] # Actions executed at the command level (both Linux and Windows), each action has to be uniquely named
*Most anything that can be done from a command line can be done with this*\
**Echo Example:** *echo1 = echo THIS IS A TEST*\
**Windows Timeout Example:** *timeout1 = timeout /t 3*\
**Delete Example:** *cleanzip1 = del /Q c:\support\washere.zip*\
\
**Example**\
#make sure things are executable\
chmodmodifyapps = chmod 775 resources/modifyhostnames resources/modifypostgreshba\
chmodactivemqdir = chmod -R 775 /opt/dcd/activemq\
#Apache httpd fixups\
addapacheuser = useradd apache -g apache\
shutdownhttpd = systemctl stop httpd\
enablehttpd = systemctl enable httpd\
starthttpd = systemctl start httpd\
#Windows Example\
dirsupportdir = dir c:\STAR\support\
createproductsfolder = mkdir c:\STAR\Products\
createmanifestsfolder = mkdir c:\STAR\Products\manifests\
\
Notice you can add comments by using the # Your Comment notations.

## [MODIFY] # Used to modify files - MUST USE 1,2,3,ETC.. DESIGNATORS --\
You can modify a line in a file.  The {FILE} designator represents the path and name of the file.\
The {CHANGE} represents a searchable, unique line in the file.\
Use the '||' token to separate the what text will overwrite the original.
The {ADD} Designator will add a line to the last line of the file.  It wil create the fill if it does not exists.

**For Local Linux or Windows use the following examples:**\
**Example:#Used to modify files usage: (number = ){FILE}filepath+filename{CHANGE}keyword||replaceword**\
**Used to modify files usage: (number = ){FILE}filepath+filename{ADD}keyword**\
*# if a file does not exists it will create it then add from the '||' delimitted list*\
*# search and replace*\
**Example:** *1 = {FILE}C:/myinstall/support/userconfig.conf{CHANGE}user1 =||user1 = Marky*\
*# search and replace*\
**Example:** *2 = {FILE}C:/myinstall/support/userconfig.conf{CHANGE}log_timezone =||log_timezone = 'UTC'*\
*# added to end of file*\
**Example:** *3 = {FILE}C:/myinstall/support/userconfig.conf{ADD}portnumber = 55001*\
*# added to end of file*\
**Example:** *4 = {FILE}C:/myinstall/support/userconfig.conf{ADD} # Muskrats Stink*\
*# create file and add lines through '||' delimitted key/values*\
**Example:** *5 = {FILE}C:/myinstall/support/createthisfile.conf{ADD}ipaddress = 111.222.333.444||portnumber = 34333||resourcefolder = d:\resources*\

## [FINAL] # Same as Actions but is the last things done, each action has to be uniquely named
**Example:** *statusjaardcm = systemctl status stardcm | grep Active:*\
**Example:** *statusjaarwcm = systemctl status activemq | grep Active:*\
**Example:** *rebootmachine = echo "********* FINISHED AND REBOOTING IN 10 SECONDS *********"*\
**Example:** *starttimer = timeout /t 10*\
**Example:** *shutitdown = shutdown /r*

# THIS ENDS THE .INI SECTION.

# SPECIAL ACTION COMMANDS  AKA TARPL (Tarpon Language)
## YESNO - YESNO allows you to popup a question to a user given them a choice of Yes or No.  
If Yes then the action after the '::' token will be taken.\
\
**Example:** 
*rebootornot = YESNO::Do you want to reboot your system now?::echo "## - rebooting in 10 seconds ##"; sleep 10; reboot*\

## MSGBOX - MSGBOX simply pop up a message dialog in the GUI,  or a displays text in a console application.
That requires a user to hit enter or press [OK] button if using the GUI.\

**Example:** 
*popupmessagetouser1 = MSGBOX "Please make sure this %hostIP% is the correct IP address."*

## (NOT IMPLEMENTED YET) [IF][THEN][ELSE] - [IF][THEN][ELSE] allow for conditional statements within actions.
**Example:** 
*checkipaddress = [IF]%hostIP% == 127.0.0.1[THEN]MSGBOX "You are using localhost"[ELSE]MSGBOX "You are not using localhost"*

## POPLIST - POPLIST allows a user to populate a list based on a comma delimitted string or file and select one.  
The syntax is: POPLIST "Message in double quotes" INPUTFILE <filename to read> or you can do INPUTLIST "one,two,three,four"\
The result selection can be used as a variable of the action key\
**Example:** 
*getusernames = POPLIST::Please choose a username::INPUTFILE::c:\path\usernames.txt::getusernamesfilevariable*\
**Example:** 
*getusernames = POPLIST::Please choose a username::INPUTLIST::"JAMES, FRED, MARY, JOHN"::getusernameslistvariable*

dothisactionnext1 = MSGBOX "You chose %getusernamesfilevariable%"\
dothisactionnext2 = MSGBOX "You chose %getusernameslistvariable%"

## IFGOTO - IFGOTO allows you to jump to an index name in the .ini file based on a condition 1 or 0 condition.
If the a goto happens, the execution of the .ini found will continue from that point.
**Example:** 
*makeuserdirectory = IFGOTO::test -d /usr/bin::iniindexnameyouwanttojumpto*

## EXEC_PYFUNC - EXEC_PYFUNC allows you to call a function from a .py file regardless of whether python is installed or not.
The syntax is:  EXEC_PYFUNC::folder_if_any\pythonfiletoexecute.py::name_of_function_to_execute::parameters,seperated,by,commas\
It can only handle string parameters right now!\
**Example:**\
executepython = EXEC_PYFUNC::sample-python-scripts\reminder.py::popup_message::"I Forgot","To Eat","Breakfast"

# FINAL NOTES:
Tarpon-Installer is a work in progress.  I have used it for many things.  I will start creating more\
examples installer.ini files in the future to show the true power.\
Thanks, Kevin Carr
