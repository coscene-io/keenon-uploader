#!/bin/bash

cat << EOF > /etc/apt/sources.list
## Note, this file is written by cloud-init on first boot of an instance
## modifications made here will not survive a re-bundle.
## if you wish to make changes you can:
## a.) add 'apt_preserve_sources_list: true' to /etc/cloud/cloud.cfg
##     or do the same in user-data
## b.) add sources in /etc/apt/sources.list.d
## c.) make changes to template file /etc/cloud/templates/sources.list.tmpl

# See http://help.ubuntu.com/community/UpgradeNotes for how to upgrade to
# newer versions of the distribution.
deb http://mirrors.cloud.aliyuncs.com/ubuntu/ xenial main restricted
deb-src http://mirrors.cloud.aliyuncs.com/ubuntu/ xenial main restricted

## Major bug fix updates produced after the final release of the
## distribution.
deb http://mirrors.cloud.aliyuncs.com/ubuntu/ xenial-updates main restricted
deb-src http://mirrors.cloud.aliyuncs.com/ubuntu/ xenial-updates main restricted

## N.B. software from this repository is ENTIRELY UNSUPPORTED by the Ubuntu
## team. Also, please note that software in universe WILL NOT receive any
## review or updates from the Ubuntu security team.
deb http://mirrors.cloud.aliyuncs.com/ubuntu/ xenial universe
deb-src http://mirrors.cloud.aliyuncs.com/ubuntu/ xenial universe
deb http://mirrors.cloud.aliyuncs.com/ubuntu/ xenial-updates universe
deb-src http://mirrors.cloud.aliyuncs.com/ubuntu/ xenial-updates universe

## N.B. software from this repository is ENTIRELY UNSUPPORTED by the Ubuntu
## team, and may not be under a free licence. Please satisfy yourself as to
## your rights to use the software. Also, please note that software in
## multiverse WILL NOT receive any review or updates from the Ubuntu
## security team.
deb http://mirrors.cloud.aliyuncs.com/ubuntu/ xenial multiverse
deb-src http://mirrors.cloud.aliyuncs.com/ubuntu/ xenial multiverse
deb http://mirrors.cloud.aliyuncs.com/ubuntu/ xenial-updates multiverse
deb-src http://mirrors.cloud.aliyuncs.com/ubuntu/ xenial-updates multiverse

## Uncomment the following two lines to add software from the 'backports'
## repository.
## N.B. software from this repository may not have been tested as
## extensively as that contained in the main release, although it includes
## newer versions of some applications which may provide useful features.
## Also, please note that software in backports WILL NOT receive any review
## or updates from the Ubuntu security team.
deb http://mirrors.cloud.aliyuncs.com/ubuntu/ xenial-backports main restricted universe multiverse
deb-src http://mirrors.cloud.aliyuncs.com/ubuntu/ xenial-backports main restricted universe multiverse

## Uncomment the following two lines to add software from Canonical's
## 'partner' repository.
## This software is not part of Ubuntu, but is offered by Canonical and the
## respective vendors as a service to Ubuntu users.
# deb http://archive.canonical.com/ubuntu xenial partner
# deb-src http://archive.canonical.com/ubuntu xenial partner

deb http://mirrors.cloud.aliyuncs.com/ubuntu xenial-security main restricted
deb-src http://mirrors.cloud.aliyuncs.com/ubuntu xenial-security main restricted
deb http://mirrors.cloud.aliyuncs.com/ubuntu xenial-security universe
deb-src http://mirrors.cloud.aliyuncs.com/ubuntu xenial-security universe
# deb http://mirrors.cloud.aliyuncs.com/ubuntu xenial-security multiverse
# deb-src http://mirrors.cloud.aliyuncs.com/ubuntu xenial-security multiverse
EOF

apt update
apt install patchelf
mkdir ~/.pip

cat << EOF > ~/.pip/pip.conf
[global]
index-url=https://mirrors.cloud.aliyuncs.com/pypi/simple/

[install]
trusted-host=mirrors.cloud.aliyuncs.com
EOF

pip install -r requirements.txt
pip install nuitka