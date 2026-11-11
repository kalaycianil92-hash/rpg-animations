#!/usr/bin/env python3
"""Cuts the Slime King's treasure pile picture (the user's generated PNG/JPG on flat magenta, 2026-11-11) into source/assets/fx/treasure_pile.png, which the page draws behind the King (fbTex.treasure_pile, normal
blending; until the file exists the page paints a stand-in with code, kingPileTex).

  python Animations/SlimeKing/source/cut_treasure.py inbox/slime_king_treasure_pile.png

The magenta is keyed like the sprites' (alpha = 1 - clip((min(r, b) - g - 70) / 110, 0, 1), the soft edges despilled), the picture is trimmed to the pile's bounding box (with 2 px of margin) and scaled down to at most 960 px
wide (the page draws it about 340 px wide on a normal stage), and it is also saved in treasure_pile/ with a white and a green check picture. The page takes the pile's aspect from the file, so any shape works; about 2.4 : 1 is
what the prompt asks for.
"""
import os, sys
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
KING = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(KING, "..", ".."))

src = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "inbox", "slime_king_treasure_pile.png")
if not os.path.isabs(src): src = os.path.join(ROOT, src)
im = Image.open(src).convert("RGB")
arr = np.array(im).astype(float)
r, g, b = arr[..., 0], arr[..., 1], arr[..., 2]
alpha = 1 - np.clip((np.minimum(r, b) - g - 70) / 110, 0, 1)
soft = alpha < 1
rgb = arr.copy()
rgb[..., 0] = np.where(soft, np.minimum(r, g + 25), r); rgb[..., 2] = np.where(soft, np.minimum(b, g + 25), b)
out = np.dstack([rgb, alpha * 255]).astype(np.uint8)
ys, xs = np.where(out[..., 3] > 128)
x0, x1, y0, y1 = max(0, xs.min() - 2), min(out.shape[1], xs.max() + 3), max(0, ys.min() - 2), min(out.shape[0], ys.max() + 3)
pile = Image.fromarray(out[y0:y1, x0:x1], "RGBA")
if pile.width > 960: pile = pile.resize((960, int(round(pile.height * 960 / pile.width))), Image.LANCZOS)
fx = os.path.join(ROOT, "source", "assets", "fx"); os.makedirs(fx, exist_ok=True)
path = os.path.join(fx, "treasure_pile.png"); pile.save(path)
d = os.path.join(KING, "treasure_pile"); os.makedirs(os.path.join(d, "source"), exist_ok=True)
pile.save(os.path.join(d, "treasure_pile.png"))
W, H = pile.size; pic = Image.new("RGB", (W * 2, H), (255, 255, 255))
for i, bg in enumerate([(255, 255, 255, 255), (38, 84, 52, 255)]):
    c = Image.new("RGBA", (W, H), bg); c.alpha_composite(pile); pic.paste(c.convert("RGB"), (i * W, 0))
pic.resize((W, H // 2), Image.LANCZOS).save(os.path.join(d, "treasure_pile_check.png"))
print("pile %d x %d (aspect %.2f) -> %s" % (W, H, H / float(W), os.path.relpath(path, ROOT)))
