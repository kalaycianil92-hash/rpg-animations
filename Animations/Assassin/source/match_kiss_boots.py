#!/usr/bin/env python3
"""Matches the boot colour of Winter's Kiss frames 11-15 (the follow-through and the catch: two single images generated in other sessions) to the boots of frames 1-10 (the sheet).

The single images came out with browner, darker, greener boots (mean RGB about (57, 48, 43)) than the sheet's purple-brown ones (about (69, 45, 53)). This moves the boots' colour statistics in Lab space
(mean and spread of each channel) from the frame's own to the sheet's, only on the boot's body pixels (below the knee, dark, not the black outline and not the bright buckles or the violet trim), with a feathered mask.
The original strip is kept as source/assassin_winters_kiss_16frame_strip.before_boot_match.png. Run again after rebuilding the strip with reskin_strip.py (a rebuild undoes this).

  python Animations/Assassin/source/match_kiss_boots.py
"""
import pathlib
import shutil
import sys

import cv2
import numpy as np
from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "source" / "tools"))
import reskin_lib as L

STRIP = ROOT / "Animations/Assassin/dagger_throw/assassin_winters_kiss_16frame_strip.png"
BACKUP = ROOT / "Animations/Assassin/source/assassin_winters_kiss_16frame_strip.before_boot_match.png"
REF = [0, 5, 9]                 # positions (0-based) of the sheet frames: raise, wind-up, throw
FIX = [10, 11, 12, 13, 14]      # positions 11-15: the follow-through (x3) and the catch (x2)

if not BACKUP.exists():
    shutil.copy2(STRIP, BACKUP)
frames, H = L.load_frames(BACKUP)       # always start from the untouched strip


def boot_mask(f):
    m = L.mask(f)
    b = L.bbox(m)
    h = b[3] - b[1] + 1
    rgb = f[..., :3].astype(float)
    yy = np.arange(f.shape[0])[:, None]
    v = rgb.max(2)
    region = m & (yy > b[1] + 0.76 * h)
    return region & (v > 28) & (v < 135)


def lab(f):
    return cv2.cvtColor(f[..., :3].astype(np.float32) / 255.0, cv2.COLOR_RGB2LAB)


ref_px = np.concatenate([lab(frames[i])[boot_mask(frames[i])] for i in REF])
tm, ts = ref_px.mean(0), ref_px.std(0)
print("target boot colour (Lab mean):", tm.round(1), "spread", ts.round(1))
out = list(frames)
done = {}
for i in FIX:
    key = frames[i].tobytes()
    if key in done:                     # repeated frames get the identical result
        out[i] = done[key]
        continue
    f = frames[i]
    bm = boot_mask(f)
    L_ = lab(f)
    px = L_[bm]
    m0, s0 = px.mean(0), px.std(0)
    new = L_.copy()
    new[bm] = (px - m0) / np.maximum(s0, 1e-3) * ts + tm
    rgb = np.clip(cv2.cvtColor(new, cv2.COLOR_LAB2RGB) * 255.0, 0, 255)
    w = cv2.GaussianBlur(bm.astype(np.float32), (0, 0), 1.2)[..., None]
    res = f.copy()
    res[..., :3] = np.clip(f[..., :3] * (1 - w) + rgb * w, 0, 255).astype(np.uint8)
    print("frame", i + 1, "boots Lab mean", m0.round(1), "->", tm.round(1), "(%d px)" % bm.sum())
    done[key] = res
    out[i] = res
L.save_strip(out, STRIP)
print("wrote", STRIP)
