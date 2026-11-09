"""Mistwood props without the stake fence and the rope snare (the user's request, 2026-11-02).

Run from the project folder, then cut the result with the tool:
  python source/tools/dev/compose_mistwood_props.py
  python source/tools/make_bg_layer.py source/assets/bg/mistwood/originals/props_1_no_fence_snare.png --key --lift 6.3 --overlap 0.05 --out source/assets/bg/mistwood/props.png

Why not just paint the two objects over with magenta and cut as before: make_bg_layer.py joins the end of a picture onto its start along a
wandering seam, and with the fence gone the start was empty, so the seam took the empty side and dropped the bird-skull totem at the end.
Here the seven kept objects are laid out again (their own gaps kept) between empty margins, and a small --overlap lets the seam run through
nothing. The original, props_1.png, is not touched.
"""
import pathlib
import numpy as np
from PIL import Image

D = pathlib.Path(__file__).resolve().parents[2] / "assets/bg/mistwood/originals"
im = np.array(Image.open(D / "props_1.png").convert("RGB"))
d = np.minimum(im[..., 0].astype(int), im[..., 2]) - im[..., 1]
mag = d > 150
M = np.median(im[mag], axis=0).astype(np.uint8)                      # the magenta this picture really has

occ = (~mag).sum(axis=0) > 6                                         # columns that have art in them
runs, x = [], 0
while x < len(occ):
    if occ[x]:
        x0 = x
        while x < len(occ) and occ[x:x + 14].any():                  # a gap narrower than 14 px belongs to the same object
            x += 1
        runs.append((x0, x - 1))
    x += 1
assert len(runs) == 9, runs                                          # 1 stake fence, 2 trap, 3 crate, 4 horned totem, 5 pot, 6 sacks, 7 lantern post, 8 rope snare, 9 bird-skull totem

PAD, GAP, MARGIN = 30, 90, 110                                       # px of the original picture
seg1 = im[:, runs[1][0] - PAD:runs[6][1] + PAD + 1]                  # objects 2 to 7
seg2 = im[:, runs[8][0] - PAD:runs[8][1] + PAD + 1]                  # object 9
fill = lambda w: np.tile(M, (im.shape[0], w, 1))
out = np.concatenate([fill(MARGIN), seg1, fill(GAP), seg2, fill(MARGIN)], axis=1)
Image.fromarray(out).save(D / "props_1_no_fence_snare.png")
print("composed", out.shape[1], "x", im.shape[0])
