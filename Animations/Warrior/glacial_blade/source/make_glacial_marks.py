#!/usr/bin/env python3
"""DRAFT hand marks and placement for the Glacial Blade strip (2026-11-20), like make_molten_marks.py.

The fists were picked by eye on gridded crops of the cells (512 x 512 px). near = the fist in front (the "off" track, front), far = the one behind (the "main" track, behind); a = degrees,
0 = the blade points up, clockwise is positive (90 = straight at the enemy). BOTH hands hold a sword (the user's rule), 0.5 long, and the shield switch is the page's. THE BLADES POINT AT THE ENEMY ALONG THE ARMS (a thrust):
a spear couched at the belt in the coil and the gather (frames 1, 2: 82 / 76), a little flatter in the drive (3), level at the bash (4: 92 / 90), heaving up 30 degrees in the shove (5: 62 / 58), back to the guard in the withdrawal (6).
Frames 1, 2 and 6 are the same drawing (the sheet's panel 6: its panels 1 and 2 were never usable), each frame has its own marks. Frame 7 is the Thunderclap's recover pose (as in the Sunder Strike and the Molten Cleave),
frame 8 the idle's first frame, so its marks are the idle's. The user refines everything in the hand tool and the page's frame position tool.

Writes next to the strip (only when the file is missing; pass --marks / --placement to rewrite a draft: do not once the user's own files are filed):
  armored_glacial_blade_8frame_strip.hand-anchors.json
  armored_glacial_blade_8frame_strip.placement.json
"""
import json
import pathlib
import sys

D = pathlib.Path(__file__).resolve().parent.parent
STEM = "armored_glacial_blade_8frame_strip"
W, H = 512, 512

# frame: (near x, y, a), (far x, y, a)
FISTS = {
    1: ((300, 303, 82), (322, 297, 76)),        # the coil: a spear couched at the belt, the blades point at the enemy and a little up
    2: ((300, 303, 84), (322, 297, 78)),        # the gather: the same drawing, the path pulls him back a little
    3: ((322, 300, 86), (338, 295, 80)),        # the drive: the fists just ahead of the belt, the blades point forward
    4: ((450, 290, 92), (462, 288, 90)),        # THE BASH (the hit frame): both arms fully extended, level, the blades straight at the target
    5: ((484, 235, 62), (497, 232, 58)),        # the shove: the arms heave up about 30 degrees, the blades follow
    6: ((300, 303, 78), (322, 297, 72)),        # the withdrawal: back in the guard, the blades a little higher
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
    "animations": [{"name": "armored_glacial_blade_8frame", "frames": 8, "columns": 8, "fps": 14, "offItem": dict(sword, kind="other"), "tracks": {"main": main, "off": off}}]}]}

# timing: the base frame is 1000/14 = 71.4 ms; holds = extra ms per frame at 100% speed
TARGET_MS = [200, 130, 60, 100, 130, 100, 100, 70]
BASE = 1000 / 14
holds = [max(0, round(t - BASE)) for t in TARGET_MS]
place = {"format": "frame-placement/1", "animation": "attack", "file": STEM + ".png", "frames": 8, "fps": 14, "hitFrame": 4, "smooth": True, "holds": holds,
         "x": [0, -0.04, 0.45, 1.0, 1.04, 1.06, 1.06, 1.06], "y": [0, 0, 0, 0, 0, 0, 0, 0],
         "note": "Glacial Blade (2026-11-20). x: 0 = home, 1 = strike point (target centre minus 0.8 character widths); y: lift in frame widths (none: a grounded attack). holds[i] = extra ms for frame i+1 at 100% speed "
                 "(coil 200, gather 130 with a small pull back, the drive 60, THE BASH 100 with the hit at 40% of it, the shove 130, the withdrawal 100, recover 100). DRAFT path: tune it in the page's frame position tool."}

if "--marks" in sys.argv or not (D / (STEM + ".hand-anchors.json")).exists():
    (D / (STEM + ".hand-anchors.json")).write_text(json.dumps(marks, indent=1), encoding="utf-8", newline="\n"); print("wrote marks")
else:
    print("hand marks kept (pass --marks to rewrite the draft)")
if "--placement" in sys.argv or not (D / (STEM + ".placement.json")).exists():
    (D / (STEM + ".placement.json")).write_text(json.dumps(place, ensure_ascii=False), encoding="utf-8", newline="\n"); print("wrote placement")
else:
    print("placement kept (pass --placement to rewrite the draft)")
print("draft holds", holds, "total ms", sum(round(BASE) + h for h in holds))
