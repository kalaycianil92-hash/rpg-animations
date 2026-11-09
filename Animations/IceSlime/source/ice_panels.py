"""Shared by the ice slime's airborne / irregular sheet cutters (glacier_slam, permafrost_eruption, blizzard_bounce, 2026-11-08; the dodge cutter has its own copy of the same ideas).

load_panels(path, row_counts) -> dict with, per panel in reading order, the panel's pieces on their REAL place in the sheet (not cut by a fixed grid):
  - the creatures are the biggest pieces of the keyed sheet (one per panel); every other piece of 40 px or more goes to the nearest creature, a piece LOWER than its creature's body (the generator's forbidden
    shadow ellipse) or cut by the sheet's edge is dropped;
  - each panel is returned as an RGBA window of its row's band, padded 300 px above and 100 px below (the crystals of an airborne frame may stand above the middle line of the sheet), so the y of a panel is
    measured from the same top for every panel of a row: the floor line of a row is then the same for its panels (a panel's local y = its y in the sheet - (PAD + row * band height - 300));
  - a crystal tip cut flat by the TOP EDGE of the sheet is repaired: the sheet is padded with magenta on top and the crystal's two edges (fitted on the 30 rows below the cut) are continued to a point, filled
    with the crystal's pale colour and outlined in the dark blue-teal.
Panel dict keys: p (RGBA array), box (x0, y0, x1, y1 of the opaque pixels, local), bw (base width: the widest row in the lowest 22% of the main piece), low (the lowest row of the main piece = the body's bottom),
row (0 or 1), tipfix (True when this sheet needed the repair).
"""
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi

PAD = 80


def _alpha(arr):
    r, g, b = arr[..., 0], arr[..., 1], arr[..., 2]
    return 1 - np.clip((np.minimum(r, b) - g - 70) / 110, 0, 1)


def repair_top_tips(im0):
    """im0: PIL RGB. Returns (padded PIL image, number of tips repaired)."""
    W0, H0 = im0.size
    img = Image.new("RGB", (W0, H0 + PAD), (255, 0, 255)); img.paste(im0, (0, PAD))
    a0 = np.array(im0).astype(float); al0 = _alpha(a0) > 0.5
    top = al0[:4]
    cols = np.where(top.any(0))[0]
    if not len(cols): return img, 0
    groups, start, prev = [], cols[0], cols[0]
    for c in cols[1:]:
        if c - prev > 8: groups.append((start, prev)); start = c
        prev = c
    groups.append((start, prev))
    d = ImageDraw.Draw(img); n_fixed = 0
    lab, _ = ndi.label(al0)
    for (x0, x1) in groups:
        if x1 - x0 < 12: continue                                        # a small chip cut by the edge: not worth a repair
        piece = np.isin(lab, np.unique(lab[:4, x0:x1 + 1][al0[:4, x0:x1 + 1]]))
        ys = np.arange(6, 36); L, R = [], []
        for y in ys:
            xs = np.where(piece[y, max(0, x0 - 40):x1 + 41])[0]
            if len(xs): L.append(xs.min() + max(0, x0 - 40)); R.append(xs.max() + max(0, x0 - 40))
            else: L.append(np.nan); R.append(np.nan)
        L = np.array(L, float); R = np.array(R, float); ok = ~np.isnan(L)
        if ok.sum() < 8: continue
        aL, bL = np.polyfit(ys[ok], L[ok], 1); aR, bR = np.polyfit(ys[ok], R[ok], 1)
        ya = (bR - bL) / (aL - aR) if abs(aL - aR) > 1e-3 else -40
        if not (-90 < ya < -2): ya = -40
        xl0, xr0 = aL * 3 + bL, aR * 3 + bR
        xa = aL * ya + bL
        patch = np.array(im0)[6:12, int(xl0 + (xr0 - xl0) * 0.3):int(xl0 + (xr0 - xl0) * 0.7)].reshape(-1, 3).mean(0)
        fill = tuple(int(v) for v in patch); line = (31, 78, 100)
        poly = [(xl0, PAD + 3), (xr0, PAD + 3), (xa, PAD + ya)]
        d.polygon(poly, fill=fill)
        d.line([(xl0, PAD + 3), (xa, PAD + ya)], fill=line, width=7); d.line([(xr0, PAD + 3), (xa, PAD + ya)], fill=line, width=7)
        n_fixed += 1
        print("tip repaired: cut from x %d to %d, edges %.2f/%.2f, apex at y %.0f above the sheet" % (x0, x1, aL, aR, -ya))
    return img, n_fixed


