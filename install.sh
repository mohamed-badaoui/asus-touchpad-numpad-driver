#!/bin/bash

# -------------------------------------------------------
# A shell script that install python driver for Asus numpad 
# MIT LICENSE file
# Written by: Badaoui Mohamed 
# Last updated on: 2021/04/04
# -------------------------------------------------------

sudo modprobe i2c-dev
interfaces=$(for i in $(sudo i2cdetect -l | grep DesignWare | sed -r "s/^(i2c\-[0-9]+).*/\1/"); do echo $i; done)
if [ -z "$interfaces" ]
then
    echo "No interface s2c found. Make sure you have installed libevdev packages"
    exit 0
fi

touchpad_detected=false;
for i in $interfaces; do
    echo -n "Testing interface $i : ";
    number=$(echo -n $i | cut -d'-' -f2)
    i2c_test=$(sudo i2ctransfer -f -y $number w13@0x15 0x05 0x00 0x3d 0x03 0x06 0x00 0x07 0x00 0x0d 0x14 0x03 0x00 0xad 2>&1)
    if [ -z "$i2c_test" ]
    then
        echo "sucess"
        touchpad_detected=true;
        break
    else
        echo "failed"
    fi
done;

if [ "$touchpad_detected" = false ] ; then
    echo 'The detection was not successful. Touchpad not found.'
    exit 0
fi

is_qwerty=false;

echo "What is your keyboard layout?"
PS3='Please enter your choice: '
options=("Qwerty" "Azerty" "Quit")
select opt in "${options[@]}"
do
    case $opt in
        "Qwerty")
        is_qwerty=true
            break
            ;;
        "Azerty")
        is_qwerty=false
            break
            ;;
        "Quit")
            exit 0
            ;;
        *) echo "invalid option $REPLY";;
    esac
done

echo
echo "What is your Numpad layout model like?"
PS3='Please enter your choice: '
options=("Numpad without % and = symbols" "Numpad with % and = symbols" "Quit")
select opt in "${options[@]}"
do
    case $opt in
        "Numpad without % and = symbols")
        echo "Copy asus python driver to /usr/bin/asus_touchpad_numpad.py"
            cat touchpad_numpad_ux433.py | sed -r "s/-y ([0-9]+)/-y $number/" | sudo tee /usr/bin/asus_touchpad_numpad.py >/dev/null
            break
            ;;
        "Numpad with % and = symbols")
            echo "Copy asus python driver to /usr/bin/asus_touchpad_numpad.py"
            if [ "$is_qwerty" = true ] ; then
                cat touchpad_numpad_m433ia.py | sed -r "s/-y ([0-9]+)/-y $number/" | sed -r "s/KEY_APOSTROPHE/KEY_5/" | sudo tee /usr/bin/asus_touchpad_numpad.py >/dev/null
            else
                cat touchpad_numpad_m433ia.py | sed -r "s/-y ([0-9]+)/-y $number/" | sudo tee /usr/bin/asus_touchpad_numpad.py >/dev/null
            fi
            break
            ;;
        "Quit")
            exit 0
            ;;
        *) echo "invalid option $REPLY";;
    esac
done



echo "Add asus touchpad service in /lib/systemd/system/"
sudo cp ./asus_touchpad_numpad.service /lib/systemd/system/
echo "i2c-dev" | sudo tee /etc/modules-load.d/i2c-dev.conf

sudo systemctl enable asus_touchpad_numpad
echo "Asus touchpad service enabled"
sudo systemctl start asus_touchpad_numpad
echo "Asus touchpad service started"
