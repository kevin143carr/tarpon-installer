# Tarpon-Installer
Tarpon Installer allows for local and remote installations based on a configuration file.  
It is command line based. Currently it supports remote installs from Windows to Linux, 
Linux to Linux and Local Windows and Unix installs.

I originally developed it to distribute different kinds of builds to raspberry pi(s), but
ended up using it at my work for many different purposes, including providing updates.

It uses a config.ini (which can be named [anything].ini) and a resource folder.

# CONFIG.INI EXPLAINED
#### [USERINFO] # Information needed to login into the machine

