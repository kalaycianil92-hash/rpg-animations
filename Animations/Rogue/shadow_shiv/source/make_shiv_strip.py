#!/usr/bin/env python3
"""Builds the Rogue's Shadow Shiv strip (5 frames) from the user's sheet (rogue_shadowshiv_sheet_3x2.png, 6 panels):

  frame 1 sprint   <- panel 1 (the last stride of the dash, a flight pose)
  frame 2 plant    <- panel 2 (the braking step, the front foot planted)
  frame 3 stab     <- panel 3 (the hit frame, a long lunge, one arm thrust forward)
  frame 4 withdraw <- panel 2 again (the user's idea: the plant pose while she slides back)
  frame 5 idle     <- the first frame of her idle strip (she ends in the idle stance, back at her place)

The user dropped panels 4 to 6 of the sheet (withdraw, turn, sprint back): no turning and no running back are needed.
The cut: scale 0.8115 (her head matched to the idle's: the sheet draws her about 1.23 times too big), the front foot planted at x 410 in the plant and the stab
(it stays put during the stab), the sprint centred; default despill (the strict one blackens her burgundy hair).

  python make_shiv_strip.py
"""
import pathlib
import subprocess
import sys
from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parents[4]
D = ROOT / "Animations" / "Rogue" / "shadow_shiv"
SHEET = D / "source" / "rogue_shadowshiv_sheet_3x2.png"
CUT = D / "source" / "shiv_6panel_cut.png"
OUT = D / "cloaked_shadow_shiv_5frame_strip.png"
IDLE = ROOT / "Animations" / "Rogue" / "idle" / "cloaked_idle_strip.png"

subprocess.check_call([sys.executable, str(ROOT / "source" / "tools" / "slice_keypose_sheet.py"), str(SHEET), str(CUT), "--cols", "3", "--rows", "2",
                       "--height", "297", "--scale-from", "panel1", "--modes", "center,toe,toe,center,center,center", "--toe-x", "410"])
cut = Image.open(CUT).convert("RGBA")
idle = Image.open(IDLE).convert("RGBA")
def fr(img, k):
    return img.crop((k * 512, 0, (k + 1) * 512, 512))
order = [fr(cut, 0), fr(cut, 1), fr(cut, 2), fr(cut, 1), fr(idle, 0)]
out = Image.new("RGBA", (512 * len(order), 512), (0, 0, 0, 0))
for i, f in enumerate(order):
    out.alpha_composite(f, (i * 512, 0))
out.save(OUT)
print("wrote", OUT, out.size)
