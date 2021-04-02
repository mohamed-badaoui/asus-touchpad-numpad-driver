# UX433 touchpad numpad

This is a python service which enables switching between numpad and touchpad for the Asus UX433.
It may work for other models.

Before installation, you need to check/modify the ic2 adapter number in ux433_touchpad_numpad.py file
```
sudo aptitude install i2c-tools
sudo i2cdetect -l
```
The rigth one, is one with label "I2C adapter"

So, if the number is 2 for example, try to turn on your numpad (replace "-y 2" by your adapter number):
```
sudo i2ctransfer -f -y 2 w13@0x15 0x05 0x00 0x3d 0x03 0x06 0x00 0x07 0x00 0x0d 0x14 0x03 0x01 0xad
```

Then, you need to install the python libevdev package, run install.sh and reboot (or start the service).

```
sudo pip3 install libevdev
sudo modprobe i2c-dev
```
To turn on/off numpad, tap F8 key. 
