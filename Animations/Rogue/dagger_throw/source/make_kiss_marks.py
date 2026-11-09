#!/usr/bin/env python3
"""Draft hand marks (hand-anchors/3) for the Rogue's Winter's Kiss strip (cloaked_winters_kiss_16frame_strip.png; the 12-frame version is in old_12frame/), in the convention of the marks the user made by hand:
track "main" = the CUTLASS (the FRONT fist, in front of her thigh, drawn behind the body like in her idle), track "off" = the DAGGER (the THROWING hand, drawn in front, the hand over its grip).
The hands are found by skin colour: the THROWING hand is the higher one (the fist raised beside her head in the raise and the wind-up, the open hand reaching out in the throw, the
follow-through and the catch), the other one is the front fist.

  frames 1-3 raise      dagger in the raised fist, pointing up and a little forward (a 35)
  frames 4-5 wind-up    dagger in the cocked fist, pointing forward over her head (a 60)
  frames 6-11           the hand is OPEN, the dagger is gone: hide = true (the page draws it flying, there and back, and in the open hand on the catch frames). The marks keep
                        the OPEN HAND's position (frame 6 = where the dagger leaves, frame 10 = where it lands), which the page reads even though the item is hidden
  frame 12 idle         the idle's first frame: the user's own idle marks, copied

  python make_kiss_marks.py [--promote]   (--promote writes the real marks next to the strip, unless they exist)
"""
import json
import pathlib
import sys
import numpy as np
from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "source" / "tools"))
import make_rogue_marks as M

D = ROOT / "Animations" / "Rogue" / "dagger_throw"
STRIP = "cloaked_winters_kiss_16frame_strip"
idle_doc = json.load(open(ROOT / "Animations" / "Rogue" / "idle" / "cloaked_idle_strip.hand-anchors.json", encoding="utf-8"))
ref = idle_doc["characters"][0]
idle_tr = ref["animations"][0]["tracks"]
# per frame (1 to 11): (dagger angle, dagger hidden, cutlass angle)
FR = [(35, False, 54)] * 5 + [(60, False, 54)] * 4 + [(90, True, 54)] * 4 + [(50, True, 54)] * 2        # frames 1-5 raise, 6-9 wind-up, 10-13 throw and follow-through, 14-15 catch (16 = the idle)

im = np.array(Image.open(D / (STRIP + ".png")).convert("RGBA")).astype(int)
H = im.shape[0]
main, off = [], []
for k, (da, dh, ca) in enumerate(FR):
    hs, face = M.hands_in(im[:, 512 * k:512 * (k + 1)])
    hs = sorted(hs, key=lambda h: h["cy"])
    top, low = hs[0], hs[-1]
    print("frame", k + 1, "hands", [(round(h["cx"]), round(h["cy"]), h["area"]) for h in hs])
    main.append({"x": round(low["cx"] / 512, 3), "y": round(low["cy"] / H, 3), "a": ca, "front": False, "hide": False, "w": 1})
    off.append({"x": round(top["cx"] / 512, 3), "y": round(top["cy"] / H, 3), "a": da, "front": True, "hide": dh, "w": 1})
main.append(dict(idle_tr["main"][0])); off.append(dict(idle_tr["off"][0]))

doc = {"format": "hand-anchors/3", "note": "Draft marks made by Animations/Rogue/dagger_throw/source/make_kiss_marks.py in the convention of the user's own marks: main = cutlass (front fist), off = dagger (the throwing hand, in front, hand over the grip). Frames 6 to 11 hide the dagger (it is thrown) but keep the open hand's position: the page reads it as the release point (frame 6) and the catch point (frame 10). Frame 12 is copied from the user's idle marks. Refine in the hand tool.",
       "characters": [{"name": ref["name"], "fist": ref.get("fist", 0.09), "items": ref["items"],
                       "animations": [{"name": STRIP[:-len("_strip")], "frames": len(FR) + 1, "columns": len(FR) + 1, "fps": 10, "offItem": ref["animations"][0]["offItem"], "tracks": {"main": main, "off": off}}]}]}
text = json.dumps(doc, separators=(", ", ": "))
(D / "source" / (STRIP + ".hand-anchors.draft.json")).write_text(text, encoding="utf-8", newline="\n")
print("wrote the draft")
real = D / (STRIP + ".hand-anchors.json")
if "--promote" in sys.argv:
    if real.exists():
        print("not promoted: the marks exist already")
    else:
        real.write_text(text, encoding="utf-8", newline="\n"); print("promoted to", real.name)
