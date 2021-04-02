# UX433 touchpad numpad

![alt text](https://github.com/mohamed-badaoui/ux433-touchpad-numpad/blob/main/Asus-ZenBook-UX433FA.jpg)

This is a python service which enables switching between numpad and touchpad for the Asus UX433.
It may work for other models.

Install required packages

```
sudo aptitude install i2c-tools
sudo modprobe i2c-dev
sudo i2cdetect -l
```

Before installation, you need to check/modify the ic2 adapter number in ux433_touchpad_numpad.py file

The rigth one, is one with label "I2C adapter"

So, if the number is 2 for example, try to turn on your numpad (replace "-y 2" by your adapter number):
```
sudo i2ctransfer -f -y 2 w13@0x15 0x05 0x00 0x3d 0x03 0x06 0x00 0x07 0x00 0x0d 0x14 0x03 0x01 0xad
```

Then, you need to install the python libevdev package, run install.sh and reboot (or start the service).

```
sudo pip3 install libevdev
sudo sh install.sh
```
To turn on/off numpad, tap top right touchpad area or F8 key. 

It is an adaptation of a solution published on reddit (https://www.reddit.com/r/linuxhardware/comments/f2vdad/a_service_handling_touchpad_numpad_switching_for/) and the users' contributions  on launchpad (https://bugs.launchpad.net/ubuntu/+source/linux/+bug/1810183)
