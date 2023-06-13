# ><###> Build Adder <###><
Build Adder is a tool for automatically adding new versions of software to the tarpon-installer config.ini file.\
It has its own .ini file which you can call [anything you want].ini.\
\
In this file is two sections one for [FILES] and the other for [RPMS].\
If you are doing a Windows install then you just need the [FILES] section.\
If you are doing a Linux install you will need the [FILES] and maybe the [RPMS] if RPMs are to be installed.\

Build Adder adds latest builds in a folder to the Tarpon Installer Config.ini File.
THE FOLDER MUST RESIDE UNDER THE [resources] FOLDER IN YOUR TARPON INSTALLER DIRECTORY
This requires the following comments in your tarponconfig.ini file:
#BUILDS START HERE
#BUILDS END HERE

#RPMS START HERE
#RPMS END HERE

Usage: buildadder -d yes -t tarponconfig.ini -b buildadderconfig.ini -f buildfolder1,buildfolder2 <--[UNDER THE resources FOLDER]

Required Arguments:
	-t     name of tarpon config file, such as win_local_config_3_2_7.ini
	-b     name of buildadder config file, such as win_local_builder.ini
	-f     folder in which the build files are located, can be multiple separated by comma
	-r     folder in which the RPM files are located, can be multiple separated by comma
	-d     cleans out the buildadder section in the ini file (yes or no) default no

**Example** - MyInstallerBuild.ini
[FILES]
Reports = C:/Program Files (x86)/JAAR-RL/reporttool/resources/properties/aarreports
ReportTool = C:/Program Files (x86)/JAAR-RL/reporttool
ActiveMQ = C:/Program Files (x86)/Apache/activemq

[RPMS]
httpd = httpd,mod_http2,httpd-filesystem,httpd-tools

**End Example**

The secret to making this work is to use names that will always

