#!/usr/bin/env python3
"""Builds the Cleric's UNHOLY SIPHON strip (2026-11-21).

  python Animations/Cleric/unholy_siphon/source/make_siphon_strip.py [--toe 411] [--out PATH]

The user's ChatGPT sheet (cleric_unholy_siphon_sheet_3x2.png, 1536 x 1024, 3 x 2): a reach and a wrench. The FAR arm hangs (1), shoots out at chest height (2), is held out higher (3), is yanked back behind the hip
while he leans back (4), is held in front of the belt with the eyes closed (5), guard (6); the NEAR arm stays at his chest in every panel (checked 2026-11-21: right in all six panels). He does not move: the FRONT
foot stays on the same spot, so
 1. slice_keypose_sheet.py cuts it in TOE mode, the front toe pinned on his idle's x 411, 512 x 512 cells, ground y 470 (nothing rises above his standing height), the scale from panel 1 (standing) and panels 5 and
    6 fitted to exactly 408 px (--scale-from panel1 --fit 5,6), as for Dark Penance;
 2. the idle's first frame is pasted as frame 7;
 3. the placement is written: fps 14, hitFrame 4 (the WRENCH), holds 19/0/249/9/89/39/0, a FLAT path.
Then: python source/tools/even_heads.py --char cleric --ref Animations/Cleric/idle/mailed_idle_strip.png <the strip>.
"""
import argparse, json, os, subprocess, sys
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
SIP = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(SIP, "..", "..", ".."))
TOOLS = os.path.join(ROOT, "source", "tools")
ap = argparse.ArgumentParser()
ap.add_argument("--toe", type=float, default=411, help="x the front toe is pinned on (his idle's)")
ap.add_argument("--out", default=os.path.join(SIP, "mailed_unholy_siphon_7frame_strip.png"))
a = ap.parse_args()
SHEET = os.path.join(HERE, "cleric_unholy_siphon_sheet_3x2.png")
IDLE = os.path.join(ROOT, "Animations", "Cleric", "idle", "mailed_idle_strip.png")

subprocess.check_call([sys.executable, os.path.join(TOOLS, "slice_keypose_sheet.py"), SHEET, a.out, "--cols", "3", "--rows", "2", "--height", "408", "--scale-from", "panel1", "--fit", "5,6",
                       "--modes", "toe", "--toe-x", str(a.toe)], cwd=TOOLS)
st = Image.open(a.out).convert("RGBA")
n = st.width // 512
out = Image.new("RGBA", (512 * (n + 1), 512), (0, 0, 0, 0))
out.paste(st, (0, 0))
out.alpha_composite(Image.open(IDLE).convert("RGBA").crop((0, 0, 512, 512)), (n * 512, 0))
out.save(a.out)
frames = n + 1
pl = {"format": "frame-placement/1", "animation": "attack", "file": os.path.basename(a.out), "frames": frames, "fps": 14, "hitFrame": 4, "smooth": True,
      "holds": [19, 0, 249, 9, 89, 39, 0], "x": [0] * frames, "y": [0] * frames,
      "note": "Unholy Siphon, a DRAFT. 7 frames at 14 fps (71 ms each) with holds: STARE 90 ms, REACH 71, the held CHANNEL 320 (the code's tendrils stream out and latch on), the WRENCH 80 (the hit: hitFrame 4), DRINK 160 (the steal flows back), recover 110, the idle's frame. "
              "A FLAT path (x and y all 0): he casts from where he stands and does not move."}
with open(a.out.replace(".png", ".placement.json"), "w", encoding="utf-8", newline="\n") as f:
    json.dump(pl, f, indent=1)
print("wrote", a.out, out.size)
