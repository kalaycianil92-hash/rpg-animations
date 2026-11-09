#!/usr/bin/env python3
"""Cuts the Elite slime's idle sheet (the user's Gemini JPG, 2528 x 1696, six panels, 3 x 2, 2026-11-10) into the 6-frame strip.

  python Animations/EliteSlime/idle/source/make_elite_idle_strip.py [base_width]

elite_panels.load_panels (the lightning loader's cousin: the body is the biggest piece, the floating fist with its sword is kept and goes to the body it is nearest to; the generator drew the skirts of panels 4 and 5
touching, they are split in the valley between them). Every panel is scaled so that its BASE is BASE_W px wide (default 350: the slimes' standard; at 300 the Elite came out smaller than the ice slime, the weakest of the others),
stands on y 470 (the body's lowest point) with the base centre on x 259, and is written into a 512 px cell.
Output: ../elite_idle_strip.png, ../elite_idle_strip.squash.json (per frame: h = height of the eyes above the ground and w = base width, against frame 1; fist = height of the fist's middle above the ground),
../elite_idle_check.png and a report.
"""
import json, os, sys
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "source"))
import elite_panels as ep

SRC = os.path.join(HERE, "elite_idle_sheet.jpg")
OUT = os.path.join(HERE, "..", "elite_idle_strip.png")
BASE_W = float(sys.argv[1]) if len(sys.argv) > 1 else 350.0
GROUND_Y, BASE_X, FRAME = 470, 259, 512
SPLITS = [(826, 1380, 1660)]                         # the skirts of panels 4 and 5 touch at x 824 to 827 (31 px of overlap column at the narrowest)

data = ep.load_panels(SRC, [3, 3], splits=SPLITS); P = data["panels"]
out = Image.new("RGBA", (FRAME * 6, FRAME), (0, 0, 0, 0))
rows = []
print("panel | base w (sheet px) | scale | eyes above ground | base w | fist mid above ground | fist gap to body | figure top y | clipped | x range")
for k, q in enumerate(P):
    sc = BASE_W / float(q["bw"])
    ox = int(round(BASE_X - ep.base_mid(q) * sc)); oy = int(round(GROUND_Y - q["low"] * sc))
    fr, clipped = ep.place(q, sc, ox, oy)
    arr = np.array(fr); a = arr[..., 3] > 128; ys, xs = np.where(a)
    # eyes: the two biggest amber blobs (orange pupils)
    R, G, B = arr[..., 0].astype(int), arr[..., 1].astype(int), arr[..., 2].astype(int)
    amber = a & (R > 200) & (G > 110) & (G < 215) & (B < 110)
    amber = ndi.binary_opening(amber, structure=np.ones((3, 3)))
    lab, n = ndi.label(amber); ey = None
    if n:
        sz = ndi.sum(amber, lab, range(1, n + 1)); top2 = np.argsort(sz)[::-1][:2]
        ey = float(np.mean([ndi.center_of_mass(lab == (i + 1))[0] for i in top2]))
    # the fist and sword: the detached pieces' middle and their gap to the body (at the scaled size)
    fm = np.array(Image.fromarray((q["fist"] * 255).astype(np.uint8)).resize((int(q["fist"].shape[1] * sc), int(q["fist"].shape[0] * sc)), Image.BILINEAR)) > 127
    bm = np.array(Image.fromarray((q["main"] * 255).astype(np.uint8)).resize((int(q["main"].shape[1] * sc), int(q["main"].shape[0] * sc)), Image.BILINEAR)) > 127
    fy, fx = np.where(fm)
    gap = float(ndi.distance_transform_edt(~bm)[fm].min()) if fm.any() else float("nan")
    fist_mid = GROUND_Y - (oy + float(np.mean(fy))) if len(fy) else float("nan")
    out.alpha_composite(fr, (FRAME * k, 0))
    rows.append((q["bw"] * sc, GROUND_Y - ey if ey is not None else float("nan"), fist_mid, gap))
    print("  %d   |   %4d   | %.3f |   %5.1f   | %.0f |   %5.1f   |   %4.1f   | %3d | %d | %d..%d" % (k + 1, q["bw"], sc, rows[-1][1], q["bw"] * sc, fist_mid, gap, ys.min(), clipped, xs.min(), xs.max()))
out.save(OUT)
R = [round(r[1] / rows[0][1], 3) for r in rows]
Q = [round(r[0] / rows[0][0], 3) for r in rows]
F = [round(r[2], 1) for r in rows]
print("eye height ratio:", R, "| base width ratio:", Q, "| fist mid above ground:", F)
json.dump({"note": "per-frame proportions of the drawn slime against frame 1: h = height of the eyes above the ground, w = width of the base; fist = height of the floating fist's middle above the ground (px in the 512 cell); the page undoes a chosen share of the deformation",
           "h": R, "w": Q, "fist": F, "match": [1.0] * 6}, open(os.path.join(os.path.dirname(OUT), "elite_idle_strip.squash.json"), "w"), indent=1)
W, H = out.size
pic = Image.new("RGB", (W, H * 2), (255, 255, 255))
for i, bg in enumerate([(255, 255, 255, 255), (38, 84, 52, 255)]):
    c = Image.new("RGBA", (W, H), bg); c.alpha_composite(out); pic.paste(c.convert("RGB"), (0, i * H))
d = ImageDraw.Draw(pic)
for i in range(2): d.line([(0, i * H + GROUND_Y), (W, i * H + GROUND_Y)], fill=(0, 0, 0) if i == 0 else (255, 255, 255), width=1)
pic.resize((W * 2 // 3, H * 2 * 2 // 3), Image.LANCZOS).save(os.path.join(HERE, "..", "elite_idle_check.png"))
print("strip", os.path.abspath(OUT))
