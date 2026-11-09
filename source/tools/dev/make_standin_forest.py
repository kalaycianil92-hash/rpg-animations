#!/usr/bin/env python3
"""Stand-in forest pictures (crude shapes, NOT seamless) in the layout the Gemini prompts ask for, for testing
make_bg_layer.py and the page's scroll before the real pictures exist.  Writes forest_far.png, forest_ground.png
and forest_mid.png into the folder given (1568 x 672, the horizon at 62% of the height, magenta where a layer is see-through).
Usage:  python make_standin_forest.py <folder> [seed]
"""
import sys, pathlib, random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

out = pathlib.Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
random.seed(int(sys.argv[2]) if len(sys.argv) > 2 else 1)
W, H = 1568, 672
HZ = int(H * .62)
MAG = (255, 0, 255)


def lerp(c1, c2, t):
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))


def noise(img, amt):
    a = np.array(img).astype(float)
    a[..., :3] += np.random.default_rng(random.randint(0, 99999)).normal(0, amt, a.shape[:2])[..., None]
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), img.mode)


# far: gradient, three rows of hazy trunks, canopy, light shafts
far = Image.new("RGB", (W, H))
d = ImageDraw.Draw(far)
for y in range(H):
    t = y / H
    d.line([(0, y), (W, y)], fill=lerp((14, 30, 26), (66, 96, 90), min(1, t / .62)) if t < .62 else lerp((66, 96, 90), (52, 78, 74), (t - .62) / .38))
for row, (n, tw, col, blur) in enumerate([(7, 20, (46, 74, 70), 5), (9, 14, (36, 60, 58), 3), (7, 24, (24, 44, 40), 1.2)]):
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    for _ in range(n):
        x = random.randint(0, W); w = tw * random.uniform(.7, 1.4)
        ld.polygon([(x - w / 2, -5), (x + w / 2, -5), (x + w * .7, HZ + 12), (x - w * .7, HZ + 12)], fill=col + (235,))
    far.paste(layer.filter(ImageFilter.GaussianBlur(blur)), (0, 0), layer.filter(ImageFilter.GaussianBlur(blur)))
for _ in range(3):
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0)); x = random.randint(0, W)
    ImageDraw.Draw(layer).polygon([(x, 0), (x + 70, 0), (x + 240, HZ), (x + 150, HZ)], fill=(255, 214, 140, 34))
    far.paste(layer.filter(ImageFilter.GaussianBlur(14)), (0, 0), layer.filter(ImageFilter.GaussianBlur(14)))
cn = Image.new("RGBA", (W, H), (0, 0, 0, 0)); cd = ImageDraw.Draw(cn)
for _ in range(90):
    x = random.randint(-20, W + 20); y = random.randint(-30, int(H * .08)); r = random.randint(30, 70)
    cd.ellipse([x - r, y - r * .6, x + r, y + r * .6], fill=(10, 24, 20, 255))
far.paste(cn.filter(ImageFilter.GaussianBlur(3)), (0, 0), cn.filter(ImageFilter.GaussianBlur(3)))
noise(far, 3).save(out / "forest_far.png")

# ground: magenta above the horizon, a path with stones, leaves and grass tufts along its far edge
gr = Image.new("RGB", (W, H), MAG); gd = ImageDraw.Draw(gr)
for y in range(HZ, H):
    gd.line([(0, y), (W, y)], fill=lerp((82, 74, 52), (46, 44, 34), (y - HZ) / (H - HZ)))
for _ in range(34):                                                     # moss
    x = random.randint(0, W); y = random.randint(HZ + 10, H - 20); r = random.randint(20, 60)
    gd.ellipse([x - r, y - r * .25, x + r, y + r * .25], fill=(56, 76, 44))
for _ in range(26):                                                     # stones
    x = random.randint(0, W); y = random.randint(HZ + 25, H - 15); r = random.randint(8, 22)
    gd.ellipse([x - r, y - r * .6, x + r, y + r * .6], fill=lerp((110, 108, 98), (70, 70, 64), random.random()))
for _ in range(70):                                                     # leaves
    x = random.randint(0, W); y = random.randint(HZ + 10, H - 6)
    gd.ellipse([x - 6, y - 2, x + 6, y + 2], fill=random.choice([(122, 84, 40), (96, 98, 40), (140, 100, 50)]))
for x in range(0, W, 9):                                                # grass along the far edge, over the magenta
    h = random.randint(6, 34)
    gd.polygon([(x, HZ + 6), (x + 5, HZ - h), (x + 10, HZ + 6)], fill=lerp((52, 82, 44), (30, 56, 34), random.random()))
noise(gr, 3).save(out / "forest_ground.png")

# mid: magenta, big trunks that leave the top edge, roots at 68% of the height, bushes at their feet
mid = Image.new("RGB", (W, H), MAG); md = ImageDraw.Draw(mid)
base = int(H * .68)
for i in range(6):
    x = int((i + random.uniform(.2, .8)) * W / 6); w = random.randint(70, 150)
    col = lerp((52, 40, 30), (40, 52, 36), random.random())
    md.polygon([(x - w * .42, -5), (x + w * .42, -5), (x + w * .5, base - 40), (x + w * .95, base + 8), (x - w * .95, base + 8), (x - w * .5, base - 40)], fill=col)
    for s in range(8):                                                  # bark streaks
        sx = x + random.uniform(-.4, .4) * w
        md.line([(sx, 0), (sx + random.uniform(-4, 4), base)], fill=lerp(col, (20, 18, 14), random.random() * .7), width=random.randint(2, 6))
    md.polygon([(x - w * .42, 0), (x - w * .2, 0), (x - w * .25, base - 20), (x - w * .5, base - 20)], fill=(58, 86, 46))   # moss on the left
    for _ in range(5):
        bx = x + random.uniform(-1.1, 1.1) * w; r = random.randint(22, 46)
        md.ellipse([bx - r, base + 6 - r * .9, bx + r, base + 6 + r * .6], fill=lerp((34, 62, 36), (50, 84, 44), random.random()))
for _ in range(10):                                                     # hanging vines
    x = random.randint(0, W)
    md.line([(x, 0), (x + random.randint(-10, 10), random.randint(60, 190))], fill=(40, 70, 40), width=4)
mid.save(out / "forest_mid.png")
print("wrote forest_far/ground/mid.png to", out)
