#!/usr/bin/env python3
"""The FINAL Abyssal Backstab strip (2026-11-04, chosen by the user: "this alternate version is the final"): the frame order is 1-2-3-4-3-6-7-8, that is frame 5 (the dive pose)
of the first version is replaced by frame 3 (the arrival pose, weapons raised), so she stays cocked in the air through the dive and the strike frame (6) lands as a surprise.

Reads the FIRST version (strip, marks, path) from old_original_8frame/ (made by make_abyssal_strip.py; its marks are the user's own, made in the hand tool) and writes the final files
into the animation folder (one level up):
  cloaked_abyssal_backstab_8frame_strip.png                (frame 5 = a copy of frame 3)
  cloaked_abyssal_backstab_8frame_strip.hand-anchors.json  (both mark tracks reordered the same way, frame 5's marks = frame 3's)
  cloaked_abyssal_backstab_8frame_strip.placement.json     (fps 12, hit frame 6, no movement: the page moves her)
WARNING: if you refine the final marks in the hand tool, do not re-run this over them.
Run from anywhere:  python make_final_strip.py     (needs Pillow)
"""
import copy
import json
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
OUT = HERE.parent
SRC = HERE / "old_original_8frame"
STEM = "cloaked_abyssal_backstab_8frame_strip"
ORDER = [1, 2, 3, 4, 3, 6, 7, 8]          # which frame of the first version is shown at each position

strip = Image.open(SRC / (STEM + ".png")).convert("RGBA")
n = 8
cw = strip.width // n
assert strip.width == cw * n, "the first version's strip is not eight equal frames"
out = Image.new("RGBA", strip.size, (0, 0, 0, 0))
for pos, f in enumerate(ORDER):
    out.alpha_composite(strip.crop(((f - 1) * cw, 0, f * cw, strip.height)), (pos * cw, 0))
out.save(OUT / (STEM + ".png"))

marks = json.loads((SRC / (STEM + ".hand-anchors.json")).read_text(encoding="utf-8"))
an = marks["characters"][0]["animations"][0]
for tk in ("main", "off"):
    an["tracks"][tk] = [copy.deepcopy(an["tracks"][tk][f - 1]) for f in ORDER]
(OUT / (STEM + ".hand-anchors.json")).write_text(json.dumps(marks, indent=1), encoding="utf-8")

pl = json.loads((SRC / (STEM + ".placement.json")).read_text(encoding="utf-8"))
pl["note"] = "Abyssal Backstab (final): frames 1-2-3-4-3-6-7-8 of the first version (frame 5 is frame 3 again). " + pl["note"]
(OUT / (STEM + ".placement.json")).write_text(json.dumps(pl), encoding="utf-8")
print("made", STEM, "order", ORDER)
