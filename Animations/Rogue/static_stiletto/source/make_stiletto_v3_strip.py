#!/usr/bin/env python3
"""Builds the Rogue's Static Stiletto strip, VERSION 3 "Spark, Streak, Stab" (2026-11-06; the first version, the Shadow Shiv's frames re-ordered, is cloaked_static_stiletto_10frame_strip.png).

The beats and the pictures they use (17 frames at 12 fps = 1.42 s, hit frame 13):
  frames  1- 2  lay      sheet panel 1   the dagger lies along the cutlass (both fists together at her chest)
  frames  3- 5  scrape   sheet panel 2   the far fist slides forward along the cutlass: half way
  frames  6- 8  tip      sheet panel 3   ... at the tip: the far arm straight (the page: sparks pour off the contact point, arcs between the blades)
  frames  9-10  garde    sheet panel 4   en garde: the dagger arm cocked back, the lightning cage forms
  frames 11-12  streak   sheet panel 5   the flat flight to the target (the path moves her: x 0.4, 0.8, a lift)
  frames 13-14  stab     the SHADOW SHIV's stab frame (shared)   the hit, held two frames (a hit-stop)
  frames 15-16  flick    sheet panel 6   the far arm whips down and back, the lightning is flicked off the blade
  frame  17     idle     the idle's first frame (shared)
The repeats are in REPEAT: change them and rerun to retime. The page (ssFx, the "v3" branch, used when the pack has 14 frames or more) derives its timing from the hit frame:
spark from frame 3, the garde at hitF-4, the streak at hitF-2, the flick at hitF+2, so keep those distances (garde 2, streak 2, stab 2, flick 2) when you retime the first part.

  python make_stiletto_v3_strip.py --placeholder           # a stand-in made of the Rogue's existing frames and SYNTHETIC marks, to try the page's code before the art exists
  python make_stiletto_v3_strip.py --cut <cut.png>         # the real strip from slice_keypose_sheet.py's cut of the six panels (read the plan in docs/DEV_NOTES.md)

The hand marks written here are DRAFTS (the near fist holds the cutlass = main, the far fist the dagger = off): the user marks the real ones in the hand tool; an existing marks file is never overwritten
(--marks to force). The placement file carries the fps, the hit frame and the path (x = share of the way to the strike point, y = a lift in character widths).
"""
import argparse
import copy
import json
import pathlib
import sys

from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parents[4]
R = ROOT / "Animations" / "Rogue"
D = R / "static_stiletto"
NAME = "cloaked_static_stiletto_17frame_strip"
FPS = 12
BEATS = ["lay", "scrape", "tip", "garde", "streak", "stab", "flick", "idle"]
REPEAT = {"lay": 2, "scrape": 3, "tip": 3, "garde": 2, "streak": 2, "stab": 2, "flick": 2, "idle": 1}
PATH_X = {"streak": [0.4, 0.8], "stab": [1, 1], "flick": [1, 0.6]}
PATH_Y = {"streak": [0.16, 0.12], "garde": [0.01, 0]}

# DRAFT marks per beat and repeat: (x, y, angle, front) as fractions of the cell; the angle is 0 = up, clockwise (negative = back). near fist = cutlass (main), far fist = dagger (off).
# The fist positions are MEASURED on the real cut (2026-11-06: skin-coloured blobs of the six frames, the face left out); the blade angles are guesses along each forearm. The user re-marks them in the hand tool.
MAIN = {"lay": (0.668, 0.354, 85, True), "scrape": (0.668, 0.354, 85, True), "tip": (0.646, 0.354, 85, True), "garde": (0.832, 0.434, 80, True), "streak": (0.336, 0.734, -110, True), "flick": (0.754, 0.449, 80, True)}
OFF = {"lay": [(0.713, 0.357, 85, True)], "scrape": [(0.791, 0.348, 85, True)], "tip": [(0.898, 0.338, 85, True)],
       "garde": [(0.463, 0.330, 80, True)], "streak": [(0.926, 0.627, 90, True)], "flick": [(0.223, 0.576, -125, True)]}
# (the placeholder strip made before the art existed used the old guesses: its marks no longer match; delete it with --placeholder files if it is ever remade)

ap = argparse.ArgumentParser()
ap.add_argument("--placeholder", action="store_true")
ap.add_argument("--cut")
ap.add_argument("--marks", action="store_true")
a = ap.parse_args()
if not a.placeholder and not a.cut:
    sys.exit("give --placeholder or --cut <the cut of the six panels>")


