#!/bin/bash

cat << EOF > /etc/apt/sources.list
deb https://mirrors.cloud.aliyuncs.com/ubuntu/ xenial main
deb-src https://mirrors.cloud.aliyuncs.com/ubuntu/ xenial main

deb https://mirrors.cloud.aliyuncs.com/ubuntu/ xenial-updates main
deb-src https://mirrors.cloud.aliyuncs.com/ubuntu/ xenial-updates main

deb https://mirrors.cloud.aliyuncs.com/ubuntu/ xenial universe
deb-src https://mirrors.cloud.aliyuncs.com/ubuntu/ xenial universe
deb https://mirrors.cloud.aliyuncs.com/ubuntu/ xenial-updates universe
deb-src https://mirrors.cloud.aliyuncs.com/ubuntu/ xenial-updates universe

deb https://mirrors.cloud.aliyuncs.com/ubuntu/ xenial-security main
deb-src https://mirrors.cloud.aliyuncs.com/ubuntu/ xenial-security main
deb https://mirrors.cloud.aliyuncs.com/ubuntu/ xenial-security universe
deb-src https://mirrors.cloud.aliyuncs.com/ubuntu/ xenial-security universe
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