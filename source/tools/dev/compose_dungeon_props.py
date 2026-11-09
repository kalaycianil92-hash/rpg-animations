"""Dungeon props, the three fixed looks (2026-11-03): Rootgate, Vigil Hall and Throne of Roots. Each props_1.png holds a few separate cut-outs in a row; this
lays the chosen ones out again as ONE picture whose middle is the middle of the stage (the page draws such a layer once, centred; centered.txt names it).
The pieces are copied whole from the untouched originals/props_1.png (so they keep their size and shape), their bases are put on one line at 74% of the
picture height (the usual depth of the props) and each piece stands at an offset from the stage's centre, given in px of the desktop stage (760 px wide).

Run from the project folder, then cut each result (--no-seam: it is one picture, never repeated):
  python source/tools/dev/compose_dungeon_props.py
  python source/tools/make_bg_layer.py source/assets/bg/<scene>/originals/props_1_fixed.png --key --mute-pink --no-seam --out source/assets/bg/<scene>/props.png

Pieces are counted left to right in props_1.png (1-based):
  dungeon_gate: 1 cold brazier, 2 fallen pillar, 3 mossy wayside shrine, 4 root-wrapped boulder
  dungeon_rest: 1 fire pit with a pot, 2 two bedrolls (one piece), 3 crates and barrel, 4 table and stool, 5 lantern post
  dungeon_boss: 1 brazier column, 2 heap of bones and armour, 3 pillar stump with chains, 4 tilted sarcophagus
"""
import pathlib
import numpy as np
from PIL import Image

ASSETS = pathlib.Path(__file__).resolve().parents[2] / "assets/bg"
DESKTOP_STAGE_H = 340                      # css px: the stage's base height on a desktop; a picture of height H is drawn at this height, so 1 css px = H / 340 picture px
BASE = 0.74                                # where the pieces' bases stand, as a share of the picture's height
MARGIN = 40                                # empty px at the picture's edges

# (piece number, mirrored?, offset of the piece's middle from the stage's middle in css px at the desktop size)
LAYOUTS = {
    "dungeon_gate": [(3, False, -150), (1, False, -10)],
    "dungeon_rest": [(3, False, -305), (2, False, -150), (1, False, 0), (4, False, 140), (5, False, 270)],
    "dungeon_boss": [(1, False, -290), (2, False, -160), (4, False, 0), (3, False, 150), (1, True, 290)],
}


def runs_of(mask_not_magenta, gap=14):
    occ = mask_not_magenta.sum(axis=0) > 6
    runs, x = [], 0
    while x < len(occ):
        if occ[x]:
            x0 = x
            while x < len(occ) and occ[x:x + gap].any():
                x += 1
            runs.append((x0, x - 1))
        x += 1
    return runs


for scene, layout in LAYOUTS.items():
    d = ASSETS / scene / "originals"
    im = np.array(Image.open(d / "props_1.png").convert("RGB"))
    keymask = (np.minimum(im[..., 0].astype(int), im[..., 2]) - im[..., 1]) > 150
    M = np.median(im[keymask], axis=0).astype(np.uint8)
    runs = runs_of(~keymask)
    H = im.shape[0]
    k = H / DESKTOP_STAGE_H                # picture px per css px
    pieces = []
    for num, mirror, off in layout:
        a, b = runs[num - 1]
        p = im[:, a:b + 1]
        rows = np.where((~keymask[:, a:b + 1]).sum(axis=1) > 3)[0]
        p = p[:, ::-1] if mirror else p
        pieces.append((p, rows.max(), off * k))
    half = int(max(abs(c) + p.shape[1] / 2 for p, _, c in pieces)) + MARGIN
    W = 2 * half
    out = np.tile(M, (H, W, 1))
    yb = int(round(BASE * H))
    for p, bottom, c in pieces:
        x0 = int(round(half + c - p.shape[1] / 2)); dy = yb - bottom
        r0, r1 = max(0, dy), min(H, H + dy)
        out[r0:r1, x0:x0 + p.shape[1]] = p[r0 - dy:r1 - dy]
    Image.fromarray(out).save(d / "props_1_fixed.png")
    print("%-13s %d x %d, %d pieces, bases at %d%% (row %d)" % (scene, W, H, len(pieces), round(100 * BASE), yb))
