#!/usr/bin/env python3
"""Cuts the fire slime's Magma Slam sheet (the user's Gemini JPG, 2752 x 1536, eight panels, 4 x 2) into the 8-frame airborne strip (2026-11-08).

  python Animations/Slime/magma_slam/source/make_slam_strip.py

An airborne cut like ../../dodge/source/make_dodge_strip.py (every frame keeps its real height above the floor; slice_keypose_sheet.py would push the airborne frames onto the ground, and
equalize_sheet.py would too), generalised to 4 x 2 with panels 1, 2, 7 and 8 on the floor and 3 to 6 in the air. What is new here: in the airborne panels the flames stream DOWN below the body, so the lowest
pixel of a frame is a flame tail, not the body; the height above the floor is measured from the BODY's bottom edge instead: the lowest row where the body's dark outline has a long horizontal run
(a flame tail has no such run). One scale from panel 1's base width (350 px, the monster standard), a correction for the second row from panel 8 (the rebound, nearly the rest pose again), the floor line
of each row from its grounded panels, the grounded bases centred on x 260 (the idle's base centre) and the airborne panels interpolated between their grounded neighbours (the page moves the slime
along a path, the art stays over one spot). Output: ../fire_magma_slam_8frame_strip.png (512 x 512 per frame) and ../fire_magma_slam_check.png, and a report.
"""
import os, sys
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "magma_slam_sheet.jpg")
OUT = os.path.join(HERE, "..", "fire_magma_slam_8frame_strip.png")
CHECK = os.path.join(HERE, "..", "fire_magma_slam_check.png")
COLS, ROWS, N = 4, 2, 8
GROUNDED = [0, 1, 6, 7]                    # panels 1, 2, 7, 8 are on the floor; 3 to 6 are in the air
BASE_W, GROUND_Y, BASE_X, FRAME = 350, 470, 260, 512

img = np.array(Image.open(SRC).convert("RGB")).astype(float)
r, g, b = img[..., 0], img[..., 1], img[..., 2]
alpha = 1 - np.clip((np.minimum(r, b) - g - 70) / 110, 0, 1)
soft = alpha < 1
rgb = img.copy()
rgb[..., 0] = np.where(soft, np.minimum(r, g + 25), r); rgb[..., 2] = np.where(soft, np.minimum(b, g + 25), b)
band = ndi.binary_dilation(alpha < 0.5, iterations=10) & (alpha >= 0.5)
mm = np.minimum(rgb[..., 0], rgb[..., 2]) - rgb[..., 1]
fix = (band | soft) & (mm > 4)
rgb[..., 0] = np.where(fix, np.minimum(rgb[..., 0], rgb[..., 1] + 4), rgb[..., 0]); rgb[..., 2] = np.where(fix, np.minimum(rgb[..., 2], rgb[..., 1] + 4), rgb[..., 2])
rgba = np.dstack([rgb, alpha * 255]).astype(np.uint8)
PW, PH = rgba.shape[1] // COLS, rgba.shape[0] // ROWS
for c in range(0, COLS + 1):                                   # clear 10 px on both sides of every panel border and the image edge (grid lines, if a sheet has them)
    x = min(c * PW, rgba.shape[1]); rgba[:, max(0, x - 10):x + 10, 3] = 0
for r_ in range(0, ROWS + 1):
    y = min(r_ * PH, rgba.shape[0]); rgba[max(0, y - 10):y + 10, :, 3] = 0

