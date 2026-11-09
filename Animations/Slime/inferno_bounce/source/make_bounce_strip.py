#!/usr/bin/env python3
"""Cuts the fire slime's Inferno Bounce sheet (the user's Gemini JPG, 2752 x 1536, eight panels, 4 x 2) into the 8-frame strip (2026-11-08).

  python Animations/Slime/inferno_bounce/source/make_bounce_strip.py

The prompt asked for eight poses ON the floor line (the page lifts the slime itself), but the generator drew three of them in the AIR: panel 3 (the launch: a round ball with a tail of flame hanging below),
panel 4 (the plummet: a teardrop with a long tail of flame above it) and panel 6 (the bounce: a startled tall blob hanging a little above the floor, with a shadow ellipse under it that the prompt had forbidden).
So the cut is the airborne one of ../../magma_slam/source/make_slam_strip.py, generalised: panels 1, 2, 5, 7, 8 are grounded, 3, 4, 6 keep their real height above their row's floor; the height is measured from
the BODY's bottom edge (the lowest row with a long run of dark outline), not from a flame tail. Sizes: ONE scale per row (the panels differ in shape on purpose): row 1 from panel 1 (the rest pose: its base
width = 350 px, the monster standard), row 2 from panel 8 (the settle, nearly the rest pose: 1.02 x 350 px) because the generator draws the bottom row bigger. Every grounded panel is put on its own floor
(the generator did not hold one floor line), the floor of an airborne panel is its row's (the median of its grounded panels), the grounded bases are centred on x 260 and the airborne panels follow between
their grounded neighbours. A flame tail that would cross the bottom of the cell (panel 3's) fades out over the last 30 px instead of being cut. Detached pieces BELOW the body (the forbidden shadow) are dropped.
Output: ../fire_inferno_bounce_8frame_strip.png (512 x 512 per frame), ../fire_inferno_bounce_check.png, ../fire_inferno_bounce_8frame_strip.placement.json and a report.
"""
import os, sys, json
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "inferno_bounce_sheet.jpg")
OUT = os.path.join(HERE, "..", "fire_inferno_bounce_8frame_strip.png")
CHECK = os.path.join(HERE, "..", "fire_inferno_bounce_check.png")
PLACE = os.path.join(HERE, "..", "fire_inferno_bounce_8frame_strip.placement.json")
COLS, ROWS, N = 4, 2, 8
GROUNDED = [0, 1, 4, 6, 7]                     # panels 1, 2, 5, 7, 8 are on the floor; 3, 4 and 6 are in the air
BASE_W, GROUND_Y, BASE_X, FRAME = 350, 470, 260, 512
P8_MUL = 1.02                                  # panel 8 (the settle) against the idle's 350 px base
FADE_FROM = 480                                # a tail of flame crossing the bottom of the cell fades out from here to the edge

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

panels, boxes, bws, lows, bodybot = [], [], [], [], []
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
        if j != keep and sizes[j - 1] >= 60 and dist[lab == j].min() <= reach and np.where(lab == j)[0].max() <= my.max():   # (a piece lower than the main piece's bottom, such as the forbidden shadow ellipse under panel 6, is dropped)
            jy, jx = np.where(lab == j)
            if jx.min() <= 14 or jx.max() >= p.shape[1] - 15 or jy.min() <= 14 or jy.max() >= p.shape[0] - 15:     # (a piece cut by the panel border, a droplet of the next panel's splat, is dropped too)
                continue
            kept |= ndi.binary_dilation(lab == j, iterations=3)
    p[..., 3] = np.where(kept, p[..., 3], 0)
    ys, xs = np.where(p[..., 3] > 128)
    boxes.append((xs.min(), ys.min(), xs.max(), ys.max()))
    y0, y1 = my.min(), my.max()
    bws.append(max(mx[my == y].max() - mx[my == y].min() for y in range(int(y1 - 0.22 * (y1 - y0)), y1 + 1) if (my == y).any()))
    lows.append(int(y1))
    lum = p[..., :3].astype(float) @ np.array([.299, .587, .114])
    dark = (p[..., 3] > 128) & (lum < 80)
    rws = np.where(dark.sum(1) >= 40)[0]
    bodybot.append(int(rws.max()) if len(rws) else int(y1))
    panels.append(p)

