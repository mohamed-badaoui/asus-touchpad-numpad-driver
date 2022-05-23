#!/bin/bash

if [[ $(id -u) != 0 ]]
then
	echo "Please, run this script as root (using sudo for example)"
	exit 1
fi

modprobe -r i2c-dev

if [[ $? != 0 ]]
then
	echo "i2c-dev module cannot be removed successfuly..."
	# exit 1
fi

systemctl stop asus_touchpad_numpad
if [[ $? != 0 ]]
then
	echo "asus_touchpad_numpad.service cannot be stopped correctly..."
	# exit 1
fi

systemctl disable asus_touchpad_numpad
if [[ $? != 0 ]]
then
	echo "asus_touchpad_numpad.service cannot be disabled correctly..."
	# exit 1
fi

rm -f /etc/systemd/system/asus_touchpad_numpad.service
if [[ $? != 0 ]]
then
	echo "/etc/systemd/system/asus_touchpad_numpad.service cannot be removed correctly..."
	# exit 1
fi

rm -rf /usr/share/asus_touchpad_numpad-driver/
if [[ $? != 0 ]]
then
	echo "/usr/share/asus_touchpad_numpad-driver/ cannot be removed correctly..."
	# exit 1
fi

echo "Asus touchpad python driver uninstalled"
