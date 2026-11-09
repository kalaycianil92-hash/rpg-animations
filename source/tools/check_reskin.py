#!/usr/bin/env python3
"""Checks a re-skinned animation against the original, frame by frame, and can correct the drift (see docs/RESKIN_PILOT_PLAN.md).

The new looks are NOT meant to have the old silhouette (other hair, cape, armour), so the check does not ask for equal outlines. It asks whether the BODY is in the same place at the same size:
for every frame it finds the scale and shift that make the new silhouette fit the original's best (the overlap, 'IoU', of the two blurred silhouettes), then reports
  as delivered  how big and where the new figure is against the original (height ratio, feet, centre) and how well the two overlap as they are
  best fit      the scale s (new x s = original size) and the shift that fit best, and the overlap at that fit
  verdict       OK     drawn at the right size and place
                FIXED  fits well after the correction, but the size or place had drifted (the scale differs from the animation's median by more than --tol-scale, or the feet / centre were off)
                BAD    does not fit even at its best: the overlap of the whole silhouettes is below --thr-iou (0.60) or the FRONT edge (the side facing the enemy: head, chest, front arm, front leg) is farther than --thr-front (6% of the figure's height) from the original's (this front test is used only for upright figures: height at least 0.8 of the width; a crouch or a lying figure has no front): the pose is wrong, draw this frame again. The back of the figure is left out of the pose test on purpose: a new look has another cape, hair or cloak there
The scale used for the correction is the animation's MEDIAN scale (a look that is drawn a little bigger or smaller than the original is scaled as a whole, the same for every frame, so nothing
jitters); only frames that differ from it by more than --snap-scale (12%) get their own. Frames that stood on the ground are put back on the ground line. The hand marks of the original are drawn on the
overlay: the fists of the new frame must sit on the dots (a visual check: this tool does not find fists).

  python source/tools/check_reskin.py --orig Animations/Rogue/idle/cloaked_idle_strip.png --new new_idle_cut.png [--map reskin/Rogue_idle/frame_map.json] [--align aligned.png] [--out reskin/check]

--new: one or more strips of the NEW frames in the order of the guides (the cut of the generated sheets). With --map the frames are matched to the original's guided unique images; without it
the new strip is matched to all the unique images, or to every position if it has as many frames as the original strip.
"""
import argparse
import json
import pathlib
import sys

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi
from scipy.signal import fftconvolve

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import reskin_lib as L

F = 2                                                                   # the fit is searched on masks shrunk by this factor


