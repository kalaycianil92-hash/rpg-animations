#!/usr/bin/env python3
"""Makes the FINAL Permafrost Execution strip (19 frames) from the 14-frame one (2026-11-05, the user: "animation is good, update the hand marks with this file (inbox/rogue_cloaked_permafrost_execution_14frame.json),
and double the duration of the first 5 frames so it looks more like focus / charge").

Reads the 14-frame files from old_14frame/ (the strip made by make_permafrost_strip.py, its path file, and the USER's own hand marks, made in the hand tool) and writes into the animation folder:
  cloaked_permafrost_execution_19frame_strip.png                (frames repeated: MAP)
  cloaked_permafrost_execution_19frame_strip.hand-anchors.json  (the user's marks of each old frame, repeated the same way; the animation is renamed; fps 12)
  cloaked_permafrost_execution_19frame_strip.placement.json     (fps 12, hit frame 14, x and y repeated the same way)

MAP (1-based old frames): each of the first five old frames lasts twice as long (settle x2 -> x4, the focus frames 3-5 x2 each), the rest is unchanged: 1 1 2 2 3 3 4 4 5 5 | 6 | 7 (dash) 8 (arrive)
9 (slash, the hit: now frame 14) 10 11 12 (the finishing pose) 13 (retreat) 14 (the idle). The page's effects follow the hit frame, so nothing else changes; the frost gathers over frames 1-11 now.
The pack-and-path attack has one frame time for all frames, so the duration is made by repeating frames (the hand tool then shows the repeats as separate frames with identical marks: edit both).

WARNING: if you refine the final marks in the hand tool, do not re-run this over them (it rewrites them from old_14frame/).
  python make_permafrost_19frame.py
"""
import copy
import json
import pathlib
from PIL import Image

HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE.parent
OLD = HERE / "old_14frame"
OLD_STEM = "cloaked_permafrost_execution_14frame_strip"
STEM = "cloaked_permafrost_execution_19frame_strip"
MAP = [1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]
FPS = 12

strip = Image.open(OLD / (OLD_STEM + ".png")).convert("RGBA")
assert strip.width == 512 * 14, "the 14-frame strip is not 14 frames of 512 px"
out = Image.new("RGBA", (512 * len(MAP), strip.height), (0, 0, 0, 0))
for i, k in enumerate(MAP):
    out.alpha_composite(strip.crop(((k - 1) * 512, 0, k * 512, strip.height)), (i * 512, 0))
out.save(OUT / (STEM + ".png"))

marks = json.loads((OLD / (OLD_STEM + ".hand-anchors.json")).read_text(encoding="utf-8"))
an = marks["characters"][0]["animations"][0]
for tk in ("main", "off"):
    an["tracks"][tk] = [copy.deepcopy(an["tracks"][tk][k - 1]) for k in MAP]
an["name"] = STEM[:-len("_strip")]
an["frames"] = an["columns"] = len(MAP)
an["fps"] = FPS
(OUT / (STEM + ".hand-anchors.json")).write_text(json.dumps(marks, indent=1), encoding="utf-8", newline="\n")

pl = json.loads((OLD / (OLD_STEM + ".placement.json")).read_text(encoding="utf-8"))
old_hit = pl["hitFrame"]
pl["file"] = STEM + ".png"
pl["frames"] = len(MAP)
pl["fps"] = FPS
pl["hitFrame"] = MAP.index(old_hit) + 1
pl["moveFrom"] = MAP.index(pl["moveFrom"]) + 1
pl["x"] = [pl["x"][k - 1] for k in MAP]
pl["y"] = [pl["y"][k - 1] for k in MAP]
pl["note"] = ("Permafrost Execution (final, 19 frames, the first five of the 14-frame version lasting twice as long): frames 1-11 settle and focus at home (hands crossed on her chest, eyes closed; the frost gathers), "
              "12 the dash (half way: x 0.5, a small arc), 13 the arrival (x 1 = 0.8 character widths in front of the target), 14 the SLASH (the hit), 15-17 the finishing pose (the X freezes), "
              "18 the retreat (x 0.5), 19 home in the idle stance. x is a share of the way to the strike point, y an arc in character widths. 12 fps makes it 1.58 s.")
(OUT / (STEM + ".placement.json")).write_text(json.dumps(pl, ensure_ascii=False), encoding="utf-8", newline="\n")
print("wrote", STEM, len(MAP), "frames; hit frame", pl["hitFrame"], "move from", pl["moveFrom"])
