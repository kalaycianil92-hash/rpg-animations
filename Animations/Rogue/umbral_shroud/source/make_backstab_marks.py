#!/usr/bin/env python3
"""Draft hand marks (hand-anchors/3) for the Rogue's REAL backstab strip (cloaked_umbral_shroud_6frame_strip.png), in the convention of the marks the user made by hand
for her other animations: track "main" = the CUTLASS (drawn behind the body), track "off" = the DAGGER (drawn in front, the hand over its grip); item settings copied
from the user's idle marks. The fists are found by skin colour (source/tools/make_rogue_marks.py hands_in).

The generator drew the strike with the FRONT arm (the one that was forward and low in frame 3), not the back arm as the prompt asked, so the dagger is given to
the hand that thrusts (the right-most fist in frames 3 to 5) and the cutlass to the other (swung back); in the stances (1 and 6) the cutlass is at the front fist and
the dagger at the back fist like everywhere else. Frame 2 (wrapped in the cloak) has no hands showing: both items are hidden ("hide only when the hand is hidden").
Drafts: refine them in hand-anchor-tool.html (they are written as the real marks only when none exist).

  python make_backstab_marks.py [--promote]
"""
import json
import pathlib
import sys
import numpy as np
from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "source" / "tools"))
import make_rogue_marks as M

B = ROOT / "Animations" / "Rogue" / "umbral_shroud"
STRIP = "cloaked_umbral_shroud_6frame_strip"
ref = json.load(open(ROOT / "Animations" / "Rogue" / "idle" / "cloaked_idle_strip.hand-anchors.json", encoding="utf-8"))["characters"][0]
# per frame: (dagger hand, cutlass hand, dagger angle, cutlass angle); hand = "L" (left-most fist), "R" (right-most) or None (hidden)
SPEC = [("L", "R", -85, 54),      # 1 gather: the stance's hands
        (None, None, 0, 0),       # 2 wrapped in the cloak: no hands showing
        ("R", "L", 100, -55),     # 3 emerge: the forward fist gets the dagger, pointing forward and a little down; the cutlass over the shoulder from the cocked fist
        ("R", "L", 90, -60),      # 4 STRIKE: the dagger along the thrust arm
        ("R", "L", 105, -50),     # 5 follow-through
        ("L", "R", -85, 54)]      # 6 the stance again

im = np.array(Image.open(B / (STRIP + ".png")).convert("RGBA")).astype(int)
H = im.shape[0]
n = im.shape[1] // 512
main, off = [], []
for k in range(n):
    hs, face = M.hands_in(im[:, 512 * k:512 * (k + 1)])
    pos = {"L": hs[0] if hs else None, "R": hs[-1] if len(hs) >= 2 else None}
    dh, ch, da, ca = SPEC[k]
    def pt(h):
        p = pos.get(h) if h else None
        return (p["cx"], p["cy"]) if p else None
    dp, cp = pt(dh), pt(ch)
    print("frame", k + 1, "fists", [(round(h["cx"]), round(h["cy"])) for h in hs], "dagger", dp and (round(dp[0]), round(dp[1])), "cutlass", cp and (round(cp[0]), round(cp[1])))
    # the cutlass is behind the body in the stances; in frames 3 to 5 it is swung up over the shoulder, where the body and the cloak would hide it, so it is drawn in front there
    main.append({"x": round((cp or (256, 300))[0] / 512, 3), "y": round((cp or (256, 300))[1] / H, 3), "a": ca, "front": k in (2, 3, 4), "hide": cp is None, "w": 1})
    off.append({"x": round((dp or (256, 300))[0] / 512, 3), "y": round((dp or (256, 300))[1] / H, 3), "a": da, "front": True, "hide": dp is None, "w": 1})

doc = json.loads(json.dumps({"format": "hand-anchors/3", "note": "Draft marks made by Animations/Rogue/umbral_shroud/source/make_backstab_marks.py in the convention of the user's own marks: main = cutlass (behind the body), off = dagger (in front, hand over the grip). Refine in the hand tool.",
                             "characters": [{"name": ref["name"], "fist": ref.get("fist", 0.09), "items": ref["items"],
                                             "animations": [{"name": STRIP[:-len("_strip")], "frames": n, "columns": n, "fps": 10, "offItem": ref["animations"][0]["offItem"], "tracks": {"main": main, "off": off}}]}]}))
text = json.dumps(doc, separators=(", ", ": "))
(B / "source" / (STRIP + ".hand-anchors.draft.json")).write_text(text, encoding="utf-8", newline="\n")
print("wrote the draft")
real = B / (STRIP + ".hand-anchors.json")
if "--promote" in sys.argv:
    if real.exists():
        print("not promoted: the marks exist already")
    else:
        real.write_text(text, encoding="utf-8", newline="\n"); print("promoted to", real.name)
