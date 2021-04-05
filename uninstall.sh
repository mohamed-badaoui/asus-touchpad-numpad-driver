#!/bin/bash

# -------------------------------------------------------
# A shell script that uninstall python driver for Asus numpad 
# MIT LICENSE file
# Written by: Badaoui Mohamed 
# Last updated on: 2021/04/04
# -------------------------------------------------------

sudo modprobe -r i2c-dev
sudo systemctl stop asus_touchpad_numpad
sudo systemctl disable asus_touchpad_numpad
sudo rm -rf /lib/systemd/system/asus_touchpad_numpad.service
sudo rm -rf /usr/bin/asus_touchpad_numpad.py

echo "Asus touchpad python driver uninstalled"
