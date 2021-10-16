#!/usr/bin/python3

import importlib
import math
import re
import subprocess
import sys
from fcntl import F_SETFL, fcntl
from os import O_NONBLOCK
from subprocess import PIPE, Popen
from time import sleep

from libevdev import EV_ABS, EV_KEY, EV_LED, EV_SYN, Device, InputEvent

model = 'gx701'  # Model used in the derived script (with symbols)
if len(sys.argv) > 1:
    model = sys.argv[1]
model_layout = importlib.import_module('numpad_layouts.' + model)

if len(sys.argv) > 2:
    percentage_key = EV_KEY.codes[int(sys.argv[2])]

tries = model_layout.try_times

# Look into the devices file #
while tries > 0:

    keyboard_detected = 0
    touchpad_detected = 0

    with open('/proc/bus/input/devices', 'r') as f:

        lines = f.readlines()
        for line in lines:
            # Look for the touchpad #
            if touchpad_detected == 0 and ("Name=\"ASUE" in line or "Name=\"ELAN" in line) and "Touchpad" in line:
                print("Touchpad detected: " + line)
                touchpad_detected = 1

            if touchpad_detected == 1:
                if "S: " in line:
                    # search device id
                    device_id = re.sub(r".*i2c-(\d+)/.*$", r'\1', line).replace("\n", "")

                if "H: " in line:
                    touchpad = line.split("event")[1]
                    touchpad = touchpad.split(" ")[0]
                    touchpad_detected = 2

            # Look for the keyboard (numlock) # AT Translated Set OR Asus Keyboard
            if keyboard_detected == 0 and ("Name=\"AT Translated Set 2 keyboard" in line or "Name=\"Asus Keyboard" in line):
                print("Keyboard_detected detected: " + line)
                keyboard_detected = 1

            if keyboard_detected == 1:
                if "H: " in line:
                    keyboard = line.split("event")[1]
                    keyboard = keyboard.split(" ")[0]
                    keyboard_detected = 2

            # Stop looking if both have been found #
            if keyboard_detected == 2 and touchpad_detected == 2:
                break

    if keyboard_detected != 2 or touchpad_detected != 2:
        tries -= 1
        if tries == 0:
            if keyboard_detected != 2:
                print("Can't find keyboard, code " + str(keyboard_detected))
            if touchpad_detected != 2:
                print("Can't find touchpad, code " + str(touchpad_detected))
            if touchpad_detected == 2 and not device_id.isnumeric():
                print("Can't find device id")
            sys.exit(1)
    else:
        break

    sleep(model_layout.try_sleep)

# Start monitoring the touchpad #
fd_t = open('/dev/input/event' + str(touchpad), 'rb')
fcntl(fd_t, F_SETFL, O_NONBLOCK)
d_t = Device(fd_t)
# Retrieve touchpad dimensions #
ai = d_t.absinfo[EV_ABS.ABS_X]
(minx, maxx) = (ai.minimum, ai.maximum)
ai = d_t.absinfo[EV_ABS.ABS_Y]
(miny, maxy) = (ai.minimum, ai.maximum)

# Start monitoring the keyboard (numlock) #
fd_k = open('/dev/input/event' + str(keyboard), 'rb')
fcntl(fd_k, F_SETFL, O_NONBLOCK)
d_k = Device(fd_k)


# KEY_5:6
# KEY_APOSTROPHE:40
# [...]
percentage_key = EV_KEY.KEY_5
calculator_key = EV_KEY.KEY_CALC

# Create a new keyboard device to send numpad events #
dev = Device()
dev.name = "Asus Touchpad/Numpad"
dev.enable(EV_KEY.KEY_LEFTSHIFT)
dev.enable(EV_KEY.KEY_NUMLOCK)
dev.enable(calculator_key)

for col in model_layout.keys:
    for key in col:
        dev.enable(key)

if percentage_key != EV_KEY.KEY_5:
    dev.enable(percentage_key)

# 31: Low, 24: Half, 1: Full
BRIGHT_VAL = [hex(val) for val in [31, 24, 1]]

udev = dev.create_uinput_device()
x = 0
y = 0
brightness = 0
numlock = False

