#!/usr/bin/env python3
"""Cuts the fire slime's Magma Eruption sheet (the user's Gemini JPG, 2752 x 1536, six panels, 3 x 2) into the 6-frame strip (2026-11-08).

  python Animations/Slime/magma_eruption/source/make_eruption_strip.py

The panels are NOT one size on purpose (the slime shrinks from panel 1 to the tiny core of panel 4 and swells back in 5 and 6), so there is no per-panel size correction: ONE scale per row.
  - Row 1 (panels 1 to 3): panel 1 is the rest pose breathing in, so its base width is set to 1.03 x 350 px (the monster standard 350 px is the idle's base width), the other panels of the row follow
    with the same scale.
  - Row 2 (panels 4 to 6): the generator draws the bottom row bigger, so the row gets its own scale from panel 6, the swelled slime that goes into the idle again: its base width is set to 0.97 x 350 px.
  - Every panel rests on its OWN floor (the generator did not hold one floor line across the panels): the lowest point of the body goes on y = 470 of the 512 cell, the base centre on x = 260.
Same keying as the other cutters (magenta -> alpha, despill, the biggest piece plus detached embers within 25% of its height), the grid lines (there are none on this sheet) cleared 10 px at every border.
Output: ../fire_magma_eruption_6frame_strip.png (512 x 512 per frame), ../fire_magma_eruption_check.png, ../fire_magma_eruption_6frame_strip.placement.json (the size of each frame against the idle, the
core's centre on frame 4 for the page's lava trail and ember) and a report.
"""
import os, sys, json
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "magma_eruption_sheet.jpg")
OUT = os.path.join(HERE, "..", "fire_magma_eruption_6frame_strip.png")
CHECK = os.path.join(HERE, "..", "fire_magma_eruption_check.png")
PLACE = os.path.join(HERE, "..", "fire_magma_eruption_6frame_strip.placement.json")
COLS, ROWS, N = 3, 2, 6
BASE_W, GROUND_Y, BASE_X, FRAME = 350, 470, 260, 512
P1_MUL, P6_MUL = 1.03, 0.97                  # panel 1 (breathing in) and panel 6 (nearly the rest pose) against the idle's 350 px base

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
for c in range(0, COLS + 1):
    x = min(c * PW, rgba.shape[1]); rgba[:, max(0, x - 10):x + 10, 3] = 0
for r_ in range(0, ROWS + 1):
    y = min(r_ * PH, rgba.shape[0]); rgba[max(0, y - 10):y + 10, :, 3] = 0

panels, boxes, bws, lows = [], [], [], []
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
        if j != keep and sizes[j - 1] >= 60 and dist[lab == j].min() <= reach and np.where(lab == j)[0].max() <= my.max():   # (a speck lower than the body's bottom is dropped: embers float ABOVE it)
            kept |= ndi.binary_dilation(lab == j, iterations=3)
    p[..., 3] = np.where(kept, p[..., 3], 0)
    ys, xs = np.where(p[..., 3] > 128)
    boxes.append((xs.min(), ys.min(), xs.max(), ys.max()))
    y0, y1 = my.min(), my.max()
    bws.append(max(mx[my == y].max() - mx[my == y].min() for y in range(int(y1 - 0.22 * (y1 - y0)), y1 + 1) if (my == y).any()))
    lows.append(int(y1))                                                        # the body's lowest row (the biggest piece only: detached embers float above it)
    panels.append(p)

s1 = BASE_W * P1_MUL / float(bws[0])
s6 = BASE_W * P6_MUL / float(bws[5])
sk = [s1, s1, s1, s6, s6, s6]
def base_mid(k):
    y1 = lows[k]; y0 = boxes[k][1]
    xs = np.where((panels[k][int(y1 - 0.06 * (y1 - y0)):y1 + 1, :, 3] > 128).any(0))[0]
    return (xs.min() + xs.max()) / 2.0

out = Image.new("RGBA", (FRAME * N, FRAME), (0, 0, 0, 0))
print("scale row 1 %.4f, row 2 %.4f; base widths in the sheet %s; lowest rows %s" % (s1, s6, [int(v) for v in bws], lows))
print("panel | base width in the cell (px) | against the idle's 350 | figure top y | figure height | clipped px | x range")
sizes_rel, info = [], []
for k, p in enumerate(panels):
    im = Image.fromarray(p).resize((int(p.shape[1] * sk[k]), int(p.shape[0] * sk[k])), Image.LANCZOS)
    ox = int(round(BASE_X - base_mid(k) * sk[k])); oy = int(round(GROUND_Y - lows[k] * sk[k]))
    canvas = Image.new("RGBA", (FRAME + 3000, FRAME + 3000), (0, 0, 0, 0)); canvas.alpha_composite(im, (1500 + ox, 1500 + oy))
    fr = canvas.crop((1500, 1500, 1500 + FRAME, 1500 + FRAME))
    clipped = int((np.array(im)[..., 3] > 128).sum() - (np.array(fr)[..., 3] > 128).sum())
    a = np.array(fr)[..., 3] > 128; ys, xs = np.where(a)
    bw = bws[k] * sk[k]; rel = bw / BASE_W; sizes_rel.append(round(rel, 3))
    print("  %d   |   %5.1f | %.2f | %3d | %3d | %d | %d..%d" % (k + 1, bw, rel, ys.min(), ys.max() - ys.min(), clipped, xs.min(), xs.max()))
    out.alpha_composite(fr, (FRAME * k, 0))
    # the body's centre on this frame (bbox of the main body, flames included only up to the body: use the lower 70% of the figure)
    top = ys.min(); bot = ys.max(); yy = np.where(a[int(top + 0.3 * (bot - top)):bot + 1].any(1))[0]
    cols = np.where(a[int(top + 0.3 * (bot - top)):bot + 1].any(0))[0]
    info.append({"x": round(float((cols.min() + cols.max()) / 2.0), 1), "bottom": int(bot), "top": int(top), "bodyW": round(float(cols.max() - cols.min()), 1)})
out.save(OUT)
json.dump({"format": "frame-placement/1", "animation": "magma_eruption", "file": "fire_magma_eruption_6frame_strip.png", "frames": N, "fps": 12,
           "sizeAgainstIdle": sizes_rel, "frameInfo": info, "slideFrame": 4, "note": "frame sizes by base width against the idle's 350 px; frame 4 (index 3) is the tiny core the page slides; the shrink plays frames 1 to 4, the re-forming plays 4, 3, 5, 6 (the generator drew frame 5 almost full size)"},
          open(PLACE, "w"), indent=1)
W, H = out.size
pic = Image.new("RGB", (W, H * 2), (255, 255, 255))
for i, bg in enumerate([(255, 255, 255, 255), (38, 84, 52, 255)]):
    c = Image.new("RGBA", (W, H), bg); c.alpha_composite(out); pic.paste(c.convert("RGB"), (0, i * H))
d = ImageDraw.Draw(pic)
for i in range(2): d.line([(0, i * H + GROUND_Y), (W, i * H + GROUND_Y)], fill=(0, 0, 0) if i == 0 else (255, 255, 255), width=1)
pic.resize((W // 2, H), Image.LANCZOS).save(CHECK)
print("strip", os.path.abspath(OUT))
