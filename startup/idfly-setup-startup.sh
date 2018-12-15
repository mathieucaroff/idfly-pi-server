#!/bin/bash
#
# idfly-setup-startup.sh
#
# This script assumes that the folder `pi-server` is in /home/pi.

# To setup autostart using the lxsession autostart system, you need to
# add a line to the autostart file. This is what this script does, but I
# didn't test it, so you might want to do it manually.
#
# The line must consist of an `@`, followed by a command to execute,
# see below.

line="@bash /home/pi/pi-server/startup/idfly-startup.sh"
autostartFile="/home/pi/.config/lxsession/LXDE-pi/autostart"

echo "$line" >> "$autostartFile"