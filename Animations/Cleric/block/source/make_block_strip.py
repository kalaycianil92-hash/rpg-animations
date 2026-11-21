#!/usr/bin/env python3
"""Builds the Cleric's BLOCK strip (2026-11-21), the Warrior's recipe (Animations/Warrior/block/source/make_block_strip.py).

  python Animations/Cleric/block/source/make_block_strip.py

1. Cuts the user's ChatGPT sheet (cleric_block_sheet_3x2.png, 1536 x 1024, 3 x 2) like the Hit (docs/PLAYBOOK.md): slice_keypose_sheet.py, 408 px tall, rear heel on x 174 (his idle's), frames 1 and 6 scaled to exactly 408, default despill.
2. Replaces frames 1 and 6 by the IDLE's frame 1 (the pack starts and ends on the idle, so there is no pop: the sheet's two guard frames matched the idle closely, front toe 410 and 411 against 412, but the idle's own frame is exact).
3. Writes the placement: fps 12 and blockFrame 4 (the frame on screen when the blow lands, like the dodge's evadeFrame). No hand marks yet: the user marks the shield (the near fist, in front) and the mace (the far fist) in the hand tool.
Then run  python source/tools/even_heads.py --char cleric --ref Animations/Cleric/idle/mailed_idle_strip.png Animations/Cleric/block/mailed_block_6frame_strip.png  (his head comes out 3 to 15% bigger in action sheets).
"""
import json, os, subprocess, sys
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
BLK = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(BLK, "..", "..", ".."))
TOOLS = os.path.join(ROOT, "source", "tools")
SHEET = os.path.join(HERE, "cleric_block_sheet_3x2.png")
STRIP = os.path.join(BLK, "mailed_block_6frame_strip.png")
IDLE = os.path.join(ROOT, "Animations", "Cleric", "idle", "mailed_idle_strip.png")

subprocess.check_call([sys.executable, os.path.join(TOOLS, "slice_keypose_sheet.py"), SHEET, STRIP, "--cols", "3", "--rows", "2", "--height", "408", "--scale-from", "median",
                       "--modes", "heel", "--heel-x", "174", "--fit", "1,6"], cwd=TOOLS)
st = Image.open(STRIP).convert("RGBA")
idle = Image.open(IDLE).convert("RGBA").crop((0, 0, 512, 512))
for k in (0, 5):
    st.paste((0, 0, 0, 0), (k * 512, 0, k * 512 + 512, 512))
    st.alpha_composite(idle, (k * 512, 0))
st.save(STRIP)
pl = {"format": "frame-placement/1", "animation": "block", "file": os.path.basename(STRIP), "frames": 6, "fps": 12, "blockFrame": 4,
      "note": "blockFrame: the frame on screen when the blow lands (the page starts the pack early enough); frames 1 and 6 are the idle's frame 1"}
with open(STRIP.replace(".png", ".placement.json"), "w", encoding="utf-8", newline="\n") as f:
    json.dump(pl, f, indent=1)
print("wrote", STRIP)
