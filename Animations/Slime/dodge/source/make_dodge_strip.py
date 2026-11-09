#!/usr/bin/env python3
"""Cuts the fire slime's Dodge sheet (the user's ChatGPT PNG, 1536 x 1024, six 512 px panels, 3 x 2) into the 6-frame strip (2026-11-08).

  python Animations/Slime/dodge/source/make_dodge_strip.py chatgpt      (dodge_sheet.png: the user's ChatGPT sheet, 1536 x 1024)
  python Animations/Slime/dodge/source/make_dodge_strip.py gemini       (dodge_sheet_gemini.jpg: the user's second, Gemini sheet, 2752 x 1536, with black grid lines between its panels)

Why not the usual cutters: the hop must keep its real height above the floor (slice_keypose_sheet.py would push every frame down onto the ground), and slice_airborne_sheet.py sizes by the figure's
height, which the flames change. This script keys each panel like the other cutters (magenta -> alpha, despill, the biggest piece plus the embers and flames detached within 25% of its height),
measures the base width of the GROUNDED panels (1, 2, 5, 6), scales all panels with ONE scale (panel 1's base width -> 350 px, the monster standard) times a per-row correction (panel 6 is the
same rest pose as panel 1, so the second row is corrected by their ratio), puts the floor line of each row (the median lowest point of its grounded panels) on y = 470 of the 512 cell,
keeps every airborne panel at its real height above that line, and centres the base of the grounded panels on x = 260 (the idle's base centre); the airborne panels follow smoothly between their
grounded neighbours (the generator wobbles sideways; the page moves the slime along a path anyway).
Output: gemini -> ../fire_dodge_6frame_strip.png (the official strip, 512 x 512 per frame) and ../fire_dodge_check.png; chatgpt -> ../alternatives/fire_dodge_chatgpt_6frame_strip.png and its check; and a report.
"""
import os, sys
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi

HERE = os.path.dirname(os.path.abspath(__file__))
# The shipped strips were cut with the lift counted twice (the airborne panel is already at its real height; the lift was also measured from the lowest pixel, flame tails included): the body hops about 66 px / 175 px
# (take-off / apex; a rough measure) instead of the drawn 26 / 52. True reproduces the shipped strips; False gives the heights as drawn (found 2026-11-08, docs/MONSTERS.md).
LEGACY_DOUBLE_LIFT = True
VARIANT = sys.argv[1] if len(sys.argv) > 1 else "chatgpt"
SRC = os.path.join(HERE, {"chatgpt": "dodge_sheet.png", "gemini": "dodge_sheet_gemini.jpg"}[VARIANT])
# the OFFICIAL dodge is the Gemini sheet's (2026-11-08: it matches the idle's rendering better); the ChatGPT one is kept in ../alternatives/
OUTDIR = os.path.join(HERE, "..") if VARIANT == "gemini" else os.path.join(HERE, "..", "alternatives")
os.makedirs(OUTDIR, exist_ok=True)
OUT = os.path.join(OUTDIR, "fire_dodge_6frame_strip.png" if VARIANT == "gemini" else "fire_dodge_chatgpt_6frame_strip.png")
CHECK = os.path.join(OUTDIR, "fire_dodge_check.png" if VARIANT == "gemini" else "fire_dodge_chatgpt_check.png")
COLS, ROWS, N = 3, 2, 6
GROUNDED = [0, 1, 4, 5]                    # panels 1, 2, 5, 6 rest on the floor; 3 and 4 are in the air
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
# the Gemini sheet has black grid lines on the panel borders and round the image although the prompt said none: clear 10 px on both sides of every border (no creature comes that close)
for c in list(range(0, COLS + 1)):
    x = min(c * PW, rgba.shape[1]); rgba[:, max(0, x - 10):x + 10, 3] = 0
for r_ in list(range(0, ROWS + 1)):
    y = min(r_ * PH, rgba.shape[0]); rgba[max(0, y - 10):y + 10, :, 3] = 0

panels, boxes, bws = [], [], []
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
    panels.append(p)

scale = BASE_W / float(bws[0])
row_fix = {0: 1.0, 1: bws[0] / float(bws[5])}               # panel 6 is the rest pose again: the second row is corrected so that it has panel 1's base width
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
print("scale %.4f, second row x %.3f; base widths in the sheet %s" % (scale, row_fix[1], [int(v) for v in bws]))
print("panel | lift above the floor (px, in the 512 cell) | figure top y | clipped px | base mid x shift")
for k, p in enumerate(panels):
    im = Image.fromarray(p).resize((int(p.shape[1] * sk[k]), int(p.shape[0] * sk[k])), Image.LANCZOS)
    lift = max(0.0, (ground[k // COLS] - boxes[k][3]) * sk[k]) if k not in GROUNDED else 0.0
    ox = int(round(shifts[k])); oy = int(round(GROUND_Y - ground[k // COLS] * sk[k] - (lift if LEGACY_DOUBLE_LIFT else 0)))
    canvas = Image.new("RGBA", (FRAME + 3000, FRAME + 3000), (0, 0, 0, 0)); canvas.alpha_composite(im, (1500 + ox, 1500 + oy))
    fr = canvas.crop((1500, 1500, 1500 + FRAME, 1500 + FRAME))
    clipped = int((np.array(im)[..., 3] > 128).sum() - (np.array(fr)[..., 3] > 128).sum())
    a = np.array(fr)[..., 3] > 128; ys, xs = np.where(a)
    print("  %d   |   %5.1f | %3d | %d | %d..%d" % (k + 1, lift, ys.min(), clipped, xs.min(), xs.max()))
    out.alpha_composite(fr, (FRAME * k, 0))
out.save(OUT)
W, H = out.size
pic = Image.new("RGB", (W, H * 2), (255, 255, 255))
for i, bg in enumerate([(255, 255, 255, 255), (38, 84, 52, 255)]):
    c = Image.new("RGBA", (W, H), bg); c.alpha_composite(out); pic.paste(c.convert("RGB"), (0, i * H))
d = ImageDraw.Draw(pic)
for i in range(2): d.line([(0, i * H + GROUND_Y), (W, i * H + GROUND_Y)], fill=(0, 0, 0) if i == 0 else (255, 255, 255), width=1)
pic.resize((W * 2 // 3, H * 2 * 2 // 3), Image.LANCZOS).save(CHECK)
print("strip", os.path.abspath(OUT))
