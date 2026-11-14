#!/usr/bin/env python3
"""Builds the Warrior's Static Bash strip (21 frames, cells 512 x 512, ground line y = 470) from the idle strip (the infusion), the Warrior's RUN strip (the sprint) and two sheets (2026-11-13 / 14).

  frames 1-6    the idle strip's frames 1-6: he stands in the idle while the swords are infused with lightning (the page's crackle builds up)
  frames 7-15   the run strip's frames 1 2 3 4 5 1 2 3 4, pasted as they are (the user's approved run: he starts running at full speed)
  frame 16      skid                 static_bash_sheet_new.png panel 2  (the animation slows down)
  frame 17      the swords RAISED    thunderclap_guillotine_sheet_A.png panel 6 (the user's idea, 2026-11-14: "add the Thunderclap sheet's 6th frame": a braced stance, both fists above the head)
  frame 18      SLAM                 static_bash_sheet_new.png panel 4  (the hit)
  frame 19      heavy slam           static_bash_sheet_new.png panel 5
  frame 20      recover              the Thunderclap's sheet B panel 6
  frame 21      the idle's first frame

The strike frames (16-20) are aligned by the FRONT TOE (x = 430): in a skid the front boot is planted while the rear leg slides, so the front foot must not jump between the skid, the raise and the slam
(the Sunder Strike's frames are aligned by the rear heel instead). Scales bring the boots to 78 px: the new sheet 0.95 (its boots measure 82), the Thunderclap's sheet A 0.96 (81), sheet B 0.91 (86).

  python make_static_bash_strip.py
"""
import pathlib
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[3]
D = HERE.parent
SRC = {
    "N": HERE / "static_bash_sheet_new.png",
    "A": ROOT / "Animations" / "Warrior" / "jump_attack" / "source" / "thunderclap_guillotine_sheet_A.png",
    "B": ROOT / "Animations" / "Warrior" / "jump_attack" / "source" / "thunderclap_guillotine_sheet_B.png",
}
RUN = ROOT / "Animations" / "Warrior" / "run" / "armored_run_5frame_strip.png"
IDLE = ROOT / "Animations" / "Warrior" / "idle" / "armored_idle_strip.png"
NAME = "armored_static_bash_21frame_strip"
CW, CH, GROUND, TOE_X = 512, 512, 470, 430
SCALE = {"N": 0.95, "A": 0.96, "B": 0.91}
DESPILL_BAND, DESPILL_THR = 10, 4
# ("idle", cell) | ("run", cell) | (sheet letter, panel)
FRAMES = [("idle", 1), ("idle", 2), ("idle", 3), ("idle", 4), ("idle", 5), ("idle", 6),
          ("run", 1), ("run", 2), ("run", 3), ("run", 4), ("run", 5), ("run", 1), ("run", 2), ("run", 3), ("run", 4),
          ("N", 2), ("A", 6), ("N", 4), ("N", 5), ("B", 6), ("idle", 1)]


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
    run = Image.open(RUN).convert("RGBA")
    idle = Image.open(IDLE).convert("RGBA")
    out = Image.new("RGBA", (CW * len(FRAMES), CH), (0, 0, 0, 0))
    for i, (s, k) in enumerate(FRAMES):
        clipped = 0
        if s == "run":
            fr = run.crop(((k - 1) * 512, 0, k * 512, 512))
        elif s == "idle":
            fr = idle.crop(((k - 1) * 512, 0, k * 512, 512))
        else:
            fr, clipped = place(panel(keyed[s], k), SCALE[s])
        bx = bbox(np.array(fr)[..., 3])
        print("frame %2d  %s%d  clipped %d  bbox x %d-%d y %d-%d (h %d, w %d)" % (i + 1, s, k, clipped, bx[0], bx[2], bx[1], bx[3], bx[3] - bx[1], bx[2] - bx[0]))
        out.alpha_composite(fr, (i * CW, 0))
    dst = D / (NAME + ".png")
    out.save(dst)
    print("wrote", dst, out.size)


if __name__ == "__main__":
    main()
