#!/usr/bin/env python3
"""Builds the Rogue's Winter's Kiss strip (the dagger throw, 16 frames) from the user's two ChatGPT sheets joined into one 3 x 2 sheet
(rogue_dagger_throw_sheet_3x2.png: the top row of the first sheet, the corrected bottom row resized to 512 cells; see docs/PROMPTS.md "Dagger throw").

  panel 1 raise       the throwing fist beside her head (the aura forms, the dagger freezes)
  panel 2 wind-up     the arm cocked back above her head
  panel 3 throw       the release: the hand has just opened (the dagger leaves it)
  panel 4 follow      the arm stretched toward the enemy (held while the dagger flies there and back)
  panel 5 hold        NOT USED (the user: "definitely not right": eyes closed, limp wrist, chest to the viewer)
  panel 6 catch       the open palm up, reaching to catch the returning dagger
  the idle's first frame ends the strip (she is back in the idle stance, the dagger in the idle hand again)

ORDER (16 frames at 12 fps = 1.33 s, no movement: x and y are 0). The user's retiming (2026-11-04, "increase the duration of first 5 frames, and speed up 6-7-8-9th frames
slightly, so we can achieve more intense charging effect and slightly faster throw"): the old order was 12 frames at 10 fps (raise x3, wind-up x2, throw, follow x3, catch x2, idle,
100 ms a frame: charge 0.5 s, throw and follow 0.4 s), the old files are in old_12frame/. Now:
  1-5     raise  x5     the frost ring grows and spins up, the dagger frosts over      (417 ms: the old frames 1-3 and part of 4-5 stretched)
  6-9     wind-up x4    the dagger is frozen, glints, the ring at full speed           (333 ms; frames 1-9 together 0.75 s instead of 0.5 s)
  10      throw         release at the start of the frame
  11-13   follow x3     the dagger hits (frame 11, the hit frame), turns, flies back   (frames 10-13 together 0.33 s instead of 0.4 s: the throw is about 17% faster,
                        the dagger flies out in about 115 ms instead of 140)
  14-15   catch x2      the dagger lands in the open hand
  16      idle          the idle's first frame
The cut: scale 0.973 (--height 432 for panel 1; the boots match the idle's), feet mode (the middle of the feet at x 293 in every panel: the
generator let the boots drift up to 38 px across the top row), default despill (the strict one blackens her burgundy hair).

  python make_kiss_strip.py
"""
import json
import pathlib
import subprocess
import sys
from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parents[4]
R = ROOT / "Animations" / "Rogue"
D = R / "dagger_throw"
SHEET = D / "source" / "rogue_dagger_throw_sheet_3x2.png"
CUT = D / "source" / "throw_6panel_cut.png"
NAME = "cloaked_winters_kiss_16frame_strip"
IDLE = R / "idle" / "cloaked_idle_strip.png"
ORDER = [0] * 5 + [1] * 4 + [2] + [3] * 3 + [5] * 2 + ["idle"]      # panel indices (0-based); panel 5 (index 4) is dropped

subprocess.check_call([sys.executable, str(ROOT / "source" / "tools" / "slice_keypose_sheet.py"), str(SHEET), str(CUT), "--cols", "3", "--rows", "2",
                       "--height", "432", "--scale-from", "panel1", "--modes", "feet", "--feet-x", "293"])
cut = Image.open(CUT).convert("RGBA")
idle = Image.open(IDLE).convert("RGBA")
def fr(img, k):
    return img.crop((k * 512, 0, (k + 1) * 512, 512))
out = Image.new("RGBA", (512 * len(ORDER), 512), (0, 0, 0, 0))
for i, k in enumerate(ORDER):
    out.alpha_composite(fr(idle, 0) if k == "idle" else fr(cut, k), (i * 512, 0))
out.save(D / (NAME + ".png"))

# the path file: no movement at all; hit frame 11 (the first follow-through frame: the dagger arrives); fps 12
pl = {"format": "frame-placement/1", "animation": "attack", "file": NAME + ".png", "frames": len(ORDER), "fps": 12, "hitFrame": 11, "smooth": True,
      "x": [0] * len(ORDER), "y": [0] * len(ORDER),
      "note": "Winter's Kiss (the dagger throw): she stands in place in every frame (x and y are 0). Frames 1-5 raise (the frost ring grows and spins up), 6-9 wind-up (the dagger is frozen), 10 throw (release), 11-13 follow-through (the dagger hits on frame 11 and flies back), 14-15 catch, 16 the idle. 12 fps makes it 1.33 s (charge 0.75 s, throw to catch 0.58 s)."}
(D / (NAME + ".placement.json")).write_text(json.dumps(pl, ensure_ascii=False), encoding="utf-8", newline="\n")
print("wrote", D / (NAME + ".png"), out.size)
