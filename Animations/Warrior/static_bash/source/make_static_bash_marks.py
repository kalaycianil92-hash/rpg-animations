#!/usr/bin/env python3
"""DRAFT hand marks and placement for the 21-frame Static Bash strip (2026-11-14), like make_sunder_marks.py.

Frames 1-6 are the IDLE's frames 1-6 and frames 7-15 the RUN strip's frames 1 2 3 4 5 1 2 3 4: their marks are COPIED from the Warrior's idle marks and from the user's run marks. Frames 16-19 (skid, the swords
raised, slam, heavy slam) are drafts: the fists were picked by eye on gridded 3-4x crops (512 x 512 cells), the blade angles are mine (0 = the blade points up, clockwise positive; near = the "off" track, in
front; far = the "main" track, behind); the skid, slam and heavy slam fists were picked on the earlier heel-aligned strip and are moved by the shift of each frame's left edge (the strike frames are aligned by
the FRONT TOE now). Frame 20 is the recover (the Sunder Strike's frame 7 moved by its shift), frame 21 the idle's first frame. Both hands hold a sword, 0.5 long. The user refines everything in the hand
tool and the frame position tool.

Writes next to the strip, only when the file is missing (pass --marks / --placement to rewrite a draft: do not once the user's own files are filed).
"""
import json
import pathlib
import sys
import numpy as np
from PIL import Image

D = pathlib.Path(__file__).resolve().parent.parent
ROOT = D.parents[2]
STEM = "armored_static_bash_21frame_strip"
W, H = 512, 512


def tracks(folder, name):
    return json.loads((ROOT / "Animations" / "Warrior" / folder / name).read_text(encoding="utf-8"))["characters"][0]["animations"][0]["tracks"]


idle = tracks("idle", "armored_idle_strip.hand-anchors.json")
run = tracks("run", "armored_run_5frame_strip.hand-anchors.json")
sun = tracks("sunder_strike", "armored_sunder_strike_8frame_strip.hand-anchors.json")
strip = np.array(Image.open(D / (STEM + ".png")).convert("RGBA"))


def left_edge(frame):                                     # the left-most opaque pixel of a frame (1-based) of the strip
    a = strip[:, (frame - 1) * W:frame * W, 3] > 128
    return int(np.where(a.any(0))[0].min())


def mark(x, y, a, front):
    return {"x": round(x, 3), "y": round(y, 3), "a": a, "front": front, "hide": False, "w": 1}


# frame: (near x, y, a), (far x, y, a) in the cell of the NEW strip (for 16, 18, 19: picked on the old heel-aligned cells, shifted below)
FISTS = {
    16: ((393, 322, 75), (418, 318, 65)),        # skid: the fists together at belt height in front, the swords up and forward
    17: ((276, 111, -12), (317, 117, 12)),       # the swords RAISED: both fists above the head, the blades up in a small V
    18: ((477, 295, 110), (493, 287, 105)),      # SLAM (the hit): both arms out in front, a little down, the blades along the arms
    19: ((463, 360, 135), (480, 350, 130)),      # the heavy slam: steeper
}
SHIFT = {16: left_edge(16) - 128, 18: left_edge(18) - 128, 19: left_edge(19) - 128}
print("shifts of the heel-picked frames:", SHIFT)
main, off = [], []
for f in range(1, 22):
    if f <= 6:
        main.append(dict(idle["main"][f - 1])); off.append(dict(idle["off"][f - 1]))
    elif f <= 15:
        k = [0, 1, 2, 3, 4, 0, 1, 2, 3][f - 7]
        main.append(dict(run["main"][k])); off.append(dict(run["off"][k]))
    elif f in FISTS:
        near, far = FISTS[f]
        dx = SHIFT.get(f, 0)
        main.append(mark((far[0] + dx) / W, far[1] / H, far[2], False)); off.append(mark((near[0] + dx) / W, near[1] / H, near[2], True))
    elif f == 20:
        dx = (left_edge(20) - 128) / W
        m, o = dict(sun["main"][6]), dict(sun["off"][6]); m["x"] = round(m["x"] + dx, 3); o["x"] = round(o["x"] + dx, 3)
        main.append(m); off.append(o)
    else:
        main.append(dict(idle["main"][0])); off.append(dict(idle["off"][0]))

sword = {"length": 0.5, "pivot": 0.81, "overlay": True, "picture": "sword"}
marks = {"format": "hand-anchors/3", "characters": [{
    "name": "Warrior", "fist": 0.09, "items": {"main": dict(sword), "off": dict(sword)},
    "animations": [{"name": "armored_static_bash_21frame", "frames": 21, "columns": 21, "fps": 14, "offItem": dict(sword, kind="other"), "tracks": {"main": main, "off": off}}]}]}

# timing: base frame 1000/14 = 71.4 ms. The idle infusion 100 ms a frame, the run 70, the skid 110, the swords raised 260 (the animation slows down), the slam 100, the heavy slam 130, the recover 100
# 2026-11-23 (the user): the run (frames 7-15) 25% faster (70 -> 57 ms), the skid, the raised swords and the slam (16-18) 25% slower (110, 260, 100 -> 138, 325, 125); the base frame is 1000/17.5 = 57 ms
FPS = 17.5
TARGET_MS = [100] * 6 + [57] * 9 + [138, 325, 125, 130, 100, 70]
BASE = 1000 / FPS
holds = [max(0, round(t - BASE)) for t in TARGET_MS]
x = [0] * 6 + [round(0.94 * k / 8, 4) for k in range(9)] + [1.0, 1.01, 1.02, 1.05, 1.05, 1.05]
place = {"format": "frame-placement/1", "animation": "attack", "file": STEM + ".png", "frames": 21, "fps": FPS, "hitFrame": 18, "smooth": True, "holds": holds,
         "x": x, "y": [0] * 21,
         "note": "Static Bash (2026-11-14). x: 0 = home, 1 = strike point (target centre minus 0.8 character widths); y: none (grounded). Frames 1-6: he stands in the idle while the swords are infused with lightning "
                 "(0.6 s), 7-15 the run strip at full speed (0.63 s), 16 the skid and 17 the swords raised (the animation slows down, the lightning intensifies), 18 the SLAM (the hit, at 40% of it), 19 the heavy slam, "
                 "20 the recover, 21 the idle. holds[i] = extra ms for frame i+1 at 100% speed. DRAFT path: tune it in the page's frame position tool."}

if "--marks" in sys.argv or not (D / (STEM + ".hand-anchors.json")).exists():
    (D / (STEM + ".hand-anchors.json")).write_text(json.dumps(marks, indent=1), encoding="utf-8", newline="\n"); print("wrote marks")
else:
    print("hand marks kept (pass --marks to rewrite the draft)")
if "--placement" in sys.argv or not (D / (STEM + ".placement.json")).exists():
    (D / (STEM + ".placement.json")).write_text(json.dumps(place, ensure_ascii=False), encoding="utf-8", newline="\n"); print("wrote placement")
else:
    print("placement kept (pass --placement to rewrite the draft)")
print("draft holds", holds, "total ms", sum(round(BASE) + h for h in holds))