s1 = BASE_W / float(bws[0])
s2 = BASE_W * P8_MUL / float(bws[7])
sk = [s1 if k < COLS else s2 for k in range(N)]
ground = {}
for rr in range(ROWS):
    ground[rr] = float(np.median([bodybot[k] for k in GROUNDED if k // COLS == rr]))
def base_mid(k):
    y1 = bodybot[k]; y0 = boxes[k][1]
    xs = np.where((panels[k][int(y1 - 0.06 * (y1 - y0)):y1 + 1, :, 3] > 128).any(0))[0]
    return (xs.min() + xs.max()) / 2.0
sh = {k: BASE_X - base_mid(k) * sk[k] for k in GROUNDED}
shifts = {}
for k in range(N):
    before = [q for q in GROUNDED if q <= k]; after = [q for q in GROUNDED if q >= k]
    if k in sh: shifts[k] = sh[k]
    else: shifts[k] = sh[before[-1]] + (sh[after[0]] - sh[before[-1]]) * (k - before[-1]) / float(after[0] - before[-1])

out = Image.new("RGBA", (FRAME * N, FRAME), (0, 0, 0, 0))
print("scale row 1 %.4f, row 2 %.4f; base widths in the sheet %s; body bottoms %s; floors %s" % (s1, s2, [int(v) for v in bws], bodybot, {k: int(v) for k, v in ground.items()}))
print("panel | body lift above the floor (px) | base/body width (px) | figure top y | figure bottom y | faded px | x range")
info = []
for k, p in enumerate(panels):
    im = Image.fromarray(p).resize((int(p.shape[1] * sk[k]), int(p.shape[0] * sk[k])), Image.LANCZOS)
    if k in GROUNDED:                                        # a grounded panel stands on its own floor
        ox = int(round(shifts[k])); oy = int(round(GROUND_Y - bodybot[k] * sk[k])); lift = 0.0
    else:                                                    # an airborne panel keeps its real height above its row's floor
        fl = ground[k // COLS]; ox = int(round(shifts[k])); oy = int(round(GROUND_Y - fl * sk[k])); lift = max(0.0, (fl - bodybot[k]) * sk[k])
    canvas = Image.new("RGBA", (FRAME + 3000, FRAME + 3000), (0, 0, 0, 0)); canvas.alpha_composite(im, (1500 + ox, 1500 + oy))
    fr = canvas.crop((1500, 1500, 1500 + FRAME, 1500 + FRAME))
    arr = np.array(fr)
    a = arr[..., 3] > 128; ys, xs = np.where(a)
    faded = 0
    full_bottom = int((np.array(canvas)[1500:1500 + 3000, 1500:1500 + FRAME, 3] > 128).any(1).nonzero()[0].max()) if True else 0
    if ys.max() >= FRAME - 6 or full_bottom > FRAME - 6:       # the figure reaches the bottom of the cell: fade its lowest part out instead of cutting it
        ramp = np.clip((FRAME - 1 - np.arange(FRAME)) / float(FRAME - 1 - FADE_FROM), 0, 1)
        arr[..., 3] = (arr[..., 3] * ramp[:, None]).astype(np.uint8); faded = int((a & (np.arange(FRAME)[:, None] > FADE_FROM)).sum())
        fr = Image.fromarray(arr); a = arr[..., 3] > 128; ys, xs = np.where(a)
    print("  %d   |   %5.1f | %5.1f | %3d | %3d | %d | %d..%d" % (k + 1, lift, bws[k] * sk[k], ys.min(), ys.max(), faded, xs.min(), xs.max()))
    out.alpha_composite(fr, (FRAME * k, 0))
    info.append({"lift": round(lift, 1), "top": int(ys.min()), "bottom": int(ys.max()), "baseW": round(float(bws[k] * sk[k]), 1), "bodyBottomY": int(round(GROUND_Y - lift))})
out.save(OUT)
json.dump({"format": "frame-placement/1", "animation": "inferno_bounce", "file": "fire_inferno_bounce_8frame_strip.png", "frames": N, "fps": 12, "hitFrame": 5, "frameInfo": info,
           "note": "frames: 1 rest, 2 crouch, 3 launch (a ball with a tail of flame below it, in the air), 4 plummet (a teardrop, flames streaming up), 5 CRASH (the hit frame), 6 bounce (startled, a little above the floor), 7 heavy landing, 8 settle. The page lifts and drops the unit itself; lift = body height above the floor in the cell."},
          open(PLACE, "w"), indent=1)
W, H = out.size
pic = Image.new("RGB", (W, H * 2), (255, 255, 255))
for i, bg in enumerate([(255, 255, 255, 255), (38, 84, 52, 255)]):
    c = Image.new("RGBA", (W, H), bg); c.alpha_composite(out); pic.paste(c.convert("RGB"), (0, i * H))
d = ImageDraw.Draw(pic)
for i in range(2): d.line([(0, i * H + GROUND_Y), (W, i * H + GROUND_Y)], fill=(0, 0, 0) if i == 0 else (255, 255, 255), width=1)
pic.resize((W // 2, H), Image.LANCZOS).save(CHECK)
print("strip", os.path.abspath(OUT))
