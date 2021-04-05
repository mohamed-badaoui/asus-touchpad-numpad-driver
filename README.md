# UX433 touchpad numpad

Without % = symbols             |  With % = symbols
:-------------------------:|:-------------------------:
![without % = symbols](https://github.com/mohamed-badaoui/ux433-touchpad-numpad/blob/main/Asus-ZenBook-UX433FA.jpg)  |  ![with % = symbols](https://github.com/mohamed-badaoui/ux433-touchpad-numpad/blob/main/Asus-VivoBook-M433IA.jpg)

This is a python service which enables switching between numpad and touchpad for the Asus UX433.
It may work for other models.

This python driver has been tested and works fine for these asus versions at the moment:
- X412DA (without extra symbols)
- UX433 (without extra symbols)
- UX431F (without extra symbols)
- UX434FA (with % and = symbols)
- UX363EA (with % and = symbols)
- M433IA (with % and = symbols)
- TM420 (with % and = symbols)

Install required packages

```
sudo aptitude install libevdev2 i2c-tools
sudo modprobe i2c-dev
sudo i2cdetect -l
```

You need to install the python libevdev package, run install.sh and reboot (or start the service).

```
sudo pip3 install libevdev
sudo chmod +x ./install.sh
sudo ./install.sh
```
To turn on/off numpad, tap top right corner touchpad area or F8 key.

It is an adaptation made thanks to:
 - solution published on reddit (https://www.reddit.com/r/linuxhardware/comments/f2vdad/a_service_handling_touchpad_numpad_switching_for/) 
 - many contributions on launchpad (https://bugs.launchpad.net/ubuntu/+source/linux/+bug/1810183)

For any question, please do not hesitate to follow this tread discussion
(https://bugs.launchpad.net/ubuntu/+source/linux/+bug/1810183)

Thank you very much to all the contributors, mainly on launchpad, who made this device driver possible. (David/magellan-2000, Pilot6/hanipouspilot, Julian Oertel /clunphumb and so many others. GG!)

