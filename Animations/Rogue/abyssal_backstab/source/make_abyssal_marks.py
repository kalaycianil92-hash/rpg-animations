#!/usr/bin/env python3
"""NOTE 2026-11-04: the marks in the folder are now the USER's own (made in the hand tool, one character, one animation, 8 frames; inbox/rogue_cloaked_abyssal_backstab_8frame.json), they replaced
this script's draft: do NOT re-run it over them (the draft is kept as cloaked_abyssal_backstab_8frame_strip.hand-anchors.draft.json).

Draft hand marks (hand-anchors/3) for the Rogue's Abyssal Backstab strip (cloaked_abyssal_backstab_8frame_strip.png, 512 x 768 cells), in the convention of the user's own marks:
track "main" = the CUTLASS in the FRONT fist (the right one, the one further along the thrust), track "off" = the DAGGER in the REAR fist (the left one). BOTH weapons are visible in every frame
(items are never hidden), in front of the body in the air frames so the arms do not hide them. The fists are found by skin colour; where the two fists touch (the dive and the strike: they are
side by side) the blob is split in two with a 2-means cut.

  frames 1 and 2   the Umbral Shroud's gather and wrapped frames: its marks, copied (their y moved down into the tall cell)
  frame 3 emerge   both weapons up (cutlass 20 degrees, dagger -5)
  frame 4 coil     both weapons cocked back and up (-40 and -60)
  frame 5 dive     both along the forearms, down and forward (118 and 112)
  frame 6 STRIKE   both thrust down and forward (140 and 134)
  frame 7 land     the cutlass forward and low (100), the dagger back and low (-100)
  frame 8 rise     the idle convention (cutlass 54 behind the body, dagger -81 in front)

  python make_abyssal_marks.py [--promote]   (--promote writes the real marks next to the strip, unless they exist)
"""
import json
import pathlib
import sys
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

ROOT = pathlib.Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "source" / "tools"))
import make_rogue_marks as M

D = ROOT / "Animations" / "Rogue" / "abyssal_backstab"
STRIP = "cloaked_abyssal_backstab_8frame_strip"
CW, CH = 512, 768
umb = json.load(open(ROOT / "Animations" / "Rogue" / "umbral_shroud" / "cloaked_umbral_shroud_6frame_strip.hand-anchors.json", encoding="utf-8"))
idle_doc = json.load(open(ROOT / "Animations" / "Rogue" / "idle" / "cloaked_idle_strip.hand-anchors.json", encoding="utf-8"))
ref = idle_doc["characters"][0]
utr = umb["characters"][0]["animations"][0]["tracks"]
# frame: (cutlass angle, dagger angle, cutlass in front of the body, dagger in front of the body)
ANG = {3: (20, -5, True, True), 4: (-40, -60, True, True), 5: (118, 112, True, True), 6: (140, 134, True, True), 7: (100, -100, True, True), 8: (54, -81, False, True)}

im = np.array(Image.open(D / (STRIP + ".png")).convert("RGBA")).astype(int)

def fists(frame):
    s = M.skin(frame)
    lab, n = ndi.label(ndi.binary_closing(s, iterations=1))
    comps = []
    for i in range(1, n + 1):
        ys, xs = np.where(lab == i)
        if len(ys) >= 80:
            comps.append(dict(area=len(ys), cx=float(xs.mean()), cy=float(ys.mean()), xs=xs, ys=ys))
    comps.sort(key=lambda c: -c["area"])
    face = comps[0]
    rest = [c for c in comps[1:] if c["area"] >= 120 and (c["cx"] - face["cx"]) ** 2 + (c["cy"] - face["cy"]) ** 2 > 40 ** 2]
    if len(rest) == 1 and rest[0]["area"] > 600:                  # the two fists touch: split the blob in two
        c = rest[0]
        pts = np.stack([c["xs"], c["ys"]], 1).astype(float)
        a, b = pts[pts[:, 0].argmin()].copy(), pts[pts[:, 0].argmax()].copy()
        for _ in range(12):
            d = ((pts - a) ** 2).sum(1) < ((pts - b) ** 2).sum(1)
            a, b = pts[d].mean(0), pts[~d].mean(0)
        rest = [dict(area=int(d.sum()), cx=a[0], cy=a[1]), dict(area=int((~d).sum()), cx=b[0], cy=b[1])]
    rest = sorted(rest, key=lambda c: -c["area"])[:2]
    rest.sort(key=lambda c: c["cx"])
    return rest, face

main, off = [], []
for k in (0, 1):                                                  # the Umbral Shroud's frames: y moves down by 256 px into the tall cell
    for tr, out in ((utr["main"], main), (utr["off"], off)):
        m = dict(tr[k]); m["y"] = round((m["y"] * 512 + (CH - 512)) / CH, 3); out.append(m)
for k in range(2, 8):
    hs, face = fists(im[:, CW * k:CW * (k + 1)])
    print("frame", k + 1, "face", (round(face["cx"]), round(face["cy"])), "fists", [(round(h["cx"]), round(h["cy"]), h["area"]) for h in hs])
    rear, front = hs[0], hs[-1]
    ca, da, cf, df = ANG[k + 1]
    main.append({"x": round(front["cx"] / CW, 3), "y": round(front["cy"] / CH, 3), "a": ca, "front": cf, "hide": False, "w": 1})
    off.append({"x": round(rear["cx"] / CW, 3), "y": round(rear["cy"] / CH, 3), "a": da, "front": df, "hide": False, "w": 1})

doc = {"format": "hand-anchors/3", "note": "Draft marks made by Animations/Rogue/abyssal_backstab/source/make_abyssal_marks.py in the convention of the user's own marks: main = cutlass (the front fist), off = dagger (the rear fist), both weapons visible in every frame. Frames 1 and 2 are the Umbral Shroud's. The two fists touch in the dive and the strike (split in two). Refine in the hand tool.",
       "characters": [{"name": ref["name"], "fist": ref.get("fist", 0.09), "items": ref["items"],
                       "animations": [{"name": STRIP[:-len("_strip")], "frames": 8, "columns": 8, "fps": 12, "offItem": ref["animations"][0]["offItem"], "tracks": {"main": main, "off": off}}]}]}
text = json.dumps(doc, separators=(", ", ": "))
(D / "source" / (STRIP + ".hand-anchors.draft.json")).write_text(text, encoding="utf-8", newline="\n")
print("wrote the draft")
real = D / (STRIP + ".hand-anchors.json")
if "--promote" in sys.argv:
    if real.exists():
        print("not promoted: the marks exist already")
    else:
        real.write_text(text, encoding="utf-8", newline="\n"); print("promoted to", real.name)
