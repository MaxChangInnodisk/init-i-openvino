#!/bin/bash

sudo update-rc.d ivit_service start 99 1 2 3 4 5 . stop 90 0 6 .
sudo update-rc.d ivit-i-safe-factory start 99 1 2 3 4 5 . stop 90 0 6 .
