#!/usr/bin/env python3

import importlib
import logging
import math
import os
import re
import subprocess
import sys
from fcntl import F_SETFL, fcntl
from time import sleep
from typing import Optional

import libevdev.const
from libevdev import EV_ABS, EV_KEY, EV_SYN, Device, InputEvent

# Setup logging
# LOG=DEBUG sudo -E ./asus_touchpad.py  # all messages
# LOG=ERROR sudo -E ./asus_touchpad.py  # only error messages
logging.basicConfig()
log = logging.getLogger('Pad')
log.setLevel(os.environ.get('LOG', 'INFO'))


# Select model from command line

model = 'm433ia'  # Model used in the derived script (with symbols)
if len(sys.argv) > 1:
    model = sys.argv[1]

model_layout = importlib.import_module('numpad_layouts.' + model)

# Figure out devices from devices file

touchpad: Optional[str] = None
keyboard: Optional[str] = None
device_id: Optional[str] = None

tries = model_layout.try_times

# Look into the devices file #
while tries > 0:

    keyboard_detected = 0
    touchpad_detected = 0

    with open('/proc/bus/input/devices', 'r') as f:
        lines = f.readlines()
        for line in lines:
            # Look for the touchpad #
            if touchpad_detected == 0 and "4F3:3101" in line and "Touchpad" in line:
                touchpad_detected = 1
                log.debug('Detect touchpad from %s', line.strip())

            if touchpad_detected == 1:
                if "S: " in line:
                    # search device id
                    device_id = re.sub(r".*i2c-(\d+)/.*$",
                                       r'\1', line).replace("\n", "")
                    log.debug('Set touchpad device id %s from %s',
                              device_id, line.strip())

                if "H: " in line:
                    touchpad = line.split("event")[1]
                    touchpad = touchpad.split(" ")[0]
                    touchpad_detected = 2
                    log.debug('Set touchpad id %s from %s',
                              touchpad, line.strip())

            # Look for the keyboard (numlock) # AT Translated Set OR Asus Keyboard
            if keyboard_detected == 0 and ("Name=\"AT Translated Set 2 keyboard" in line or "Name=\"Asus Keyboard" in line):
                keyboard_detected = 1
                log.debug('Detect keyboard from %s', line.strip())

            if keyboard_detected == 1:
                if "H: " in line:
                    keyboard = line.split("event")[1]
                    keyboard = keyboard.split(" ")[0]
                    keyboard_detected = 2
                    log.debug('Set keyboard %s from %s',
                              keyboard, line.strip())

            # Stop looking if both have been found #
            if keyboard_detected == 2 and touchpad_detected == 2:
                break

    if keyboard_detected != 2 or touchpad_detected != 2:
        tries -= 1
        if tries == 0:
            if keyboard_detected != 2:
                log.error("Can't find keyboard (code: %s)", keyboard_detected)
            if touchpad_detected != 2:
                log.error("Can't find touchpad (code: %s)", touchpad_detected)
            if touchpad_detected == 2 and not device_id.isnumeric():
                log.error("Can't find device id")
            sys.exit(1)
    else:
        break

    sleep(model_layout.try_sleep)


# Start monitoring the touchpad

try:
    fd_t = open('/dev/input/event' + str(touchpad), 'rb')
except PermissionError:
    log.error("Can't open /dev/input/event" + str(touchpad))
    exit(1)
fcntl(fd_t, F_SETFL, os.O_NONBLOCK)
d_t = Device(fd_t)


# Retrieve touchpad dimensions #

ai = d_t.absinfo[EV_ABS.ABS_X]
(minx, maxx) = (ai.minimum, ai.maximum)
ai = d_t.absinfo[EV_ABS.ABS_Y]
(miny, maxy) = (ai.minimum, ai.maximum)
log.debug('Touchpad min-max: x %d-%d, y %d-%d', minx, maxx, miny, maxy)


# Start monitoring the keyboard (numlock)

fd_k = open('/dev/input/event' + str(keyboard), 'rb')
fcntl(fd_k, F_SETFL, os.O_NONBLOCK)
d_k = Device(fd_k)


# Create a new keyboard device to send numpad events
# KEY_5:6
# KEY_APOSTROPHE:40
# [...]
percentage_key = EV_KEY.KEY_5
calculator_key = EV_KEY.KEY_CALC

if len(sys.argv) > 2:
    percentage_key = EV_KEY.codes[int(sys.argv[2])]

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

udev = dev.create_uinput_device()


# Brightness 31: Low, 24: Half, 1: Full

BRIGHT_VAL = [hex(val) for val in [31, 24, 1]]


