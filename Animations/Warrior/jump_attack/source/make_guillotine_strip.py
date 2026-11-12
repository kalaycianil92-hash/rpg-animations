#!/usr/bin/env python3
"""Builds the Warrior's NEW Thunderclap Guillotine strip (11 frames, cells 512 x 640) from two ChatGPT sheets (2026-11-12):

  sheet A  source/thunderclap_guillotine_sheet_A.png   (the user's picks: panels 1, 3, 4, 5)
  sheet B  inbox/warrior_Thunderclap_Guillotine_sheetB.png  (copy in source/thunderclap_guillotine_sheet_B.png)
  the idle strip (its first frame is pasted in as the last frame)

  frame  1 crouch          A1   grounded
  frame  2 crouch          A1   (the charge: two frames of the same pose, the page holds them 100 ms each)
  frame  3 launch          B1   airborne (the vertical spring; A2 = the Superman launch and B2 = the bounding leap are the alternates)
  frame  4 rising arch     A3   airborne
  frame  5 APEX ARCH       A4   airborne (held 300 ms by the page)
  frame  6 plunge          A5   airborne, falling feet-first, swords overhead
  frame  7 STRIKE (air)    B3   airborne: the swords chop down onto the target = the hit frame
  frame  8 strike, landed  B4   grounded lunge
  frame  9 follow-through  B5   grounded deep lunge (the old jump's frame 7)
  frame 10 recover         B6   grounded, rising toward the guard
  frame 11 the idle's first frame (the guard stance)

The sheets are drawn bigger than the idle: the scales below (A 1.00, B 0.91) bring the heads to the idle's (about 75 px) and the two sheets to each other
(sheet B's boots are about 10% longer than sheet A's). Cells are 512 x 640 with the ground line 42 px above the bottom (y = 598), like the old jump:
grounded frames stand on it with the middle of the feet at x = 293 (the idle's); airborne frames are pure poses (lowest point on the ground line, bounding
box centred at x = 293): the page's path gives the height.  Keying and despill are the project's (slice_keypose_sheet.py, despill band 10 / threshold 4).

  python make_guillotine_strip.py [--only-preview]
"""
import json
import pathlib
import sys
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[3]
D = HERE.parent
SHEET_A = HERE / "thunderclap_guillotine_sheet_A.png"
SHEET_B = HERE / "thunderclap_guillotine_sheet_B.png"
if not SHEET_B.exists():
    SHEET_B = ROOT / "inbox" / "warrior_Thunderclap_Guillotine_sheetB.png"
IDLE = ROOT / "Animations" / "Warrior" / "idle" / "armored_idle_strip.png"
NAME = "armored_thunderclap_guillotine_11frame_strip"
CW, CH, GROUND, FEET_X = 512, 640, 598, 293
SCALE = {"A": 1.00, "B": 0.91}
DESPILL_BAND, DESPILL_THR = 10, 4

# (sheet, panel 1-6, mode)  grounded = middle of the lowest 10% at FEET_X; air = bounding box centre at FEET_X, lowest point on the ground line
FRAMES = [("A", 1, "ground"), ("A", 1, "ground"), ("B", 1, "air"), ("A", 3, "air"), ("A", 4, "air"), ("A", 5, "air"),
          ("B", 3, "air"), ("B", 4, "ground"), ("B", 5, "ground"), ("B", 6, "ground"), ("idle", 1, "idle")]


def key_sheet(path):
    img = np.array(Image.open(path).convert("RGB")).astype(float)
    r, g, b = img[..., 0], img[..., 1], img[..., 2]
    alpha = 1 - np.clip((np.minimum(r, b) - g - 70) / 110, 0, 1)
    soft = alpha < 1
    rgb = img.copy()
    rgb[..., 0] = np.where(soft, np.minimum(r, g + 25), r)
    rgb[..., 2] = np.where(soft, np.minimum(b, g + 25), b)
    band = ndi.binary_dilation(alpha < 0.5, iterations=DESPILL_BAND) & (alpha >= 0.5)
    mm = np.minimum(rgb[..., 0], rgb[..., 2]) - rgb[..., 1]
    fix = (band | soft) & (mm > DESPILL_THR)
    rgb[..., 0] = np.where(fix, np.minimum(rgb[..., 0], rgb[..., 1] + DESPILL_THR), rgb[..., 0])
    rgb[..., 2] = np.where(fix, np.minimum(rgb[..., 2], rgb[..., 1] + DESPILL_THR), rgb[..., 2])
    return np.dstack([rgb, alpha * 255]).astype(np.uint8)


def panel(rgba, k, cols=3, rows=2):
    H, W = rgba.shape[:2]
    pw, ph = W // cols, H // rows
    r, c = divmod(k - 1, cols)
    p = rgba[r * ph:(r + 1) * ph, c * pw:(c + 1) * pw].copy()
    solid = p[..., 3] > 128
    lab, n = ndi.label(solid)
    sizes = ndi.sum(solid, lab, range(1, n + 1))
    main = lab == 1 + int(np.argmax(sizes))
    kept = ndi.binary_dilation(main, iterations=3)
    p[..., 3] = np.where(kept, p[..., 3], 0)
    return p


def bbox(a):
    ys, xs = np.where(a > 128)
    return xs.min(), ys.min(), xs.max(), ys.max()


def place(p, sc, mode):
    x0, y0, x1, y1 = bbox(p[..., 3])
    im = Image.fromarray(p).resize((int(round(p.shape[1] * sc)), int(round(p.shape[0] * sc))), Image.LANCZOS)
    if mode == "ground":
        low = p[int(y1 - 0.10 * (y1 - y0)):y1 + 1, :, 3] > 128
        lx = np.where(low.any(0))[0]
        ox = FEET_X - (lx.min() + lx.max()) / 2 * sc
    else:
        ox = FEET_X - (x0 + x1) / 2 * sc
    oy = GROUND - y1 * sc
    canvas = Image.new("RGBA", (3000, 3000), (0, 0, 0, 0))
    canvas.alpha_composite(im, (1000 + int(round(ox)), 1000 + int(round(oy))))
    frame = canvas.crop((1000, 1000, 1000 + CW, 1000 + CH))
    clipped = int((np.array(im)[..., 3] > 128).sum() - (np.array(frame)[..., 3] > 128).sum())
    return frame, clipped


def main():
    sheets = {"A": key_sheet(SHEET_A), "B": key_sheet(SHEET_B)}
    idle = Image.open(IDLE).convert("RGBA").crop((0, 0, 512, 512))
    out = Image.new("RGBA", (CW * len(FRAMES), CH), (0, 0, 0, 0))
    for i, (s, k, mode) in enumerate(FRAMES):
        if s == "idle":
            fr = Image.new("RGBA", (CW, CH), (0, 0, 0, 0)); fr.alpha_composite(idle, (0, CH - 512)); clipped = 0
        else:
            fr, clipped = place(panel(sheets[s], k), SCALE[s], mode)
        a = np.array(fr)[..., 3]
        bx = bbox(a)
        print("frame %2d  %s%d %-6s clipped %d  bbox x %d-%d y %d-%d  (h %d, w %d)" % (i + 1, s, k, mode, clipped, bx[0], bx[2], bx[1], bx[3], bx[3] - bx[1], bx[2] - bx[0]))
        out.alpha_composite(fr, (i * CW, 0))
    dst = D / (NAME + ".png")
    out.save(dst)
    print("wrote", dst, out.size)


if __name__ == "__main__":
    main()
