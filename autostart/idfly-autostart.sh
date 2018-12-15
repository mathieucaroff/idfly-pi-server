#!/bin/bash
#
# Start the server for the remote.
#
# This script assumes that the folder `pi-server` is in /home/pi.
# This script was refactored but didn't undergo test(s) afterward, so
# there is a slim chance that it might not work.

# Start pigpiod if not already started
pgrep pigpiod &>/dev/null || sudo pigpiod

# Kill any other running serveur
# Beware it doesn't use `kill -9`. Processe(s) may survive.
sudo kill $(pgrep -a python3 | grep idfly.py | cut -d' ' -f 1) &> /dev/null



## Start the server ##

logFile="/idfly.log"
# Skip a line in the log file
echo | sudo tee -a "$logFile"
# Print the date in the log file
date '+[%Y-%m-%dT%H:%M] Start' | sudo tee -a "$logFile"

# Start the server on port 80, sending its output to the log file. 
sudo python3 /home/pi/pi-server/idfly.py /home/pi/nodeRemote/ 80 \
| sudo tee -a "$logFile"
