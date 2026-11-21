#!/usr/bin/env python3
"""DRAFT hand marks and placement for the Execute strip (2026-11-20), like make_glacial_marks.py.

The fists were picked by eye on gridded crops of the cells (512 x 512 px). near = the fist in front (the "off" track, front), far = the one behind (the "main" track, behind); a = degrees,
0 = the blade points up, clockwise is positive (90 = straight at the enemy, 180 = straight down). BOTH hands hold a sword (the user's rule), 0.5 long (the grip is at 81% of its length: the tip is 207 px from the fist), and the
shield switch is the page's. THE BLADES: planted straight down in the floor in the vigil (frame 1: 180 / 180, the marks sit on the lower edge of the fists so that the tips reach the floor), forward and down over the rear shoulder
in the draw (2: 115 / 108), forward and down over the front shoulder in the stride (3: 112 / 105), buried in the target along the arms in the impale (4: 104 / 101), still pointing at the target in the wrench (5: 125 / 120),
hanging low with the tips resting on the floor in standing over (6: 140 / 134). Frame 7 is the Thunderclap's recover pose (as in the Sunder Strike, Molten Cleave and Glacial Blade), frame 8 the idle's first frame, so its
marks are the idle's. The user refines everything in the hand tool and the page's frame position tool.

Writes next to the strip (only when the file is missing; pass --marks / --placement to rewrite a draft: do not once the user's own files are filed):
  armored_execute_8frame_strip.hand-anchors.json
  armored_execute_8frame_strip.placement.json
"""
import json
import pathlib
import sys

D = pathlib.Path(__file__).resolve().parent.parent
STEM = "armored_execute_8frame_strip"
W, H = 512, 512

# frame: (near x, y, a), (far x, y, a)
FISTS = {
    1: ((326, 252, 180), (344, 248, 180)),      # THE VIGIL: both fists at chest height resting on the pommels, the blades planted straight down in the floor in front of him
    2: ((192, 166, 115), (210, 160, 108)),      # THE DRAW: both fists beside and above the rear shoulder, the blades point forward and down over his head and shoulder
    3: ((414, 202, 112), (428, 196, 105)),      # THE STRIDE: the fists ahead of and above the front shoulder, the blades point forward and down at the target
    4: ((466, 294, 104), (478, 291, 101)),      # THE IMPALE (the hit frame): the arms fully extended forward and a little down, the blades buried in the target
    5: ((330, 272, 125), (345, 266, 120)),      # THE WRENCH: the fists pulled in at the belly, the blades still point at the target
    6: ((322, 312, 140), (338, 308, 134)),      # STANDING OVER: the arms hang, the blades point forward and down, the tips rest on the floor
    7: ((323, 243, -5), (375, 252, -35)),       # recover: back toward the guard (the same pose as the Sunder Strike's frame 7)
}
IDLE_FAR = (0.781, 0.350, -42)                  # the idle's first frame (Animations/Warrior/idle marks), same 512 x 512 cell
IDLE_NEAR = (0.545, 0.381, 0)


def mark(x, y, a, front):
    return {"x": round(x, 3), "y": round(y, 3), "a": a, "front": front, "hide": False, "w": 1}


main, off = [], []
for f in range(1, 9):
    if f == 8:
        main.append(mark(IDLE_FAR[0], IDLE_FAR[1], IDLE_FAR[2], False)); off.append(mark(IDLE_NEAR[0], IDLE_NEAR[1], IDLE_NEAR[2], True))
        continue
    near, far = FISTS[f]
    main.append(mark(far[0] / W, far[1] / H, far[2], False))
    off.append(mark(near[0] / W, near[1] / H, near[2], True))

sword = {"length": 0.5, "pivot": 0.81, "overlay": True, "picture": "sword"}
marks = {"format": "hand-anchors/3", "characters": [{
    "name": "Warrior", "fist": 0.09, "items": {"main": dict(sword), "off": dict(sword)},
    "animations": [{"name": "armored_execute_8frame", "frames": 8, "columns": 8, "fps": 14, "offItem": dict(sword, kind="other"), "tracks": {"main": main, "off": off}}]}]}

# timing: the base frame is 1000/14 = 71.4 ms; holds = extra ms per frame at 100% speed
TARGET_MS = [600, 220, 60, 250, 120, 200, 100, 70]
BASE = 1000 / 14
holds = [max(0, round(t - BASE)) for t in TARGET_MS]
place = {"format": "frame-placement/1", "animation": "attack", "file": STEM + ".png", "frames": 8, "fps": 14, "hitFrame": 4, "smooth": True, "holds": holds,
         "x": [0, -0.03, 0.5, 1.0, 0.98, 0.96, 0.96, 0.96], "y": [0, 0, 0, 0, 0, 0, 0, 0],
         "note": "Execute (2026-11-20). x: 0 = home, 1 = strike point (target centre minus 0.8 character widths); y: lift in frame widths (none: a grounded attack). holds[i] = extra ms for frame i+1 at 100% speed "
                 "(the vigil 600, the draw 220 with a small pull back, the stride 60, THE IMPALE 250 with the hit at 40% of it and the rest a HOLD, the wrench 120, standing over 200, recover 100). DRAFT path: tune it in the page's frame position tool."}

if "--marks" in sys.argv or not (D / (STEM + ".hand-anchors.json")).exists():
    (D / (STEM + ".hand-anchors.json")).write_text(json.dumps(marks, indent=1), encoding="utf-8", newline="\n"); print("wrote marks")
else:
    print("hand marks kept (pass --marks to rewrite the draft)")
if "--placement" in sys.argv or not (D / (STEM + ".placement.json")).exists():
    (D / (STEM + ".placement.json")).write_text(json.dumps(place, ensure_ascii=False), encoding="utf-8", newline="\n"); print("wrote placement")
else:
    print("placement kept (pass --placement to rewrite the draft)")
print("draft holds", holds, "total ms", sum(round(BASE) + h for h in holds))
