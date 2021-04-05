# UX433 touchpad numpad

![alt text](https://github.com/mohamed-badaoui/ux433-touchpad-numpad/blob/main/Asus-ZenBook-UX433FA.jpg)

This is a python service which enables switching between numpad and touchpad for the Asus UX433.
It may work for other models.

Install required packages

```
sudo aptitude install libevdev2
sudo aptitude install i2c-tools
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

It is an adaptation of a solution published on reddit (https://www.reddit.com/r/linuxhardware/comments/f2vdad/a_service_handling_touchpad_numpad_switching_for/) and the users' contributions  on launchpad (https://bugs.launchpad.net/ubuntu/+source/linux/+bug/1810183)

For any question, please do not hesitate to follow this tread discussion
(https://bugs.launchpad.net/ubuntu/+source/linux/+bug/1810183)

Many contributors could help you to adapt this to your laptop as a workaround for the moment.
The contributor magellan-2000 has worked on a solution for the M433IA asus model, do not hesitate to contact him for further informations.

