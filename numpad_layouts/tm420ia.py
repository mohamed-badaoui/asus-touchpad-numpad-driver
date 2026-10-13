"""
Keypad layout configuration for ASUS VivoBook Flip 14 (TM420IA / TP420IA).
5 columns x 4 rows layout with adjusted top offset for the convertible chassis.
"""
from libevdev import EV_KEY

# Number of tries to identify the interface number
try_times = 5
try_sleep = 0.1

cols = 5
rows = 4

# Offsets for VivoBook Flip 14 (touchpad physical size: 105 x 60 mm)
# top_offset includes a generous buffer for the fingertip to avoid accidentally
# triggering the '7' key when tapping the brightness control icon in the top-left area.
top_offset = 0.35      # 8 mm top margin + 13 mm fingertip buffer = 21 mm (21/60 = 0.35)
bottom_offset = 0.05   # 3 mm bottom margin (3/60 = 0.05)
left_offset = 0.028    # 3 mm left margin (3/105 = 0.028)
right_offset = 0.028   # 3 mm right margin (3/105 = 0.028)

keys = [
    [EV_KEY.KEY_KP7, EV_KEY.KEY_KP8, EV_KEY.KEY_KP9, EV_KEY.KEY_KPSLASH, EV_KEY.KEY_BACKSPACE],
    [EV_KEY.KEY_KP4, EV_KEY.KEY_KP5, EV_KEY.KEY_KP6, EV_KEY.KEY_KPASTERISK, EV_KEY.KEY_BACKSPACE],
    [EV_KEY.KEY_KP1, EV_KEY.KEY_KP2, EV_KEY.KEY_KP3, EV_KEY.KEY_KPMINUS, EV_KEY.KEY_KPSLASH],
    [EV_KEY.KEY_KP0, EV_KEY.KEY_KPDOT, EV_KEY.KEY_KPENTER, EV_KEY.KEY_KPPLUS, EV_KEY.KEY_KPEQUAL]
]
