# Asus touchpad numpad driver

| Without % = symbols             |  With % = symbols       |  With % = symbols (but incompatible with the non-universal version) |
|:-------------------------:|:-------------------------:|:-------------------------:|
| Model/Layout = ux433fa          | Model/Layout = m433ia   | Model/Layout = ux581l |
| ![without % = symbols](https://github.com/mohamed-badaoui/ux433-touchpad-numpad/blob/main/Asus-ZenBook-UX433FA.jpg)  |  ![with % = symbols](https://github.com/mohamed-badaoui/ux433-touchpad-numpad/blob/main/Asus-VivoBook-M433IA.jpg) | ![model ux581](https://github.com/mohamed-badaoui/ux433-touchpad-numpad/blob/main/Asus-ZenBook-UX581l.jpg) |

This is a python service which enables switching between numpad and touchpad for the Asus UX433.
It may work for other models.

This python driver has been tested and works fine for these asus versions at the moment:
- M433IA (with % and = symbols)
- R424DA (without extra symbols)
- ROG Strix G15 2021 
- S413DA (with % and = symbols)
- TM420 (with % and = symbols)
- UM433DA (with % and = symbols)
- UX425EA (with % and = symbols)
- UX425JA (with % and = symbols)
- UX434FA (with % and = symbols)
- UX463FL (with % and = symbols)
- UX463FA (with % and = symbols)
- UX433 (without extra symbols)
- UX431F (without extra symbols)
- UX393 (with % and = symbols)
- UX371E (With % and = symbols)
- UX362-FA (without extra symbols)
- UX363EA (with % and = symbols)
- UX333FA (without extra symbols)
- UX325EA (with % and = symbols)
- X412DA (without extra symbols)
- UX581L (with % and = symbols)

Install required packages

- Debian / Ubuntu / Linux Mint / Pop!_OS / Zorin OS:
```
sudo apt install libevdev2 python3-libevdev i2c-tools git
```

- Arch Linux / Manjaro:
```
sudo pacman -S libevdev python-libevdev i2c-tools git
```

- Fedora:
```
sudo dnf install libevdev python-libevdev i2c-tools git
```

Then enabble i2c
```
sudo modprobe i2c-dev
sudo i2cdetect -l
```

Now you can get the latest ASUS Touchpad Numpad Driver for Linux from Git and install it using the following commands.
```
git clone https://github.com/mohamed-badaoui/asus-touchpad-numpad-driver
cd asus-touchpad-numpad-driver
sudo ./install.sh
```

To turn on/off numpad, tap top right corner touchpad area or F8 key.

To uninstall, just run:
```
sudo ./uninstall.sh
```

It is an adaptation made thanks to:
 - solution published on reddit (https://www.reddit.com/r/linuxhardware/comments/f2vdad/a_service_handling_touchpad_numpad_switching_for/) 
 - many contributions on launchpad (https://bugs.launchpad.net/ubuntu/+source/linux/+bug/1810183)

For any question, please do not hesitate to follow this tread discussion
(https://bugs.launchpad.net/ubuntu/+source/linux/+bug/1810183)

Thank you very much to all the contributors, mainly on launchpad, who made this device driver possible. (David/magellan-2000, Pilot6/hanipouspilot, Julian Oertel /clunphumb, YannikSc and so many others. GG!)

