#!/usr/bin/env python3
"""Cuts the Elite slime's idle sheet (the user's Gemini JPG, 2528 x 1696, six panels, 3 x 2, 2026-11-10) into the 6-frame strip.

  python Animations/EliteSlime/idle/source/make_elite_idle_strip.py [base_width [keep]]

elite_panels.load_panels (the lightning loader's cousin: the body is the biggest piece, the floating fist with its sword is kept and goes to the body it is nearest to; the generator drew the skirts of panels 4 and 5
touching, they are split in the valley between them). Every panel is scaled so that its BASE is BASE_W px wide (default 350: the slimes' standard), stands on y 470 (the body's lowest point) with the base centre
on x 259, and is written into a 512 px cell.

TONING THE HEAD DOWN (2026-11-10, the user: "head part bounce so much"). Measured on the cut strip (per part, rows against frame 1): the dome's top plate rises up to 21 px in frame 5 (7% of the figure), the face
only 3, the shield 6, the belt 3, the skirt 0: the generator stretched the DOME upward far more than the prompt's 2%. So the body (not the fist and sword) is warped vertically, per frame, by a piecewise-linear
row shift through the measured rows (skirt, belt, shield, face, top of the dome): only `keep` (default 0.3) of each part's measured movement is kept, the rest is taken out (keep 1 = as drawn, 0 = frozen).
The floating fist and its sword are NOT warped: they stay the idle's visible life.
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
KEEP = float(sys.argv[2]) if len(sys.argv) > 2 else 0.3
GROUND_Y, BASE_X, FRAME = 470, 259, 512
SPLITS = [(826, 1380, 1660)]                         # the skirts of panels 4 and 5 touch at x 824 to 827 (31 px of overlap column at the narrowest)
# rows (frame-1 coordinates, 512 cell, base 350) and column ranges of the parts whose shift is measured by matching against frame 1 (x0, x1, y0, y1)
REGIONS = {"skirt": (100, 420, 410, 468), "belt": (100, 330, 375, 410), "shield": (100, 200, 290, 420), "face": (215, 335, 235, 330)}
SEARCH = 30

data = ep.load_panels(SRC, [3, 3], splits=SPLITS); P = data["panels"]


def layers(q):
    """(scale, ox, oy, full, body, fist): the panel placed in the 512 cell as one picture, and as the body alone and the floating fist alone."""
    sc = BASE_W / float(q["bw"])
    ox = int(round(BASE_X - ep.base_mid(q) * sc)); oy = int(round(GROUND_Y - q["low"] * sc))
    mb = ndi.binary_dilation(q["main"], iterations=3); mf = ndi.binary_dilation(q["fist"], iterations=3) & ~mb
    pb = q["p"].copy(); pb[..., 3] = np.where(mb, pb[..., 3], 0)
    pf = q["p"].copy(); pf[..., 3] = np.where(mf, pf[..., 3], 0)
    full, clipped = ep.place(q, sc, ox, oy)
    body, _ = ep.place(dict(q, p=pb), sc, ox, oy); fist, _ = ep.place(dict(q, p=pf), sc, ox, oy)
    return sc, ox, oy, full, body, fist, clipped


def gray(im):
    f = np.array(im).astype(float); a = f[..., 3] / 255
    return (0.3 * f[..., 0] + 0.59 * f[..., 1] + 0.11 * f[..., 2]) * a + 90 * (1 - a)


def top_row(im):
    return int(np.where((np.array(im)[..., 3] > 128).any(1))[0].min())


L = [layers(q) for q in P]
G = [gray(l[3]) for l in L]
shifts = []                                              # per frame: {part: rows the part sits higher (-) or lower (+) than in frame 1}
for k in range(6):
    s = {}
    for nm, (x0, x1, y0, y1) in REGIONS.items():
        base = G[0][y0:y1, x0:x1]; best = None
        for dy in range(-SEARCH, SEARCH + 1):
            ssd = ((G[k][y0 + dy:y1 + dy, x0:x1] - base) ** 2).mean()
            if best is None or ssd < best[0]: best = (ssd, dy)
        s[nm] = best[1]
    s["top"] = top_row(L[k][4]) - top_row(L[0][4])       # the dome's top edge (the silhouette: the most reliable measure of the dome's stretch)
    shifts.append(s)


def warp(body, s):
    """Vertical, row by row: the part measured at row y of frame 1 moves by s(y) in this frame; the output keeps only KEEP of that movement (sampling source row y + (1 - KEEP) s(y))."""
    ys = [468, 440, 392, 355, 282, 205, 169]
    sv = [0, s["skirt"], s["belt"], s["shield"], s["face"], 0.5 * (s["face"] + s["top"]), s["top"]]       # (row 205: half way up the dome)
    order = np.argsort(ys); ys = np.array(ys)[order]; sv = np.array(sv, float)[order]
    rows = np.arange(FRAME, dtype=float)
    d = (1 - KEEP) * np.interp(rows, ys, sv)             # np.interp holds the end values: below the skirt 0, above the dome's top the top's shift
    src = rows + d
    arr = np.array(body).astype(float); pm = arr.copy(); pm[..., :3] *= (arr[..., 3:4] / 255)
    out = np.zeros_like(pm)
    y0 = np.clip(np.floor(src).astype(int), 0, FRAME - 1); y1 = np.clip(y0 + 1, 0, FRAME - 1); t = (src - np.floor(src))[:, None, None]
    out = pm[y0] * (1 - t) + pm[y1] * t
    out[(src < 0) | (src > FRAME - 1)] = 0
    a = out[..., 3:4]; rgb = np.where(a > 0.5, out[..., :3] / np.maximum(a / 255, 1e-6), 0)
    return Image.fromarray(np.dstack([np.clip(rgb, 0, 255), a]).astype(np.uint8))


strip = Image.new("RGBA", (FRAME * 6, FRAME), (0, 0, 0, 0))
rows_info = []
print("panel | shifts vs frame 1 (skirt belt shield face top) | eyes above ground | base w | fist mid above ground | fist gap | figure top y | clipped")
for k, q in enumerate(P):
    sc, ox, oy, full, body, fist, clipped = L[k]
    wb = warp(body, shifts[k]) if k else body
    fr = Image.new("RGBA", (FRAME, FRAME), (0, 0, 0, 0)); fr.alpha_composite(wb); fr.alpha_composite(fist)
    arr = np.array(fr); a = arr[..., 3] > 128; ys, xs = np.where(a)
    R, G_, B = arr[..., 0].astype(int), arr[..., 1].astype(int), arr[..., 2].astype(int)
    amber = ndi.binary_opening(a & (R > 200) & (G_ > 110) & (G_ < 215) & (B < 110), structure=np.ones((3, 3)))
    lab, n = ndi.label(amber); ey = None
    if n:
        sz = ndi.sum(amber, lab, range(1, n + 1)); top2 = np.argsort(sz)[::-1][:2]
        ey = float(np.mean([ndi.center_of_mass(lab == (i + 1))[0] for i in top2]))
    fa = np.array(fist)[..., 3] > 128; fy, fx = np.where(fa); ba = np.array(wb)[..., 3] > 128
    gap = float(ndi.distance_transform_edt(~ba)[fa].min()) if fa.any() else float("nan")
    fist_mid = GROUND_Y - float(np.mean(fy)) if len(fy) else float("nan")
    strip.alpha_composite(fr, (FRAME * k, 0))
    rows_info.append((q["bw"] * sc, GROUND_Y - ey if ey is not None else float("nan"), fist_mid, gap))
    s = shifts[k]
    print("  %d   | %3d %3d %3d %3d %3d | %5.1f | %.0f | %5.1f | %4.1f | %3d | %d" % (k + 1, s["skirt"], s["belt"], s["shield"], s["face"], s["top"], rows_info[-1][1], q["bw"] * sc, fist_mid, gap, ys.min(), clipped))
strip.save(OUT)
R = [round(r[1] / rows_info[0][1], 3) for r in rows_info]
Q = [round(r[0] / rows_info[0][0], 3) for r in rows_info]
F = [round(r[2], 1) for r in rows_info]
tops = [top_row(strip.crop((k * FRAME, 0, (k + 1) * FRAME, FRAME)).crop((0, 0, 370, FRAME))) for k in range(6)]
print("KEEP", KEEP, "| eye height ratio:", R, "| base width ratio:", Q, "| fist mid above ground:", F, "| dome top rows:", tops)
json.dump({"note": "per-frame proportions of the drawn slime against frame 1: h = height of the eyes above the ground, w = width of the base; fist = height of the floating fist's middle above the ground (px in the 512 cell); the page undoes a chosen share of the deformation. The dome's own stretch was already toned down in the strip (keep=%.2f, see make_elite_idle_strip.py)" % KEEP,
           "h": R, "w": Q, "fist": F, "match": [1.0] * 6}, open(os.path.join(os.path.dirname(OUT), "elite_idle_strip.squash.json"), "w"), indent=1)
W, H = strip.size
pic = Image.new("RGB", (W, H * 2), (255, 255, 255))
for i, bg in enumerate([(255, 255, 255, 255), (38, 84, 52, 255)]):
    c = Image.new("RGBA", (W, H), bg); c.alpha_composite(strip); pic.paste(c.convert("RGB"), (0, i * H))
d = ImageDraw.Draw(pic)
for i in range(2): d.line([(0, i * H + GROUND_Y), (W, i * H + GROUND_Y)], fill=(0, 0, 0) if i == 0 else (255, 255, 255), width=1)
pic.resize((W * 2 // 3, H * 2 * 2 // 3), Image.LANCZOS).save(os.path.join(HERE, "..", "elite_idle_check.png"))
print("strip", os.path.abspath(OUT))