def activate_numlock(brightness):
    numpad_cmd = "i2ctransfer -f -y " + device_id + \
        " w13@0x15 0x05 0x00 0x3d 0x03 0x06 0x00 0x07 0x00 0x0d 0x14 0x03 " + \
        BRIGHT_VAL[brightness] + " 0xad"
    events = [
        InputEvent(EV_KEY.KEY_NUMLOCK, 1),
        InputEvent(EV_SYN.SYN_REPORT, 0)
    ]
    udev.send_events(events)
    d_t.grab()
    subprocess.call(numpad_cmd, shell=True)


def deactivate_numlock():
    numpad_cmd = "i2ctransfer -f -y " + device_id + \
        " w13@0x15 0x05 0x00 0x3d 0x03 0x06 0x00 0x07 0x00 0x0d 0x14 0x03 0x00 0xad"
    events = [
        InputEvent(EV_KEY.KEY_NUMLOCK, 0),
        InputEvent(EV_SYN.SYN_REPORT, 0)
    ]
    udev.send_events(events)
    d_t.ungrab()
    subprocess.call(numpad_cmd, shell=True)


def launch_calculator():
    try:
        events = [
            InputEvent(calculator_key, 1),
            InputEvent(EV_SYN.SYN_REPORT, 0),
            InputEvent(calculator_key, 0),
            InputEvent(EV_SYN.SYN_REPORT, 0)
        ]
        udev.send_events(events)
    except OSError as e:
        pass


# status 1 = min bright
# status 2 = middle bright
# status 3 = max bright
def change_brightness(brightness):
    brightness = (brightness + 1) % len(BRIGHT_VAL)
    numpad_cmd = "i2ctransfer -f -y " + device_id + \
        " w13@0x15 0x05 0x00 0x3d 0x03 0x06 0x00 0x07 0x00 0x0d 0x14 0x03 " + \
        BRIGHT_VAL[brightness] + " 0xad"
    subprocess.call(numpad_cmd, shell=True)
    return brightness


# Run - process and act on events

numlock: bool = False
pos_x: int = 0
pos_y: int = 0
button_pressed: libevdev.const = None
brightness: int = 0

while True:
    # If touchpad sends tap events, convert x/y position to numlock key and send it #
    for e in d_t.events():

        # ignore others events, except position and finger events
        if not (
            e.matches(EV_ABS.ABS_MT_POSITION_X) or
            e.matches(EV_ABS.ABS_MT_POSITION_Y) or
            e.matches(EV_KEY.BTN_TOOL_FINGER)
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

        # Else event is tap: e.matches(EV_KEY.BTN_TOOL_FINGER) #

        # If end of tap, send release key event #
        if e.value == 0:
            log.debug('finger up at x %d y %d', x, y)

            if button_pressed:
                log.debug('send key up event %s', button_pressed)
                events = [
                    InputEvent(EV_KEY.KEY_LEFTSHIFT, 0),
                    InputEvent(button_pressed, 0),
                    InputEvent(EV_SYN.SYN_REPORT, 0)
                ]
                try:
                    udev.send_events(events)
                    button_pressed = None
                except OSError as err:
                    log.error("Cannot send release event, %s", err)
                    pass

        elif e.value == 1 and not button_pressed:
            # Start of tap #
            log.debug('finger down at x %d y %d', x, y)

            # Check if numlock was hit #
            if (x > 0.95 * maxx) and (y < 0.09 * maxy):
                numlock = not numlock
                if numlock:
                    activate_numlock(brightness)
                else:
                    deactivate_numlock()
                continue

            # Check if calculator was hit #
            elif (x < 0.06 * maxx) and (y < 0.07 * maxy):
                if numlock:
                    brightness = change_brightness(brightness)
                else:
                    launch_calculator()
                continue

            # If touchpad mode, ignore #
            if not numlock:
                continue

            # else numpad mode is activated
            col = math.floor(model_layout.cols * x / (maxx+1))
            row = math.floor((model_layout.rows * y / maxy) -
                             model_layout.top_offset)
            # Ignore top_offset region #
            if row < 0:
                continue
            try:
                button_pressed = model_layout.keys[row][col]
            except IndexError:
                # skip invalid row and col values
                log.debug(
                    'Unhandled col/row %d/%d for position %d-%d', col, row, x, y)
                continue

            if button_pressed == EV_KEY.KEY_5:
                button_pressed = percentage_key

            # Send press key event #
            log.debug('send press key event %s', button_pressed)

            if button_pressed == percentage_key:
                events = [
                    InputEvent(EV_KEY.KEY_LEFTSHIFT, 1),
                    InputEvent(button_pressed, 1),
                    InputEvent(EV_SYN.SYN_REPORT, 0)
                ]
            else:
                events = [
                    InputEvent(button_pressed, 1),
                    InputEvent(EV_SYN.SYN_REPORT, 0)
                ]

            try:
                udev.send_events(events)
            except OSError as err:
                log.warning("Cannot send press event, %s", err)
    sleep(0.1)
