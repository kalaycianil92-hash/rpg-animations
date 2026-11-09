#!/usr/bin/env python3
"""Draws a strip with its hand marks and item pictures into one picture, the way the test page does, to check marks without opening the browser.

  python preview_marks.py <strip.png> <strip.hand-anchors.json> <main item.png> <off item.png> <out.png> [--cols 3]

main item = the picture for the main track (far hand), off item = the picture for the off track (near hand).
Draw order as in the page: items behind the body (front=false), the body, items in front, then the hand drawn over each
item in front whose overlay is on (here: the skin-coloured pixels of the fist near the mark, a simplified copy of the page's rule).
Needs pillow, numpy and scipy.
"""
import argparse
import json
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

ap = argparse.ArgumentParser()
ap.add_argument("strip"); ap.add_argument("marks"); ap.add_argument("main_item"); ap.add_argument("off_item"); ap.add_argument("out")
ap.add_argument("--cols", type=int, default=3)
a = ap.parse_args()

strip = Image.open(a.strip).convert("RGBA")
doc = json.load(open(a.marks, encoding="utf-8"))
ch = doc["characters"][0]; an = ch["animations"][0]
cfg = {"main": ch["items"]["main"], "off": an["offItem"]}
pics = {"main": Image.open(a.main_item).convert("RGBA"), "off": Image.open(a.off_item).convert("RGBA")}
W = 512; H = strip.size[1]; n = strip.size[0] // W
rad = round(ch.get("fist", 0.09) * W)

def draw_item(canvas, tk, m):
    c = cfg[tk]; pic = pics[tk]
    h = c["length"] * W; s = h / pic.size[1]
    it = pic.resize((max(1, round(pic.size[0] * s * m.get("w", 1))), max(1, round(h))), Image.LANCZOS)
    R = int(max(it.size) * 1.5)
    box = Image.new("RGBA", (2 * R, 2 * R), (0, 0, 0, 0))
    box.alpha_composite(it, (R - it.size[0] // 2, R - round(c["pivot"] * it.size[1])))     # the grip point sits at the centre of the box
    box = box.rotate(-m["a"], resample=Image.BICUBIC)                                       # canvas angles are clockwise
    canvas.alpha_composite(box, (round(m["x"] * W) - R, round(m["y"] * H) - R))

def hand_layer(frame, m):
    arr = np.array(frame).astype(int)
    r, g, b = [arr[..., i] / 255.0 for i in range(3)]
    mx, mn = np.maximum(np.maximum(r, g), b), np.minimum(np.minimum(r, g), b)
    d = mx - mn + 1e-9
    hh = np.where(mx == r, ((g - b) / d) % 6, np.where(mx == g, (b - r) / d + 2, (r - g) / d + 4)) * 60
    ss = np.where(mx > 0, (mx - mn) / (mx + 1e-9), 0)
    skin = (arr[..., 3] > 200) & (hh > 6) & (hh < 24) & (ss > 0.2) & (ss < 0.55) & (mx > 0.72)
    yy, xx = np.mgrid[0:H, 0:W]
    circ = (xx - m["x"] * W) ** 2 + (yy - m["y"] * H) ** 2 <= rad ** 2
    lab, k = ndi.label(skin & circ)
    if not k:
        return None
    l0 = lab[int(round(m["y"] * H)), int(round(m["x"] * W))]
    if l0 == 0:                                                   # the mark is not on skin: take the biggest piece in the circle
        l0 = 1 + int(np.argmax(ndi.sum(skin & circ, lab, range(1, k + 1))))
    mask = ndi.binary_dilation(lab == l0, iterations=2) & (arr[..., 3] > 0)
    out = np.zeros_like(arr, dtype=np.uint8); out[mask] = arr[mask]
    return Image.fromarray(out, "RGBA")

cols = a.cols; rows = (n + cols - 1) // cols
sheet = Image.new("RGB", (W * cols, H * rows), (60, 64, 76))
for k in range(n):
    frame = strip.crop((k * W, 0, (k + 1) * W, H))
    back = Image.new("RGBA", (W, H), (0, 0, 0, 0)); front = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    marks = {}
    for tk in ("main", "off"):
        m = an["tracks"][tk][k]
        if not m or m.get("hide"):
            continue
        marks[tk] = m
        draw_item(front if m.get("front") else back, tk, m)
    comp = Image.new("RGBA", (W, H), (60, 64, 76, 255))
    comp.alpha_composite(back); comp.alpha_composite(frame); comp.alpha_composite(front)
    for tk, m in marks.items():
        if m.get("front") and cfg[tk].get("overlay"):
            hl = hand_layer(frame, m)
            if hl:
                comp.alpha_composite(hl)
    sheet.paste(comp.convert("RGB"), ((k % cols) * W, (k // cols) * H))
sheet.save(a.out)
print("wrote", a.out)
