#!/usr/bin/env python3
"""Cuts the ice slime's Dodge sheet (the user's Gemini JPG, 2752 x 1536, six panels, 3 x 2) into the 6-frame strip (2026-11-08).

  python Animations/IceSlime/dodge/source/make_dodge_strip.py

The fire slime's dodge cutter (Animations/Slime/dodge/source/make_dodge_strip.py) with three changes for this sheet:
  1. The panels are NOT cut by a fixed grid. The generator drew the airborne panels high (panel 3, top right) and low-floating (panel 4, bottom left) and the crystals of panel 4 reach above the middle line of
     the sheet, so the creatures are found as pieces: the six biggest pieces are the creatures, every other piece of 40 px or more goes to the nearest one, and each panel keeps its real place in the sheet
     (its y is measured from the top of its row's band, so the floor line of a row is the same for its panels).
  2. The tip of panel 3's tall crystal touches the top edge of the sheet and is cut flat (235 px in the top 4 rows): the sheet is padded with magenta and the missing pointed tip is repaired (the crystal's
     two edges are continued to a point, filled with the crystal's own pale colour and outlined in the dark blue-teal).
  3. The height of the hop is the panel's REAL height above its row's floor (no double counting: the fire dodge's script added the lift twice, docs/MONSTERS.md).
One scale from panel 1's base width (350 px, the monster standard), panel 6 (the rest pose again) corrects the second row, the floor line of each row from its grounded panels (1, 2, 5, 6), the grounded
bases centred on x 256 (the ice idle's base centre) and the airborne panels in between.
Output: ../ice_dodge_6frame_strip.png (512 x 512 per frame) and ../ice_dodge_check.png.
"""
import os, sys
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "dodge_sheet.jpg")
OUT = os.path.join(HERE, "..", "ice_dodge_6frame_strip.png")
CHECK = os.path.join(HERE, "..", "ice_dodge_check.png")
COLS, ROWS, N = 3, 2, 6
GROUNDED = [0, 1, 4, 5]                    # panels 1, 2, 5, 6 rest on the floor; 3 and 4 are in the air
BASE_W, GROUND_Y, BASE_X, FRAME = 350, 470, 256, 512
PAD = 80                                   # magenta added above the sheet for the repaired crystal tip

