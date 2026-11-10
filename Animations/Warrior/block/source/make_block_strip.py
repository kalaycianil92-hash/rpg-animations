#!/usr/bin/env python3
"""Builds the Warrior's BLOCK strip and its first-draft files (2026-11-10).

  python Animations/Warrior/block/source/make_block_strip.py

1. Cuts the user's ChatGPT sheet (armored_block_6frame_sheet.png, 1536 x 1024, 3 x 2) like the Hit (docs/PLAYBOOK.md): slice_keypose_sheet.py, 408 px tall, heel on x 160, frames 1 and 6 scaled to exactly 408.
2. Replaces frames 1 and 6 by the IDLE's frame 1 (the sheet's two guard-stance frames matched the idle at 0.935 of the silhouette, the Hit's at 0.967: the pack starts and ends on the idle, so it is the idle's own frame, no pop).
3. Writes the placement (fps 12, blockFrame 4: the frame on screen when the blow lands, like the dodge's evadeFrame) and DRAFT hand marks: the fists read off the frames by eye (frames 2 to 5), the idle's marks for frames 1 and 6;
   the near fist (the off hand, the second sword, in front of the body) at the face on frames 3 and 4 with the blade tilted forward, the far fist (the main hand, the first sword, behind the body) beside it with the blade tilted back,
   so the two blades cross in front of the face. The user re-marks them in the hand tool.
"""
import json, os, subprocess, sys
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
WB = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(WB, "..", "..", ".."))
TOOLS = os.path.join(ROOT, "source", "tools")
SHEET = os.path.join(HERE, "armored_block_6frame_sheet.png")
STRIP = os.path.join(WB, "armored_block_6frame_strip.png")
IDLE = os.path.join(ROOT, "Animations", "Warrior", "idle", "armored_idle_strip.png")
IDLE_MARKS = os.path.join(ROOT, "Animations", "Warrior", "idle", "armored_idle_strip.hand-anchors.json")
HIT_MARKS = os.path.join(ROOT, "Animations", "Warrior", "hit", "armored_hit_6frame_strip.hand-anchors.json")

# 1. cut
subprocess.check_call([sys.executable, os.path.join(TOOLS, "slice_keypose_sheet.py"), SHEET, STRIP, "--cols", "3", "--rows", "2", "--height", "408", "--scale-from", "median", "--modes", "heel", "--heel-x", "160",
                       "--fit", "1,6", "--despill-band", "10", "--despill-thr", "4"], cwd=TOOLS)
# 2. frames 1 and 6 = the idle's frame 1
st = Image.open(STRIP).convert("RGBA"); idle = Image.open(IDLE).convert("RGBA").crop((0, 0, 512, 512))
for k in (0, 5):
    st.paste((0, 0, 0, 0), (k * 512, 0, k * 512 + 512, 512)); st.alpha_composite(idle, (k * 512, 0))
st.save(STRIP)
# 3. placement
pl = {"format": "frame-placement/1", "animation": "block", "file": os.path.basename(STRIP), "frames": 6, "fps": 12, "blockFrame": 4,
      "note": "blockFrame: the frame on screen when the blow lands (the page starts the pack early enough); frames 1 and 6 are the idle's frame 1"}
json.dump(pl, open(STRIP.replace(".png", ".placement.json"), "w"), indent=1)
# 4. draft marks: fist centres in px of the 512 frame, read off the frames by eye
FISTS = {   # frame: (near fist = off hand, far fist = main hand)
    2: ((283, 207), (385, 157)),
    3: ((345, 143), (381, 183)),
    4: ((273, 147), (320, 180)),
    5: ((325, 147), (371, 183)),
}
ANG = {2: (15, -40), 3: (35, -38), 4: (38, -34), 5: (30, -38)}   # frame: (off blade, main blade) in degrees, 0 = up, clockwise positive
idle_c = json.load(open(IDLE_MARKS, encoding="utf-8"))["characters"][0]
ia = idle_c["animations"][0]
doc = json.load(open(HIT_MARKS, encoding="utf-8"))
c = doc["characters"][0]
main, off = [], []
for k in range(1, 7):
    if k in (1, 6):
        main.append(dict(ia["tracks"]["main"][0])); off.append(dict(ia["tracks"]["off"][0])); continue
    (ox, oy), (mx, my) = FISTS[k]
    ao, am = ANG[k]
    off.append({"x": round(ox / 512, 3), "y": round(oy / 512, 3), "a": ao, "front": True, "hide": False, "w": 1})
    main.append({"x": round(mx / 512, 3), "y": round(my / 512, 3), "a": am, "front": False, "hide": False, "w": 1})
c["animations"] = [{"name": "armored_block_6frame", "frames": 6, "columns": 6, "fps": 12, "offItem": dict(ia["offItem"]), "tracks": {"main": main, "off": off}}]
doc["note"] = doc.get("note", "")
json.dump(doc, open(STRIP.replace(".png", ".hand-anchors.json"), "w"), indent=1)
print("strip", os.path.relpath(STRIP, ROOT), "| placement and DRAFT marks written")
