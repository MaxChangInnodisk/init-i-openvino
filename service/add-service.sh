#!/bin/bash

sudo chmod +x ./run-ivit-i-intel.sh
sudo chmod +x ./run-ivit-web-ui.sh

sudo chmod 644 ./ivit.service
sudo chmod 644 ./ivit-demo.service

sudo cp ./ivit.service /etc/systemd/system/
sudo cp ./ivit-demo.service /etc/systemd/system/

ls /etc/systemd/system | grep ivit

sudo systemctl daemon-reload

sudo systemctl enable ivit
sudo systemctl enable ivit-demo