#!/usr/bin/env python3
"""Blend test (2026-11-07): the warrior and the fire slime on the Glimmerwood stage, as the test page draws them
(desktop size: stage 760 x 485, units 184 px, soles 41 px above the bottom), in four treatments, stacked:
  A  as it is now
  B  colour grade only: less saturation, the forest's tint, the pure blacks of the outlines pulled toward the forest's shadow colour
  C  B + a soft contact shadow on the ground + soft outline edges (a sub-pixel blur of the alpha only)
  D  C + a real blur of the whole sprite (to show what "reducing the sharpness" costs)
The warrior's sword is a separate layer in the page and is not drawn here.
Run from the project folder:  python source/tools/dev/blend_test.py   ->  docs/blend_test_1.png
"""
import numpy as np
from PIL import Image, ImageFilter, ImageDraw

ROOT = "."
S = 1.5                                    # render scale
W, H = 760, 485
SH, EXTRA, UNIT = 340, 145, 184
UG = 0.8
GROUND_Y = EXTRA + .62 * SH

def load(p): return Image.open(p).convert("RGBA")

def stage():
    far = load(ROOT + "/source/assets/bg/glimmerwood/far.jpg")
    gnd = load(ROOT + "/source/assets/bg/glimmerwood/ground.png")
    props = load(ROOT + "/source/assets/bg/glimmerwood/props.png")
    im = Image.new("RGBA", (int(W * S), int(H * S)), (0, 0, 0, 255))
    fh = (SH + EXTRA / .62)
    f = far.resize((int(far.width * fh / far.height * S), int(fh * S)), Image.LANCZOS)
    im.alpha_composite(f.crop((0, 0, im.width, im.height)).convert("RGBA"))
    gh = SH
    for pic in (gnd, props):
        g = pic.resize((int(pic.width * gh / pic.height * S), int(gh * S)), Image.LANCZOS)
        im.alpha_composite(g.crop((0, 0, min(g.width, im.width), g.height)), (0, int((H - gh) * S)))
    return im

def frame(path, idx):
    st = load(path)
    return st.crop((idx * 512, 0, idx * 512 + 512, 512))

def grade(im, sat, tint=(0.93, 0.97, 0.90), bright=0.95, lift=0.35):
    a = np.array(im).astype(float)
    rgb, al = a[..., :3], a[..., 3]
    lum = rgb @ np.array([.299, .587, .114])
    rgb = lum[..., None] + (rgb - lum[..., None]) * sat
    rgb = rgb * np.array(tint) * bright
    lum2 = rgb @ np.array([.299, .587, .114])
    w = np.clip((90 - lum2) / 90, 0, 1)[..., None] * lift          # the darker the pixel, the more it takes the forest's shadow colour
    rgb = rgb * (1 - w) + np.array([22, 40, 28]) * w
    a[..., :3] = np.clip(rgb, 0, 255)
    return Image.fromarray(a.astype(np.uint8))

def soft_edge(im, r):
    a = im.split()[3].filter(ImageFilter.GaussianBlur(r))
    out = im.copy(); out.putalpha(a); return out

def place(canvas, spr, left, flip, shadow_w, shadow, blur=0.0):
    size = int(UNIT * UG * 1.0 * S) if False else int(UNIT * S)
    spr = spr.resize((size, size), Image.LANCZOS)
    if flip: spr = spr.transpose(Image.FLIP_LEFT_RIGHT)
    if blur: spr = spr.filter(ImageFilter.GaussianBlur(blur * S))
    bottom_unit = H - SH * .12
    top = bottom_unit + UNIT * .082 - UNIT                               # the sprite is shifted down by the blank 8.2%
    x = left if not flip else W - UNIT - left
    cx = (x + UNIT / 2) * S
    soles = (top + 470 / 512 * UNIT) * S
    if shadow:
        sh = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(sh)
        rw, rh = shadow_w * S / 2, 9 * S
        d.ellipse([cx - rw, soles - rh * .6, cx + rw, soles + rh * 1.4], fill=(8, 14, 8, 120))
        sh = sh.filter(ImageFilter.GaussianBlur(5 * S))
        canvas.alpha_composite(sh)
    canvas.alpha_composite(spr, (int(cx - size / 2), int(top * S)))

def variant(kind):
    bg = stage()
    war = frame(ROOT + "/Animations/Warrior/idle/armored_idle_strip.png", 0)
    sli = frame(ROOT + "/Animations/Slime/idle/fire_idle_strip.png", 0)
    if kind in "BCD":
        war = grade(war, .82); sli = grade(sli, .66, bright=.93)
    if kind in "CD":
        war = soft_edge(war, .7); sli = soft_edge(sli, .7)
    blur = 0.9 if kind == "D" else 0.0
    shadow = kind in "CD"
    place(bg, war, 0.03 * W, False, 120, shadow, blur)
    place(bg, sli, 0.03 * W, True, 190, shadow, blur)
    return bg.crop((0, int(190 * S), bg.width, bg.height)).convert("RGB")

def main():
    rows = [variant(k) for k in "ABCD"]
    out = Image.new("RGB", (rows[0].width, sum(r.height for r in rows) + 6 * 3), (255, 255, 255))
    y = 0
    d = ImageDraw.Draw(out)
    for k, r in zip("ABCD", rows):
        out.paste(r, (0, y))
        d.rectangle([6, y + 6, 26, y + 26], fill=(0, 0, 0)); d.text((12, y + 10), k, fill=(255, 255, 255))
        y += r.height + 6
    out.save(ROOT + "/docs/blend_test_1.png")
    print("saved", out.size)

if __name__ == "__main__":
    main()
