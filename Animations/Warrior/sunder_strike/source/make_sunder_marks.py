#!/usr/bin/env python3
"""DRAFT hand marks and placement for the Sunder Strike strip (2026-11-13), like make_guillotine_marks.py.

The fists were picked by eye on gridded 3x zoom crops of the cells (512 x 512 px). near = the fist in front (the "off" track, front), far = the one behind (the "main" track, behind); a = degrees,
0 = the blade points up, clockwise is positive. BOTH hands hold a sword (the user's rule: the prompts and the art are for two swords; the near hand can be switched to a shield in the page), 0.5 long.
Frame 8 is the idle's first frame, so its marks are the idle's. The user refines everything in the hand tool and the page's frame position tool.

Writes next to the strip (only when the file is missing; pass --marks / --placement to rewrite a draft: do not once the user's own files are filed):
  armored_sunder_strike_8frame_strip.hand-anchors.json
  armored_sunder_strike_8frame_strip.placement.json
"""
import json
import pathlib
import sys

D = pathlib.Path(__file__).resolve().parent.parent
STEM = "armored_sunder_strike_8frame_strip"
W, H = 512, 512

# frame: (near x, y, a), (far x, y, a)
FISTS = {
    1: ((152, 322, -130), (180, 322, -120)),    # wind-up: both fists behind the hip, the blades trail down and back
    2: ((157, 112, -135), (193, 102, -128)),    # raise: both fists above and behind the head, the blades point back and down (the user's Thunderclap apex)
    3: ((387, 120, 60), (410, 132, 50)),        # step-in: the swords come over the top, pointing up and forward
    4: ((447, 303, 120), (463, 297, 115)),      # CLEAVE A: both fists out in front, the blades along the arms, forward and down (the hit frame)
    5: ((432, 353, 140), (450, 347, 135)),      # cleave B: lower and steeper
    6: ((462, 397, 135), (485, 387, 130)),      # follow-through: low and far forward
    7: ((323, 243, -5), (375, 252, -35)),       # recover: back toward the guard
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
    "animations": [{"name": "armored_sunder_strike_8frame", "frames": 8, "columns": 8, "fps": 14, "offItem": dict(sword, kind="other"), "tracks": {"main": main, "off": off}}]}]}

# timing: the base frame is 1000/14 = 71.4 ms; holds = extra ms per frame at 100% speed
TARGET_MS = [120, 100, 70, 90, 100, 120, 100, 70]
BASE = 1000 / 14
holds = [max(0, round(t - BASE)) for t in TARGET_MS]
place = {"format": "frame-placement/1", "animation": "attack", "file": STEM + ".png", "frames": 8, "fps": 14, "hitFrame": 4, "smooth": True, "holds": holds,
         "x": [0, 0, 0.45, 1.0, 1.04, 1.07, 1.07, 1.07], "y": [0, 0, 0, 0, 0, 0, 0, 0],
         "note": "Sunder Strike (2026-11-13). x: 0 = home, 1 = strike point (target centre minus 0.8 character widths); y: lift in frame widths (none: a grounded attack). holds[i] = extra ms for frame i+1 at 100% speed "
                 "(wind-up 120, raise 100, step-in 70, CLEAVE A 90 with the hit at 40% of it, cleave B 100, follow-through 120, recover 100). DRAFT path: tune it in the page's frame position tool."}

if "--marks" in sys.argv or not (D / (STEM + ".hand-anchors.json")).exists():
    (D / (STEM + ".hand-anchors.json")).write_text(json.dumps(marks, indent=1), encoding="utf-8", newline="\n"); print("wrote marks")
else:
    print("hand marks kept (pass --marks to rewrite the draft)")
if "--placement" in sys.argv or not (D / (STEM + ".placement.json")).exists():
    (D / (STEM + ".placement.json")).write_text(json.dumps(place, ensure_ascii=False), encoding="utf-8", newline="\n"); print("wrote placement")
else:
    print("placement kept (pass --placement to rewrite the draft)")
print("draft holds", holds, "total ms", sum(round(BASE) + h for h in holds))
