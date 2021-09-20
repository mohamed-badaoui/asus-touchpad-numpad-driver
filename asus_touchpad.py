#!/usr/bin/python3

import importlib
import math
import re
import subprocess
import os
import sys
from fcntl import F_SETFL, fcntl
from os import O_NONBLOCK
from subprocess import PIPE, Popen
from time import sleep
import logging

from typing import Optional

import libevdev.const
from libevdev import EV_ABS, EV_KEY, EV_LED, EV_SYN, Device, InputEvent

# Setup logging
# LOG=DEBUG sudo -E ./asus-touchpad-numpad-driver  # all messages
# LOG=ERROR sudo -E ./asus-touchpad-numpad-driver  # only error messages
logging.basicConfig()
log = logging.getLogger('Pad')
log.setLevel(os.environ.get('LOG', 'INFO'))


# Select model from command line

model = 'm433ia' # Model used in the derived script (with symbols)

# KEY_5:6
# KEY_APOSTROPHE:40
# [...]
percentage_key = EV_KEY.KEY_5
calculator_key = EV_KEY.KEY_CALC

if len(sys.argv) > 1:
    model = sys.argv[1]
model_layout = importlib.import_module('numpad_layouts.'+ model)

if len(sys.argv) > 2:
    percentage_key = EV_KEY.codes[int(sys.argv[2])]



# Figure out devices from devices file

touchpad: Optional[str] = None
keyboard: Optional[str] = None
device_id: Optional[str] = None

for one_try in range(model_layout.try_times):

    with open('/proc/bus/input/devices', 'r') as f:
        # iterate over lines, once (through all for loops)
        lines = iter(f.readlines())
        for line in lines:
            if line.startswith('N:'):

                # Look for the touchpad #
                if not touchpad and ("Name=\"ASUE" in line or "Name=\"ELAN" in line) and "Touchpad" in line:
                    log.info('Detect touchpad from %s', line.strip())

                    for line in lines:
                        if line.startswith('S:'):
                            # search device id
                            device_id=re.sub(r".*i2c-(\d+)/.*$", r'\1', line).replace("\n", "")
                            log.info('Set touchpad device id %s from %s', device_id, line.strip())
                        elif line.startswith('H:'):
                            # touchpad device
                            touchpad = line.split("event")[1].split(" ")[0]
                            log.info('Set touchpad id %s from %s', touchpad, line.strip())
                        elif not line.strip():
                            break

                # Look for the keyboard (numlock) # AT Translated Set OR Asus Keyboard
                elif not keyboard and ("Name=\"AT Translated Set 2 keyboard" in line or "Name=\"Asus Keyboard" in line):
                    log.info('Detect keyboard from %s', line.strip())

                    for line in lines:
                        if line.startswith('H:'):
                            # keyboard device
                            keyboard = line.split("event")[1].split(" ")[0]
                            log.info('Set keyboard %s from %s', keyboard, line.strip())
                            break
                        elif not line.strip():
                            break

        if keyboard is not None and touchpad is not None and device_id is not None:
            break

    sleep(0.1)
else:
    # Couldn't properly detect keyboard or touchpad
    if keyboard is None:
        log.error("Can't find keyboard")
    if touchpad is None:
        log.error("Can't find touchpad")
    if device_id is None:
        log.error("Can't find device id")
    elif not device_id.isnumeric():
        log.error("Unknown touchpad device id %s", device_id)
    sys.exit(1)


# Start monitoring the touchpad

fd_t = open('/dev/input/event' + str(touchpad), 'rb')
fcntl(fd_t, F_SETFL, O_NONBLOCK)
d_t = Device(fd_t)


# Retrieve touchpad dimensions #

ai = d_t.absinfo[EV_ABS.ABS_X]
(minx, maxx) = (ai.minimum, ai.maximum)
ai = d_t.absinfo[EV_ABS.ABS_Y]
(miny, maxy) = (ai.minimum, ai.maximum)
log.debug('Touchpad min-max: x %d-%d, y %d-%d', minx, maxx, miny, maxy)


# Start monitoring the keyboard (numlock)

fd_k = open('/dev/input/event' + str(keyboard), 'rb')
fcntl(fd_k, F_SETFL, O_NONBLOCK)
d_k = Device(fd_k)


# Create a new keyboard device to send numpad events

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
    numpad_cmd = "i2ctransfer -f -y " + device_id + " w13@0x15 0x05 0x00 0x3d 0x03 0x06 0x00 0x07 0x00 0x0d 0x14 0x03 " + BRIGHT_VAL[brightness] + " 0xad"
    events = [
        InputEvent(EV_KEY.KEY_NUMLOCK, 1),
        InputEvent(EV_SYN.SYN_REPORT, 0)
    ]
    udev.send_events(events)
    d_t.grab()
    subprocess.call(numpad_cmd, shell=True)


def deactivate_numlock():
    numpad_cmd = "i2ctransfer -f -y " + device_id + " w13@0x15 0x05 0x00 0x3d 0x03 0x06 0x00 0x07 0x00 0x0d 0x14 0x03 0x00 0xad"
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
    numpad_cmd = "i2ctransfer -f -y " + device_id + " w13@0x15 0x05 0x00 0x3d 0x03 0x06 0x00 0x07 0x00 0x0d 0x14 0x03 " + BRIGHT_VAL[brightness] + " 0xad"
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

        # Get x position #
        if e.matches(EV_ABS.ABS_MT_POSITION_X):
            x = e.value

        # Get y position #
        elif e.matches(EV_ABS.ABS_MT_POSITION_Y):
            y = e.value

        # If tap #
        elif e.matches(EV_KEY.BTN_TOOL_FINGER):

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

                # Check if caclulator was hit #
                elif (x < 0.06 * maxx) and (y < 0.07 * maxy):
                    if numlock:
                        brightness = change_brightness(brightness)
                    else:
                        launch_calculator()
                    continue

                # If touchpad mode, check key #
                elif numlock:

                    col = math.floor(model_layout.cols * x / (maxx+1) )
                    row = math.floor((model_layout.rows * y / maxy) - model_layout.top_offset)
                    try:
                        button_pressed = model_layout.keys[row][col]
                    except IndexError:
                        # skip invalid row and col values
                        log.debug('Unhandled col/row %d/%d for position %d-%d', col, row, x, y)
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
