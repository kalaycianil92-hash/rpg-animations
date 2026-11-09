#!/usr/bin/env python3
"""Cuts the ice slime's Hit sheet (the user's Gemini JPG, 2752 x 1536, 3 x 2 panels) into the 6-frame strip (2026-11-08).

  python Animations/IceSlime/hit/source/make_hit_strip.py

equalize_sheet.py (3 x 2), then slice_keypose_sheet.py with every panel scaled on its own to a base width of 350 px (--fit-base: a hit leaves the base where it is, and the faces cannot size the panels:
the eyes are shut in the first two; the base widths in the sheet were 819, 851, 838, 849, 851, 855) and the base centred on x 256 (the ice idle's base centre).
Output: ../ice_hit_6frame_strip.png (512 x 512 per frame, base 350 px, ground line y 470) and ../ice_hit_check.png.
"""
import os, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
SRC = os.path.join(HERE, "hit_sheet.jpg"); EQ = os.path.join(HERE, "hit_equal_sheet.png")
OUT = os.path.join(HERE, "..", "ice_hit_6frame_strip.png"); CHECK = os.path.join(HERE, "..", "ice_hit_check.png")
T = os.path.join(ROOT, "source", "tools"); py = sys.executable
subprocess.run([py, os.path.join(T, "equalize_sheet.py"), SRC, EQ, "--cols", "3", "--rows", "2"], check=True)
subprocess.run([py, os.path.join(T, "slice_keypose_sheet.py"), EQ, OUT, "--cols", "3", "--rows", "2", "--base-width", "350", "--scale-from", "panel1", "--fit-base", "1,2,3,4,5,6",
                "--modes", "feet", "--feet-x", "256", "--keep-near", "0.25", "--despill-band", "10", "--despill-thr", "4"], check=True)
st = Image.open(OUT).convert("RGBA"); W, H = st.size
pic = Image.new("RGB", (W, H * 2), (255, 255, 255))
for i, bg in enumerate([(255, 255, 255, 255), (38, 84, 52, 255)]):
    c = Image.new("RGBA", (W, H), bg); c.alpha_composite(st); pic.paste(c.convert("RGB"), (0, i * H))
d = ImageDraw.Draw(pic)
for i in range(2): d.line([(0, i * H + 470), (W, i * H + 470)], fill=(0, 0, 0) if i == 0 else (255, 255, 255), width=1)
pic.resize((W * 2 // 3, H * 2 * 2 // 3), Image.LANCZOS).save(CHECK)
idle = np.array(Image.open(os.path.join(ROOT, "Animations", "IceSlime", "idle", "ice_idle_strip.png")).convert("RGBA"))[:, :512]
a = np.array(st)[:, 5 * 512:6 * 512]
A = idle[..., 3] > 128; B = a[..., 3] > 128
print("silhouette IoU of the last frame with the idle's rest frame: %.3f" % ((A & B).sum() / (A | B).sum()))
print("strip", os.path.abspath(OUT))
