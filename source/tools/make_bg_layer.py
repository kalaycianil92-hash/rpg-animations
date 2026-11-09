#!/usr/bin/env python3
"""Turns one or more generated background pictures into ONE layer that repeats sideways without a visible seam.

Gemini cannot match a picture's left edge to its right edge, so the edges are made to meet by cutting a seam: the last
stretch of the strip and its first stretch are laid over each other and the picture switches from one to the other
along the path where they differ least (a vertical, wandering line that finds its way between the trunks, not through
them). With several pictures they are joined end to end the same way (a longer forest repeats less) and the last one
is joined to the first.

Usage:
  python make_bg_layer.py inbox/forest_far.png --out ../assets/bg/forest/far.jpg
  python make_bg_layer.py inbox/forest_ground.png --key --out ../assets/bg/forest/ground.png
  python make_bg_layer.py a.png b.png c.png --key --out ../assets/bg/forest/mid.png

--key       the picture is on flat magenta (#FF00FF): remove it. Unlike the sprite cutters this un-mixes the magenta from the edge pixels
            (it measures the picture's own magenta, makes each edge pixel as transparent as it is magenta and puts back the leaf or bark
            colour under it), so thin ferns and branches keep their painted edge and lose the pink
--mute-pink with --key: pixels that are pink, magenta or violet but belong to the art (Gemini paints pink stains, blossoms and glows even when the
            prompt says none) keep only an eighth of their colour. Use it where no pink is meant (the ashfall and warhorn acts); do not use it where
            pink is part of the picture (a pink lantern glass, pink flowers)
--lift N    with --key: move everything UP by N percent of the picture's height. For a props picture whose objects stand too low on the floor (the props'
            bases should be at about 71 to 76% of the height, a little below the floor's far edge at 62%; Mistwood's came out at about 80% and was lifted 6.3)
--no-seam   no wrap-around seam: the strip is used as it is and simply repeats (for a keyed picture whose first and last columns are empty, like a props
            row with margins at both ends). The normal seam lays the end over the start and picks the emptier side where they differ, so it can drop an
            object that stands near an end (it dropped Mistwood's bird-skull totem once); with this flag nothing is cut or merged
--height    every picture is scaled to this height first (default 768; the page draws the far and trunk layers up to about 650 px high)
--overlap   how much of one picture's width the seam may wander in (default 0.2)
--out       .jpg for a layer without transparency (smaller), .png for a keyed one
The page needs the three files far, ground and mid in assets/bg/forest/ (build.py inlines them).
"""
import argparse, os
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

ap = argparse.ArgumentParser()
ap.add_argument("src", nargs="+")
ap.add_argument("--out", required=True)
ap.add_argument("--key", action="store_true")
ap.add_argument("--height", type=int, default=768)
ap.add_argument("--overlap", type=float, default=0.2)
ap.add_argument("--despill-band", type=int, default=3)
ap.add_argument("--despill-thr", type=float, default=0)
ap.add_argument("--mute-pink", action="store_true")
ap.add_argument("--lift", type=float, default=0)
ap.add_argument("--no-seam", action="store_true")
a = ap.parse_args()


