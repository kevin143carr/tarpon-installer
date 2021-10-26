# Tarpon-Installer
Tarpon Installer allows for local and remote installations based on a configuration file.  
It is command line based. Currently it supports remote installs from Windows to Linux, 
Linux to Linux and Local Windows and Linux installs.

I originally developed it to distribute different kinds of builds to raspberry pi(s), but
ended up using it at my work for many different purposes, including providing updates.

It uses a config.ini (which can be named [anything].ini) and a resource folder.

# CONFIG.INI EXPLAINED
### [USERINFO] # Information needed to login into the machine
The contains the username and password fields.  Yes it is in plaintext!  This is often
used to update hosts files and other files that need this information, especially when
doing remote installations.  The username and password will be used to ssh into a linux
box when doing a "Remote Linux Install".

### [SERVERCONFIG] # ip address information
Perhaps not the best name, but this field is used as the Remote IP that will be ssh(d) into
as well as used to update hosts files and other configuration files that is needed.

### [BUILD] # buildtype:(WINDOWS OR LINUX) -- installtype:(LOCAL OR REMOTE) -- resources:example shows relative folder
**buildtype** = *Used to determine if the installed files are going on a LINUX or WINDOWS system.  Use upper case!*\
**installtype** =	*# Used to determine if it is a LOCAL or REMOTE style install.*\
**resources** = *# Used to tell the installer where the resource directory is it can be either a*\
				*# full path such as C:\Resources or a relative path to the executable '/resources'*\
	*Example: repo.tar.gz = /root/repo*\
	*Exmample: installpkg.sh = /root*\

### [REPO] # Files that support the RPMS
**repo.tar.gz** =		*# Used to point the installer to a local repo extracted from a repo.tar.gz file*\
**installpkg.sh** =	*# Path to the installpkg.sh file*\
*There are two utility scripts included called getpackage.sh and installpkg.sh.  getpackage.sh downloads*\
*a package to the repo folder, while installpkg.sh will install that package.*\

### [RPM] #RPMs (name/command) that need to be installed prior to softare installation
**unzip = unzip**	*# this will install the unzip RPM from the local repo*\
**postgresql-12**	*# postgresql12-server # this will install postgresql RPM from the local repo*\
**httpd = httpd**	*# this will install the httpd RPM from the local repo*\
**java = java**	*# This will install java RPM from the local repo*\
