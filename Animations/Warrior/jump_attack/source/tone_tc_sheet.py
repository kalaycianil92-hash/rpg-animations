#!/usr/bin/env python3
"""Tones down the user's ChatGPT lightning sheet for the Thunderclap Guillotine (2026-11-13).

The user: "it seems a bit cartoonish for my taste. I actually like your effects, you can use the generated ones by toning them down."
What made it cartoonish: flat violet outlines round every bolt and very wide, saturated glows. So, before the sheet is cut:
  1. the colour is replaced by the game's ONE lightning blue (the user's rule of 2026-11-09, see LTC in the page: deep 35,55,215, mid 60,95,255, bright 125,148,255, core 240,244,255),
     with no violet at all;
  2. the brightness goes through a gamma (default 1.9; 1.35 was tried first and made the cores wider and whiter, which looked MORE flat), which thins the glows and the cores and leaves a periwinkle peak instead of white (like the recoloured Static Stiletto pictures);
  2b. a light Gaussian blur (--blur 2.2) takes the hard, clean vector edges off the shapes (they were flat solid polygons: the other half of the cartoon look);
  3. (the page then draws the pictures at a low strength, 45% by default, on top of its own code bolts.)

  python tone_tc_sheet.py [--gamma 1.9]
  python ../../../../source/tools/cut_fx_sheet.py thunderclap_fx_sheet_toned.png ../../../../source/assets/fx --cols 3 --rows 2 --min 40 --pad 12 "--names=tc_bolt_a,tc_bolt_b,tc_bolt_heavy,tc_blade,tc_burst,tc_ground"
(the second command is run for you by this script unless --no-cut is given)
"""
import argparse
import pathlib
import subprocess
import sys
import numpy as np
from PIL import Image

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[3]
ap = argparse.ArgumentParser()
ap.add_argument("--src", default=str(ROOT / "inbox" / "SPELL VFX" / "lightning_effects_vfx.png"))
ap.add_argument("--gamma", type=float, default=1.9)
ap.add_argument("--blur", type=float, default=2.2, help="Gaussian blur (px of the 1536 px sheet) that takes the hard vector edges off the shapes")
ap.add_argument("--no-cut", action="store_true")
a = ap.parse_args()

STOPS = [(0.00, (0, 0, 0)), (0.30, (25, 40, 170)), (0.60, (60, 95, 255)), (0.85, (125, 148, 255)), (1.00, (205, 215, 255))]      # the same periwinkle peak as the recoloured ss_* pictures (about 158,176,255 at their brightest), not white
img = np.array(Image.open(a.src).convert("RGB")).astype(float) / 255
v = img.max(axis=2)
v = np.clip((v - 0.04) / 0.96, 0, 1) ** a.gamma                       # the generator's faint black haze goes, the halos get thinner
out = np.zeros(img.shape)
xs = [s[0] for s in STOPS]
for c in range(3):
    out[..., c] = np.interp(v, xs, [s[1][c] for s in STOPS])
if a.blur > 0:
    from scipy import ndimage as ndi
    for c in range(3):
        out[..., c] = ndi.gaussian_filter(out[..., c], a.blur)
dst = HERE / "thunderclap_fx_sheet_toned.png"
Image.fromarray(np.clip(out, 0, 255).astype(np.uint8)).save(dst)
print("wrote", dst, "gamma", a.gamma)
if not a.no_cut:
    subprocess.check_call([sys.executable, str(ROOT / "source" / "tools" / "cut_fx_sheet.py"), str(dst), str(ROOT / "source" / "assets" / "fx"), "--cols", "3", "--rows", "2",
                           "--min", "40", "--pad", "12", "--names=tc_bolt_a,tc_bolt_b,tc_bolt_heavy,tc_blade,tc_burst,tc_ground"])
