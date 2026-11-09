"""Panel loader for the ELITE slime's sheets (2026-11-10). A trimmed copy of the lightning slime's light_panels.py with the Elite's two differences:

  1. the creature is grey stone, steel, bronze and brown leather (nothing pink), so the plain magenta key is enough and the body is measured from the BIGGEST piece of its panel (no colour test);
  2. the FLOATING FIST WITH ITS SWORD is a separate piece (the generator keeps a gap between it and the body): every piece of `min_piece` px or more goes to the body it is nearest to (by real pixel distance,
     not by bounding box: the fist's box sits inside the body's box and, in the bottom row, inside the next panel's box too).

load_panels(path, row_counts, splits=()) -> dict(panels=[...]), panels in reading order. `splits` = [(x, y0, y1), ...]: the generator drew the skirts of two neighbouring panels touching each other; the piece is cut
at the column x for the rows y0..y1 (the valley between the two skirts) and the cut column goes to the LEFT panel.
Panel dict keys: p (RGBA array, tight window of the panel's own pixels), box, bw (base width: the widest row of the lowest 22% of the body), low (the body's lowest row), main (bool mask of the body),
fist (bool mask of the detached pieces), row.
"""
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

MIN_PIECE = 400


def _alpha(arr):
    r, g, b = arr[..., 0], arr[..., 1], arr[..., 2]
    return 1 - np.clip((np.minimum(r, b) - g - 70) / 110, 0, 1)


def load_panels(path, row_counts, splits=(), min_piece=MIN_PIECE):
    im0 = Image.open(path).convert("RGB")
    arr = np.array(im0).astype(float)
    r, g, b = arr[..., 0], arr[..., 1], arr[..., 2]
    alpha = _alpha(arr)
    soft = alpha < 1
    rgb = arr.copy()
    rgb[..., 0] = np.where(soft, np.minimum(r, g + 25), r); rgb[..., 2] = np.where(soft, np.minimum(b, g + 25), b)
    band = ndi.binary_dilation(alpha < 0.5, iterations=10) & (alpha >= 0.5)
    mm = np.minimum(rgb[..., 0], rgb[..., 2]) - rgb[..., 1]
    fix = (band | soft) & (mm > 4)
    rgb[..., 0] = np.where(fix, np.minimum(rgb[..., 0], rgb[..., 1] + 4), rgb[..., 0]); rgb[..., 2] = np.where(fix, np.minimum(rgb[..., 2], rgb[..., 1] + 4), rgb[..., 2])
    rgba = np.dstack([rgb, alpha * 255]).astype(np.uint8)
    H, Wd = rgba.shape[:2]
    N = sum(row_counts)
    solid = rgba[..., 3] > 128
    cut = np.zeros_like(solid)
    for (x, y0, y1) in splits: cut[y0:y1 + 1, x] = True
    lab, n = ndi.label(solid & ~cut)
    # the cut column's own pixels: to the piece on their left
    for (x, y0, y1) in splits:
        for y in range(y0, y1 + 1):
            if solid[y, x] and x > 0 and lab[y, x - 1] > 0: lab[y, x] = lab[y, x - 1]
    sizes = ndi.sum(solid, lab, range(1, n + 1)); objs = ndi.find_objects(lab)
    order = np.argsort(sizes)[::-1]; bigs = [int(i) + 1 for i in order[:N]]
    def box(i):
        sl = objs[i - 1]; return sl[1].start, sl[0].start, sl[1].stop, sl[0].stop
    cen = {i: ((box(i)[0] + box(i)[2]) / 2, (box(i)[1] + box(i)[3]) / 2) for i in bigs}
    by_y = sorted(bigs, key=lambda i: cen[i][1])
    panel_ids, rowof, k0 = [], [], 0
    for rr, cnt in enumerate(row_counts):
        row = sorted(by_y[k0:k0 + cnt], key=lambda i: cen[i][0]); panel_ids += row; rowof += [rr] * cnt; k0 += cnt
    # distance of every pixel to each body
    dist = [ndi.distance_transform_edt(lab != i) for i in panel_ids]
    owner = {i: k for k, i in enumerate(panel_ids)}
    for i in range(1, n + 1):
        if i in owner or sizes[i - 1] < min_piece: continue
        m = lab == i
        dd = [float(d[m].min()) for d in dist]; owner[i] = int(np.argmin(dd))
        if min(dd) > 150: print("  warning: piece of %d px is %.0f px from its nearest body: kept anyway" % (sizes[i - 1], min(dd)))
    panels = []
    for k in range(N):
        main_i = panel_ids[k]
        mask = np.zeros(solid.shape, bool); fist = np.zeros(solid.shape, bool)
        for i, kk in owner.items():
            if kk != k: continue
            if i == main_i: mask |= (lab == i)
            else: mask |= (lab == i); fist |= (lab == i)
        main = lab == main_i
        grow = ndi.binary_dilation(mask, iterations=3) & (rgba[..., 3] > 0)
        ys_, xs_ = np.where(grow)
        wx0, wx1 = max(0, xs_.min() - 30), min(Wd, xs_.max() + 31); wy0, wy1 = max(0, ys_.min() - 30), min(H, ys_.max() + 31)
        # pixels of ANOTHER panel's pieces inside this window are removed (the neighbour's skirt)
        p = np.where(grow[wy0:wy1, wx0:wx1, None], rgba[wy0:wy1, wx0:wx1], 0).astype(np.uint8)
        m = main[wy0:wy1, wx0:wx1]; f = fist[wy0:wy1, wx0:wx1]
        ys, xs = np.where(p[..., 3] > 128)
        my, mx = np.where(m); y0, y1 = my.min(), my.max()
        bw = max(mx[my == y].max() - mx[my == y].min() for y in range(int(y1 - 0.22 * (y1 - y0)), y1 + 1) if (my == y).any())
        panels.append({"p": p, "box": (int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())), "bw": int(bw), "low": int(y1), "main": m, "fist": f, "row": rowof[k],
                       "origin": (int(wx0), int(wy0))})
    return {"panels": panels}


def base_mid(pan):
    x0, y0, x1, y1 = pan["box"]
    low = pan["low"]; top = y0
    m = pan["main"]; best = None
    for y in range(int(low - 0.22 * (low - top)), low + 1):
        xs = np.where(m[y])[0]
        if len(xs) and (best is None or xs.max() - xs.min() > best[0]): best = (xs.max() - xs.min(), (xs.min() + xs.max()) / 2.0)
    return best[1]


def place(pan, scale, ox, oy, FRAME=512):
    """The panel scaled by `scale`, its local pixel (0, 0) at (ox, oy) of the 512 cell. Returns (cell RGBA image, clipped px)."""
    im = Image.fromarray(pan["p"]).resize((max(1, int(round(pan["p"].shape[1] * scale))), max(1, int(round(pan["p"].shape[0] * scale)))), Image.LANCZOS)
    canvas = Image.new("RGBA", (FRAME + 3000, FRAME + 3000), (0, 0, 0, 0)); canvas.alpha_composite(im, (1500 + ox, 1500 + oy))
    fr = canvas.crop((1500, 1500, 1500 + FRAME, 1500 + FRAME))
    clipped = int((np.array(im)[..., 3] > 128).sum() - (np.array(fr)[..., 3] > 128).sum())
    return fr, clipped
