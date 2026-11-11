#!/usr/bin/env python3
"""Cuts the holy effect sheet (the user's generated PNG on PURE BLACK, 3 x 3, 2026-11-11, prompt: Animations/SlimeKing/holy_fx/source/holy_fx_glow_prompt.txt) into nine textures in source/assets/fx/ with the
project's fx cutter (source/tools/cut_fx_sheet.py: the black level taken out, each panel cropped to the effect, the edges feathered, brightness turned into transparency so that the page's additive drawing adds exactly
its own light):

  python Animations/SlimeKing/source/cut_holy_fx.py inbox/holy_fx_glow_sheet.png

Names (panel order, left to right, top row first): hl_orb, hl_burst, hl_pillar, hl_ring, hl_halo, hl_rise, hl_star, hl_motes, hl_rays. A copy of the sheet is kept in Animations/SlimeKing/holy_fx/source/.
"""
import os, shutil, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
KING = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(KING, "..", ".."))
NAMES = "hl_orb,hl_burst,hl_pillar,hl_ring,hl_halo,hl_rise,hl_star,hl_motes,hl_rays"

src = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "inbox", "holy_fx_glow_sheet.png")
if not os.path.isabs(src): src = os.path.join(ROOT, src)
d = os.path.join(KING, "holy_fx", "source"); os.makedirs(d, exist_ok=True)
keep = os.path.join(d, "holy_fx_glow_sheet" + os.path.splitext(src)[1])
if os.path.abspath(src) != os.path.abspath(keep): shutil.copyfile(src, keep)
out = os.path.join(ROOT, "source", "assets", "fx")
cmd = [sys.executable, os.path.join(ROOT, "source", "tools", "cut_fx_sheet.py"), keep, out, "--cols", "3", "--rows", "3", "--min", "40", "--pad", "12", "--names=" + NAMES]
print(" ".join(cmd)); subprocess.check_call(cmd)

# ---- hl_ring: the generator drew the ring as a tilted oval; the page wants it LEVEL (a ring lying on the ground), so it is turned by the angle of its long axis (the principal axis of its light) and trimmed again
import numpy as np
from PIL import Image
rp = os.path.join(out, "hl_ring.png")
if os.path.isfile(rp):
    im = Image.open(rp).convert("RGBA"); a = np.array(im)[..., 3].astype(float)
    ys, xs = np.nonzero(a > 20); w = a[ys, xs]
    cx, cy = np.average(xs, weights=w), np.average(ys, weights=w)
    cov = np.cov(np.vstack([xs - cx, ys - cy]), aweights=w); vals, vecs = np.linalg.eigh(cov)
    vx, vy = vecs[:, np.argmax(vals)]; ang = np.degrees(np.arctan2(vy, vx))
    if ang > 90: ang -= 180
    if ang < -90: ang += 180
    big = Image.new("RGBA", (im.width * 2, im.height * 2), (0, 0, 0, 0)); big.paste(im, (im.width // 2, im.height // 2))
    big = big.rotate(ang, resample=Image.BICUBIC, center=(big.width / 2, big.height / 2))      # (PIL turns counter-clockwise: the long axis at `ang` degrees below the horizontal comes level)
    bb = big.getchannel("A").point(lambda v: 255 if v > 3 else 0).getbbox(); big = big.crop((max(0, bb[0] - 6), max(0, bb[1] - 6), min(big.width, bb[2] + 6), min(big.height, bb[3] + 6)))
    big.save(rp); print("hl_ring levelled by %.1f degrees -> %d x %d" % (ang, big.width, big.height))
