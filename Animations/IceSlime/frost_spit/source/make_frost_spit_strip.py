#!/usr/bin/env python3
"""Cuts the ice slime's Frost Spit sheet (the user's Gemini JPG, 2752 x 1536, 4 x 2 panels) into the 8-frame strip (2026-11-08).

  python Animations/IceSlime/frost_spit/source/make_frost_spit_strip.py

The fire slime's spit cutter for the ice slime:
1. equalize_sheet.py re-lays the eight creatures into equal cells (nothing crossed a border here either);
2. slice_keypose_sheet.py with ONE scale from panel 1's base width (350 px, the same as the idle), the base of every frame CENTRED on x 256 (--modes feet: the idle's base centre; the heel mode of the fire
   spit did not hold the back end of this sheet's bases still: the generator slid whole bases forward in panels 5 to 7, by up to 58 px), and the size corrections
   --scale-mult 1,1.01,1.01,0.99,1.04,1.03,0.96,0.96 (a template match of the idle's eye band against every frame: 1.00, 0.99, 0.99, 1.01, 0.96, 0.97, 1.04, 1.04);
3. the ice shard in the mouth is found on frames 4 and 5 (the biggest bright cyan blob in the face area: the shard sticks a little out of the mouth) and the dark mouth opening on frame 6 (the biggest
   dark blob), and written to ice_frost_spit_8frame_strip.mouth.json: where the page starts the spit, in the 512 cell BEFORE the page mirrors the sprite (x becomes 512 - x).
"""
import json, os, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
SRC = os.path.join(HERE, "frost_spit_sheet.jpg")
EQ = os.path.join(HERE, "frost_spit_equal_sheet.png")
OUT = os.path.join(HERE, "..", "ice_frost_spit_8frame_strip.png")
CHECK = os.path.join(HERE, "..", "ice_frost_spit_check.png")
T = os.path.join(ROOT, "source", "tools")
py = sys.executable
subprocess.run([py, os.path.join(T, "equalize_sheet.py"), SRC, EQ, "--cols", "4", "--rows", "2"], check=True)
subprocess.run([py, os.path.join(T, "slice_keypose_sheet.py"), EQ, OUT, "--cols", "4", "--rows", "2", "--base-width", "350", "--scale-from", "panel1",
                "--scale-mult", "1,1.01,1.01,0.99,1.04,1.03,0.96,0.96", "--modes", "feet", "--feet-x", "256", "--keep-near", "0.25",
                "--despill-band", "10", "--despill-thr", "4"], check=True)

st = np.array(Image.open(OUT).convert("RGBA")).astype(int)
marks = {}
for k in (3, 4, 5):
    f = st[:, k * 512:(k + 1) * 512]
    box = np.zeros(f.shape[:2], bool); box[250:430, 240:512] = True
    r, g, b, a = f[..., 0], f[..., 1], f[..., 2], f[..., 3]
    if k < 5: m = box & (a > 128) & (r < 150) & (g > 215) & (b > 235); need = 250                     # the bright cyan ice shard
    else: m = box & (a > 128) & (0.3 * r + 0.59 * g + 0.11 * b < 120); need = 600                       # the dark mouth opening
    lab, n = ndi.label(m)
    best = None
    for i in range(1, n + 1):
        ys, xs = np.where(lab == i)
        if len(ys) > need and (best is None or len(ys) > best[0]):
            best = (len(ys), float(xs.mean()), float(ys.mean()), int(xs.max() - xs.min()), int(ys.max() - ys.min()))
    if best:
        marks[k + 1] = {"area": best[0], "x": round(best[1], 1), "y": round(best[2], 1), "w": best[3], "h": best[4]}
json.dump({"note": "the ice shard in the mouth on frames 4 and 5 and the open mouth on frame 6 (centre and size in the 512 cell, before the page mirrors the sprite): the spit leaves the mouth at the release frame 5",
           "mouth": marks}, open(os.path.join(HERE, "..", "ice_frost_spit_8frame_strip.mouth.json"), "w"), indent=1)
print("mouth marks:", marks)
W, H = st.shape[1], st.shape[0]
img = Image.fromarray(st.astype(np.uint8))
pic = Image.new("RGB", (W, H * 2), (255, 255, 255))
for i, bg in enumerate([(255, 255, 255, 255), (38, 84, 52, 255)]):
    c = Image.new("RGBA", (W, H), bg); c.alpha_composite(img); pic.paste(c.convert("RGB"), (0, i * H))
d = ImageDraw.Draw(pic)
for i in range(2): d.line([(0, i * H + 470), (W, i * H + 470)], fill=(0, 0, 0) if i == 0 else (255, 255, 255), width=1)
for k, mk in marks.items():
    for i in range(2): d.ellipse([(k - 1) * 512 + mk["x"] - 5, i * H + mk["y"] - 5, (k - 1) * 512 + mk["x"] + 5, i * H + mk["y"] + 5], outline=(255, 0, 0), width=2)
pic.resize((W // 2, H), Image.LANCZOS).save(CHECK)
print("strip", os.path.abspath(OUT))
