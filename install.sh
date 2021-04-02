#! /bin/bash
sudo modprobe i2c-dev
sudo cp ./ux433_touchpad_numpad.py /usr/bin
sudo cp ./ux433_touchpad_numpad.service /lib/systemd/system/
echo "i2c-dev" | sudo tee /etc/modules-load.d/i2c-dev.conf
sudo systemctl enable ux433_touchpad_numpad
sudo systemctl start ux433_touchpad_numpad