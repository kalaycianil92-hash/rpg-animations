#!/usr/bin/env python3
"""Evens out a re-skinned character's HEAD SIZE across its animations, IN PLACE on finished strips (2026-11-07, the Spellblade).

Why: a generator draws the head a little bigger (relative to the body) in action sheets than in the calm idle, and the cut scales the whole figure to the Rogue's silhouette, so the head comes out
10-30% bigger in the skills than in the idle (the Spellblade's Umbral Shroud 29%, her hit 6-21%, her dodge 7-25%). The body must keep its size (the poses, marks and paths fit the Rogue's), so only
the HEAD is scaled, with a local warp:
  - the head size of a frame = sqrt(width x height) of the bounding box of its HAIR mask (hair_mask.py finds the hair from its colour and the face next to it); the target is the idle's;
  - a frame whose head is more than 0% bigger is shrunk by  1 - (1 - idle/frame) x ramp  (the ramp is 0 at ratio 1.0 and 1 at ratio 1.06, so there is no jump between neighbouring frames), never below --min-scale;
    a smaller head is left alone (--grow makes it bigger by up to the same rule, off by default);
  - the warp scales the picture around the NECK (the head centre plus 0.9 head radii toward the body) by that factor, with a weight that is 1 on the head (the hair's convex hull, 12 px wider) and fades
    out over about 20 px (a Gaussian), so the head sinks a few px toward the shoulders, the collar and the shoulders stay, and nothing tears.
A backup of every strip is kept (source/<strip>.before_heads.png in its folder, once). Run it AFTER the strip is final (cut, align, rebuild, despink) and again after every rebuild; then remake the hair mask
(python source/tools/hair_mask.py --all --char spellblade). The idle is the reference and is not changed.

  python source/tools/even_heads.py --char spellblade --ref Animations/Spellblade/idle/spellblade_idle_strip.png  Animations/Spellblade/hit/spellblade_hit_6frame_strip.png [...]  [--dry-run] [--preview out.png]
"""
import argparse
import pathlib
import shutil
import sys

import cv2
import numpy as np
from PIL import Image

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import hair_mask as HM

ap = argparse.ArgumentParser()
ap.add_argument("strips", nargs="+")
ap.add_argument("--char", default="spellblade")
ap.add_argument("--ref", required=True, help="the idle strip: its head size is the target")
ap.add_argument("--cell-w", type=int, default=512)
ap.add_argument("--min-scale", type=float, default=0.80)
ap.add_argument("--grow", action="store_true", help="also enlarge a head that is smaller than the idle's (up to 1/min-scale... capped at 1.08)")
ap.add_argument("--min-ratio", type=float, default=1.0, help="leave a frame alone unless its head is at least this many times the idle's (a second, light pass for the frames the first pass could not shrink enough because of --min-scale: --min-ratio 1.06)")
ap.add_argument("--dry-run", action="store_true")
ap.add_argument("--preview", default="", help="write before / after head crops of every processed frame to this png")
a = ap.parse_args()
P = HM.PROFILES[a.char]


def head_size(hair):
    ys, xs = np.where(hair)
    if len(xs) < 200:
        return None
    return float(np.sqrt((xs.max() - xs.min() + 1) * (ys.max() - ys.min() + 1)))


def frames_of(path):
    im = np.array(Image.open(path).convert("RGBA"))
    return im, [im[:, i * a.cell_w:(i + 1) * a.cell_w].copy() for i in range(im.shape[1] // a.cell_w)]


def head_geometry(f, hair):
    """head mask (hair hull widened), head centre, radius and the neck pivot"""
    pts = cv2.findNonZero(hair.astype(np.uint8))
    hull = cv2.convexHull(pts)
    hm = np.zeros(hair.shape, np.uint8)
    cv2.fillConvexPoly(hm, hull, 1)
    hm = cv2.dilate(hm, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (25, 25))) > 0
    hm &= f[..., 3] > 0
    ys, xs = np.where(hm)
    c = np.array([xs.mean(), ys.mean()])
    r = float(np.sqrt(hm.sum() / np.pi))
    far = cv2.dilate(hm.astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (51, 51))) > 0
    body = (f[..., 3] > 0) & ~far
    if body.sum() < 200:
        u = np.array([0.0, 1.0])
    else:
        by, bx = np.where(body)
        u = np.array([bx.mean(), by.mean()]) - c
        u = u / max(np.hypot(*u), 1e-6)
    return hm, c, r, c + u * 0.9 * r


