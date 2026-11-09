#!/usr/bin/env python3
"""Removes the magenta background that a cut left inside small enclosed gaps (between an arm and the waist, under a cape) of a finished strip, IN PLACE (2026-11-07).

The cutters key the flat magenta background out, but a gap that is closed on all sides can keep a pink sliver (the generator blended the colours a little). This makes every magenta-looking pixel
(min(red, blue) - green > 55, red > 170, blue > 85) and the connected pinkish pixels around them (blue >= green + 5 and red > green + 40, at most 20 px away: the salmon and the darker rose where the magenta blended with ivory or
an outline) transparent. Hair (orange-red: low blue), skin, gold and ivory never match, and pink that is not connected to a bright magenta pixel is left alone. It prints how many pixels it removed per frame; run it again after rebuilding a strip with reskin_strip.py / reskin_pipeline.py (the rebuild brings the slivers back).

  python source/tools/despink.py Animations/Spellblade/death/spellblade_death_6frame_strip.png [more strips ...] [--cell-w 512]
"""
import argparse

import numpy as np
from PIL import Image
from scipy import ndimage as ndi

ap = argparse.ArgumentParser()
ap.add_argument("strips", nargs="+")
ap.add_argument("--cell-w", type=int, default=512)
a = ap.parse_args()

for path in a.strips:
    im = np.array(Image.open(path).convert("RGBA"))
    r, g, b, al = [im[..., i].astype(int) for i in range(4)]
    mm = np.minimum(r, b) - g
    core = (al > 20) & (mm > 55) & (r > 170) & (b > 85)
    soft = (al > 0) & (b >= g + 5) & (r > g + 40)                      # pinkish, also the dark rose where the magenta blended with an outline
    kill = ndi.binary_dilation(core, iterations=20, mask=soft) | core   # grown only from the bright pink, over connected pinkish pixels, at most 20 px
    if kill.any():
        im[..., 3] = np.where(kill, 0, im[..., 3])
        Image.fromarray(im).save(path)
    per = [int(kill[:, i * a.cell_w:(i + 1) * a.cell_w].sum()) for i in range(im.shape[1] // a.cell_w)]
    print(path.replace("\\", "/").split("/")[-1], "removed", int(kill.sum()), "px", "per frame", per if kill.any() else "")
