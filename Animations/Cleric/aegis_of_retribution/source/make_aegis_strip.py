#!/usr/bin/env python3
"""Builds the Cleric's AEGIS OF RETRIBUTION strip (2026-11-21).

  python Animations/Cleric/aegis_of_retribution/source/make_aegis_strip.py [--panel1 sheet|idle] [--out PATH]

The user's ChatGPT sheet (cleric_aegis_of_retribution_sheet_3x2.png, 1536 x 1024, 3 x 2): a braced cast that draws a shield in the air, the FAR arm traces a rising arc (low behind the hip, low in front,
shoulder height, high above the head, plunged down in a deep crouch, guard) and the NEAR arm stays at his chest in every panel (checked 2026-11-21: right in all six panels). The user's note: the sheet's FIRST panel was
the problem (nothing good came out in a few tries), and the skill does not have to be that distinct (it only generates a shield): so --panel1 idle (the default) starts the cast from the IDLE's first frame (his guard
stance, no pop at the start, the far fist at belt height) and the arc begins with the low sweep; --panel1 sheet uses the sheet's own first panel instead.
 1. slice_keypose_sheet.py cuts 640 x 640 cells (ground y 598; the raised fist of panel 4 is 493 px above the floor, more than a 512 cell holds above its ground line), TOE mode (his FRONT foot never moves, so
    the front toe is pinned on the idle's x 411 + 64), the scale from panel 1 and panel 6 (the guard stance) fitted to exactly 408 px, the standing panels at the idle's size;
 2. each cell is cropped to 512 wide (cell x 64..576);
 3. frame 1 is the idle's first frame (or the sheet's panel 1), the idle's first frame is pasted as frame 7 too (padded to 640 tall, ground 470 -> 598);
 4. the placement is written: fps 14, hitFrame 5 (the SEAL, the lock), holds, a FLAT path (x and y all 0: he does not move).
Then: python source/tools/even_heads.py --char cleric --ref Animations/Cleric/idle/mailed_idle_strip.png <the strip>.
"""
import argparse, json, os, subprocess, sys
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
AEG = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(AEG, "..", "..", ".."))
TOOLS = os.path.join(ROOT, "source", "tools")
ap = argparse.ArgumentParser()
ap.add_argument("--panel1", choices=["idle", "sheet"], default="idle", help="frame 1: the idle's first frame (default) or the sheet's own first panel")
ap.add_argument("--out", default=os.path.join(AEG, "mailed_aegis_of_retribution_7frame_strip.png"))
a = ap.parse_args()
SHEET = os.path.join(HERE, "cleric_aegis_of_retribution_sheet_3x2.png")
IDLE = os.path.join(ROOT, "Animations", "Cleric", "idle", "mailed_idle_strip.png")
TMP = os.path.join(HERE, "_cut640.png")
GROUND, CELL_H, CELL_W, PAD, TOE = 598, 640, 512, 64, 411

subprocess.check_call([sys.executable, os.path.join(TOOLS, "slice_keypose_sheet.py"), SHEET, TMP, "--cols", "3", "--rows", "2", "--height", "408", "--scale-from", "panel1", "--fit", "6",
                       "--modes", "toe", "--toe-x", str(TOE + PAD), "--frame", "640", "--ground", str(GROUND)], cwd=TOOLS)
im = Image.open(TMP).convert("RGBA")
cells = [im.crop((i * 640 + PAD, 0, i * 640 + PAD + CELL_W, CELL_H)) for i in range(im.width // 640)]
n = len(cells)
idle = Image.new("RGBA", (CELL_W, CELL_H), (0, 0, 0, 0))
idle.alpha_composite(Image.open(IDLE).convert("RGBA").crop((0, 0, 512, 512)), (0, GROUND - 470))
if a.panel1 == "idle":
    cells[0] = idle
out = Image.new("RGBA", (CELL_W * (n + 1), CELL_H), (0, 0, 0, 0))
for i, c in enumerate(cells):
    out.paste(c, (i * CELL_W, 0))
out.alpha_composite(idle, (n * CELL_W, 0))
out.save(a.out)
os.remove(TMP)
print("wrote", a.out, out.size)

first = 9 if a.panel1 == "idle" else 49
pl = {"format": "frame-placement/1", "animation": "attack", "file": os.path.basename(a.out), "frames": n + 1, "fps": 14, "hitFrame": 5, "smooth": True,
      "holds": [first, 0, 0, 249, 29, 69, 0], "x": [0] * (n + 1), "y": [0] * (n + 1),
      "note": "Aegis of Retribution, a DRAFT. 7 frames at 14 fps (71 ms each) with holds: BRACE " + ("80" if a.panel1 == "idle" else "120") + " ms (the idle's first frame), SWEEP LOW 71, RISE 71, the held CREST 320 (the code's glass half-dome forms), "
              "the SEAL 100 (the hit frame = the lock: hitFrame 5), STAND FIRM 140, the idle's frame. A FLAT path (x and y all 0): he casts from where he stands and does not move."}
with open(a.out.replace(".png", ".placement.json"), "w", encoding="utf-8", newline="\n") as f:
    json.dump(pl, f, indent=1)
