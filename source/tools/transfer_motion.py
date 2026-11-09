#!/usr/bin/env python3
"""Gives a re-skinned idle the ORIGINAL idle's motion (breathing, the small sway), for generated frames that came out almost identical (see docs/RESKIN_PILOT_PLAN.md).

An image generator draws the six panels of a breathing idle as the same pose with new random details (a cape that wobbles, shading that flickers), so the loop is nearly frozen and shimmers.
This takes ONE generated frame (the base) and makes every frame of the loop by warping it with the motion of the original character's idle: the optical flow from the original's frame k to its
frame 1 (smoothed, so only the slow movement of the body, the head and the cloak remains, not their texture), applied to the base. Frame 1 stays the generated picture itself; the other frames
are the same picture moved the way the original moved, so there is no flicker and the timing, the marks and the effects of the original fit exactly.

  python source/tools/transfer_motion.py --orig Animations/Rogue/idle/cloaked_idle_strip.png --new reskin/assassin_idle_aligned.png --out Animations/Assassin/idle/assassin_idle_strip.png [--base 1] [--smooth 7] [--max 8] [--strength 1]

--new   the aligned frames (check_reskin.py --align), in the order of the original's unique frames
--strength  share of the original's motion that is applied (1 = all; the Spellblade's idle uses 0.65 at the user's request, 2026-11-06)
--base  which new frame is used as the picture that gets warped (1-based; default: the one closest to the others)
"""
import argparse
import pathlib
import sys

import cv2
import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import reskin_lib as L


def gray_on_grey(f):
    a = f[..., 3:4].astype(np.float32) / 255.0
    rgb = f[..., :3].astype(np.float32) * a + 110.0 * (1 - a)
    return cv2.cvtColor(rgb.astype(np.uint8), cv2.COLOR_RGB2GRAY)


def flow_to(o0, ok, smooth, limit):
    """backward flow: where in frame 1 the pixel (y, x) of frame k comes from, smoothed and limited"""
    g0, gk = gray_on_grey(o0), gray_on_grey(ok)
    fl = cv2.calcOpticalFlowFarneback(gk, g0, None, 0.5, 4, 41, 5, 7, 1.5, 0)
    fl = cv2.GaussianBlur(fl, (0, 0), smooth)
    m = np.hypot(fl[..., 0], fl[..., 1])
    return fl * np.minimum(1.0, limit / np.maximum(m, 1e-6))[..., None]


def warp(base, fl, body):
    H, W = base.shape[:2]
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    fade = cv2.GaussianBlur(cv2.dilate(body.astype(np.uint8), np.ones((15, 15), np.uint8)).astype(np.float32), (0, 0), 6)[..., None]   # no motion far outside the figure
    fl = fl * fade
    pm = base.astype(np.float32)
    a = pm[..., 3:4] / 255.0
    pm[..., :3] *= a                                                                                      # premultiplied: no dark fringes at the soft edge
    out = cv2.remap(pm, xx + fl[..., 0], yy + fl[..., 1], cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0, 0))
    a2 = out[..., 3:4] / 255.0
    rgb = np.where(a2 > 1e-3, out[..., :3] / np.maximum(a2, 1e-3), 0)
    return np.dstack([np.clip(rgb, 0, 255), out[..., 3]]).astype(np.uint8)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--orig", required=True)
    ap.add_argument("--new", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--base", type=int, default=0)
    ap.add_argument("--smooth", type=float, default=7.0, help="blur of the motion field in px: higher = only the slowest, biggest movements")
    ap.add_argument("--max", type=float, default=8.0, help="the longest move of any pixel in px")
    ap.add_argument("--strength", type=float, default=1.0, help="how much of the original's motion to apply: 1 = all of it, 0.6 = a gentler breathing, 0 = none (a frozen frame)")
    a = ap.parse_args()
    of, _ = L.load_frames(a.orig)
    nf, _ = L.load_frames(a.new)
    if len(of) != len(nf):
        sys.exit("the original has %d frames, the new strip %d" % (len(of), len(nf)))
    if a.base:
        b = a.base - 1
    else:                                                               # the new frame closest to all the others (the medoid)
        d = [sum(float(np.abs(nf[i][..., :3].astype(int) - nf[j][..., :3].astype(int)).mean()) for j in range(len(nf))) for i in range(len(nf))]
        b = int(np.argmin(d))
    print("base frame:", b + 1)
    out = []
    for k in range(len(of)):
        fl = np.zeros(of[0].shape[:2] + (2,), np.float32) if k == 0 else flow_to(of[0], of[k], a.smooth, a.max) * a.strength
        out.append(nf[b] if k == 0 else warp(nf[b], fl, L.mask(nf[b])))
        print("frame %d: largest move %.1f px" % (k + 1, float(np.hypot(fl[..., 0], fl[..., 1]).max())))
    L.save_strip(out, a.out)
    print("->", a.out)


if __name__ == "__main__":
    main()
