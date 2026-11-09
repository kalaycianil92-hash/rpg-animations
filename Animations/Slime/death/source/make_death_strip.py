#!/usr/bin/env python3
"""Cuts the fire slime's Death sheet (the user's Gemini JPG, 2752 x 1536, 3 x 2 panels) into the 6-frame strip (2026-11-08).

  python Animations/Slime/death/source/make_death_strip.py

One shared scale from panel 1's base width (350 px, the monster standard): the body melts and spreads (the base widths in the sheet were 708, 707, 776, 792, 859, 492), so no panel can be sized by its own base.
--modes feet centres the base of every frame on x 260 (the idle's base centre), which is also the middle of the puddle. The last frame is the flat cooled puddle, NOT the rest pose, so its IoU with the idle is meaningless.
Output: ../fire_death_6frame_strip.png (512 x 512 per frame, base 350 px, ground line y 470) and ../fire_death_check.png (white and forest green, the ground line drawn).
"""
import os, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
SRC = os.path.join(HERE, "death_sheet.jpg")
EQ = os.path.join(HERE, "death_equal_sheet.png")
OUT = os.path.join(HERE, "..", "fire_death_6frame_strip.png")
CHECK = os.path.join(HERE, "..", "fire_death_check.png")
T = os.path.join(ROOT, "source", "tools")
py = sys.executable
subprocess.run([py, os.path.join(T, "equalize_sheet.py"), SRC, EQ, "--cols", "3", "--rows", "2"], check=True)
subprocess.run([py, os.path.join(T, "slice_keypose_sheet.py"), EQ, OUT, "--cols", "3", "--rows", "2", "--base-width", "350", "--scale-from", "panel1",
                "--modes", "feet", "--feet-x", "260", "--keep-near", "0.25", "--despill-band", "10", "--despill-thr", "4"], check=True)
st = Image.open(OUT).convert("RGBA"); W, H = st.size
pic = Image.new("RGB", (W, H * 2), (255, 255, 255))
for i, bg in enumerate([(255, 255, 255, 255), (38, 84, 52, 255)]):
    c = Image.new("RGBA", (W, H), bg); c.alpha_composite(st); pic.paste(c.convert("RGB"), (0, i * H))
d = ImageDraw.Draw(pic)
for i in range(2): d.line([(0, i * H + 470), (W, i * H + 470)], fill=(0, 0, 0) if i == 0 else (255, 255, 255), width=1)
pic.resize((W // 2, H), Image.LANCZOS).save(CHECK)
# how close the last frame is to the idle's rest pose (silhouettes, after the same base width): the animation must join the idle
idle = np.array(Image.open(os.path.join(ROOT, "Animations", "Slime", "idle", "fire_idle_strip.png")).convert("RGBA"))[:, :512]
a = np.array(st)[:, 5 * 512:(5 + 1) * 512]
A = idle[..., 3] > 128; B = a[..., 3] > 128
print("silhouette IoU of the last frame with the idle's rest frame: %.3f" % ((A & B).sum() / (A | B).sum()))
print("strip", os.path.abspath(OUT))
