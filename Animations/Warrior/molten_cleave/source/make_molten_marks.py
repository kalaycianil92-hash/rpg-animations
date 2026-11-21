#!/usr/bin/env python3
"""DRAFT hand marks and placement for the Molten Cleave strip (2026-11-20), like make_sunder_marks.py.

The fists were picked by eye on gridded 4x zoom crops of the cells (512 x 512 px). near = the fist in front (the "off" track, front), far = the one behind (the "main" track, behind); a = degrees,
0 = the blade points up, clockwise is positive. BOTH hands hold a sword (the user's rule: the prompts and the art are for two swords; the near hand can be switched to a shield in the page), 0.5 long.
THE BLADES FOLLOW THE SWEEP: the tip trails low behind him in frame 1 (the swords drag along the ground), swings down and forward under the fists in frame 2 (the tip scrapes along the ground in front),
whips up to point forward at the level blow (frame 3) and keeps turning counter-clockwise up and over: up and forward (4, 5), up and a little back at the top of the arc (6).
Frame 7 is the Thunderclap's recover pose (as in the Sunder Strike), frame 8 the idle's first frame, so its marks are the idle's. The user refines everything in the hand tool and the page's frame position tool.

Writes next to the strip (only when the file is missing; pass --marks / --placement to rewrite a draft: do not once the user's own files are filed):
  armored_molten_cleave_8frame_strip.hand-anchors.json
  armored_molten_cleave_8frame_strip.placement.json
"""
import json
import pathlib
import sys

D = pathlib.Path(__file__).resolve().parent.parent
STEM = "armored_molten_cleave_8frame_strip"
W, H = 512, 512

# frame: (near x, y, a), (far x, y, a)
FISTS = {
    1: ((200, 380, -122), (172, 365, -115)),    # wind-up: deep crouch, both fists at knee height behind the rear leg, the blades drag behind along the ground
    2: ((410, 322, 135), (402, 318, 142)),      # the sweep begins: fists at hip height in front, the blades point down and forward, the tips scrape the ground
    3: ((448, 250, 80), (440, 248, 72)),        # level: the blow lands (the hit frame): fists at chest height at the very front, the blades forward and a little up
    4: ((412, 168, 55), (404, 166, 48)),        # rising: fists at shoulder height, the blades point up and forward
    5: ((387, 117, 28), (378, 112, 20)),        # high: fists at head height, the blades point nearly up
    6: ((208, 63, -35), (231, 60, -25)),        # the top of the arc: both fists above and behind the head, the blades point up and a little back
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
    "animations": [{"name": "armored_molten_cleave_8frame", "frames": 8, "columns": 8, "fps": 14, "offItem": dict(sword, kind="other"), "tracks": {"main": main, "off": off}}]}]}

# timing: the base frame is 1000/14 = 71.4 ms; holds = extra ms per frame at 100% speed
TARGET_MS = [250, 60, 90, 70, 70, 130, 100, 70]
BASE = 1000 / 14
holds = [max(0, round(t - BASE)) for t in TARGET_MS]
place = {"format": "frame-placement/1", "animation": "attack", "file": STEM + ".png", "frames": 8, "fps": 14, "hitFrame": 3, "smooth": True, "holds": holds,
         "x": [0, 0.35, 1.0, 1.03, 1.05, 1.06, 1.06, 1.06], "y": [0, 0, 0, 0, 0, 0, 0, 0],
         "note": "Molten Cleave (2026-11-20). x: 0 = home, 1 = strike point (target centre minus 0.8 character widths); y: lift in frame widths (none: a grounded attack). holds[i] = extra ms for frame i+1 at 100% speed "
                 "(wind-up 250, the sweep begins 60, LEVEL BLOW 90 with the hit at 40% of it, rising 70, high 70, the top of the arc 130, recover 100). DRAFT path: tune it in the page's frame position tool."}

if "--marks" in sys.argv or not (D / (STEM + ".hand-anchors.json")).exists():
    (D / (STEM + ".hand-anchors.json")).write_text(json.dumps(marks, indent=1), encoding="utf-8", newline="\n"); print("wrote marks")
else:
    print("hand marks kept (pass --marks to rewrite the draft)")
if "--placement" in sys.argv or not (D / (STEM + ".placement.json")).exists():
    (D / (STEM + ".placement.json")).write_text(json.dumps(place, ensure_ascii=False), encoding="utf-8", newline="\n"); print("wrote placement")
else:
    print("placement kept (pass --placement to rewrite the draft)")
print("draft holds", holds, "total ms", sum(round(BASE) + h for h in holds))
