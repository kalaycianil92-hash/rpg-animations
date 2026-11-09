#!/usr/bin/env python3
"""Cuts the fire slime's Ember Spit sheet (the user's Gemini JPG, 2752 x 1536, 4 x 2 panels) into the 8-frame strip (2026-11-08).

  python Animations/Slime/ember_spit/source/make_spit_strip.py

1. equalize_sheet.py re-lays the eight creatures into equal cells (nothing crossed a cell border in this sheet, but it makes the cut independent of the generator's layout);
2. slice_keypose_sheet.py: --base-width 350 on panel 1 (the project's monster standard, the same size as the idle's rest pose), --modes heel so the BACK end of the base stays on one
   spot and the body can stretch forward (--heel-x 87 puts frame 1 within 6 px of the idle's rest pose: the best alignment of the two silhouettes, IoU 0.92), and size corrections
   --scale-mult 1,1,1,.98,.98,.98,.97,.965 (eye-band template match against frame 1: the generator drew every panel within 4% of the same size; frames 2 and 8 use their base widths, 350 and 362 px);
3. the glowing mouth of frames 4 to 6 is found (the biggest bright yellow-orange blob inside the face) and written to fire_ember_spit_8frame_strip.mouth.json: where the page starts the spit,
   in the 512 cell BEFORE the page mirrors the sprite (x becomes 512 - x). Frame 7's blob is an eye, not the mouth, and is left out.
"""
import json, os, subprocess, sys
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
SRC = os.path.join(HERE, "ember_spit_sheet.jpg")
EQ = os.path.join(HERE, "ember_spit_equal_sheet.png")
OUT = os.path.join(HERE, "..", "fire_ember_spit_8frame_strip.png")
T = os.path.join(ROOT, "source", "tools")
py = sys.executable
subprocess.run([py, os.path.join(T, "equalize_sheet.py"), SRC, EQ, "--cols", "4", "--rows", "2"], check=True)
subprocess.run([py, os.path.join(T, "slice_keypose_sheet.py"), EQ, OUT, "--cols", "4", "--rows", "2", "--base-width", "350", "--scale-from", "panel1",
                "--scale-mult", "1,1,1,0.98,0.98,0.98,0.97,0.965", "--modes", "heel", "--heel-x", "87", "--keep-near", "0.25",
                "--despill-band", "10", "--despill-thr", "4"], check=True)

st = np.array(Image.open(OUT).convert("RGBA")).astype(int)
marks = {}
for k in range(8):
    f = st[:, k * 512:(k + 1) * 512]
    box = np.zeros(f.shape[:2], bool); box[250:430, 240:500] = True
    m = box & (f[..., 3] > 128) & (f[..., 0] > 235) & (f[..., 1] > 165) & (f[..., 2] < 150)
    lab, n = ndi.label(m)
    best = None
    for i in range(1, n + 1):
        ys, xs = np.where(lab == i)
        if len(ys) > 600 and (best is None or len(ys) > best[0]):
            best = (len(ys), float(xs.mean()), float(ys.mean()), int(xs.max() - xs.min()), int(ys.max() - ys.min()))
    if best:
        marks[k + 1] = {"area": best[0], "x": round(best[1], 1), "y": round(best[2], 1), "w": best[3], "h": best[4]}
json.dump({"note": "the glowing mouth interior per frame (centre and size in the 512 cell, before the page mirrors the sprite): the spit leaves the mouth at the release frame 5",
           "mouth": marks}, open(os.path.join(HERE, "..", "fire_ember_spit_8frame_strip.mouth.json"), "w"), indent=1)
print("mouth marks:", marks)
