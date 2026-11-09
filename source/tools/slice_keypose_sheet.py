#!/usr/bin/env python3
"""Turns a generated key-pose sheet (N equal panels in one row on a flat magenta
background) into a transparent 512x512-per-frame strip, the same way the attack
and death strips in ../assets were made.

Steps: remove magenta (soft alpha + despill), keep the largest blob per panel,
scale ALL panels with one shared scale, then place each panel on the 512 frame
with its lowest point on the ground line (y=470).

Alignment modes (one per panel, comma separated):
  toe    front-most foot tip goes to --toe-x   (attack: the front foot stays planted)
  feet   centre of the lowest 10% goes to --feet-x   (standing / falling poses)
  center bounding-box centre goes to x=256   (lying poses)
  heel   left-most point of the lowest 8% (rear heel) goes to --heel-x   (idle cycles: planted feet)

Example (attack, matching the idle strip's front toe at x=336):
  python slice_keypose_sheet.py attack_sheet.png attack_strip.png --panels 3 \
      --panel1-height 408 --modes toe,toe,toe --toe-x 336
Example (death):
  python slice_keypose_sheet.py death_sheet.png death_strip.png --panels 3 \
      --panel1-height 395 --modes feet,feet,center --feet-x 248

Example (idle, a 3 columns x 2 rows sheet, 6 frames, shared scale = median height of all frames):
  python slice_keypose_sheet.py idle_sheet.png idle_strip.png --cols 3 --rows 2 \
      --height 408 --scale-from median --modes heel --heel-x 160

Example (a monster with crisp flames, embers and smoke, e.g. the fire slime; added 2026-11-07):
  python slice_keypose_sheet.py slime_idle_sheet.png slime_idle_strip.png --cols 3 --rows 2 \
      --base-width 350 --scale-from median --keep-near 0.25 --modes feet --feet-x 256 \
      --despill-band 10 --despill-thr 4
  --base-width sizes by the width of the base (flames of different heights cannot resize the body);
  --keep-near keeps the embers and puffs that float near the body.

Needs:  pip install pillow numpy scipy
"""
import argparse
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

ap = argparse.ArgumentParser()
ap.add_argument("src"); ap.add_argument("dst")
ap.add_argument("--panels", type=int, default=3, help="panels in ONE row (ignored when --cols/--rows are given)")
ap.add_argument("--count", type=int, default=0, help="use only the first N panels of the grid (a sheet with empty slots at the end)")
ap.add_argument("--cols", type=int, default=0)
ap.add_argument("--rows", type=int, default=0)
ap.add_argument("--panel1-height", "--height", dest="panel1_height", type=float, default=408, help="pixel height the character should have (sets the shared scale)")
ap.add_argument("--scale-from", choices=["panel1", "median"], default="panel1")
ap.add_argument("--heel-x", type=float, default=160)
ap.add_argument("--modes", default="toe,toe,toe")
ap.add_argument("--toe-x", default="336", help="x of the front toe in toe mode; one number, or a comma list with one per panel (the last one repeats)")
ap.add_argument("--feet-x", type=float, default=248)
ap.add_argument("--frame", type=int, default=512)
ap.add_argument("--ground", type=int, default=470)
ap.add_argument("--fit", default="", help="panels (1-based, comma separated) that are full-height standing poses: each is scaled on its own to exactly --height, so a clip that ends in the idle stance ends the same size as the idle")
ap.add_argument("--scale-mult", default="", help="per-panel size correction, comma separated (1 = unchanged), for sheets where the generator drew some panels bigger or smaller than the rest: e.g. 1,1,1.17,0.82,0.8,0.93 (measure the face or boots in the cut strip to find the numbers)")
ap.add_argument("--despill-band", type=int, default=3, help="px from the silhouette in which leftover magenta is pulled out (raise it when the sheet has a purple glow around the outline)")
ap.add_argument("--despill-thr", type=float, default=12, help="how far red and blue may exceed green inside that band (lower = stricter)")
# --- options for monsters with loose crisp effects (a slime's embers and smoke), added 2026-11-07; the defaults change nothing ---
ap.add_argument("--keep-near", type=float, default=0, help="also keep detached pieces (embers, sparks, smoke puffs) whose gap to the main body is at most this share of the main body's height (0 = keep only the biggest piece, the old behaviour; try 0.25)")
ap.add_argument("--min-piece", type=int, default=60, help="with --keep-near: ignore detached pieces smaller than this many pixels (dust)")
ap.add_argument("--base-width", type=float, default=0, help="size by the WIDTH OF THE BASE instead of the figure's height: the shared scale makes the median (or panel 1's) base width this many px (e.g. 350 for a slime in the 512 cell); flames and smoke of different heights then cannot resize the body. 0 = off. The base width is printed for every panel")
ap.add_argument("--base-band", type=float, default=0.22, help="with --base-width: the base is measured over the lowest this share of the figure's height (widest row of the main body in that band)")
ap.add_argument("--fit-base", default="", help="with --base-width: panels (1-based) that are each scaled on their own to exactly --base-width (a clip that must end at the idle's size)")
a = ap.parse_args()
modes = a.modes.split(",")
toe_xs = [float(x) for x in str(a.toe_x).split(",")]

