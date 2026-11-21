#!/usr/bin/env python3
"""Builds the Cleric's SANCTIFIED JUDGMENT strip (2026-11-22).

  python Animations/Cleric/sanctified_judgment/source/make_judgment_strip.py [--panel2 smite|sheet] [--out PATH]

The user's ChatGPT sheet (cleric_sanctified_judgment_sheet_3x2.png, 1536 x 1024, 3 x 2): a call from the heavens and a verdict. Checked 2026-11-22: panels 1, 3, 4, 5 and 6 are right (the near arm with its pauldron stays at
his chest, the far arm hangs, is raised straight up from behind the head, is thrown down and points, points a little higher, guard) but PANEL 2 (the lift) is WRONG: the raised arm comes out of the NEAR shoulder (the big
pauldron) and a second arm lies across the chest, so he has two near arms. The user's call: that frame needs a redraw. Until a redraw of panel 2 arrives:
 --panel2 smite (the default) takes frame 2 of the Radiant Smite strip instead (mailed_radiant_smite_7frame_strip.png, the same man, the same 512 x 640 cell with the ground at y 598, the far arm bent up from behind
   his shoulder with the fist at head height, the near arm at the chest, already head-evened), shifted sideways so its front toe is on the same x as the other frames (his head is level there, not tilted up: a 71 ms
   glitch in the head only);
 --panel2 sheet uses the sheet's own (wrong) panel 2.
 1. slice_keypose_sheet.py cuts 640 x 640 cells (ground y 598: panel 3's fist is 125% of his height above the floor, more than a 512 cell holds), TOE mode, the front toe pinned on the idle's x 411 (+ the crop's 64),
    the scale from panel 1 (standing tall) with panel 6 (the guard) fitted to 408 px; each cell is cropped to 512 wide (cell x 64..576);
 2. frame 2 as above; the idle's first frame is pasted as frame 7 (padded to 640 tall, ground 470 -> 598);
 3. the placement: fps 14, hitFrame 4 (the VERDICT), holds 39/0/379/29/179/69/0 (the CALL holds 450 ms), a FLAT path.
Then: python source/tools/even_heads.py --char cleric --ref Animations/Cleric/idle/mailed_idle_strip.png <the strip>.
"""
import argparse, json, os, subprocess, sys
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
JUD = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(JUD, "..", "..", ".."))
TOOLS = os.path.join(ROOT, "source", "tools")
ap = argparse.ArgumentParser()
ap.add_argument("--panel2", choices=["smite", "sheet"], default="smite", help="frame 2: Radiant Smite's frame 2 (default, until panel 2 is redrawn) or the sheet's own panel 2")
ap.add_argument("--out", default=os.path.join(JUD, "mailed_sanctified_judgment_7frame_strip.png"))
a = ap.parse_args()
SHEET = os.path.join(HERE, "cleric_sanctified_judgment_sheet_3x2.png")
IDLE = os.path.join(ROOT, "Animations", "Cleric", "idle", "mailed_idle_strip.png")
SMITE = os.path.join(ROOT, "Animations", "Cleric", "radiant_smite", "mailed_radiant_smite_7frame_strip.png")
TMP = os.path.join(HERE, "_cut640.png")
GROUND, CELL_H, CELL_W, PAD, TOE = 598, 640, 512, 64, 411


def front_toe(cell):                                                                 # the x of the front boot's toe: the right-most opaque pixel of the lowest 40 rows above the floor
    al = np.array(cell)[GROUND - 40:GROUND, :, 3] > 40
    xs = np.where(al.any(axis=0))[0]
    return int(xs.max())


subprocess.check_call([sys.executable, os.path.join(TOOLS, "slice_keypose_sheet.py"), SHEET, TMP, "--cols", "3", "--rows", "2", "--height", "408", "--scale-from", "panel1", "--fit", "6",
                       "--modes", "toe", "--toe-x", str(TOE + PAD), "--frame", "640", "--ground", str(GROUND)], cwd=TOOLS)
im = Image.open(TMP).convert("RGBA")
cells = [im.crop((i * 640 + PAD, 0, i * 640 + PAD + CELL_W, CELL_H)) for i in range(im.width // 640)]
n = len(cells)
if a.panel2 == "smite":
    sm = Image.open(SMITE).convert("RGBA").crop((CELL_W, 0, 2 * CELL_W, CELL_H))      # Radiant Smite's frame 2
    dx = front_toe(cells[0]) - front_toe(sm)                                          # the front toe goes to where the other frames have it
    moved = Image.new("RGBA", (CELL_W, CELL_H), (0, 0, 0, 0))
    moved.alpha_composite(sm, (dx, 0)) if dx >= 0 else moved.alpha_composite(sm.crop((-dx, 0, CELL_W, CELL_H)), (0, 0))
    cells[1] = moved
    print("frame 2 from the Radiant Smite strip, shifted by", dx, "px")
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
      "holds": [39, 0, 379, 29, 179, 69, 0], "x": [0] * (n + 1), "y": [0] * (n + 1),
      "note": "Sanctified Judgment, a DRAFT. 7 frames at 14 fps (71 ms each) with holds: LISTEN 110 ms, LIFT 71, the held CALL 450 (the code's ring of light and the gathering light), the VERDICT 100 (the hit: hitFrame 4, the pillar), "
              "HOLD 250, recover 140, the idle's frame. A FLAT path (x and y all 0): he casts from where he stands and does not move. Frame 2 is borrowed from the Radiant Smite strip until panel 2 of the sheet is redrawn (--panel2 smite)."}
with open(a.out.replace(".png", ".placement.json"), "w", encoding="utf-8", newline="\n") as f:
    json.dump(pl, f, indent=1)
