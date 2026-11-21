#!/usr/bin/env python3
"""Builds the Cleric's SPITEFUL COVENANT strip (2026-11-22).

  python Animations/Cleric/spiteful_covenant/source/make_covenant_strip.py [--out PATH]

The user's ChatGPT sheet (cleric_spiteful_covenant_sheet_3x2.png, 1536 x 1024, 3 x 2): paying in pain, then a roar of defiance. Checked 2026-11-22, every panel counted: ONE near arm (its big pauldron and ring-mail sleeve)
across the chest in all six panels; the far arm is driven into his belly (1, 2: the second fist is the far one, from the smaller far shoulder), hangs clenched (3), is thrown up and forward from behind his neck (4), is
bent at head height (5), guard (6). He does not move: the FRONT foot stays on the same spot, so
 1. slice_keypose_sheet.py cuts 640 x 640 cells (ground y 598: the roar's fist is about 112% of his height above the floor, too close to the top of a 512 cell), TOE mode, the front toe pinned on the idle's x 411
    (+ the crop's 64); the SCALE from the standing panels (the median of the six heights, panels 1 and 2 are bowed and lower) with panels 5 and 6 fitted to exactly 408 px;
 2. each cell is cropped to 512 wide (cell x 64..576); the idle's first frame is pasted as frame 7 (padded to 640 tall, ground 470 -> 598);
 3. the placement: fps 14, hitFrame 4 (the ROAR, the lock), holds 129/529/149/29/209/69/0 (frames 1 to 3 doubled, 2026-11-22), a FLAT path.
Then: python source/tools/even_heads.py --char cleric --ref Animations/Cleric/idle/mailed_idle_strip.png <the strip>.
"""
import argparse, json, os, subprocess, sys
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
COV = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(COV, "..", "..", ".."))
TOOLS = os.path.join(ROOT, "source", "tools")
ap = argparse.ArgumentParser()
ap.add_argument("--out", default=os.path.join(COV, "mailed_spiteful_covenant_7frame_strip.png"))
ap.add_argument("--scale-from", default="median", choices=["median", "panel1"])
a = ap.parse_args()
SHEET = os.path.join(HERE, "cleric_spiteful_covenant_sheet_3x2.png")
IDLE = os.path.join(ROOT, "Animations", "Cleric", "idle", "mailed_idle_strip.png")
TMP = os.path.join(HERE, "_cut640.png")
GROUND, CELL_H, CELL_W, PAD, TOE = 598, 640, 512, 64, 411

subprocess.check_call([sys.executable, os.path.join(TOOLS, "slice_keypose_sheet.py"), SHEET, TMP, "--cols", "3", "--rows", "2", "--height", "408", "--scale-from", a.scale_from, "--fit", "5,6",
                       "--modes", "toe", "--toe-x", str(TOE + PAD), "--frame", "640", "--ground", str(GROUND)], cwd=TOOLS)
im = Image.open(TMP).convert("RGBA")
cells = [im.crop((i * 640 + PAD, 0, i * 640 + PAD + CELL_W, CELL_H)) for i in range(im.width // 640)]
n = len(cells)
idle = Image.new("RGBA", (CELL_W, CELL_H), (0, 0, 0, 0))
idle.alpha_composite(Image.open(IDLE).convert("RGBA").crop((0, 0, 512, 512)), (0, GROUND - 470))
out = Image.new("RGBA", (CELL_W * (n + 1), CELL_H), (0, 0, 0, 0))
for i, c in enumerate(cells):
    out.paste(c, (i * CELL_W, 0))
out.alpha_composite(idle, (n * CELL_W, 0))
out.save(a.out)
os.remove(TMP)
print("wrote", a.out, out.size)

pl = {"format": "frame-placement/1", "animation": "attack", "file": os.path.basename(a.out), "frames": n + 1, "fps": 14, "hitFrame": 4, "smooth": True,
      "holds": [129, 529, 149, 29, 209, 69, 0], "x": [0] * (n + 1), "y": [0] * (n + 1),
      "note": "Spiteful Covenant, a DRAFT. 7 frames at 14 fps (71 ms each) with holds: PAY 200 ms (the cost: dark-red motes drawn out of his chest, his HP drops), DOUBLED OVER 600, RISE 220 (frames 1 to 3 doubled at the user's request, 2026-11-22), the ROAR 100 "
              "(the lock: hitFrame 4, the barrier erupts), HOLD 280, recover 140, the idle's frame. A FLAT path (x and y all 0): he casts from where he stands and does not move."}
with open(a.out.replace(".png", ".placement.json"), "w", encoding="utf-8", newline="\n") as f:
    json.dump(pl, f, indent=1)
