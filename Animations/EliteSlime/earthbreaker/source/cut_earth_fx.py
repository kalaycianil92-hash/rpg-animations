#!/usr/bin/env python3
"""Cuts the Earthbreaker's painted effects sheet (the user's ChatGPT sheet, 1254 x 1254, 3 x 3, flat magenta, 2026-11-10) into nine RGBA pictures in source/assets/fx/.

  python Animations/EliteSlime/earthbreaker/source/cut_earth_fx.py

The pieces are SOLID and OPAQUE stone, earth and dust (drawn with normal blending, not added as light), so the magenta is keyed as for the Elite's own sheets
(alpha = 1 - clip((min(r, b) - g - 70) / 110, 0, 1), the colour of the soft edge pixels pulled off the pink), then every panel is cropped to its piece (the bottom of a spike's picture IS its flat base line) with a few px of margin.
Names, in reading order: eb_cluster, eb_spike_a, eb_spike_b, eb_twin, eb_crack, eb_plunge, eb_debris, eb_dust_ring, eb_dust_plume.
"""
import os, shutil
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
SRC = os.path.join(HERE, "earthbreaker_fx_sheet.png")
if not os.path.isfile(SRC): shutil.copyfile(os.path.join(ROOT, "inbox", "earthbreaker_fx_sheet.png"), SRC)
OUT = os.path.join(ROOT, "source", "assets", "fx")
NAMES = ["eb_cluster", "eb_spike_a", "eb_spike_b", "eb_twin", "eb_crack", "eb_plunge", "eb_debris", "eb_dust_ring", "eb_dust_plume"]
PAD, INSET = 6, 4

arr = np.array(Image.open(SRC).convert("RGB")).astype(float)
H, W = arr.shape[:2]
r, g, b = arr[..., 0], arr[..., 1], arr[..., 2]
alpha = 1 - np.clip((np.minimum(r, b) - g - 70) / 110, 0, 1)
soft = alpha < 1
rgb = arr.copy()
rgb[..., 0] = np.where(soft, np.minimum(r, g + 25), r); rgb[..., 2] = np.where(soft, np.minimum(b, g + 25), b)
band = ndi.binary_dilation(alpha < 0.5, iterations=6) & (alpha >= 0.5)
mm = np.minimum(rgb[..., 0], rgb[..., 2]) - rgb[..., 1]
fix = (band | soft) & (mm > 4)
rgb[..., 0] = np.where(fix, np.minimum(rgb[..., 0], rgb[..., 1] + 4), rgb[..., 0]); rgb[..., 2] = np.where(fix, np.minimum(rgb[..., 2], rgb[..., 1] + 4), rgb[..., 2])
rgba = np.dstack([rgb, alpha * 255]).clip(0, 255).astype(np.uint8)
os.makedirs(OUT, exist_ok=True)
pw, ph = W // 3, H // 3
for k, name in enumerate(NAMES):
    rr, cc = divmod(k, 3)
    x0, y0 = cc * pw + INSET, rr * ph + INSET
    panel = rgba[y0:(rr + 1) * ph - INSET, x0:(cc + 1) * pw - INSET].copy()
    solid = panel[..., 3] > 40
    lab, n = ndi.label(ndi.binary_dilation(solid, iterations=3))
    sizes = ndi.sum(solid, lab, range(1, n + 1)); keep = np.zeros_like(solid)
    for i in range(1, n + 1):
        if sizes[i - 1] >= 12: keep |= (lab == i)                                    # specks of a few px are dust of the key, not pieces (the debris keeps its small chips: they are 30 px and more)
    panel[~keep, 3] = 0
    ys, xs = np.where(panel[..., 3] > 40)
    y1, y2, x1, x2 = max(0, ys.min() - PAD), min(panel.shape[0], ys.max() + 2), max(0, xs.min() - PAD), min(panel.shape[1], xs.max() + PAD + 1)   # (the bottom row of the content is the flat base line of a spike: only 1 px under it, so the page can plant the picture's bottom edge on the ground)
    im = Image.fromarray(panel[y1:y2, x1:x2])
    im.save(os.path.join(OUT, name + ".png"))
    a = np.array(im)[..., 3]
    pink = ((np.array(im)[..., 0].astype(int) - np.array(im)[..., 1] > 60) & (np.array(im)[..., 2].astype(int) - np.array(im)[..., 1] > 60) & (a > 128)).sum()
    print("%-13s %4d x %4d px | bottom row of content at %d of %d | pink px left: %d" % (name, im.width, im.height, ys.max() - y1 + 1, im.height, pink))
# a check picture: the nine pieces on white (top) and on a dark forest green (bottom), 5 + 4 per row
sheet = Image.new("RGB", (1500, 1100), (255, 255, 255))
for bgi, bg in enumerate([(255, 255, 255), (38, 84, 52)]):
    for k, name in enumerate(NAMES):
        im = Image.open(os.path.join(OUT, name + ".png")).convert("RGBA")
        sc = min(1.0, 270.0 / max(im.size)); im = im.resize((max(1, int(im.width * sc)), max(1, int(im.height * sc))), Image.LANCZOS)
        cx, cy = (k % 5) * 300, bgi * 560 + (k // 5) * 280
        sheet.paste(Image.new("RGB", (300, 280), bg), (cx, cy))
        sheet.paste(im, (cx + (300 - im.width) // 2, cy + 275 - im.height), im)
sheet.save(os.path.join(HERE, "..", "earthbreaker_fx_check.png"))
