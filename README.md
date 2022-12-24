# Asus touchpad numpad driver

| Without % = symbols             |  With % = symbols       |  With % = symbols (but incompatible with the non-universal version) |
|:-------------------------:|:-------------------------:|:-------------------------:|
| Model/Layout = ux433fa          | Model/Layout = m433ia   | Model/Layout = ux581l |
| ![without % = symbols](https://github.com/mohamed-badaoui/ux433-touchpad-numpad/blob/main/images/Asus-ZenBook-UX433FA.jpg)  |  ![with % = symbols](https://github.com/mohamed-badaoui/ux433-touchpad-numpad/blob/main/images/Asus-VivoBook-M433IA.jpg) | ![model ux581](https://github.com/mohamed-badaoui/ux433-touchpad-numpad/blob/main/images/Asus-ZenBook-UX581l.jpg) |

This is a python service which enables switching between numpad and touchpad for the Asus UX433. It may work for other models. When running the script, use as an argument one of the strings `ux433fa` or `m433ia` or `ux581l to select the layout that fits your touchpad. You can inspect the different layouts [here](https://github.com/mohamed-badaoui/asus-touchpad-numpad-driver/tree/main/numpad_layouts).

This python driver has been tested and works fine for these asus versions at the moment:
- E210MA (with % and = symbols)
- M433IA (with % and = symbols)
- R424DA (without extra symbols)
- ROG Strix G15 2021 
- S413DA (with % and = symbols)
- TM420 (with % and = symbols)
- UM425I (with % and = symbols)
- UM425IA (with % and = symbols)
- UM425UA (with % and = symbols)
- UM431DA (without extra symbols)
- UM433DA (with % and = symbols)
- UX425EA (with % and = symbols)
- UX425JA (with % and = symbols)
- UX434FA (with % and = symbols)
- UX463FL (with % and = symbols)
- UX463FA (with % and = symbols)
- UM462DA (without extra symbols)
- UX433 (without extra symbols)
- UX431F (without extra symbols)
- UX393 (with % and = symbols)
- UX371E (With % and = symbols)
- UX362-FA (without extra symbols)
- UX363EA (with % and = symbols)
- UX363JA (with % and = symbols)
- UX333FA (without extra symbols)
- UX325EA (with % and = symbols)
- UM325UA (with % and = symbols)
- X412DA (without extra symbols)
- UX581L (with % and = symbols)
- Zephyrus S GX701 (with % and = symbols)

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

- NixOS:

Add these to your `/etc/nixos/configuration.nix`:

```nix
# i2c for https://github.com/mohamed-badaoui/asus-touchpad-numpad-driver
hardware.i2c.enable = true;
systemd.services.asus-touchpad-numpad = {
  description = "Activate Numpad inside the touchpad with top right corner switch";
  documentation = ["https://github.com/mohamed-badaoui/asus-touchpad-numpad-driver"];
  path = [ pkgs.i2c-tools ];
  script = ''
    cd ${pkgs.fetchFromGitHub {
      owner = "mohamed-badaoui";
      repo = "asus-touchpad-numpad-driver";
      # These needs to be updated from time to time
      rev = "d80980af6ef776ee6acf42c193689f207caa7968";
      sha256 = "sha256-AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=";
    }}
    # In the last argument here you choose your layout.
    ${pkgs.python3.withPackages(ps: [ ps.libevdev ])}/bin/python asus_touchpad.py ux433fa
  '';
  # Probably needed because it fails on boot seemingly because the driver
  # is not ready yet. Alternativly, you can use `sleep 3` or similar in the
  # `script`.
  serviceConfig = {
    RestartSec = "1s";
    Restart = "on-failure";
  };
  wantedBy = [ "multi-user.target" ];
};

```

Then enable i2c
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

To turn on/off numpad, tap top right corner touchpad area.
To adjust numpad brightness, tap top left corner touchpad area.

To uninstall, just run:
```
sudo ./uninstall.sh
```

**Troubleshooting**

To activate logger, do in a console:
```
LOG=DEBUG sudo -E ./asus_touchpad.py
```

For some operating systems with boot failure (Pop!OS, Mint, ElementaryOS, SolusOS), before installing, please uncomment in the asus_touchpad.service file, this following property and adjust its value:
```
# ExecStartPre=/bin/sleep 2
```


It is an adaptation made thanks to:
 - solution published on reddit (https://www.reddit.com/r/linuxhardware/comments/f2vdad/a_service_handling_touchpad_numpad_switching_for/) 
 - many contributions on launchpad (https://bugs.launchpad.net/ubuntu/+source/linux/+bug/1810183)

For any question, please do not hesitate to follow this tread discussion
(https://bugs.launchpad.net/ubuntu/+source/linux/+bug/1810183)

Thank you very much to all the contributors, mainly on launchpad, who made this device driver possible. (Kawaegle, David/magellan-2000, Pilot6/hanipouspilot, Julian Oertel /clunphumb, YannikSc and so many others. GG!)