def load_panels(path, row_counts):
    im0 = Image.open(path).convert("RGB")
    W0, H0 = im0.size
    img, tips = repair_top_tips(im0)
    arr = np.array(img).astype(float)
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
    N = sum(row_counts); ROWS = len(row_counts)
    solid = rgba[..., 3] > 128
    lab, n = ndi.label(solid); sizes = ndi.sum(solid, lab, range(1, n + 1)); objs = ndi.find_objects(lab)
    order = np.argsort(sizes)[::-1]; bigs = [int(i) + 1 for i in order[:N]]
    def box(i):
        sl = objs[i - 1]; return sl[1].start, sl[0].start, sl[1].stop, sl[0].stop
    def box_dist(b1, b2):
        dx = max(b1[0] - b2[2], b2[0] - b1[2], 0); dy = max(b1[1] - b2[3], b2[1] - b1[3], 0)
        return (dx * dx + dy * dy) ** 0.5
    cen = {i: ((box(i)[0] + box(i)[2]) / 2, (box(i)[1] + box(i)[3]) / 2) for i in bigs}
    by_y = sorted(bigs, key=lambda i: cen[i][1])
    panel_ids, rowof, k0 = [], [], 0
    for rr, cnt in enumerate(row_counts):
        row = sorted(by_y[k0:k0 + cnt], key=lambda i: cen[i][0]); panel_ids += row; rowof += [rr] * cnt; k0 += cnt
    owner = {i: k for k, i in enumerate(panel_ids)}
    for i in range(1, n + 1):
        if i in owner or sizes[i - 1] < 40: continue
        dd = [box_dist(box(i), box(p)) for p in panel_ids]; owner[i] = int(np.argmin(dd))
    PH = (H - PAD) // ROWS
    panels = []
    for k in range(N):
        rr = rowof[k]
        main_i = panel_ids[k]; main_bottom = box(main_i)[3]
        mask = np.zeros(solid.shape, bool)
        for i, kk in owner.items():
            if kk != k: continue
            x0_, y0_, x1_, y1_ = box(i)
            if i != main_i:
                if y1_ > main_bottom + 2: continue                                   # lower than the body: the forbidden shadow
                if x0_ <= 14 or x1_ >= Wd - 15: continue                                   # cut by the sheet's side edge
            mask |= (lab == i)
        mask = ndi.binary_dilation(mask, iterations=3) & (rgba[..., 3] > 0)
        ys_, xs_ = np.where(mask)
        wx0, wx1 = max(0, xs_.min() - 40), min(Wd, xs_.max() + 41)
        wy0 = PAD + rr * PH - 300; wy1 = PAD + (rr + 1) * PH + 100
        p = np.zeros((wy1 - wy0, wx1 - wx0, 4), np.uint8)
        ya, yb = max(0, wy0), min(H, wy1)
        p[ya - wy0:yb - wy0] = np.where(mask[ya:yb, wx0:wx1, None], rgba[ya:yb, wx0:wx1], 0)
        ys, xs = np.where(p[..., 3] > 128)
        ml, mn = ndi.label(p[..., 3] > 128); msz = ndi.sum(p[..., 3] > 128, ml, range(1, mn + 1)); mmain = ml == 1 + int(np.argmax(msz))
        my, mx = np.where(mmain); y0, y1 = my.min(), my.max()
        bw = max(mx[my == y].max() - mx[my == y].min() for y in range(int(y1 - 0.22 * (y1 - y0)), y1 + 1) if (my == y).any())
        panels.append({"p": p, "box": (int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())), "bw": int(bw), "low": int(y1), "row": rr, "main": mmain})
    return {"panels": panels, "tips": tips, "PH": PH}


def base_mid(pan):
    x0, y0, x1, y1 = pan["box"]
    low = pan["low"]; top = y0
    m = pan["main"]; best = None                                                                 # the middle of the WIDEST row of the lowest 22% of the main piece: the base's own width (the lowest 6% can be a single chip or a corner of the lip)
    for y in range(int(low - 0.22 * (low - top)), low + 1):
        xs = np.where(m[y])[0]
        if len(xs) and (best is None or xs.max() - xs.min() > best[0]): best = (xs.max() - xs.min(), (xs.min() + xs.max()) / 2.0)
    return best[1]


def place(pan, scale, ox, oy, FRAME=512, fade_from=480):
    """The panel scaled by `scale`, its local pixel (0, 0) at (ox, oy) of the 512 cell; a part below the cell's bottom fades out instead of being cut. Returns (cell RGBA image, clipped px, faded px)."""
    im = Image.fromarray(pan["p"]).resize((max(1, int(pan["p"].shape[1] * scale)), max(1, int(pan["p"].shape[0] * scale))), Image.LANCZOS)
    canvas = Image.new("RGBA", (FRAME + 3000, FRAME + 3000), (0, 0, 0, 0)); canvas.alpha_composite(im, (1500 + ox, 1500 + oy))
    fr = canvas.crop((1500, 1500, 1500 + FRAME, 1500 + FRAME))
    arr = np.array(fr)
    full = np.array(canvas)[1500:1500 + 3000, 1500:1500 + FRAME, 3] > 128
    below = bool(full[FRAME - 6:].any())
    clipped = int((np.array(im)[..., 3] > 128).sum() - (arr[..., 3] > 128).sum())
    faded = 0
    if below:
        ramp = np.clip((FRAME - 1 - np.arange(FRAME)) / float(FRAME - 1 - fade_from), 0, 1)
        faded = int(((arr[..., 3] > 128) & (np.arange(FRAME)[:, None] > fade_from)).sum())
        arr[..., 3] = (arr[..., 3] * ramp[:, None]).astype(np.uint8)
        fr = Image.fromarray(arr)
    return fr, clipped, faded
