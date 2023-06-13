# ><###> Modify Host Names <###><
This is a simple tool that can be used for both Linux and Windows to modify the hosts file.\

*  Modify Hostnames														*\
*  modifies the hosts files with as many IPs you need					*\
*																		*\
* 	--searchfor = previous entry hostname								*\
* 	--addresses = name and IP address to put in							*\
* 	--modifier = identifies application or person who made the change	*

You can have multiple addresses by adding a comma between the addresses\
**Example**\
modifyhostsnames --searchfor test --modifier myname(or something else) --addresses test1=a.a.a.a,test2=b.b.b.b\
\
# ><###> Modify Postgres HBA <###><
*  ><###> Modify pg_hba.conf files <###>< is an open source install creator. *"\
**Example**\
usage: modifypostgreshba --address xxx.xxx.xxx.xxx (where xxx = IP address) --directory /var/lib/pgsql 