panels, boxes, bws, bodybot = [], [], [], []
for k in range(N):
    rr, cc = divmod(k, COLS)
    p = rgba[rr * PH:(rr + 1) * PH, cc * PW:(cc + 1) * PW].copy()
    solid = p[..., 3] > 128
    lab, n = ndi.label(solid); sizes = ndi.sum(solid, lab, range(1, n + 1))
    keep = 1 + int(np.argmax(sizes)); main = lab == keep
    my, mx = np.where(main); reach = 0.25 * (my.max() - my.min())
    dist = ndi.distance_transform_edt(~main)
    kept = ndi.binary_dilation(main, iterations=3)
    for j in range(1, n + 1):
        if j != keep and sizes[j - 1] >= 60 and dist[lab == j].min() <= reach:
            kept |= ndi.binary_dilation(lab == j, iterations=3)
    p[..., 3] = np.where(kept, p[..., 3], 0)
    ys, xs = np.where(p[..., 3] > 128)
    boxes.append((xs.min(), ys.min(), xs.max(), ys.max()))
    y0, y1 = my.min(), my.max()
    bws.append(max(mx[my == y].max() - mx[my == y].min() for y in range(int(y1 - 0.22 * (y1 - y0)), y1 + 1) if (my == y).any()))
    # the body's bottom edge: the lowest row with a long run of dark outline pixels (flame tails and droplets do not make one)
    lum = p[..., :3].astype(float) @ np.array([.299, .587, .114])
    dark = (p[..., 3] > 128) & (lum < 80)
    runs = dark.sum(1)
    rows = np.where(runs >= 40)[0]
    bodybot.append(int(rows.max()) if len(rows) else int(boxes[-1][3]))
    panels.append(p)

scale = BASE_W / float(bws[0])
row_fix = {0: 1.0, 1: bws[0] / float(bws[7])}               # panel 8 is nearly the rest pose again: the second row is corrected so that it has panel 1's base width
sk = [scale * row_fix[k // COLS] for k in range(N)]
ground = {}
for rr in range(ROWS):
    ground[rr] = float(np.median([boxes[k][3] for k in GROUNDED if k // COLS == rr]))
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
print("scale %.4f, second row x %.3f; base widths in the sheet %s; body bottoms %s; floors %s" % (scale, row_fix[1], [int(v) for v in bws], bodybot, {k: int(v) for k, v in ground.items()}))
print("panel | body lift above the floor (px, in the 512 cell) | figure top y | lowest flame/droplet below the floor (px) | clipped px | x range")
for k, p in enumerate(panels):
    im = Image.fromarray(p).resize((int(p.shape[1] * sk[k]), int(p.shape[0] * sk[k])), Image.LANCZOS)
    fl = ground[k // COLS]
    lift = 0.0 if k in GROUNDED else max(0.0, (fl - bodybot[k]) * sk[k])
    below = max(0.0, (boxes[k][3] - fl) * sk[k])
    ox = int(round(shifts[k])); oy = int(round(GROUND_Y - fl * sk[k]))                     # the panel's own floor goes on y 470; an airborne figure is already at its real height inside its panel (do NOT add the lift again)
    canvas = Image.new("RGBA", (FRAME + 3000, FRAME + 3000), (0, 0, 0, 0)); canvas.alpha_composite(im, (1500 + ox, 1500 + oy))
    fr = canvas.crop((1500, 1500, 1500 + FRAME, 1500 + FRAME))
    clipped = int((np.array(im)[..., 3] > 128).sum() - (np.array(fr)[..., 3] > 128).sum())
    a = np.array(fr)[..., 3] > 128; ys, xs = np.where(a)
    print("  %d   |   %5.1f | %3d | %4.1f | %d | %d..%d" % (k + 1, lift, ys.min(), below, clipped, xs.min(), xs.max()))
    out.alpha_composite(fr, (FRAME * k, 0))
out.save(OUT)
W, H = out.size
pic = Image.new("RGB", (W, H * 2), (255, 255, 255))
for i, bg in enumerate([(255, 255, 255, 255), (38, 84, 52, 255)]):
    c = Image.new("RGBA", (W, H), bg); c.alpha_composite(out); pic.paste(c.convert("RGB"), (0, i * H))
d = ImageDraw.Draw(pic)
for i in range(2): d.line([(0, i * H + GROUND_Y), (W, i * H + GROUND_Y)], fill=(0, 0, 0) if i == 0 else (255, 255, 255), width=1)
pic.resize((W // 2, H), Image.LANCZOS).save(CHECK)
print("strip", os.path.abspath(OUT))
