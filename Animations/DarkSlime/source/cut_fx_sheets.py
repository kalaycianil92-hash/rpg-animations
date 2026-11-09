#!/usr/bin/env python3
"""Cuts the dark slime's two painted effect sheets (the user's, 2026-11-09, 1254 x 1254, 3 x 3) into source/assets/fx/dk_*.png.

  python Animations/DarkSlime/source/cut_fx_sheets.py

GLOW sheet (pure black, drawn ADDITIVELY): source/tools/cut_fx_sheet.py (brightness becomes transparency): dk_orb, dk_burst, dk_fissure, dk_geyser, dk_ripple, dk_streak, dk_crescents, dk_motes, dk_tendrils.
INK sheet (flat GREEN key, drawn NORMALLY, solid ink): the green-key alpha and despill of dark_panels.py; every panel is cropped to its pieces (+12 px), longest side at most 512 px: dk_splash, dk_splat, dk_pool,
dk_drips, dk_drops_a, dk_drops_b, dk_smear, dk_vines, dk_bubbles.
"""
import os, subprocess, sys
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
FX = os.path.join(ROOT, "source", "assets", "fx")
sys.path.insert(0, HERE)
import dark_panels as dp

GLOW = "dk_orb,dk_burst,dk_fissure,dk_geyser,dk_ripple,dk_streak,dk_crescents,dk_motes,dk_tendrils"
subprocess.run([sys.executable, os.path.join(ROOT, "source", "tools", "cut_fx_sheet.py"), os.path.join(HERE, "dark_fx_glow_sheet.png"), FX, "--cols", "3", "--rows", "3", "--min", "40", "--pad", "12", "--names=" + GLOW], check=True)

INK = "dk_splash,dk_splat,dk_pool,dk_drips,dk_drops_a,dk_drops_b,dk_smear,dk_vines,dk_bubbles".split(",")
arr = np.array(Image.open(os.path.join(HERE, "dark_fx_ink_sheet.png")).convert("RGB")).astype(float)
r, g, b = arr[..., 0], arr[..., 1], arr[..., 2]
alpha = dp._alpha(arr)
soft = alpha < 1
rgb = arr.copy()
rgb[..., 1] = np.where(soft, np.minimum(g, np.maximum(r, b) + 25), g)
band = ndi.binary_dilation(alpha < 0.5, iterations=6) & (alpha >= 0.5)
mm = rgb[..., 1] - np.maximum(rgb[..., 0], rgb[..., 2])
fix = (band | soft) & (mm > 4)
rgb[..., 1] = np.where(fix, np.minimum(rgb[..., 1], np.maximum(rgb[..., 0], rgb[..., 2]) + 4), rgb[..., 1])
greenish = (rgb[..., 1] > 110) & (rgb[..., 1] >= rgb[..., 2] - 10)                        # leftover pale cyan-green slivers in the gaps (the despilled key): not violet, so not ink
alpha = np.where(greenish, 0, alpha)
rgba = np.dstack([rgb, alpha * 255]).clip(0, 255).astype(np.uint8)
H, W = rgba.shape[:2]; pw, ph = W // 3, H // 3
for k, name in enumerate(INK):
    cx, cy = k % 3, k // 3
    panel = rgba[cy * ph + 6:(cy + 1) * ph - 6, cx * pw + 6:(cx + 1) * pw - 6]
    a = panel[..., 3] > 40
    lab, n = ndi.label(ndi.binary_dilation(a, iterations=14))
    ys, xs = np.where(a)
    if not len(ys): print("empty", name); continue
    pad = 12
    y0, y1, x0, x1 = max(0, ys.min() - pad), min(panel.shape[0], ys.max() + pad), max(0, xs.min() - pad), min(panel.shape[1], xs.max() + pad)
    im = Image.fromarray(panel[y0:y1, x0:x1])
    s = 512 / max(im.size)
    if s < 1: im = im.resize((max(1, int(im.width * s)), max(1, int(im.height * s))), Image.LANCZOS)
    im.save(os.path.join(FX, name + ".png"))
    print(name, im.size)
