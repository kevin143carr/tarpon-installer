echo install package $1
mkdir repo
mkdir repo/$1.repo
yum install --downloadonly --installroot=/root/repo/$1-installroot --releasever=7 --downloaddir=/root/repo/$1.repo $1
# yum install --downloadonly --installroot=/var/tmp/repo/$1-installroot --releasever=7 --downloaddir=/var/tmp/repo/$1 $1
# createrepo --database /var/tmp/repo/$1
createrepo --database /root/repo/$1.repo
rm -rf /var/tmp/$1-installroot

