#!/usr/bin/env python3
"""NOTE 2026-11-04: this makes the FIRST version of the strip (it is archived in old_original_8frame/); the FINAL one (frames 1-2-3-4-3-6-7-8) is made from it by make_final_strip.py.
Re-running this writes the first version into the animation folder, over the final strip: move the result to old_original_8frame/ and run make_final_strip.py.

Builds the Rogue's Abyssal Backstab strip (8 frames, TALL cells 512 x 768) from the user's ChatGPT sheet (rogue_abyssal_backstab_sheet_3x2.png) and the first two frames of the Umbral Shroud strip.

  frame 1 gather        <- Umbral Shroud frame 1 (she crouches at home)
  frame 2 wrapped       <- Umbral Shroud frame 2 (the dissolve at home)
  frame 3 emerge        <- panel 1 (in the air, both fists raised overhead)
  frame 4 coil          <- panel 2 (arched back, fists behind the head)
  frame 5 dive          <- panel 3 (nose-down, fists together forward)
  frame 6 STRIKE        <- panel 4 (nose-down about 50 degrees, both arms thrust forward and down) = the hit frame
  frame 7 land          <- panel 5 (deep crouch)
  frame 8 rise          <- panel 6 (the ready stance)

The cells are 512 wide and 768 tall (like the warrior's jump strip: the page grows tall frames upward from the unit's bottom; the ground line is 42 px above the cell's bottom, so standing
frames sit at the bottom and the airborne ones have room above AND room for the weapons round the fists). The airborne panels (1 to 4) are centred in the cell (the page moves her by code: a lift
and a dive path, aimed with the hand marks), panels 5 and 6 stand on the ground line with the middle of the feet at x 293 like her idle.

The cut: scale from panel 1 (--height 408, about 0.98) with panel 6 fitted to exactly 408 (so the rise matches her idle), default despill (the strict one blackens her burgundy hair).
  python make_abyssal_strip.py
"""
import json
import pathlib
import subprocess
import sys
import numpy as np
from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parents[4]
R = ROOT / "Animations" / "Rogue"
D = R / "abyssal_backstab"
SHEET = D / "source" / "rogue_abyssal_backstab_sheet_3x2.png"
CUT = D / "source" / "abyssal_6panel_cut.png"
UMB = R / "umbral_shroud" / "cloaked_umbral_shroud_6frame_strip.png"
NAME = "cloaked_abyssal_backstab_8frame_strip"
CW, CH = 512, 768
MULT = sys.argv[1] if len(sys.argv) > 1 else "1,1,1,1,1,1"          # per-panel size correction if the generator drew some panels too small (see the montage)
AIR_Y = 380                                                           # where the airborne figures' bounding boxes are centred vertically in the tall cell

subprocess.check_call([sys.executable, str(ROOT / "source" / "tools" / "slice_keypose_sheet.py"), str(SHEET), str(CUT), "--cols", "3", "--rows", "2", "--height", "408", "--scale-from", "panel1",
                       "--fit", "6", "--scale-mult", MULT, "--modes", "center,center,center,center,feet,feet", "--feet-x", "293"])
cut = Image.open(CUT).convert("RGBA")
umb = Image.open(UMB).convert("RGBA")

def fr(img, k):
    return img.crop((k * 512, 0, (k + 1) * 512, 512))
def bbox(im):
    a = np.array(im)[..., 3] > 128
    ys, xs = np.where(a)
    return xs.min(), ys.min(), xs.max(), ys.max()

frames = []
for k in (0, 1):                                                      # Umbral Shroud's gather and wrapped frames, standing on the ground line of the tall cell
    f = Image.new("RGBA", (CW, CH), (0, 0, 0, 0)); f.alpha_composite(fr(umb, k), (0, CH - 512)); frames.append(f)
for k in range(6):
    src = fr(cut, k)
    f = Image.new("RGBA", (CW, CH), (0, 0, 0, 0))
    if k < 4:                                                         # airborne: the bounding box centred at (256, AIR_Y)
        x0, y0, x1, y1 = bbox(src)
        f.alpha_composite(src, (int(round(256 - (x0 + x1) / 2)), int(round(AIR_Y - (y0 + y1) / 2))))
    else:                                                             # landed: on the ground line (the cut already put the feet there)
        f.alpha_composite(src, (0, CH - 512))
    frames.append(f)
out = Image.new("RGBA", (CW * len(frames), CH), (0, 0, 0, 0))
for i, f in enumerate(frames):
    out.alpha_composite(f, (i * CW, 0))
out.save(D / (NAME + ".png"))
for i, f in enumerate(frames):
    print("frame", i + 1, "bbox", bbox(f))

pl = {"format": "frame-placement/1", "animation": "attack", "file": NAME + ".png", "frames": len(frames), "fps": 12, "hitFrame": 6, "smooth": True,
      "x": [0] * len(frames), "y": [0] * len(frames),
      "note": "Abyssal Backstab: the page moves her itself (it dissolves her at home with frames 1-2, brings her into the air behind the target mirrored, dives her on the target's upper back, and back). The path file carries the fps (12) and the hit frame (6, the strike). The strike frame is held a moment by the page (hit-stop)."}
(D / (NAME + ".placement.json")).write_text(json.dumps(pl, ensure_ascii=False), encoding="utf-8", newline="\n")
print("wrote", D / (NAME + ".png"), out.size)
