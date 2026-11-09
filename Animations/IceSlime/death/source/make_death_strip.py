#!/usr/bin/env python3
"""Cuts the ice slime's Death sheet (the user's Gemini JPG, 2752 x 1536, 3 x 2 panels) into the 6-frame strip (2026-11-08).

  python Animations/IceSlime/death/source/make_death_strip.py

ONE shared scale from panel 1's base width (350 px, the monster standard): the body cracks, breaks and collapses into a pile (the base widths in the sheet were 841, 838, 861, 842, 818, 823), so no panel can be
sized by its own base. --modes feet centres the base of every frame on x 256 (the ice idle's base centre), which is also the middle of the pile. The last frame is the pile of dull shards, NOT the rest pose.
Output: ../ice_death_6frame_strip.png (512 x 512 per frame, base 350 px, ground line y 470) and ../ice_death_check.png.
"""
import os, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
SRC = os.path.join(HERE, "death_sheet.jpg"); EQ = os.path.join(HERE, "death_equal_sheet.png")
OUT = os.path.join(HERE, "..", "ice_death_6frame_strip.png"); CHECK = os.path.join(HERE, "..", "ice_death_check.png")
T = os.path.join(ROOT, "source", "tools"); py = sys.executable
subprocess.run([py, os.path.join(T, "equalize_sheet.py"), SRC, EQ, "--cols", "3", "--rows", "2"], check=True)
subprocess.run([py, os.path.join(T, "slice_keypose_sheet.py"), EQ, OUT, "--cols", "3", "--rows", "2", "--base-width", "350", "--scale-from", "panel1",
                "--modes", "feet", "--feet-x", "256", "--keep-near", "0.25", "--despill-band", "10", "--despill-thr", "4"], check=True)
st = Image.open(OUT).convert("RGBA"); W, H = st.size
pic = Image.new("RGB", (W, H * 2), (255, 255, 255))
for i, bg in enumerate([(255, 255, 255, 255), (38, 84, 52, 255)]):
    c = Image.new("RGBA", (W, H), bg); c.alpha_composite(st); pic.paste(c.convert("RGB"), (0, i * H))
d = ImageDraw.Draw(pic)
for i in range(2): d.line([(0, i * H + 470), (W, i * H + 470)], fill=(0, 0, 0) if i == 0 else (255, 255, 255), width=1)
pic.resize((W * 2 // 3, H * 2 * 2 // 3), Image.LANCZOS).save(CHECK)
print("strip", os.path.abspath(OUT))
