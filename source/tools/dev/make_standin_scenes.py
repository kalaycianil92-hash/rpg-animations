#!/usr/bin/env python3
"""Stand-in stage pictures, so the scene mechanism and the props layer can be seen working before the real pictures exist.

- Scenes moonshade, ashfall and warhorn (acts 3 to 5): the mistwood far and ground pictures, tinted (night blue, ash grey, smoky red-brown).
  Each folder gets a standin.txt, which makes the page label it as a stand-in. A scene folder that has no standin.txt is never touched.
- props.png for mistwood, moonshade, ashfall and warhorn: crude flat shapes (totems, shrines, hut frames, banners ...) on magenta, keyed and made
  seamless by make_bg_layer.py like the real ones will be. Existing props.png files are kept unless --force.
Usage:  python make_standin_scenes.py [--force]      (run from anywhere)
"""
import sys, random, pathlib, subprocess, tempfile
import numpy as np
from PIL import Image, ImageDraw

BG = pathlib.Path(__file__).resolve().parents[2] / "assets" / "bg"
TOOL = pathlib.Path(__file__).resolve().parents[1] / "make_bg_layer.py"
FORCE = "--force" in sys.argv
MAG = (255, 0, 255)

TINTS = {                       # name: (per-channel multiply, how much colour is kept, added)
    "moonshade": ((0.34, 0.5, 0.8), 1.0, (0, 3, 12)),
    "ashfall":   ((1.0, 0.96, 0.9), 0.15, (14, 10, 6)),
    "warhorn":   ((1.08, 0.8, 0.7), 0.4, (6, 0, 0)),
}


def tint(img, mul, keep, add):
    a = np.array(img).astype(float)
    rgb = a[..., :3]
    grey = rgb.mean(axis=2, keepdims=True)
    rgb = (grey + (rgb - grey) * keep) * np.array(mul) * 0.85 + np.array(add)
    a[..., :3] = rgb
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), img.mode)


def scenes():
    src = BG / "mistwood"
    for name, (mul, keep, add) in TINTS.items():
        d = BG / name
        if d.exists() and not (d / "standin.txt").exists():
            print("kept", name, "(real pictures)"); continue
        d.mkdir(exist_ok=True)
        tint(Image.open(src / "far.jpg").convert("RGB"), mul, keep, add).save(d / "far.jpg", quality=88)
        tint(Image.open(src / "ground.png").convert("RGBA"), mul, keep, add).save(d / "ground.png", optimize=True)
        (d / "standin.txt").write_text("far.jpg and ground.png are tinted copies of mistwood, to test the scene change. Replace them by the real pictures and delete this file.\n")
        print("scene", name)


# crude props: every one stands with its feet on (x, y); sizes are in px of a 1568 x 672 picture
def totem(d, x, y):
    d.rectangle([x - 7, y - 110, x + 7, y], fill=(86, 70, 46)); d.ellipse([x - 17, y - 140, x + 17, y - 106], fill=(190, 184, 166))
    d.ellipse([x - 9, y - 130, x - 3, y - 122], fill=(40, 34, 30)); d.ellipse([x + 3, y - 130, x + 9, y - 122], fill=(40, 34, 30))
def stakes(d, x, y):
    for i in range(3): d.polygon([(x + i * 26 - 10, y), (x + i * 26, y - 70 - i * 6), (x + i * 26 + 10, y)], fill=(90, 74, 48))
def sack(d, x, y): d.ellipse([x - 32, y - 40, x + 32, y], fill=(130, 114, 82))
def lantern(d, x, y):
    d.rectangle([x - 3, y - 120, x + 3, y], fill=(60, 50, 38)); d.ellipse([x - 12, y - 140, x + 12, y - 116], fill=(224, 176, 80))
def shrine(d, x, y):
    d.rectangle([x - 20, y - 100, x + 20, y], fill=(104, 104, 112)); d.ellipse([x - 16, y - 132, x + 16, y - 100], fill=(236, 214, 140))
def altar(d, x, y):
    d.rectangle([x - 26, y - 70, x + 26, y], fill=(44, 34, 54)); d.ellipse([x - 14, y - 98, x + 14, y - 70], fill=(138, 80, 206))
def boulder(d, x, y): d.ellipse([x - 44, y - 50, x + 44, y], fill=(66, 72, 80))
def hut(d, x, y):
    d.line([(x - 50, y), (x - 50, y - 70), (x, y - 120), (x + 50, y - 70), (x + 50, y)], fill=(44, 38, 34), width=8); d.line([(x - 50, y - 70), (x + 50, y - 70)], fill=(44, 38, 34), width=6)
def wheel(d, x, y):
    d.ellipse([x - 40, y - 80, x + 40, y], outline=(62, 50, 40), width=7); d.line([(x - 40, y - 40), (x + 40, y - 40)], fill=(62, 50, 40), width=5); d.line([(x, y - 80), (x, y)], fill=(62, 50, 40), width=5)
def ash(d, x, y): d.ellipse([x - 60, y - 26, x + 60, y], fill=(124, 116, 110))
def scarecrow(d, x, y):
    d.line([(x, y - 130), (x, y)], fill=(76, 58, 40), width=7); d.line([(x - 40, y - 100), (x + 40, y - 100)], fill=(76, 58, 40), width=7)
def banner(d, x, y):
    d.rectangle([x - 3, y - 190, x + 3, y], fill=(58, 48, 40)); d.rectangle([x + 3, y - 186, x + 56, y - 120], fill=(138, 42, 34))
def tent(d, x, y):
    d.polygon([(x - 80, y), (x, y - 100), (x + 80, y)], fill=(106, 74, 52)); d.polygon([(x - 18, y), (x, y - 44), (x + 18, y)], fill=(42, 30, 24))
def barricade(d, x, y):
    for i in range(5): d.polygon([(x + i * 24 - 9, y), (x + i * 24, y - 84), (x + i * 24 + 9, y)], fill=(74, 58, 40))
def fire(d, x, y):
    d.ellipse([x - 34, y - 14, x + 34, y + 6], fill=(70, 62, 56)); d.ellipse([x - 14, y - 38, x + 14, y - 8], fill=(240, 138, 42))

PROPS = {
    "mistwood": [totem, stakes, sack, lantern],
    "moonshade": [shrine, altar, boulder, boulder],
    "ashfall": [hut, wheel, ash, scarecrow],
    "warhorn": [banner, tent, barricade, fire],
}


def props(name, kinds, seed):
    out = BG / name / "props.png"
    if out.exists() and not FORCE:
        print("kept", name, "props"); return
    rnd = random.Random(seed)
    W, H = 1568, 672
    im = Image.new("RGB", (W, H), MAG)
    d = ImageDraw.Draw(im)
    n = 8
    for i in range(n):
        x = int((i + .5) * W / n + rnd.randint(-50, 50)); y = rnd.randint(450, 555)    # feet between 67% and 83% of the height
        rnd.choice(kinds)(d, x, y)
    with tempfile.TemporaryDirectory() as t:
        raw = pathlib.Path(t) / "props_raw.png"; im.save(raw)
        subprocess.run([sys.executable, str(TOOL), str(raw), "--key", "--out", str(out)], check=True)
    print("props", name)


scenes()
for i, (name, kinds) in enumerate(PROPS.items()):
    if (BG / name).exists(): props(name, kinds, 10 + i)
