#!/usr/bin/env python3
"""Cuts the fire slime's idle sheet (the user's Gemini JPG, 2528 x 1696, 3 x 2 panels) into the 6-frame strip.

Why not just slice_keypose_sheet.py: the generator drew the tall flame of panel 5 and its top ember ABOVE the
middle line of the sheet (y 812 to 842, the middle line is y 848), so an equal 2-row split would give that ember to
panel 2 and keep it there (--keep-near). This script moves the row split to y = SPLIT (empty space between the
top row's lowest point, y 717, and that ember, y 812), pads the top row with magenta to the same height as the
bottom row, writes one equal-cell sheet and calls the cutter.

Run from the project folder:
  python Animations/Slime/idle/source/make_fire_idle_strip.py
Output: Animations/Slime/idle/fire_idle_strip.png (6 frames, 512 x 512) and a scratch sheet next to this script.
"""
import subprocess, sys, os
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
SRC = os.path.join(ROOT, "Animations", "Slime", "idle", "source", "slime_fire_idle_sheet.jpg")
SHEET = os.path.join(HERE, "slime_fire_idle_sheet_equalcells.png")
OUT = os.path.join(ROOT, "Animations", "Slime", "idle", "old", "first_glossy", "fire_idle_strip.png")   # (the first, glossy idle; since 2026-11-07 the official strip is the calm Gemini v4 sheet)
SPLIT = 765

img = Image.open(SRC).convert("RGB")
W, H = img.size
top = img.crop((0, 0, W, SPLIT))
bot = img.crop((0, SPLIT, W, H))
cell_h = max(top.height, bot.height)
sheet = Image.new("RGB", (W, cell_h * 2), (255, 0, 255))
sheet.paste(top, (0, 0))
sheet.paste(bot, (0, cell_h))
sheet.save(SHEET)

extra = sys.argv[1:]
cmd = [sys.executable, os.path.join(ROOT, "source", "tools", "slice_keypose_sheet.py"), SHEET, OUT,
       "--cols", "3", "--rows", "2", "--base-width", "350", "--scale-from", "panel1",
       # the generator drew the bottom row about 7% bigger than panels 1 and 2 (a template match of panel 1's face
       # gave 1.00, 1.01, 1.03, 1.07, 1.07, 1.08); one shared scale on panel 1's base (622 px -> 350 px) and these
       # per-panel corrections (1 / face scale) make the face the same size in every frame
       "--scale-mult", "1,0.99,0.97,0.935,0.935,0.926",
       "--keep-near", "0.25", "--modes", "feet", "--feet-x", "256",
       "--despill-band", "10", "--despill-thr", "4"] + extra
print(" ".join(cmd))
subprocess.run(cmd, check=True)
