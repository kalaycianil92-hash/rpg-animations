#!/usr/bin/env python3
"""Builds the Cleric's RADIANT SMITE strip (2026-11-21).

  python Animations/Cleric/radiant_smite/source/make_radiant_strip.py [--heel-a 173] [--heel-b 126] [--out PATH]

The user's ChatGPT sheet (cleric_radiant_smite_sheet_3x2.png, 1536 x 1024, 3 x 2): panel 3 holds the weapon arm straight up and its fist is 455 px above the floor in the sheet (489 px at his
size), more than a 512 px cell holds with the ground line at y = 470, so the strip is 512 wide and 640 TALL with the ground line at y = 598 (the same as the Warrior's Thunderclap Guillotine, the Rogue's dodge
frames etc.: the extra height is headroom). The keypose cutter only makes square cells, so:
 1. slice_keypose_sheet.py cuts 640 x 640 cells (ground y 598), heel mode: the REAR heel of every frame is pinned (the rear foot stays planted while the front boot steps in, like the Warrior's Sunder
    Strike), one shared scale from the median height (his idle is 408 px);
 2. each cell is cropped to 512 wide: cell x 64..576, so the heel lands on the pin in the finished frame. TWO pins (the sheet is cut twice): the stance frames 1, 2, 3 and 6 use --heel-a 173 (his idle's heel, so the
    attack starts and ends exactly where the idle stands: no pop), the two lunge frames 4 and 5 use --heel-b 126 (the far fist is 378 px ahead of the heel in panel 5, a heel at 173 would cut it off at the
    right edge; at 126 it ends at x 504). The rear foot therefore jumps back 47 px between frames 3 and 4 (hidden by the step-in, the path moves him forward at the same time) and forward again between 5 and 6
    (the rear foot brought up to the front foot, which hardly moves);
 3. the idle's first frame is pasted as frame 7 (padded to 640 tall: its ground line 470 goes to 598);
 4. the placement (fps 14, hitFrame 4, holds, the draft path) is written.
Then: even_heads.py --char cleric --ref Animations/Cleric/idle/mailed_idle_strip.png <the strip>   (cell width 512; the head is the same measure on any cell height).
"""
import argparse, json, os, subprocess, sys
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
SK = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(SK, "..", "..", ".."))
TOOLS = os.path.join(ROOT, "source", "tools")
ap = argparse.ArgumentParser()
ap.add_argument("--heel-a", type=float, default=173, help="rear heel of the stance frames 1, 2, 3, 6 (his idle's)")
ap.add_argument("--heel-b", type=float, default=106, help="rear heel of the lunge frames 4, 5")
LUNGE = (3, 4)   # 0-based indexes of the lunge frames
ap.add_argument("--out", default=os.path.join(SK, "mailed_radiant_smite_7frame_strip.png"))
a = ap.parse_args()

SHEET = os.path.join(HERE, "cleric_radiant_smite_sheet_3x2.png")
IDLE = os.path.join(ROOT, "Animations", "Cleric", "idle", "mailed_idle_strip.png")
TMP = os.path.join(HERE, "_cut640.png")
GROUND, CELL_H, CELL_W, PAD = 598, 640, 512, 64

# 1. cut at 640 x 640, twice (one rear-heel pin for the stance frames, one for the lunge frames)
def cut(heel):
    subprocess.check_call([sys.executable, os.path.join(TOOLS, "slice_keypose_sheet.py"), SHEET, TMP, "--cols", "3", "--rows", "2", "--height", "408", "--scale-from", "median",
                           "--modes", "heel", "--heel-x", str(heel + PAD), "--frame", "640", "--ground", str(GROUND)], cwd=TOOLS)
    im = Image.open(TMP).convert("RGBA")
    return [im.crop((i * 640 + PAD, 0, i * 640 + PAD + CELL_W, CELL_H)) for i in range(im.width // 640)]
cells_a, cells_b = cut(a.heel_a), cut(a.heel_b)
n = len(cells_a)
# 2. frames 1, 2, 3, 6 from the first cut, the lunge frames 4 and 5 from the second
out = Image.new("RGBA", (CELL_W * (n + 1), CELL_H), (0, 0, 0, 0))
for i in range(n):
    out.paste((cells_b if i in LUNGE else cells_a)[i], (i * CELL_W, 0))
# 3. the idle's first frame as the last frame, its ground line 470 -> 598
idle = Image.open(IDLE).convert("RGBA").crop((0, 0, 512, 512))
out.alpha_composite(idle, (n * CELL_W, GROUND - 470))
out.save(a.out)
os.remove(TMP)
print("wrote", a.out, out.size)

# 4. placement (a DRAFT path: the user can refine it in the frame position tool): x = a share of the distance to the target, no lift
pl = {"format": "frame-placement/1", "animation": "attack", "file": os.path.basename(a.out), "frames": n + 1, "fps": 14, "hitFrame": 4, "smooth": True, "xUnit": "distance-share",
      "holds": [49, 29, 229, 19, 49, 39, 0],
      "x": [0, 0, 0.1, 0.9, 1.0, 1.0, 1.0], "y": [0] * (n + 1),
      "note": "Radiant Smite, a DRAFT. 7 frames at 14 fps: wind-up 120 ms, raise 90, the held CONSECRATE pose 300 (the code's glow), the STRIKE 70 (the hit at its end: hitFrame 4), follow-through 120, recover 110, the idle's frame. "
              "holds = extra ms per frame on top of 1000/fps (71 ms): 49 + 71 = 120, 29 + 71 = 100, 229 + 71 = 300, 19 + 71 = 90, 49 + 71 = 120, 39 + 71 = 110. The page slides him toward the target during frames 3 and 4 and home after frame 7."}
with open(a.out.replace(".png", ".placement.json"), "w", encoding="utf-8", newline="\n") as f:
    json.dump(pl, f, indent=1)
