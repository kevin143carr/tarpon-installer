# ><###> Tarpon-Installer <###><
Tarpon Installer allows for local and remote installations based on a configuration file.  
It is command line based. Currently it supports remote installs from Windows to Linux, 
Linux to Linux and Local Windows and Local Linux installs.

I originally developed it to distribute different kinds of builds to raspberry pi(s), but
ended up using it at my work for many different purposes, including providing updates.

It uses a config.ini (which can be named [anything].ini) and a resource folder.

# CONFIG.INI EXPLAINED
### [USERINFO] # Information needed to log into the machine
This is the username and password fields.  Yes it is in plaintext!  This is often
used to update hosts files and other files that need this information, especially when
doing remote installations.  The username and password will be used to ssh into a linux
box when doing a "Remote Linux Install".

### [SERVERCONFIG] # ip address information
Perhaps not the best name, but this field is used as the Remote IP that will be ssh(d) into
as well as used to update hosts files and other configuration files that is needed.  You can use the %host% 
to use as a variable to the host field.

### [BUILD] # buildtype:(WINDOWS OR LINUX) -- installtype:(LOCAL OR REMOTE) -- resources: (Relative or Full path)
**buildtype** = *Used to determine if the installed files are going on a LINUX or WINDOWS system.  Use upper case!*\
**installtype** =	*# Used to determine if it is a LOCAL or REMOTE style install.*\
**resources** = *# Used to tell the installer where the resource directory is it can be either a*\
*full path such as C:\Resources or a relative path to the executable '/resources'.*\
*This is where you place files you want to copy onto the new system.*\
**Example: repo.tar.gz** = /root/repo*\
**Example: installpkg.sh** = /root*\
**Example: resources** = c:\support\resources

### [REPO] # Files that support using RPMs and a local repo
**repo.tar.gz** =		*# Used to point the installer to a local repo extracted from a repo.tar.gz file*\
**installpkg.sh** =	*# Path to the installpkg.sh file*\
*There are two utility scripts included called getpackage.sh and installpkg.sh.  getpackage.sh downloads*\
*a package to the repo folder, while installpkg.sh will install that package.*\
*The repo folder should then be zipped up using the linux gzip command.  The name **HAS TO BE** **repo.tar.gz**

### [RPM] #RPMs (name/command) that need to be installed prior to softare installation
**unzip = unzip**	*# this will install the unzip RPM from the local repo*\
**postgresql-12**	*# postgresql12-server # this will install postgresql RPM from the local repo*\
**httpd = httpd**	*# this will install the httpd RPM from the local repo*\
**java = java**	*# This will install java RPM from the local repo*\

### [FILES] # Copies files from the resource folder to the paths and unzips if necessary.
*if a specified directory does not exists it will create it.  It will unzip in the specified folder*\
*as well as keeping the subdirectories.  BUT it will ignore an initial folder in the zip file if one exists*\
**Simple Copy Example:** *httpd.conf = c:/support/httpd/Apache24/conf*\
**Rename copy Example:** *myappsettings.json = c:/support/thing/appsettings.json*\
**Unzip file Example:** *transformer.zip = c:/support/newtransform*\

### [ACTIONS] # Actions executed at the command level (both Linux and Windows), each action has to be uniquely named
*Most anything that can be done from a command line can be done with this*\
**Echo Example:** *echo1 = echo THIS IS A TEST*\
**Windows Timeout Example:** *timeout1 = timeout /t 3*\
**Delete Example:** *cleanzip1 = del /Q c:\support\washere.zip

### [MODIFY] {LINUX ONLY} # Used to modify files - MUST USE 1,2,3,ETC.. DESIGNATORS
*usage: (number-)filepath+filename = keyword||replaceword (this only works in strings without "", /, \)*\
**Example:** *1-/var/lib/pgsql/12/data/postgresql.conf = #listen_addresses = 'localhost'||listen_addresses = '*'*\
**Example:** *2-/var/lib/pgsql/12/data/postgresql.conf = log_timezone =||log_timezone = 'UTC' #changed#*\
**Example:** *3-/opt/webconfigurationmanager/appsettings.json = localhost:55001||*:55001*\

### [FINAL] # Same as Actions but is the last things done, each action has to be uniquely named
**Example:** *statusjaardcm = systemctl status jaardcm | grep Active:*\
**Example:** *statusjaarwcm = systemctl status jaarwcm | grep Active:*\
**Example:** *rebootmachine = echo "********* FINISHED AND REBOOTING IN 10 SECONDS *********"*\
**Example:** *starttimer = timeout /t 10*\
**Example:** *shutitdown = shutdown /r*

# FINAL NOTES:
*I like using pyinstaller with it so I only have the executable, config file and resource folder.*\
*A typical **REMOTE LINUX INSTALL** looks like this from a **WINDOWS** box:*\
*D:\installer*\
*D:\installer\config.ini*\
*D:\installer\tarpon_installer.exe* (using pyinstall)*\
*D:\installer\resources*\ (make sure installpkg.sh is in there)

