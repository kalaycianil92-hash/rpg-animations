#!/usr/bin/env python3
"""Builds the Warrior's Molten Cleave strip (8 frames, cells 512 x 512, ground line y = 470) from the user's ChatGPT sheet (2026-11-20) and the Thunderclap's sheet B.

  frame 1 wind-up        panel 1  250 ms   deep crouch, both fists together at knee height behind the rear leg (the swords drag; the page heats the blades, sparks fly)
  frame 2 sweep begins   panel 2   60 ms   the step in, fists at hip height in front
  frame 3 level          panel 3   90 ms   the blow lands (the hit, 40% into it), fists at shoulder/chest height at the very front
  frame 4 rising         panel 4   70 ms
  frame 5 high           panel 5   70 ms
  frame 6 top of arc     panel 6  130 ms   both fists above the head
  frame 7 recover        the Thunderclap's sheet B panel 6  100 ms
  frame 8 the idle's first frame (pasted in)

Every panel is GROUNDED and aligned by the FRONT TOE (x = 430, as in the Static Bash): the front boot stays planted while the rear leg slides, so the front foot does not jump between the panels.
The sheet's boots measure 81-82 px on both rows (the bottom row is NOT bigger), so one scale of 0.957 brings them to 78 px (the project's target); sheet B 0.91. Keying and despill are the project's (band 10, threshold 4).

  python make_molten_strip.py
"""
import pathlib
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[3]
D = HERE.parent
SRC = {
    "M": HERE / "molten_cleave_sheet.png",
    "B": ROOT / "Animations" / "Warrior" / "jump_attack" / "source" / "thunderclap_guillotine_sheet_B.png",
}
IDLE = ROOT / "Animations" / "Warrior" / "idle" / "armored_idle_strip.png"
NAME = "armored_molten_cleave_8frame_strip"
CW, CH, GROUND, TOE_X = 512, 512, 470, 430
SCALE = {"M": 0.957, "B": 0.91}
DESPILL_BAND, DESPILL_THR = 10, 4
FRAMES = [("M", 1), ("M", 2), ("M", 3), ("M", 4), ("M", 5), ("M", 6), ("B", 6), ("idle", 1)]


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
    p[..., 3] = np.where(ndi.binary_dilation(main, iterations=3), p[..., 3], 0)
    return p


def bbox(a):
    ys, xs = np.where(a > 128)
    return xs.min(), ys.min(), xs.max(), ys.max()


def place(p, sc):
    x0, y0, x1, y1 = bbox(p[..., 3])
    im = Image.fromarray(p).resize((int(round(p.shape[1] * sc)), int(round(p.shape[0] * sc))), Image.LANCZOS)
    low = p[int(y1 - 0.08 * (y1 - y0)):y1 + 1, :, 3] > 128
    lx = np.where(low.any(0))[0]
    ox, oy = TOE_X - lx.max() * sc, GROUND - y1 * sc                  # the FRONT toe (the right-most point of the lowest 8%) on x = 430
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
