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