def shrink_head(f, hm, piv, s0):
    H, W = hm.shape
    w = cv2.GaussianBlur(hm.astype(np.float32), (0, 0), 9)[..., None]
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    s = 1.0 + (s0 - 1.0) * w[..., 0]
    mx = (piv[0] + (xx - piv[0]) / s).astype(np.float32)
    my = (piv[1] + (yy - piv[1]) / s).astype(np.float32)
    pm = f.astype(np.float32)
    al = pm[..., 3:4] / 255.0
    pm[..., :3] *= al                                                                      # premultiplied: no dark fringes
    out = cv2.remap(pm, mx, my, cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0, 0))
    a2 = out[..., 3:4] / 255.0
    rgb = np.where(a2 > 1e-3, out[..., :3] / np.maximum(a2, 1e-3), 0)
    return np.dstack([np.clip(rgb, 0, 255), out[..., 3]]).astype(np.uint8)


_, ref_frames = frames_of(a.ref)
ref_sizes = [head_size(HM.hair_in_frame(f, P)) for f in ref_frames]
target = float(np.mean([x for x in ref_sizes if x]))
print("target head size (the idle's) %.1f px  (sqrt of the hair box width x height)" % target)

crops = []
for path in a.strips:
    im, frames = frames_of(path)
    out_frames, rows = [], []
    for i, f in enumerate(frames):
        hair = HM.hair_in_frame(f, P)
        S = head_size(hair)
        if S is None:
            out_frames.append(f)
            rows.append("frame %d: no hair found, left alone" % (i + 1))
            continue
        ratio = S / target
        if ratio < a.min_ratio:
            out_frames.append(f)
            rows.append("frame %d: head %.2f x the idle's: left alone" % (i + 1, ratio))
            continue
        if ratio > 1.0:
            s0 = 1.0 - (1.0 - 1.0 / ratio) * min(1.0, (ratio - 1.0) / 0.06)
        elif a.grow and ratio < 1.0:
            s0 = 1.0 + (1.0 / ratio - 1.0) * min(1.0, (1.0 - ratio) / 0.06)
        else:
            s0 = 1.0
        s0 = float(np.clip(s0, a.min_scale, 1.08))
        if abs(s0 - 1.0) < 0.01:
            out_frames.append(f)
            rows.append("frame %d: head %.2f x the idle's: left alone" % (i + 1, ratio))
            continue
        hm, c, r, piv = head_geometry(f, hair)
        g = shrink_head(f, hm, piv, s0)
        out_frames.append(g)
        rows.append("frame %d: head %.2f x the idle's -> scaled by %.3f around (%.0f, %.0f)" % (i + 1, ratio, s0, piv[0], piv[1]))
        if a.preview:
            x0, y0 = int(max(c[0] - 1.6 * r, 0)), int(max(c[1] - 1.7 * r, 0))
            box = (x0, y0, min(x0 + int(3.2 * r), f.shape[1]), min(y0 + int(3.6 * r), f.shape[0]))
            pair = []
            for src in (f, g):
                bg = Image.new("RGBA", f.shape[1::-1] if False else (f.shape[1], f.shape[0]), (58, 62, 78, 255))
                bg.alpha_composite(Image.fromarray(src))
                pair.append(bg.crop(box).resize((200, 225), Image.LANCZOS))
            crops.append((pathlib.Path(path).parent.name + " %d" % (i + 1), pair))
    print(pathlib.Path(path).name)
    print("   " + "\n   ".join(rows))
    if not a.dry_run:
        bak = pathlib.Path(path).parent / "source" / (pathlib.Path(path).name[:-4] + ".before_heads.png")
        bak.parent.mkdir(exist_ok=True)
        if not bak.exists():
            shutil.copy2(path, bak)
        Image.fromarray(np.concatenate(out_frames, axis=1)).save(path)

if a.preview and crops:
    cols = 6
    rowsn = (len(crops) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * 410, rowsn * 232), (30, 30, 40))
    from PIL import ImageDraw
    for k, (name, pair) in enumerate(crops):
        x, y = (k % cols) * 410, (k // cols) * 232
        sheet.paste(pair[0].convert("RGB"), (x, y + 7)); sheet.paste(pair[1].convert("RGB"), (x + 205, y + 7))
        ImageDraw.Draw(sheet).text((x + 3, y), name, fill=(255, 255, 0))
    sheet.save(a.preview)
    print("preview ->", a.preview)
