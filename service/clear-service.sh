#!/bin/bash

systemctl stop ivit
systemctl disable ivit
rm /etc/systemd/system/ivit
rm /etc/systemd/system/ivit # and symlinks that might be related
rm /usr/lib/systemd/system/ivit 
rm /usr/lib/systemd/system/ivit # and symlinks that might be related

systemctl stop ivit-demo
systemctl disable ivit-demo
rm /etc/systemd/system/ivit-demo
rm /etc/systemd/system/ivit-demo # and symlinks that might be related
rm /usr/lib/systemd/system/ivit-demo 
rm /usr/lib/systemd/system/ivit-demo # and symlinks that might be related

systemctl daemon-reload
systemctl reset-failed

rm /etc/systemd/system/graphical.target.wants/*