#!/usr/bin/env python3
"""Draft hand marks (hand-anchors/3) for the Rogue's Shadow Shiv strip (cloaked_shadow_shiv_5frame_strip.png), in the convention of the marks the user made by hand:
track "main" = the CUTLASS, track "off" = the DAGGER (drawn in front, the hand over its grip). The fists are found by skin colour. In frames 1 to 4 the forward fist is the
striking hand (the dagger, pointing along the arm), the other fist (cocked back at the hip or the ribs) gets the cutlass, drawn in front because the body and the cloak would hide
it; frame 5 is the idle's first frame, so its marks are the user's own marks of that frame, copied.

  python make_shiv_marks.py [--promote]   (--promote writes the real marks next to the strip, unless they exist)
"""
import json
import pathlib
import sys
import numpy as np
from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "source" / "tools"))
import make_rogue_marks as M

D = ROOT / "Animations" / "Rogue" / "shadow_shiv"
STRIP = "cloaked_shadow_shiv_5frame_strip"
idle_doc = json.load(open(ROOT / "Animations" / "Rogue" / "idle" / "cloaked_idle_strip.hand-anchors.json", encoding="utf-8"))
ref = idle_doc["characters"][0]
idle_tr = ref["animations"][0]["tracks"]
# per frame: (dagger angle, cutlass angle) for frames 1 to 4 (dagger at the right fist, cutlass at the left fist)
ANG = [(80, -115), (85, -55), (90, -60), (85, -55)]

im = np.array(Image.open(D / (STRIP + ".png")).convert("RGBA")).astype(int)
H = im.shape[0]
main, off = [], []
for k in range(4):
    hs, face = M.hands_in(im[:, 512 * k:512 * (k + 1)])
    left, right = hs[0], hs[-1]
    da, ca = ANG[k]
    print("frame", k + 1, "fists", [(round(h["cx"]), round(h["cy"])) for h in hs])
    main.append({"x": round(left["cx"] / 512, 3), "y": round(left["cy"] / H, 3), "a": ca, "front": True, "hide": False, "w": 1})
    off.append({"x": round(right["cx"] / 512, 3), "y": round(right["cy"] / H, 3), "a": da, "front": True, "hide": False, "w": 1})
main.append(dict(idle_tr["main"][0])); off.append(dict(idle_tr["off"][0]))

doc = {"format": "hand-anchors/3", "note": "Draft marks made by Animations/Rogue/shadow_shiv/source/make_shiv_marks.py in the convention of the user's own marks: main = cutlass, off = dagger (in front, hand over the grip). Frame 5 is copied from the user's idle marks. Refine in the hand tool.",
       "characters": [{"name": ref["name"], "fist": ref.get("fist", 0.09), "items": ref["items"],
                       "animations": [{"name": STRIP[:-len("_strip")], "frames": 5, "columns": 5, "fps": 10, "offItem": ref["animations"][0]["offItem"], "tracks": {"main": main, "off": off}}]}]}
text = json.dumps(doc, separators=(", ", ": "))
(D / "source" / (STRIP + ".hand-anchors.draft.json")).write_text(text, encoding="utf-8", newline="\n")
print("wrote the draft")
real = D / (STRIP + ".hand-anchors.json")
if "--promote" in sys.argv:
    if real.exists():
        print("not promoted: the marks exist already")
    else:
        real.write_text(text, encoding="utf-8", newline="\n"); print("promoted to", real.name)
