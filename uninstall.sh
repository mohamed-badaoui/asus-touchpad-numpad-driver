#!/bin/bash

# -------------------------------------------------------
# A shell script that uninstall python driver for Asus numpad 
# MIT LICENSE file
# Written by: Badaoui Mohamed 
# Last updated on: 2021/04/04
# -------------------------------------------------------

if [[ $(id -u) != 0 ]]
then
	echo "Please, run this script as root (using sudo for example)"
	exit 1
fi

modprobe -r i2c-dev

if [[ $? != 0 ]]
then
	echo "i2c-dev module cannot be removed successfuly..."
	exit 1
fi

systemctl stop asus_touchpad_numpad
if [[ $? != 0 ]]
then
	echo "asus_touchpad_numpad.service cannot be stopped correctly..."
	exit 1
fi

systemctl disable asus_touchpad_numpad
if [[ $? != 0 ]]
then
	echo "asus_touchpad_numpad.service cannot be disabled correctly..."
	exit 1
fi

rm -f /lib/systemd/system/asus_touchpad_numpad.service
if [[ $? != 0 ]]
then
	echo "/lib/systemd/system/asus_touchpad_numpad.service cannot be removed correctly..."
	exit 1
fi

rm -f /usr/bin/asus_touchpad_numpad.py
if [[ $? != 0 ]]
then
	echo "/usr/bin/asus_touchpad_numpad.py cannot be removed correctly..."
	exit 1
fi

echo "Asus touchpad python driver uninstalled"
exit 0
