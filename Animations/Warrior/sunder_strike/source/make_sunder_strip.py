#!/usr/bin/env python3
"""Builds the Warrior's Sunder Strike strip (8 frames, cells 512 x 512, ground line y = 470) from the user's three ChatGPT sheets (2026-11-13) and the Thunderclap's sheet B.

The user generated three versions of the v3 prompt and named the files after the panels to use:
  S1 warrior_sunder_strike_sheet_first2frame.png      panels 1, 2   (wind-up, raise)
  S2 warrior_sunder_strike_alternate_frame3.png       panel 3       (step-in)
  S3 warrior_sunder_strike_alternate_last3frame.png   panels 4, 5, 6 (cleave A, cleave B, follow-through)

  frame 1 wind-up         S1 panel 1   120 ms
  frame 2 raise           S1 panel 2   100 ms
  frame 3 step-in         S2 panel 3    70 ms
  frame 4 CLEAVE A        S3 panel 4    90 ms   the hit frame (the impact 40% into it)
  frame 5 cleave B        S3 panel 5   100 ms
  frame 6 follow-through  S3 panel 6   120 ms
  frame 7 recover         the Thunderclap's sheet B panel 6 (the same man, already used there) 100 ms
  frame 8 the idle's first frame (pasted in)

Every panel is GROUNDED: the REAR heel (the left-most point of the lowest 8%) goes to x = 128 (30 px left of the idle's rear heel at 160, because the lunges are 350 px wide and the cell is 512: at 160 two
frames were clipped on the right; the rear foot stays planted from frame to frame and the front boot steps forward) and the lowest point goes to the ground line y = 470. The sheets were drawn bigger than the idle and not equally big (the boots measure 80 px on S1, 85 on S2, 89 on S3, 86 on B against
the 71 px of the idle's front boot); the scales below bring them to one size (the Thunderclap's sheet B at 0.91 gives a 78 px boot). Keying and despill are the project's (band 10, threshold 4).

  python make_sunder_strip.py
"""
import pathlib
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[3]
D = HERE.parent
SRC = {
    "S1": HERE / "warrior_sunder_strike_sheet_first2frame.png",
    "S2": HERE / "warrior_sunder_strike_alternate_frame3.png",
    "S3": HERE / "warrior_sunder_strike_alternate_last3frame.png",
    "B": ROOT / "Animations" / "Warrior" / "jump_attack" / "source" / "thunderclap_guillotine_sheet_B.png",
}
IDLE = ROOT / "Animations" / "Warrior" / "idle" / "armored_idle_strip.png"
NAME = "armored_sunder_strike_8frame_strip"
CW, CH, GROUND, HEEL_X = 512, 512, 470, 128      # (the idle's rear heel is 160; the wide lunges need the room on the right: the cell is 512 wide, so the rear heel of the pose frames is at 128 and only the pasted idle frame stays at 160)
SCALE = {"S1": 0.963, "S2": 0.918, "S3": 0.876, "B": 0.91}
DESPILL_BAND, DESPILL_THR = 10, 4
FRAMES = [("S1", 1), ("S1", 2), ("S2", 3), ("S3", 4), ("S3", 5), ("S3", 6), ("B", 6), ("idle", 1)]


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


def place(p, sc):
    x0, y0, x1, y1 = bbox(p[..., 3])
    im = Image.fromarray(p).resize((int(round(p.shape[1] * sc)), int(round(p.shape[0] * sc))), Image.LANCZOS)
    low = p[int(y1 - 0.08 * (y1 - y0)):y1 + 1, :, 3] > 128
    lx = np.where(low.any(0))[0]
    ox = HEEL_X - lx.min() * sc                                           # the rear heel on the idle's rear heel
    oy = GROUND - y1 * sc
    canvas = Image.new("RGBA", (3000, 3000), (0, 0, 0, 0))
    canvas.alpha_composite(im, (1000 + int(round(ox)), 1000 + int(round(oy))))
    frame = canvas.crop((1000, 1000, 1000 + CW, 1000 + CH))
    clipped = int((np.array(im)[..., 3] > 128).sum() - (np.array(frame)[..., 3] > 128).sum())
    return frame, clipped


def main():
    keyed = {k: key_sheet(v) for k, v in SRC.items()}
    idle = Image.open(IDLE).convert("RGBA").crop((0, 0, 512, 512))
    out = Image.new("RGBA", (CW * len(FRAMES), CH), (0, 0, 0, 0))
    for i, (s, k) in enumerate(FRAMES):
        if s == "idle":
            fr, clipped = idle, 0
        else:
            fr, clipped = place(panel(keyed[s], k), SCALE[s])
        bx = bbox(np.array(fr)[..., 3])
        print("frame %d  %s%d  clipped %d  bbox x %d-%d y %d-%d (h %d, w %d)" % (i + 1, s, k, clipped, bx[0], bx[2], bx[1], bx[3], bx[3] - bx[1], bx[2] - bx[0]))
        out.alpha_composite(fr, (i * CW, 0))
    dst = D / (NAME + ".png")
    out.save(dst)
    print("wrote", dst, out.size)


if __name__ == "__main__":
    main()
