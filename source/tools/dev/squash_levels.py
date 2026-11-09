#!/usr/bin/env python3
"""Shows the squash frame (3) and the stretch frame (5) of each candidate idle at 100%, 50% and 0% of their squash and stretch
(what the page's "Squash and stretch" slider does), next to frame 1, on the forest green. Writes docs/squash_levels.png.
  python source/tools/dev/squash_levels.py
"""
import json
from PIL import Image, ImageDraw

D = "Animations/Slime/idle/candidates/"
rows = []
for tag, label in (("gemini", "Gemini"), ("gpt", "ChatGPT")):
    strip = Image.open(D + tag + "_fire_idle_strip.png").convert("RGBA")
    sq = json.load(open(D + tag + "_fire_idle_strip.squash.json"))
    def frame(i, a):
        f = strip.crop((i * 512, 0, i * 512 + 512, 512))
        r, q = sq["h"][i], sq["w"][i]
        sy, sx = (1 + a * (r - 1)) / r, (1 + a * (q - 1)) / q
        w, h = int(512 * sx), int(512 * sy)
        g = f.resize((w, h), Image.LANCZOS)
        out = Image.new("RGBA", (512, 512), (0, 0, 0, 0))
        out.alpha_composite(g, (256 - int(256 * sx), 470 - int(470 * sy)))
        return out
    cols = [("frame 1", frame(0, 1))]
    for i, name in ((2, "squash"), (4, "stretch")):
        for a in (1.0, 0.5, 0.0):
            cols.append(("%s %d%%" % (name, round(a * 100)), frame(i, a)))
    rows.append((label, cols))

cw = 330
W = cw * 7; H = 330 * 2 + 20
img = Image.new("RGB", (W, H), (38, 84, 52))
d = ImageDraw.Draw(img)
for ri, (label, cols) in enumerate(rows):
    for ci, (name, f) in enumerate(cols):
        t = Image.new("RGBA", (512, 512), (38, 84, 52, 255)); t.alpha_composite(f)
        t = t.resize((cw, cw), Image.LANCZOS).convert("RGB")
        img.paste(t, (ci * cw, ri * (330 + 20)))
        d.text((ci * cw + 8, ri * 350 + 6), "%s: %s" % (label, name), fill=(255, 255, 255))
        d.line([(ci * cw, ri * 350 + int(470 / 512 * cw)), (ci * cw + cw, ri * 350 + int(470 / 512 * cw))], fill=(255, 255, 255), width=1)
img.save("docs/squash_levels.png")
print("saved", img.size)
