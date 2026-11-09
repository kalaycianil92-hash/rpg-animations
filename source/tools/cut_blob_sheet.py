#!/usr/bin/env python3
"""Cuts a generated sheet whose panels are NOT on a clean grid (the generator drew the figures where it liked, a sheet of another shape than asked for) into a strip of tall or square cells.

It finds the figures themselves (connected blobs of non-magenta, small bits joined), sorts them into rows and columns, and puts each on a cell of CELL_W x CELL_H:
  --scale-panel K  --height H   the figure of panel K (1-based) is scaled to a bounding-box height of H px and every panel gets the SAME scale (a standing pose that must match the idle: 408)
  --air 1,2,3                   airborne panels: the bounding box is centred at (256, --air-y)
  the others                    stand on the ground line (42 px above the bottom of the cell) with the middle of the feet at --feet-x (293, like the idle)
Like slice_keypose_sheet.py, but for the tall cells of the Abyssal Backstab (512 x 768) and for sheets that came out in the wrong shape.

  python source/tools/cut_blob_sheet.py inbox/assassin_abyssal_backstab_sheet1.png reskin/work/abyssal_cut.png --expect 5 --cell-h 768 --scale-panel 5 --height 408 --air 1,2,3 --air-y 380
"""
import argparse

import numpy as np
from PIL import Image
from scipy import ndimage as ndi

ap = argparse.ArgumentParser()
ap.add_argument("src")
ap.add_argument("dst")
ap.add_argument("--expect", type=int, required=True, help="how many figures the sheet has")
ap.add_argument("--cell-h", type=int, default=768)
ap.add_argument("--scale-panel", type=int, default=1)
ap.add_argument("--height", type=float, default=408)
ap.add_argument("--fit", default="", help="panels (1-based, comma separated) that are standing poses to be scaled on their OWN to exactly --fit-height (the generator drew the standing pose of a sheet bigger than the airborne ones)")
ap.add_argument("--fit-height", type=float, default=408)
ap.add_argument("--air", default="")
ap.add_argument("--air-y", type=float, default=380)
ap.add_argument("--feet-x", type=float, default=293)
a = ap.parse_args()

img = np.array(Image.open(a.src).convert("RGB")).astype(float)
r, g, b = img[..., 0], img[..., 1], img[..., 2]
alpha = 1 - np.clip((np.minimum(r, b) - g - 70) / 110, 0, 1)
rgb = img.copy()
soft = alpha < 1
rgb[..., 0] = np.where(soft, np.minimum(r, g + 25), r)
rgb[..., 2] = np.where(soft, np.minimum(b, g + 25), b)
band = ndi.binary_dilation(alpha < 0.5, iterations=3) & (alpha >= 0.5)
mm = np.minimum(rgb[..., 0], rgb[..., 2]) - rgb[..., 1]
fix = (band | soft) & (mm > 12)
rgb[..., 0] = np.where(fix, np.minimum(rgb[..., 0], rgb[..., 1] + 12), rgb[..., 0])
rgb[..., 2] = np.where(fix, np.minimum(rgb[..., 2], rgb[..., 1] + 12), rgb[..., 2])
rgba = np.dstack([rgb, alpha * 255]).astype(np.uint8)

solid = rgba[..., 3] > 128
lab, n = ndi.label(ndi.binary_dilation(solid, iterations=14))
sizes = ndi.sum(solid, lab, range(1, n + 1))
keep = np.argsort(-sizes)[:a.expect] + 1
if len(keep) < a.expect:
    raise SystemExit("found only %d figures" % len(keep))
figs = []
for k in keep:
    m = solid & (lab == k)
    ys, xs = np.where(m)
    figs.append(dict(m=m, x0=xs.min(), y0=ys.min(), x1=xs.max(), y1=ys.max(), cx=(xs.min() + xs.max()) / 2, cy=(ys.min() + ys.max()) / 2))
H = rgba.shape[0]
nrows = 2 if a.expect > 3 else 1
split = H / nrows
figs.sort(key=lambda f: (int(f["cy"] // split) if nrows > 1 else 0, f["cx"]))
panels = []
for f in figs:
    p = rgba.copy()
    p[..., 3] = np.where(ndi.binary_dilation(f["m"], iterations=3), p[..., 3], 0)
    panels.append(Image.fromarray(p).crop((f["x0"] - 2, f["y0"] - 2, f["x1"] + 3, f["y1"] + 3)))
heights = [f["y1"] - f["y0"] + 1 for f in figs]
scale = a.height / heights[a.scale_panel - 1]
air = [int(x) - 1 for x in a.air.split(",") if x.strip()]
fit = [int(x) - 1 for x in a.fit.split(",") if x.strip()]
out = Image.new("RGBA", (512 * len(panels), a.cell_h), (0, 0, 0, 0))
for k, p in enumerate(panels):
    sc = a.fit_height / heights[k] if k in fit else scale
    im = p.resize((max(1, int(p.width * sc)), max(1, int(p.height * sc))), Image.LANCZOS)
    arr = np.array(im)
    ys, xs = np.where(arr[..., 3] > 128)
    cell = Image.new("RGBA", (512, a.cell_h), (0, 0, 0, 0))
    if k in air:
        ox = int(round(256 - (xs.min() + xs.max()) / 2))
        oy = int(round(a.air_y - (ys.min() + ys.max()) / 2))
    else:
        low = arr[int(ys.max() - 0.10 * (ys.max() - ys.min())):ys.max() + 1, :, 3] > 128
        lx = np.where(low.any(0))[0]
        ox = int(round(a.feet_x - (lx.min() + lx.max()) / 2))
        oy = int(round(a.cell_h - 42 - ys.max() - 1))
    cell.alpha_composite(im, (max(0, ox), max(0, oy))) if ox >= 0 and oy >= 0 else cell.paste(im, (ox, oy), im)
    out.alpha_composite(cell, (512 * k, 0))
    print("panel", k + 1, "figure %d x %d px in the sheet, scaled to %d x %d" % (figs[k]["x1"] - figs[k]["x0"] + 1, heights[k], im.width, im.height), "(air)" if k in air else "(ground)", "own scale %.3f" % sc if k in fit else "")
out.save(a.dst)
print("scale", round(scale, 4), "->", a.dst)
