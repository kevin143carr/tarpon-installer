# ><###> Build Adder <###><
Build Adder is a tool for automatically adding new versions of software to the tarpon-installer config.ini file.\
It has its own .ini file which you can call [anything you want].ini.\
\
In this file is two sections one for [FILES] and the other for [RPMS].\
If you are doing a Windows install then you just need the [FILES] section.\
If you are doing a Linux install you will need the [FILES] and maybe the [RPMS] if RPMs are to be installed.\
\
Build Adder adds latest builds in a folder to the Tarpon Installer Config.ini File.\
THE FOLDER MUST RESIDE UNDER THE [resources] FOLDER IN YOUR TARPON INSTALLER DIRECTORY\
This requires the following comments in your tarponconfig.ini file:\
#BUILDS START HERE\
#BUILDS END HERE\
\
#RPMS START HERE\
#RPMS END HERE\
\
Usage: buildadder -d yes -t tarponconfig.ini -b buildadderconfig.ini -f buildfolder1,buildfolder2 -r RPMS<--[UNDER THE resources FOLDER]\
\
Required Arguments:\
	-t     name of tarpon config file, such as win_local_config_3_2_7.ini\
	-b     name of buildadder config file, such as win_local_builder.ini\
	-f     folder in which the build files are located, can be multiple separated by comma\
	-r     folder in which the RPM files are located, can be multiple separated by comma\
	-d     cleans out the buildadder section in the ini file (yes or no) default no\
\
**Example** - MyInstallerBuild.ini\
[FILES]\
Reports = C:/Program Files (x86)/JAAR-RL/reporttool/resources/properties/aarreports\
ReportTool = C:/Program Files (x86)/JAAR-RL/reporttool\
activemq = C:/Program Files (x86)/Apache/activemq\
\
[RPMS]\
httpd = httpd,mod_http2,httpd-filesystem,httpd-tools\
\
**End Example**\
\
The secret to making this work is to use names that will always be in the file name.\
For example:  Let's say we put apache-activemq-5.16.0-bin.zip in our resources/externalbuilds folder.\
if you want to use activemq then put 'activemq' as your key (see above)\
and buildadder will search your builds folders for anything that has activemq as part of the name\
and add it to your tarpon-install installer.ini file under the [FILES] section.  In this case it might\
find the externalbuilds/apache-activemq-5.16.0-bin.zip and use that complete filename.

Same thing works for the RPMS.  But they are a little different.  You can stack multiple RPMs on one\
line in order to make sure all the dependent RPMs are in place.  But like the example above, it will find\
files located in the designated (-r) folder and put the full name of that version of the file in your\
installer.ini file.

