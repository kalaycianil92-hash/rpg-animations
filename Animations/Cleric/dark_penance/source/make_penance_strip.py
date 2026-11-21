#!/usr/bin/env python3
"""Builds the Cleric's DARK PENANCE strip (2026-11-21).

  python Animations/Cleric/dark_penance/source/make_penance_strip.py [--out PATH]

The user's ChatGPT sheet (cleric_dark_penance_sheet_3x2.png, 1536 x 1024, 3 x 2). A kneeling cast that never moves forward: the FRONT foot stays on the same spot, so
 1. slice_keypose_sheet.py cuts it in TOE mode, the front toe pinned on x 411 (his idle's), 512 x 512 cells, ground y 470 (nothing rises above his standing height: no tall cell);
 2. the SCALE comes from panel 1 and panels 5 and 6 are fitted to exactly 408 px (--scale-from panel1 --fit 5,6): the standing frames (1, 5, 6) are drawn 418 px tall in the sheet but the kneeling ones about
    330, so the usual median scale would have made the standing frames 8% too big (439 to 443 px against his idle's 407); this way the three standing frames come out at the idle's size and footing
    (rear heel 173 to 174, front toe 410 to 411) and the cast starts and ends exactly where the idle stands;
 3. the idle's first frame is pasted as frame 7;
 4. the placement is written: fps 14, hitFrame 4, holds, and a FLAT path (x and y all 0: he does not move; the effect runs along the floor from him to the target).
Then: python source/tools/even_heads.py --char cleric --ref Animations/Cleric/idle/mailed_idle_strip.png <the strip>  (a bowed head reads differently: check by eye).
"""
import argparse, json, os, subprocess, sys
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
PEN = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(PEN, "..", "..", ".."))
TOOLS = os.path.join(ROOT, "source", "tools")
ap = argparse.ArgumentParser()
ap.add_argument("--out", default=os.path.join(PEN, "mailed_dark_penance_7frame_strip.png"))
a = ap.parse_args()
SHEET = os.path.join(HERE, "cleric_dark_penance_sheet_3x2.png")
IDLE = os.path.join(ROOT, "Animations", "Cleric", "idle", "mailed_idle_strip.png")

subprocess.check_call([sys.executable, os.path.join(TOOLS, "slice_keypose_sheet.py"), SHEET, a.out, "--cols", "3", "--rows", "2", "--height", "408", "--scale-from", "panel1", "--fit", "5,6",
                       "--modes", "toe", "--toe-x", "411"], cwd=TOOLS)
st = Image.open(a.out).convert("RGBA")
n = st.width // 512
out = Image.new("RGBA", (512 * (n + 1), 512), (0, 0, 0, 0))
out.paste(st, (0, 0))
out.alpha_composite(Image.open(IDLE).convert("RGBA").crop((0, 0, 512, 512)), (n * 512, 0))
out.save(a.out)
frames = n + 1
pl = {"format": "frame-placement/1", "animation": "attack", "file": os.path.basename(a.out), "frames": frames, "fps": 14, "hitFrame": 4, "smooth": True,
      "holds": [39, 19, 249, 9, 69, 39, 0], "x": [0] * frames, "y": [0] * frames,
      "note": "Dark Penance, a DRAFT. 7 frames at 14 fps (71 ms each) with holds: BOW 110 ms, KNEEL 90, the GATHER pause 320 (the code's dark gathers and creeps along the floor), RELEASE 80 (the hit at its end: hitFrame 4), POINT 140, recover 110, the idle's frame. "
              "A FLAT path (x and y all 0): he casts from where he stands and does not move."}
with open(a.out.replace(".png", ".placement.json"), "w", encoding="utf-8", newline="\n") as f:
    json.dump(pl, f, indent=1)
print("wrote", a.out, out.size)
