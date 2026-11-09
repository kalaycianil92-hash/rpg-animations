#!/usr/bin/env python3
"""Re-lays a generated sprite sheet (N creatures on flat magenta, cols x rows) into EQUAL cells so that the cutter
(slice_keypose_sheet.py, which splits a sheet into equal cells) cannot mix panels up. Added 2026-11-07.

Why: generators draw a tall flame or a floating ember across the middle line of the sheet or close to a neighbour; an equal
split then gives that piece to the wrong panel, and --keep-near would keep it as a stray bit under the neighbour.

What it does: keys the magenta (the cutter's rule), finds the cols x rows biggest pieces (the creatures), gives every other
piece of 40 px or more to the nearest creature, blanks everything else in that creature's crop to pure magenta, and pastes
the crops, centred and bottom-aligned, into one sheet of equal cells (the size of the biggest crop). It reports each panel's
bounding box, the gap to its neighbours and the pieces it moved, and writes a lossless PNG.

  python source/tools/equalize_sheet.py sheet.jpg equal_sheet.png            (3 x 2 by default)
  python source/tools/equalize_sheet.py sheet.png out.png --cols 3 --rows 2 --margin 30
"""
import argparse
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

ap = argparse.ArgumentParser()
ap.add_argument("src"); ap.add_argument("dst")
ap.add_argument("--cols", type=int, default=3)
ap.add_argument("--rows", type=int, default=2)
ap.add_argument("--margin", type=int, default=30, help="empty px kept round each creature's crop")
ap.add_argument("--min-piece", type=int, default=40, help="smaller pieces are dust and are dropped")
a = ap.parse_args()

img = np.array(Image.open(a.src).convert("RGB"))
f = img.astype(float)
r, g, b = f[..., 0], f[..., 1], f[..., 2]
alpha = 1 - np.clip((np.minimum(r, b) - g - 70) / 110, 0, 1)
solid = alpha > 0.5
lab, n = ndi.label(solid)
sizes = ndi.sum(solid, lab, range(1, n + 1))
objs = ndi.find_objects(lab)
N = a.cols * a.rows
order = np.argsort(sizes)[::-1]
bigs = [int(i) + 1 for i in order[:N]]
print("creatures found:", N, "areas", [int(sizes[i - 1]) for i in bigs], "| next biggest piece", int(sizes[order[N]]) if n > N else 0)

def box(i):
    sl = objs[i - 1]; return sl[1].start, sl[0].start, sl[1].stop, sl[0].stop
def box_dist(b1, b2):
    dx = max(b1[0] - b2[2], b2[0] - b1[2], 0); dy = max(b1[1] - b2[3], b2[1] - b1[3], 0)
    return (dx * dx + dy * dy) ** 0.5

# the creatures in reading order: rows by their centre y, then columns by centre x
cen = {i: ((box(i)[0] + box(i)[2]) / 2, (box(i)[1] + box(i)[3]) / 2) for i in bigs}
by_y = sorted(bigs, key=lambda i: cen[i][1])
rows = [sorted(by_y[k * a.cols:(k + 1) * a.cols], key=lambda i: cen[i][0]) for k in range(a.rows)]
panels = [i for row in rows for i in row]

owner = {}
moved = 0
for i in range(1, n + 1):
    if i in panels or sizes[i - 1] < a.min_piece:
        continue
    d = [box_dist(box(i), box(p)) for p in panels]
    k = int(np.argmin(d)); owner[i] = k
    # report pieces that lie inside another panel's equal cell (the ones an equal split would have mixed up)
    cx = (box(i)[0] + box(i)[2]) / 2; cy = (box(i)[1] + box(i)[3]) / 2
    cell = (int(cx // (img.shape[1] / a.cols)), int(cy // (img.shape[0] / a.rows)))
    own_cell = (int(cen[panels[k]][0] // (img.shape[1] / a.cols)), int(cen[panels[k]][1] // (img.shape[0] / a.rows)))
    if cell != own_cell:
        moved += 1
        print("  piece of %d px at x %d, y %d lies in another cell than its creature (panel %d): moved with it" % (sizes[i - 1], box(i)[0], box(i)[1], k + 1))
print("pieces assigned:", len(owner), "| of those that an equal split would have mixed up:", moved)

crops = []
for k, p in enumerate(panels):
    keep = lab == p
    for i, kk in owner.items():
        if kk == k:
            keep |= lab == i
    keep = ndi.binary_dilation(keep, iterations=6)
    ys, xs = np.where(keep)
    x0, y0, x1, y1 = xs.min(), ys.min(), xs.max() + 1, ys.max() + 1
    m = a.margin
    X0, Y0, X1, Y1 = max(0, x0 - m), max(0, y0 - m), min(img.shape[1], x1 + m), min(img.shape[0], y1 + m)
    c = img[Y0:Y1, X0:X1].copy()
    c[~keep[Y0:Y1, X0:X1]] = (255, 0, 255)
    crops.append((c, (x0 - X0, y0 - Y0, x1 - X0, y1 - Y0)))
    print("panel %d: creature box x %d..%d y %d..%d (%d x %d)" % (k + 1, x0, x1, y0, y1, x1 - x0, y1 - y0))

cw = max(c.shape[1] for c, _ in crops); ch = max(c.shape[0] for c, _ in crops)
out = np.zeros((ch * a.rows, cw * a.cols, 3), np.uint8); out[:] = (255, 0, 255)
for k, (c, bb) in enumerate(crops):
    rr, cc = divmod(k, a.cols)
    ox = cc * cw + (cw - c.shape[1]) // 2
    oy = rr * ch + (ch - c.shape[0])
    out[oy:oy + c.shape[0], ox:ox + c.shape[1]] = c
Image.fromarray(out).save(a.dst)
print("cell", cw, "x", ch, "->", a.dst)