im0 = Image.open(SRC).convert("RGB")
W0, H0 = im0.size
img = Image.new("RGB", (W0, H0 + PAD), (255, 0, 255)); img.paste(im0, (0, PAD))
a0 = np.array(im0).astype(float)
al0 = 1 - np.clip((np.minimum(a0[..., 0], a0[..., 2]) - a0[..., 1] - 70) / 110, 0, 1)
cut_cols = np.where((al0[:4] > 0.5).any(0))[0]
if len(cut_cols):                          # repair of the tip cut by the top edge
    x0, x1 = int(cut_cols.min()), int(cut_cols.max())
    d = ImageDraw.Draw(img)
    patch = np.array(im0)[6:12, x0 + (x1 - x0) // 3:x0 + 2 * (x1 - x0) // 3].reshape(-1, 3).mean(0)
    fill = tuple(int(v) for v in patch); line = (31, 78, 100)
    px = PAD                                # the sheet's row 0 is at y = PAD in the padded image
    # the left edge is nearly vertical, the right edge comes in at about 45 degrees: the apex is where they meet
    left_x = x0 + 2; apex = (left_x + 2, px - (x1 - left_x) + 6)
    poly = [(x0 + 1, px + 4), (x1 + 1, px + 4), apex]
    d.polygon(poly, fill=fill)
    d.line([(x0 + 1, px + 4), apex], fill=line, width=7); d.line([(x1 + 1, px + 4), apex], fill=line, width=7)
    print("tip repaired: cut from x %d to %d, apex %s" % (x0, x1, apex))
arr = np.array(img).astype(float)
r, g, b = arr[..., 0], arr[..., 1], arr[..., 2]
alpha = 1 - np.clip((np.minimum(r, b) - g - 70) / 110, 0, 1)
soft = alpha < 1
rgb = arr.copy()
rgb[..., 0] = np.where(soft, np.minimum(r, g + 25), r); rgb[..., 2] = np.where(soft, np.minimum(b, g + 25), b)
band = ndi.binary_dilation(alpha < 0.5, iterations=10) & (alpha >= 0.5)
mm = np.minimum(rgb[..., 0], rgb[..., 2]) - rgb[..., 1]
fix = (band | soft) & (mm > 4)
rgb[..., 0] = np.where(fix, np.minimum(rgb[..., 0], rgb[..., 1] + 4), rgb[..., 0]); rgb[..., 2] = np.where(fix, np.minimum(rgb[..., 2], rgb[..., 1] + 4), rgb[..., 2])
rgba = np.dstack([rgb, alpha * 255]).astype(np.uint8)
H, Wd = rgba.shape[:2]

# ---- the creatures as pieces
solid = rgba[..., 3] > 128
lab, n = ndi.label(solid); sizes = ndi.sum(solid, lab, range(1, n + 1)); objs = ndi.find_objects(lab)
order = np.argsort(sizes)[::-1]; bigs = [int(i) + 1 for i in order[:N]]
def box(i):
    sl = objs[i - 1]; return sl[1].start, sl[0].start, sl[1].stop, sl[0].stop
def box_dist(b1, b2):
    dx = max(b1[0] - b2[2], b2[0] - b1[2], 0); dy = max(b1[1] - b2[3], b2[1] - b1[3], 0)
    return (dx * dx + dy * dy) ** 0.5
cen = {i: ((box(i)[0] + box(i)[2]) / 2, (box(i)[1] + box(i)[3]) / 2) for i in bigs}
by_y = sorted(bigs, key=lambda i: cen[i][1])
panel_ids = []
for k in range(ROWS):
    panel_ids += sorted(by_y[k * COLS:(k + 1) * COLS], key=lambda i: cen[i][0])
owner = {i: k for k, i in enumerate(panel_ids)}
for i in range(1, n + 1):
    if i in owner or sizes[i - 1] < 40: continue
    dd = [box_dist(box(i), box(p)) for p in panel_ids]; owner[i] = int(np.argmin(dd))
print("creature pieces: areas %s; the sheet's rows start at y %s" % ([int(sizes[i - 1]) for i in panel_ids], [int(sorted(by_y)[0])]))

PH = (H - PAD) // ROWS
panels, boxes, bws = [], [], []
for k in range(N):
    rr = k // COLS
    mask = np.zeros(solid.shape, bool)
    for i, kk in owner.items():
        if kk == k: mask |= (lab == i)
    mask = ndi.binary_dilation(mask, iterations=3) & (rgba[..., 3] > 0)
    ys_, xs_ = np.where(mask)
    wx0, wx1 = max(0, xs_.min() - 40), min(Wd, xs_.max() + 41)
    wy0 = PAD + rr * PH - 300; wy1 = PAD + (rr + 1) * PH + 100          # the band of the panel's row, padded: the crystals may stand above it
    p = np.zeros((wy1 - wy0, wx1 - wx0, 4), np.uint8)
    ya, yb = max(0, wy0), min(H, wy1)
    p[ya - wy0:yb - wy0] = np.where(mask[ya:yb, wx0:wx1, None], rgba[ya:yb, wx0:wx1], 0)
    ys, xs = np.where(p[..., 3] > 128)
    boxes.append((xs.min(), ys.min(), xs.max(), ys.max()))
    main = ndi.label(p[..., 3] > 128)[0]; ml, mn = ndi.label(p[..., 3] > 128); msz = ndi.sum(p[..., 3] > 128, ml, range(1, mn + 1)); mmain = ml == 1 + int(np.argmax(msz))
    my, mx = np.where(mmain); y0, y1 = my.min(), my.max()
    bws.append(max(mx[my == y].max() - mx[my == y].min() for y in range(int(y1 - 0.22 * (y1 - y0)), y1 + 1) if (my == y).any()))
    panels.append(p)

scale = BASE_W / float(bws[0])
row_fix = {0: 1.0, 1: bws[0] / float(bws[5])}               # panel 6 is the rest pose again
sk = [scale * row_fix[k // COLS] for k in range(N)]
ground = {rr: float(np.median([boxes[k][3] for k in GROUNDED if k // COLS == rr])) for rr in range(ROWS)}
def base_mid(k):
    x0, y0, x1, y1 = boxes[k]
    xs = np.where((panels[k][int(y1 - 0.06 * (y1 - y0)):y1 + 1, :, 3] > 128).any(0))[0]
    return (xs.min() + xs.max()) / 2.0
sh = {k: BASE_X - base_mid(k) * sk[k] for k in GROUNDED}
shifts = {}
for k in range(N):
    before = [q for q in GROUNDED if q <= k]; after = [q for q in GROUNDED if q >= k]
    if k in sh: shifts[k] = sh[k]
    else: shifts[k] = sh[before[-1]] + (sh[after[0]] - sh[before[-1]]) * (k - before[-1]) / float(after[0] - before[-1])

out = Image.new("RGBA", (FRAME * N, FRAME), (0, 0, 0, 0))
print("scale %.4f, second row x %.3f; base widths in the sheet %s" % (scale, row_fix[1], [int(v) for v in bws]))
print("panel | lift above the floor (px, in the 512 cell) | figure top y | clipped px | x range")
for k, p in enumerate(panels):
    im = Image.fromarray(p).resize((int(p.shape[1] * sk[k]), int(p.shape[0] * sk[k])), Image.LANCZOS)
    lift = max(0.0, (ground[k // COLS] - boxes[k][3]) * sk[k]) if k not in GROUNDED else 0.0
    ox = int(round(shifts[k])); oy = int(round(GROUND_Y - ground[k // COLS] * sk[k]))          # (the airborne panel is already at its real height: no lift is added)
    canvas = Image.new("RGBA", (FRAME + 3000, FRAME + 3000), (0, 0, 0, 0)); canvas.alpha_composite(im, (1500 + ox, 1500 + oy))
    fr = canvas.crop((1500, 1500, 1500 + FRAME, 1500 + FRAME))
    clipped = int((np.array(im)[..., 3] > 128).sum() - (np.array(fr)[..., 3] > 128).sum())
    a = np.array(fr)[..., 3] > 128; ys, xs = np.where(a)
    print("  %d   |   %5.1f | %3d | %d | %d..%d" % (k + 1, lift, ys.min(), clipped, xs.min(), xs.max()))
    out.alpha_composite(fr, (FRAME * k, 0))
out.save(OUT)
Wc, Hc = out.size
pic = Image.new("RGB", (Wc, Hc * 2), (255, 255, 255))
for i, bg in enumerate([(255, 255, 255, 255), (38, 84, 52, 255)]):
    c = Image.new("RGBA", (Wc, Hc), bg); c.alpha_composite(out); pic.paste(c.convert("RGB"), (0, i * Hc))
d = ImageDraw.Draw(pic)
for i in range(2): d.line([(0, i * Hc + GROUND_Y), (Wc, i * Hc + GROUND_Y)], fill=(0, 0, 0) if i == 0 else (255, 255, 255), width=1)
pic.resize((Wc * 2 // 3, Hc * 2 * 2 // 3), Image.LANCZOS).save(CHECK)
print("strip", os.path.abspath(OUT))