def soft_small(m):
    img = Image.fromarray((m * 255).astype(np.uint8)).resize((m.shape[1] // F, m.shape[0] // F), Image.BILINEAR)
    return ndi.gaussian_filter(np.asarray(img, float) / 255.0, 1.2)


def scaled_small(crop_u8, s):
    h, w = crop_u8.shape
    img = Image.fromarray(crop_u8).resize((max(2, int(round(w * s / F))), max(2, int(round(h * s / F)))), Image.BILINEAR)
    return ndi.gaussian_filter(np.asarray(img, float) / 255.0, 1.2)


def best_shift(A, B):
    cor = fftconvolve(A, B[::-1, ::-1], mode="full")
    iy, ix = np.unravel_index(int(np.argmax(cor)), cor.shape)
    return float(cor[iy, ix]), iy - (B.shape[0] - 1), ix - (B.shape[1] - 1)


def fit(A, crop_u8, scales):
    sa, best = A.sum(), None
    for s in scales:
        B = scaled_small(crop_u8, s)
        ov, dy, dx = best_shift(A, B)
        iou = ov / (sa + B.sum() - ov)
        if best is None or iou > best[0]:
            best = (iou, float(s), dy * F, dx * F)
    return best                                                         # (iou, scale, top-left y, top-left x) in cell px


def fit_at(A, crop_u8, s):
    B = scaled_small(crop_u8, s)
    ov, dy, dx = best_shift(A, B)
    return ov / (A.sum() + B.sum() - ov), dy * F, dx * F


def place(frame, bb, s, ty, tx):
    """the new frame's figure (cut to its bounding box) scaled by s and put with its top left at (tx, ty) on an empty cell"""
    x0, y0, x1, y1 = bb
    crop = Image.fromarray(frame[y0:y1 + 1, x0:x1 + 1])
    w, h = int(round(crop.width * s)), int(round(crop.height * s))
    crop = crop.resize((max(1, w), max(1, h)), Image.LANCZOS)
    layer = Image.new("RGBA", (frame.shape[1], frame.shape[0]), (0, 0, 0, 0))
    layer.paste(crop, (int(tx), int(ty)))
    return np.array(layer)


def iou_soft(A, mB):
    B = soft_small(mB)
    ov = float((A * B).sum())
    return ov / (A.sum() + B.sum() - ov)


def refine_shift(mO, crop_u8, s, ty, tx, upright, grounded, rad=24):
    """Polishes the placement found from the soft overlap: the overlap alone is pulled toward the big mass of a cape, so for an upright figure the score also asks the FRONT edge (head, chest, front arm, front leg) to sit where the original's is.
    Searches +-rad px in x (and in y unless the figure stands on the ground: that was fixed already) for the best  hard overlap - 1.5 x front error / height."""
    h, w = crop_u8.shape
    img = Image.fromarray(crop_u8).resize((max(1, int(round(w * s))), max(1, int(round(h * s)))), Image.BILINEAR)
    sm = np.asarray(img) > 127
    Hc, Wc = mO.shape
    ho = max(1, int(mO.any(1).sum()))
    best = None
    for dy in ([0] if grounded else range(-rad, rad + 1, 2)):
        for dx in range(-rad, rad + 1, 2):
            y0, x0 = int(ty) + dy, int(tx) + dx
            m = np.zeros((Hc, Wc), bool)
            ys0, xs0 = max(0, y0), max(0, x0)
            ye, xe = min(Hc, y0 + sm.shape[0]), min(Wc, x0 + sm.shape[1])
            if ye <= ys0 or xe <= xs0:
                continue
            m[ys0:ye, xs0:xe] = sm[ys0 - y0:ye - y0, xs0 - x0:xe - x0]
            iou = float((m & mO).sum()) / max(1, int((m | mO).sum()))
            sc = iou
            if upright:
                fe, _ = front_error(mO, m)
                sc -= 1.5 * fe / ho
            if best is None or sc > best[0]:
                best = (sc, y0, x0)
    return best[1], best[2]


def mO_of(r, of):
    return L.mask(of[r["_tp"]])


def front_error(mO, mA):
    """How far apart the two silhouettes' FRONT edges are (the rightmost pixel of every row, the side that faces the enemy): the back of a new look (a different cape, hair, cloak) does not matter for the pose, the front does. -> mean px, share of rows both have"""
    rows = np.where(mO.any(1) & mA.any(1))[0]
    if not len(rows):
        return 999.0, 0.0
    w = mO.shape[1] - 1
    xo = w - np.argmax(mO[rows][:, ::-1], axis=1)
    xa = w - np.argmax(mA[rows][:, ::-1], axis=1)
    return float(np.mean(np.abs(xo - xa))), len(rows) / max(1, int(mO.any(1).sum()))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--orig", required=True)
    ap.add_argument("--new", required=True, nargs="+")
    ap.add_argument("--map")
    ap.add_argument("--marks", help="the original's hand marks (default: next to the original strip)")
    ap.add_argument("--partial", action="store_true", help="the new frames are only the FIRST ones of the guides (a sheet generated before the single images): compare just those")
    ap.add_argument("--align", help="write the corrected frames (the new strip, same order) here")
    ap.add_argument("--out", help="folder for the report and the overlay sheets (default: next to --align, or reskin/check)")
    ap.add_argument("--thr-iou", type=float, default=0.60, help="BAD below this overlap even at the best fit (new looks have other capes, hair and armour, so a right pose scores about 0.7: wrong poses scored about 0.5)")
    ap.add_argument("--thr-front", type=float, default=0.06, help="BAD when the front edge of the figure (the side facing the enemy) is on average farther than this share of the figure's height from the original's")
    ap.add_argument("--tol-scale", type=float, default=0.04, help="a frame whose best scale differs from the animation's median by more than this counts as drifted (FIXED)")
    ap.add_argument("--snap-scale", type=float, default=0.12, help="a frame within this of the median scale is corrected with the median itself (no jitter from noise in the fit); a frame farther off gets its own scale. Wide on purpose: on real sheets the generator draws every panel of a sheet at one scale (+-3 percent), and a frame whose BEST scale is far from the median is one whose POSE differs (tucked legs fit a smaller figure better), which a per-frame scale would turn into a wrong size")
    ap.add_argument("--tol-feet", type=float, default=5)
    ap.add_argument("--tol-centre", type=float, default=12)
    a = ap.parse_args()

    of, H = L.load_frames(a.orig)
    first, pos, groups = L.uniques(of)
    new = []
    for p in a.new:
        fr, h = L.load_frames(p)
        if h != H:
            sys.exit("the new strip %s is %d px tall, the original %d px: cut it with the same cell height" % (p, h, H))
        new += fr
    if a.map:
        mp = json.loads(pathlib.Path(a.map).read_text(encoding="utf-8"))
        uids = list(mp["guided"])[:len(new)] if a.partial else list(mp["guided"])
        targets = [first[u] for u in uids]
    elif len(new) == len(first):
        targets, uids = list(first), list(range(len(first)))
    elif len(new) == len(of):
        targets, uids = list(range(len(of))), list(pos)
    else:
        sys.exit("cannot match %d new frames: the original has %d positions and %d unique images (give --map)" % (len(new), len(of), len(first)))
    if len(targets) != len(new):
        sys.exit("the new frames (%d) do not match the %d images to compare (the order of the guide sheets)" % (len(new), len(targets)))
    marks = L.load_marks(a.marks or L.default_marks_path(a.orig))
    gy = L.ground_y(H)

    coarse = np.arange(0.70, 1.45, 0.02)
    rows = []
    for i, (tp, fN) in enumerate(zip(targets, new)):
        fO = of[tp]
        mO, mN = L.mask(fO), L.mask(fN)
        bO, bN = L.bbox(mO), L.bbox(mN)
        r = {"frame": i + 1, "uid": uids[i], "orig_position": tp + 1}
        if bN is None:
            r.update(status="BAD", note="empty frame")
            rows.append(r)
            continue
        A = soft_small(mO)
        crop = (mN[bN[1]:bN[3] + 1, bN[0]:bN[2] + 1] * 255).astype(np.uint8)
        c = fit(A, crop, coarse)
        c = fit(A, crop, np.arange(c[1] - 0.02, c[1] + 0.0201, 0.004))
        r.update(iou_best=c[0], scale=c[1], _crop=crop, _bN=bN, _bO=bO, _A=A, _tp=tp,
                 h_ratio=(bN[3] - bN[1] + 1) / (bO[3] - bO[1] + 1), feet_delta=bN[3] - bO[3], iou_raw=iou_soft(A, mN),
                 centre_delta=float(np.hypot(*(np.array(ndi.center_of_mass(mN)) - np.array(ndi.center_of_mass(mO))))), grounded=bool(bO[3] >= gy - 8))
        rows.append(r)

    good = [r["scale"] for r in rows if "scale" in r and r["iou_best"] >= 0.6]
    s_med = float(np.median(good)) if good else 1.0
    aligned = []
    for r in rows:
        if "scale" not in r:
            aligned.append(None)
            continue
        s_use = s_med if abs(r["scale"] / s_med - 1) <= a.snap_scale else r["scale"]
        iou, ty, tx = fit_at(r["_A"], r["_crop"], s_use)
        bN, bO = r["_bN"], r["_bO"]
        h_new = int(round((bN[3] - bN[1] + 1) * s_use))
        if r["grounded"] and abs(ty + h_new - 1 - bO[3]) <= 30:         # a figure that stood on the ground goes back on the ground line
            ty += bO[3] - (ty + h_new - 1)
        hO, wO = bO[3] - bO[1] + 1, bO[2] - bO[0] + 1
        upright = hO >= 0.8 * wO                                          # a standing or lunging figure has a front; a crouch or a lying one does not
        ty, tx = refine_shift(mO_of(r, of), r["_crop"], s_use, ty, tx, upright, r["grounded"] and abs(ty - (bO[3] - h_new + 1)) < 2)
        ty = max(int(ty), 2)                                               # (a taller figure in an airborne frame must not lose its head at the top of the cell)
        fr = place(new[len(aligned)], bN, s_use, ty, tx)
        mA = L.mask(fr)
        bA = L.bbox(mA)
        fe, fshare = front_error(mO_of(r, of), mA)
        r.update(scale_used=s_use, shift=(int(tx), int(ty)), iou_aligned=iou_soft(r["_A"], mA), front_err=fe, front_frac=fe / (bO[3] - bO[1] + 1), upright=bool(upright),
                 extent_delta={"left": bA[0] - bO[0], "right": bA[2] - bO[2], "top": bA[1] - bO[1]} if bA else None)
        drift = abs(r["scale"] / s_med - 1) > a.tol_scale or (r["grounded"] and abs(r["feet_delta"]) > a.tol_feet) or r["centre_delta"] > a.tol_centre
        r["status"] = "BAD" if (r["iou_aligned"] < a.thr_iou or (r["upright"] and r["front_frac"] > a.thr_front)) else ("FIXED" if drift else "OK")
        aligned.append(fr)

    print("original %s: %d positions, %d unique images; %d new frames; median scale to apply %.3f" % (pathlib.Path(a.orig).name, len(of), len(first), len(new), s_med))
    print(" #  uid  height  feet  centre  overlap(raw)  best scale  overlap(aligned)  front edge  verdict")
    for r in rows:
        if "scale" not in r:
            print("%2d  %3d  %s" % (r["frame"], r["uid"], r["note"]))
            continue
        print("%2d  %3d  %5.2f  %+4d  %5.1f   %5.2f        %5.3f        %5.2f         %4.1f px %4.1f%%   %s" % (r["frame"], r["uid"], r["h_ratio"], r["feet_delta"], r["centre_delta"], r["iou_raw"], r["scale"], r["iou_aligned"], r["front_err"], 100 * r["front_frac"], r["status"]))
    n = len(rows)
    cnt = {k: sum(1 for r in rows if r["status"] == k) for k in ("OK", "FIXED", "BAD")}
    share = (cnt["OK"] + cnt["FIXED"]) / max(1, n)
    print("OK %d, FIXED %d, BAD %d of %d frames: %s (the pilot passes at 80%% usable and no shimmer)" % (cnt["OK"], cnt["FIXED"], cnt["BAD"], n, "%.0f%% usable" % (100 * share)))

    out = pathlib.Path(a.out) if a.out else (pathlib.Path(a.align).parent / "check" if a.align else pathlib.Path(a.orig).resolve().parents[2] / "reskin" / "check")
    out.mkdir(parents=True, exist_ok=True)
    if a.align:
        cell = [f if f is not None else np.zeros_like(new[0]) for f in aligned]
        L.save_strip(cell, a.align)
        print("aligned frames ->", a.align)
    rep = [{k: (v if not k.startswith("_") else None) for k, v in r.items() if not k.startswith("_")} for r in rows]
    (out / "check_report.json").write_text(json.dumps({"median_scale": s_med, "summary": cnt, "frames": rep}, indent=1, default=float), encoding="utf-8")

    # overlay sheets: the original's outline (red) and its hand marks (dots) over the new frame, as delivered (top) and corrected (bottom)
    per, th = 8, 250
    for si in range(0, n, per):
        chunk = list(range(si, min(n, si + per)))
        tw = int(L.CW * th / H)
        sheet = Image.new("RGB", (tw * len(chunk), th * 2), (60, 60, 75))
        d = ImageDraw.Draw(sheet)
        for k, i in enumerate(chunk):
            r = rows[i]
            if "scale" not in r:
                continue
            fO = of[r["_tp"]]
            edge = L.mask(fO) & ~ndi.binary_erosion(L.mask(fO), iterations=2)
            for row, fr in ((0, new[i]), (1, aligned[i])):
                bg = Image.new("RGBA", (L.CW, H), (92, 92, 108, 255))
                bg.alpha_composite(Image.fromarray(fr))
                arr = np.array(bg)
                arr[edge] = (255, 50, 50, 255)
                tile = Image.fromarray(arr).convert("RGB")
                td = ImageDraw.Draw(tile)
                for tr, x, y in L.marks_at(marks, r["_tp"]):
                    cx, cy = x * L.CW, y * H
                    td.ellipse([cx - 9, cy - 9, cx + 9, cy + 9], outline=(255, 255, 255), width=3)
                    td.ellipse([cx - 6, cy - 6, cx + 6, cy + 6], fill=(230, 40, 40) if tr == "main" else (40, 90, 230))
                sheet.paste(tile.resize((tw, th), Image.LANCZOS), (k * tw, row * th))
            d.text((k * tw + 6, 4), "%d uid%d" % (r["frame"], r["uid"]), fill=(255, 255, 255))
            d.text((k * tw + 6, th + 4), "%s %.2f" % (r["status"], r["iou_aligned"]), fill=(255, 235, 120) if r["status"] != "OK" else (160, 255, 160))
        sheet.save(out / ("check_overlay_%d.png" % (si // per + 1)))
    print("report and overlay sheets ->", out)


if __name__ == "__main__":
    main()
