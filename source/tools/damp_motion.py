#!/usr/bin/env python3
"""Turns down the movement in a finished strip (an idle that bobs or sways too much) without a new generation.

For every frame it measures how far each part of the picture moved compared with a reference frame (optical flow),
then warps the frame back toward the reference so only a share of that movement is left.  Nothing is blended, so the
lines stay sharp and there is no ghosting; frame 1 (the reference) is untouched.  The art, the frame size and the
feet alignment stay as they were (parts that did not move do not move).

  python damp_motion.py ../../Animations/Mage/idle/robed_idle_strip.png ../../Animations/Mage/idle/robed_idle_strip.png --keep 0.5

--keep 0.5   half of the movement stays (0 = frozen at the reference pose, 1 = unchanged)
--ref 1      the frame the others are measured against and pulled toward (the rest pose, 1-based)
--smooth 6   blur of the measured movement in px; raise it if a frame shows wobbly lines, lower it for small parts

It prints, per frame, the movement left compared with the reference (head, body, hand) as a check.
Needs pillow, numpy and opencv-python (pip install opencv-python).
"""
import argparse
import numpy as np
import cv2
from PIL import Image

ap = argparse.ArgumentParser()
ap.add_argument("src"); ap.add_argument("dst")
ap.add_argument("--keep", type=float, default=0.5, help="share of the movement that stays (0 to 1)")
ap.add_argument("--ref", type=int, default=1, help="reference frame, 1-based")
ap.add_argument("--frame", type=int, default=512, help="frame width in px")
ap.add_argument("--smooth", type=float, default=6, help="blur of the measured movement in px")
a = ap.parse_args()

im = np.array(Image.open(a.src).convert("RGBA"))
W = a.frame
n = im.shape[1] // W
frames = [im[:, k * W:(k + 1) * W] for k in range(n)]
ref = frames[a.ref - 1]

def gray(f):                                          # the flow is measured on the picture over flat grey
    al = f[..., 3:4].astype(np.float32) / 255
    c = f[..., :3] * al + 128 * (1 - al)
    return cv2.cvtColor(np.clip(c, 0, 255).astype(np.uint8), cv2.COLOR_RGB2GRAY)

def flow(f):                                          # where each pixel of the reference went in frame f
    fl = cv2.calcOpticalFlowFarneback(gray(ref), gray(f), None, 0.5, 5, 21, 5, 7, 1.5, 0)
    if a.smooth > 0:
        fl = cv2.GaussianBlur(fl, (0, 0), a.smooth)
    return fl

def warp(f, fl, t):                                   # move frame f a fraction t of the way back to the reference
    ys, xs = np.mgrid[0:f.shape[0], 0:f.shape[1]].astype(np.float32)
    al = f[..., 3:4].astype(np.float32) / 255
    pm = np.dstack([f[..., :3].astype(np.float32) * al, al * 255])      # premultiplied, so edges do not pick up colour from outside
    out = cv2.remap(pm, xs + t * fl[..., 0], ys + t * fl[..., 1], cv2.INTER_LANCZOS4, borderMode=cv2.BORDER_CONSTANT, borderValue=0)
    alpha = np.clip(out[..., 3], 0, 255)
    rgb = np.where(alpha[..., None] > 0.5, out[..., :3] / np.maximum(alpha[..., None] / 255, 1e-3), 0)
    return np.dstack([np.clip(rgb, 0, 255), alpha]).astype(np.uint8)

def regions(fl, mask):                                 # mean vertical movement of the head, the body and the open hand
    ys, xs = np.mgrid[0:fl.shape[0], 0:fl.shape[1]]
    top = np.where(mask)[0].min()
    def m(sel):
        sel = sel & mask
        return float(fl[..., 1][sel].mean()) if sel.any() else 0.0
    return m(ys < top + 66), m((ys >= top + 66) & (ys < top + 236)), m(xs > 380)

out = []
mask = ref[..., 3] > 128
print("frame  movement vs frame %d before -> after (px, + = down): head   body   hand" % a.ref)
for k, f in enumerate(frames):
    if k == a.ref - 1:
        out.append(f); print("%5d  (reference)" % (k + 1)); continue
    fl = flow(f)
    g = warp(f, fl, 1 - a.keep)
    after = cv2.calcOpticalFlowFarneback(gray(ref), gray(g), None, 0.5, 5, 21, 5, 7, 1.5, 0)
    before, left = regions(fl, mask), regions(cv2.GaussianBlur(after, (0, 0), a.smooth) if a.smooth > 0 else after, mask)
    print("%5d  %s  ->  %s" % (k + 1, "  ".join("%6.2f" % v for v in before), "  ".join("%6.2f" % v for v in left)))
    out.append(g)
Image.fromarray(np.hstack(out), "RGBA").save(a.dst)
print("wrote", a.dst)
