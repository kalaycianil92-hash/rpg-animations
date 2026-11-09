#!/usr/bin/env python3
"""Draws a stick-figure pose guide (side view, facing right) to attach to an image generator.
RED = the swinging (weapon) arm, BLUE = the guard arm, grey = body. Poses are lists of joint
coordinates inside a 512x512 panel, ground line at y=470.  Edit POSES to make a new guide.

  python stick_figure_guide.py out.png --cols 4 --rows 2
"""
import argparse
from PIL import Image, ImageDraw

G = dict(hip=(245, 262), neck=(248, 138), head=(252, 98), rk=(195, 362), ra=(160, 452), rt=(205, 470),
         fk=(305, 355), fa=(335, 452), ft=(380, 470),
         sw=[(246, 150), (288, 190), (336, 168)], gd=[(244, 152), (256, 225), (292, 230)])
POSES = [
    G,
    dict(hip=(238, 262), neck=(232, 138), head=(232, 98), rk=(190, 365), ra=(150, 452), rt=(195, 470),
         fk=(295, 352), fa=(330, 452), ft=(375, 470), sw=[(234, 150), (200, 180), (205, 125)], gd=[(236, 152), (262, 215), (300, 195)]),
    dict(hip=(235, 262), neck=(222, 138), head=(220, 98), rk=(190, 365), ra=(150, 452), rt=(195, 470),
         fk=(295, 352), fa=(330, 452), ft=(375, 470), sw=[(224, 150), (165, 115), (190, 55)], gd=[(226, 152), (255, 215), (293, 190)]),
    dict(hip=(250, 272), neck=(262, 142), head=(268, 102), rk=(195, 372), ra=(135, 452), rt=(175, 470),
         fk=(320, 350), fa=(340, 452), ft=(386, 470), sw=[(262, 152), (292, 98), (342, 76)], gd=[(262, 155), (285, 215), (320, 195)]),
    dict(hip=(255, 285), neck=(312, 168), head=(338, 138), rk=(188, 378), ra=(108, 455), rt=(148, 470),
         fk=(352, 342), fa=(346, 452), ft=(396, 470), sw=[(312, 178), (362, 228), (418, 288)], gd=[(308, 182), (282, 240), (320, 214)]),
    dict(hip=(262, 290), neck=(332, 186), head=(358, 158), rk=(205, 382), ra=(140, 432), rt=(118, 470),
         fk=(352, 345), fa=(350, 452), ft=(398, 470), sw=[(328, 196), (352, 268), (378, 334)], gd=[(326, 202), (300, 252), (336, 238)]),
    dict(hip=(255, 275), neck=(290, 150), head=(305, 112), rk=(195, 372), ra=(135, 452), rt=(178, 470),
         fk=(325, 350), fa=(342, 452), ft=(388, 470), sw=[(288, 162), (310, 225), (345, 262)], gd=[(286, 164), (268, 225), (305, 205)]),
    G,
]

ap = argparse.ArgumentParser(); ap.add_argument("dst"); ap.add_argument("--cols", type=int, default=4); ap.add_argument("--rows", type=int, default=2)
a = ap.parse_args()
S, N = 2, 512
GR, RED, BLUE = (110, 110, 120), (220, 40, 40), (40, 90, 220)
out = Image.new("RGB", (N * a.cols * S, N * a.rows * S), (238, 238, 238)); d = ImageDraw.Draw(out)
for k, p in enumerate(POSES[:a.cols * a.rows]):
    r, c = divmod(k, a.cols); ox, oy = c * N, r * N
    sh = lambda pts: [(x + ox, y + oy) for x, y in pts]
    def L(pts, col, w):
        pts = [(x * S, y * S) for x, y in pts]; d.line(pts, fill=col, width=w * S, joint="curve")
        for x, y in (pts[0], pts[-1]): d.ellipse((x - w * S / 2, y - w * S / 2, x + w * S / 2, y + w * S / 2), fill=col)
    d.line(((ox + 10) * S, (oy + 470) * S, (ox + N - 10) * S, (oy + 470) * S), fill=(170, 170, 170), width=2 * S)
    if c: d.line((ox * S, oy * S, ox * S, (oy + N) * S), fill=(200, 200, 200), width=2 * S)
    if r: d.line((ox * S, oy * S, (ox + N) * S, oy * S), fill=(200, 200, 200), width=2 * S)
    L(sh([p["hip"], p["rk"], p["ra"], p["rt"]]), GR, 14); L(sh([p["hip"], p["fk"], p["fa"], p["ft"]]), GR, 14)
    L(sh([p["hip"], p["neck"]]), GR, 26)
    hx, hy = p["head"][0] + ox, p["head"][1] + oy
    d.ellipse(((hx - 30) * S, (hy - 30) * S, (hx + 30) * S, (hy + 30) * S), outline=GR, width=6 * S, fill=(238, 238, 238))
    d.polygon([((hx + 30) * S, (hy - 4) * S), ((hx + 46) * S, (hy + 6) * S), ((hx + 30) * S, (hy + 12) * S)], fill=GR)  # nose: facing right
    L(sh([p["neck"], (p["head"][0], p["head"][1] + 30)]), GR, 10)
    L(sh(p["gd"]), BLUE, 14); L(sh(p["sw"]), RED, 14)
    for col, pt in ((RED, p["sw"][-1]), (BLUE, p["gd"][-1])):
        x, y = pt[0] + ox, pt[1] + oy; d.ellipse(((x - 14) * S, (y - 14) * S, (x + 14) * S, (y + 14) * S), fill=col)
out.resize((N * a.cols, N * a.rows), Image.LANCZOS).save(a.dst)
