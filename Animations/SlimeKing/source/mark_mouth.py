#!/usr/bin/env python3
"""Marks the Slime King's mouth on the Radiant Ooze strip (2026-11-11): the open mouth's dark warm-brown / orange inside per frame (centre and size in the 512 cell, before the page mirrors the sprite), written to
radiant_ooze/king_radiant_ooze_8frame_strip.mouth.json like the slimes' (the page's monMouth reads it: the spit leaves the mouth at the release frame 5, the charge glow sits in it on frames 4 to 6)."""
import json, os
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
HERE = os.path.dirname(os.path.abspath(__file__)); KING = os.path.abspath(os.path.join(HERE, ".."))
path = os.path.join(KING, "radiant_ooze", "king_radiant_ooze_8frame_strip.png")
im = np.array(Image.open(path).convert("RGBA")).astype(int)
out = {}
for k in (4, 5, 6, 7):
    f = im[:, 512 * (k - 1):512 * k]
    r, g, b, a = f[..., 0], f[..., 1], f[..., 2], f[..., 3]
    m = (a > 200) & (r > 90) & (r - g > 50) & (g < 125) & (b < 85)
    m &= (np.arange(512)[None, :] < 430) & (np.arange(512)[:, None] > 250)                  # (not the staff, not the crown: the face is the lower half)
    lab, n = ndi.label(m)
    if not n: print("frame", k, "no mouth found"); continue
    sizes = ndi.sum(m, lab, range(1, n + 1)); i = int(np.argmax(sizes)) + 1
    ys, xs = np.where(lab == i)
    out[str(k)] = {"area": int(sizes[i - 1]), "x": round(float(xs.mean()), 1), "y": round(float(ys.mean()), 1), "w": int(xs.max() - xs.min() + 1), "h": int(ys.max() - ys.min() + 1)}
    print("frame", k, out[str(k)])
json.dump({"note": "the open mouth's inside per frame (centre and size in the 512 cell, before the page mirrors the sprite): the Radiant Ooze leaves the mouth at the release frame 5", "mouth": out}, open(path.replace(".png", ".mouth.json"), "w"), indent=1)
