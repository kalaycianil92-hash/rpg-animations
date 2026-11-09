#!/usr/bin/env python3
"""Compares slime looks on the Glimmerwood stage next to the warrior (2026-11-07, the re-look candidates).
Takes any number of  label=cut.png  pairs (512 x 512 cells made by slice_keypose_sheet.py with --base-width 350 --feet-x 256)
and writes docs/relook_compare.png: for each look one row of the stage with the page's DEFAULT Stage blend (grade, soft shadow),
the same without any blend, and a 3x close-up of the slime.
  python source/tools/dev/relook_compare.py old=a.png gemini=b.png gpt=c.png
"""
import sys
import numpy as np
from PIL import Image, ImageDraw
sys.path.insert(0, "source/tools/dev")
import blend_test as b

SAT_W, SAT_M, LIFT, TINT, BRIGHT = .90, .92, .08, .60, .98     # the page's defaults

def graded(im, sat):
    tint = tuple(1 + TINT * (v - 1) for v in (0.93, 0.97, 0.90))
    return b.grade(im, sat * 1.0, tint=tint, bright=BRIGHT, lift=LIFT * 4.4)   # b.grade's lift is a 0..1 weight on dark pixels only, the page's is a flat fade: x4.4 is close for the darkest pixels

def row(slime_path, blend):
    bg = b.stage()
    war = b.frame("Animations/Warrior/idle/armored_idle_strip.png", 0)
    sli = Image.open(slime_path).convert("RGBA")
    if blend:
        war = graded(war, SAT_W); sli = graded(sli, SAT_M)
    b.place(bg, war, 0.03 * b.W, False, 120, blend, 0)
    b.place(bg, sli, 0.03 * b.W, True, 190, blend, 0)
    return bg.crop((0, int(190 * b.S), bg.width, bg.height)).convert("RGB")

def closeup(slime_path):
    # the slime as the page shows it (184 px unit, mirrored), then 3x
    sli = Image.open(slime_path).convert("RGBA").resize((184, 184), Image.LANCZOS).transpose(Image.FLIP_LEFT_RIGHT)
    bg = Image.new("RGBA", sli.size, (60, 96, 52, 255)); bg.alpha_composite(sli)
    return bg.resize((184 * 3, 184 * 3), Image.NEAREST).convert("RGB")

items = [a.split("=", 1) for a in sys.argv[1:]]
rows = []
for label, path in items:
    r1, r2, c = row(path, True), row(path, False), closeup(path)
    W = r1.width
    block = Image.new("RGB", (W, r1.height + r2.height + 8), (255, 255, 255))
    block.paste(r1, (0, 0)); block.paste(r2, (0, r1.height + 8))
    rows.append((label, block, c))

H = sum(bl.height for _, bl, _ in rows) + 12 * len(rows)
W = rows[0][1].width + rows[0][2].width + 8
out = Image.new("RGB", (W, H), (255, 255, 255))
d = ImageDraw.Draw(out); y = 0
for label, bl, c in rows:
    out.paste(bl, (0, y)); out.paste(c, (bl.width + 8, y))
    d.rectangle([6, y + 6, 110, y + 26], fill=(0, 0, 0)); d.text((12, y + 10), label + "  (blend on / off)", fill=(255, 255, 255))
    y += bl.height + 12
out.save("docs/relook_compare.png")
print("saved", out.size)