img = np.array(Image.open(a.src).convert("RGB")).astype(float)
r, g, b = img[..., 0], img[..., 1], img[..., 2]
alpha = 1 - np.clip((np.minimum(r, b) - g - 70) / 110, 0, 1)          # magenta -> transparent
soft = alpha < 1
rgb = img.copy()
rgb[..., 0] = np.where(soft, np.minimum(r, g + 25), r)                  # despill the pink fringe
rgb[..., 2] = np.where(soft, np.minimum(b, g + 25), b)
# Extra despill: within --despill-band px of the silhouette (and in the semi-transparent edge pixels), any pixel
# where BOTH red and blue exceed green is magenta leaking into the outline, so pull red and blue down to just above green.
band = ndi.binary_dilation(alpha < 0.5, iterations=a.despill_band) & (alpha >= 0.5)
mm = np.minimum(rgb[..., 0], rgb[..., 2]) - rgb[..., 1]
fix = (band | soft) & (mm > a.despill_thr)
rgb[..., 0] = np.where(fix, np.minimum(rgb[..., 0], rgb[..., 1] + a.despill_thr), rgb[..., 0])
rgb[..., 2] = np.where(fix, np.minimum(rgb[..., 2], rgb[..., 1] + a.despill_thr), rgb[..., 2])
rgba = np.dstack([rgb, alpha * 255]).astype(np.uint8)

cols = a.cols or a.panels
rows = a.rows or 1
a.panels = cols * rows
if a.count:
    a.panels = min(a.panels, a.count)
W = rgba.shape[1] // cols
Hh = rgba.shape[0] // rows
panels = []
base_ws = []
for k in range(a.panels):
    r_, c_ = divmod(k, cols)
    p = rgba[r_ * Hh:(r_ + 1) * Hh, c_ * W:(c_ + 1) * W].copy()
    solid = p[..., 3] > 128
    lab, n = ndi.label(solid)
    sizes = ndi.sum(solid, lab, range(1, n + 1))
    keep = 1 + int(np.argmax(sizes))                                    # drop dust, keep the character
    main = lab == keep
    kept = ndi.binary_dilation(main, iterations=3)
    if a.keep_near > 0:                                                  # loose embers / sparks / smoke puffs close to the body stay
        my, mx = np.where(main)
        reach = a.keep_near * (my.max() - my.min())
        dist = ndi.distance_transform_edt(~main)
        nk = 0
        for j in range(1, n + 1):
            if j == keep or sizes[j - 1] < a.min_piece:
                continue
            comp = lab == j
            if dist[comp].min() <= reach:
                kept |= ndi.binary_dilation(comp, iterations=3)
                nk += 1
        print("panel", k + 1, "loose pieces kept:", nk, "of", n - 1)
    p[..., 3] = np.where(kept, p[..., 3], 0)
    my, mx = np.where(main)                                             # base width: widest row of the main body in its lowest band
    y_lo, y_hi = my.min(), my.max()
    band = np.arange(int(y_hi - a.base_band * (y_hi - y_lo)), y_hi + 1)
    base_ws.append(max((mx[my == yy].max() - mx[my == yy].min()) for yy in band if (my == yy).any()))
    panels.append(p)

def bbox(p):
    ys, xs = np.where(p[..., 3] > 128)
    return xs.min(), ys.min(), xs.max(), ys.max()

hs = [bbox(p)[3] - bbox(p)[1] for p in panels]
if a.base_width:
    print("base widths (px in the sheet):", [int(v) for v in base_ws])
    ref_w = base_ws[0] if a.scale_from == "panel1" else float(np.median(base_ws))
    scale = a.base_width / ref_w
else:
    scale = a.panel1_height / (hs[0] if a.scale_from == "panel1" else float(np.median(hs)))
fit = [int(x) - 1 for x in a.fit.split(",") if x.strip()]
fit_base = [int(x) - 1 for x in a.fit_base.split(",") if x.strip()]
mult = [float(x) for x in a.scale_mult.split(",") if x.strip()]
out = Image.new("RGBA", (a.frame * a.panels, a.frame), (0, 0, 0, 0))
for k, p in enumerate(panels):
    x0, y0, x1, y1 = bbox(p)
    sc = (a.base_width / base_ws[k] if (a.base_width and k in fit_base) else (a.panel1_height / hs[k] if k in fit else scale)) * (mult[k] if k < len(mult) else 1)
    im = Image.fromarray(p).resize((int(p.shape[1] * sc), int(p.shape[0] * sc)), Image.LANCZOS)
    mode = modes[min(k, len(modes) - 1)]
    low = p[int(y1 - (0.08 if mode == "heel" else 0.10) * (y1 - y0)):y1 + 1, :, 3] > 128
    lx = np.where(low.any(0))[0]
    if mode == "heel":
        ox = a.heel_x - lx.min() * sc
    elif mode == "toe":
        ox = toe_xs[min(k, len(toe_xs) - 1)] - lx.max() * sc
    elif mode == "feet":
        ox = a.feet_x - (lx.min() + lx.max()) / 2 * sc
    else:
        ox = a.frame / 2 - (x0 + x1) / 2 * sc
    oy = a.ground - y1 * sc
    canvas = Image.new("RGBA", (3000, 3000), (0, 0, 0, 0))
    canvas.alpha_composite(im, (1000 + int(round(ox)), 1000 + int(round(oy))))
    frame = canvas.crop((1000, 1000, 1000 + a.frame, 1000 + a.frame))
    clipped = int((np.array(im)[..., 3] > 128).sum() - (np.array(frame)[..., 3] > 128).sum())
    print("panel", k + 1, mode, "clipped pixels:", clipped)
    out.alpha_composite(frame, (a.frame * k, 0))
out.save(a.dst)
print("scale", round(scale, 4), "->", a.dst)
