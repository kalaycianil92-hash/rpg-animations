"""Arena props, a fixed composition (the user's request, 2026-11-03): five pieces in this order, left to right: cold fire basket, armour stand, gong,
armour stand, cold fire basket; equal gaps between neighbours (measured between the pieces' own edges) and the gong at the exact centre. The pieces are
cut from the untouched props_1.png (their own columns are copied whole, so every piece keeps its height and its base line); the right pair is the left
pair mirrored, so the whole set is symmetrical about the gong.

Run from the project folder, then cut the result (--no-seam: the composition is one picture, never repeated):
  python source/tools/dev/compose_arena_props.py
  python source/tools/make_bg_layer.py source/assets/bg/arena/originals/props_1_fixed.png --key --mute-pink --no-seam --out source/assets/bg/arena/props.png

The page draws this layer once, centred on the stage (the file source/assets/bg/arena/centered.txt names it), so the gong stands at the stage's centre
whatever the stage's width.

The objects of props_1.png, left to right (1-based): 1 banner standard, 2 weapon rack with shields, 3 straw dummy, 4 straw archery target, 5 armour
stand with shields, 6 gong, 7 signal horn, 8 fire basket, 9 pile of arms.
"""
import pathlib
import numpy as np
from PIL import Image

D = pathlib.Path(__file__).resolve().parents[2] / "assets/bg/arena/originals"
GAP, MARGIN = 100, 40                               # px of the original picture: between neighbours, and the empty edge of the picture (at the desktop stage the set is about 650 px wide)

im = np.array(Image.open(D / "props_1.png").convert("RGB"))
d = np.minimum(im[..., 0].astype(int), im[..., 2]) - im[..., 1]
mag = d > 150
M = np.median(im[mag], axis=0).astype(np.uint8)     # the magenta this picture really has

occ = (~mag).sum(axis=0) > 6                        # columns that have art in them
runs, x = [], 0
while x < len(occ):
    if occ[x]:
        x0 = x
        while x < len(occ) and occ[x:x + 14].any():  # a gap narrower than 14 px belongs to the same object
            x += 1
        runs.append((x0, x - 1))
    x += 1
assert len(runs) == 9, runs


def piece(k, mirror):
    a, b = runs[k - 1]
    p = im[:, a:b + 1]
    return p[:, ::-1] if mirror else p


basket_l, armour_l, gong, armour_r, basket_r = piece(8, False), piece(5, False), piece(6, False), piece(5, True), piece(8, True)
wg = gong.shape[1]; half = wg // 2
left_ext = half + GAP + armour_l.shape[1] + GAP + basket_l.shape[1] + MARGIN
right_ext = (wg - half) + GAP + armour_r.shape[1] + GAP + basket_r.shape[1] + MARGIN
W, H = left_ext + right_ext, im.shape[0]
out = np.tile(M, (H, W, 1))


def put(p, x):
    out[:, x:x + p.shape[1]] = p
    return x, x + p.shape[1]


g0, g1 = put(gong, left_ext - half)                 # the gong first: its middle is the picture's middle
a0, _ = put(armour_l, g0 - GAP - armour_l.shape[1])
put(basket_l, a0 - GAP - basket_l.shape[1])
_, a1 = put(armour_r, g1 + GAP)
put(basket_r, a1 + GAP)
Image.fromarray(out).save(D / "props_1_fixed.png")
print("composed %d x %d | gong middle at column %.1f, picture middle at %.1f | gaps %d, margins %d" % (W, H, (g0 + g1 - 1) / 2, (W - 1) / 2, GAP, MARGIN))