#try:
#    sub_value = subprocess.check_output('xset -q | grep "Num Lock" | cut -c 46-48', shell=True).decode().strip()
#    if str(sub_value) == 'on':
#        numlock = True
#except OSError as e:
#    pass


def press_key(pressed_key):
    try:
        udev.send_events([
            InputEvent(pressed_key, 1),
            InputEvent(EV_SYN.SYN_REPORT, 0),
        ])
    except OSError as e:
        pass


def release_key(released_key):
    try:
        udev.send_events([
            InputEvent(released_key, 0),
            InputEvent(EV_SYN.SYN_REPORT, 0),
        ])
    except OSError as e:
        pass


def send_key(sent_key):
    press_key(sent_key)
    release_key(sent_key)


def activate_numlock(brightness):
    numpad_cmd = "i2ctransfer -f -y " + device_id + " w13@0x15 0x05 0x00 0x3d 0x03 0x06 0x00 0x07 0x00 0x0d 0x14 0x03 " + BRIGHT_VAL[brightness] + " 0xad"
    press_key(EV_KEY.KEY_NUMLOCK)
    d_t.grab()
    subprocess.call(numpad_cmd, shell=True)


def deactivate_numlock():
    numpad_cmd = "i2ctransfer -f -y " + device_id + " w13@0x15 0x05 0x00 0x3d 0x03 0x06 0x00 0x07 0x00 0x0d 0x14 0x03 0x00 0xad"
    release_key(EV_KEY.KEY_NUMLOCK)
    d_t.ungrab()
    subprocess.call(numpad_cmd, shell=True)


# status 1 = min bright
# status 2 = middle bright
# status 3 = max bright
def change_brightness(brightness):
    brightness = (brightness + 1) % len(BRIGHT_VAL)
    numpad_cmd = "i2ctransfer -f -y " + device_id + " w13@0x15 0x05 0x00 0x3d 0x03 0x06 0x00 0x07 0x00 0x0d 0x14 0x03 " + BRIGHT_VAL[brightness] + " 0xad"
    subprocess.call(numpad_cmd, shell=True)
    return brightness


# Process events while running #
while True:
    # If touchpad sends tap events, convert x/y position to numlock key and send it #
    for e in d_t.events():
        # ignore others events, except position and tracking release
        if not (
            e.matches(EV_ABS.ABS_MT_POSITION_X) or
            e.matches(EV_ABS.ABS_MT_POSITION_Y) or
            e.matches(EV_ABS.ABS_MT_TRACKING_ID)
        ):
            continue

        # Get x position #
        if e.matches(EV_ABS.ABS_MT_POSITION_X):
            x = e.value
            continue

        # Get y position #
        if e.matches(EV_ABS.ABS_MT_POSITION_Y):
            y = e.value
            continue

        if (e.matches(EV_ABS.ABS_MT_TRACKING_ID) and
            e.value == -1
        ):
            # Check if numlock was hit #
            if (model_layout.touchpad_num_lock == 1 and (x > 0.95 * maxx) and (y < 0.09 * maxy)):
                numlock = not numlock
                if numlock:
                    activate_numlock(brightness)
                else:
                    deactivate_numlock()

            # Check if calculator was hit #
            if (model_layout.touchpad_calculator == 1 and (x < 0.06 * maxx) and (y < 0.07 * maxy)):
                if numlock:
                    brightness = change_brightness(brightness)
                else:
                    send_key(calculator_key)
                continue

            # If touchpad mode, ignore #
            if not numlock:
                continue

            # Release finger after touchpad movement #
            try:
                col = math.floor(model_layout.cols * x / maxx)
                row = math.floor((model_layout.rows * y / maxy) - model_layout.top_offset)

                if row < 0:
                    continue

                value = model_layout.keys[row][col]

                # Send press key event #
                if value == EV_KEY.KEY_5:
                    press_key(EV_KEY.KEY_LEFTSHIFT)
                    send_key(percentage_key)
                    release_key(EV_KEY.KEY_LEFTSHIFT)
                else:
                    send_key(value)
            except OSError as e:
                pass

    for e in d_k.events():
        # Get num lock is pressed from internal or external keyboard
        if e.matches(EV_LED.LED_NUML):
            numlock = bool(e.value)
            continue
    sleep(0.1)

# Close file descriptors #
fd_k.close()
fd_t.close()
