#!/usr/bin/env python3
"""Checks a finished strip against the frame standard and draws it under the idle strip with alignment guides.

Prints, per frame: height of the figure, how far its lowest and highest points are above the ground line, its
left and right edge, the rear heel and front toe (the left-most and right-most point of the lowest 8%), and the
middle of the feet.  Also counts leftover magenta/purple pixels on the outline (a glow the cut did not remove).
Writes a picture: the idle on the first row, the strip on the second, on a dark background, with the guides
rear heel x=160 (red), middle of the feet x=248 (yellow), front toe x=336 (green) and the ground line (blue).

  python check_strip.py ../../Animations/Warrior/hit/armored_hit_6frame_strip.png --out hit_check.png

What good looks like: 512 px wide frames; the ground line 42 px above the bottom (y=470 of 512, y=598 of 640);
a standing figure about 408 px tall; the frames that should match the idle (first and last of a hit or dodge)
have the same height and the same heel and toe; "fringe" in the low hundreds or less.
Needs pillow and numpy.
"""
import argparse
import pathlib
import numpy as np
from PIL import Image, ImageDraw

ap = argparse.ArgumentParser()
ap.add_argument("strip")
ap.add_argument("--idle", default=str(pathlib.Path(__file__).resolve().parents[2] / "Animations" / "Warrior" / "idle" / "armored_idle_strip.png"),
                help="the idle strip to compare with (default: the warrior's)")
ap.add_argument("--frame", type=int, default=512, help="frame width in px")
ap.add_argument("--ground-from-bottom", type=int, default=42)
ap.add_argument("--out", default="")
a = ap.parse_args()

def measure(path):
    im = Image.open(path).convert("RGBA")
    arr = np.array(im).astype(int)
    h = im.size[1]
    n = im.size[0] // a.frame
    ground = h - a.ground_from_bottom
    rows = []
    for k in range(n):
        f = arr[:, k * a.frame:(k + 1) * a.frame]
        ys, xs = np.where(f[..., 3] > 128)
        if not len(ys):
            rows.append(None)
            continue
        low = ys > ys.max() - max(1, int(0.08 * (ys.max() - ys.min())))
        rows.append(dict(h=int(ys.max() - ys.min()), above=int(ground - ys.max()), top=int(ground - ys.min()),
                         x0=int(xs.min()), x1=int(xs.max()), heel=int(xs[low].min()), toe=int(xs[low].max())))
    r, g, b, al = arr[..., 0], arr[..., 1], arr[..., 2], arr[..., 3]
    fringe = int(((np.minimum(r, b) - g > 12) & (al > 20)).sum())
    return im, rows, h, n, ground, fringe

im, rows, H, n, ground, fringe = measure(a.strip)
print("%s: %d x %d, %d frames of %d px, ground line at y=%d, fringe pixels %d" % (pathlib.Path(a.strip).name, im.size[0], H, n, a.frame, ground, fringe))
print("frame  height  above-ground  top-above-ground  x-range      heel  toe  feet-mid")
for k, m in enumerate(rows):
    if m is None:
        print("%5d  (empty)" % (k + 1)); continue
    print("%5d  %6d  %12d  %16d  %3d-%-3d   %4d  %3d  %8d" % (k + 1, m["h"], m["above"], m["top"], m["x0"], m["x1"], m["heel"], m["toe"], (m["heel"] + m["toe"]) // 2))
if im.size[0] % a.frame:
    print("WARNING: the width is not a multiple of %d px" % a.frame)
if any(m and (m["x0"] <= 0 or m["x1"] >= a.frame - 1) for m in rows):
    print("WARNING: some frame touches the left or right edge (clipped?)")

try:
    idle, _, ih, _, _, _ = measure(a.idle)
    th = max(H, ih)
    sheet = Image.new("RGBA", (im.size[0], th * 2), (60, 64, 76, 255))
    sheet.alpha_composite(idle, (0, th - ih))
    sheet.alpha_composite(im, (0, th + th - H))
    d = ImageDraw.Draw(sheet)
    for row in range(2):
        gy = row * th + th - a.ground_from_bottom
        for k in range(im.size[0] // a.frame):
            x0 = k * a.frame
            d.line([(x0 + 160, row * th), (x0 + 160, row * th + th)], fill=(255, 80, 80, 255))
            d.line([(x0 + 248, row * th), (x0 + 248, row * th + th)], fill=(255, 255, 80, 120))
            d.line([(x0 + 336, row * th), (x0 + 336, row * th + th)], fill=(80, 255, 80, 255))
            d.line([(x0, gy), (x0 + a.frame, gy)], fill=(80, 160, 255, 255))
            d.rectangle([x0, row * th, x0 + a.frame - 1, row * th + th - 1], outline=(255, 255, 255, 70))
    out = a.out or ("check_" + pathlib.Path(a.strip).stem + ".png")
    scale = min(1.0, 2000.0 / sheet.size[0])
    sheet.convert("RGB").resize((int(sheet.size[0] * scale), int(sheet.size[1] * scale)), Image.LANCZOS).save(out)
    print("wrote", out)
except FileNotFoundError:
    print("(no idle strip found for the comparison picture; use --idle)")
