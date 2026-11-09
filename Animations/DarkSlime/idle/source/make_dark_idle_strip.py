#!/usr/bin/env python3
"""Cuts the dark slime's idle sheet (the user's Gemini JPG, 2752 x 1536, six panels, 3 x 2, flat GREEN background) into the 6-frame strip (2026-11-09).

  python Animations/DarkSlime/idle/source/make_dark_idle_strip.py

dark_panels.load_panels (the ice slime's piece-based loader with a GREEN key) finds the six creatures (crescents and ink blobs go to their creature). Every panel is scaled so that its BASE is 350 px wide
(the monster standard), stands on y 470 (the body's lowest point) with the base centre on x 259, and is written into a 512 px cell. squash.json: per frame the height of the eyes above the ground and the
base width against frame 1 (the page's Squash slider uses it). Output: ../dark_idle_strip.png, ../dark_idle_strip.squash.json, ../dark_idle_check.png and a report.
"""
import json, os, sys
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "source"))
import dark_panels as dp

SRC = os.path.join(HERE, "dark_idle_sheet.jpg")
OUT = os.path.join(HERE, "..", "dark_idle_strip.png")
BASE_W, GROUND_Y, BASE_X, FRAME = 350, 470, 259, 512

data = dp.load_panels(SRC, [3, 3]); P = data["panels"]
out = Image.new("RGBA", (FRAME * 6, FRAME), (0, 0, 0, 0))
rows = []
print("panel | base w (sheet px) | scale | eyes height above ground | base w | figure top y | clipped | faded | x range")
for k, q in enumerate(P):
    sc = BASE_W / float(q["bw"])
    ox = int(round(BASE_X - dp.base_mid(q) * sc)); oy = int(round(GROUND_Y - q["low"] * sc))
    fr, clipped, faded = dp.place(q, sc, ox, oy)
    arr = np.array(fr); a = arr[..., 3] > 128; ys, xs = np.where(a)
    # the eyes: the two biggest bright violet-pink blobs in the face area (the horns' pale tips are above it)
    r_, g_, b_ = arr[..., 0].astype(int), arr[..., 1].astype(int), arr[..., 2].astype(int)
    box = np.zeros(a.shape, bool); box[250:420, 259:512] = True
    eye = a & box & (r_ > 185) & (b_ > 215) & (g_ > 100)
    eye = ndi.binary_opening(eye, structure=np.ones((5, 5)))
    lab, n = ndi.label(eye); ey = None
    if n:
        sz = ndi.sum(eye, lab, range(1, n + 1)); top2 = np.argsort(sz)[::-1][:2]
        ey = float(np.mean([ndi.center_of_mass(lab == (i + 1))[0] for i in top2]))
    out.alpha_composite(fr, (FRAME * k, 0))
    rows.append((q["bw"] * sc, GROUND_Y - ey if ey is not None else float("nan")))
    print("  %d   |   %4d   | %.3f |   %5.1f   | %.0f | %3d | %d | %d | %d..%d" % (k + 1, q["bw"], sc, rows[-1][1], q["bw"] * sc, ys.min(), clipped, faded, xs.min(), xs.max()))
out.save(OUT)
R = [round(r[1] / rows[0][1], 3) for r in rows]
Q = [round(r[0] / rows[0][0], 3) for r in rows]
print("eye height ratio:", R, "| base width ratio:", Q)
json.dump({"note": "per-frame proportions of the drawn slime against frame 1: h = height of the eyes above the ground, w = width of the base; the page undoes a chosen share of the deformation",
           "h": R, "w": Q, "match": [1.0] * 6}, open(os.path.join(os.path.dirname(OUT), "dark_idle_strip.squash.json"), "w"), indent=1)
W, H = out.size
pic = Image.new("RGB", (W, H * 2), (255, 255, 255))
for i, bg in enumerate([(255, 255, 255, 255), (38, 84, 52, 255)]):
    c = Image.new("RGBA", (W, H), bg); c.alpha_composite(out); pic.paste(c.convert("RGB"), (0, i * H))
d = ImageDraw.Draw(pic)
for i in range(2): d.line([(0, i * H + GROUND_Y), (W, i * H + GROUND_Y)], fill=(0, 0, 0) if i == 0 else (255, 255, 255), width=1)
pic.resize((W * 2 // 3, H * 2 * 2 // 3), Image.LANCZOS).save(os.path.join(HERE, "..", "dark_idle_check.png"))
print("strip", os.path.abspath(OUT))