def fr(img, k):
    return img.crop((k * 512, 0, (k + 1) * 512, 512))


shiv = Image.open(R / "shadow_shiv" / "cloaked_shadow_shiv_5frame_strip.png").convert("RGBA")
idle = Image.open(R / "idle" / "cloaked_idle_strip.png").convert("RGBA")
if a.placeholder:
    src = {"lay": fr(shiv, 1), "scrape": fr(shiv, 1), "tip": fr(shiv, 1), "garde": fr(shiv, 1), "streak": fr(shiv, 0), "flick": fr(shiv, 1)}
else:
    cut = Image.open(a.cut).convert("RGBA")
    if cut.width != 512 * 6:
        sys.exit("the cut must be six 512 px frames (one per panel), it is %d px wide" % cut.width)
    src = {b: fr(cut, k) for k, b in enumerate(["lay", "scrape", "tip", "garde", "streak", "flick"])}
src["stab"] = fr(shiv, 2)
src["idle"] = fr(idle, 0)

order, x, y = [], [], []
for b in BEATS:
    for i in range(REPEAT[b]):
        order.append((b, i))
        x.append(PATH_X.get(b, [0] * REPEAT[b])[i])
        y.append(PATH_Y.get(b, [0] * REPEAT[b])[i])
n = len(order)
hit = 1 + sum(REPEAT[b] for b in BEATS[:BEATS.index("stab")])
out = Image.new("RGBA", (512 * n, 512), (0, 0, 0, 0))
for i, (b, _) in enumerate(order):
    out.alpha_composite(src[b], (i * 512, 0))
out.save(D / (NAME + ".png"))
print("wrote", NAME + ".png", out.size, "frames", n, "hit frame", hit)

pl = {"format": "frame-placement/1", "animation": "attack", "file": NAME + ".png", "frames": n, "fps": FPS, "hitFrame": hit, "moveFrom": 1 + sum(REPEAT[b] for b in BEATS[:BEATS.index("streak")]), "smooth": True, "x": x, "y": y,
      "note": "Static Stiletto v3, Spark Streak Stab (2026-11-06): frames 1-2 lay the dagger along the cutlass, 3-8 scrape it to the tip (sparks), 9-10 en garde (the lightning cage), 11-12 the flat streak to the target (x 0.4, 0.8 with a lift), 13-14 the stab (the Shadow Shiv's frame; the hit, held two frames), 15-16 the flick, 17 the idle. 12 fps makes it 1.42 s."}
(D / (NAME + ".placement.json")).write_text(json.dumps(pl, ensure_ascii=False), encoding="utf-8", newline="\n")

mp = D / (NAME + ".hand-anchors.json")
if mp.exists() and not a.marks:
    print("marks exist, not overwritten (use --marks to rewrite the drafts)")
else:
    doc = json.load(open(D / "cloaked_static_stiletto_10frame_strip.hand-anchors.json", encoding="utf-8"))
    an = doc["characters"][0]["animations"][0]
    shiv_marks = json.load(open(R / "shadow_shiv" / "cloaked_shadow_shiv_5frame_strip.hand-anchors.json", encoding="utf-8"))["characters"][0]["animations"][0]["tracks"]
    idle_marks = json.load(open(R / "idle" / "cloaked_idle_strip.hand-anchors.json", encoding="utf-8"))["characters"][0]["animations"][0]["tracks"]

    def mk(t, front=True):
        return {"x": t[0], "y": t[1], "a": t[2], "front": t[3], "hide": False, "w": 1}
    main, off = [], []
    for b, i in order:
        if b == "stab":
            main.append(copy.deepcopy(shiv_marks["main"][2])); off.append(copy.deepcopy(shiv_marks["off"][2]))
        elif b == "idle":
            main.append(copy.deepcopy(idle_marks["main"][0])); off.append(copy.deepcopy(idle_marks["off"][0]))
        else:
            main.append(mk(MAIN[b])); off.append(mk(OFF[b][min(i, len(OFF[b]) - 1)]))
    an["name"] = NAME[:-len("_strip")]
    an["frames"] = an["columns"] = n
    an["fps"] = FPS
    an["tracks"] = {"main": main, "off": off}
    doc["note"] = "DRAFT marks for the Static Stiletto v3 made by make_stiletto_v3_strip.py (synthetic fist positions for the new poses): mark them in the hand tool. main = the cutlass in the near fist, off = the dagger in the far fist."
    mp.write_text(json.dumps(doc, ensure_ascii=False, separators=(", ", ": ")), encoding="utf-8", newline="\n")
    print("wrote the draft marks")
