#!/usr/bin/env python3
"""Builds a run strip by hand from panels of one or more Gemini sheets, in the order you give.

Gemini draws a running stride badly (it repeats the first step), so the run is put together from the panels that fit: each panel is cut out of
its sheet with the project's magenta keying and despill (the same as slice_keypose_sheet.py), scaled and placed in a 512 px cell so that the HEAD
has the size and x of the idle's head, and the panel's floor line lands on the cell's ground line. Every panel of a sheet uses the same
transform, so the figure keeps the position and the bob the generator gave it.

  python make_run_strip.py --sheet new=inbox/new.png --sheet old=inbox/old.png --scale new=0.94 --scale old=0.97 \
         --frames new:3,new:2,old:6,old:3,old:2 --out Animations/Mage/run/robed_run_5frame_strip.png

--frames   sheet:panel pairs, panels counted from 1 left to right, top row first, in play order
--scale    per sheet: how much to scale a 600 px panel so the head matches the idle's head (the mage: 0.94 for the sheet "new", 0.97 for "old";
           find it by template-matching the idle's head, or compare the face by eye)
--anchor-x/--anchor-y   the point of the panel that goes to (--head-x, --ground) in the cell: the mean head x of the chosen panels and the floor line
           (one value for all sheets, or name=value per sheet, repeated: sheets drawn separately have their figures at different x).
           Anchors and scales are for a 600 px panel; a sheet with another panel size is converted by itself (a sheet of 3 columns that is 1800 px wide has 600 px panels),
           unless --native is given: then they are in the sheet's own pixels
Needs pillow, numpy, scipy and opencv-python.
"""
import argparse
import numpy as np
import cv2
from PIL import Image
from scipy import ndimage as ndi

ap = argparse.ArgumentParser()
ap.add_argument("--sheet", action="append", required=True, help="name=path (repeat)")
ap.add_argument("--scale", action="append", default=[], help="name=value (repeat; default 1)")
ap.add_argument("--frames", required=True)
ap.add_argument("--out", required=True)
ap.add_argument("--cols", type=int, default=4)
ap.add_argument("--panel", type=int, default=0, help="side of one square panel in the sheet, px (default: the sheet's width divided by --cols, per sheet)")
ap.add_argument("--cell", type=int, default=512)
ap.add_argument("--ground", type=float, default=470)
ap.add_argument("--head-x", type=float, default=288)
ap.add_argument("--anchor-x", action="append", default=[], help="x, or name=x for one sheet (repeat); default 305")
ap.add_argument("--anchor-y", action="append", default=[], help="y, or name=y for one sheet (repeat); default 491")
ap.add_argument("--native", action="store_true", help="--scale and --anchor-x/y are in the sheet's own pixels (no 600 px panel conversion)")
ap.add_argument("--despill-band", type=int, default=10)
ap.add_argument("--despill-thr", type=float, default=4)
a = ap.parse_args()

sheets = {}
for s in a.sheet:
    k, v = s.split("=", 1)
    sheets[k] = np.asarray(Image.open(v).convert("RGB")).astype(np.float32)
def per_sheet(vals, default):
    d = {k: default for k in sheets}
    for s in vals:
        if "=" in s:
            k, v = s.split("=", 1); d[k] = float(v)
        else:
            d = {k: float(s) for k in sheets}
    return d


anchors_x = per_sheet(a.anchor_x, 305.0)
anchors_y = per_sheet(a.anchor_y, 491.0)
scales = {k: 1.0 for k in sheets}
for s in a.scale:
    k, v = s.split("=", 1)
    scales[k] = float(v)


def panel_size(name):
    return a.panel or sheets[name].shape[1] // a.cols


def panel_rgba(name, n):
    P = panel_size(name)
    r, c = divmod(n - 1, a.cols)
    p = sheets[name][r * P:(r + 1) * P, c * P:(c + 1) * P].copy()
    R, G, B = p[..., 0], p[..., 1], p[..., 2]
    al = 1 - np.clip((np.minimum(R, B) - G - 70) / 110, 0, 1)             # magenta -> transparent
    soft = al < 1
    rgb = p.copy()
    rgb[..., 0] = np.where(soft, np.minimum(R, G + 25), R)                # despill the pink fringe
    rgb[..., 2] = np.where(soft, np.minimum(B, G + 25), B)
    band = ndi.binary_dilation(al < 0.5, iterations=a.despill_band) & (al >= 0.5)
    mm = np.minimum(rgb[..., 0], rgb[..., 2]) - rgb[..., 1]
    fix = (band | soft) & (mm > a.despill_thr)
    rgb[..., 0] = np.where(fix, np.minimum(rgb[..., 0], rgb[..., 1] + a.despill_thr), rgb[..., 0])
    rgb[..., 2] = np.where(fix, np.minimum(rgb[..., 2], rgb[..., 1] + a.despill_thr), rgb[..., 2])
    solid = al > 0.5                                                      # keep the character, drop dust
    lab, k = ndi.label(solid)
    if k > 1:
        keep = 1 + int(np.argmax(ndi.sum(solid, lab, range(1, k + 1))))
        al = np.where(ndi.binary_dilation(lab == keep, iterations=3), al, 0)
    return np.dstack([np.clip(rgb, 0, 255), al * 255.0])


def place(name, n):
    p = panel_rgba(name, n)
    k = 1.0 if a.native else panel_size(name) / 600.0                      # anchors and scales are given for a 600 px panel (unless --native)
    s = scales[name] / k
    ax, ay = anchors_x[name] * k, anchors_y[name] * k
    pm = p.copy()
    pm[..., :3] *= (p[..., 3:4] / 255.0)                                  # premultiply so the resize does not pull in the key colour
    M = np.array([[s, 0, a.head_x - ax * s], [0, s, a.ground - ay * s]], dtype=np.float32)
    out = cv2.warpAffine(pm, M, (a.cell, a.cell), flags=cv2.INTER_LANCZOS4, borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0, 0))
    al = out[..., 3:4]
    rgb = np.where(al > 1, out[..., :3] / np.maximum(al / 255.0, 1e-3), 0)
    return np.dstack([np.clip(rgb, 0, 255), np.clip(al, 0, 255)]).astype(np.uint8)


frames = [(f.split(":")[0], int(f.split(":")[1])) for f in a.frames.split(",")]
strip = Image.fromarray(np.concatenate([place(n, k) for n, k in frames], axis=1), "RGBA")
strip.save(a.out, optimize=True)
print("wrote", a.out, strip.size, "frames:", a.frames)
