"""Makes the Cleric's wand picture source/assets/wand.png (2026-11-22): the user's generated wand (cleric_wand_source.png) NARROWED row by row.

Every row of the cut-out is squeezed towards the wand's axis by a factor that is smooth from row to row:
  --shaft 0.58   the crystal, the cup and the shaft keep 58% of their width (the heights are untouched, so the item's Length and its grip point in the page do not change)
  --pommel 0.88  the round pommel keeps 88% (it must stay a ball: a smaller squeeze at the bottom, blended in over the rows above it)
0.58 and 0.88 are the thickness the user chose (the defaults below).

  python Animations/Cleric/source/make_wand_between.py [--shaft 0.58] [--pommel 0.88]     -> source/assets/wand.png (then: source/tools/embed_item_art.py, source/tools/build.py)
Needs pillow, numpy and scipy (and source/tools/cut_item.py).
"""
import argparse
import pathlib
import subprocess
import sys
import tempfile

import numpy as np
from PIL import Image
from scipy import ndimage as ndi

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SRC = HERE / "cleric_wand_source.png"
OUT = ROOT / "source" / "assets" / "wand.png"

ap = argparse.ArgumentParser()
ap.add_argument("--shaft", type=float, default=0.58)          # the user's choice (2026-11-22)
ap.add_argument("--pommel", type=float, default=0.88)
ap.add_argument("--ball-from", type=float, default=0.885, help="share of the height where the factor starts to grow towards the pommel's")
ap.add_argument("--ball-to", type=float, default=0.935, help="share of the height where the pommel's factor is reached")
ap.add_argument("--out", default=str(OUT))
a = ap.parse_args()

with tempfile.TemporaryDirectory() as td:
    cut = pathlib.Path(td) / "cut.png"
    subprocess.run([sys.executable, str(ROOT / "source" / "tools" / "cut_item.py"), str(SRC), str(cut), "--max-height", "1000"], check=True, stdout=subprocess.DEVNULL)
    im = Image.open(cut).convert("RGBA")
arr = np.asarray(im).astype(np.float32)
H, W = arr.shape[:2]
alpha = arr[..., 3] / 255.0

# the wand's axis: the middle of the shaft rows (the cup's horns are not symmetric)
rows = np.arange(int(H * 0.45), int(H * 0.80))
xs = [np.where(alpha[r] > 0.5)[0] for r in rows]
axis = float(np.mean([(x.min() + x.max()) / 2.0 for x in xs if len(x)]))

# the factor per row: shaft factor down to the ball, then a smooth blend to the pommel's
y = np.arange(H) / (H - 1.0)
t = np.clip((y - a.ball_from) / max(1e-6, a.ball_to - a.ball_from), 0, 1)
t = t * t * (3 - 2 * t)
f = a.shaft + (a.pommel - a.shaft) * t
f = ndi.gaussian_filter1d(f, 6)

# resample every row about the axis (premultiplied colour, so the outline has no halo)
pm = arr.copy()
pm[..., :3] *= alpha[..., None]
Wout = W
xo = np.arange(Wout, dtype=np.float32)
out = np.zeros_like(pm)
for yy in range(H):
    src = axis + (xo - axis) / f[yy]
    for c in range(4):
        out[yy, :, c] = np.interp(src, np.arange(W), pm[yy, :, c], left=0, right=0)
oa = out[..., 3] / 255.0
res = out.copy()
res[..., :3] = np.where(oa[..., None] > 1e-3, out[..., :3] / np.maximum(oa[..., None], 1e-3), 0)
img = Image.fromarray(np.clip(res, 0, 255).astype(np.uint8), "RGBA")
bbox = img.getchannel("A").point(lambda v: 255 if v > 8 else 0).getbbox()
img = img.crop((max(0, bbox[0] - 3), 0, min(Wout, bbox[2] + 3), H))
img.save(a.out)
print("wand", img.size, "shaft", a.shaft, "pommel", a.pommel, "axis", round(axis, 1), "->", a.out)
