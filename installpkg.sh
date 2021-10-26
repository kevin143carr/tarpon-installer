PKG=$1
echo "[offline-$PKG]
name=CentOS-\$releasever - $1
baseurl=file:///root/repo/$1.repo/
enabled=0
gpgcheck=1
gpgkey=file:///etc/pki/rpm-gpg/RPM-GPG-KEY-CentOS-7" >  /etc/yum.repos.d/offline-$PKG.repo

# install package offline:
yum -y --disablerepo=\* --enablerepo=offline-$PKG install --nogpgcheck $1
