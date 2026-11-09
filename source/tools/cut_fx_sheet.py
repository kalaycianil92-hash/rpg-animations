#!/usr/bin/env python3
"""Cuts a sheet of fire textures (generated on PURE BLACK) into separate pictures for the test page's "Painted" look.

The textures are added over the scene, so black must add nothing and nothing has to be cut out by hand. This tool
(1) takes the black level out (generators leave a faint haze that would show as a dark square), (2) crops each panel to the effect,
(3) feathers the crop edges so no square edge can show, (4) turns brightness into transparency (alpha = the brightest channel, colour divided by
it), so that drawn with the canvas "lighter" operation the picture adds exactly its own light and nothing else (plain black pixels would otherwise
paint opaque black squares on the effects layer), (5) shrinks it to at most --max px. The result is an RGBA png.

  python cut_fx_sheet.py ../../inbox/firebolt_textures_sheet.png ../assets/fx --cols 3 --rows 2

Default names (panel order, left to right, top row first): fb_head_a, fb_head_b, fb_trail, fb_burst_1, fb_burst_2, fb_burst_3. --names takes
your own list for a sheet with another layout; a name "-" skips that panel (Gemini made a 3 x 3 sheet once: --cols 3 --rows 3). --inset skips the
edge of each panel, where generators sometimes draw white divider lines even when asked not to.
Needs pillow, numpy and scipy.
"""
import argparse
import pathlib
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

ap = argparse.ArgumentParser()
ap.add_argument("src"); ap.add_argument("outdir")
ap.add_argument("--cols", type=int, default=3); ap.add_argument("--rows", type=int, default=2)
ap.add_argument("--names", default="fb_head_a,fb_head_b,fb_trail,fb_burst_1,fb_burst_2,fb_burst_3")
ap.add_argument("--black", type=float, default=14, help="values up to this (0-255) are taken as black and removed")
ap.add_argument("--min", type=float, default=10, help="after that, pixels brighter than this count as part of the effect when cropping")
ap.add_argument("--max", type=int, default=512, help="longest side in px")
ap.add_argument("--pad", type=int, default=6)
ap.add_argument("--inset", type=int, default=6, help="px skipped at every edge of each panel (divider lines)")
ap.add_argument("--grow", type=int, default=24, help="bright specks farther than this (px) from the main body of the effect are ignored (they are often a piece of the neighbouring panel)")
a = ap.parse_args()

img = np.array(Image.open(a.src).convert("RGB")).astype(np.float32)
H, W = img.shape[:2]
pw, ph = W // a.cols, H // a.rows
names = a.names.split(",")
out = pathlib.Path(a.outdir); out.mkdir(parents=True, exist_ok=True)
for k, name in enumerate(names[:a.cols * a.rows]):
    r, c = divmod(k, a.cols)
    if name == "-":
        continue
    p = img[r * ph + a.inset:(r + 1) * ph - a.inset, c * pw + a.inset:(c + 1) * pw - a.inset]
    p = np.clip((p - a.black) * 255.0 / (255.0 - a.black), 0, 255)                     # take the black level out
    lum = p.max(2)
    mask = lum > a.min
    lab, nl = ndi.label(ndi.binary_dilation(mask, iterations=a.grow))                      # keep only the main body of the effect
    if nl > 1:
        keep = 1 + int(np.argmax(ndi.sum(mask, lab, range(1, nl + 1))))
        p = p * ndi.binary_dilation(lab == keep, iterations=a.pad)[..., None]
        mask = mask & (lab == keep)
    ys, xs = np.where(mask)
    if not len(ys):
        print(name, "is empty"); continue
    x0, x1, y0, y1 = max(xs.min() - a.pad, 0), min(xs.max() + a.pad + 1, p.shape[1]), max(ys.min() - a.pad, 0), min(ys.max() + a.pad + 1, p.shape[0])
    q = p[y0:y1, x0:x1]
    h, w = q.shape[:2]
    fx = np.minimum(1, np.minimum(np.arange(w), np.arange(w)[::-1]) / max(2.0, w * 0.04))   # fade the border so the crop never shows a hard edge
    fy = np.minimum(1, np.minimum(np.arange(h), np.arange(h)[::-1]) / max(2.0, h * 0.04))
    q = q * (fy[:, None] * fx[None, :])[..., None]
    al = q.max(2)
    rgb = np.where(al[..., None] > 0, q * 255.0 / np.maximum(al[..., None], 1.0), 0)           # un-premultiplied: colour / brightness
    im = Image.fromarray(np.dstack([np.clip(rgb, 0, 255), al]).astype(np.uint8), "RGBA")
    if max(im.size) > a.max:
        s = a.max / max(im.size); im = im.resize((max(1, round(im.size[0] * s)), max(1, round(im.size[1] * s))), Image.LANCZOS)
    im.save(out / (name + ".png"))
    print(name, im.size)
