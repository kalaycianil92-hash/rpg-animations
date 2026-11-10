"""Earthbreaker sheet preparation (2026-11-10): erases the stone ARM that the generator grew from the body to the fist in panels 2 and 5, so the fist floats as in the accepted Elite look.

The sheet (inbox/Elite_slime_animations/elite_slime_earth_breaker.jpg, 2752 x 1536, 3 x 2) is read, the arms are painted out with the magenta key, and the cleaned copy is returned. How it works:
  - the arm is a grey area behind the head, bounded by thick near-black outlines (luminance < 55): a flood fill of the non-dark pixels from a seed inside the arm finds it (panel 5);
    in panel 2 the arm and the fist are one grey area, so a short dark barrier line (BARRIER) is drawn first between the fist and the arm: it becomes the fist's closing outline;
  - the arm's own silhouette outline (dark, next to the magenta) and its inner crack lines are removed with it; the outlines of the head, plate, fist, crossguard and blade are protected
    (every dark pixel within 13 px of another big grey area, plus the PROTECT boxes);
  - hairline leftovers are cleaned by a small opening inside the arm's neighbourhood.
"""
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

OUTLINE = (36, 32, 40)
KEY = (255, 0, 255)

# panel 5 (bottom middle): the window (x0, y0, x1, y1) of the sheet, a seed inside the arm, boxes whose dark pixels are kept
P5 = dict(win=(1450, 880, 1900, 1480), seed=(1650, 1133), protect=[(1560, 940, 1625, 1045), (1625, 1048, 1800, 1112)], barrier=None)
# panel 2 (top middle): filled in below once the cut line is chosen
P2 = dict(win=(1400, 20, 1850, 520), seed=(1610, 240), protect=[(1480, 150, 1605, 340), (1615, 170, 1770, 225)],
          barrier=[(1622, 142), (1640, 163), (1657, 173), (1673, 177), (1673, 196)])


def M2(a):
    return (np.minimum(a[..., 0], a[..., 2]).astype(int) - a[..., 1]) > 100


def remove_arm(arr, win, seed, protect, barrier=None, dilate=30, dark_thr=55):
    x0, y0, x1, y1 = win
    sub = arr[y0:y1, x0:x1].copy()
    if barrier:                                                              # a dark line between the fist and the arm (the fist's closing outline)
        from PIL import ImageDraw
        im = Image.fromarray(sub); d = ImageDraw.Draw(im)
        d.line([(px - x0, py - y0) for px, py in barrier], fill=OUTLINE, width=5)
        sub = np.array(im)
    lum = sub.astype(int).mean(axis=2)
    M = (np.minimum(sub[..., 0], sub[..., 2]).astype(int) - sub[..., 1]) > 100
    dark = lum < dark_thr; free = ~dark & ~M
    lab, n = ndi.label(free); a = lab[seed[1] - y0, seed[0] - x0]
    assert a > 0, "seed is not in a free area"
    arm = lab == a
    sizes = ndi.sum(free, lab, range(1, n + 1))
    big = np.zeros_like(free)
    for i in range(1, n + 1):
        if i != a and sizes[i - 1] > 300: big |= (lab == i)
    prot = dark & ndi.binary_dilation(big, iterations=13)
    for (bx0, by0, bx1, by1) in protect:
        prot[by0 - y0:by1 - y0, bx0 - x0:bx1 - x0] |= dark[by0 - y0:by1 - y0, bx0 - x0:bx1 - x0]
    rem = arm | (dark & ndi.binary_dilation(arm, iterations=dilate) & ~prot)
    zone = ndi.binary_dilation(arm, iterations=dilate)
    rem |= zone & ~rem & ~M & ~big & ~prot
    out = sub.copy(); out[rem] = KEY
    # hairline leftovers: whatever is thinner than 5 px inside the arm's neighbourhood
    solid = (np.minimum(out[..., 0], out[..., 2]).astype(int) - out[..., 1]) < 30          # clearly not magenta-tinted (the anti-aliased hairlines of the removed outlines are tinted)
    opened = ndi.binary_opening(solid, structure=np.ones((5, 5), bool))
    thin = ~opened & zone & ~M2(out)
    out[thin] = KEY
    new = arr.copy(); new[y0:y1, x0:x1] = out
    return new, int(rem.sum()), int(thin.sum())


def clean(src, dst):
    arr = np.array(Image.open(src).convert("RGB"))
    for name, job in (("panel 5", P5), ("panel 2", P2)):
        if job["barrier"] is None and name == "panel 2": continue
        arr, r, t = remove_arm(arr, **job)
        print("  %s: arm removed (%d px, %d hairline px)" % (name, r, t))
    Image.fromarray(arr).save(dst)
    return dst
