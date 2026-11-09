#!/usr/bin/env python3
"""Builds the Rogue's Static Stiletto strip (9 frames) from the Shadow Shiv strip: no new sheet was needed (the user: it is a basic skill, it may look like the Shadow Shiv, but slower,
and the lightning-charged stab must show). The lightning is code (the page): the dagger crackles harder and harder while she holds the plant pose, a lightning aura turns round her,
and the stab discharges into the target.

  frame 1 sprint   <- shiv frame 1     the dash is slower than the Shadow Shiv's: two frames
  frame 2 sprint   <- shiv frame 1
  frame 3 plant    <- shiv frame 2     she arrives and plants her front foot
  frame 4 plant    <- shiv frame 2     charge
  frame 5 plant    <- shiv frame 2     charge
  frame 6 plant    <- shiv frame 2     charge, the peak (the path lifts her a hair on frames 4 and 6: she trembles)
  frame 7 stab     <- shiv frame 3     the hit frame
  frame 8 plant    <- shiv frame 2     the withdrawal, sliding back
  frame 9 idle     <- shiv frame 5     the idle's first frame

THE ORDER (the user's change, 2026-11-04: charge first, then leap): the six plant frames are the charge AT HOME (the first version dashed to the target first and charged
there), frame 7 is the sprint pose as the leap (the path gives it an arc), frame 8 the stab (hit frame), frame 9 the plant pose again while she slides back, frame 10 the idle.
The nine-frame first version is in ../source/old_9frame/ (strip, marks and path file).

Writes cloaked_static_stiletto_10frame_strip.png, its .hand-anchors.json (the marks of each shiv frame, copied: the user's convention main = cutlass, off = dagger) and its
.placement.json (fps 10, hit frame 8, x = 0 for the charge, .55, 1, .6, 0). The marks follow the shiv's: refine them there or in the tool.

  python make_stiletto_strip.py
"""
import json
import pathlib
from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parents[4]
R = ROOT / "Animations" / "Rogue"
D = R / "static_stiletto"
SHIV = R / "shadow_shiv" / "cloaked_shadow_shiv_5frame_strip"
NAME = "cloaked_static_stiletto_10frame_strip"
ORDER = [1, 1, 1, 1, 1, 1, 0, 2, 1, 4]         # shiv frame indices (0-based): plant x6, sprint, stab, plant, idle

strip = Image.open(str(SHIV) + ".png").convert("RGBA")
out = Image.new("RGBA", (512 * len(ORDER), 512), (0, 0, 0, 0))
for i, k in enumerate(ORDER):
    out.alpha_composite(strip.crop((k * 512, 0, (k + 1) * 512, 512)), (i * 512, 0))
out.save(D / (NAME + ".png"))

doc = json.load(open(str(SHIV) + ".hand-anchors.json", encoding="utf-8"))
an = doc["characters"][0]["animations"][0]
tr = an["tracks"]
an["name"] = NAME[:-len("_strip")]
an["frames"] = an["columns"] = len(ORDER)
an["tracks"] = {t: [dict(tr[t][k]) for k in ORDER] for t in ("main", "off")}
doc["note"] = "Marks copied frame by frame from the Shadow Shiv's marks (see make_stiletto_strip.py)."
(D / (NAME + ".hand-anchors.json")).write_text(json.dumps(doc, ensure_ascii=False, separators=(", ", ": ")), encoding="utf-8", newline="\n")

pl = {"format": "frame-placement/1", "animation": "attack", "file": NAME + ".png", "frames": len(ORDER), "fps": 10, "hitFrame": 8, "moveFrom": 7, "smooth": True,
      "x": [0, 0, 0, 0, 0, 0, 0.55, 1, 0.6, 0], "y": [0, 0.008, 0, 0.018, 0, 0.025, 0.15, 0, 0, 0],
      "note": "Static Stiletto (the user's order, 2026-11-04): she charges at HOME in the crouch for frames 1 to 6 (a lightning halo forms over frames 1 to 3, the weapons electrify over 4 to 6, she trembles a hair), LEAPS to the target on frame 7 (the sprint pose; y is the arc), stabs on the hit frame 8, and withdraws sliding back in the plant pose (9; the effect fades during it) into the idle (10). 10 fps makes it 1.0 s."}
(D / (NAME + ".placement.json")).write_text(json.dumps(pl, ensure_ascii=False), encoding="utf-8", newline="\n")
print("wrote", D / (NAME + ".png"), out.size)
