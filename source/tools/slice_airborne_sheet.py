#!/usr/bin/env python3
"""Like slice_keypose_sheet.py, but for sheets where the character LEAVES the ground (jumps).
Each frame keeps its real height above the ground instead of being pushed down onto it.

How it works
- magenta removal + despill + largest blob per panel (same as the other script)
- one shared scale: the average height of the --standing panels is scaled to --height px
- the ground of each panel row = the median lowest point of the --grounded panels in that row
  (the generator does not keep the ground line identical between rows)
- horizontal position is the position drawn in the sheet, shifted so --ref-panel's front toe lands on --toe-x
- the output frame is 512 wide and --out-height tall, with the ground line --ground-from-bottom px above the
  bottom edge (42 = the same ground line as the 512x512 strips, so the character stays the same size and
  the extra height is just headroom for the jump)

  python slice_airborne_sheet.py jump_sheet.png jump_strip.png --cols 4 --rows 2 \
      --grounded 1,2,3,7,8 --standing 1,8 --ref-panel 1 --height 408 --toe-x 336 --lift-scale 2.0
  (--lift-scale raises the airborne frames only; the output height grows to fit unless --out-height is given)
"""
import argparse
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

ap = argparse.ArgumentParser()
ap.add_argument("src"); ap.add_argument("dst")
ap.add_argument("--cols", type=int, default=4); ap.add_argument("--rows", type=int, default=2)
ap.add_argument("--grounded", default="1"); ap.add_argument("--standing", default="1")
ap.add_argument("--ref-panel", type=int, default=1)
ap.add_argument("--height", type=float, default=408); ap.add_argument("--toe-x", type=float, default=336)
ap.add_argument("--width", type=int, default=512); ap.add_argument("--out-height", type=int, default=0)
ap.add_argument("--ground-from-bottom", type=int, default=42)
ap.add_argument("--lift-scale", type=float, default=1.0,
                help="multiplies how far the feet are above the ground in the airborne frames (2.0 = jumps twice as high)")
ap.add_argument("--align", choices=["toe", "feet"], default="toe",
                help="toe: every panel keeps the horizontal position it was drawn at (shifted so --ref-panel's front toe lands on --toe-x). "
                     "feet: each grounded panel is moved so the middle of its feet lands on --feet-x, and the airborne panels follow smoothly between their grounded neighbours (removes the sideways wobble of the generator; use it for in-place moves such as a hop)")
ap.add_argument("--feet-x", type=float, default=248, help="with --align feet: where the middle of the feet goes (the idle's feet are 160 and 336 apart, so 248)")
ap.add_argument("--fit", default="", help="panels (1-based, comma separated) that are full-height standing poses: each is scaled on its own to exactly --height, so a hop that starts and ends in the idle stance joins the idle without a size jump")
ap.add_argument("--scale-mult", default="", help="per-panel size correction, comma separated (1 = unchanged), for sheets where the generator drew some panels bigger or smaller than the rest")
ap.add_argument("--despill-band", type=int, default=3, help="px from the silhouette in which leftover magenta is pulled out (raise it when the sheet has a purple glow around the outline)")
ap.add_argument("--despill-thr", type=float, default=12, help="how far red and blue may exceed green inside that band (lower = stricter)")
a = ap.parse_args()
grounded = [int(x) - 1 for x in a.grounded.split(",")]; standing = [int(x) - 1 for x in a.standing.split(",")]

img = np.array(Image.open(a.src).convert("RGB")).astype(float)
r, g, b = img[..., 0], img[..., 1], img[..., 2]
alpha = 1 - np.clip((np.minimum(r, b) - g - 70) / 110, 0, 1)
soft = alpha < 1
rgb = img.copy()
rgb[..., 0] = np.where(soft, np.minimum(r, g + 25), r); rgb[..., 2] = np.where(soft, np.minimum(b, g + 25), b)
band = ndi.binary_dilation(alpha < 0.5, iterations=a.despill_band) & (alpha >= 0.5)
mm = np.minimum(rgb[..., 0], rgb[..., 2]) - rgb[..., 1]
fix = (band | soft) & (mm > a.despill_thr)
rgb[..., 0] = np.where(fix, np.minimum(rgb[..., 0], rgb[..., 1] + a.despill_thr), rgb[..., 0])
rgb[..., 2] = np.where(fix, np.minimum(rgb[..., 2], rgb[..., 1] + a.despill_thr), rgb[..., 2])
rgba = np.dstack([rgb, alpha * 255]).astype(np.uint8)