def load(path):
    im = Image.open(path).convert("RGB")
    if not a.key:
        return im.resize((round(im.width * a.height / im.height), a.height), Image.LANCZOS)
    img = np.array(im).astype(float)
    r, g, b = img[..., 0], img[..., 1], img[..., 2]
    d = np.minimum(r, b) - g                                               # about 255 on magenta, 0 or less on leaves, bark and dirt
    sel = d > 150
    M = np.median(img[sel], axis=0) if sel.sum() > 1000 else np.array([255., 0., 255.])   # the magenta this picture really has
    lin = np.clip(1 - np.maximum(d, 0) / (min(M[0], M[2]) - M[1]), 0, 1)   # how much of a pixel is not magenta
    lin = np.where(lin < .12, 0, lin)                                      # the generator's noise on the flat colour
    edge = ndi.binary_dilation(lin < .5, iterations=a.despill_band)        # the silhouette: transparent pixels and the few px next to them
    alpha = np.where(edge, lin, 1.)                                        # (inside the art nothing becomes see-through, even a purple flower)
    # An edge pixel is leaf mixed with magenta: take the magenta out of it (pixel = a * leaf + (1 - a) * magenta) so the dark painted edge stays and the pink goes.
    rgb = np.where(edge[..., None], np.clip((img - (1 - alpha)[..., None] * M) / np.maximum(alpha, 1e-3)[..., None], 0, 255), img)
    fix = edge & (np.minimum(rgb[..., 0], rgb[..., 2]) - rgb[..., 1] > a.despill_thr)   # what pink is left
    rgb[..., 0] = np.where(fix, np.minimum(rgb[..., 0], rgb[..., 1] + a.despill_thr), rgb[..., 0])
    rgb[..., 2] = np.where(fix, np.minimum(rgb[..., 2], rgb[..., 1] + a.despill_thr), rgb[..., 2])
    if a.mute_pink:                                                        # pink, magenta and violet INSIDE the art (opaque, so the key cannot take them out)
        pink = (np.minimum(rgb[..., 0], rgb[..., 2]) - rgb[..., 1] > 18) & (alpha > .2)
        lum = (0.3 * rgb[..., 0] + 0.59 * rgb[..., 1] + 0.11 * rgb[..., 2])[..., None]
        rgb = np.where(pink[..., None], lum + (rgb - lum) * 0.12, rgb)    # keeps an eighth of their colour: dull, not a hole and not a hot spot
    if a.lift:                                                             # everything moves up by this share of the picture's height (the empty top is cut, the bottom stays empty)
        n = int(round(rgb.shape[0] * a.lift / 100))
        rgb = np.roll(rgb, -n, axis=0); alpha = np.roll(alpha, -n, axis=0)
        rgb[-n:] = 0; alpha[-n:] = 0
    im = Image.fromarray(np.dstack([np.clip(rgb, 0, 255), alpha * 255]).astype(np.uint8), "RGBA")
    return im.resize((round(im.width * a.height / im.height), a.height), Image.LANCZOS)


def merge(A, B):
    """A and B are the same stretch of two pictures: A on the left of a seam, B on the right of it, along the cheapest path."""
    pa, pb = A.copy(), B.copy()
    if A.shape[2] == 4:                                                    # a see-through pixel has no colour of its own
        pa[..., :3] *= A[..., 3:] / 255; pb[..., :3] *= B[..., 3:] / 255
    cost = ((pa - pb) ** 2).sum(axis=2)
    h, w = cost.shape
    e = cost.copy()
    for y in range(1, h):                                                  # cheapest way down to each pixel
        up = e[y - 1]
        e[y] += np.minimum(np.minimum(np.r_[up[0], up[:-1]], up), np.r_[up[1:], up[-1]])
    path = np.zeros(h, int)
    path[-1] = e[-1].argmin()
    for y in range(h - 2, -1, -1):                                         # and back up
        x = path[y + 1]
        lo, hi = max(0, x - 1), min(w, x + 2)
        path[y] = lo + e[y, lo:hi].argmin()
    wb = np.clip((np.arange(w)[None, :] - path[:, None]) / 6 + 0.5, 0, 1)[..., None]   # 0 = A, 1 = B, feathered over a few px
    return A * (1 - wb) + B * wb


def join(left, right, o):
    return np.concatenate([left[:, :-o], merge(left[:, -o:], right[:, :o]), right[:, o:]], axis=1)


ims = [np.array(load(p)).astype(float) for p in a.src]
o = int(ims[0].shape[1] * a.overlap)
strip = ims[0]
for nxt in ims[1:]:
    strip = join(strip, nxt, o)
if a.no_seam:
    tile = strip                                                       # no merge: the end is followed by the start as it is
    if strip.shape[2] == 4 and ((strip[:, :3, 3] > 20).sum() > 12 or (strip[:, -3:, 3] > 20).sum() > 12):
        print("WARNING: --no-seam, but the first or last columns are not empty: an object touches the edge and will be cut where the strip repeats")
else:
    tile = np.concatenate([merge(strip[:, -o:], strip[:, :o]), strip[:, o:-o]], axis=1)   # the end now runs on into the start
tile = np.clip(tile + 0.5, 0, 255).astype(np.uint8)

# Check: the jump between the last and first column against the usual jump between neighbouring columns.
f = tile.astype(float)
if f.shape[2] == 4:
    f[..., :3] *= f[..., 3:] / 255
jump = np.abs(f[:, 0] - f[:, -1]).mean()
usual = np.abs(np.diff(f, axis=1)).mean()
print("tile", tile.shape[1], "x", tile.shape[0], "| jump at the seam %.2f, usual %.2f" % (jump, usual))

os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)                  # (a new act's folder does not exist yet)
out = Image.fromarray(tile, "RGBA" if tile.shape[2] == 4 else "RGB")
if a.out.lower().endswith((".jpg", ".jpeg")):
    out.convert("RGB").save(a.out, quality=88)
else:
    out.save(a.out, optimize=True)
print("wrote", a.out)
