#!/usr/bin/env python3
"""Cuts an item picture (staff, sword, orb, shield...) out of its flat grey background and saves a tight transparent PNG.

The generated item pictures have a thick dark outline on a flat mid-grey background with a soft glow around the shiny parts.
The cut keeps everything inside the outer dark outline (so glows inside the item stay) and drops the grey and the glow outside it.

  python cut_item.py ../../inbox/staff.png ../assets/staff.png --max-height 1000 --holes
  python cut_item.py ../../inbox/sword.png ../assets/sword.png --rotate 180 --max-height 1000      (the generated sword points down)

--rotate 180   turn the picture around after cutting (items must point UP: the hand marks say 0 degrees = the item points up)
--dark 75      pixels darker than this (0-255) count as outline
--holes        also make transparent the flat grey areas that are enclosed by the item (a gap between the twists of a staff)
--max-height   shrink to at most this many px high (items are drawn at 100 to 450 px on screen, so 1000 is plenty)

Needs pillow, numpy and scipy.
"""
import argparse
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

ap = argparse.ArgumentParser()
ap.add_argument("src"); ap.add_argument("dst")
ap.add_argument("--rotate", type=int, default=0, choices=[0, 90, 180, 270])
ap.add_argument("--dark", type=float, default=75)
ap.add_argument("--holes", action="store_true")
ap.add_argument("--max-height", type=int, default=1000)
ap.add_argument("--pad", type=int, default=3)
a = ap.parse_args()

rgb = np.array(Image.open(a.src).convert("RGB")).astype(np.float32)
lum = rgb.mean(2)
bg = np.median(np.concatenate([rgb[:8].reshape(-1, 3), rgb[-8:].reshape(-1, 3), rgb[:, :8].reshape(-1, 3), rgb[:, -8:].reshape(-1, 3)]), axis=0)
print("background grey", bg.round(0).tolist())

dark = lum < a.dark
sil = ndi.binary_fill_holes(ndi.binary_closing(dark, structure=np.ones((3, 3)), iterations=3))
lab, n = ndi.label(sil)                                           # keep the item and what is attached to it, drop specks
if n > 1:
    sizes = ndi.sum(sil, lab, range(1, n + 1))
    sil = np.isin(lab, [i + 1 for i, s in enumerate(sizes) if s > 0.002 * sil.size])
if a.holes:
    flat = (np.abs(rgb - bg).max(2) <= 8) & sil                  # flat grey inside the silhouette = see-through gap
    hl, hn = ndi.label(flat)
    for i in range(1, hn + 1):
        m = hl == i
        if m.sum() >= 150:
            sil &= ~m
            print("opened a gap of", int(m.sum()), "px")

core = ndi.binary_erosion(sil, iterations=1)                      # drop the outline pixels that are blended with the grey
alpha = np.clip(ndi.gaussian_filter(core.astype(np.float32), 0.9) * 1.25, 0, 1) * ndi.binary_dilation(sil, iterations=1)
solid = alpha > 0.99
idx = ndi.distance_transform_edt(~solid, return_distances=False, return_indices=True)
rgb = rgb[idx[0], idx[1]]                                         # colour of the nearest solid pixel, so soft edges carry no grey
out = np.dstack([rgb, alpha * 255]).astype(np.uint8)

ys, xs = np.where(alpha > 0.02)
x0, x1, y0, y1 = max(xs.min() - a.pad, 0), min(xs.max() + a.pad + 1, out.shape[1]), max(ys.min() - a.pad, 0), min(ys.max() + a.pad + 1, out.shape[0])
im = Image.fromarray(out[y0:y1, x0:x1], "RGBA")
if a.rotate:
    im = im.rotate(-a.rotate, expand=True)
if im.size[1] > a.max_height:
    s = a.max_height / im.size[1]
    im = im.resize((max(1, round(im.size[0] * s)), a.max_height), Image.LANCZOS)
im.save(a.dst)
print("wrote", a.dst, im.size)