PW, PH = rgba.shape[1] // a.cols, rgba.shape[0] // a.rows
panels, boxes = [], []
for k in range(a.cols * a.rows):
    rr, cc = divmod(k, a.cols)
    p = rgba[rr * PH:(rr + 1) * PH, cc * PW:(cc + 1) * PW].copy()
    solid = p[..., 3] > 128
    lab, n = ndi.label(solid); sizes = ndi.sum(solid, lab, range(1, n + 1))
    p[..., 3] = np.where(ndi.binary_dilation(lab == 1 + int(np.argmax(sizes)), iterations=3), p[..., 3], 0)
    ys, xs = np.where(p[..., 3] > 128)
    panels.append(p); boxes.append((xs.min(), ys.min(), xs.max(), ys.max()))

scale = a.height / float(np.mean([boxes[k][3] - boxes[k][1] for k in standing]))
fit = [int(x) - 1 for x in a.fit.split(",") if x.strip()]
mult = [float(x) for x in a.scale_mult.split(",") if x.strip()]
sk = [(a.height / float(boxes[k][3] - boxes[k][1]) if k in fit else scale) * (mult[k] if k < len(mult) else 1) for k in range(len(panels))]   # scale of each panel
ground = {}
for rr in range(a.rows):
    ks = [k for k in grounded if k // a.cols == rr]
    ground[rr] = float(np.median([boxes[k][3] for k in ks])) if ks else float(max(boxes[k][3] for k in range(rr * a.cols, (rr + 1) * a.cols)))
def toe(k):
    x0, y0, x1, y1 = boxes[k]
    low = panels[k][int(y1 - 0.08 * (y1 - y0)):y1 + 1, :, 3] > 128
    return np.where(low.any(0))[0].max()
shift_x = a.toe_x - toe(a.ref_panel - 1) * sk[a.ref_panel - 1]
def feet_mid(k):
    x0, y0, x1, y1 = boxes[k]
    xs = np.where((panels[k][int(y1 - 0.08 * (y1 - y0)):y1 + 1, :, 3] > 128).any(0))[0]
    return (xs.min() + xs.max()) / 2.0
if a.align == "feet":
    gk = sorted(grounded)
    sh = {k: a.feet_x - feet_mid(k) * sk[k] for k in gk}
    shifts = {}
    for k in range(len(panels)):
        before = [q for q in gk if q <= k]; after = [q for q in gk if q >= k]
        if k in sh: shifts[k] = sh[k]
        elif before and after: shifts[k] = sh[before[-1]] + (sh[after[0]] - sh[before[-1]]) * (k - before[-1]) / float(after[0] - before[-1])
        else: shifts[k] = sh[before[-1]] if before else sh[after[0]]
else:
    shifts = dict((k, shift_x) for k in range(len(panels)))
def air_px(k):  # feet above the ground in output px, after the lift scale
    natural = max(0.0, (ground[k // a.cols] - boxes[k][3]) * sk[k])
    return natural if k in grounded else natural * a.lift_scale  # grounded panels are never lifted
ext = max((ground[k // a.cols] - boxes[k][1]) * sk[k] + (air_px(k) - max(0.0, (ground[k // a.cols] - boxes[k][3]) * sk[k])) for k in range(len(panels)))
H = a.out_height or int(np.ceil((ext + a.ground_from_bottom + 12) / 128.0) * 128)
print("scale %.3f  tallest above ground %.0f px  output height %d" % (scale, ext, H))
out = Image.new("RGBA", (a.width * len(panels), H), (0, 0, 0, 0))
for k, p in enumerate(panels):
    im = Image.fromarray(p).resize((int(p.shape[1] * sk[k]), int(p.shape[0] * sk[k])), Image.LANCZOS)
    ox = int(round(shifts[k])); oy = int(round(H - a.ground_from_bottom - ground[k // a.cols] * sk[k] - (air_px(k) - max(0.0, (ground[k // a.cols] - boxes[k][3]) * sk[k]))))
    canvas = Image.new("RGBA", (a.width + 3000, H + 3000), (0, 0, 0, 0))
    canvas.alpha_composite(im, (1500 + ox, 1500 + oy))
    fr = canvas.crop((1500, 1500, 1500 + a.width, 1500 + H))
    clipped = int((np.array(im)[..., 3] > 128).sum() - (np.array(fr)[..., 3] > 128).sum())
    air = air_px(k)
    print("panel %d: feet %4.0f px above ground, clipped px %d" % (k + 1, air, clipped))
    out.alpha_composite(fr, (a.width * k, 0))
out.save(a.dst)
