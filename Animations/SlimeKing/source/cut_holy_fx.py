#!/usr/bin/env python3
"""Cuts the holy effect sheets (the user's generated pictures on PURE BLACK, 3 x 3; prompt: Animations/SlimeKing/holy_fx/source/holy_fx_glow_prompt.txt) into textures for the page.

  python Animations/SlimeKing/source/cut_holy_fx.py

TWO sheets exist (2026-11-12): the user's GEMINI sheet (inbox/holy_fx_glow_sheet.jpg, 2048 x 2048) and the user's CHATGPT sheet (inbox/holy_fx_glow_sheet.png, 1254 x 1254, the same prompt). Both are kept in holy_fx/source/
(holy_fx_gemini_sheet.jpg, holy_fx_chatgpt_sheet.png) and BOTH are cut with the project's fx cutter (source/tools/cut_fx_sheet.py: the black level taken out, each panel cropped to the effect, the edges feathered,
brightness turned into transparency so that the page's additive drawing adds exactly its own light) into holy_fx/gemini/ and holy_fx/chatgpt/. PICK below says which sheet each piece used by the page comes from; the
picked pieces are copied to source/assets/fx/ (the page embeds every png there). Change PICK and run again to switch a piece.

Panel order, left to right, top row first: hl_orb, hl_burst, hl_pillar, hl_ring, hl_halo, hl_rise, hl_star, hl_motes, hl_rays. Panel 2 (the splash, hl_burst) is NOT cut: the user did not like the Gemini splash
(2026-11-12) and the page does not use one. A tilted ring (the Gemini one) is levelled after the cut.
"""
import os, shutil, subprocess, sys
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
KING = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(KING, "..", ".."))
NAMES = "hl_orb,-,hl_pillar,hl_ring,hl_halo,hl_rise,hl_star,hl_motes,hl_rays"
SHEETS = {"gemini": ("holy_fx_gemini_sheet.jpg", "holy_fx_glow_sheet.jpg"), "chatgpt": ("holy_fx_chatgpt_sheet.png", "holy_fx_glow_sheet.png")}   # (the kept name, the name in inbox/)
# the user asked (2026-11-12) to compare and replace where better: the ChatGPT pieces are cleaner and more 'holy' (a level halo ring with rays instead of a HUD-like tilted ring, an egg-shaped aura with a bright base, a
# tapering pillar with a spiral of light, a thin symmetric star and sunburst, sparse sparkles); the Gemini ORB stays (whiter and more like light: the ChatGPT one is deeper orange and reads as a fireball)
PICK = {"hl_orb": "gemini", "hl_pillar": "chatgpt", "hl_ring": "chatgpt", "hl_halo": "chatgpt", "hl_rise": "chatgpt", "hl_star": "chatgpt", "hl_motes": "chatgpt", "hl_rays": "chatgpt"}

d = os.path.join(KING, "holy_fx"); os.makedirs(os.path.join(d, "source"), exist_ok=True)
fx = os.path.join(ROOT, "source", "assets", "fx")
for tag, (keep_name, inbox_name) in SHEETS.items():
    keep = os.path.join(d, "source", keep_name)
    if not os.path.isfile(keep): shutil.copyfile(os.path.join(ROOT, "inbox", inbox_name), keep)
    out = os.path.join(d, tag); os.makedirs(out, exist_ok=True)
    cmd = [sys.executable, os.path.join(ROOT, "source", "tools", "cut_fx_sheet.py"), keep, out, "--cols", "3", "--rows", "3", "--min", "40", "--pad", "12", "--names=" + NAMES]
    print(tag, "cut"); subprocess.check_call(cmd, stdout=subprocess.DEVNULL)
    rp = os.path.join(out, "hl_ring.png")                                                              # a tilted ring is turned level (a ring lying on the ground): by the angle of its long axis
    im = Image.open(rp).convert("RGBA"); a = np.array(im)[..., 3].astype(float)
    ys, xs = np.nonzero(a > 20); w = a[ys, xs]; cx, cy = np.average(xs, weights=w), np.average(ys, weights=w)
    cov = np.cov(np.vstack([xs - cx, ys - cy]), aweights=w); vals, vecs = np.linalg.eigh(cov); vx, vy = vecs[:, np.argmax(vals)]
    ang = np.degrees(np.arctan2(vy, vx)); ang = ang - 180 if ang > 90 else ang + 180 if ang < -90 else ang
    if abs(ang) > 2:
        big = Image.new("RGBA", (im.width * 2, im.height * 2), (0, 0, 0, 0)); big.paste(im, (im.width // 2, im.height // 2))
        big = big.rotate(ang, resample=Image.BICUBIC, center=(big.width / 2, big.height / 2))
        bb = big.getchannel("A").point(lambda v: 255 if v > 3 else 0).getbbox(); big = big.crop((max(0, bb[0] - 6), max(0, bb[1] - 6), min(big.width, bb[2] + 6), min(big.height, bb[3] + 6)))
        big.save(rp); print("  %s ring levelled by %.1f degrees" % (tag, ang))
for f in os.listdir(fx):
    if f.startswith("hl_"): os.remove(os.path.join(fx, f))
for name, tag in PICK.items():
    shutil.copyfile(os.path.join(d, tag, name + ".png"), os.path.join(fx, name + ".png")); print("  %s <- %s (%s px)" % (name, tag, "x".join(map(str, Image.open(os.path.join(fx, name + ".png")).size))))
